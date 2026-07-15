# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestCase, TestContext, TestFailure, assert_equal, chromium, html, local_server


def assert_found_id(tab, locator: str, expected_id: str) -> None:
    ele = tab.ele(locator, timeout=1)
    assert_equal(ele.attr("id"), expected_id, f"{locator!r} should find expected element")


def assert_not_found(tab, locator: str) -> None:
    from DrissionPage.errors import ElementNotFoundError

    try:
        ele = tab.ele(locator, timeout=.5)
    except ElementNotFoundError:
        return
    if not ele:
        return
    raise TestFailure(f"{locator!r} should not fall back to text search, got id={ele.attr('id')!r}")


def run(ctx: TestContext) -> None:
    routes = {
        "/locator-explicit": lambda _req: html("""
            <body>
              <p id='text'>//missing .absent #absent</p>
              <section>
                <div id='target' class='present'>ok</div>
                <div id='second'>two</div>
              </section>
            </body>
        """, title="locator explicit"),
    }
    with local_server(routes) as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        nav = tab.get(base + "/locator-explicit")
        if nav is not True and bool(nav) is not True:
            raise TestFailure(f"locator page navigation failed: {nav!r}")

        assert_found_id(tab, 'xpath://div[@id="target"]', "target")
        assert_found_id(tab, 'x://div[@id="target"]', "target")
        assert_found_id(tab, "css:#target", "target")
        assert_found_id(tab, "#target", "target")
        assert_found_id(tab, ".present", "target")
        assert_found_id(tab, "#=target", "target")
        assert_found_id(tab, ".:present", "target")

        assert_not_found(tab, "xpath://missing")
        assert_not_found(tab, "x://missing")
        assert_not_found(tab, "//missing")
        assert_not_found(tab, "css:.absent")
        assert_not_found(tab, "#absent")
        assert_not_found(tab, ".absent")

        # Bare/any locators intentionally keep text fallback behavior.
        assert_found_id(tab, "absent", "text")


TEST_CASE = TestCase(
    name="locator_explicit_syntax",
    title="Explicit xpath/css locators do not fall back to text search",
    requires_browser=True,
    features=("locator_explicit_syntax",),
    run=run,
)
