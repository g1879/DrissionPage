#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exercise CI retry and gate propagation without launching real tests."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CI_SCRIPT = ROOT / "tests" / "ci.sh"

FAKE_PYTHON = r'''#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
if not args or args[0] == "-":
    print("fake_python=true")
    raise SystemExit(0)
if args[:2] == ["-m", "compileall"]:
    raise SystemExit(0)
if "--list-cases" in args:
    print("fake_case")
    raise SystemExit(0)

def option(name):
    try:
        return args[args.index(name) + 1]
    except (ValueError, IndexError):
        return None

report_json = option("--report-json")
report_md = option("--report-md")
if report_json:
    path = Path(report_json)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"summary": {"passed": 1, "failed": 0}}), encoding="utf-8")
if report_md:
    path = Path(report_md)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# fake report\n", encoding="utf-8")

is_browser_gate = "--suite" in args and option("--suite") == "stable" and "--browser-only" in args
is_current = not ("--source" in args and option("--source") == "pre")
if is_browser_gate and is_current:
    mode = os.environ.get("FAKE_CURRENT_BROWSER_MODE", "pass")
    state = Path(os.environ["FAKE_STATE_FILE"])
    count = int(state.read_text(encoding="utf-8")) if state.exists() else 0
    state.write_text(str(count + 1), encoding="utf-8")
    if mode == "always-fail" or (mode == "flaky" and count == 0):
        raise SystemExit(1)

selected_cases = [args[i + 1] for i, arg in enumerate(args[:-1]) if arg == "--case"]
if os.environ.get("FAKE_SSR_GATE_FAIL") == "1" and "ssr_marketplace_flow" in selected_cases:
    raise SystemExit(1)
raise SystemExit(0)
'''


def run_scenario(tmp: Path, *, browser_mode: str, ssr_fail: bool = False) -> subprocess.CompletedProcess[str]:
    tmp.mkdir(parents=True, exist_ok=True)
    fake_python = tmp / "fake-python"
    fake_python.write_text(FAKE_PYTHON, encoding="utf-8")
    fake_python.chmod(0o755)
    state_file = tmp / "browser-attempts.txt"
    state_file.unlink(missing_ok=True)
    browser_path = shutil.which("true")
    if not browser_path:
        raise RuntimeError("the platform does not provide a true executable")
    env = os.environ.copy()
    env.update({
        "PYTHON_BIN": str(fake_python),
        "DP_BROWSER_PATH": browser_path,
        "DP_TESTS_REPORT_DIR": str(tmp / "reports"),
        "DP_TESTS_ARTIFACT_DIR": str(tmp / "artifacts"),
        "DP_TESTS_PRE_VENV": str(tmp / "pre-venv"),
        "DP_TESTS_COVERAGE": "0",
        "DP_TESTS_RUN_KNOWN": "0",
        "DP_TESTS_RUN_LOCAL_SSR": "1" if ssr_fail else "0",
        "DP_TEST_SITE_URL": "http://127.0.0.1:4321" if ssr_fail else "",
        "DP_TESTS_BROWSER_GATE_ATTEMPTS": "2",
        "FAKE_CURRENT_BROWSER_MODE": browser_mode,
        "FAKE_STATE_FILE": str(state_file),
        "FAKE_SSR_GATE_FAIL": "1" if ssr_fail else "0",
    })
    return subprocess.run(
        ["bash", str(CI_SCRIPT)],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def require(condition: bool, message: str, output: str) -> None:
    if not condition:
        raise AssertionError(f"{message}\n--- ci output ---\n{output}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="dp-ci-retry-") as raw_tmp:
        tmp = Path(raw_tmp)

        flaky = run_scenario(tmp / "flaky", browser_mode="flaky")
        require(flaky.returncode == 0, "a browser gate that passes on retry should recover", flaky.stdout)
        require("passed on attempt 2/2" in flaky.stdout, "retry success should be visible", flaky.stdout)
        require("Flaky gates:" in flaky.stdout, "retry recovery should be summarized", flaky.stdout)
        for name in (
            "current-stable-browser-attempt-1.json",
            "current-stable-browser-attempt-2.json",
            "current-stable-browser.json",
        ):
            require((tmp / "flaky" / "reports" / name).is_file(), f"missing retry report {name}", flaky.stdout)

        failed = run_scenario(tmp / "failed", browser_mode="always-fail")
        require(failed.returncode == 1, "a browser gate that exhausts retries should fail", failed.stdout)
        require("Failed gates:" in failed.stdout, "final failures should be summarized", failed.stdout)
        require(
            (tmp / "failed" / "reports" / "current-stable-browser-attempt-2.json").is_file(),
            "the final failed attempt report should be retained",
            failed.stdout,
        )

        ssr = run_scenario(tmp / "ssr", browser_mode="pass", ssr_fail=True)
        require(ssr.returncode == 1, "the local SSR business gate must propagate failure", ssr.stdout)
        require("current local SSR business scenarios gate" in ssr.stdout, "SSR failure should be named", ssr.stdout)

    print("CI retry and gate propagation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
