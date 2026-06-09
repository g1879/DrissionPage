"""Feature: tab object management contracts."""
from __future__ import annotations

from feature_cases.core_feature_server import core_feature_server
from support import assert_equal, assert_false, assert_true, chromium, wait_until

FEATURE_ID = "tab_management"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed tab contracts skipped by --skip-browser")
    with core_feature_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/tab"), "tab test page should load")

        created = browser.new_tab(base + "/tab", background=True)
        try:
            assert_true(getattr(created, "tab_id", None), "new_tab(background=True) should return a tab object")
            assert_true(created.tab_id in browser.tab_ids, "new tab should be tracked by browser.tab_ids")
            assert_equal(created("#tab-ready", timeout=ctx.timeout).text, "tab ready", "background tab should be operable without switching")
            by_num = browser.get_tab(0)
            assert_true(getattr(by_num, "tab_id", None), "get_tab(0) should return a tab object by index")
            by_id = browser.get_tab(created.tab_id)
            assert_equal(by_id.tab_id, created.tab_id, "get_tab(id_or_num) should return the requested tab")
            created.close()
            wait_until(lambda: created.tab_id not in browser.tab_ids, timeout=ctx.timeout, desc="tab close")
        finally:
            try:
                if created.tab_id in browser.tab_ids:
                    created.close()
            except Exception:
                pass

        tab("#alert-button").click(by_js=True)
        wait_until(lambda: tab.states.has_alert, timeout=ctx.timeout, desc="tab alert")
        assert_equal(tab.handle_alert(timeout=ctx.timeout), "tab-alert", "tab.handle_alert() should handle its own dialog")
        assert_false(tab.states.has_alert, "tab states should reflect closed alert")
