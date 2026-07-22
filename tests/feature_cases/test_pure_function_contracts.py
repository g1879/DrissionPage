"""Feature: deterministic contracts for shared pure-function helpers."""
from __future__ import annotations

from base64 import b64encode
from contextlib import redirect_stdout
from io import StringIO
from json import loads
from pathlib import Path
from tempfile import TemporaryDirectory

import DrissionPage.common as common
from DrissionPage._functions.by import By
from DrissionPage._functions.cookies import (
    CookiesList,
    cookie_to_dict,
    cookies_to_tuple,
    format_cookie,
    is_cookie_in_driver,
    set_browser_cookies,
    set_session_cookies,
    set_tab_cookies,
)
from DrissionPage._functions.keys import Keys, input_text_or_keys, keys_to_typing, make_input_data, send_key
from DrissionPage._functions.locator import (
    css_trans,
    get_loc,
    is_selenium_loc,
    is_str_loc,
    locator_to_tuple,
    quotes_escape,
    str_to_ax_loc,
    str_to_css_loc,
    str_to_xpath_loc,
    translate_css_loc,
    translate_loc,
)
from DrissionPage._functions.settings import Settings
from DrissionPage._functions.web import (
    NavResult,
    format_headers,
    format_html,
    get_blob,
    get_ele_txt,
    get_mhtml,
    get_pdf,
    get_proxy_info,
    is_js_func,
    location_in_viewport,
    make_absolute_link,
    offset_scroll,
    save_page,
    tree,
)
from DrissionPage.errors import AlertExistsError, LocatorError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = 'pure_function_contracts'
REQUIRES_BROWSER = False


def run(ctx):
    test_locator_contracts()
    test_cookie_contracts()
    test_web_contracts()
    test_key_contracts()
    test_settings_contracts()
    test_common_contracts()


