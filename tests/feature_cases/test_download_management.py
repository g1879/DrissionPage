"""Feature: browser download management contracts."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from feature_cases.core_feature_server import core_feature_server
from support import assert_equal, assert_true, chromium

FEATURE_ID = "download_management"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed download contracts skipped by --skip-browser")
    with core_feature_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/download-page"), "download page should load")
        with TemporaryDirectory(prefix="dp-download-management-") as tmp:
            tab.set.download_path(tmp)
            tab.set.download_file_name("download-renamed", suffix="txt")
            tab("#download-link").click(by_js=True)
            mission = tab.wait.download_begin(timeout=ctx.timeout)
            assert_true(mission, "wait.download_begin() should return a mission after a real browser download starts")
            final_path = mission.wait(show=False, timeout=ctx.timeout + 3)
            assert_true(final_path, "DownloadMission.wait() should complete the local browser download")
            path = Path(final_path)
            assert_equal(path.name, "download-renamed.txt", "set.download_file_name() should rename the download")
            assert_equal(path.read_text(encoding="utf-8"), "download-body", "downloaded body mismatch")
