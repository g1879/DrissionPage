"""Feature: deterministic listener packet and filter contracts."""
from __future__ import annotations

from base64 import b64encode
from queue import Queue
from types import SimpleNamespace

from DrissionPage._units.listener import (
    BrowserDataPacket,
    DataPacket,
    Listener,
    SSEPacket,
    WebSocketConnectInfo,
    WebSocketPacket,
    in_targets,
    sse2list,
)
from DrissionPage.errors import WaitTimeoutError
from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "listener_data_contracts"
REQUIRES_BROWSER = False


class _Owner:
    def __init__(self):
        self.tab_id = "tab-17"
        self._frame_id = "frame-17"
        self.timeout = 0
        self._messenger_running = True
        self.callbacks = {}
        self.enabled = []
        self.disabled = []
        self.cdp_calls = []
        self.response_bodies = {}
        self.post_data = {}
        self.listen = None
        self.browser = None

    def _set_callback(self, event, callback):
        self.callbacks[event] = callback

    def _enable_domain(self, domain, **kwargs):
        self.enabled.append((domain, kwargs))

    def _disable_domain(self, domain):
        self.disabled.append(domain)

    def _run_cdp(self, method, **kwargs):
        self.cdp_calls.append((method, kwargs))
        request_id = kwargs.get("requestId")
        if method == "Network.getResponseBody":
            return self.response_bodies.get(request_id, {})
        if method == "Network.getRequestPostData":
            return {"postData": self.post_data.get(request_id)}
        raise AssertionError(f"unexpected CDP call: {method}")


def run(ctx):
    _check_data_packet_contracts()
    _check_body_and_post_data_parsing()
    _check_websocket_and_sse_packets()
    _check_filter_setters_and_target_matching()
    _check_listener_lifecycle_and_queues()
    _check_http_event_correlation()
    _check_websocket_and_sse_callbacks()
    _check_browser_data_packet_contracts()


def _make_packet(*, raw_post_data=None, post_data_entries=None, body='{"ok": true}', base64_body=False):
    owner = _Owner()
    owner.listen = SimpleNamespace(listening=True)
    packet = DataPacket(owner, ("/api", "POST", "Fetch"))
    request = {
        "url": "https://example.test/api?one=1&blank=&one=last",
        "method": "POST",
        "headers": {"Content-Type": "application/json", "X-Base": "request"},
        "timestamp": 12.5,
        "hasPostData": bool(raw_post_data or post_data_entries),
    }
    if post_data_entries is not None:
        request["postDataEntries"] = post_data_entries
    packet._raw_request = {"request": request, "frameId": "frame-api"}
    packet._raw_post_data = raw_post_data
    packet._requestExtraInfo = {
        "headers": {"content-type": "ignored/duplicate", "X-Extra": "extra"},
        "associatedCookies": [
            {"cookie": {"name": "accepted", "value": "1"}, "blockedReasons": []},
            {"cookie": {"name": "blocked", "value": "2"}, "blockedReasons": ["SecureOnly"]},
        ],
    }
    packet._raw_response = {
        "url": request["url"],
        "status": 201,
        "headers": {"Content-Type": "application/json", "X-Base": "response"},
    }
    packet._responseExtraInfo = {
        "headers": {"content-type": "ignored/duplicate", "X-Response-Extra": "extra"},
        "statusCode": 201,
    }
    packet._raw_body = body
    packet._base64_body = base64_body
    packet._resource_type = "Fetch"
    packet.timestamp = 13.5
    return packet