def test_locator_contracts():
    tuple_cases = (
        ('.=hero', {'and': True, 'args': [['class', '=', 'hero', False]]}),
        ('@data-id=42', {'and': True, 'args': [['data-id', '=', '42', False]]}),
        ('tag=DIV', {'and': True, 'args': [['tag()', '=', 'div', False]]}),
        ('text=hello', {'and': True, 'args': [['text()', '=', 'hello', False]]}),
        ('@@id=main@@class:hero',
         {'and': True, 'args': [['id', '=', 'main', False], ['class', ':', 'hero', False]]}),
        ('@|id=main@|name=main',
         {'and': False, 'args': [['id', '=', 'main', False], ['name', '=', 'main', False]]}),
        ('@!disabled', {'and': True, 'args': [['disabled', None, None, True]]}),
    )
    for locator, expected in tuple_cases:
        assert_equal(locator_to_tuple(locator), expected, f'locator_to_tuple({locator!r}) mismatch')

    xpath_cases = (
        ('.=hero', ('xpath', '//*[@class="hero"]')),
        ('#=main', ('xpath', '//*[@id="main"]')),
        ('tag=DIV', ('xpath', '//*[name()="DIV"]')),
        ('text=hello', ('xpath', '//*[text()="hello"]')),
        ('text:hello', ('xpath', '//*/text()[contains(., "hello")]/..')),
        ('xpath://main/div', ('xpath', '//main/div')),
        ('css:div.item', ('css selector', 'div.item')),
        ('plain text', ('any', 'plain text')),
        ('', ('xpath', '//*')),
    )
    for locator, expected in xpath_cases:
        assert_equal(str_to_xpath_loc(locator), expected, f'str_to_xpath_loc({locator!r}) mismatch')

    css_cases = (
        ('.=hero', ('css selector', '*[class=hero]')),
        ('#=main', ('css selector', '*[id=main]')),
        ('tag=div@data-id=42', ('css selector', 'div[data-id=42]')),
        ('css:main > div', ('css selector', 'main > div')),
        ('text=hello', ('xpath', '//*[text()="hello"]')),
        ('', ('css selector', '*')),
    )
    for locator, expected in css_cases:
        assert_equal(str_to_css_loc(locator), expected, f'str_to_css_loc({locator!r}) mismatch')

    selenium_cases = (
        ((By.ID, 'alpha'), ('xpath', '//*[@id="alpha"]')),
        ((By.CLASS_NAME, 'hero'), ('xpath', '//*[@class="hero"]')),
        ((By.LINK_TEXT, 'Home'), ('xpath', '//a[text()="Home"]')),
        ((By.NAME, 'query'), ('xpath', '//*[@name="query"]')),
        ((By.TAG_NAME, 'section'), ('xpath', '//*[name()="section"]')),
        ((By.PARTIAL_LINK_TEXT, 'ome'), ('xpath', '//a[contains(text(),"ome")]')),
        ((By.CSS_SELECTOR, 'div.item'), ('css selector', 'div.item')),
    )
    for locator, expected in selenium_cases:
        assert_equal(get_loc(locator), expected, f'get_loc({locator!r}) mismatch')
        assert_equal(translate_loc(locator), expected, f'translate_loc({locator!r}) mismatch')

    assert_equal(str_to_ax_loc('ax:role=button@name=Save'),
                 ('ax', {'role': 'button', 'accessibleName': 'Save'}),
                 'accessibility locator fields should be normalized')
    assert_equal(str_to_ax_loc('ax:ignored=x@accessibleName:Open'),
                 ('ax', {'accessibleName': 'Open'}),
                 'accessibility locator should ignore unsupported fields')
    assert_equal(translate_css_loc((By.ID, 'main')), ('css selector', '#main'),
                 'ID should translate to a CSS selector')
    assert_equal(translate_css_loc((By.TAG_NAME, 'section')), ('css selector', 'section'),
                 'tag name should translate to a CSS selector')
    assert_equal(translate_css_loc((By.XPATH, '//main')), ('xpath', '//main'),
                 'XPath should remain XPath during CSS translation')

    assert_equal(quotes_escape("plain ' value"), '"plain \' value"',
                 'single quotes should not require XPath concat()')
    assert_equal(quotes_escape('a"b'), 'concat("a",\'"\',"b","")',
                 'double quotes should use an XPath concat() expression')
    assert_equal(css_trans('a b#c.d'), r'a\ b\#c\.d', 'CSS punctuation should be escaped')
    assert_true(is_str_loc('#=main'), 'locator prefix should be recognized')
    assert_false(is_str_loc('plain text'), 'plain text should not be classified as explicit locator syntax')
    assert_true(is_selenium_loc((By.ID, 'main')), 'valid Selenium-style tuple should be recognized')
    assert_false(is_selenium_loc(('unknown', 'main')), 'unknown Selenium locator strategy should be rejected')
    assert_false(is_selenium_loc((By.ID, 1)), 'non-string Selenium locator value should be rejected')
    _assert_raises(LocatorError, get_loc, 3.14)
    _assert_raises(LocatorError, translate_loc, (By.ID, 'one', 'extra'))


