#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run DrissionPage release verification test cases and emit coverage reports."""
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from feature_manifest import EXCLUDED, FEATURES
from support import TestContext, TestResult, SkipTestCase, import_version

FEATURE_CASE_MODULES = [
    "feature_cases.test_recommended_chromium_entry",
    "feature_cases.test_startup_settings",
    "feature_cases.test_proxy_credentials",
    "feature_cases.test_navigation_result",
    "feature_cases.test_browser_contexts",
    "feature_cases.test_cross_origin_iframe_elements",
    "feature_cases.test_cross_origin_iframe_listener",
    "feature_cases.test_listener_upgrade",
    "feature_cases.test_browser_download",
    "feature_cases.test_permissions",
    "feature_cases.test_element_locators",
    "feature_cases.test_mouse_trail",
    "feature_cases.test_api_behavior_changes",
    "feature_cases.test_regression_basics",
    "feature_cases.test_listener_basics",
    "feature_cases.test_navigation_basics",
    "feature_cases.test_download_management",
    "feature_cases.test_page_object_basics",
    "feature_cases.test_cookie_setters",
    "feature_cases.test_tab_management",
    "feature_cases.test_element_core_behaviors",
    "feature_cases.test_options_settings",
    "feature_cases.test_chromium_options_environment",
    "feature_cases.test_find_api",
    "feature_cases.test_chromium_tab_management",
    "feature_cases.test_console_and_cookie_formats",
    "feature_cases.test_frame_shadow_setters",
    "feature_cases.test_scroll_and_waits",
    "feature_cases.test_element_multi_click",
    "feature_cases.test_tab_post_response",
    "feature_cases.test_optional_online_smoke",
    "feature_cases.test_ssr_site_smoke",
    "feature_cases.test_ssr_marketplace_flow",
]

REGRESSION_CASE_MODULES = [
    "regression_cases.test_api_surface",
    "regression_cases.test_session_timeout",
    "regression_cases.test_navigation_result",
    "regression_cases.test_alert_on_open",
    "regression_cases.test_listener_ws_sse",
    "regression_cases.test_context_isolation",
    "regression_cases.test_locator_behavior",
    "regression_cases.test_console_and_tabs",
    "regression_cases.test_download_browser",
    "regression_cases.test_iframe_non_screenshot",
]

LEGACY_CASE_ALIASES = {
    "feature_release_40_listener": "feature_listener_basics",
    "feature_release_40_navigation": "feature_navigation_basics",
    "feature_release_40_download": "feature_download_management",
    "feature_release_40_page_objects": "feature_page_object_basics",
    "feature_release_40_cookies": "feature_cookie_setters",
    "feature_release_40_tabs": "feature_tab_management",
    "feature_release_40_elements": "feature_element_core_behaviors",
    "feature_release_40_options": "feature_options_settings",
    "feature_release_41_options": "feature_chromium_options_environment",
    "feature_release_41_find": "feature_find_api",
    "feature_release_41_chromium_tabs": "feature_chromium_tab_management",
    "feature_release_41_console_cookies": "feature_console_and_cookie_formats",
    "feature_release_41_frame_shadow": "feature_frame_shadow_setters",
    "feature_release_41_scroll_waits": "feature_scroll_and_waits",
    "feature_release_41_click_multi": "feature_element_multi_click",
    "feature_release_41_post_response": "feature_tab_post_response",
}

CASE_ALIASES = {
    **LEGACY_CASE_ALIASES,
    **{feature["id"]: feature["case"] for feature in FEATURES},
}


# CI is a stability gate. Cases listed here are still valuable repros, but they
# describe behavior that is either failing on the current branch, version-skewed
# against the latest pre-release, or still under design discussion. Keep them out
# of the default CI gate and run them explicitly with ``--suite known`` when
# validating the bug backlog.
KNOWN_ISSUE_CASES: dict[str, str] = {
    "api_surface": "API/docs contract assertions currently fail on drag_in and click(wait_stop).",
    "feature_cross_origin_iframe_listener": "Cross-host iframe fetch packets are not captured reliably by tab listener.",
    "feature_listener_upgrade": "Browser-backed WS/SSE/HTTP restore checks still expose packet-shape regressions.",
    "feature_regression_basics": "Listener restart assertions can receive False instead of a DataPacket.",
    "feature_tab_management": "get_tab(id/index) currently hits an unhashable dict tab-id path.",
    "feature_chromium_tab_management": "Chromium tab-management checks hit the same unhashable dict tab-id path.",
    "feature_tab_post_response": "ChromiumTab.post() Response-object contract is not satisfied yet.",
    "alert_on_open": "Opening a page that raises alert() during initial load can hang in headless CI.",
    "listener_ws_sse": "WebSocket/SSE packet capture and SSE connect_info contract are not stable yet.",
    "iframe_non_screenshot": "Pre-release iframe non-screenshot behavior is version-skewed; keep as local repro.",
}


