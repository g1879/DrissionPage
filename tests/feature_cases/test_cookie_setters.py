"""Feature: cookie setter contracts."""
from __future__ import annotations

from DrissionPage import SessionPage

from feature_cases.core_feature_server import core_feature_server
from support import assert_equal, assert_false, assert_true, chromium

FEATURE_ID = "cookie_setters"
REQUIRES_BROWSER = True


def run(ctx):
    _check_session_cookie_setters()
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed cookie contracts skipped by --skip-browser")
    _check_browser_cookie_setters(ctx)


def _check_session_cookie_setters() -> None:
    page = SessionPage()
    try:
        page.set.cookies({"name": "session_one", "value": "1"})
        assert_equal(page.cookies(all_domains=True).as_dict().get("session_one"), "1", "SessionPage set.cookies() should accept one cookie")
        page.set.cookies.remove("session_one")
        assert_false("session_one" in page.cookies(all_domains=True).as_dict(), "SessionPage set.cookies.remove() should delete one cookie")
        page.set.cookies({"name": "session_two", "value": "2"})
        page.set.cookies.clear()
        assert_equal(page.cookies(all_domains=True).as_dict(), {}, "SessionPage set.cookies.clear() should clear cookies")
    finally:
        page.close()


def _check_browser_cookie_setters(ctx) -> None:
    with core_feature_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/cookies"), "cookie test page should load")
        tab.set.cookies({"name": "browser_one", "value": "1"})
        assert_equal(tab.cookies(all_domains=True).as_dict().get("browser_one"), "1", "tab set.cookies() should accept one cookie")
        tab.set.cookies.remove("browser_one")
        assert_false("browser_one" in tab.cookies(all_domains=True).as_dict(), "tab set.cookies.remove() should delete one cookie")
        tab.set.cookies({"name": "browser_two", "value": "2"})
        tab.set.cookies.clear()
        assert_false("browser_two" in tab.cookies(all_domains=True).as_dict(), "tab set.cookies.clear() should clear cookies")