def test_cookie_contracts():
    source = {'name': 'sid', 'value': 'abc'}
    assert_true(cookie_to_dict(source) is source, 'cookie_to_dict(dict) should preserve the dict object')
    assert_equal(cookie_to_dict('sid=abc; domain=example.com; path=/; secure'),
                 {'name': 'sid', 'value': 'abc', 'domain': 'example.com', 'path': '/', 'secure': ''},
                 'Set-Cookie-style string should parse into cookie fields')
    assert_equal(cookies_to_tuple('a=1; b=two'),
                 ({'name': 'a', 'value': '1'}, {'name': 'b', 'value': 'two'}),
                 'cookie header string should split into individual cookies')
    assert_equal(cookies_to_tuple({'a': '1', 'b': 2, 'domain': 'example.com', 'path': '/'}),
                 ({'name': 'a', 'value': '1', 'domain': 'example.com', 'path': '/'},
                  {'name': 'b', 'value': 2, 'domain': 'example.com', 'path': '/'}),
                 'shared cookie attributes should be copied onto named cookies')
    assert_equal(cookies_to_tuple({'name': 'sid', 'value': 'x', 'secure': True}),
                 ({'name': 'sid', 'value': 'x', 'secure': True},),
                 'single cookie dict should remain one cookie')
    _assert_raises(ValueError, cookie_to_dict, object())
    _assert_raises(ValueError, cookies_to_tuple, object())

    format_cases = (
        ({'name': 'n', 'value': None, 'expiry': '123', 'sameSite': 'Lax',
          'priority': 'High', 'sourceScheme': 'Secure'},
         {'name': 'n', 'value': '', 'expires': 123, 'sameSite': 'Lax',
          'priority': 'High', 'sourceScheme': 'Secure'}),
        ({'name': '__Host-id', 'value': 3},
         {'name': '__Host-id', 'value': '3', 'path': '/', 'secure': True}),
        ({'name': '__Secure-id', 'value': 'x'},
         {'name': '__Secure-id', 'value': 'x', 'secure': True}),
        ({'name': 'n', 'value': 'x', 'expires': 'bad', 'sameSite': 'bad',
          'priority': None, 'sourceScheme': False},
         {'name': 'n', 'value': 'x'}),
    )
    for cookie, expected in format_cases:
        assert_equal(format_cookie(cookie.copy()), expected, f'format_cookie({cookie!r}) mismatch')
    _assert_raises(ValueError, format_cookie, {'name': 'n', 'value': 'x', 'priority': 'Urgent'})
    _assert_raises(ValueError, format_cookie, {'name': 'n', 'value': 'x', 'sourceScheme': 'HTTP'})

    cookies = CookiesList(({'name': 'a', 'value': '1'}, {'name': 'b', 'value': 'two'}))
    assert_equal(cookies.as_dict(), {'a': '1', 'b': 'two'}, 'CookiesList.as_dict() mismatch')
    assert_equal(cookies.as_str(), 'a=1; b=two', 'CookiesList.as_str() mismatch')
    assert_equal(loads(cookies.as_json()), list(cookies), 'CookiesList.as_json() should serialize the list')

    session = _FakeSession()
    set_session_cookies(session, ({'name': 'sid', 'value': None, 'expiry': 123, 'path': '/'},))
    assert_equal(session.cookies.calls, [('sid', '', {'expires': 123, 'path': '/'})],
                 'session cookie setter should normalize value and expiry')

    default_browser = _FakeBrowser(default_context=True)
    set_browser_cookies(default_browser, {'name': 'sid', 'value': 7, 'domain': 'example.com'})
    assert_equal(default_browser.calls,
                 [('Storage.setCookies', {'cookies': [{'name': 'sid', 'value': '7', 'domain': 'example.com'}]})],
                 'default browser context should set cookies without a context id')
    isolated_browser = _FakeBrowser(default_context=False)
    set_browser_cookies(isolated_browser, {'name': 'sid', 'value': 'x', 'url': 'https://example.com'})
    assert_equal(isolated_browser.calls[0][1]['browserContextId'], 'ctx-1',
                 'isolated browser cookie setter should include browser context id')
    _assert_raises(ValueError, set_browser_cookies, default_browser, {'name': 'sid', 'value': 'x'})

    tab = _FakeCookieTab('https://example.com/path')
    set_tab_cookies(tab, ({'name': '__Host-id', 'value': '1'},
                          {'name': 'domain-id', 'value': '2', 'domain': 'example.com'}))
    assert_equal(tab.calls[0][1],
                 {'name': '__Host-id', 'value': '1', 'path': '/', 'secure': True,
                  'url': 'https://example.com/path'},
                 '__Host- cookie should bind to the current HTTP URL')
    assert_equal(tab.calls[1][1]['domain'], 'example.com', 'domain cookie should retain explicit domain')
    assert_true(is_cookie_in_driver(tab, {'name': 'domain-id', 'value': '2', 'domain': 'example.com'}),
                'cookie lookup should match name, value, and domain')
    assert_false(is_cookie_in_driver(tab, {'name': 'missing', 'value': 'x'}),
                 'cookie lookup should report a missing cookie')


