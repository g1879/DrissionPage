#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper that runs the tests against current source or an installed pre-release venv."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _has_drissionpage(py: Path) -> bool:
    result = subprocess.run(
        [str(py), "-c", "import DrissionPage"],
        cwd="/tmp",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def ensure_venv(venv_dir: Path, install_mode: str) -> tuple[Path, str]:
    py = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not py.exists():
        print(f"Creating venv: {venv_dir}", flush=True)
        venv.EnvBuilder(with_pip=True).create(venv_dir)

    if install_mode == "never":
        return py, "skipped"

    if install_mode == "auto" and _has_drissionpage(py):
        return py, "already-installed"

    if install_mode == "upgrade":
        print("Installing/upgrading latest DrissionPage pre-release...", flush=True)
        subprocess.check_call([str(py), "-m", "pip", "install", "--upgrade", "pip"], cwd="/tmp")
        subprocess.check_call([str(py), "-m", "pip", "install", "--pre", "--upgrade", "DrissionPage"], cwd="/tmp")
        return py, "upgraded"

    print("Installing DrissionPage pre-release into venv...", flush=True)
    subprocess.check_call([str(py), "-m", "pip", "install", "--pre", "DrissionPage"], cwd="/tmp")
    return py, "installed"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--venv", default="/tmp/dp-tests-pre-venv")
    parser.add_argument("--source", choices=("pre", "current"), default="pre",
                        help="pre: run installed PyPI pre-release in venv; current: run this checkout source")
    parser.add_argument("--no-install", action="store_true", help="do not pip install/upgrade DrissionPage --pre")
    parser.add_argument("--upgrade-pre", "--install-pre", action="store_true", dest="upgrade_pre",
                        help="pip install --pre --upgrade DrissionPage before running pre-release test cases")
    parser.add_argument("--browser-path", default=None)
    parser.add_argument("--skip-browser", action="store_true")
    parser.add_argument("--include-online", action="store_true")
    parser.add_argument("--artifacts-dir", default="/tmp/dp-tests-artifacts")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--case", action="append", dest="cases")
    parser.add_argument("--browser-only", action="store_true")
    parser.add_argument("--no-browser-only", action="store_true")
    parser.add_argument("--suite", choices=("stable", "known", "local", "all"), default=None,
                        help="stable is the CI gate; known/local are isolated report-only repro/smoke suites")
    parser.add_argument("--list-cases", action="store_true", dest="list_cases")
    parser.add_argument("--report-json", default=None)
    parser.add_argument("--report-md", default=None)
    parser.add_argument("--fail-on-failures", action="store_true", dest="fail_on_failures", help="propagate test case failures as exit code 1")
    args = parser.parse_args(argv)
    if args.source == "pre" and args.no_install and args.upgrade_pre:
        parser.error("--no-install cannot be used together with --upgrade-pre")

    repo_root = ROOT.parent
    if args.source == "current":
        py = Path(sys.executable)
        install_status = "current-checkout"
    else:
        if args.no_install:
            install_mode = "never"
        elif args.upgrade_pre:
            install_mode = "upgrade"
        else:
            install_mode = "auto"
        py, install_status = ensure_venv(Path(args.venv), install_mode=install_mode)
    cmd = [str(py), str(ROOT / "runner.py")]
    if args.browser_path:
        cmd += ["--browser-path", args.browser_path]
    if args.skip_browser:
        cmd.append("--skip-browser")
    if args.include_online:
        cmd.append("--include-online")
    if args.artifacts_dir:
        cmd += ["--artifacts-dir", args.artifacts_dir]
    if args.timeout:
        cmd += ["--timeout", str(args.timeout)]
    for case in args.cases or []:
        cmd += ["--case", case]
    if args.browser_only:
        cmd.append("--browser-only")
    if args.no_browser_only:
        cmd.append("--no-browser-only")
    if args.suite:
        cmd += ["--suite", args.suite]
    if args.list_cases:
        cmd.append("--list-cases")
    if args.report_json:
        cmd += ["--report-json", str(Path(args.report_json).resolve())]
    if args.report_md:
        cmd += ["--report-md", str(Path(args.report_md).resolve())]
    if args.fail_on_failures:
        cmd.append("--fail-on-failures")

    env = os.environ.copy()
    if args.source == "current":
        env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(repo_root), env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
        cwd = str(repo_root)
    else:
        env["PYTHONPATH"] = str(ROOT)
        # cwd outside repo is critical: do not import checkout DrissionPage by accident.
        cwd = "/tmp"
    print(f"Run source: {args.source} | python: {py} | pre_install: {install_status}", flush=True)
    return subprocess.call(cmd, cwd=cwd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
