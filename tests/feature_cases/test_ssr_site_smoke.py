"""Optional private Astro SSR fixture smoke checks."""
from __future__ import annotations

import os
import tempfile
import time
from urllib.parse import urljoin

from DrissionPage import SessionPage

from support import assert_equal, assert_in, assert_nav_result, assert_true, make_browser


FEATURE_ID = 'ssr_site_smoke'
FEATURES = ('ssr_site_smoke',)
BROWSER_PHASE = True
PRIVATE_FIXTURE_URL_ENV = 'DP_PRIVATE_FIXTURE_URL'



def site_url(path: str = '') -> str:
    base = (os.environ.get(PRIVATE_FIXTURE_URL_ENV) or '').strip().rstrip('/')
    if not base:
        return ''
    if not path:
        return base
    return urljoin(base + '/', path.lstrip('/'))


def run(ctx):
    if not ctx.include_online:
        ctx.skip('SSR site smoke requires --include-online')
        return
    base = site_url()
    if not base:
        ctx.skip(f'SSR fixture smoke requires {PRIVATE_FIXTURE_URL_ENV}')
        return

    session_page = SessionPage()
    health = session_page.get(site_url('/api/health.json'), timeout=20)
    assert_nav_result(health, status=200, ok=True, label='SSR health endpoint')
    health_json = health.Response.json()
    assert_true(health_json['ok'] is True, 'health endpoint should report ok=true')
    assert_equal(health_json['service'], 'drissionpage-ssr-test-site', 'health endpoint service mismatch')

    manifest = session_page.get(site_url('/api/manifest.json'), timeout=20)
    assert_nav_result(manifest, status=200, ok=True, label='SSR manifest endpoint')
    manifest_json = manifest.Response.json()
    assert_true(manifest_json['ok'] is True, 'manifest should report ok=true')
    case_ids = {item['id'] for item in manifest_json['cases']}
    for required in ('home', 'locators', 'network', 'forms', 'frames', 'waits', 'visual', 'upload-download', 'dynamic'):
        assert_in(required, case_ids, 'manifest should include expected fixture case')

    missing = session_page.get(site_url('/api/status/404'), timeout=20, retry=0, raise_err=False)
    assert_nav_result(missing, status=404, ok=False, label='SSR explicit 404 endpoint')

    dynamic = session_page.get(site_url('/cases/dynamic?name=session-smoke'), timeout=20)
    assert_nav_result(dynamic, status=200, ok=True, label='SSR dynamic page')
    assert_in('session-smoke', session_page.html, 'SSR dynamic page should include query value')

    download = session_page.get(site_url('/api/download.txt?name=session-fixture.txt'), timeout=20)
    assert_nav_result(download, status=200, ok=True, label='SSR download endpoint')
    assert_in('attachment;', download.headers.get('content-disposition', ''),
              'download endpoint should expose attachment content-disposition')
    assert_in('session-fixture.txt', download.Response.text, 'download body should include requested filename')

    if ctx.skip_browser:
        ctx.skip_current_browser('SSR browser smoke skipped by --skip-browser')
        return

    with make_browser(ctx.browser_path, page_load_timeout=20) as browser:
        tab = browser.latest_tab

        home = tab.get(site_url('/'))
        assert_nav_result(home, status=200, ok=True, label='SSR home Chromium navigation')
        assert_equal(tab('[data-testid="site-name"]', timeout=10).text, 'DrissionPage SSR Test Site',
                     'home should expose stable site-name test id')
        assert_true(tab('[data-testid="api-manifest"]', timeout=10), 'home should link manifest endpoint')

        locators = tab.get(site_url('/cases/locators'))
        assert_nav_result(locators, status=200, ok=True, label='SSR locators page')
        assert_equal(tab('x://div[@id="target"]', timeout=10).attr('data-testid'), 'xpath-target',
                     'explicit XPath should find locator target')
        assert_equal(tab('ax:@name=Save Now@role=button', timeout=10).attr('data-testid'), 'aria-save-button',
                     'AX locator should find accessible button')

        network = tab.get(site_url('/cases/network'))
        assert_nav_result(network, status=200, ok=True, label='SSR network page')
        tab.listen.start('/api/echo.json')
        try:
            tab('[data-testid="fetch-json"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/echo.json?from=fetch-json' in packet.url,
                        'listener should capture SSR fixture fetch packet')
            assert_equal(packet.response.status, 200, 'SSR fixture fetch should return 200')
            assert_equal(packet.response.body['query']['from'], 'fetch-json',
                         'SSR fixture fetch should expose query in JSON body')
        finally:
            tab.listen.stop()
        deadline = time.time() + 10
        while time.time() < deadline and 'fetch-json status=200' not in tab('[data-testid="network-log"]').text:
            time.sleep(0.2)
        assert_in('fetch-json status=200', tab('[data-testid="network-log"]').text,
                  'network page should render fetch result in log')

        frames = tab.get(site_url('/cases/frames'))
        assert_nav_result(frames, status=200, ok=True, label='SSR frames page')
        frame = tab.get_frame(1, timeout=10)
        assert_equal(frame('[data-testid="inside-frame"]', timeout=10).text, 'inside frame: primary',
                     'frame child should expose stable inside-frame text')

        waits = tab.get(site_url('/cases/waits'))
        assert_nav_result(waits, status=200, ok=True, label='SSR waits page')
        tab('[data-testid="start-waits"]', timeout=10).click(by_js=True)
        deadline = time.time() + 10
        while time.time() < deadline and tab('[data-testid="delayed-visible"]', timeout=2).attr('hidden') is not None:
            time.sleep(0.1)
        assert_true(tab('[data-testid="delayed-visible"]', timeout=2).attr('hidden') is None,
                    'wait fixture delayed-visible should become visible')
        deadline = time.time() + 10
        while time.time() < deadline and tab('[data-testid="text-target"]', timeout=2).text != 'text-ready':
            time.sleep(0.1)
        assert_equal(tab('[data-testid="text-target"]', timeout=2).text, 'text-ready',
                     'wait fixture text target should become ready')
        assert_equal(tab('[data-testid="attr-target"]', timeout=2).attr('data-state'), 'ready',
                     'wait fixture attr target should become ready')
        tab('[data-testid="stabilize-html"]', timeout=10).click(by_js=True)
        deadline = time.time() + 10
        while time.time() < deadline and tab('[data-testid="html-stable-list"]', timeout=2).attr('data-stable') != 'true':
            time.sleep(0.1)
        assert_equal(tab('[data-testid="html-stable-list"]', timeout=2).attr('data-stable'), 'true',
                     'wait fixture html-stable-list should mark stable')

        visual = tab.get(site_url('/cases/visual'))
        assert_nav_result(visual, status=200, ok=True, label='SSR visual page')
        assert_true(tab('[data-testid="visual-target"]', timeout=10), 'visual target should exist')
        assert_equal(tab('[data-testid="band-red"]', timeout=10).text, 'red band',
                     'visual fixture should expose red band')
        assert_true(tab('[data-testid="dot-top-left"]', timeout=10), 'visual fixture should expose green dot anchors')
        assert_true(tab('[data-testid="long-visual-target"]', timeout=10), 'visual fixture should expose long target')

        upload_download = tab.get(site_url('/cases/upload-download'))
        assert_nav_result(upload_download, status=200, ok=True, label='SSR upload/download page')
        assert_true(tab('[data-testid="file-input"]', timeout=10), 'upload fixture should expose file input')
        assert_in('/api/download.txt?name=dp-fixture.txt', tab('[data-testid="download-link"]', timeout=10).attr('href'),
                  'upload/download fixture should expose deterministic download link')
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as tmp:
            tmp.write('upload smoke')
            upload_path = tmp.name
        try:
            tab('[data-testid="file-input"]', timeout=10).input(upload_path)
            tab('[data-testid="upload-submit"]', timeout=10).click(by_js=True)
            deadline = time.time() + 10
            while time.time() < deadline and 'upload' not in tab('[data-testid="upload-output"]', timeout=2).text:
                time.sleep(0.1)
            assert_in('.txt', tab('[data-testid="upload-output"]', timeout=2).text,
                      'upload fixture should render uploaded file metadata')
        finally:
            try:
                os.unlink(upload_path)
            except OSError:
                pass