def test_web_contracts():
    assert_equal(format_html('&lt;a&gt;&nbsp;&amp;'), '<a> &', 'HTML entities should be unescaped')
    assert_equal(format_html(''), '', 'empty HTML text should remain empty')
    html_ele = common.make_session_ele('<div>one <span>two</span><br>three &amp; four</div>')
    assert_equal(get_ele_txt(html_ele), 'one two\nthree & four', 'element text should preserve inline and br semantics')

    link_cases = (
        ('../asset.js', 'https://example.com/a/b/', 'https://example.com/a/asset.js'),
        ('//cdn.example.com/x', 'https://example.com/a', 'https://cdn.example.com/x'),
        ('https://cdn.example.com/x', 'https://example.com/a', 'https://cdn.example.com/x'),
        (' images\\a.png ', None, 'images/a.png'),
        ('', 'https://example.com/', ''),
        (None, 'https://example.com/', None),
    )
    for link, base, expected in link_cases:
        assert_equal(make_absolute_link(link, base), expected, f'make_absolute_link({link!r}) mismatch')

    for script in ('function(){return 1;}', ' async function(){return 1;} '):
        assert_true(is_js_func(script), f'{script!r} should be recognized as a JavaScript function')
    for script in ('return 1;', 'value => value'):
        assert_false(is_js_func(script), f'{script!r} should not be recognized as a function wrapper')

    dict_headers = {':method': 'GET', 'Count': 3, 'Enabled': True, 'Empty': None}
    assert_equal(format_headers(dict_headers), {'Count': '3', 'Enabled': True, 'Empty': None},
                 'dict headers should remove pseudo headers and stringify scalar values')
    assert_equal(format_headers(':method: GET\nAccept: text/plain\nX-Test: yes'),
                 {'Accept': 'text/plain', 'X-Test': 'yes'},
                 'text headers should parse and omit pseudo headers')

    proxy_cases = (
        (' http://u:p@host.test:8080 ', ('http://host.test:8080', 'u', 'p', 'http://u:p@host.test:8080')),
        ('u:p@host.test:8080', ('host.test:8080', 'u', 'p', 'u:p@host.test:8080')),
        ('host.test:8080', ('host.test:8080', None, None, 'host.test:8080')),
    )
    for proxy, expected in proxy_cases:
        assert_equal(get_proxy_info(proxy), expected, f'get_proxy_info({proxy!r}) mismatch')

    page = _FakeWebPage()
    assert_true(location_in_viewport(page, 10, 20), 'viewport helper should return JavaScript result')
    assert_in('let x = 10; let y = 20;', page.js_calls[-1][0], 'viewport helper should embed coordinates')
    assert_equal(get_blob(page, 'blob:test', as_bytes=True), b'blob body', 'blob helper should decode data URL')
    assert_equal(get_blob(page, 'blob:test', as_bytes=False), page.blob_data,
                 'blob helper should return data URL when bytes are disabled')
    _assert_raises(ValueError, get_blob, page, 'https://example.com/file')
    _assert_raises(RuntimeError, get_blob, _BrokenBlobPage(), 'blob:test')

    owner = _FakeScrollOwner()
    assert_equal(offset_scroll(_FakeScrollElement(owner), 5, 6), (25, 36),
                 'offset scroll should return viewport coordinates')
    assert_equal(owner.scroll.calls, [(55, 106)], 'offscreen point should scroll toward viewport center')

    with TemporaryDirectory(prefix='dp-pure-web-') as tmp:
        archive_page = _FakeArchivePage()
        assert_equal(get_mhtml(archive_page), 'snapshot', 'get_mhtml() should return captured data')
        assert_equal(get_mhtml(archive_page, tmp, 'page'), 'snapshot', 'get_mhtml() should return saved data')
        assert_equal(Path(tmp, 'page.mhtml').read_text(encoding='utf-8'), 'snapshot',
                     'get_mhtml() should write the snapshot')
        assert_equal(get_pdf(archive_page), b'pdf bytes', 'get_pdf() should decode PDF bytes')
        assert_equal(get_pdf(archive_page, tmp, 'page'), b'pdf bytes', 'get_pdf() should return saved bytes')
        assert_equal(Path(tmp, 'page.pdf').read_bytes(), b'pdf bytes', 'get_pdf() should write PDF bytes')
        assert_equal(save_page(archive_page, Path(tmp, 'saved.mhtml')), 'snapshot',
                     'save_page() should infer MHTML from suffix')
        assert_equal(save_page(archive_page, Path(tmp, 'saved.pdf')), b'pdf bytes',
                     'save_page() should infer PDF from suffix')
        assert_equal(save_page(archive_page, tmp, 'named.pdf'), b'pdf bytes',
                     'save_page() should infer PDF from the name suffix')
        assert_equal(save_page(archive_page, tmp, 'named.mhtml'), 'snapshot',
                     'save_page() should infer MHTML from the name suffix')
        pdf_kwargs = {'landscape': True, 'printBackground': False}
        assert_equal(save_page(archive_page, tmp, 'explicit', as_pdf=True, kwargs=pdf_kwargs), b'pdf bytes',
                     'save_page(as_pdf=True) should forward PDF options')
        assert_equal(pdf_kwargs['transferMode'], 'ReturnAsBase64', 'PDF helper should request base64 transfer mode')
        assert_false(pdf_kwargs['printBackground'], 'explicit printBackground should be preserved')
        _assert_raises(RuntimeError, get_pdf, _BrokenPdfPage())

        tree_root = _TreeNode('html', {'lang': 'en'}, 'root text', [
            _TreeNode('body', {'id': 'main'}, 'body text', [
                _TreeNode('script', {}, 'console.log(1)', []),
                _TreeNode('style', {}, 'body { color: red; }', []),
                _TreeNode('p', {'class': 'item'}, 'paragraph text', []),
            ]),
        ])
        output = StringIO()
        with redirect_stdout(output):
            tree(_TreePage(tree_root), text=9)
        rendered = output.getvalue()
        assert_in("<html lang='en'> root text", rendered, 'tree() should render root attributes and truncated text')
        assert_in("<body id='main'> body text", rendered, 'tree() should render nested elements')
        assert_in("<p class='item'> paragraph", rendered, 'tree() should truncate ordinary text to the requested length')
        assert_false('console.log' in rendered, 'tree() should hide script text by default')
        assert_false('color: red' in rendered, 'tree() should hide style text by default')
        output = StringIO()
        with redirect_stdout(output):
            tree(_TreePage(tree_root), text=True, show_js=True, show_css=True)
        rendered = output.getvalue()
        assert_in('console.log(1)', rendered, 'tree(show_js=True) should include script text')
        assert_in('body { color: red; }', rendered, 'tree(show_css=True) should include style text')

    nav = NavResult()
    assert_equal(nav.ok, None, 'unset navigation status should have unknown ok state')
    assert_false(bool(nav), 'unset navigation result should be falsey')
    nav.url = 'https://example.com/'
    nav.status = 204
    assert_true(nav.ok, '2xx navigation status should be successful')
    assert_true(bool(nav), 'successful navigation result should be truthy')
    assert_equal(repr(nav), '<NavResult url: https://example.com/, status: 204 >', 'NavResult repr mismatch')
    nav.status = 404
    assert_false(nav.ok, '4xx navigation status should be unsuccessful')
    nav.status = 'connection error'
    assert_false(nav.ok, 'text navigation status should be unsuccessful')


