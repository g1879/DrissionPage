#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the custom runner's classification, redaction, and report semantics."""
from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
import os
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

import runner
import run as run_wrapper
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


def test_selected_case_collection_is_lazy() -> None:
    selected_module = "feature_cases.test_listener_data_contracts"
    imported: list[str] = []

    def fake_import(module_name: str):
        imported.append(module_name)
        if module_name != selected_module:
            raise AssertionError(f"unrelated test module was imported: {module_name}")
        return SimpleNamespace(FEATURE_ID="listener_data_contracts", run=lambda ctx: None)

    original_import = runner.importlib.import_module
    runner.importlib.import_module = fake_import
    try:
        cases = runner.load_cases({"feature_listener_data_contracts"})
    finally:
        runner.importlib.import_module = original_import

    require(imported == [selected_module], "selected case collection must import only its module")
    require([case.name for case in cases] == ["feature_listener_data_contracts"],
            "selected feature case should still be constructed")


def test_unknown_case_error_lists_all_available_cases() -> None:
    stderr = StringIO()
    with redirect_stderr(stderr):
        runner.print_unknown_case_error({"does_not_exist"}, [Case("feature_listener_data_contracts")])

    output = stderr.getvalue()
    require("feature_listener_data_contracts" in output, "loaded case names should remain visible")
    require("feature_proxy_credentials" in output,
            "lazy loading must not hide unrelated available cases from diagnostics")


def test_pre_release_probe_isolated_from_checkout() -> None:
    captured: dict[str, object] = {}

    def fake_run(*args, **kwargs):
        captured["args"] = args
        captured.update(kwargs)
        return SimpleNamespace(returncode=0)

    original_run = run_wrapper.subprocess.run
    old_pythonpath = os.environ.get("PYTHONPATH")
    old_pythonhome = os.environ.get("PYTHONHOME")
    os.environ["PYTHONPATH"] = "/tmp/current-checkout"
    os.environ["PYTHONHOME"] = "/tmp/current-python-home"
    try:
        run_wrapper.subprocess.run = fake_run
        require(run_wrapper._has_drissionpage(Path("/tmp/pre-venv/bin/python")),
                "a successful isolated import should report the package as installed")
    finally:
        run_wrapper.subprocess.run = original_run
        if old_pythonpath is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = old_pythonpath
        if old_pythonhome is None:
            os.environ.pop("PYTHONHOME", None)
        else:
            os.environ["PYTHONHOME"] = old_pythonhome

    probe_env = captured.get("env")
    require(isinstance(probe_env, dict), "pre-release probing must pass an explicit environment")
    require("PYTHONPATH" not in probe_env, "checkout PYTHONPATH must not affect pre-release probing")
    require("PYTHONHOME" not in probe_env, "host PYTHONHOME must not affect the pre-release venv")
    require("PATH" in probe_env, "ordinary process environment should remain available to the probe")
    command = captured["args"][0]
    require("-I" in command, "pre-release probing must ignore the working directory and user Python config")
    require("importlib.metadata" in command[-1] and "version('DrissionPage')" in command[-1],
            "pre-release probing must verify installed distribution metadata")


def main() -> int:
    test_failed_cases_do_not_count_as_coverage()
    test_passed_cases_count_as_coverage()
    test_sensitive_values_are_redacted()
    test_case_selection_and_suite_classification()
    test_selected_case_collection_is_lazy()
    test_unknown_case_error_lists_all_available_cases()
    test_pre_release_probe_isolated_from_checkout()
    print("Runner quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
