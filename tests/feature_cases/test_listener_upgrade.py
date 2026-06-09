"""Feature: upgraded listener API, WebSocketPacket, and SSEPacket."""
from __future__ import annotations

from inspect import signature
import time

from DrissionPage._units.listener import Listener

from support import (
    TestFailure,
    WebSocketServer,
    assert_equal,
    assert_false,
    assert_in,
    assert_not_in,
    assert_true,
    html,
    json_response,
    local_server,
    make_browser,
    sse_response,
)


FEATURE_ID = 'listener_upgrade'

BROWSER_PHASE = True

def run(ctx):
    test_listener_api_shape()
    if ctx.skip_browser:
        ctx.skip_current_browser('browser-backed listener checks skipped by --skip-browser')
        return
    test_websocket_sse_and_http_restore(ctx.browser_path)


def test_listener_api_shape():
    start_params = signature(Listener.start).parameters
    targets_params = signature(Listener.set_targets).parameters
    assert_not_in('method', start_params, 'listen.start() should remove method parameter')
    assert_not_in('res_type', start_params, 'listen.start() should remove res_type parameter')
    assert_not_in('method', targets_params, 'listen.set_targets() should remove method parameter')
    assert_not_in('res_type', targets_params, 'listen.set_targets() should remove res_type parameter')
    assert_true(hasattr(Listener, 'set_method'), 'Listener should expose set_method fluent setter')
    assert_true(hasattr(Listener, 'set_res_type'), 'Listener should expose set_res_type fluent setter')


def _collect_until(tab, predicate, *, timeout=8):
    packets = []
    deadline = time.time() + timeout
    while time.time() < deadline:
        packet = tab.listen.wait(timeout=1, fit_count=False)
        if not packet:
            continue
        if isinstance(packet, list):
            packets.extend(packet)
        else:
            packets.append(packet)
        matched = [p for p in packets if predicate(p)]
        if matched:
            return matched, packets
    return [], packets


def _record(errors, label, func):
    try:
        func()
    except TestFailure as exc:
        errors.append(f'{label}: {exc}')


def test_websocket_sse_and_http_restore(executable):
    errors = []
    with WebSocketServer() as ws_url:
        routes = {
            '/ws-page': lambda req: html(
                f"""
                <body>
                <script>
                window.socket = new WebSocket('{ws_url}');
                window.socket.addEventListener('open', () => window.socket.send(JSON.stringify({{kind: 'client', n: 2}})));
                </script>
                websocket
                </body>
                """,
                title='websocket page',
            ),
            '/sse-page': lambda req: html(
                """
                <body>
                <script>
                window.sseEvents = [];
                window.es = new EventSource('/events');
                window.es.addEventListener('message', event => window.sseEvents.push(event.data));
                window.es.addEventListener('done', event => window.sseEvents.push(event.data));
                </script>
                sse
                </body>
                """,
                title='sse page',
            ),
            '/events': lambda req: sse_response([
                'id: 1\nevent: message\ndata: {"kind":"hello"}\n\n',
                'id: 2\nevent: done\ndata: finished\n\n',
            ]),
            '/api': lambda req: json_response({'ok': True}),
        }
        with local_server(routes) as base, make_browser(executable) as browser:
            tab = browser.latest_tab

            def check_ws():
                tab.listen.set_res_type.WebSocket(only=True)
                tab.listen.start()
                try:
                    assert_true(tab.get(base + '/ws-page'), 'websocket page should load')
                    ws_packets, _ = _collect_until(tab, lambda p: getattr(p, 'type', None) == 'WebSocketPacket')
                    assert_true(ws_packets, 'set_res_type.WebSocket(only=True) should capture WebSocketPacket values')
                    assert_true(all(hasattr(p, 'timestamp') for p in ws_packets), 'WebSocketPacket should expose timestamp')
                    assert_true(all(hasattr(p, 'is_sent') for p in ws_packets), 'WebSocketPacket should expose is_sent')
                    assert_true(any(hasattr(p, 'payload') or hasattr(p, 'data') for p in ws_packets),
                                'WebSocketPacket should expose payload/data content')
                    assert_true(any(getattr(p, 'data', None) for p in ws_packets), 'WebSocketPacket data should be readable')
                finally:
                    tab.listen.stop()

            def check_sse():
                tab.listen.set_res_type.EventSource(only=True)
                tab.listen.start('/events')
                try:
                    assert_true(tab.get(base + '/sse-page'), 'sse page should load')
                    sse_packets, _ = _collect_until(tab, lambda p: getattr(p, 'type', None) == 'SSEPacket')
                    assert_true(sse_packets, 'set_res_type.EventSource(only=True) should capture SSEPacket values')
                    packet = sse_packets[0]
                    assert_true(hasattr(packet, 'timestamp'), 'SSEPacket should expose timestamp')
                    assert_in(packet.name, ('message', 'done'), 'SSEPacket should expose event name')
                    assert_true(packet.id in ('1', '2'), 'SSEPacket should expose event id')
                    assert_true(packet.data, 'SSEPacket should expose event data')
                finally:
                    tab.listen.stop()

            def check_http_restore():
                tab.listen.set_res_type.all()
                tab.listen.set_method.all()
                tab.listen.start('/api')
                try:
                    tab.run_js("fetch('/api').catch(() => {});")
                    http_packet = tab.listen.wait(timeout=5)
                    assert_equal(getattr(http_packet, 'type', 'DataPacket'), 'DataPacket',
                                 'normal listener should return DataPacket after WS/SSE modes')
                    assert_equal(http_packet.response.body, {'ok': True},
                                 'normal listener should still parse fetch response body')
                finally:
                    tab.listen.stop()

            def check_method_filter():
                tab.listen.set_method.GET(only=True)
                tab.listen.start('/api')
                try:
                    tab.run_js("fetch('/api', {method: 'POST'}).catch(() => {});")
                    assert_false(tab.listen.wait(timeout=0.8), 'set_method.GET(only=True) should filter out POST fetch')
                finally:
                    tab.listen.stop()
                    tab.listen.set_method.all()

            _record(errors, 'WebSocketPacket/set_res_type.WebSocket', check_ws)
            _record(errors, 'SSEPacket/set_res_type.EventSource', check_sse)
            _record(errors, 'HTTP DataPacket restore', check_http_restore)
            _record(errors, 'method filter', check_method_filter)

    if errors:
        raise TestFailure('\n'.join(errors))