def _check_data_packet_contracts():
    packet = _make_packet(raw_post_data='{"name": "DrissionPage", "enabled": true}')

    assert_equal(packet.type, "DataPacket", "DataPacket should expose its packet type")
    assert_equal(packet.tab_id, "tab-17", "DataPacket should retain the owner tab id")
    assert_equal(packet.target, ("/api", "POST", "Fetch"), "DataPacket should retain the matched target")
    assert_equal(packet.url, "https://example.test/api?one=1&blank=&one=last",
                 "DataPacket.url should delegate to the request URL")
    assert_equal(packet.method, "POST", "DataPacket.method should delegate to the request method")
    assert_equal(packet.frameId, "frame-api", "DataPacket should expose the request frame id")
    assert_equal(packet.resourceType, "Fetch", "DataPacket should expose the response resource type")
    assert_equal(packet.request.params, {"one": "last", "blank": ""},
                 "request params should retain blank values and the last duplicate value")
    assert_equal(packet.request.postData, {"name": "DrissionPage", "enabled": True},
                 "JSON post data should decode to native values")
    assert_equal(packet.request.timestamp, 12.5, "request timestamp should come from the CDP request")
    assert_equal(packet.request.headers["CONTENT-TYPE"], "application/json",
                 "request headers should be case-insensitive")
    assert_equal(packet.request.headers["x-extra"], "extra",
                 "request extra-info headers should fill missing values")
    assert_equal(packet.request.headers["content-type"], "application/json",
                 "request extra-info headers should not replace primary headers")
    assert_equal(packet.request.cookies, [{"name": "accepted", "value": "1"}],
                 "request cookies should exclude entries with blocked reasons")
    assert_equal(packet.request.extra_info.all_info, packet._requestExtraInfo,
                 "request extra_info should expose the complete raw mapping")
    assert_equal(packet.response.status, 201, "response attributes should proxy the raw response")
    assert_equal(packet.response.timestamp, 13.5, "response timestamp should retain the packet timestamp")
    assert_equal(packet.response.headers["CONTENT-TYPE"], "application/json",
                 "response headers should be case-insensitive")
    assert_equal(packet.response.headers["x-response-extra"], "extra",
                 "response extra-info headers should fill missing values")
    assert_equal(packet.response.headers["content-type"], "application/json",
                 "response extra-info headers should not replace primary headers")
    assert_equal(packet.response.extra_info.statusCode, 201,
                 "response extra_info should proxy optional CDP values")
    assert_equal(packet.response.raw_body, '{"ok": true}', "raw_body should remain available")
    assert_equal(packet.response.body, {"ok": True}, "JSON response bodies should decode to native values")
    assert_equal(packet.data, {"ok": True}, "DataPacket.data should alias response.body")
    assert_false(packet.is_failed, "new DataPacket instances should not be marked failed")
    assert_equal(packet.fail_info.errorText, None, "missing failure fields should resolve to None")
    assert_equal(repr(packet),
                 '<DataPacket target="(\'/api\', \'POST\', \'Fetch\')" url="https://example.test/api?one=1&blank=&one=last">',
                 "DataPacket repr should include the target and URL")
    assert_true(packet.request is packet.request, "request wrappers should be cached")
    assert_true(packet.response is packet.response, "response wrappers should be cached")

    packet._raw_fail_info = {"errorText": "net::ERR_ABORTED", "canceled": True}
    packet._fail_info = None
    assert_equal(packet.fail_info.errorText, "net::ERR_ABORTED", "failure details should proxy CDP fields")
    assert_true(packet.fail_info.canceled, "failure details should retain boolean fields")
    assert_true(packet.wait_extra_info(timeout=0), "wait_extra_info should return immediately when data exists")

    packet._responseExtraInfo = None
    packet.tab._messenger_running = False
    assert_false(packet.wait_extra_info(timeout=0),
                 "wait_extra_info should stop immediately when the messenger is no longer running")


