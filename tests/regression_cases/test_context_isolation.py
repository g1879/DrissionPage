# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestCase, TestContext, assert_equal, assert_true, chromium, local_server


def run(ctx: TestContext) -> None:
    with local_server() as (base, _server), chromium(ctx) as browser:
        assert_true(hasattr(browser, "new_context"), "Chromium.new_context() missing")
        c1 = browser.new_context()
        c2 = browser.new_context()
        try:
            t1 = c1.new_tab(base + "/ok")
            t2 = c2.new_tab(base + "/ok")
            t1.run_js("document.cookie='ctx_cookie=one; path=/'; localStorage.setItem('ctx_local','one'); sessionStorage.setItem('ctx_session','one');")
            t2.run_js("document.cookie='ctx_cookie=two; path=/'; localStorage.setItem('ctx_local','two'); sessionStorage.setItem('ctx_session','two');")
            assert_equal(t1.run_js("return document.cookie.includes('ctx_cookie=one')"), True, "context 1 cookie missing")
            assert_equal(t2.run_js("return document.cookie.includes('ctx_cookie=two')"), True, "context 2 cookie missing")
            assert_equal(t1.run_js("return localStorage.getItem('ctx_local')"), "one", "context 1 localStorage mismatch")
            assert_equal(t2.run_js("return localStorage.getItem('ctx_local')"), "two", "context 2 localStorage mismatch")
            assert_true("ctx_cookie=two" not in t1.run_js("return document.cookie"), "context 2 cookie leaked into context 1")
            assert_true("ctx_cookie=one" not in t2.run_js("return document.cookie"), "context 1 cookie leaked into context 2")

            assert_true(t1.tab_id in c1.tab_ids, "context 1 tab id missing from tab_ids")
            assert_true(t2.tab_id in c2.tab_ids, "context 2 tab id missing from tab_ids")
            assert_equal(c1.get_tab(t1.tab_id).tab_id, t1.tab_id, "context get_tab(id) mismatch")

            # Permissions setter should be exposed on both browser and BrowserContext.
            assert_true(hasattr(browser.set, "perm"), "browser.set.perm missing")
            assert_true(hasattr(c1.set, "perm"), "context.set.perm missing")
            browser.set.perm.camera()
            c1.set.perm.geolocation()
        finally:
            c1.close()
            c2.close()


TEST_CASE = TestCase(
    name="context_isolation",
    title="Independent browser contexts, storage/cookie isolation and permissions setters",
    requires_browser=True,
    features=("context_isolation", "permissions"),
    run=run,
)
