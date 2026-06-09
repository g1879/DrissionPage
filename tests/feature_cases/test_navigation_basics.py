"""Feature: navigation timeout, load mode, and local-file contracts."""
from __future__ import annotations

import tempfile
import time
from pathlib import Path

from DrissionPage import SessionPage

from feature_cases.core_feature_server import core_feature_server
from support import assert_equal, assert_true, chromium

FEATURE_ID = "navigation_basics"
REQUIRES_BROWSER = True


def run(ctx):
    _check_session_local_file()
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed navigation contracts skipped by --skip-browser")
    _check_browser_navigation(ctx)


def _check_session_local_file() -> None:
    with tempfile.TemporaryDirectory(prefix="dp-local-file-") as tmp:
        path = Path(tmp) / "local.html"
        path.write_text("<!doctype html><title>local ok</title><div id='local'>local file body</div>", encoding="utf-8")
        page = SessionPage()
        assert_true(page.get(str(path)), "SessionPage.get() should load a local file path")
        assert_equal(page.title, "local ok", "SessionPage local file should parse title")
        assert_equal(page("#local").text, "local file body", "SessionPage local file should expose DOM")
        page.close()


def _check_browser_navigation(ctx) -> None:
    with core_feature_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        tab.set.load_mode.none()
        start = time.perf_counter()
        result = tab.get(base + "/nav", timeout=ctx.timeout)
        elapsed = time.perf_counter() - start
        assert_true(result is not False and result is not None, "load_mode none should return a navigation result")
        assert_true(elapsed < 1.2, "load_mode none should not wait for slow subresources", elapsed=elapsed)
        assert_true(tab.wait.eles_loaded("#early", timeout=ctx.timeout), "DOM should be usable in none load mode")
        tab.stop_loading()

        tab.set.load_mode.normal()
        start = time.perf_counter()
        ok = tab.get(base + "/slow-main", timeout=0.5, retry=0)
        elapsed = time.perf_counter() - start
        assert_true(ok is False or elapsed < 1.3, "get(timeout) should bound slow main-document navigation", ok=ok, elapsed=elapsed)
