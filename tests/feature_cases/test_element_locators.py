"""Feature: ax: locator, automatic locator matching, and non-string tab ele() results."""
from __future__ import annotations

from DrissionPage._elements.session_element import make_session_ele
from DrissionPage._functions.locator import get_loc

from support import assert_equal, assert_false, assert_true, html, local_server, make_browser


FEATURE_ID = 'element_locators'

BROWSER_PHASE = True

def run(ctx):
    test_no_browser_locator_contracts()
    if ctx.skip_browser:
        ctx.skip_current_browser('browser-backed locator checks skipped by --skip-browser')
        return
    test_browser_locator_contracts(ctx.browser_path)


def test_no_browser_locator_contracts():
    assert_equal(get_loc('ax:@name=文档@role=link'), ('ax', {'accessibleName': '文档', 'role': 'link'}),
                 'ax locator should parse name and role')
    assert_equal(get_loc('ax:@accessibleName=主导航@role=navigation'),
                 ('ax', {'accessibleName': '主导航', 'role': 'navigation'}),
                 'ax locator should accept accessibleName explicitly')

    document = """
    <html><body>
      <button aria-label="Docs">Docs</button>
      <div id="app" class="raw-css-target">OK<span>child</span></div>
    </body></html>
    """
    assert_equal(make_session_ele(document, 'x://div[@id="app"]').attr('id'), 'app',
                 'SessionElement should support explicit XPath lookup')
    assert_equal(make_session_ele(document, 'css:.raw-css-target').attr('id'), 'app',
                 'SessionElement should support explicit CSS lookup')
    assert_equal(str(make_session_ele(document, 'x://div[@id="app"]/text()')), 'OK',
                 'SessionElement XPath text-node behavior should remain available')

    try:
        make_session_ele('<button aria-label="Docs">Docs</button>', 'ax:@name=Docs@role=button')
    except ValueError as exc:
        assert_true('不支持' in str(exc) or 'not support' in str(exc),
                    'SessionElement should reject ax: with clear unsupported message')
    else:
        raise AssertionError('SessionElement should not support ax: locators')


def test_browser_locator_contracts(executable):
    routes = {
        '/': lambda req: html(
            """
            <body>
              <button id="parent-button" aria-label="Parent Action">Parent Button</button>
              <p id="text-confuser">div</p>
              <div class="raw-css-target">Raw CSS</div>
              <div id="strict-target">Strict Element</div>
              <div id="text-host"><span>Nested Element</span></div>
            </body>
            """,
            title='locator page',
        ),
    }
    with local_server(routes) as base, make_browser(executable) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + '/'), 'locator page should load')
        assert_equal(tab('//button[@id="parent-button"]', timeout=5).text, 'Parent Button', 'raw XPath should locate')
        assert_equal(tab('.raw-css-target', timeout=5).text, 'Raw CSS', 'raw CSS should locate')
        assert_equal(tab('div#strict-target', timeout=5).text, 'Strict Element',
                     'raw CSS should locate a div even when page text contains the word div')
        assert_equal(tab('text:div', timeout=5).attr('id'), 'text-confuser',
                     'explicit text locator should still locate text content')
        ax_button = tab('ax:@name=Parent Action@role=button', timeout=5)
        assert_equal(ax_button.attr('id'), 'parent-button', 'ax locator should find accessible button')
        text_result = tab('x://div[@id="text-host"]/text()', timeout=2)
        assert_false(isinstance(text_result, str), 'Chromium tab ele() should not return raw text string')
