"""Feature: scroll and wait behavior contracts."""
from __future__ import annotations

from feature_cases.browser_interaction_server import browser_interaction_server
from support import assert_true, chromium

FEATURE_ID = "scroll_and_waits"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed scroll/wait contracts skipped by --skip-browser")
    with browser_interaction_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/main"), "scroll/wait test page should load")
        old_y = tab.run_js("return window.scrollY")
        tab.scroll.to_see("#scroll-target", center=True)
        new_y = tab.run_js("return window.scrollY")
        assert_true(new_y > old_y, "page scroll.to_see() should scroll toward target")
        target = tab.ele("#scroll-target")
        target.scroll.to_center()
        assert_true(target.states.is_whole_in_viewport or target.states.has_rect, "element scroll.to_center() should leave target measurable/in view")

        tab.wait(0.05)
        assert_true(tab.wait.eles_loaded("#primary", timeout=2), "wait.eles_loaded() should detect existing DOM element")
        tab.run_js("setTimeout(() => { document.title = '4.1 title changed'; }, 100)")
        assert_true(tab.wait.title_change("4.1 title changed", timeout=2), "wait.title_change() should detect the target title text")
        tab.run_js("setTimeout(() => { history.pushState({}, '', '#scroll-waits'); }, 100)")
        assert_true(tab.wait.url_change("#scroll-waits", timeout=2), "wait.url_change() should detect the target URL text")