def test_key_contracts():
    typing_cases = (
        ((Keys.CONTROL, 'ab', 12, 3.5), (2, 'ab123.5')),
        ((Keys.SHIFT, Keys.ALT, 'x'), (9, 'x')),
        ((Keys.COMMAND, 'a'), (4, 'a')),
        (('plain',), (0, 'plain')),
    )
    for value, expected in typing_cases:
        assert_equal(keys_to_typing(value), expected, f'keys_to_typing({value!r}) mismatch')

    letter = make_input_data(0, 'a')
    assert_equal({k: letter[k] for k in ('modifiers', 'key', 'text', 'code', 'type', 'location', 'isKeypad')},
                 {'modifiers': 0, 'key': 'a', 'text': 'a', 'code': 'KeyA', 'type': 'keyDown',
                  'location': 0, 'isKeypad': False},
                 'letter key event payload mismatch')
    assert_true(letter['_ignore'] is AlertExistsError, 'key event should ignore alert interruption')
    control = make_input_data(2, 'a')
    assert_equal((control['text'], control['type']), ('', 'rawKeyDown'),
                 'control-modified key should suppress text and use rawKeyDown')
    shifted = make_input_data(8, '!')
    assert_equal((shifted['key'], shifted['text']), ('!', '!'), 'shift should select shifted key value')
    released = make_input_data(0, Keys.ENTER, key_up=True)
    assert_equal((released['key'], released['text'], released['type']), ('Enter', '\r', 'keyUp'),
                 'key-up event payload mismatch')
    assert_equal(make_input_data(0, '界'), None, 'unknown key should not produce a key event payload')

    page = _FakeInputPage()
    send_key(page, 0, 'a')
    assert_equal([call[1]['type'] for call in page.calls], ['keyDown', 'keyUp'],
                 'send_key() should dispatch down and up events')
    page.calls.clear()
    send_key(page, 0, '界')
    assert_equal(page.calls, [('Input.insertText', {'text': '界', '_ignore': AlertExistsError})],
                 'unknown key should fall back to insertText')
    page.calls.clear()
    input_text_or_keys(page, 'hello')
    assert_equal(page.calls, [('Input.insertText', {'text': 'hello', '_ignore': AlertExistsError})],
                 'plain input should use one insertText call')
    page.calls.clear()
    input_text_or_keys(page, 'hello\n')
    assert_equal(page.calls[0], ('Input.insertText', {'text': 'hello', '_ignore': AlertExistsError}),
                 'newline input should insert preceding text first')
    assert_equal([call[1]['type'] for call in page.calls[1:]], ['keyDown', 'keyUp'],
                 'newline input should dispatch Enter down and up')


