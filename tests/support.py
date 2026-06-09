# -*- coding: utf-8 -*-
"""Local deterministic helpers for DrissionPage release verification tests.

This module intentionally has no pytest dependency. The runner executes it from a
venv outside the repository root so imports resolve to the installed DrissionPage
package, not the checkout source tree.
"""
from __future__ import annotations

import base64
import hashlib
import inspect
import json
import os
import socket
import struct
import tempfile
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import parse_qs, urlparse


DEFAULT_BROWSER = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class TestFailure(AssertionError):
    """Assertion raised by tests."""


@dataclass
class TestContext:
    browser_path: str | None = None
    include_browser: bool = True
    include_online: bool = False
    artifacts_dir: Path = field(default_factory=lambda: Path(tempfile.gettempdir()) / "dp-tests-artifacts")
    timeout: float = 5.0
    headless: bool = True

    @property
    def skip_browser(self) -> bool:
        return not self.include_browser

    def skip(self, message: str) -> None:
        raise SkipTestCase(message)

    def skip_current_browser(self, message: str) -> None:
        raise SkipTestCase(message)

    def __post_init__(self) -> None:
        self.artifacts_dir = Path(self.artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class TestResult:
    name: str
    status: str
    duration: float
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TestCase:
    name: str
    title: str
    requires_browser: bool
    features: tuple[str, ...]
    run: Callable[[TestContext], None]


class SkipTestCase(Exception):
    pass


def assert_true(value: Any, message: str, **details: Any) -> None:
    if not value:
        if details:
            message = f"{message} | details={json.dumps(details, ensure_ascii=False, default=str)}"
        raise TestFailure(message)


def assert_false(value: Any, message: str, **details: Any) -> None:
    if value:
        if details:
            message = f"{message} | details={json.dumps(details, ensure_ascii=False, default=str)}"
        raise TestFailure(message)


def assert_equal(actual: Any, expected: Any, message: str = "values differ") -> None:
    if actual != expected:
        raise TestFailure(f"{message}: expected={expected!r}, actual={actual!r}")


def assert_in(member: Any, container: Iterable[Any], message: str = "member missing") -> None:
    if member not in container:
        raise TestFailure(f"{message}: {member!r} not in {container!r}")


def assert_not_in(member: Any, container: Iterable[Any], message: str = "unexpected member") -> None:
    if member in container:
        raise TestFailure(f"{message}: {member!r} unexpectedly in {container!r}")


def assert_nav_result(result: Any, *, status: Any = None, ok: bool | None = None, label: str = "navigation") -> None:
    assert_true(hasattr(result, "status") and hasattr(result, "ok"), f"{label} should return NavResult-like object")
    if status is not None:
        assert_equal(result.status, status, f"{label} status mismatch")
    if ok is not None:
        assert_equal(result.ok, ok, f"{label} ok mismatch")


def version_tuple() -> tuple[int, ...]:
    import re
    import DrissionPage as dp

    return tuple(int(part) for part in re.findall(r"\d+", getattr(dp, "__version__", "0"))[:3])


def wait_until(predicate: Callable[[], Any], timeout: float = 5.0, interval: float = 0.05, desc: str = "condition") -> Any:
    end = time.perf_counter() + timeout
    last: Any = None
    while time.perf_counter() < end:
        last = predicate()
        if last:
            return last
        time.sleep(interval)
    raise TestFailure(f"Timed out waiting for {desc}; last={last!r}")


def require_browser(ctx: TestContext) -> None:
    if not ctx.include_browser:
        raise SkipTestCase("browser checks disabled by --skip-browser")
    browser = ctx.browser_path or os.environ.get("DRISSIONPAGE_BROWSER_PATH") or DEFAULT_BROWSER
    if browser and not Path(browser).exists():
        raise SkipTestCase(f"browser executable not found: {browser}")


def make_chromium(ctx: TestContext, *, force_oopif: bool = False):
    """Create a Chromium object for release verification.

    force_oopif is kept for non-screenshot iframe diagnostics; the default
    tests deliberately does not run iframe screenshot checks.
    """
    require_browser(ctx)
    from DrissionPage import Chromium, ChromiumOptions

    co = ChromiumOptions(read_file=False)
    co.auto_port()
    co.headless(ctx.headless)
    co.set_load_mode("normal")
    browser_path = ctx.browser_path or os.environ.get("DRISSIONPAGE_BROWSER_PATH") or DEFAULT_BROWSER
    if browser_path:
        co.set_browser_path(browser_path)
    if os.environ.get("CI"):
        co.set_argument("--no-sandbox")
        co.set_argument("--disable-dev-shm-usage")
        co.set_argument("--disable-gpu")
    if force_oopif:
        # Keep this available for non-screenshot cross-origin diagnostics only.
        co.remove_argument("--disable-site-isolation-trials")
        co.set_argument("--site-per-process")
    return Chromium(co)


@contextmanager
def chromium(ctx: TestContext, **kwargs: Any):
    browser = make_chromium(ctx, **kwargs)
    try:
        yield browser
    finally:
        try:
            browser.quit()
        except Exception:
            pass


@contextmanager
def make_browser(browser_path: str | None = None, *, page_load_timeout: float | None = None, force_oopif: bool = False):
    ctx = TestContext(browser_path=browser_path, include_browser=True, timeout=page_load_timeout or 5.0)
    browser = make_chromium(ctx, force_oopif=force_oopif)
    try:
        if page_load_timeout is not None:
            try:
                browser.latest_tab.set.timeouts(page_load=page_load_timeout)
            except Exception:
                pass
        yield browser
    finally:
        try:
            browser.quit()
        except Exception:
            pass


def import_version() -> dict[str, str]:
    import DrissionPage

    return {
        "version": getattr(DrissionPage, "__version__", "unknown"),
        "module": getattr(DrissionPage, "__file__", "unknown"),
    }


class LocalHandler(BaseHTTPRequestHandler):
    server_version = "DPTestHTTP/1.0"

    def log_message(self, *_: Any) -> None:  # keep reports deterministic/noiseless
        return

    def _write(self, body: bytes | str, *, status: int = 200, content_type: str = "text/html; charset=utf-8", headers: dict[str, str] | None = None) -> None:
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        self._write(json.dumps({"method": "POST", "body": body}), content_type="application/json")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        if path == "/":
            self._write("<html><title>root</title><body><h1 id='root'>root</h1></body></html>")
        elif path == "/ok":
            self._write("ok", content_type="text/plain; charset=utf-8", headers={"X-Check": "ok"})
        elif path == "/json":
            self._write(json.dumps({"ok": True, "query": qs}), content_type="application/json")
        elif path == "/missing":
            self._write("missing", status=404, content_type="text/plain; charset=utf-8")
        elif path == "/error":
            self._write("error", status=500, content_type="text/plain; charset=utf-8")
        elif path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
        elif path == "/slow":
            delay = float(qs.get("delay", ["2"])[0])
            time.sleep(delay)
            self._write("slow", content_type="text/plain; charset=utf-8")
        elif path == "/page/nav":
            self._write("""
                <!doctype html><meta charset='utf-8'><title>nav check</title>
                <body><a id='to-missing' href='/missing'>missing</a></body>
            """)
        elif path == "/page/locator":
            self._write("""
                <!doctype html><meta charset='utf-8'><title>locator check</title>
                <body>
                  plain text only marker
                  <main id='main' role='main' aria-label='Main Area'>
                    <button id='save' aria-label='Save Now'>Save</button>
                    <p id='text'>//div[@id="target"]</p>
                    <section><div id='target' class='needle' data-kind='target'>target div</div></section>
                    <div id='123abc' class='numeric'>numeric id</div>
                    <label><input id='check1' type='checkbox'> check me</label>
                    <svg id='svgroot' width='60' height='30'><rect id='svgrect' width='60' height='30' fill='red' onclick='window.svgClicked=1'></rect></svg>
                  </main>
                  <script>window.svgClicked = 0;</script>
                </body>
            """)
        elif path == "/page/listener":
            mode = qs.get("mode", ["all"])[0]
            port = self.server.server_port
            self._write(f"""
                <!doctype html><meta charset='utf-8'><title>listener {mode}</title>
                <body><h1>listener {mode}</h1><script>
                window.events = [];
                function note(x) {{ window.events.push(x); }}
                async function run() {{
                  if ({mode!r} === 'fetch' || {mode!r} === 'all') {{
                    await fetch('/json?from=listener').then(r => r.text()).then(() => note('fetch'));
                  }}
                  if ({mode!r} === 'sse' || {mode!r} === 'all') {{
                    let es = new EventSource('/events');
                    es.addEventListener('check', ev => {{ note('sse:' + ev.data); es.close(); }});
                  }}
                  if ({mode!r} === 'ws' || {mode!r} === 'all') {{
                    let ws = new WebSocket('ws://127.0.0.1:{port}/ws');
                    ws.onopen = () => {{ note('ws-open'); ws.send(JSON.stringify({{kind:'client', value:42}})); }};
                    ws.onmessage = ev => {{ note('ws:' + ev.data); ws.close(); }};
                  }}
                }}
                run();
                </script></body>
            """)
        elif path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            payload = "id: 7\nevent: check\ndata: {\"kind\":\"sse\",\"value\":42}\n\n"
            self.wfile.write(payload.encode("utf-8"))
            self.wfile.flush()
            time.sleep(0.2)
        elif path == "/ws":
            self._handle_ws()
        elif path == "/download/file.txt":
            self._write("download body\n", content_type="text/plain; charset=utf-8", headers={"Content-Disposition": "attachment; filename=check.txt"})
        elif path == "/page/console":
            self._write("""
                <!doctype html><meta charset='utf-8'><title>console check</title>
                <script>
                  console.log('check-log', {value: 42});
                  console.warn('check-warn');
                  console.error('check-error');
                </script><body>console</body>
            """)
        elif path == "/page/iframe-parent":
            child = qs.get("child", [f"http://127.0.0.1:{self.server.server_port}/page/iframe-child"])[0]
            self._write(f"""
              <!doctype html><meta charset='utf-8'><title>parent-before</title>
              <body><iframe id='child' src='{child}'></iframe></body>
            """)
        elif path == "/page/iframe-child":
            self._write("""
              <!doctype html><meta charset='utf-8'><title>child-title</title>
              <body><a id='swap' href='/page/iframe-child-2'>swap</a><div id='inside'>inside frame</div></body>
            """)
        elif path == "/page/iframe-child-2":
            self._write("""
              <!doctype html><meta charset='utf-8'><title>child-title-2</title>
              <body><div id='inside2'>inside frame 2</div></body>
            """)
        elif path == "/page/iframe-fetch-child":
            self._write("""
              <!doctype html><meta charset='utf-8'><title>iframe-fetch-child</title>
              <body><div id='cross-inside'>cross host inside</div>
              <script>fetch('/json?from=iframe').then(r => r.text()).then(t => window.fetchDone = t);</script>
              </body>
            """)
        elif path == "/page/alert":
            self._write("""
              <!doctype html><meta charset='utf-8'><title>alert check</title>
              <script>alert('check-alert');</script><body>alert page</body>
            """)
        else:
            self._write(f"not found: {path}", status=404, content_type="text/plain; charset=utf-8")

    def _handle_ws(self) -> None:
        key = self.headers.get("Sec-WebSocket-Key")
        if not key:
            self.send_error(HTTPStatus.BAD_REQUEST, "missing websocket key")
            return
        accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        self.close_connection = True
        try:
            self.connection.settimeout(2)
            # Read one client text frame so CDP sees both sent and received packets.
            _ = self._read_ws_frame()
            self._send_ws_text(json.dumps({"kind": "server", "value": 43}))
            time.sleep(0.2)
            self._send_ws_close()
        except Exception:
            return

    def _read_ws_frame(self) -> bytes:
        header = self.connection.recv(2)
        if len(header) < 2:
            return b""
        b1, b2 = header
        length = b2 & 0x7F
        if length == 126:
            length = struct.unpack("!H", self.connection.recv(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self.connection.recv(8))[0]
        mask = self.connection.recv(4) if (b2 & 0x80) else b""
        payload = self.connection.recv(length) if length else b""
        if mask:
            payload = bytes(payload[i] ^ mask[i % 4] for i in range(len(payload)))
        return payload

    def _send_ws_text(self, text: str) -> None:
        payload = text.encode("utf-8")
        header = bytes([0x81])
        if len(payload) < 126:
            header += bytes([len(payload)])
        elif len(payload) < 65536:
            header += bytes([126]) + struct.pack("!H", len(payload))
        else:
            header += bytes([127]) + struct.pack("!Q", len(payload))
        self.connection.sendall(header + payload)

    def _send_ws_close(self) -> None:
        try:
            self.connection.sendall(b"\x88\x00")
        except Exception:
            pass


def html(body: str, *, title: str = "") -> tuple[int, str, str, dict[str, str]]:
    prefix = "<!doctype html><meta charset='utf-8'>"
    if title:
        prefix += f"<title>{title}</title>"
    return 200, "text/html; charset=utf-8", prefix + body, {}


def json_response(data: Any, *, status: int = 200, headers: dict[str, str] | None = None) -> tuple[int, str, str, dict[str, str]]:
    return status, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False), headers or {}


def binary_response(body: bytes, content_type: str, headers: dict[str, str] | None = None, *, status: int = 200) -> tuple[int, str, bytes, dict[str, str]]:
    return status, content_type, body, headers or {}


def sse_response(chunks: list[str] | tuple[str, ...]) -> tuple[int, str, str, dict[str, str]]:
    return 200, "text/event-stream; charset=utf-8", "".join(chunks), {"Cache-Control": "no-cache", "Connection": "keep-alive"}


def request_body(req: BaseHTTPRequestHandler) -> str:
    if hasattr(req, "_cached_body"):
        return req._cached_body
    length = int(req.headers.get("Content-Length") or 0)
    body = req.rfile.read(length).decode("utf-8", "replace") if length else ""
    req._cached_body = body
    return body


def _write_route_response(req: BaseHTTPRequestHandler, response: Any) -> None:
    if isinstance(response, tuple):
        status, content_type, body, headers = response
    else:
        status, content_type, body, headers = 200, "text/html; charset=utf-8", response, {}
    if isinstance(body, str):
        body = body.encode("utf-8")
    req.send_response(status)
    req.send_header("Content-Type", content_type)
    req.send_header("Content-Length", str(len(body)))
    req.send_header("Cache-Control", headers.get("Cache-Control", "no-store") if isinstance(headers, dict) else "no-store")
    if headers:
        for k, v in headers.items():
            if k.lower() == "cache-control":
                continue
            req.send_header(k, v)
    req.end_headers()
    try:
        req.wfile.write(body)
        req.wfile.flush()
    except (BrokenPipeError, ConnectionResetError):
        pass


def _route_handler(routes: dict[str, Callable[[BaseHTTPRequestHandler], Any]]):
    class RouteHandler(BaseHTTPRequestHandler):
        server_version = "DPFeatureHTTP/1.0"

        def log_message(self, *_: Any) -> None:
            return

        def do_GET(self) -> None:
            self._serve()

        def do_POST(self) -> None:
            self._serve()

        def _serve(self) -> None:
            path = urlparse(self.path).path
            route = routes.get(path)
            if route is None:
                _write_route_response(self, (404, "text/plain; charset=utf-8", f"not found: {path}", {}))
                return
            _write_route_response(self, route(self))

    return RouteHandler


@contextmanager
def local_server(handler: type[BaseHTTPRequestHandler] | dict[str, Callable[[BaseHTTPRequestHandler], Any]] | None = None, *, host: str = "127.0.0.1"):
    route_mode = isinstance(handler, dict)
    handler_cls = _route_handler(handler) if route_mode else (handler or LocalHandler)
    server = ThreadingHTTPServer((host, 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://{host}:{server.server_port}"
        yield base if route_mode else (base, server)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


class WebSocketServer:
    def __init__(self, host: str = "127.0.0.1"):
        self.host = host
        self._ctx = None
        self.url = None

    def __enter__(self) -> str:
        self._ctx = local_server(LocalHandler, host=self.host)
        base, _server = self._ctx.__enter__()
        self.url = base.replace("http://", "ws://") + "/ws"
        return self.url

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._ctx:
            self._ctx.__exit__(exc_type, exc, tb)


def function_accepts(fn: Callable[..., Any], name: str) -> bool:
    try:
        return name in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def wait_for_packet(tab: Any, wanted: Callable[[Any], bool], *, timeout: float = 5.0, desc: str = "packet") -> Any:
    end = time.perf_counter() + timeout
    seen: list[str] = []
    while time.perf_counter() < end:
        remain = max(0.05, min(0.5, end - time.perf_counter()))
        packet = tab.listen.wait(timeout=remain, fit_count=False)
        if packet is False:
            continue
        packets = packet if isinstance(packet, list) else [packet]
        for item in packets:
            seen.append(getattr(item, "type", type(item).__name__))
            if wanted(item):
                return item
    raise TestFailure(f"No {desc} before timeout; seen={seen}")
