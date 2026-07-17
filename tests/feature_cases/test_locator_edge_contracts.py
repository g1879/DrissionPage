"""Feature: deterministic locator conversion edge contracts."""
from __future__ import annotations

from DrissionPage._functions.by import By
from DrissionPage._functions.locator import (
    get_loc,
    locator_to_tuple,
    str_to_ax_loc,
    str_to_css_loc,
    str_to_xpath_loc,
    translate_css_loc,
    translate_loc,
)
from DrissionPage.errors import LocatorError

from support import assert_equal, assert_true


FEATURE_ID = "locator_edge_contracts"
REQUIRES_BROWSER = False


def _expect_raises(exc_type, func, *args):
    try:
        func(*args)
    except exc_type:
        return
    raise AssertionError(f"{func.__name__}() should raise {exc_type.__name__}")


def test_single_locator_forms():
    cases = (
        ("@name", ("xpath", "//*[@name]"), ("css selector", "*[name]")),
        ("@name:value", ("xpath", '//*[contains(@name,"value")]'), ("css selector", "*[name*=value]")),
        ("@name^pre", ("xpath", '//*[starts-with(@name,"pre")]'), ("css selector", "*[name^=pre]")),
        ("@name$suf", ("xpath", '//*[substring(@name, string-length(@name) - string-length("suf") +1) = "suf"]'),
         ("css selector", "*[name$=suf]")),
        ("@text()=hello", ("xpath", '//*[text()="hello"]'), ("xpath", '//*[text()="hello"]')),
        ("@text():ell", ("xpath", '//*/text()[contains(., "ell")]/..'),
         ("xpath", '//*/text()[contains(., "ell")]/..')),
        ("@text()^he", ("xpath", '//*/text()[starts-with(., "he")]/..'),
         ("xpath", '//*/text()[starts-with(., "he")]/..')),
        ("@text()$lo", ("xpath", '//*/text()[substring(., string-length(.) - string-length("lo") +1) = "lo"]/..'),
         ("xpath", '//*/text()[substring(., string-length(.) - string-length("lo") +1) = "lo"]/..')),
        ("@tag()=DIV", ("xpath", '//*[name()="div"]'), ("css selector", "DIV")),
        ("text^hello", ("xpath", '//*/text()[starts-with(., "hello")]/..'),
         ("xpath", '//*/text()[starts-with(., "hello")]/..')),
        ("text$hello", ("xpath", '//*/text()[substring(., string-length(.) - string-length("hello") +1) = "hello"]/..'),
         ("xpath", '//*/text()[substring(., string-length(.) - string-length("hello") +1) = "hello"]/..')),
        ("c:div", ("css selector", "div"), ("css selector", "div")),
        ("x://div", ("xpath", "//div"), ("xpath", "//div")),
    )
    for locator, xpath_expected, css_expected in cases:
        assert_equal(str_to_xpath_loc(locator), xpath_expected, f"XPath conversion mismatch for {locator}")
        assert_equal(str_to_css_loc(locator), css_expected, f"CSS conversion mismatch for {locator}")

    tuple_cases = (
        ("@name", {"and": True, "args": [["name", None, None, False]]}),
        ("@name:value", {"and": True, "args": [["name", ":", "value", False]]}),
        ("@text()^he", {"and": True, "args": [["text()", "^", "he", False]]}),
        ("text$hello", {"and": True, "args": [["text()", "$", "hello", False]]}),
        ("plain", {"and": True, "args": [["text()", "=", "plain", False]]}),
    )
    for locator, expected in tuple_cases:
        assert_equal(locator_to_tuple(locator), expected, f"tuple conversion mismatch for {locator}")


