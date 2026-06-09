# -*- coding: utf-8 -*-
from __future__ import annotations

import time

from support import TestFailure, TestCase, TestContext, chromium, local_server, wait_for_packet


def _packet_type(packet):
    return getattr(packet, "type", type(packet).__name__)


def run(ctx: TestContext) -> None:
    from DrissionPage.items import DataPacket, SSEPacket, WebSocketPacket

    errors: list[str] = []
    with local_server() as (base, _server), chromium(ctx) as browser:
        tab = browser.latest_tab

        try:
            tab.listen.set_res_type.WebSocket(only=True)
            tab.listen.start("/ws")
            tab.get(base + "/page/listener?mode=ws")
            ws_packet = wait_for_packet(tab, lambda p: isinstance(p, WebSocketPacket), timeout=ctx.timeout, desc="WebSocketPacket")
            if ws_packet.resourceType != "WebSocket":
                errors.append(f"WebSocketPacket.resourceType mismatch: {ws_packet.resourceType!r}")
            if ws_packet.connect_info is None:
                errors.append("WebSocketPacket.connect_info should exist when listening before connect")
        except Exception as e:
            errors.append(f"set_res_type.WebSocket(only=True) did not capture WebSocketPacket: {type(e).__name__}: {e}; internal _res_type={getattr(tab.listen, '_res_type', None)!r}")
        finally:
            tab.listen.stop()

        try:
            tab.listen.set_res_type.EventSource(only=True)
            tab.listen.start("/events")
            tab.get(base + "/page/listener?mode=sse")
            sse_packet = wait_for_packet(tab, lambda p: isinstance(p, SSEPacket), timeout=ctx.timeout, desc="SSEPacket")
            if sse_packet.resourceType != "EventSource":
                errors.append(f"SSEPacket.resourceType mismatch: {sse_packet.resourceType!r}")
            if sse_packet.name != "check" or sse_packet.id != "7" or "sse" not in sse_packet.data:
                errors.append(f"SSEPacket fields mismatch: name={sse_packet.name!r}, id={sse_packet.id!r}, data={sse_packet.data!r}")
            if sse_packet.connect_info is None:
                errors.append("SSEPacket.connect_info should exist when listening before connect")
        except Exception as e:
            errors.append(f"set_res_type.EventSource(only=True) did not capture SSEPacket: {type(e).__name__}: {e}; internal _res_type={getattr(tab.listen, '_res_type', None)!r}")
        finally:
            tab.listen.stop()

        try:
            tab.listen.set_res_type.Fetch(only=True)
            tab.listen.start("/json")
            tab.get(base + "/page/listener?mode=fetch")
            http_packet = wait_for_packet(tab, lambda p: isinstance(p, DataPacket) and p.response.status == 200, timeout=ctx.timeout, desc="Fetch DataPacket after restart")
            if not http_packet.url.endswith("/json?from=listener"):
                errors.append(f"Fetch packet URL mismatch after restart: {http_packet.url!r}")
        except Exception as e:
            errors.append(f"listener stop()/start() Fetch restart failed: {type(e).__name__}: {e}")
        finally:
            tab.listen.stop()

        try:
            tab.listen.set_res_type.all().remove_WebSocket()
            tab.listen.start(True)
            tab.get(base + "/page/listener?mode=all")
            seen = []
            end = time.perf_counter() + ctx.timeout
            got_fetch = False
            while time.perf_counter() < end:
                packet = tab.listen.wait(timeout=0.3, fit_count=False)
                if packet is False:
                    continue
                for item in (packet if isinstance(packet, list) else [packet]):
                    seen.append(_packet_type(item))
                    if isinstance(item, WebSocketPacket):
                        errors.append(f"remove_WebSocket() should suppress WebSocketPacket; seen={seen}")
                    if isinstance(item, DataPacket) and "/json" in item.url:
                        got_fetch = True
                if got_fetch:
                    break
            if not got_fetch:
                errors.append(f"remove_WebSocket() should still allow normal HTTP DataPacket; seen={seen}")
        except Exception as e:
            errors.append(f"set_res_type.all().remove_WebSocket() scenario failed: {type(e).__name__}: {e}")
        finally:
            tab.listen.stop()

    if errors:
        raise TestFailure("Listener WS/SSE mismatches:\n- " + "\n- ".join(errors))


TEST_CASE = TestCase(
    name="listener_ws_sse",
    title="Listener setters, WebSocketPacket/SSEPacket and restart filtering",
    requires_browser=True,
    features=("listener_setters", "websocket_packet", "sse_packet", "listener_restart"),
    run=run,
)