def _check_body_and_post_data_parsing():
    plain_post = _make_packet(raw_post_data="name=DrissionPage&enabled=yes")
    assert_equal(plain_post.request.postData, "name=DrissionPage&enabled=yes",
                 "non-JSON post data should remain text")

    one_entry = [{"bytes": b64encode(b'{"part": 1}').decode()}]
    entry_packet = _make_packet(post_data_entries=one_entry)
    assert_equal(entry_packet.request.postData, {"part": 1},
                 "one postDataEntries item should decode to one object")

    many_entries = [
        {"bytes": b64encode(b'{"part": 1}').decode()},
        {"bytes": b64encode(b'{"part": 2}').decode()},
    ]
    entries_packet = _make_packet(post_data_entries=many_entries)
    assert_equal(entries_packet.request.postData, [{"part": 1}, {"part": 2}],
                 "multiple postDataEntries items should decode in order")

    no_post = _make_packet(raw_post_data=None, post_data_entries=None)
    assert_false(no_post.request.postData, "requests without post data should expose False")

    encoded = b64encode(b"binary-response\x00").decode()
    binary_packet = _make_packet(body=encoded, base64_body=True)
    assert_equal(binary_packet.response.body, b"binary-response\x00",
                 "base64 response bodies should decode to bytes")

    text_packet = _make_packet(body="plain response")
    assert_equal(text_packet.response.body, "plain response", "plain response bodies should remain text")

    event_stream = 'event: message\ndata: {"ok": true}\n\ndata: finished'
    sse_packet = _make_packet(body=event_stream)
    sse_packet._raw_response["headers"]["Content-Type"] = "text/event-stream; charset=utf-8"
    assert_equal(sse_packet.response.body,
                 [{"event": "message", "data": {"ok": True}}, {"data": "finished"}],
                 "event-stream response bodies should split into structured event rows")
    assert_equal(sse2list("id: 1\ndata: true\n\nid: second\ndata: text"),
                 [{"id": 1, "data": True}, {"id": "second", "data": "text"}],
                 "sse2list should JSON-decode individual values when possible")

    empty_packet = _make_packet(body="")
    assert_equal(empty_packet.response.body, None, "empty response bodies should expose None")


def _check_websocket_and_sse_packets():
    owner = _Owner()
    connection = WebSocketConnectInfo(owner, ("socket", "GET", "WebSocket"), "ws-1",
                                      "wss://example.test/socket", {"type": "script"})
    connection.request = {"headers": {"Upgrade": "websocket"}}
    connection.response = {"response": {"status": 101}}

    text_packet = WebSocketPacket(owner, connection.target, {
        "requestId": "ws-1",
        "timestamp": 20.5,
        "response": {"opcode": 1, "payloadData": '{"kind": "message", "count": 2}'},
    }, True)
    text_packet._connect_info = connection
    assert_equal(text_packet.type, "WebSocketPacket", "WebSocketPacket should expose its packet type")
    assert_equal(text_packet.resourceType, "WebSocket", "WebSocketPacket should expose its resource type")
    assert_equal(text_packet.tab_id, "tab-17", "WebSocketPacket should retain the owner tab id")
    assert_true(text_packet.is_sent, "sent websocket frames should retain their direction")
    assert_equal(text_packet.timestamp, 20.5, "WebSocketPacket should expose its timestamp")
    assert_equal(text_packet.data, {"kind": "message", "count": 2},
                 "text websocket JSON should decode to native values")
    assert_equal(text_packet.url, "wss://example.test/socket", "connected frames should expose the socket URL")
    assert_equal(text_packet.request, connection.request, "connected frames should expose handshake request data")
    assert_equal(text_packet.response, connection.response, "connected frames should expose handshake response data")
    assert_equal(text_packet.frameId, "frame-17", "websocket frames should use the owner frame id")
    assert_equal(text_packet.method, None, "websocket frame packets should not report an HTTP method")
    assert_false(text_packet.is_failed, "websocket frame packets should not be marked failed")
    assert_equal(repr(text_packet), '<WebSocketPacket sent requestId=ws-1 timestamp=20.5>',
                 "WebSocketPacket repr should include direction, request id, and timestamp")

    raw_text = WebSocketPacket(owner, True, {
        "requestId": "ws-2", "timestamp": 21, "response": {"opcode": 1, "payloadData": "not-json"}
    }, False)
    assert_equal(raw_text.data, "not-json", "non-JSON websocket text should remain text")
    assert_equal(raw_text.url, None, "unconnected websocket frames should not invent a URL")

    binary = WebSocketPacket(owner, True, {
        "requestId": "ws-3", "timestamp": 22,
        "response": {"opcode": 2, "payloadData": b64encode(b"frame-bytes").decode()},
    }, False)
    assert_equal(binary.data, b"frame-bytes", "binary websocket frames should decode from base64")

    event = SSEPacket(owner, ("events", "GET", "EventSource"), {
        "requestId": "sse-1", "timestamp": 30.5, "eventName": "update", "eventId": "evt-7",
        "data": '{"ready": true}',
    })
    assert_equal(event.type, "SSEPacket", "SSEPacket should expose its packet type")
    assert_equal(event.resourceType, "EventSource", "SSEPacket should expose its resource type")
    assert_equal(event.name, "update", "SSEPacket should expose the event name")
    assert_equal(event.id, "evt-7", "SSEPacket should expose the event id")
    assert_equal(event.data, '{"ready": true}', "SSEPacket data should preserve the CDP event text")
    assert_equal(event.timestamp, 30.5, "SSEPacket should expose its timestamp")
    assert_equal(event.frameId, "frame-17", "unconnected SSE events should use the owner frame id")
    assert_equal(event.url, None, "unconnected SSE events should not invent a URL")
    assert_equal(event.method, None, "unconnected SSE events should not invent a method")
    assert_false(event.is_failed, "SSE packets should not be marked failed")
    assert_equal(repr(event), '<SSEPacket requestId=sse-1 timestamp=30.5>',
                 "SSEPacket repr should include request id and timestamp")

    event._connect_info = SimpleNamespace(
        url="https://example.test/events", method="GET", frameId="event-frame",
        request={"url": "https://example.test/events"}, response={"status": 200},
    )
    assert_equal(event.url, "https://example.test/events", "connected SSE events should expose their URL")
    assert_equal(event.method, "GET", "connected SSE events should expose their request method")
    assert_equal(event.frameId, "event-frame", "connected SSE events should expose their request frame")
    assert_equal(event.request, event._connect_info.request, "connected SSE events should expose request data")
    assert_equal(event.response, event._connect_info.response, "connected SSE events should expose response data")