def test_settings_contracts():
    names = ('wait_stop_before_click', 'raise_when_ele_not_found', 'raise_when_click_failed',
             'raise_when_wait_failed', 'singleton_tab_obj', 'cdp_timeout', 'browser_connect_timeout',
             'auto_handle_alert', 'suffixes_list', '_lang')
    old = {name: getattr(Settings, name) for name in names}
    try:
        setter_cases = (
            (Settings.set_wait_stop_before_click, False, 'wait_stop_before_click'),
            (Settings.set_raise_when_ele_not_found, True, 'raise_when_ele_not_found'),
            (Settings.set_raise_when_click_failed, True, 'raise_when_click_failed'),
            (Settings.set_raise_when_wait_failed, True, 'raise_when_wait_failed'),
            (Settings.set_singleton_tab_obj, False, 'singleton_tab_obj'),
            (Settings.set_cdp_timeout, 1.5, 'cdp_timeout'),
            (Settings.set_browser_connect_timeout, 2.5, 'browser_connect_timeout'),
            (Settings.set_auto_handle_alert, False, 'auto_handle_alert'),
        )
        for setter, value, attr in setter_cases:
            assert_true(setter(value) is Settings, f'{setter.__name__}() should return Settings')
            assert_equal(getattr(Settings, attr), value, f'{setter.__name__}() should update {attr}')

        with TemporaryDirectory(prefix='dp-settings-') as tmp:
            relative = Path(tmp, '..', Path(tmp).name)
            assert_true(Settings.set_suffixes_list(relative) is Settings,
                        'set_suffixes_list() should return Settings')
            assert_equal(Settings.suffixes_list, str(relative.resolve()).replace('\\', '/'),
                         'set_suffixes_list() should store a normalized absolute path')

        assert_true(Settings.set_language('en') is Settings, 'set_language() should return Settings')
        assert_true(hasattr(Settings._lang, 'INCORRECT_TYPE_'), 'selected language should expose message fields')
    finally:
        for name, value in old.items():
            setattr(Settings, name, value)


def test_common_contracts():
    expected_exports = ('make_session_ele', 'Actions', 'Keys', 'By', 'Settings', 'wait_until', 'configs_to_here',
                        'get_blob', 'tree', 'from_selenium', 'from_playwright')
    assert_equal(tuple(common.__all__), expected_exports, 'DrissionPage.common exports mismatch')
    assert_true(common.Keys is Keys, 'common.Keys should expose the shared Keys class')
    assert_true(common.By is By, 'common.By should expose the shared By class')
    assert_true(common.Settings is Settings, 'common.Settings should expose the shared Settings class')

    class MissingSeleniumAddress:
        caps = {}

    class BrokenPlaywrightBrowser:
        def new_browser_cdp_session(self):
            raise RuntimeError('unavailable')

    _assert_raises(RuntimeError, common.from_selenium, MissingSeleniumAddress())
    _assert_raises(RuntimeError, common.from_playwright, BrokenPlaywrightBrowser())

    class FakeOptions:
        def __init__(self):
            self.port = None
            self._ua_set = False

        def set_local_port(self, port):
            self.port = port
            return self

    old_chromium = common.Chromium
    old_options = common.ChromiumOptions
    common.Chromium = lambda options: options
    common.ChromiumOptions = FakeOptions
    try:
        selenium = type('SeleniumDriver', (), {
            'caps': {'goog:chromeOptions': {'debuggerAddress': '127.0.0.1:9222'}},
        })()
        converted = common.from_selenium(selenium)
        assert_equal(converted.port, '9222', 'from_selenium() should reuse the debugger port')
        assert_true(converted._ua_set, 'from_selenium() should mark user-agent setup complete')

        class Session:
            def send(self, method):
                assert_equal(method, 'SystemInfo.getProcessInfo', 'from_playwright() should query process info')
                return {'processInfo': [{'type': 'renderer', 'id': 1}, {'type': 'browser', 'id': 42}]}

        class Browser:
            def new_browser_cdp_session(self):
                return Session()

        page = type('Page', (), {'context': type('Context', (), {'browser': Browser()})()})()
        import psutil
        old_connections = psutil.net_connections
        psutil.net_connections = lambda: [
            type('Connection', (), {'pid': 7, 'laddr': type('Addr', (), {'port': 1})()})(),
            type('Connection', (), {'pid': 42, 'laddr': type('Addr', (), {'port': 9333})()})(),
        ]
        try:
            converted = common.from_playwright(page)
        finally:
            psutil.net_connections = old_connections
        assert_equal(converted.port, 9333, 'from_playwright() should resolve the browser process port')
        assert_true(converted._ua_set, 'from_playwright() should mark user-agent setup complete')

        class NoBrowserProcess:
            def new_browser_cdp_session(self):
                return type('Session', (), {'send': lambda self, method: {'processInfo': []}})()

        _assert_raises(RuntimeError, common.from_playwright, NoBrowserProcess())
    finally:
        common.Chromium = old_chromium
        common.ChromiumOptions = old_options


