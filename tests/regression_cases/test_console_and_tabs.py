# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestCase, TestContext, assert_equal, assert_true, chromium, local_server, wait_until


def run(ctx: TestContext) -> None:
    with local_server() as (base, _server), chromium(ctx) as browser:
        tab = browser.latest_tab
        tab.console.start()
        tab.get(base + "/page/console")
        first = tab.console.wait(timeout=ctx.timeout)
        assert_true(first is not False, "console.wait() should return ConsoleData")
        assert_true(hasattr(first, "data"), "ConsoleData.data missing")
        messages = [first] + tab.console.messages
        assert_true(any((m.data.get("type") == "log" or m.data.get("level") == "info") for m in messages), "console log message not captured", messages=[m.data for m in messages])
        assert_true(any("args" in m.data or "text" in m.data for m in messages), "console payload should expose args/text", messages=[m.data for m in messages])
        tab.console.stop()

        hidden = browser.new_tab(base + "/ok", hidden=True)
        assert_true(hidden.tab_id, "hidden new_tab should return a tab with id")
        hidden_id = browser.get_tab(hidden.tab_id, as_id=True)
        assert_equal(hidden_id, hidden.tab_id, "get_tab(as_id=True) should return matching tab id")
        visible = browser.new_tab(base + "/page/nav")
        visible.activate()
        assert_equal(browser.latest_tab.tab_id, visible.tab_id, "activate() should make tab latest_tab")
        visible.close()
        hidden.close()


TEST_CASE = TestCase(
    name="console_and_tabs",
    title="Console listener payloads, hidden tabs, get_tab(as_id) and activate()",
    requires_browser=True,
    features=("console_listener", "hidden_tab", "get_tab_as_id", "tab_activate"),
    run=run,
)