def _check_filter_setters_and_target_matching():
    owner = _Owner()
    listener = Listener(owner)
    owner.listen = listener

    assert_true(listener.urls is True, "listeners should initially match every URL")
    listener.set_urls("/api")
    assert_equal(listener.urls, {"/api"}, "a string URL filter should become a one-item set")
    listener.set_urls(["/api", "/asset", "/api"], is_regex=True)
    assert_equal(listener.urls, {"/api", "/asset"}, "URL filters should remove duplicates")
    assert_true(listener._is_regex, "set_urls should retain regex mode")
    listener.set_urls(None, is_regex=False)
    assert_equal(listener.urls, {"/api", "/asset"}, "None should preserve the current URL filters")
    assert_false(listener._is_regex, "regex mode should update independently of URL filters")
    listener.set_urls(True)
    assert_true(listener.urls is True, "True should reset URL matching to all requests")
    _expect_error(ValueError, lambda: listener.set_urls(17), "unsupported URL filter types should be rejected")

    assert_true(listener.set_method is listener.set_method, "method setters should be cached")
    assert_true(listener.set_res_type is listener.set_res_type, "resource-type setters should be cached")
    listener.set_method.PUT()
    assert_equal(listener._method, {"GET", "POST", "PUT"}, "method setters should add allowed methods")
    listener.set_method.PATCH(only=True)
    assert_equal(listener._method, {"PATCH"}, "only=True should replace the method filter")
    listener.set_method.GET().remove_PATCH()
    assert_equal(listener._method, {"GET"}, "remove methods should discard one selected method")
    listener.set_method.all().remove_CONNECT()
    assert_equal(listener._method, listener.set_method._ALLOW - {"CONNECT"},
                 "removing from all methods should materialize every other allowed method")
    listener.set_method.all()
    assert_true(listener._method is True, "method all() should reset the method filter")
    _expect_error(ValueError, lambda: listener.set_method.UNKNOWN(), "unknown method setters should be rejected")

    listener.set_res_type.ws(only=True)
    assert_equal(listener._res_type, {"WebSocket"}, "ws() should alias WebSocket filtering")
    listener.set_res_type.sse()
    assert_equal(listener._res_type, {"WebSocket", "EventSource"}, "sse() should alias EventSource filtering")
    listener.set_res_type.remove_ws()
    assert_equal(listener._res_type, {"EventSource"}, "remove_ws() should remove WebSocket filtering")
    listener.set_res_type.remove_sse()
    assert_equal(listener._res_type, set(), "remove_sse() should remove EventSource filtering")
    listener.set_res_type.all()
    assert_true(listener._res_type is True, "resource-type all() should reset resource filtering")

    listener.set_urls(["/api", r"/items/\d+"], is_regex=False)
    listener._method = {"GET"}
    listener._res_type = {"Fetch"}
    assert_equal(in_targets(listener, "https://host.test/api/list", "GET", "Fetch"),
                 ("/api", "GET", "Fetch"), "literal target matching should return the matched filter and metadata")
    assert_false(in_targets(listener, "https://host.test/api/list", "POST", "Fetch"),
                 "method filters should reject non-matching requests")
    assert_false(in_targets(listener, "https://host.test/api/list", "GET", "XHR"),
                 "resource filters should reject non-matching requests")
    listener.set_urls(r"/items/\d+", is_regex=True)
    assert_equal(in_targets(listener, "https://host.test/items/42", "GET", "Fetch"),
                 (r"/items/\d+", "GET", "Fetch"), "regex URL filters should use regular-expression matching")
    listener.set_urls(True)
    listener._method = True
    listener._res_type = True
    assert_equal(in_targets(listener, "https://host.test/anything", "OPTIONS", "Other"),
                 (True, "OPTIONS", "Other"), "all filters should retain request metadata in the target tuple")


