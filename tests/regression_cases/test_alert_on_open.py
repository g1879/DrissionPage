# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from support import TestFailure, DEFAULT_BROWSER, TestCase, TestContext


def _child(browser_path: str, profile: str) -> int:
    from DrissionPage import Chromium, ChromiumOptions

    co = ChromiumOptions(read_file=False)
    co.auto_port()
    co.headless(True)
    co.set_user_data_path(profile)
    if browser_path:
        co.set_browser_path(browser_path)
    browser = Chromium(co)
    try:
        tab = browser.latest_tab
        start = time.perf_counter()
        res = tab.get("data:text/html,<title>alert-check</title><script>alert('check-alert')</script><body>ok</body>", retry=0, timeout=2, raise_err=False)
        elapsed = time.perf_counter() - start
        try:
            tab.handle_alert(accept=True)
        except Exception:
            pass
        after = tab.get("data:text/html,<title>after-alert</title><body>after</body>", retry=0, timeout=2, raise_err=False)
        print(f"returned elapsed={elapsed:.3f} res={res!r} ok={getattr(res, 'ok', None)!r} status={getattr(res, 'status', None)!r} after={after!r}")
        return 0 if elapsed < 8 and getattr(after, "ok", False) else 3
    finally:
        try:
            browser.quit()
        except BaseException:
            pass


def run(ctx: TestContext) -> None:
    browser_path = ctx.browser_path or DEFAULT_BROWSER
    profile = Path(tempfile.gettempdir()) / f"dp-alert-on-open-{int(time.time() * 1000)}"
    cmd = [sys.executable, __file__, "--child", browser_path, str(profile)]
    try:
        proc = subprocess.run(cmd, cwd="/tmp", text=True, capture_output=True, timeout=max(8.0, ctx.timeout + 4))
    except subprocess.TimeoutExpired as e:
        subprocess.run(["pkill", "-f", f"user-data-dir={profile}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raise TestFailure(
            "Opening a page that immediately raises alert() hung past the check timeout; "
            f"cmd={' '.join(cmd)!r}; stdout={e.stdout!r}; stderr={e.stderr!r}"
        )
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if proc.returncode != 0:
        raise TestFailure(f"alert-on-open child failed rc={proc.returncode}; stdout={proc.stdout!r}; stderr={proc.stderr!r}")


TEST_CASE = TestCase(
    name="alert_on_open",
    title="Page with alert() during initial load should not hang",
    requires_browser=True,
    features=("alert_on_open",),
    run=run,
)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--child", action="store_true")
    ap.add_argument("browser_path")
    ap.add_argument("profile")
    ns = ap.parse_args()
    if ns.child:
        raise SystemExit(_child(ns.browser_path, ns.profile))
