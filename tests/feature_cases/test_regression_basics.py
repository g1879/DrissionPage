"""Feature: baseline regression checks for 4.2 fixes and optimizations."""
from __future__ import annotations

from DrissionPage import SessionPage
from DrissionPage._functions.keys import Keys, keys_to_typing

from support import assert_equal, assert_in, assert_true, html, json_response, local_server, make_browser


FEATURE_ID = 'regression_basics'

BROWSER_PHASE = True

def run(ctx):
    test_no_browser_regressions()
    if ctx.skip_browser:
        ctx.skip_current_browser('browser-backed regression checks skipped by --skip-browser')
        return
    test_browser_regressions(ctx.browser_path)


def test_no_browser_regressions():
    assert_equal(keys_to_typing((Keys.COMMAND, 'a')), (4, 'a'), 'COMMAND key tuple should map to meta modifier')
    assert_equal(keys_to_typing((Keys.META, 'a')), (4, 'a'), 'META key tuple should map to meta modifier')

    seen = {}

    def ok(req):
        seen['timeout'] = getattr(req.server, 'timeout_marker', None)
        return html("<body><div id='ok'>ok</div></body>", title='session timeout')

    # This local server check proves SessionPage accepts timeout= without breaking navigation.
    with local_server({'/ok': ok}) as base:
        page = SessionPage()
        result = page.get(base + '/ok', timeout=3)
        assert_equal(result.status, 200, 'SessionPage.get(timeout=...) should still navigate successfully')
        assert_true(result.ok, 'SessionPage.get(timeout=...) should return ok NavResult')


def test_browser_regressions(executable):
    frame_routes = {
        '/frame-start': lambda req: html("<body><div id='frame-start'>start</div></body>", title='frame start'),
        '/frame-final': lambda req: html("<body><div id='frame-final'>final</div></body>", title='frame final'),
    }
    with local_server(frame_routes) as frame_base:
        routes = {
            '/': lambda req: html(
                f"""
                <body>
                  <div id="123abc">numeric id</div>
                  <iframe id="child-frame" src="{frame_base}/frame-start"></iframe>
                </body>
                """,
                title='regression host',
            ),
            '/api': lambda req: json_response({'ok': True}),
        }
        with local_server(routes) as base, make_browser(executable) as browser:
            tab = browser.latest_tab
            assert_true(tab.get(base + '/'), 'regression host page should load')

            css_selector = tab('#123abc', timeout=5).css_selector
            assert_in('123abc', css_selector, 'css_selector should include numeric-leading id without failing')

            tab.listen.start('/api')
            tab.run_js("fetch('/api').catch(() => {});")
            first = tab.listen.wait(timeout=5)
            assert_equal(first.response.body, {'ok': True}, 'listener should capture first fetch')
            tab.listen.stop()
            tab.listen.start('/api')
            tab.run_js("fetch('/api').catch(() => {});")
            second = tab.listen.wait(timeout=5)
            assert_equal(second.response.body, {'ok': True}, 'listener stop() then start() should capture later fetch')
            tab.listen.stop()

            frame = tab.get_frame(1, timeout=5)
            assert_true(frame.get(frame_base + '/frame-final'), 'iframe should navigate to final page')
            assert_true(frame.wait.url_change('frame-final', timeout=3), 'iframe wait.url_change() should detect frame URL')
            assert_true(frame.wait.title_change('frame final', timeout=3), 'iframe wait.title_change() should detect frame title')
