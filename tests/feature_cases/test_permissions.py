"""Feature: browser and BrowserContext permission setters."""
from __future__ import annotations

from support import assert_true, html, local_server, make_browser


FEATURE_ID = 'permissions'

REQUIRES_BROWSER = True

def run(ctx):
    if ctx.skip_browser:
        ctx.skip('browser-backed permission setter checks skipped by --skip-browser')
        return

    routes = {'/': lambda req: html("<body>permissions</body>", title='permissions')}
    with local_server(routes) as base, make_browser(ctx.browser_path) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + '/'), 'permission test page should load')
        browser.set.perm.geolocation(False)
        browser.set.perm.geolocation(True)
        context = browser.new_context()
        try:
            context.set.perm.geolocation(False)
            context.set.perm.geolocation(True)
        finally:
            context.close()
