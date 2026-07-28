"""Feature: non-finite JavaScript arguments use the CDP Runtime.CallArgument contract."""
from __future__ import annotations

import json
from math import inf, nan
from urllib.request import urlopen

from feature_cases.browser_interaction_server import browser_interaction_server
from support import assert_equal, assert_true, chromium

FEATURE_ID = "cdp_argument_values"
FEATURES = ("cdp_nonfinite_argument_browser",)
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("CDP argument-value checks skipped by --skip-browser")

    with browser_interaction_server() as base, chromium(ctx) as browser:
        version = browser._run_cdp("Browser.getVersion")
        assert_true(version.get("product"), "Browser.getVersion should identify the tested Chromium build")
        with urlopen(f"http://{browser.address}/json/protocol", timeout=ctx.timeout) as response:
            protocol = json.load(response)
        runtime = next(domain for domain in protocol["domains"] if domain["domain"] == "Runtime")
        call_argument = next(item for item in runtime["types"] if item["id"] == "CallArgument")
        argument_fields = {item["name"] for item in call_argument["properties"]}
        assert_true(
            "unserializableValue" in argument_fields,
            f"{version['product']} Runtime.CallArgument should support unserializableValue",
        )

        tab = browser.latest_tab
        assert_true(tab.get(base + "/main"), "CDP argument test page should load")

        assert_true(
            tab.run_js("function(value){return value === Infinity;}", inf),
            "run_js() should deliver positive infinity through CDP",
        )
        assert_true(
            tab.run_js("function(value){return value === -Infinity;}", -inf),
            "run_js() should deliver negative infinity through CDP",
        )
        assert_true(
            tab.run_js("function(value){return Number.isNaN(value);}", nan),
            "run_js() should deliver NaN through CDP",
        )
        assert_true(
            tab.run_js("function(value){return Object.is(value, -0);}", -0.0),
            "run_js() should preserve negative zero through CDP",
        )
        assert_equal(
            tab.run_js("function(value){return value.answer;}", {"answer": 42}),
            42,
            "ordinary serializable object arguments should remain unchanged",
        )
