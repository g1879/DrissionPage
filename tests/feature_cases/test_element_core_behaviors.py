"""Feature: element locator, rect, state, input, select, and fallback contracts."""
from __future__ import annotations

from inspect import signature

from DrissionPage._elements.session_element import make_session_ele

from feature_cases.core_feature_server import core_feature_server
from support import assert_equal, assert_false, assert_true, chromium

FEATURE_ID = "element_core_behaviors"
REQUIRES_BROWSER = True


def run(ctx):
    _check_session_element_contracts()
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed element contracts skipped by --skip-browser")
    _check_browser_element_contracts(ctx)


def _check_session_element_contracts() -> None:
    document = """
      <section id='items'>
        <p id='one' class='item' data-kind='keep'>one</p>
        <p id='two' class='item' data-kind='drop'>two</p>
        <p id='three' class='item' data-kind='keep'>three</p>
      </section>
    """
    kept = make_session_ele(document, "tag:p@!data-kind=drop", index=None)
    assert_equal([item.attr("id") for item in kept], ["one", "three"], "@! negative locator should exclude matching attributes")
    first = make_session_ele(document, "#one")
    assert_equal(first.next(1).attr("id"), "two", "relative next(1) should use positional index")
    assert_equal(first.parent("#items", index=1).attr("id"), "items", "parent(locator, index=...) should find matching ancestor")


def _check_browser_element_contracts(ctx) -> None:
    with core_feature_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/elements"), "element test page should load")

        kept = tab.eles("tag:p@!data-kind=drop", timeout=ctx.timeout)
        assert_equal([item.attr("id") for item in kept], ["one", "three"], "browser @! negative locator should exclude matching attributes")
        assert_equal(tab("#one").next(1).attr("id"), "two", "browser relative next(1) should use positional index")

        text = tab("#text-input")
        text.input("typed-by-js", by_js=True)
        assert_equal(text.value, "typed-by-js", "element.input(by_js=True) should set input value")

        checkbox = tab("#check")
        checkbox.check(by_js=True)
        assert_true(checkbox.states.is_checked, "element.check() should check a checkbox")
        _set_checked(checkbox, False)
        assert_false(checkbox.states.is_checked, "element.check() should uncheck a checkbox")

        select = tab("#choices")
        option = tab("#opt-b")
        select.select.by_option(option)
        assert_true(option.states.is_selected, "select.by_option() should select the given option element")
        select.select.cancel_by_option(option)
        assert_false(option.states.is_selected, "select.cancel_by_option() should clear the given option element")

        box = tab("#box")
        assert_true(box.states.has_rect, "element states.has_rect should expose geometry availability")
        assert_true(box.wait.has_rect(timeout=ctx.timeout), "element wait.has_rect() should wait for geometry")
        assert_true(box.rect.size[0] > 0 and box.rect.size[1] > 0, "element rect.size should expose dimensions")
        box.scroll.to_center()
        assert_true(box.states.is_whole_in_viewport, "element scroll.to_center() should bring the element fully into viewport")
        assert_true(box == tab("#box"), "two handles for the same DOM node should compare equal")

        tab.set.NoneElement_value("missing-value")
        try:
            assert_equal(tab("#missing", timeout=0).text, "missing-value", "NoneElement_value should provide a safe fallback value")
        finally:
            tab.set.NoneElement_value(None, on_off=False)


def _set_checked(checkbox, checked: bool) -> None:
    """Use the current public checkbox API while keeping this 4.0 check behavior-focused."""
    params = signature(checkbox.check).parameters
    if "checked" in params:
        checkbox.check(checked=checked, by_js=True)
    else:
        checkbox.check(uncheck=not checked, by_js=True)
