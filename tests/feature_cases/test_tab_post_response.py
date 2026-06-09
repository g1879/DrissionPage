"""Feature: Chromium tab post() Response contract."""
from __future__ import annotations

from feature_cases.browser_interaction_server import browser_interaction_server
from support import assert_equal, assert_true, chromium

FEATURE_ID = "tab_post_response"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed post response contract skipped by --skip-browser")
    with browser_interaction_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/main"), "post test page should load")
        response = tab.post(base + "/post", data="alpha=1", timeout=3)
        assert_true(hasattr(response, "status_code"), "Chromium tab post() should return a requests Response object in session mode")
        assert_equal(response.status_code, 200, "post() response status mismatch")
        assert_equal(response.json()["body"], "alpha=1", "post() should preserve request body")
