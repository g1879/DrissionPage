# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from support import TestCase, TestContext, assert_equal, assert_true, chromium, local_server


def run(ctx: TestContext) -> None:
    with local_server() as (base, _server), chromium(ctx) as browser:
        tab = browser.latest_tab
        save_dir = ctx.artifacts_dir / "downloads"
        save_dir.mkdir(parents=True, exist_ok=True)
        target = save_dir / "check-browser.txt"
        if target.exists():
            target.unlink()
        mission = tab.download.by_browser(
            base + "/download/file.txt",
            save_path=save_dir,
            rename="check-browser",
            suffix="txt",
            timeout=ctx.timeout,
            file_exists="overwrite",
        )
        assert_true(mission, "download.by_browser() should return a DownloadMission")
        done = mission.wait(timeout=ctx.timeout + 3)
        assert_true(done is not False, "DownloadMission.wait() should complete")
        assert_true(target.exists(), "downloaded file should exist", path=target)
        assert_equal(target.read_text("utf-8"), "download body\n", "downloaded file content mismatch")


TEST_CASE = TestCase(
    name="download_browser",
    title="download.by_browser() local deterministic download",
    requires_browser=True,
    features=("download_by_browser",),
    run=run,
)