def test_multi_locator_forms():
    cases = (
        ("@@name=value@@title:hi", ("xpath", '//*[@name="value" and contains(@title,"hi")]'),
         ("css selector", "*[name=value][title*=hi]")),
        ("@|name=value@|title=hi", ("xpath", '//*[@name="value" or @title="hi"]'),
         ("css selector", "*[name=value],*[title=hi]")),
        ("@!name=value", ("xpath", '//*[not(@name="value")]'), ("css selector", "*:not([name=value])")),
        ("tag:DIV@name=value", ("xpath", '//*[name()="DIV" and @name="value"]'),
         ("css selector", "DIV[name=value]")),
        ("tag:DIV@@name=value@@title:hi",
         ("xpath", '//*[(name()="DIV") and (@name="value" and contains(@title,"hi"))]'),
         ("css selector", "DIV[name=value][title*=hi]")),
        ("tag:DIV@|name=value@|title=hi",
         ("xpath", '//*[(name()="DIV") and (@name="value" or @title="hi")]'),
         ("css selector", "DIV[name=value],DIV[title=hi]")),
        ("tag:DIV@!name=value", ("xpath", '//*[(name()="DIV") and (not(@name="value"))]'),
         ("css selector", "DIV:not([name=value])")),
        ("@@tag()=DIV@@name=x", ("xpath", '//*[(name()="DIV") and (@name="x")]'),
         ("css selector", "DIV[name=x]")),
        ("@@text():hi@@name=x", ("xpath", '//*[contains(.,"hi") and @name="x"]'),
         ("css selector", '//*[contains(.,"hi") and @name="x"]')),
    )
    for locator, xpath_expected, css_expected in cases:
        assert_equal(str_to_xpath_loc(locator), xpath_expected, f"multi XPath mismatch for {locator}")
        assert_equal(str_to_css_loc(locator), css_expected, f"multi CSS mismatch for {locator}")

    assert_equal(locator_to_tuple("tag:DIV@!name=value"), {
        "and": True,
        "args": [["name", "=", "value", True], ["tag()", "=", "div", False]],
    }, "tag plus negated attribute tuple should preserve both clauses")
    _expect_raises(LocatorError, str_to_xpath_loc, "@@name=x@|title=y")
    _expect_raises(LocatorError, str_to_css_loc, "@@name=x@|title=y")
    _expect_raises(LocatorError, locator_to_tuple, "@@name=x@|title=y")


def test_selenium_and_ax_edges():
    translate_cases = (
        ((By.XPATH, "//main"), ("xpath", "//main"), ("xpath", "//main")),
        ((By.CSS_SELECTOR, "main > div"), ("css selector", "main > div"), ("css selector", "main > div")),
        ((By.CLASS_NAME, "a b"), ("xpath", '//*[@class="a b"]'), ("css selector", r".a\ b")),
        ((By.LINK_TEXT, "Home"), ("xpath", '//a[text()="Home"]'), ("xpath", '//a[text()="Home"]')),
        ((By.NAME, "q"), ("xpath", '//*[@name="q"]'), ("css selector", "*[@name=q]")),
        ((By.PARTIAL_LINK_TEXT, "om"), ("xpath", '//a[contains(text(),"om")]'),
         ("xpath", '//a[contains(text(),"om")]')),
    )
    for locator, xpath_expected, css_expected in translate_cases:
        assert_equal(translate_loc(locator), xpath_expected, f"translate_loc mismatch for {locator}")
        assert_equal(translate_css_loc(locator), css_expected, f"translate_css_loc mismatch for {locator}")

    assert_equal(get_loc("css:div.item", translate_css=True),
                 ("xpath", "div[@class and contains(concat(' ', normalize-space(@class), ' '), ' item ')]"),
                 "valid CSS should translate to XPath when requested")
    assert_equal(get_loc("css:div > span", translate_css=True), ("xpath", "div/span"),
                 "child CSS combinator should translate to XPath")
    assert_equal(str_to_ax_loc("ax:@role=button@name: Save @description=ignored"),
                 ("ax", {"role": "button", "accessibleName": "Save"}),
                 "AX parsing should trim supported fields and ignore unsupported fields")
    assert_equal(str_to_ax_loc("ax:invalid@role"), ("ax", {}),
                 "AX fields without separators should be ignored")

    for func in (translate_loc, translate_css_loc):
        _expect_raises(LocatorError, func, ("bad", "value"))
        _expect_raises(LocatorError, func, (By.ID, "value", "extra"))
    assert_true(get_loc("@name") == ("xpath", "//*[@name]"), "get_loc should retain valid attribute locators")


def run(ctx):
    test_single_locator_forms()
    test_multi_locator_forms()
    test_selenium_and_ax_edges()