def _check_listener_lifecycle_and_queues():
    owner = _Owner()
    listener = Listener(owner)
    owner.listen = listener
    listener.set_res_type.WebSocket(only=True)
    listener.start("/socket")
    assert_true(listener.listening, "start should put the listener in listening state")
    assert_equal(owner.enabled, [("Network", {})], "start should enable the Network domain once")
    assert_true(callable(owner.callbacks["Network.webSocketCreated"]),
                "WebSocket-only listeners should register websocket callbacks")
    assert_false("Network.requestWillBeSent" in owner.callbacks,
                 "WebSocket-only listeners should not register HTTP request callbacks")

    listener._caught.put("retained")
    listener.pause(clear=False)
    assert_false(listener.listening, "pause should leave listening state")
    assert_equal(listener._caught.get_nowait(), "retained", "pause(clear=False) should preserve queued packets")
    assert_true(all(callback is None for callback in owner.callbacks.values()),
                "pause should unregister every callback that was installed")

    listener.start()
    listener._caught.put("discarded")
    listener.stop()
    assert_false(listener.listening, "stop should leave listening state")
    assert_true(listener._caught.empty(), "stop should clear queued packets")
    assert_equal(owner.disabled, ["Network"], "stop should disable the Network domain")

    listener.clear()
    listener.listening = True
    listener._caught.put("first")
    assert_equal(listener.wait(timeout=0.01), "first", "wait should return one available packet directly")
    listener._caught.put("one")
    listener._caught.put("two")
    assert_equal(listener.wait(count=2, timeout=0.01), ["one", "two"],
                 "wait should preserve queue order for multiple packets")
    listener._caught.put("partial")
    assert_equal(listener.wait(count=2, timeout=0.001, fit_count=False), ["partial"],
                 "fit_count=False should return a partial packet list at timeout")
    assert_false(listener.wait(timeout=0.001), "empty wait timeouts should return False by default")
    _expect_error(WaitTimeoutError, lambda: listener.wait(timeout=0.001, raise_err=True),
                  "raise_err=True should turn an empty wait timeout into WaitTimeoutError")

    listener._caught.put("step-1")
    listener._caught.put("step-2")
    assert_equal(list(listener.steps(count=2, timeout=0.1)), ["step-1", "step-2"],
                 "steps should yield queued packets in order and stop at count")
    listener._caught.put("batch-1")
    listener._caught.put("batch-2")
    assert_equal(list(listener.steps(count=2, timeout=0.1, gap=2)), [["batch-1", "batch-2"]],
                 "steps should yield fixed-size batches when gap is greater than one")

    listener._running_requests = 0
    listener._running_targets = 0
    assert_true(listener.wait_silent(timeout=0.01),
                "wait_silent should succeed immediately when no requests are active")
    listener._running_requests = 1
    assert_false(listener.wait_silent(timeout=0.001),
                 "wait_silent should time out while the active-request count exceeds the limit")
    assert_true(listener.wait_silent(timeout=0.01, limit=1),
                "wait_silent limit should permit the configured number of active requests")

    browser_queue = Queue()
    browser_queue.put("browser-one")
    browser_listen = SimpleNamespace(listening=True, _caught={owner.tab_id: browser_queue}, start=lambda: None)
    owner.browser = SimpleNamespace(listen=browser_listen)
    assert_equal(listener.browser_wait(timeout=0.01), "browser-one",
                 "browser_wait should return an immediately available tab packet")
    browser_queue.put("browser-step-1")
    browser_queue.put("browser-step-2")
    assert_equal(list(listener.browser_steps(count=2, timeout=0.1)), ["browser-step-1", "browser-step-2"],
                 "browser_steps should yield the current tab queue in order")


