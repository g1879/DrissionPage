"""Feature: element multi-click behavior contract."""
from __future__ import annotations

from feature_cases.browser_interaction_server import browser_interaction_server
from support import assert_equal, assert_true, chromium

FEATURE_ID = "element_multi_click"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed multi-click contract skipped by --skip-browser")
    with browser_interaction_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/main"), "multi-click test page should load")
        clicked = tab.ele("#clicker")
        clicked.scroll.to_center()

        assert_true(clicked.click(by_js=True) is clicked, "element click(by_js=True) should return element for chaining")
        assert_equal(tab.run_js("return window.clickCount"), 1, "element click(by_js=True) should trigger the control click handler")
        tab.run_js("window.clickCount = 0; window.doubleClickCount = 0; window.clickDetails = []; window.doubleClickDetails = []")

        clicked.click()
        assert_equal(tab.run_js("return window.clickCount"), 1, "element real click() should trigger the control click handler")
        tab.run_js("window.clickCount = 0; window.doubleClickCount = 0; window.clickDetails = []; window.doubleClickDetails = []")

        clicked.click.multi(times=2)
        click_details = tab.run_js("return window.clickDetails")
        double_click_details = tab.run_js("return window.doubleClickDetails")
        assert_true(click_details, "element click.multi(times=2) should dispatch at least one click event")
        assert_true(2 in click_details,
                    "element click.multi(times=2) should expose browser double-click detail semantics",
                    click_details=click_details)
        assert_equal(tab.run_js("return window.doubleClickCount"), 1,
                     "element click.multi(times=2) should dispatch one dblclick event")
        assert_true(2 in double_click_details,
                    "element click.multi(times=2) dblclick event should carry detail=2",
                    double_click_details=double_click_details)
