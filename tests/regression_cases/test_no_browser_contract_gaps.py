# -*- coding: utf-8 -*-
"""Report-only repros for confirmed deterministic no-browser contract gaps."""
from __future__ import annotations

from math import inf
from types import SimpleNamespace

from DrissionPage import SessionOptions
from DrissionPage._base.base import BaseParser
from DrissionPage._browsers.chromium import Tabs
from DrissionPage._elements.chromium_element import convert_argument
from DrissionPage._functions.elements import SessionElementsList
from DrissionPage._pages.chromium_tab import ChromiumTab
from DrissionPage._pages.session_page import set_charset
from DrissionPage._units.listener import Listener
from requests import Response

from support import TestCase, TestContext, TestFailure


def run(ctx: TestContext) -> None:
    issues = []

    options = SessionOptions(read_file=False)
    try:
        result = options.add_adapter("mock://", object())
        if result is not options:
            issues.append("SessionOptions.add_adapter() should remain chainable")
    except Exception as exc:
        issues.append(f"SessionOptions.add_adapter() raised {type(exc).__name__}: {exc}")

    owner = type("Owner", (), {"_none_ele_value": None, "_none_ele_return_value": False})()
    try:
        texts = SessionElementsList(owner, ["text node"]).texts
        if texts != ["text node"]:
            issues.append(f"SessionElementsList.texts returned an unexpected value: {texts!r}")
    except Exception as exc:
        issues.append(f"SessionElementsList.texts crashed on a text node: {type(exc).__name__}: {exc}")

    response = Response()
    response._content = b"<html></html>"
    response.headers["content-type"] = "text/html; charset=utf-8"
    set_charset(response)
    if response.encoding != "utf-8":
        issues.append(f"set_charset() retained an invalid charset token: {response.encoding!r}")

    if convert_argument(inf) != {"unserializableValue": "Infinity"}:
        issues.append(f"convert_argument(inf) produced {convert_argument(inf)!r} instead of CDP Infinity")

    class Parser(BaseParser):
        _type = "SessionParser"
        timeout = 0

        def _ele(self, locator, **kwargs):
            return locator

    try:
        Parser().find((("id", "one"), ("id", "two")), any_one=False, timeout=0)
    except Exception as exc:
        issues.append(f"find() crashed on two locator tuples: {type(exc).__name__}: {exc}")

    mode_calls = []
    tab = object.__new__(ChromiumTab)
    tab._d_mode = False
    tab._session = object()
    tab._timeouts = SimpleNamespace(page_load=5)
    tab._mode_obj = SimpleNamespace(post=lambda *args, **kwargs: mode_calls.append(kwargs) or True)
    tab.post("https://example.test", timeout=3)
    if mode_calls[-1].get("timeout") != 3:
        issues.append(f"ChromiumTab.post(timeout=3) forwarded timeout={mode_calls[-1].get('timeout')!r}")

    listener = object.__new__(Listener)
    listener._running_requests = 1
    packet = SimpleNamespace(_raw_fail_info=None, _resource_type=None, is_failed=False)
    listener._request_ids = {"request-1": packet}
    listener._extra_info_ids = {}
    result = listener._loading_failed_sse(requestId="request-1", type="Fetch", errorText="failed")
    if result is not packet:
        issues.append("Listener._loading_failed_sse() did not return the failed packet for queueing")

    tabs = Tabs()
    tabs.add("session-1", "target-1", context_id="context-1", obj=SimpleNamespace(_stop_messenger=lambda: None))
    tabs.add("session-2", "target-1", context_id="context-1", obj=SimpleNamespace(_stop_messenger=lambda: None))
    try:
        tabs.stop_target("target-1")
    except RuntimeError as exc:
        issues.append(f"Tabs.stop_target() mutated sessions during iteration: {exc}")

    stale = Tabs()
    stale.add("session", "target", context_id="context")
    stale.set_newest_tab("context", "target")
    stale.set_proxy("context", ("proxy", None, None, None))
    stale.clear()
    if stale._contexts or stale._context_newest_tab or stale._proxies:
        issues.append("Tabs.clear() left stale context/newest-tab/proxy bookkeeping")

    if issues:
        raise TestFailure("Confirmed no-browser contract gaps:\n- " + "\n- ".join(issues))


TEST_CASE = TestCase(
    name="no_browser_contract_gaps",
    title="Confirmed deterministic no-browser contract gaps",
    requires_browser=False,
    features=("session_options_adapter", "session_elements_text_nodes", "charset_parsing", "cdp_infinity",
              "find_locator_tuple", "tab_post_timeout", "listener_failed_packet", "tabs_cleanup"),
    run=run,
)
