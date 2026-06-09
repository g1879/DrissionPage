# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestFailure, TestCase, TestContext, chromium, local_server
from support import function_accepts


def set_checked(checkbox, checked: bool) -> None:
    if function_accepts(checkbox.check, "checked"):
        checkbox.check(checked=checked, by_js=True)
    else:
        checkbox.check(uncheck=not checked, by_js=True)


def run(ctx: TestContext) -> None:
    errors: list[str] = []
    with local_server() as (base, _server), chromium(ctx) as browser:
        tab = browser.latest_tab
        tab.get(base + "/page/locator")

        def check_ele(label: str, ele, expected_id: str):
            got = ele.attr("id") if ele else None
            if got != expected_id:
                errors.append(f"{label}: expected id={expected_id!r}, got {got!r}, ele={ele!r}")

        check_ele("auto XPath //div[@id=target]", tab.ele('//div[@id="target"]'), "target")
        check_ele("explicit XPath x://div[@id=target]", tab.ele('x://div[@id="target"]'), "target")
        check_ele("auto CSS .needle", tab.ele(".needle"), "target")
        text_ele = tab.ele("target div")
        if not text_ele or getattr(text_ele, "tag", None) == "text":
            errors.append(f"auto text locator should return element, got {text_ele!r}")

        text_node = tab.ele("x://body/text()")
        if isinstance(text_node, str):
            errors.append(f"ChromiumTab.ele() should not return str text nodes in 4.2, got {text_node!r}")

        check_ele("ax locator", tab.ele("ax:@name=Save Now@role=button"), "save")
        check_ele("element-scoped ax locator", tab.ele("tag:main").ele("ax:@name=Save Now@role=button"), "save")

        numeric = tab.ele("#123abc")
        check_ele("numeric-start id CSS", numeric, "123abc")
        if numeric:
            selector = numeric.css_selector
            if "123abc" not in selector and "\\31" not in selector:
                errors.append(f"numeric id css_selector should include escaped id, got {selector!r}")

        checkbox = tab.ele("#check1")
        set_checked(checkbox, True)
        if checkbox.states.is_checked is not True:
            errors.append("check(checked=True) should check checkbox")
        set_checked(checkbox, False)
        if checkbox.states.is_checked is not False:
            errors.append("check(checked=False) should uncheck checkbox")

        svg_rect = tab.ele("#svgrect")
        try:
            svg_rect.click(by_js=True)
            if tab.run_js("return window.svgClicked") != 1:
                errors.append("SVG element JS click should trigger onclick")
        except Exception as exc:
            errors.append(f"SVG element JS click should not raise: {type(exc).__name__}: {exc}")

    if errors:
        raise TestFailure("Locator behavior mismatches:\n- " + "\n- ".join(errors))


TEST_CASE = TestCase(
    name="locator_behavior",
    title="AX locator, auto locator, text-node behavior, checkbox and SVG click fixes",
    requires_browser=True,
    features=("ax_locator", "auto_locator", "tab_no_text_str", "css_selector", "check_checked"),
    run=run,
)
