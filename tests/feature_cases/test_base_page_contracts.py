"""Feature: deterministic base-page, session-page, and page-wrapper contracts."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from requests import Response
from requests.structures import CaseInsensitiveDict

from DrissionPage._base.base import BaseElement, BasePage, BaseParser, DrissionElement, Messenger
from DrissionPage._configs.session_options import SessionOptions
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._elements.none_element import NoneElement
from DrissionPage._elements.session_element import SessionElement
from DrissionPage._pages.chromium_frame import ChromiumFrame
from DrissionPage._pages.chromium_tab import ChromiumTab
from DrissionPage._pages.session_page import SessionPage, check_headers, set_charset
from DrissionPage.errors import ElementNotFoundError, PageDisconnectedError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "base_page_contracts"
REQUIRES_BROWSER = False


def run(ctx):
    _check_base_parser_and_element_contracts()
    _check_base_page_contracts()
    _check_messenger_contracts()
    _check_session_page_properties_and_elements()
    _check_session_page_connections()
    _check_session_helpers()
    _check_chromium_tab_delegation()
    _check_chromium_frame_delegation()


def _expect_error(error_type, action, message):
    try:
        action()
    except error_type:
        return
    except Exception as exc:
        raise AssertionError(f"{message}: expected {error_type.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"{message}: expected {error_type.__name__}")


def _response(content=b"ok", *, status=200, url="https://example.test/path", headers=None):
    response = Response()
    response._content = content
    response.status_code = status
    response.url = url
    response.headers.update(headers or {})
    response.request = SimpleNamespace(method="GET", url=url)
    return response


def _check_base_parser_and_element_contracts():
    class Parser(BaseParser):
        _type = "SessionParser"
        timeout = 8

        def __init__(self):
            self.calls = []

        def _ele(self, locator, timeout=None, index=1, raise_err=None, method=None):
            self.calls.append((locator, timeout, index, raise_err, method))
            values = {"first": "one", "many": ["one", "two"], "missing": None}
            return values.get(locator)

    parser = Parser()
    assert_equal(parser("first"), "one", "BaseParser.__call__() should delegate to ele()")
    assert_equal(parser.ele("first", index=2, timeout=3), "one", "ele() should return its delegated lookup")
    assert_equal(parser.eles("many", timeout=4), ["one", "two"], "eles() should request all results")
    assert_equal(parser.calls[:3], [
        ("first", None, 1, None, "ele()"),
        ("first", 3, 2, None, "ele()"),
        ("many", 4, None, None, None),
    ], "parser helpers should preserve locator, timeout, index, and method metadata")
    key, found = parser.find(("missing", "first"), any_one=True, timeout=99)
    assert_equal((key, found), ("first", "one"), "Session parser find() should return the first match")
    assert_equal(parser.calls[-2][1], 0, "Session parser find() should use a non-waiting lookup")
    assert_equal(parser.find(("missing",), any_one=True), (None, None),
                 "find(any_one=True) should return an explicit empty pair")
    assert_equal(parser.find(("first", "many"), any_one=False),
                 {"first": "one", "many": ["one", "two"]},
                 "find(any_one=False) should retain a locator-keyed mapping")

    owner = SimpleNamespace(timeout=6, _none_ele_value=None, _none_ele_return_value=False)

    class Element(BaseElement):
        def __init__(self, owner=None):
            super().__init__(owner)
            self.calls = []

        def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
            self.calls.append((locator, timeout, index, relative, raise_err))
            if locator == "count":
                return 3.0
            if locator == "many":
                return []
            return NoneElement(self.owner)

    element = Element(owner)
    marker = SimpleNamespace(_type="ExistingElement")
    assert_true(element._ele(marker) is marker, "BaseElement should preserve an existing element object")
    missing = element._ele("missing", method="contract()")
    assert_true(isinstance(missing, NoneElement), "missing BaseElement lookups should retain NoneElement")
    assert_equal(missing.method, "contract()", "missing lookup should retain method metadata")
    assert_equal(missing.args, {"locator": "missing", "index": 1, "timeout": 6},
                 "missing lookup should retain locator arguments")
    assert_equal(element._ele("many"), [], "empty list lookups should retain their collection type")
    assert_equal(element._ele("count"), 3.0, "numeric XPath-like results should be returned")
    assert_equal(element.timeout, 6, "element timeout should delegate to its owner")
    orphan = Element()
    assert_equal(orphan.timeout, 10, "ownerless elements should use the base timeout")
    _expect_error(ElementNotFoundError, lambda: element._ele("missing", raise_err=True),
                  "raise_err=True should reject a missing element")
    _expect_error(ValueError, lambda: element.get_frame(object()),
                  "get_frame() should reject unsupported locator types")

    class Relative(DrissionElement):
        def __init__(self):
            super().__init__(owner)
            self.calls = []

        @property
        def attrs(self):
            return {"href": "", "src": "/asset.png"}

        def attr(self, name):
            return self.attrs.get(name)

        def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
            self.calls.append((locator, timeout, index, relative, raise_err))
            if "count" in locator:
                return 4
            if index is None:
                return ["  ", "kept"]
            return SimpleNamespace(value=locator)

    relative = Relative()
    assert_equal(relative.link, "/asset.png", "link should fall back from href to src")
    assert_equal(relative.child_count, 4, "child_count should coerce numeric lookup results")
    assert_equal(relative.comments, ["  ", "kept"], "comments should delegate to comment-node lookup")
    assert_equal(relative.children(), ["kept"], "children() should discard whitespace-only text nodes")
    relative.parent(2)
    assert_equal(relative.calls[-1][0], "xpath:./ancestor::*[2]",
                 "integer parent lookup should address the requested ancestor level")
    relative.next(index=2)
    assert_equal(relative.calls[-1][0], "xpath:./following-sibling::*",
                 "next() should build a following-sibling lookup")
    assert_equal(relative.calls[-1][2], 2, "next() should preserve the requested index")


def _check_base_page_contracts():
    class Page(BasePage):
        def __init__(self):
            super().__init__()
            self.results = {}

        @property
        def timeout(self):
            return 7

        def get(self, url, retry=None, interval=None, timeout=None, raise_err=False):
            return url

        def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
            return self.results.get(locator, NoneElement(self))

    page = Page()
    assert_equal((page.url_available, page.download_path), (None, None),
                 "BasePage should expose its initial availability and download path")
    assert_equal((page.retry_times, page.retry_interval), (3, 2),
                 "BasePage should initialize retry defaults")
    assert_equal(page.title, None, "title should be absent when no title element exists")
    page.results["xpath://title"] = SimpleNamespace(text="Contract title")
    assert_equal(page.title, "Contract title", "title should expose title element text")
    _expect_error(ElementNotFoundError, lambda: page._ele(""), "empty page locators should be rejected")
    missing = page._ele("missing", method="lookup")
    assert_equal(missing.method, "lookup", "page missing-result metadata should retain the method")
    assert_equal(missing.args["timeout"], 7, "page missing-result metadata should retain default timeout")
    page.results["empty"] = []
    assert_equal(page._ele("empty"), [], "BasePage should retain empty collection results")

    retry, interval, is_file = page._before_connect("https://example.test/a path?q=one two", None, None)
    assert_equal((retry, interval, is_file), (3, 2, False),
                 "remote connection preparation should apply retry defaults")
    assert_equal(page._url, "https://example.test/a%20path?q=one%20two",
                 "remote URLs should be safely quoted without losing separators")
    retry, interval, is_file = page._before_connect("https://example.test", 1, 0.25)
    assert_equal((retry, interval, is_file), (1, 0.25, False),
                 "explicit retry settings should override defaults")
    with TemporaryDirectory(prefix="dp-base-page-") as tmp:
        path = Path(tmp) / "page file.html"
        path.write_text("<title>local</title>", encoding="utf-8")
        retry, interval, is_file = page._before_connect(path, 0, 0)
        assert_true(is_file, "an existing Path should be recognized as a local file")
        assert_equal(page._url, str(path.resolve()), "local paths should resolve to an absolute filename")

    options = SessionOptions(read_file=False).set_timeout(4).set_retry(2, 0.1)
    page._set_session_options(options)
    assert_true(page._session_options is options, "BasePage should retain explicit SessionOptions identity")
    assert_equal(page._timeout, 4, "session option timeout should become the page timeout")
    page._create_session()
    assert_true(page._session is not None, "_create_session() should create a requests session")
    assert_true(page._headers is not None, "_create_session() should create request headers")
    page._session.close()


def _check_messenger_contracts():
    messenger = Messenger()
    driver_calls = []
    messenger._driver = SimpleNamespace(run=lambda command, **kwargs: driver_calls.append((command, kwargs)) or {"ok": 1})
    messenger._browser = SimpleNamespace(_detach=lambda session_id: driver_calls.append(("detach", session_id)))
    messenger._session_id = "session-4"
    messenger._debug = "Network"
    assert_equal(messenger._run_cdp_("Runtime.evaluate", _timeout=2, expression="1"), {"ok": 1},
                 "messenger CDP calls should return driver payloads")
    assert_equal(driver_calls[0], ("Runtime.evaluate", {
        "_timeout": 2,
        "_session_id": "session-4",
        "_debug": "Network",
        "expression": "1",
    }), "messenger CDP calls should route timeout, session, debug, and command arguments")

    seen = []

    def callback(**kwargs):
        seen.append(kwargs)
    messenger._set_callback("Network.event", callback, immediate=True)
    messenger._recv_event({"method": "Network.event", "params": {"value": 1}})
    assert_equal(seen, [{"value": 1}], "immediate events should invoke callbacks synchronously")
    assert_true(messenger._event_queue.empty(), "immediate events should not enter the queued-event path")
    messenger._remove_callback("Network.event", callback)
    messenger._recv_event({"method": "Page.event", "params": {"value": 2}})
    assert_equal(messenger._event_queue.get_nowait()["method"], "Page.event",
                 "ordinary events should enter the event queue")

    domain_calls = []
    messenger._run_func = lambda command, **kwargs: domain_calls.append((command, kwargs))
    messenger._enable_domain("Network", maxPostDataSize=10)
    messenger._enable_domain("Network", maxPostDataSize=99)
    assert_equal(messenger._enabled, {"Network": 2}, "domain enables should be reference counted")
    assert_equal(domain_calls, [("Network.enable", {"maxPostDataSize": 10})],
                 "a domain should only be enabled on its first reference")
    messenger._disable_domain("Network")
    messenger._disable_domain("Network", reason="done")
    assert_equal(domain_calls[-1], ("Network.disable", {"reason": "done"}),
                 "the final reference should disable the domain")
    assert_equal(messenger._enabled, {}, "disabled domains should leave reference bookkeeping")

    messenger._stop_messenger()
    assert_false(messenger._messenger_running, "stopping a messenger should clear its running flag")
    assert_in(("detach", "session-4"), driver_calls, "stopping should detach the exact CDP session")
    _expect_error(PageDisconnectedError, lambda: messenger._run_cdp("Runtime.evaluate"),
                  "stopped messengers should reject further CDP calls")


def _session_options(download_path=None):
    options = SessionOptions(read_file=False)
    options.set_headers({"User-Agent": "contract-agent", "X-Base": "base"})
    options.set_timeout(1.5).set_retry(2, 0)
    if download_path is not None:
        options.set_download_path(download_path)
    return options


def _check_session_page_properties_and_elements():
    with TemporaryDirectory(prefix="dp-session-page-") as tmp:
        page = SessionPage(_session_options(tmp))
        assert_equal((page.url, page._session_url), (None, None), "new session pages should have no current URL")
        assert_equal((page.raw_data, page.html, page.json), (b"", "", None),
                     "new session pages should expose empty response representations")
        assert_equal(page.user_agent, "contract-agent", "user_agent should use case-insensitive headers")
        assert_true(page.session is page._session, "session should expose the underlying requests session")
        assert_equal(page.response, None, "response should be absent before navigation")
        assert_equal(page.encoding, None, "encoding override should be absent by default")
        assert_equal(page.timeout, 1.5, "timeout should inherit SessionOptions")
        assert_equal(page.retry_times, 2, "retry count should inherit SessionOptions")
        assert_equal(page.retry_interval, 0, "retry interval should inherit SessionOptions")
        assert_equal(page.download_path, str(Path(tmp).resolve()), "download path should be normalized")
        assert_true(page.set is page.set, "SessionPage.set should cache its setter")
        assert_in("url=None", repr(page), "SessionPage repr should expose its current URL")

        local = Path(tmp) / "local.html"
        local.write_text(
            "<html><head><title>Local title</title></head><body>"
            "<article class='item' data-id='1'>Alpha</article>"
            "<article class='item' data-id='2'>Beta</article></body></html>",
            encoding="utf-8",
        )
        assert_true(page.get(f"file:///{local}"), "get(file:///) should load an existing local file")
        assert_equal(page.url, str(local.resolve()), "local navigation should expose an absolute file path")
        assert_equal(page.response.status_code, 200, "local navigation should synthesize a successful response")
        assert_in(b"Local title", page.raw_data, "raw_data should expose response bytes")
        assert_in("Local title", page.html, "html should expose decoded response text")
        assert_equal(page.title, "Local title", "title should parse the local response document")
        first = page.ele(("css selector", "article.item"))
        assert_true(isinstance(first, SessionElement), "ele() should produce a SessionElement")
        assert_equal(first.attr("data-id"), "1", "ele() should use one-based element indexing")
        assert_equal([item.text for item in page.eles(("css selector", "article.item"))], ["Alpha", "Beta"],
                     "eles() should preserve document order")
        assert_equal(page(("css selector", "article.item"), index=2).text, "Beta",
                     "SessionPage.__call__() should delegate indexed element lookup")
        assert_true(page.s_ele() is not None, "s_ele() without a locator should expose the document element")
        assert_equal(len(page.s_eles(("css selector", "article.item"))), 2,
                     "s_eles() should return all matching session elements")
        assert_true(page._find_elements(first, timeout=0) is first,
                    "_find_elements() should preserve SessionElement identity")
        key, found = page.find([("css selector", ".missing"), ("css selector", ".item")], any_one=True)
        assert_equal(key, ("css selector", ".item"), "SessionPage.find() should report the matching locator")
        assert_equal(found.text, "Alpha", "SessionPage.find() should return the first matching element")

        page._response = _response(b'{"ready": true}', headers={"content-type": "application/json"})
        assert_equal(page.json, {"ready": True}, "json should decode a JSON response")
        page._response = _response(b"not-json")
        assert_equal(page.json, None, "json should return None for undecodable payloads")

        page.session.cookies.set("root", "one", domain="")
        page.session.cookies.set("example", "two", domain=".example.test")
        page._url = None
        compact = page.cookies()
        assert_equal({item["name"] for item in compact}, {"root", "example"},
                     "cookies() without a URL should include the session cookie jar")
        detailed = page.cookies(all_domains=True, all_info=True)
        assert_true(all("name" in item and "value" in item for item in detailed),
                    "all_info cookies should expose complete cookie dictionaries")
        page.close()


def _check_session_page_connections():
    page = SessionPage(_session_options())

    class FakeSession:
        def __init__(self, outcomes):
            self.outcomes = list(outcomes)
            self.calls = []

        def get(self, url, **kwargs):
            self.calls.append(("get", url, kwargs))
            outcome = self.outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        def post(self, url, **kwargs):
            self.calls.append(("post", url, kwargs))
            outcome = self.outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

    success = _response(b"<meta charset='gbk'>ok", headers={"content-type": "text/html"})
    fake = FakeSession([RuntimeError("temporary"), success])
    page._session = fake
    result = page._make_response("https://example.test/path", mode="get", retry=1, interval=0,
                                 headers={"X-Request": 9})
    assert_true(result is success, "_make_response() should return the first non-empty successful response")
    assert_equal(len(fake.calls), 2, "transient request failures should consume the configured retry")
    request_headers = fake.calls[-1][2]["headers"]
    assert_equal(request_headers["X-Base"], "base", "request headers should merge page defaults")
    assert_equal(request_headers["X-Request"], "9", "request headers should normalize scalar values")
    assert_equal(request_headers["Referer"], "https://example.test", "first request should derive its referer")
    assert_equal(request_headers["Host"], "example.test", "request should derive its Host header")
    assert_equal(fake.calls[-1][2]["timeout"], 1.5, "request should apply the page timeout")
    assert_equal(success.encoding, "gbk", "HTML meta charset should determine response encoding")

    page._encoding = "utf-16"
    encoded = _response("ready".encode("utf-16"))
    page._session = FakeSession([encoded])
    assert_true(page._make_response("https://example.test/data", retry=0) is encoded,
                "encoding overrides should still return a successful response")
    assert_equal(encoded.encoding, "utf-16", "page encoding override should take precedence")

    empty = _response(b"", status=204)
    page._session = FakeSession([empty, empty])
    assert_equal(page._make_response("https://example.test/empty", retry=1, interval=0), None,
                 "empty responses should return None after retries")
    assert_equal(len(page._session.calls), 2, "empty responses should consume retry attempts")
    page._session = FakeSession([RuntimeError("terminal")])
    _expect_error(RuntimeError,
                  lambda: page._make_response("https://example.test/fail", retry=0, raise_err=True),
                  "raise_err should preserve the request exception")

    nav_response = _response(b"created", status=201, url="https://example.test/created")
    page._session = FakeSession([nav_response])
    nav = page._s_connect("https://example.test/created", mode="post", retry=0, timeout=2)
    assert_true(nav, "2xx session navigation should return a truthy NavResult")
    assert_equal((nav.status, nav.url, nav.Response), (201, nav_response.url, nav_response),
                 "NavResult should expose response status, URL, and identity")
    assert_true(page.url_available, "successful navigation should update URL availability")
    assert_true(page.response is nav_response, "successful navigation should retain response identity")
    assert_equal(page._session.calls[0][0], "post", "post navigation should use Session.post()")

    failed_response = _response(b"missing", status=404)
    page._session = FakeSession([failed_response])
    failed = page._s_connect("https://example.test/missing", mode="get", retry=0)
    assert_false(failed, "non-2xx session navigation should return a false-like NavResult")
    assert_equal(failed.status, 404, "failed NavResult should retain response status")
    assert_false(page.url_available, "failed navigation should update URL availability")
    page._session = FakeSession([failed_response])
    _expect_error(ConnectionError,
                  lambda: page._s_connect("https://example.test/missing", mode="get", retry=0, raise_err=True),
                  "raise_err should reject an unsuccessful HTTP status")

    get_calls = []
    page._s_connect = lambda **kwargs: get_calls.append(kwargs) or "get-result"
    assert_equal(page.get("https://example.test/a path", timeout=3, params={"q": "x"}), "get-result",
                 "get() should return its session connection result")
    assert_equal(get_calls[-1]["timeout"], 3, "get() should forward an explicit timeout")
    assert_equal(get_calls[-1]["params"], {"q": "x"}, "get() should forward request options")
    assert_equal(get_calls[-1]["url"], "https://example.test/a%20path", "get() should forward its quoted URL")
    assert_equal(page.post("https://example.test/post", data="body"), "get-result",
                 "post() should return its session connection result")
    assert_equal(get_calls[-1]["mode"], "post", "post() should choose the post connection mode")
    assert_equal(get_calls[-1]["timeout"], page.timeout, "post() should apply the default page timeout")


def _check_session_helpers():
    assert_true(check_headers(CaseInsensitiveDict({"Timeout": 1}), CaseInsensitiveDict(), "timeout"),
                "check_headers() should treat request arguments case-insensitively")
    assert_true(check_headers(CaseInsensitiveDict(), CaseInsensitiveDict({"Referer": "x"}), "referer"),
                "check_headers() should inspect default headers case-insensitively")
    assert_false(check_headers(CaseInsensitiveDict(), CaseInsensitiveDict(), "Host"),
                 "check_headers() should report missing values")

    html = _response(b"<html><head><meta charset='Big5'></head></html>", headers={"content-type": "text/html"})
    assert_true(set_charset(html) is html, "set_charset() should preserve response identity")
    assert_equal(html.encoding, "Big5", "HTML meta declarations should set response encoding")
    plain = _response(b"plain", headers={"content-type": "text/plain"})
    set_charset(plain)
    assert_equal(plain.encoding, None, "non-HTML content without a charset should retain default encoding")


class _ModeObject:
    def __init__(self):
        self.calls = []
        self.title = "Mode title"
        self.html = "<html>mode</html>"
        self.raw_data = b"mode"
        self.json = {"mode": True}
        self.user_agent = "mode-agent"

    def _call(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))
        return f"{name}-result"

    def __call__(self, *args, **kwargs):
        return self._call("call", *args, **kwargs)

    def get(self, *args, **kwargs):
        return self._call("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._call("post", *args, **kwargs)

    def ele(self, *args, **kwargs):
        return self._call("ele", *args, **kwargs)

    def eles(self, *args, **kwargs):
        return self._call("eles", *args, **kwargs)

    def s_ele(self, *args, **kwargs):
        return self._call("s_ele", *args, **kwargs)

    def s_eles(self, *args, **kwargs):
        return self._call("s_eles", *args, **kwargs)

    def cookies(self, *args, **kwargs):
        return self._call("cookies", *args, **kwargs)

    def _find_elements(self, *args, **kwargs):
        return self._call("find", *args, **kwargs)


def _check_chromium_tab_delegation():
    tab = object.__new__(ChromiumTab)
    mode = _ModeObject()
    browser_calls = []
    tab._mode_obj = mode
    tab._d_mode = True
    tab._response = None
    tab._session = SimpleNamespace(close=lambda: browser_calls.append("session-close"))
    tab._target_id = "tab-7"
    tab._timeouts = SimpleNamespace(base=2, page_load=5)
    tab._timeout = 9
    tab._messenger_running = False
    tab._browser = SimpleNamespace(
        id="browser-1",
        _run_cdp=lambda command, **kwargs: browser_calls.append((command, kwargs)),
        _close_tab=lambda value: browser_calls.append(("close", value)),
        close_tabs=lambda value, **kwargs: browser_calls.append(("close-tabs", value, kwargs)),
    )

    assert_equal((tab.mode, tab.title, tab.html, tab.json, tab.user_agent),
                 ("d", "Mode title", "<html>mode</html>", {"mode": True}, "mode-agent"),
                 "ChromiumTab properties should delegate to the active mode object")
    assert_equal(tab.raw_data, mode.html, "driver mode raw_data should expose active HTML")
    assert_equal(tab.url, None, "an inactive driver messenger should have no browser URL")
    assert_equal(tab.timeout, 2, "driver mode timeout should use the base browser timeout")
    assert_equal(tab("#item", index=2, timeout=3), "call-result", "tab calls should delegate to the mode object")
    assert_equal(tab.ele("#item", index=2, timeout=3), "ele-result", "ele() should delegate to the mode object")
    assert_equal(tab.eles(".item", timeout=3), "eles-result", "eles() should delegate to the mode object")
    assert_equal(tab.s_ele("#item", index=2, timeout=3), "s_ele-result", "s_ele() should delegate")
    assert_equal(tab.s_eles(".item", timeout=3), "s_eles-result", "s_eles() should delegate")
    assert_equal(tab.cookies(True, True), "cookies-result", "cookies() should preserve both options")
    assert_equal(tab._find_elements("#item", 3, index=2, relative=True), "find-result",
                 "_find_elements() should delegate lookup details")
    assert_equal(tab.get("https://example.test", retry=1, interval=0, timeout=4), "get-result",
                 "driver-mode get() should delegate navigation")
    assert_equal(mode.calls[-1], ("get", (), {
        "url": "https://example.test", "retry": 1, "interval": 0, "timeout": 4, "raise_err": False,
    }), "driver-mode get() should preserve navigation arguments")
    _expect_error(ValueError, lambda: tab.get("https://example.test", params={"q": 1}),
                  "driver-mode get() should reject session-only request arguments")
    tab.activate()
    assert_in(("Target.activateTarget", {"targetId": "tab-7"}), browser_calls,
              "activate() should target this tab id")

    tab._d_mode = False
    tab._response = SimpleNamespace(url="https://session.test", close=lambda: browser_calls.append("response-close"))
    assert_equal((tab.mode, tab.url, tab.raw_data, tab.timeout),
                 ("s", "https://session.test", b"mode", 9),
                 "session mode should expose response URL, bytes, and session timeout")
    assert_equal(tab.get("https://session.test/next", params={"q": 1}), "get-result",
                 "session-mode get() should delegate request arguments")
    assert_equal(mode.calls[-1][2]["timeout"], 5, "session-mode get() should default to page-load timeout")
    assert_equal(tab.post("https://session.test/post", data="body"), "post-result",
                 "post() should delegate to the session mode object")
    assert_equal(mode.calls[-1][2]["timeout"], 5, "post() should default to page-load timeout")

    tab.close(session=True)
    assert_in(("close", tab), browser_calls, "close() should ask the browser to close this exact tab")
    assert_in("session-close", browser_calls, "close(session=True) should close the requests session")
    assert_in("response-close", browser_calls, "close(session=True) should close the retained response")
    tab.close(others=True, session=True)
    assert_in(("close-tabs", "tab-7", {"others": True}), browser_calls,
              "close(others=True) should preserve this tab and close its siblings")

    old_tabs = ChromiumTab._TABS.copy()
    try:
        ChromiumTab._TABS["tab-7"] = tab
        tab._disconnect_flag = False
        tab._on_disconnect()
        assert_not_present("tab-7", ChromiumTab._TABS,
                           "disconnect should evict a non-disconnecting singleton tab")
    finally:
        ChromiumTab._TABS.clear()
        ChromiumTab._TABS.update(old_tabs)


def assert_not_present(member, mapping, message):
    if member in mapping:
        raise AssertionError(f"{message}: {member!r} unexpectedly present")


class _FrameElement:
    def __init__(self):
        self._obj_id = "frame-object"
        self._node_id = 17
        self._backend_id = 18
        self.owner = "frame-owner"
        self.tag = "iframe"
        self.link = "https://frame.test"
        self.attrs = {"id": "contract-frame", "name": "frame-name"}
        self.xpath = "/html/body/iframe"
        self.css_selector = "html > body > iframe"
        self.sr = "shadow"
        self.calls = []

    def _record(self, method, *args, **kwargs):
        self.calls.append((method, args, kwargs))
        return f"{method}-result"

    def _run_js(self, *args, **kwargs):
        return self._record("run_js", *args, **kwargs)

    def property(self, *args, **kwargs):
        return self._record("property", *args, **kwargs)

    def attr(self, *args, **kwargs):
        return self._record("attr", *args, **kwargs)

    def remove_attr(self, *args, **kwargs):
        return self._record("remove_attr", *args, **kwargs)

    def style(self, *args, **kwargs):
        return self._record("style", *args, **kwargs)

    def parent(self, *args, **kwargs):
        return self._record("parent", *args, **kwargs)

    def prev(self, *args, **kwargs):
        return self._record("prev", *args, **kwargs)

    def next(self, *args, **kwargs):
        return self._record("next", *args, **kwargs)

    def before(self, *args, **kwargs):
        return self._record("before", *args, **kwargs)

    def after(self, *args, **kwargs):
        return self._record("after", *args, **kwargs)

    def prevs(self, *args, **kwargs):
        return self._record("prevs", *args, **kwargs)

    def nexts(self, *args, **kwargs):
        return self._record("nexts", *args, **kwargs)

    def befores(self, *args, **kwargs):
        return self._record("befores", *args, **kwargs)

    def afters(self, *args, **kwargs):
        return self._record("afters", *args, **kwargs)

    def get_screenshot(self, *args, **kwargs):
        return self._record("screenshot", *args, **kwargs)


class _DocumentElement:
    def __init__(self):
        self.calls = []

    def _run_js(self, script, *args, **kwargs):
        self.calls.append((script, args, kwargs))
        values = {
            "return this.location.href;": "https://frame.test/page",
            "return this.documentElement.outerHTML;": "<html>frame body</html>",
            "return this.activeElement;": "active",
            "return this.readyState;": "complete",
        }
        return values.get(script, "document-js-result")

    def _ele(self, *args, **kwargs):
        self.calls.append(("ele", args, kwargs))
        return "document-element"


def _check_chromium_frame_delegation():
    frame = object.__new__(ChromiumFrame)
    frame_ele = _FrameElement()
    doc_ele = _DocumentElement()
    target_calls = []
    frame._frame_ele = frame_ele
    frame.doc_ele = doc_ele
    frame._target_page = SimpleNamespace(
        _run_cdp=lambda method, **kwargs: target_calls.append((method, kwargs)) or {
            "outerHTML": '<iframe id="contract-frame"></iframe>'
        }
    )
    frame._tab = SimpleNamespace(tab_id="tab-8")
    frame._download_path = "/tmp/downloads"
    frame._frame_id = "frame-9"
    frame._is_diff_domain = False
    frame._ele = lambda locator, **kwargs: 5 if "count" in locator else SimpleNamespace(text="Frame title")

    other = object.__new__(ChromiumFrame)
    other._frame_id = "frame-9"
    assert_true(frame == other, "frames with the same frame id should compare equal")
    other._frame_id = "frame-10"
    assert_false(frame == other, "frames with different frame ids should compare unequal")
    assert_in("id='contract-frame'", repr(frame), "frame repr should expose frame-element attributes")
    assert_equal((frame._obj_id, frame._node_id, frame.owner), ("frame-object", 17, "frame-owner"),
                 "frame identity properties should delegate to the frame element")
    assert_true(frame.frame_ele is frame_ele, "frame_ele should preserve element identity")
    assert_equal((frame.tag, frame.link, frame.attrs),
                 ("iframe", "https://frame.test", frame_ele.attrs),
                 "frame metadata should delegate to the frame element")
    assert_equal((frame.xpath, frame.css_selector, frame.sr, frame.shadow_root),
                 (frame_ele.xpath, frame_ele.css_selector, "shadow", "shadow"),
                 "frame path and shadow-root properties should delegate")
    assert_equal((frame.tab_id, frame.download_path), ("tab-8", "/tmp/downloads"),
                 "frame should expose tab identity and download path")
    assert_equal(frame.url, "https://frame.test/page", "frame URL should use its document element")
    assert_equal(frame.inner_html, "<html>frame body</html>", "inner_html should use the frame document")
    assert_equal(frame.html, '<iframe id="contract-frame"><html>frame body</html></iframe>',
                 "html should combine the outer frame tag with inner document HTML")
    assert_equal(target_calls, [("DOM.getOuterHTML", {"backendNodeId": 18})],
                 "frame HTML should query its exact backend node")
    assert_equal((frame.title, frame.active_ele, frame.child_count, frame._js_ready_state),
                 ("Frame title", "active", 5, "complete"),
                 "frame document properties should expose deterministic delegated values")

    assert_equal(frame.property("hidden"), "property-result", "property() should delegate to the frame element")
    assert_equal(frame.attr("id"), "attr-result", "attr() should delegate to the frame element")
    assert_equal(frame.remove_attr("hidden"), None, "remove_attr() should preserve its mutating return contract")
    assert_equal(frame.style("display", "::before"), "style-result", "style() should preserve pseudo-element options")
    frame.refresh()
    assert_equal(doc_ele.calls[-1][0], "this.location.reload();", "refresh() should reload the frame document")
    assert_equal(frame.run_js("return document.title;", 1, as_expr=True, timeout=2), "document-js-result",
                 "ordinary frame JavaScript should run against the document")
    assert_equal(frame.run_js("this.scrollIntoView();", as_expr=False), "run_js-result",
                 "scroll-into-view JavaScript should run against the frame element")

    assert_equal(frame.parent(2, 3, timeout=4), "parent-result", "parent() should delegate traversal arguments")
    assert_equal(frame.prev(".item", 2, timeout=4, ele_only=False), "prev-result",
                 "prev() should delegate traversal arguments")
    assert_equal(frame.next(".item", 2, timeout=4, ele_only=False), "next-result",
                 "next() should delegate traversal arguments")
    assert_equal(frame.before(".item", 2, timeout=4, ele_only=False), "before-result",
                 "before() should delegate traversal arguments")
    assert_equal(frame.after(".item", 2, timeout=4, ele_only=False), "after-result",
                 "after() should delegate traversal arguments")
    assert_equal(frame.prevs(".item", timeout=4, ele_only=False), "prevs-result",
                 "prevs() should delegate traversal arguments")
    assert_equal(frame.nexts(".item", timeout=4, ele_only=False), "nexts-result",
                 "nexts() should delegate traversal arguments")
    assert_equal(frame.befores(".item", timeout=4, ele_only=False), "befores-result",
                 "befores() should delegate traversal arguments")
    assert_equal(frame.afters(".item", timeout=4, ele_only=False), "afters-result",
                 "afters() should delegate traversal arguments")
    assert_equal(frame.get_screenshot(path="/tmp", name="frame.png", as_bytes=True), "screenshot-result",
                 "frame screenshot should delegate to the frame element")

    frame._ele = lambda locator, **kwargs: f"element:{locator}:{kwargs['index']}"
    assert_equal(frame("#inside", index=2, timeout=3), "element:#inside:2",
                 "ChromiumFrame.__call__() should delegate to frame element lookup")
    existing = object.__new__(ChromiumElement)
    assert_true(frame._find_elements(existing, timeout=0) is existing,
                "frame lookup should preserve ChromiumElement-like identity only for actual ChromiumElement instances")
