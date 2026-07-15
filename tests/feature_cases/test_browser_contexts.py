"""Feature: isolated browser contexts."""
from __future__ import annotations

from support import assert_in, assert_not_in, assert_true, html, local_server, make_browser


FEATURE_ID = 'browser_contexts'

REQUIRES_BROWSER = True

def run(ctx):
    if ctx.skip_browser:
        ctx.skip('browser-backed context checks skipped by --skip-browser')
        return

    routes = {
        '/cookie': lambda req: html("<body><div id='cookie'>cookie seed</div></body>", title='cookie seed'),
        '/echo-cookie': lambda req: html(
            f"<body><div id='cookie'>{req.headers.get('Cookie', '')}</div></body>", title='cookie echo'),
    }
    with local_server(routes) as base, make_browser(ctx.browser_path) as browser:
        ctx1 = browser.new_context()
        ctx2 = browser.new_context()
        try:
            t1 = ctx1.new_tab(base + '/cookie')
            t2 = ctx2.new_tab(base + '/cookie')
            t1.run_js("document.cookie = 'dp_ctx=one; path=/';")
            assert_true(t1.get(base + '/echo-cookie'), 'context 1 echo should load')
            assert_true(t2.get(base + '/echo-cookie'), 'context 2 echo should load')
            assert_in('dp_ctx=one', t1('#cookie').text, 'context 1 should keep its cookie')
            assert_not_in('dp_ctx=one', t2('#cookie').text, 'context 2 should not see context 1 cookie')
            assert_true(ctx1.latest_tab is not None, 'BrowserContext.latest_tab should be available')
            assert_true(isinstance(ctx1.tab_ids, list), 'BrowserContext.tab_ids should be a list')
            assert_true(ctx1.get_tab(id_or_num=t1.tab_id), 'BrowserContext.get_tab() should find tab by id')
            assert_true(ctx1.get_tabs(), 'BrowserContext.get_tabs() should return context tabs')
            ctx1.set.perm.geolocation(False)
            ctx1.set.perm.geolocation(True)
        finally:
            ctx1.close()
            ctx2.close()