def _assert_raises(error_type, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except error_type:
        return
    except Exception as error:
        raise AssertionError(
            f'{func.__name__}() raised {type(error).__name__}, expected {error_type.__name__}'
        ) from error
    raise AssertionError(f'{func.__name__}() did not raise {error_type.__name__}')


class _CookieRecorder:
    def __init__(self):
        self.calls = []

    def set(self, name, value, **kwargs):
        self.calls.append((name, value, kwargs))


class _FakeSession:
    def __init__(self):
        self.cookies = _CookieRecorder()


class _FakeBrowser:
    def __init__(self, default_context):
        self._default_context = default_context
        self._context_id = 'ctx-1'
        self.calls = []

    def _run_cdp(self, method, **kwargs):
        self.calls.append((method, kwargs))


class _FakeCookieTab:
    def __init__(self, url):
        self.url = url
        self._browser_url = url
        self.calls = []
        self.stored = []

    def _run_cdp_loaded(self, method, **kwargs):
        self.calls.append((method, kwargs.copy()))
        self.stored.append(kwargs.copy())

    def cookies(self, all_domains=False):
        assert_true(all_domains, 'cookie verification should request all domains')
        return self.stored


class _FakeWebPage:
    blob_data = 'data:application/octet-stream;base64,' + b64encode(b'blob body').decode()

    def __init__(self):
        self.js_calls = []

    def _run_js(self, script, *args):
        self.js_calls.append((script, args))
        return self.blob_data if args else True


class _BrokenBlobPage:
    def _run_js(self, script, *args):
        raise RuntimeError('blob unavailable')


class _FakeScroll:
    def __init__(self):
        self.calls = []

    def to_location(self, x, y):
        self.calls.append((x, y))


class _FakeScrollOwner:
    def __init__(self):
        self.scroll = _FakeScroll()

    def _run_js(self, script):
        if script.startswith('function()'):
            return False
        if 'clientWidth' in script:
            return 100
        if 'clientHeight' in script:
            return 200
        return False


class _FakeRect:
    location = (100, 200)
    click_point = (110, 220)
    viewport_location = (20, 30)
    viewport_click_point = (25, 35)


class _FakeScrollElement:
    rect = _FakeRect()

    def __init__(self, owner):
        self.owner = owner


class _FakeArchivePage:
    title = 'archive'

    def _run_cdp(self, method, **kwargs):
        if method == 'Page.captureSnapshot':
            return {'data': 'snapshot'}
        if method == 'Page.printToPDF':
            return {'data': b64encode(b'pdf bytes').decode()}
        raise AssertionError(f'unexpected CDP method: {method}')


class _BrokenPdfPage:
    def _run_cdp(self, method, **kwargs):
        raise RuntimeError('print unavailable')


class _TreeNode:
    def __init__(self, tag, attrs, text, children):
        self.tag = tag
        self.attrs = attrs
        self._text = text
        self._children = children

    def children(self):
        return self._children

    def __call__(self, locator):
        assert_equal(locator, 'x:/text()', 'tree() should request direct text nodes')
        return self._text


class _TreePage:
    def __init__(self, root):
        self.root = root

    def s_ele(self):
        return self.root


class _FakeInputPage:
    def __init__(self):
        self.calls = []

    def _run_cdp(self, method, **kwargs):
        self.calls.append((method, kwargs.copy()))
