"""Feature: direct element lookup inside cross-origin iframes."""
from __future__ import annotations

from support import assert_equal, assert_true, html, local_server, make_browser


FEATURE_ID = 'cross_origin_iframe_elements'

REQUIRES_BROWSER = True

def run(ctx):
    if ctx.skip_browser:
        ctx.skip('browser-backed cross-origin iframe element check skipped by --skip-browser')
        return

    child_routes = {
        '/frame': lambda req: html(
            """
            <body>
              <div id="inside-frame">Frame Domain</div>
              <button id="frame-button" aria-label="Frame Action">Frame Button</button>
            </body>
            """,
            title='child frame',
        ),
    }
    with local_server(child_routes, host='127.0.0.1') as child_base:
        parent_routes = {
            '/': lambda req: html(
                f"""
                <body>
                  <div id="parent-ready">Parent Ready</div>
                  <iframe id="child-frame" src="{child_base.replace('127.0.0.1', 'localhost')}/frame"></iframe>
                </body>
                """,
                title='parent page',
            ),
        }
        with local_server(parent_routes, host='127.0.0.1') as parent_base, make_browser(ctx.browser_path) as browser:
            tab = browser.latest_tab
            assert_true(tab.get(parent_base + '/'), 'parent page should load')
            assert_equal(tab('#parent-ready', timeout=5).text, 'Parent Ready', 'parent element should be found')
            frame_ele = tab('#inside-frame', timeout=5)
            assert_equal(frame_ele.text, 'Frame Domain', 'tab should locate inside cross-host iframe directly')
            frame = tab.get_frame(1, timeout=5)
            assert_equal(frame('#inside-frame', timeout=5).text, 'Frame Domain', 'frame fallback lookup should still work')
