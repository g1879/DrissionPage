#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the custom runner's classification, redaction, and report semantics."""
from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

import runner
from support import TestContext, TestResult


class Case:
    def __init__(self, name: str, features=()):
        self.name = name
        self.title = name
        self.requires_browser = False
        self.features = tuple(features)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def build(results, cases):
    with tempfile.TemporaryDirectory(prefix="dp-runner-quality-") as tmp:
        ctx = TestContext(include_browser=False, artifacts_dir=Path(tmp))
        return runner.build_report(results, cases, time.perf_counter(), ctx, suite="all")


def test_failed_cases_do_not_count_as_coverage() -> None:
    case = Case("api_surface", ("chromium_entrypoint",))
    report = build([TestResult("api_surface", "failed", 0.01, "known failure")], [case])
    summary = report["summary"]
    require(summary["features_executed"] > 0, "failed cases should still count as executed diagnostics")
    require(summary["features_covered_by_run"] == 0, "failed cases must not count as covered features")
    statuses = {feature["status"] for feature in report["features"] if feature["case"] == "api_surface"}
    require(statuses == {"executed-failed"}, "failed feature status should remain explicit")


def test_passed_cases_count_as_coverage() -> None:
    case = Case("navigation_result", ("nav_result",))
    report = build([TestResult("navigation_result", "passed", 0.01)], [case])
    require(report["summary"]["features_covered_by_run"] >= 1, "passed feature cases should count as covered")


def test_sensitive_values_are_redacted() -> None:
    old = os.environ.get("DP_TEST_SITE_URL")
    os.environ["DP_TEST_SITE_URL"] = "https://secret.example.test/path"
    try:
        value = runner.redact_sensitive({"url": "https://secret.example.test/path/api", "host": "secret.example.test"})
        require("secret.example.test" not in repr(value), "fixture URLs and hosts must be redacted")
        require("<fixture-url-redacted>" in repr(value), "redaction marker should be visible")
    finally:
        if old is None:
            os.environ.pop("DP_TEST_SITE_URL", None)
        else:
            os.environ["DP_TEST_SITE_URL"] = old


def test_case_selection_and_suite_classification() -> None:
    selected = runner.normalize_case_names(["navigation_result.py", "sse_packet"])
    require("navigation_result" in selected, "file-like case names should normalize to their stem")
    require("listener_ws_sse" in selected, "feature aliases should normalize to their owning case")
    require(runner.case_suite(Case("session_timeout")) == "stable", "unlisted cases should be stable")
    require(runner.case_suite(Case("api_surface")) == "known", "known issues should stay report-only")
    require(runner.case_suite(Case("feature_optional_online_smoke")) == "local", "online smoke should stay local")


def main() -> int:
    test_failed_cases_do_not_count_as_coverage()
    test_passed_cases_count_as_coverage()
    test_sensitive_values_are_redacted()
    test_case_selection_and_suite_classification()
    print("Runner quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
