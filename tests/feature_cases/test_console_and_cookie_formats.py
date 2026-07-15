"""Feature: console and CookiesList behavior contracts."""
from __future__ import annotations

import json

from feature_cases.browser_interaction_server import browser_interaction_server
from support import assert_equal, assert_in, assert_true, chromium

FEATURE_ID = "console_and_cookie_formats"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed console/cookie contracts skipped by --skip-browser")
    with browser_interaction_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/main"), "console/cookie test page should load")

        tab.console.start()
        try:
            tab.run_js("console.log('console-format-event', {ok:true});")
            packet = None
            for _ in range(10):
                candidate = tab.console.wait(timeout=0.5)
                if candidate is not False and "console-format-event" in str(getattr(candidate, "data", "")):
                    packet = candidate
                    break
            assert_true(packet is not None, "tab.console.wait() should receive the target console event")
            assert_true(hasattr(packet, "data"), "console event should expose data")
        finally:
            tab.console.stop()

        tab.set.cookies({"name": "server_cookie", "value": "two"})
        cookies = tab.cookies(all_domains=True)
        assert_equal(cookies.as_dict().get("server_cookie"), "two", "tab cookies should support as_dict()")
        assert_in("server_cookie=two", cookies.as_str(), "tab cookies should support as_str()")
        assert_true(any(c["name"] == "server_cookie" for c in json.loads(cookies.as_json())), "tab cookies should support as_json()")