def _check_http_event_correlation():
    owner = _Owner()
    listener = Listener(owner)
    owner.listen = listener
    owner.response_bodies["http-1"] = {"body": '{"ok": true}', "base64Encoded": False}
    listener.start("/api")

    listener._requestWillBeSent(
        requestId="http-1",
        frameId="frame-http",
        type="Fetch",
        request={
            "url": "https://example.test/api?id=7",
            "method": "GET",
            "headers": {"Accept": "application/json"},
            "timestamp": 40.0,
            "hasPostData": False,
        },
    )
    listener._requestWillBeSentExtraInfo(
        requestId="http-1",
        headers={"X-Request-Extra": "yes"},
        associatedCookies=[],
    )
    listener._response_received(
        requestId="http-1",
        type="Fetch",
        timestamp=41.0,
        response={"url": "https://example.test/api?id=7", "status": 200,
                  "headers": {"Content-Type": "application/json"}},
    )
    listener._responseReceivedExtraInfo(
        requestId="http-1", headers={"X-Response-Extra": "yes"}, statusCode=200
    )
    listener._loading_finished(requestId="http-1")

    packet = listener.wait(timeout=0.01)
    assert_true(isinstance(packet, DataPacket), "normal HTTP callbacks should enqueue a DataPacket")
    assert_equal(packet.target, ("/api", "GET", "Fetch"),
                 "HTTP callback correlation should retain matched target metadata")
    assert_equal(packet.frameId, "frame-http", "HTTP callback correlation should retain frame identity")
    assert_equal(packet.response.body, {"ok": True}, "loading completion should attach and parse the response body")
    assert_equal(packet.request.headers["x-request-extra"], "yes",
                 "request extra-info should correlate by request id")
    assert_equal(packet.response.headers["x-response-extra"], "yes",
                 "response extra-info should correlate by request id")
    assert_equal(listener._running_requests, 0, "completed HTTP callbacks should balance running request counts")
    assert_equal(listener._running_targets, 0, "completed target callbacks should balance running target counts")
    assert_false("http-1" in listener._request_ids, "completed requests should be removed from correlation state")
    assert_false("http-1" in listener._extra_info_ids,
                 "completed extra-info records should be removed from correlation state")
    assert_in(("Network.getResponseBody", {"requestId": "http-1", "_ignore": True}), owner.cdp_calls,
              "loading completion should retrieve the response body by request id")

