"""Feature: find() and browser s_ele()/s_eles() contracts."""
from __future__ import annotations

from DrissionPage._elements.session_element import make_session_ele
from feature_cases.browser_interaction_server import browser_interaction_server
from support import assert_equal, assert_true, chromium

FEATURE_ID = "find_api"
REQUIRES_BROWSER = True


def run(ctx):
    _check_session_find_contracts()
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed find contracts skipped by --skip-browser")
    _check_browser_find_contracts(ctx)


def _check_session_find_contracts() -> None:
    document = """
      <html><body>
        <section id='root'>
          <article class='card' data-kind='a'><span class='name'>alpha</span></article>
          <article class='card' data-kind='b'><span class='name'>beta</span></article>
        </section>
      </body></html>
    """
    ele = make_session_ele(document)
    key, found = ele.find((".missing", ".card"), any_one=True, first_ele=True)
    assert_equal(key, ".card", "SessionElement.find(any_one=True) should return first matching locator key")
    assert_equal(found.attr("data-kind"), "a", "SessionElement.find() should return a real matching element")
    all_found = ele.find((".card", ".name"), any_one=False, first_ele=False)
    assert_equal(len(all_found[".card"]), 2, "SessionElement.find(first_ele=False) should return all matching cards")
    assert_equal(len(all_found[".name"]), 2, "SessionElement.find(first_ele=False) should return all matching names")
    parent = all_found[".name"][1].parent(".card", index=1)
    assert_equal(parent.attr("data-kind"), "b", "parent(locator, index=...) should select the matching ancestor")


def _check_browser_find_contracts(ctx) -> None:
    with browser_interaction_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/main"), "find test page should load")
        key, found = tab.find(("#missing", "#primary", "#secondary"), any_one=True, first_ele=True, timeout=2)
        assert_equal(key, "#primary", "Tab.find(any_one=True) should return first matching locator key")
        assert_equal(found.attr("id"), "primary", "Tab.find(any_one=True) should return the matching element")
        all_found = tab.find(("button", "#secondary"), any_one=False, first_ele=False, timeout=2)
        assert_true(len(all_found["button"]) >= 1, "Tab.find(first_ele=False) should return matching regular button elements")
        assert_equal(all_found["#secondary"][0].attr("id"), "secondary", "Tab.find(any_one=False) should include locator-specific results")
        assert_equal(tab.s_ele("#primary", timeout=2).text, "primary", "browser s_ele(timeout=...) should return a session element snapshot")
        assert_true(len(tab.s_eles("tag:button", timeout=2)) >= 2, "browser s_eles(timeout=...) should return session element snapshots")
