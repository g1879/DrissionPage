"""Feature: get()/post() return navigation status information."""
from __future__ import annotations

import json

from DrissionPage import SessionPage

from support import assert_equal, assert_false, assert_true, html, local_server, request_body


FEATURE_ID = 'navigation_result'

BROWSER_PHASE = True

def run(ctx):
    test_session_navigation_objects()
    if ctx.skip_browser:
        ctx.skip_current_browser('browser-backed navigation matrix skipped by --skip-browser')
        return
    test_browser_navigation_matrix(ctx.browser_path)


def test_session_navigation_objects():
    routes = {
        '/ok': lambda req: html("<body><div id='ok'>session ok</div></body>", title='session ok'),
        '/post': lambda req: (
            201,
            'application/json; charset=utf-8',
            json.dumps({'body': request_body(req)}, ensure_ascii=False),
            {},
        ),
    }
    with local_server(routes) as base:
        page = SessionPage()
        ok = page.get(base + '/ok', timeout=5)
        assert_equal(ok.status, 200, 'SessionPage.get() should return NavResult status for 200')
        assert_true(ok.ok, 'SessionPage.get() NavResult.ok should be true for 200')
        assert_equal(ok.url, base + '/ok', 'SessionPage.get() should expose final url')
        assert_true(ok.headers, 'SessionPage.get() should expose response headers')
        assert_true(ok.request, 'SessionPage.get() should expose request object')
        assert_true(ok.Response, 'SessionPage.get() should expose Response in s mode')
        assert_equal(page('#ok').text, 'session ok', 'SessionPage DOM lookup should still work after get()')

        posted = page.post(base + '/post', data='alpha=1', timeout=5)
        assert_equal(posted.status, 201, 'SessionPage.post() should return NavResult status')
        assert_true(posted.ok, 'SessionPage.post() NavResult.ok should be true for 201')
        assert_equal(posted.Response.json(), {'body': 'alpha=1'}, 'SessionPage.post() should keep response body')


def test_browser_navigation_matrix(executable):
    from support import make_browser

    routes = {
        '/ok': lambda req: html("<body><div id='ok'>OK</div></body>", title='ok'),
        '/missing': lambda req: (404, 'text/html; charset=utf-8', "<body><div id='missing'>Missing</div></body>", {}),
        '/error': lambda req: (500, 'text/html; charset=utf-8', "<body><div id='error'>Error</div></body>", {}),
        '/redirect': lambda req: (302, 'text/plain; charset=utf-8', b'', {'Location': '/final'}),
        '/final': lambda req: html("<body><div id='final'>Final</div></body>", title='final'),
    }
    with local_server(routes) as base, make_browser(executable) as browser:
        tab = browser.latest_tab

        ok = tab.get(base + '/ok')
        assert_true(ok, '200 navigation result should be truthy')
        assert_equal(ok.status, 200, '200 navigation should expose status=200')
        assert_true(ok.ok, '200 navigation should expose ok=True')
        assert_equal(ok.url, base + '/ok', '200 navigation should expose final url')
        assert_true(getattr(ok, 'headers', None), 'navigation result should expose headers')
        assert_true(getattr(ok, 'request', None), 'navigation result should expose request info')

        missing = tab.get(base + '/missing')
        assert_equal(missing.status, 404, '404 navigation should expose status=404')
        assert_false(missing.ok, '404 navigation should expose ok=False')
        assert_true(getattr(missing, 'http_error', True), '404 navigation should mark http_error')
        assert_equal(missing.url, base + '/missing', '404 navigation should expose final url')

        error = tab.get(base + '/error')
        assert_equal(error.status, 500, '500 navigation should expose status=500')
        assert_false(error.ok, '500 navigation should expose ok=False')
        assert_true(getattr(error, 'http_error', True), '500 navigation should mark http_error')
        assert_equal(error.url, base + '/error', '500 navigation should expose final url')

        redirected = tab.get(base + '/redirect')
        assert_equal(redirected.status, 200, 'redirect final navigation should expose final status')
        assert_true(redirected.ok, 'redirect final navigation should expose ok=True')
        assert_equal(redirected.url, base + '/final', 'redirect navigation should expose final url')