def _check_websocket_and_sse_callbacks():
    owner = _Owner()
    listener = Listener(owner)
    owner.listen = listener
    listener.set_res_type.WebSocket(only=True)
    listener.start("/socket")
    listener._webSocketCreated(requestId="ws-callback", url="wss://example.test/socket",
                               initiator={"type": "script"})
    listener._webSocketWillSendHandshakeRequest(
        requestId="ws-callback", request={"headers": {"Upgrade": "websocket"}}, timestamp=50
    )
    listener._webSocketHandshakeResponseReceived(
        requestId="ws-callback", response={"status": 101}, timestamp=51
    )
    listener._webSocketFrameSent(
        requestId="ws-callback", timestamp=52,
        response={"opcode": 1, "payloadData": '{"direction": "sent"}'},
    )
    listener._webSocketFrameReceived(
        requestId="ws-callback", timestamp=53,
        response={"opcode": 1, "payloadData": '{"direction": "received"}'},
    )
    sent, received = listener.wait(count=2, timeout=0.01)
    assert_true(sent.is_sent, "sent websocket callbacks should mark packet direction")
    assert_false(received.is_sent, "received websocket callbacks should mark packet direction")
    assert_equal(sent.data, {"direction": "sent"}, "sent websocket callback payload should parse")
    assert_equal(received.data, {"direction": "received"}, "received websocket callback payload should parse")
    assert_equal(sent.url, "wss://example.test/socket", "websocket callbacks should attach connection metadata")
    assert_equal(sent.request["request"]["headers"]["Upgrade"], "websocket",
                 "websocket callbacks should attach handshake request data")
    assert_equal(sent.response["response"]["status"], 101,
                 "websocket callbacks should attach handshake response data")
    listener._webSocketClosed(requestId="ws-callback")
    assert_false("ws-callback" in listener._ws_info, "closed websocket ids should leave correlation state")

    listener.stop()
    listener.set_res_type.EventSource(only=True)
    listener.start("/events")
    listener._requestWillBeSent(
        requestId="sse-callback", frameId="frame-events", type="EventSource",
        request={
            "url": "https://example.test/events", "method": "GET", "headers": {},
            "timestamp": 60.0, "hasPostData": False,
        },
    )
    listener._eventSourceMessageReceived(
        requestId="sse-callback", timestamp=61.0, eventName="message", eventId="9", data="ready"
    )
    event = listener.wait(timeout=0.01)
    assert_true(isinstance(event, SSEPacket), "EventSource callbacks should enqueue SSEPacket values")
    assert_equal(event.url, "https://example.test/events", "SSE callbacks should attach request URL data")
    assert_equal(event.method, "GET", "SSE callbacks should attach request method data")
    assert_equal(event.frameId, "frame-events", "SSE callbacks should attach request frame data")
    assert_equal(event.data, "ready", "SSE callbacks should retain event data")


def _check_browser_data_packet_contracts():
    raw = {
        "requestId": "fetch-1",
        "frameId": "frame-fetch",
        "resourceType": "XHR",
        "request": {
            "url": "https://example.test/browser-api?item=7&blank=",
            "method": "POST",
            "postDataEntries": [{"bytes": b64encode(b'{"name": "browser"}').decode()}],
        },
        "responseHeaders": [{"name": "Content-Type", "value": "application/json"}],
        "responseStatusCode": 202,
        "responseStatusText": "Accepted",
        "body": {"body": b64encode(b'{"queued": true}').decode(), "base64Encoded": True},
    }
    packet = BrowserDataPacket("tab-fetch", ("/browser-api", "POST", "XHR"), raw)
    assert_equal(packet.url, "https://example.test/browser-api?item=7&blank=",
                 "BrowserDataPacket should expose the intercepted URL")
    assert_equal(packet.method, "POST", "BrowserDataPacket should expose the intercepted method")
    assert_equal(packet.frameId, "frame-fetch", "BrowserDataPacket should expose the intercepted frame id")
    assert_equal(packet.resourceType, "XHR", "BrowserDataPacket should expose the intercepted resource type")
    assert_equal(packet.request.params, {"item": "7", "blank": ""},
                 "BrowserDataPacket request params should preserve blank values")
    assert_equal(packet.request.postData, {"name": "browser"},
                 "BrowserDataPacket postDataEntries should decode JSON")
    assert_equal(packet.response.statusCode, 202, "BrowserDataPacket should expose the response status code")
    assert_equal(packet.response.statusText, "Accepted", "BrowserDataPacket should expose the response status text")
    assert_equal(packet.response.headers["content-type"], "application/json",
                 "BrowserDataPacket response headers should be case-insensitive")
    assert_equal(packet.data, {"queued": True}, "base64 BrowserDataPacket response bodies should decode JSON")
    assert_false(packet.is_failed, "responses without responseErrorReason should not be marked failed")
    assert_equal(packet.timestamp, None, "BrowserDataPacket should expose its documented empty timestamp")
    assert_in("BrowserDataRacket", repr(packet), "BrowserDataPacket repr should remain readable")

    failed_raw = dict(raw, responseErrorReason="Failed")
    failed_packet = BrowserDataPacket("tab-fetch", True, failed_raw)
    assert_true(failed_packet.is_failed, "responseErrorReason should mark BrowserDataPacket failures")
    assert_equal(failed_packet.response.errorReason, "Failed", "browser response errors should remain available")


def _expect_error(error_type, action, message):
    try:
        action()
    except error_type:
        return
    except Exception as exc:
        raise AssertionError(f"{message}: expected {error_type.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"{message}: expected {error_type.__name__}")
