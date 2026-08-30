"""Feature: Tab listener captures packets generated inside cross-origin iframes."""
from __future__ import annotations

from support import assert_equal, assert_true, html, json_response, local_server, make_browser


FEATURE_ID = 'cross_origin_iframe_listener'

REQUIRES_BROWSER = True

def run(ctx):
    if ctx.skip_browser:
        ctx.skip('browser-backed cross-origin iframe listener check skipped by --skip-browser')
        return

    child_routes = {
        '/frame': lambda req: html(
            """
            <body>
              <div id="inside-frame">Frame Domain</div>
              <script>fetch('/api/data').then(r => r.text()).catch(() => {});</script>
            </body>
            """,
            title='child frame',
        ),
        '/api/data': lambda req: json_response({'ok': True, 'source': 'iframe'}),
    }
    with local_server(child_routes, host='127.0.0.1') as child_base:
        parent_routes = {
            '/': lambda req: html(
                f"<body><iframe id='child-frame' src='{child_base.replace('127.0.0.1', 'localhost')}/frame'></iframe></body>",
                title='parent page',
            ),
        }
        # Force site isolation so the child is a real OOPIF/CDP target rather
        # than an in-process frame hidden by the default test flags.
        with local_server(parent_routes, host='127.0.0.1') as parent_base, make_browser(
                ctx.browser_path, force_oopif=True) as browser:
            tab = browser.latest_tab
            tab.listen.start('/api/data')
            try:
                assert_true(tab.get(parent_base + '/'), 'parent page should load')
                packet = tab.listen.wait(timeout=5)
                assert_true(packet and '/api/data' in packet.url, 'tab listener should capture iframe fetch packet')
                assert_equal(packet.response.body, {'ok': True, 'source': 'iframe'}, 'iframe packet body should be parsed')
            finally:
                tab.listen.stop()
