"""Feature: Chromium object tab-management contracts."""
from __future__ import annotations

from feature_cases.browser_interaction_server import browser_interaction_server
from support import assert_equal, assert_false, assert_true, chromium, wait_until

FEATURE_ID = "chromium_tab_management"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed Chromium tab contracts skipped by --skip-browser")
    with browser_interaction_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/main"), "Chromium tab test page should load")
        assert_true(tab.__class__.__name__.endswith("Tab"), "Chromium.latest_tab should return a Tab object")
        assert_false(tab.__class__.__name__.endswith("Page"), "Chromium should not return Page objects as tabs")

        extra = browser.new_tab(base + "/main", background=True)
        try:
            assert_true(extra.tab_id in browser.tab_ids, "new_tab(background=True) should create a controllable tab")
            by_num = browser.get_tab(0)
            assert_true(getattr(by_num, "tab_id", None), "get_tab(0) should return a tab object by tab order")
            found = browser.get_tab(extra.tab_id)
            assert_equal(found.tab_id, extra.tab_id, "get_tab(id) should return the matching tab")
            found.activate()
            wait_until(lambda: browser.latest_tab.tab_id == found.tab_id, timeout=2, desc="activated latest tab")
            found.close()
            wait_until(lambda: extra.tab_id not in browser.tab_ids, timeout=3, desc="closed extra tab")
        finally:
            try:
                if extra.tab_id in browser.tab_ids:
                    extra.close()
            except Exception:
                pass

        keep = browser.new_tab(base + "/main", background=True)
        other = browser.new_tab(base + "/main", background=True)
        try:
            keep_id = keep.tab_id
            other_id = other.tab_id
            keep.close(others=True)
            wait_until(lambda: keep_id in browser.tab_ids and other_id not in browser.tab_ids, timeout=3, desc="close(others=True) result")
            assert_equal(browser.get_tab(keep_id).tab_id, keep_id, "close(others=True) should keep the caller tab open")
        finally:
            for item in (keep, other):
                try:
                    if item.tab_id in browser.tab_ids:
                        item.close()
                except Exception:
                    pass
