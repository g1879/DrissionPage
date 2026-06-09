"""Feature: page object actions, states, waits, frames, and CDP helpers."""
from __future__ import annotations

from feature_cases.core_feature_server import core_feature_server
from support import assert_equal, assert_true, chromium, wait_until

FEATURE_ID = "page_object_basics"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed page-object contracts skipped by --skip-browser")
    with core_feature_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/page-object"), "page-object test page should load")
        assert_true(tab.states.is_alive, "page states should report an alive tab")
        assert_true(tab.wait.doc_loaded(timeout=ctx.timeout), "wait.doc_loaded() should confirm document readiness")
        assert_true(tab.wait.eles_loaded("#action-input", timeout=ctx.timeout), "wait.eles_loaded() should detect DOM")

        tab.run_js("document.querySelector('#action-input').focus();")
        assert_equal(tab.run_js("return document.activeElement.id"), "action-input", "test input should be focused before keyboard actions")
        tab.actions.input("abc")
        assert_equal(tab("#action-input").value, "abc", "built-in actions should type into the focused input")

        tab("#title-button").click(by_js=True)
        assert_true(tab.wait.title_change("changed-title", timeout=ctx.timeout), "wait.title_change() should observe the target title text")
        assert_true(tab.wait.url_change("#changed", timeout=ctx.timeout), "wait.url_change() should observe the target URL text")

        frame = tab.get_frame("frame", timeout=ctx.timeout)
        assert_true(frame.states.is_alive, "ChromiumFrame states should report an alive frame")
        assert_true(frame.rect.size[0] > 0 and frame.rect.size[1] > 0, "ChromiumFrame.rect.size should expose frame geometry")
        assert_equal(frame("#frame-ready").text, "frame ready", "frame object should query its own DOM")

        init_id = tab.add_init_js("window.__featureInit = 'ready';")
        assert_true(tab.get(base + "/init"), "init script page should load")
        assert_equal(tab.run_js("return window.__featureInit"), "ready", "add_init_js() should run before page scripts")
        tab.remove_init_js(init_id)

        tab.set.blocked_urls(base + "/blocked-data*")
        try:
            assert_true(tab.get(base + "/blocked"), "blocked-url page should load")
            wait_until(lambda: tab.run_js("return window.blockStatus"), timeout=ctx.timeout, desc="blocked fetch status")
            assert_equal(tab.run_js("return window.blockStatus"), "blocked", "set.blocked_urls() should block matching fetches")
        finally:
            tab.set.blocked_urls([])
