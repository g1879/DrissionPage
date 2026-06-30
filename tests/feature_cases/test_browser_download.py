"""Feature: actively trigger browser downloads."""
from __future__ import annotations

from inspect import signature
from pathlib import Path
import tempfile

from DrissionGet import DrissionGet

from support import assert_equal, assert_in, assert_true, binary_response, html, local_server, make_browser


FEATURE_ID = 'browser_download'

BROWSER_PHASE = True

def run(ctx):
    assert_in('file_exists', signature(DrissionGet.by_browser).parameters,
              'download.by_browser() should expose file_exists')
    if ctx.skip_browser:
        ctx.skip_current_browser('browser-backed download check skipped by --skip-browser')
        return

    routes = {
        '/': lambda req: html("<body><div id='ready'>ready</div></body>", title='download host'),
        '/browser-download.txt': lambda req: binary_response(
            b'browser-download-body',
            'text/plain; charset=utf-8',
            {'Content-Disposition': 'attachment; filename=browser-download.txt'},
        ),
    }
    with local_server(routes) as base, make_browser(ctx.browser_path) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + '/'), 'download host page should load')
        with tempfile.TemporaryDirectory(prefix='dp-pre-download-') as download_dir:
            mission = tab.download.by_browser(
                base + '/browser-download.txt',
                save_path=download_dir,
                rename='from-browser',
                suffix='txt',
                timeout=8,
                file_exists='overwrite',
            )
            final_path = mission.wait(show=False, timeout=8)
            assert_true(final_path, 'download.by_browser() should complete a local download')
            assert_equal(Path(final_path).read_text(encoding='utf-8'), 'browser-download-body',
                         'download.by_browser() should save the expected file body')