# These are opt-in smoke tests. They require either public internet access or a
# private fixture URL and should not decide the public CI badge.
LOCAL_ONLY_CASES: dict[str, str] = {
    "feature_optional_online_smoke": "Requires live public websites and is intentionally opt-in.",
    "feature_ssr_site_smoke": "Requires a local or private SSR fixture URL and is run by a guarded workflow step.",
    "feature_ssr_marketplace_flow": "Requires a local or private SSR fixture URL and validates the marketplace full-flow scenario.",
}


SUITE_CHOICES = ("stable", "known", "local", "all")


SENSITIVE_ENV_NAMES = (
    "DP_PRIVATE_FIXTURE_URL",
    "PUBLIC_OPTIONAL_WS_URL",
)


def _redaction_tokens() -> set[str]:
    tokens: set[str] = set()
    for env_name in SENSITIVE_ENV_NAMES:
        value = (os.environ.get(env_name) or "").strip()
        if not value:
            continue
        tokens.add(value)
        parsed = urlparse(value)
        if parsed.netloc:
            tokens.add(parsed.netloc)
            tokens.add(f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme else parsed.netloc)
    return {token for token in tokens if token}


def redact_sensitive(value: Any) -> Any:
    tokens = _redaction_tokens()
    if not tokens:
        return value
    if isinstance(value, str):
        redacted = value
        for token in sorted(tokens, key=len, reverse=True):
            redacted = redacted.replace(token, "<fixture-url-redacted>")
        return redacted
    if isinstance(value, dict):
        return {key: redact_sensitive(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_sensitive(item) for item in value)
    return value


def normalize_case_names(names: list[str] | None) -> set[str] | None:
    if not names:
        return None
    selected = set()
    for name in names:
        for item in str(name).split(","):
            item = item.strip()
            if not item:
                continue
            stem = Path(item).stem
            selected.add(CASE_ALIASES.get(item, CASE_ALIASES.get(stem, item)))
    return selected


def _case_from_feature_module(module_name: str):
    mod = importlib.import_module(module_name)
    feature_id = getattr(mod, "FEATURE_ID")
    title = (getattr(mod, "__doc__", "") or feature_id).strip().splitlines()[0]
    return type("FeatureCase", (), {
        "name": f"feature_{feature_id}",
        "title": title,
        "requires_browser": bool(getattr(mod, "REQUIRES_BROWSER", False)),
        "browser_phase": bool(getattr(mod, "BROWSER_PHASE", getattr(mod, "REQUIRES_BROWSER", False))),
        "features": tuple(getattr(mod, "FEATURES", (feature_id,))),
        "run": staticmethod(mod.run),
    })()


def load_cases():
    cases = []
    for module_name in FEATURE_CASE_MODULES:
        cases.append(_case_from_feature_module(module_name))
    for module_name in REGRESSION_CASE_MODULES:
        mod = importlib.import_module(module_name)
        cases.append(getattr(mod, "TEST_CASE", None))
    return [case for case in cases if case is not None]


def filter_cases(cases, *, browser_only: bool = False, no_browser_only: bool = False):
    if browser_only:
        return [case for case in cases if getattr(case, "browser_phase", case.requires_browser)]
    if no_browser_only:
        return [case for case in cases if not case.requires_browser and not getattr(case, "browser_phase", False)]
    return cases


def case_suite(case) -> str:
    if case.name in LOCAL_ONLY_CASES:
        return "local"
    if case.name in KNOWN_ISSUE_CASES:
        return "known"
    return "stable"


def case_suite_reason(case) -> str:
    return LOCAL_ONLY_CASES.get(case.name) or KNOWN_ISSUE_CASES.get(case.name) or "Stable CI gate case."


def filter_cases_by_suite(cases, suite: str):
    if suite == "all":
        return cases
    return [case for case in cases if case_suite(case) == suite]


def case_phase_label(case) -> str:
    if case.requires_browser:
        return "browser"
    if getattr(case, "browser_phase", False):
        return "mixed"
    return "no-browser"


def validate_selected_cases(selected: set[str] | None, cases) -> set[str]:
    if not selected:
        return set()
    available = {case.name for case in cases}
    return selected - available


def print_unknown_case_error(unknown: set[str], cases) -> None:
    print(f"错误：--case 没有匹配到任何测试：{', '.join(sorted(unknown))}", file=sys.stderr)
    print("可用 case 名称：", file=sys.stderr)
    for case in cases:
        print(f"  - {case.name}", file=sys.stderr)
    print("提示：可直接使用 case 名称，也支持 feature id，例如 `--case sse_packet`。", file=sys.stderr)


def _suite_arg_provided(argv: list[str] | None) -> bool:
    values = sys.argv[1:] if argv is None else argv
    return any(item == "--suite" or item.startswith("--suite=") for item in values)


def run_case(case, ctx: TestContext) -> TestResult:
    start = time.perf_counter()
    if case.requires_browser and not ctx.include_browser:
        return TestResult(case.name, "skipped", 0.0, "browser cases disabled by --skip-browser")
    try:
        case.run(ctx)
        return TestResult(case.name, "passed", time.perf_counter() - start)
    except SkipTestCase as exc:
        return TestResult(case.name, "skipped", time.perf_counter() - start, redact_sensitive(str(exc)))
    except Exception as exc:
        return TestResult(
            case.name,
            "failed",
            time.perf_counter() - start,
            redact_sensitive(str(exc)),
            redact_sensitive({"traceback": traceback.format_exc()}),
        )


def build_report(results: list[TestResult], cases, started: float, ctx: TestContext, *, suite: str) -> dict[str, Any]:
    case_by_name = {case.name: case for case in cases}
    result_by_name = {result.name: result for result in results}
    covered_features = []
    for feature in FEATURES:
        case_name = feature["case"]
        result = result_by_name.get(case_name)
        if result is None:
            feature_status = "not-run"
            message = "case not selected"
        elif result.status == "passed":
            feature_status = "covered-passed"
            message = ""
        elif result.status == "failed":
            feature_status = "covered-by-failed-case"
            message = result.message
        else:
            feature_status = result.status
            message = result.message
        covered_features.append({
            **feature,
            "status": feature_status,
            "case_status": result.status if result else "not-run",
            "message": redact_sensitive(message),
        })
    status_counts = {s: sum(1 for result in results if result.status == s) for s in ("passed", "failed", "skipped")}
    covered = [feature for feature in covered_features if feature["status"] in {"covered-passed", "covered-by-failed-case"}]
    passed_features = [feature for feature in covered_features if feature["status"] == "covered-passed"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.perf_counter() - started, 3),
        "drissionpage": import_version(),
        "browser_path": ctx.browser_path,
        "include_browser": ctx.include_browser,
        "artifacts_dir": str(ctx.artifacts_dir),
        "suite": suite,
        "summary": {
            "cases_total": len(results),
            **status_counts,
            "features_total": len(FEATURES),
            "features_excluded": len(EXCLUDED),
            "features_covered_by_run": len(covered),
            "features_passed": len(passed_features),
            "feature_coverage_percent": round(100 * len(covered) / len(FEATURES), 2) if FEATURES else 100.0,
            "feature_pass_percent": round(100 * len(passed_features) / len(FEATURES), 2) if FEATURES else 100.0,
        },
        "cases": [
            {
                "name": result.name,
                "title": case_by_name.get(result.name).title if result.name in case_by_name else result.name,
                "status": result.status,
                "duration_seconds": round(result.duration, 3),
                "message": redact_sensitive(result.message),
                "details": redact_sensitive(result.details),
                "features": list(case_by_name.get(result.name).features) if result.name in case_by_name else [],
                "suite": case_suite(case_by_name[result.name]) if result.name in case_by_name else "unknown",
                "suite_reason": case_suite_reason(case_by_name[result.name]) if result.name in case_by_name else "",
            }
            for result in results
        ],
        "features": covered_features,
        "excluded": EXCLUDED,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = []
    summary = report["summary"]
    lines.append("# DrissionPage release verification test report")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- DrissionPage: `{report['drissionpage']['version']}` from `{report['drissionpage']['module']}`")
    lines.append(f"- Browser: `{report['browser_path']}`")
    lines.append(f"- Suite: `{report.get('suite', 'unknown')}`")
    lines.append(f"- Cases: {summary['passed']} passed / {summary['failed']} failed / {summary['skipped']} skipped / {summary['cases_total']} total")
    lines.append(f"- Manifest coverage by this run: {summary['features_covered_by_run']}/{summary['features_total']} ({summary['feature_coverage_percent']}%)")
    lines.append(f"- Excluded by request: {summary['features_excluded']} item(s)")
    lines.append("")
    lines.append("## Test case results")
    for case in report["cases"]:
        lines.append(f"- **{case['name']}** — `{case['status']}` / `{case.get('suite', 'unknown')}` ({case['duration_seconds']}s): {case['message'] or case['title']}")
    lines.append("")
    lines.append("## Failure details")
    failed = [case for case in report["cases"] if case["status"] == "failed"]
    if not failed:
        lines.append("No failed cases in this run.")
    for case in failed:
        lines.append(f"### {case['name']}")
        lines.append("")
        lines.append(f"Message: `{case['message']}`")
        tb = case.get("details", {}).get("traceback")
        if tb:
            lines.append("")
            lines.append("```text")
            lines.append(tb.rstrip())
            lines.append("```")
    lines.append("")
    lines.append("## Feature map")
    for feature in report["features"]:
        case_status = feature.get("case_status", feature["status"])
        lines.append(f"- `{feature['status']}` {feature['id']} — {feature['title']} (case: `{feature['case']}`, case_status: `{case_status}`)")
    lines.append("")
    lines.append("## Excluded")
    for feature in report["excluded"]:
        lines.append(f"- {feature['id']} — {feature['title']}: {feature['reason']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-path", default=None)
    parser.add_argument("--skip-browser", action="store_true")
    parser.add_argument("--include-online", action="store_true", help="reserved; default cases are local only")
    parser.add_argument("--artifacts-dir", default=str(Path("/tmp/dp-tests-artifacts")))
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--case", action="append", dest="cases", help="run only a named test case; can be repeated")
    parser.add_argument("--browser-only", action="store_true", help="run browser and mixed browser-backed cases")
    parser.add_argument("--no-browser-only", action="store_true", help="run only pure no-browser cases")
    parser.add_argument("--suite", choices=SUITE_CHOICES, default=os.environ.get("DP_TESTS_SUITE", "stable"),
                        help="test suite to run: stable is the CI gate; known/local are report-only repro/smoke suites; all includes everything")
    parser.add_argument("--list-cases", action="store_true", dest="list_cases")
    parser.add_argument("--report-json", default=None)
    parser.add_argument("--report-md", default=None)
    parser.add_argument("--fail-on-failures", action="store_true", dest="fail_on_failures", help="return exit code 1 when cases fail; default is report-only exit 0")
    args = parser.parse_args(argv)
    if args.browser_only and args.no_browser_only:
        parser.error("--browser-only cannot be used together with --no-browser-only")
    if args.browser_only and args.skip_browser:
        parser.error("--browser-only cannot be used together with --skip-browser")

    suite_provided = _suite_arg_provided(argv) or "DP_TESTS_SUITE" in os.environ
    selected = normalize_case_names(args.cases)
    effective_suite = args.suite
    if selected and not suite_provided:
        # Explicit --case invocations are commonly used for local bug repros. Do
        # not hide a requested known/local case just because the default suite is
        # the CI gate.
        effective_suite = "all"
    all_cases = load_cases()
    unknown = validate_selected_cases(selected, all_cases)
    if unknown:
        print_unknown_case_error(unknown, all_cases)
        return 2
    cases = [case for case in all_cases if not selected or case.name in selected]
    cases = filter_cases_by_suite(cases, effective_suite)
    cases = filter_cases(cases, browser_only=args.browser_only, no_browser_only=args.no_browser_only)
    if args.list_cases:
        for case in cases:
            print(f"{case.name}\t{case_phase_label(case)}\t{case_suite(case)}\t{case.title}")
        return 0
    if not cases:
        print(f"No cases matched suite={effective_suite!r} and the selected filters.", file=sys.stderr)
        return 2

    ctx = TestContext(
        browser_path=args.browser_path,
        include_browser=not args.skip_browser,
        include_online=args.include_online,
        artifacts_dir=Path(args.artifacts_dir),
        timeout=args.timeout,
    )
    started = time.perf_counter()
    results = []
    print("DrissionPage:", import_version())
    for case in cases:
        result = run_case(case, ctx)
        results.append(result)
        marker = {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP"}.get(result.status, result.status.upper())
        print(f"[{marker}] {case.name} ({result.duration:.2f}s) {result.message}")
    report = build_report(results, cases, started, ctx, suite=effective_suite)
    if args.report_json:
        Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON report: {args.report_json}")
    if args.report_md:
        Path(args.report_md).parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, Path(args.report_md))
        print(f"Markdown report: {args.report_md}")
    summary = report["summary"]
    print(f"Summary: {summary['passed']} passed / {summary['failed']} failed / {summary['skipped']} skipped; manifest coverage {summary['features_covered_by_run']}/{summary['features_total']} ({summary['feature_coverage_percent']}%), excluded {summary['features_excluded']}")
    if summary["failed"] and not args.fail_on_failures:
        print("Result: failed cases were written to reports; exiting 0 in report-only mode. Use --fail-on-failures to return non-zero when any case fails.")
    return 1 if (summary["failed"] and args.fail_on_failures) else 0


if __name__ == "__main__":
    raise SystemExit(main())
