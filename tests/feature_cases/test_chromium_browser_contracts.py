"""Feature: deterministic Chromium browser, tab, base-page, and frame contracts."""
from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace

import DrissionPage._browsers.chromium as chromium_module
import DrissionPage._pages.chromium_base as chromium_base_module
import DrissionPage._pages.chromium_tab as chromium_tab_module
from DrissionPage._browsers.chromium import Chromium, Tabs
from DrissionPage._pages.chromium_base import ChromiumBase, Timeout
from DrissionPage._pages.chromium_frame import ChromiumFrame
from DrissionPage._pages.chromium_tab import ChromiumTab
from DrissionPage.errors import BrowserConnectError, JavaScriptError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = 'chromium_browser_contracts'
REQUIRES_BROWSER = False


def run(ctx):
    test_browser_properties_context_cookies_and_latest_tab()
    test_browser_tab_lookup_activation_and_close_normalization()
    test_tabs_bookkeeping_contracts()
    test_chromium_base_properties_widgets_cookies_and_storage()
    test_chromium_tab_delegation_close_and_disconnect()
    test_chromium_frame_properties_delegation_and_bookkeeping()


@contextmanager
def _patched(target, **replacements):
    originals = {name: getattr(target, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(target, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(target, name, value)


@contextmanager
def _preserved_dict(mapping):
    original = dict(mapping)
    try:
        yield
    finally:
        mapping.clear()
        mapping.update(original)


def _assert_raises(expected, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except expected as error:
        return error
    except Exception as error:
        raise AssertionError(
            f'{func.__name__} raised {type(error).__name__}, expected {expected.__name__}'
        ) from error
    raise AssertionError(f'{func.__name__} did not raise {expected.__name__}')


def test_browser_properties_context_cookies_and_latest_tab():
    browser = object.__new__(Chromium)
    browser._browser_id = 'browser-1'
    browser._chromium_options = SimpleNamespace(user_data_path='/tmp/profile')
    browser._process_id = 321
    browser._timeouts = Timeout(base=2, page_load=3, script=4)
    browser._load_mode = 'eager'
    browser._download_path = '/tmp/downloads'
    browser._context = None

    assert_equal(browser.id, 'browser-1', 'id should expose the browser target id')
    assert_equal(browser.user_data_path, '/tmp/profile', 'user_data_path should delegate to options')
    assert_equal(browser.process_id, 321, 'process_id should expose the discovered process id')
    assert_equal(browser.timeout, 2, 'timeout should expose the base timeout')
    assert_true(browser.timeouts is browser._timeouts, 'timeouts should preserve the timeout object')
    assert_equal(browser.load_mode, 'eager', 'load_mode should expose the configured mode')
    assert_equal(browser.download_path, '/tmp/downloads', 'download_path should expose the resolved path')

    context_calls = []

    class FakeContext:
        def __init__(self, owner, context_id):
            context_calls.append((owner, context_id))
            self.owner = owner
            self.id = context_id

    with _patched(chromium_module, ChromiumContext=FakeContext):
        context = browser.context
        assert_true(browser.context is context, 'context should cache its wrapper')
    assert_equal(context_calls, [(browser, 'browser-1')], 'context should use the default browser context id')

    cookie_calls = []
    cookie_payload = [
        {'name': 'sid', 'value': 'abc', 'domain': 'example.test', 'path': '/', 'secure': True},
        {'name': 'theme', 'value': 'dark', 'domain': 'example.test', 'path': '/'},
    ]

    def run_cdp(method, **kwargs):
        cookie_calls.append((method, kwargs))
        assert_equal(method, 'Storage.getCookies', 'browser cookies should use Storage.getCookies')
        return {'cookies': cookie_payload}

    browser._run_func = run_cdp
    reduced = browser.cookies()
    assert_equal(
        reduced,
        [
            {'name': 'sid', 'value': 'abc', 'domain': 'example.test'},
            {'name': 'theme', 'value': 'dark', 'domain': 'example.test'},
        ],
        'default browser cookies should expose the compact public shape',
    )
    assert_equal(browser._cookies(all_info=True, context_id='context-2'), cookie_payload,
                 'all_info browser cookies should preserve protocol fields')
    assert_equal(cookie_calls[-1], ('Storage.getCookies', {'browserContextId': 'context-2'}),
                 'context cookies should use the exact browser context id')
    assert_equal(reduced.as_dict(), {'sid': 'abc', 'theme': 'dark'},
                 'browser cookies should retain CookiesList helpers')

    lookup_calls = []
    browser._tab_ids = lambda context_id: ['tab-new']
    browser._get_tab = lambda context_id, **kwargs: lookup_calls.append((context_id, kwargs)) or 'tab-object'
    with _patched(chromium_module._S, singleton_tab_obj=True):
        assert_equal(browser.latest_tab, 'tab-object', 'latest_tab should return the tab wrapper in singleton mode')
    assert_equal(
        lookup_calls[-1],
        ('browser-1', {'id_or_num': 'tab-new', 'as_id': False}),
        'latest_tab should resolve the newest target in the default context',
    )

    with _patched(chromium_module._S, singleton_tab_obj=False):
        assert_equal(browser.latest_tab, 'tab-object', 'latest_tab should preserve delegated id-mode results')
    assert_equal(lookup_calls[-1][1]['as_id'], True, 'non-singleton latest_tab should request an id result')

    browser._tab_ids = lambda context_id: []
    browser.new_tab = lambda: SimpleNamespace(tab_id='created-tab')
    with _patched(chromium_module._S, singleton_tab_obj=True):
        assert_equal(browser.latest_tab.tab_id, 'created-tab', 'latest_tab should create a tab when none exist')
    with _patched(chromium_module._S, singleton_tab_obj=False):
        assert_equal(browser.latest_tab, 'created-tab', 'id mode should return the created tab id')


def test_browser_tab_lookup_activation_and_close_normalization():
    browser = object.__new__(Chromium)
    browser._browser_id = 'context-main'
    browser._ws_only = True
    target_infos = [
        {
            'targetId': 'tab-a',
            'browserContextId': 'context-main',
            'type': 'page',
            'title': 'Alpha dashboard',
            'url': 'https://example.test/a',
        },
        {
            'targetId': 'tab-b',
            'browserContextId': 'context-main',
            'type': 'page',
            'title': 'Beta dashboard',
            'url': 'https://example.test/b',
        },
        {
            'targetId': 'worker-1',
            'browserContextId': 'context-main',
            'type': 'worker',
            'title': 'background',
            'url': 'https://example.test/worker.js',
        },
        {
            'targetId': 'other-context',
            'browserContextId': 'context-other',
            'type': 'page',
            'title': 'Other',
            'url': 'https://example.test/other',
        },
    ]
    cdp_calls = []

    def run_cdp(method, **kwargs):
        cdp_calls.append((method, kwargs))
        if method == 'Target.getTargets':
            return {'targetInfos': target_infos}
        return None

    browser._run_func = run_cdp

    class FakeTab:
        def __init__(self, owner, tab_id, context_id):
            self.browser = owner
            self.tab_id = tab_id
            self.context_id = context_id

    with _patched(chromium_module, ChromiumTab=FakeTab):
        assert_equal(
            browser._get_tab_ids('context-main', 'page', 'Beta', '/b'),
            ['tab-b'],
            'tab discovery should normalize a string tab type and apply title/url filters',
        )
        assert_equal(browser._get_tab('context-main', as_id=True), 'tab-a',
                     'default tab lookup should return the first matching id')
        assert_equal(browser._get_tab('context-main', id_or_num=2, as_id=True), 'tab-b',
                     'positive tab numbers should use one-based selection')
        assert_equal(browser._get_tab('context-main', id_or_num=0, as_id=True), 'tab-a',
                     'zero should select the first tab')
        assert_equal(browser._get_tab('context-main', id_or_num=-1, as_id=True), 'tab-b',
                     'negative tab numbers should use Python-style indexing')
        assert_equal(browser._get_tab('context-main', id_or_num='tab-b', as_id=True), 'tab-b',
                     'valid explicit tab ids should pass through unchanged')

        existing = FakeTab(browser, 'tab-a', 'old-context')
        wrapped = browser._get_tab('context-main', id_or_num=existing)
        assert_equal((wrapped.tab_id, wrapped.context_id), ('tab-a', 'context-main'),
                     'tab-object lookup should normalize to the requested context')

        tabs = browser._get_tabs('context-main')
        assert_equal([tab.tab_id for tab in tabs], ['tab-a', 'tab-b'],
                     'multi-tab lookup should return wrappers in protocol order')
        assert_true(all(isinstance(tab, FakeTab) for tab in tabs),
                    'multi-tab object mode should preserve the wrapper return shape')
        _assert_raises(RuntimeError, browser._get_tab, 'context-main', id_or_num='missing-tab')

        browser._tab_ids = lambda context_id: ['tab-a', 'tab-b', 'tab-c']
        browser.activate_tab(1)
        browser.activate_tab('tab-b')
        browser.activate_tab(FakeTab(browser, 'tab-c', 'context-main'))

        activation_ids = [kwargs['targetId'] for method, kwargs in cdp_calls
                          if method == 'Target.activateTarget']
        assert_equal(activation_ids, ['tab-a', 'tab-b', 'tab-c'],
                     'activate_tab should normalize number, id, and tab-object inputs')

        closed = []
        quits = []
        browser._close_tab = lambda tab: closed.append(tab)
        browser.quit = lambda: quits.append(True)

        browser.close_tabs(FakeTab(browser, 'tab-a', 'context-main'))
        assert_equal(closed, ['tab-a'], 'close_tabs should normalize a tab wrapper to its id')
        closed.clear()
        browser.close_tabs(['tab-a', FakeTab(browser, 'tab-b', 'context-main')])
        assert_equal(set(closed), {'tab-a', 'tab-b'}, 'close_tabs should normalize mixed tab/id lists')
        closed.clear()
        browser.close_tabs('tab-a', others=True)
        assert_equal(set(closed), {'tab-b', 'tab-c'}, 'others=True should close the complement of the keep set')
        browser.close_tabs(['tab-a', 'tab-b', 'tab-c'])
        assert_equal(quits, [True], 'closing every tab should delegate to browser quit')
        _assert_raises(ValueError, browser.close_tabs, {'tab-a'})


def test_tabs_bookkeeping_contracts():
    tabs = Tabs()

    class StopProbe:
        def __init__(self):
            self.stops = 0

        def _stop_messenger(self):
            self.stops += 1

    first = StopProbe()
    second = StopProbe()
    replacement = StopProbe()
    tabs.add('session-1', 'target-1', context_id='context-1', opener='opener-1', obj=first)
    tabs.add('session-2', 'target-1', context_id='context-1', obj=second)
    tabs.add('session-3', 'target-2', context_id='context-2')
    tabs.add_obj('session-3', replacement)
    tabs.add_obj('missing-session', StopProbe())
    tabs.add_frame('frame-1', 'target-1')
    tabs.add_frame('frame-2', 'target-2')

    assert_equal(set(tabs.session_ids), {'session-1', 'session-2', 'session-3'},
                 'session_ids should expose every tracked session')
    assert_equal(set(tabs.target_ids), {'target-1', 'target-2'},
                 'target_ids should expose every tracked target')
    assert_equal(set(tabs.objects), {first, second, replacement},
                 'objects should expose registered session owners')
    assert_equal(tabs.openers, {'target-1': 'opener-1'}, 'openers should retain target relationships')
    assert_equal(tabs.frame_ids, {'frame-1': 'target-1', 'frame-2': 'target-2'},
                 'frame_ids should map frames to their owning targets')
    assert_equal(tabs.get_session_ids('target-1'), {'session-1', 'session-2'},
                 'target lookup should return every attached session')
    assert_equal(tabs.get_target_id('session-2'), 'target-1',
                 'session lookup should return its target id')
    assert_equal(tabs.get_context_id(target_id='target-1'), 'context-1',
                 'target context lookup should return the tracked context')
    assert_equal(tabs.get_context_id(frame_id='frame-2'), 'context-2',
                 'frame context lookup should resolve through its target')
    assert_true(tabs.get_object('session-3') is replacement,
                'add_obj should attach an owner only to a known session')
    fallback = object()
    assert_true(tabs.get_object('missing', fallback) is fallback,
                'get_object should preserve an explicit fallback')

    main_proxy = ('http://main:8000', 'main-user', 'main-pass', 'main-full')
    context_proxy = ('http://ctx:9000', 'ctx-user', 'ctx-pass', 'ctx-full')
    tabs.set_proxy('main', main_proxy)
    tabs.set_proxy('context-1', context_proxy)
    assert_equal(tabs.get_proxy('context-1'), context_proxy, 'context proxy should override the main proxy')
    assert_equal(tabs.get_proxy('unknown'), main_proxy, 'unknown contexts should inherit the main proxy')

    tabs.set_newest_tab('context-1', 'target-1')
    assert_equal(tabs.get_newest_tab('context-1'), 'target-1',
                 'newest-tab lookup should be isolated by context')

    tabs.stop_session('session-2')
    assert_equal(second.stops, 1, 'stop_session should stop the registered object exactly once')
    assert_false('session-2' in tabs.session_ids, 'stop_session should remove the session mapping')
    assert_equal(tabs.get_session_ids('target-1'), {'session-1'},
                 'stop_session should remove only the selected target session')

    tabs.remove_frame('frame-2')
    assert_false('frame-2' in tabs.frame_ids, 'remove_frame should discard the selected frame')
    tabs.remove_target('target-1')
    assert_false('target-1' in tabs.target_ids, 'remove_target should discard the target mapping')
    assert_false('session-1' in tabs.session_ids, 'remove_target should discard attached session mappings')
    assert_false('frame-1' in tabs.frame_ids, 'remove_target should discard attached frame mappings')
    assert_false('target-1' in tabs.openers, 'remove_target should discard the opener relationship')

    tabs.remove_context('context-1')
    assert_equal(tabs.get_newest_tab('context-1'), None, 'remove_context should clear newest-tab state')
    assert_equal(tabs.get_proxy('context-1'), main_proxy,
                 'removed contexts should fall back to the main proxy')


def test_chromium_base_properties_widgets_cookies_and_storage():
    page = object.__new__(ChromiumBase)
    page._browser = SimpleNamespace()
    page._driver = object()
    page._target_id = 'target-7'
    page._timeouts = Timeout(base=1, page_load=2, script=3)
    page._load_mode = 'normal'
    page._upload_list = ['one.txt']
    page._session = object()

    assert_true(page.browser is page._browser, 'browser should expose the owning browser')
    assert_true(page.driver is page._driver, 'driver should expose the connected driver')
    assert_equal(page.tab_id, 'target-7', 'tab_id should expose the target id')
    assert_equal(page.timeout, 1, 'timeout should expose the base timeout')
    assert_true(page.timeouts is page._timeouts, 'timeouts should preserve the page timeout object')
    assert_equal(page.load_mode, 'normal', 'load_mode should expose the runtime load mode')
    assert_equal(page.upload_list, ['one.txt'], 'upload_list should expose pending upload paths')
    assert_true(page.session is page._session, 'session should reuse an existing requests session')

    page._driver = None
    _assert_raises(BrowserConnectError, lambda: page.driver)
    page._driver = object()

    class Widget:
        def __init__(self, owner):
            self.owner = owner
            self.loaded_calls = 0

        def doc_loaded(self):
            self.loaded_calls += 1

    page._wait = None
    page._set = None
    page._screencast = None
    page._actions = None
    page._listener = None
    page._states = None
    page._scroll = None
    page._rect = None
    page._console = None
    with _patched(
        chromium_base_module,
        BaseWaiter=Widget,
        ChromiumBaseSetter=Widget,
        Screencast=Widget,
        Actions=Widget,
        Listener=Widget,
        PageStates=Widget,
        PageScroller=Widget,
        TabRect=Widget,
        Console=Widget,
    ):
        wait = page.wait
        assert_true(page.wait is wait, 'wait should cache its wrapper')
        assert_true(page.set.owner is page, 'set should bind to the page')
        assert_true(page.screencast.owner is page, 'screencast should bind to the page')
        assert_true(page.actions.owner is page, 'actions should bind to the page')
        assert_true(page.listen.owner is page, 'listen should bind to the page')
        assert_true(page.states.owner is page, 'states should bind to the page')
        assert_true(page.scroll.owner is page, 'scroll should bind to the page')
        assert_true(page.rect.owner is page, 'rect should bind to the page')
        assert_true(page.console.owner is page, 'console should bind to the page')
        assert_equal(wait.loaded_calls, 2, 'actions and scroll should wait for document readiness')

    wait_calls = []
    page._wait = SimpleNamespace(doc_loaded=lambda: wait_calls.append(True))
    page._default_context = True
    page._context_id = 'context-7'
    cookie_payload = [
        {'name': 'sid', 'value': 'abc', 'domain': 'example.test', 'path': '/', 'httpOnly': True},
    ]
    browser_calls = []
    page_calls = []
    page._browser = SimpleNamespace(
        _run_cdp=lambda method, **kwargs: browser_calls.append((method, kwargs)) or {'cookies': cookie_payload},
        _tabs=SimpleNamespace(remove_session=lambda **kwargs: page_calls.append(('remove_session', kwargs))),
    )

    def page_cdp(method, **kwargs):
        page_calls.append((method, kwargs))
        if method == 'Network.getCookies':
            return {'cookies': cookie_payload}
        if method == 'Page.addScriptToEvaluateOnNewDocument':
            return {'identifier': 'script-1'}
        return None

    page._run_func = page_cdp
    assert_equal(page.cookies(), [{'name': 'sid', 'value': 'abc', 'domain': 'example.test'}],
                 'page cookies should default to the compact current-domain shape')
    assert_equal(page.cookies(all_domains=True, all_info=True), cookie_payload,
                 'all-domain all-info cookies should preserve protocol fields')
    assert_equal(browser_calls[-1], ('Storage.getCookies', {}),
                 'default-context all-domain cookies should omit browserContextId')
    page._default_context = False
    page.cookies(all_domains=True)
    assert_equal(browser_calls[-1], ('Storage.getCookies', {'browserContextId': 'context-7'}),
                 'non-default all-domain cookies should include browserContextId')
    assert_equal(len(wait_calls), 3, 'each cookie read should wait for document readiness')

    js_calls = []
    page._run_js_loaded = lambda script, **kwargs: js_calls.append((script, kwargs)) or f'value:{script}'
    assert_equal(page.session_storage(), 'value:sessionStorage',
                 'session_storage without an item should return the storage object')
    page.session_storage('token')
    page.local_storage()
    page.local_storage('theme')
    assert_equal(
        js_calls,
        [
            ('sessionStorage', {'as_expr': True}),
            ('sessionStorage.getItem("token")', {'as_expr': True}),
            ('localStorage', {'as_expr': True}),
            ('localStorage.getItem("theme")', {'as_expr': True}),
        ],
        'storage getters should generate exact expression-mode scripts',
    )

    page._init_jss = []
    assert_equal(page.add_init_js('window.ready = true;'), 'script-1',
                 'add_init_js should return and retain the protocol identifier')
    assert_equal(page._init_jss, ['script-1'], 'add_init_js should retain its identifier')
    page.remove_init_js('script-1')
    assert_equal(page._init_jss, [], 'remove_init_js should discard a selected identifier')
    assert_in(
        ('Page.removeScriptToEvaluateOnNewDocument', {'identifier': 'script-1'}),
        page_calls,
        'remove_init_js should remove the selected protocol script',
    )

    stopped = []
    page._session_id = 'session-7'
    page._stop_messenger = lambda: stopped.append(True)
    page.disconnect()
    assert_equal(stopped, [True], 'disconnect should stop the page messenger')
    assert_in(('remove_session', {'session_id': 'session-7'}), page_calls,
              'disconnect should remove the exact browser session')


def test_chromium_tab_delegation_close_and_disconnect():
    calls = []

    class Mode:
        title = 'Mode title'
        html = '<html>mode</html>'
        raw_data = b'raw-mode'
        json = {'ok': True}
        user_agent = 'mode-agent'

        def __call__(self, locator, **kwargs):
            calls.append(('call', locator, kwargs))
            return 'called'

        def get(self, **kwargs):
            calls.append(('get', kwargs))
            return 'get-result'

        def post(self, **kwargs):
            calls.append(('post', kwargs))
            return 'post-result'

        def ele(self, locator, **kwargs):
            calls.append(('ele', locator, kwargs))
            return 'element'

        def eles(self, locator, **kwargs):
            calls.append(('eles', locator, kwargs))
            return ['elements']

        def s_ele(self, locator, **kwargs):
            calls.append(('s_ele', locator, kwargs))
            return 'session-element'

        def s_eles(self, locator, **kwargs):
            calls.append(('s_eles', locator, kwargs))
            return ['session-elements']

        def cookies(self, *args):
            calls.append(('cookies', args))
            return ['cookie-result']

        def _find_elements(self, locator, **kwargs):
            calls.append(('find', locator, kwargs))
            return ['found']

    class CloseProbe:
        def __init__(self):
            self.closed = 0

        def close(self):
            self.closed += 1

    browser_calls = []
    browser = SimpleNamespace(
        id='browser-9',
        _run_cdp=lambda method, **kwargs: browser_calls.append((method, kwargs)),
        _close_tab=lambda tab: browser_calls.append(('close_tab', tab)),
        close_tabs=lambda tab_id, **kwargs: browser_calls.append(('close_tabs', tab_id, kwargs)),
    )
    tab = object.__new__(ChromiumTab)
    tab._mode_obj = Mode()
    tab._d_mode = True
    tab._browser = browser
    tab._target_id = 'tab-9'
    tab._timeouts = Timeout(base=2, page_load=8, script=3)
    tab._timeout = 4
    tab._response = CloseProbe()
    tab._response.url = 'https://session.test/'
    tab._session = CloseProbe()

    assert_equal(tab('t:div', index=2, timeout=3), 'called', '__call__ should delegate to the active mode')
    assert_equal(tab.title, 'Mode title', 'title should delegate to the active mode')
    assert_equal(tab.raw_data, '<html>mode</html>', 'driver-mode raw_data should expose HTML')
    assert_equal(tab.html, '<html>mode</html>', 'html should delegate to the active mode')
    assert_equal(tab.json, {'ok': True}, 'json should delegate to the active mode')
    assert_true(tab.response is tab._response, 'response should expose the last session response')
    assert_equal(tab.mode, 'd', 'driver mode should report d')
    assert_equal(tab.user_agent, 'mode-agent', 'user_agent should delegate to the active mode')
    assert_equal(tab.timeout, 2, 'driver-mode timeout should expose the base browser timeout')
    assert_in('browser_id=browser-9 tab_id=tab-9', repr(tab), 'repr should identify browser and tab ids')

    tab.activate()
    assert_equal(browser_calls[-1], ('Target.activateTarget', {'targetId': 'tab-9'}),
                 'activate should target the exact tab id')
    assert_equal(tab.get('https://example.test/', retry=2, interval=.1, timeout=5), 'get-result',
                 'driver-mode get should return the delegated result')
    _assert_raises(ValueError, tab.get, 'https://example.test/', headers={'X-Test': '1'})

    tab._d_mode = False
    assert_equal(tab.mode, 's', 'session mode should report s')
    assert_equal(tab.url, 'https://session.test/', 'session-mode url should expose the response url')
    assert_equal(tab.raw_data, b'raw-mode', 'session-mode raw_data should delegate to session content')
    assert_equal(tab.timeout, 4, 'session-mode timeout should expose the requests timeout')
    assert_equal(tab.get('https://example.test/s'), 'get-result',
                 'session-mode get should return the delegated result')
    assert_equal(calls[-1][1]['timeout'], 8, 'session-mode get should default to page-load timeout')

    cookie_copies = []
    tab._d_mode = True
    tab.cookies_to_session = lambda: cookie_copies.append(True)
    assert_equal(tab.post('https://example.test/post', payload='body'), 'post-result',
                 'post should preserve the active-mode return value')
    assert_equal(cookie_copies, [True], 'driver-mode post should copy cookies to the session first')
    assert_equal(calls[-1][1]['timeout'], 8, 'post should default to page-load timeout')
    assert_equal(tab.ele('t:div', index=2, timeout=1), 'element', 'ele should delegate arguments and result')
    assert_equal(tab.eles('t:div', timeout=1), ['elements'], 'eles should delegate arguments and result')
    assert_equal(tab.s_ele('t:div', index=3, timeout=1), 'session-element',
                 's_ele should delegate arguments and result')
    assert_equal(tab.s_eles('t:div', timeout=1), ['session-elements'],
                 's_eles should delegate arguments and result')
    assert_equal(tab.cookies(True, True), ['cookie-result'], 'cookies should delegate flags and result')
    assert_equal(tab._find_elements('t:div', timeout=2, index=4, relative=True), ['found'],
                 '_find_elements should preserve the delegated result')
    assert_equal(calls[-1], ('find', 't:div', {'timeout': 2, 'index': 4, 'relative': True}),
                 '_find_elements should pass locator, timeout, index, and relative mode')

    with _patched(chromium_tab_module, save_page=lambda *args: args):
        saved = tab.save('/tmp', 'page', as_pdf=True, quality=90)
    assert_equal(saved[1:], ('/tmp', 'page', True, {'quality': 90}),
                 'save should normalize options for save_page')

    session = tab._session
    response = tab._response
    tab.close(session=True)
    assert_in(('close_tab', tab), browser_calls, 'close should delegate the exact tab object')
    assert_equal((session.closed, response.closed), (1, 1),
                 'close(session=True) should close session and response resources')

    browser_calls.clear()
    tab.close(others=True, session=True)
    assert_equal(browser_calls, [('close_tabs', 'tab-9', {'others': True})],
                 'close(others=True) should keep this tab and avoid closing its session')
    assert_equal((session.closed, response.closed), (1, 1),
                 'others=True should preserve the caller session and response')

    tab._disconnect_flag = False
    with _preserved_dict(ChromiumTab._TABS):
        ChromiumTab._TABS['tab-9'] = tab
        tab._on_disconnect()
        assert_false('tab-9' in ChromiumTab._TABS,
                     'disconnect should remove a non-reconnecting tab from the singleton cache')


def test_chromium_frame_properties_delegation_and_bookkeeping():
    calls = []

    class FrameElement:
        _obj_id = 'object-1'
        _node_id = 2
        _backend_id = 3
        owner = 'element-owner'
        tag = 'iframe'
        link = 'https://frame.test/'
        attrs = {'id': 'frame-id'}
        xpath = '/html/body/iframe'
        css_selector = 'html > body > iframe'
        sr = 'shadow-root'

        def _run_js(self, script, *args, **kwargs):
            calls.append(('frame_js', script, args, kwargs))
            return 'frame-js-result'

        def property(self, name):
            calls.append(('property', name))
            return f'property:{name}'

        def attr(self, name):
            calls.append(('attr', name))
            return f'attr:{name}'

        def remove_attr(self, name):
            calls.append(('remove_attr', name))

        def style(self, **kwargs):
            calls.append(('style', kwargs))
            return 'style-result'

        def parent(self, *args, **kwargs):
            calls.append(('parent', args, kwargs))
            return 'parent-result'

        def prev(self, *args, **kwargs):
            calls.append(('prev', args, kwargs))
            return 'prev-result'

        def next(self, *args, **kwargs):
            calls.append(('next', args, kwargs))
            return 'next-result'

        def before(self, *args, **kwargs):
            calls.append(('before', args, kwargs))
            return 'before-result'

        def after(self, *args, **kwargs):
            calls.append(('after', args, kwargs))
            return 'after-result'

        def prevs(self, *args, **kwargs):
            calls.append(('prevs', args, kwargs))
            return ['prevs-result']

        def nexts(self, *args, **kwargs):
            calls.append(('nexts', args, kwargs))
            return ['nexts-result']

        def befores(self, *args, **kwargs):
            calls.append(('befores', args, kwargs))
            return ['befores-result']

        def afters(self, *args, **kwargs):
            calls.append(('afters', args, kwargs))
            return ['afters-result']

        def get_screenshot(self, **kwargs):
            calls.append(('screenshot', kwargs))
            return b'frame-image'

    class Document:
        def _run_js(self, script, *args, **kwargs):
            calls.append(('doc_js', script, args, kwargs))
            values = {
                'return this.location.href;': 'https://frame.test/page',
                'return this.documentElement.outerHTML;': '<html><body>frame</body></html>',
                'return this.activeElement;': 'active-element',
                'return this.readyState;': 'complete',
            }
            return values.get(script, 'doc-js-result')

    frame_element = FrameElement()
    frame = object.__new__(ChromiumFrame)
    frame._frame_id = 'frame-1'
    frame._frame_ele = frame_element
    frame._tab = SimpleNamespace(tab_id='tab-1')
    frame._download_path = '/tmp/frame-downloads'
    frame.doc_ele = Document()
    frame._target_page = SimpleNamespace(
        _run_cdp=lambda method, **kwargs: {
            'outerHTML': '<iframe id="frame-id"></iframe>'
        },
        timeouts=Timeout(base=2, page_load=4, script=6),
        retry_times=3,
        retry_interval=.2,
        download_path='/tmp/target-downloads',
        _auto_handle_alert=True,
        _load_mode='eager',
    )
    frame._is_diff_domain = False

    assert_in("<ChromiumFrame iframe id='frame-id'>", repr(frame),
              'repr should expose frame tag and attributes')
    other = object.__new__(ChromiumFrame)
    other._frame_id = 'frame-1'
    assert_true(frame == other, 'frame equality should use frame id')
    other._frame_id = 'frame-2'
    assert_false(frame == other, 'different frame ids should not compare equal')

    assert_equal(frame._obj_id, 'object-1', '_obj_id should delegate to the frame element')
    assert_equal(frame._node_id, 2, '_node_id should delegate to the frame element')
    assert_equal(frame.owner, 'element-owner', 'owner should delegate to the frame element')
    assert_true(frame.frame_ele is frame_element, 'frame_ele should expose the backing iframe element')
    assert_equal(frame.tag, 'iframe', 'tag should delegate to the frame element')
    assert_equal(frame.url, 'https://frame.test/page', 'url should delegate to the frame document')
    assert_equal(frame.inner_html, '<html><body>frame</body></html>',
                 'inner_html should expose the frame document HTML')
    assert_equal(frame.html, '<iframe id="frame-id"><html><body>frame</body></html></iframe>',
                 'html should combine the iframe opening tag and inner document')
    assert_equal(frame.link, 'https://frame.test/', 'link should delegate to the frame element')
    frame._ele = lambda locator, **kwargs: SimpleNamespace(text='Frame title') if locator == 't:title' else '3'
    assert_equal(frame.title, 'Frame title', 'title should expose the frame title element text')
    assert_equal(frame.attrs, {'id': 'frame-id'}, 'attrs should delegate to the frame element')
    assert_equal(frame.active_ele, 'active-element', 'active_ele should delegate to the frame document')
    assert_equal(frame.xpath, '/html/body/iframe', 'xpath should delegate to the frame element')
    assert_equal(frame.css_selector, 'html > body > iframe',
                 'css_selector should delegate to the frame element')
    assert_equal(frame.tab_id, 'tab-1', 'tab_id should delegate to the owning tab')
    assert_equal(frame.download_path, '/tmp/frame-downloads', 'download_path should expose frame runtime state')
    assert_equal(frame.sr, 'shadow-root', 'sr should delegate to the frame element shadow root')
    assert_equal(frame.shadow_root, 'shadow-root', 'shadow_root should retain the sr compatibility alias')
    assert_equal(frame.child_count, 3, 'child_count should normalize the XPath count to int')
    assert_equal(frame._js_ready_state, 'complete', 'same-domain ready state should use the frame document')

    frame.refresh()
    assert_equal(frame.property('name'), 'property:name', 'property should delegate to the frame element')
    assert_equal(frame.attr('src'), 'attr:src', 'attr should delegate to the frame element')
    frame.remove_attr('sandbox')
    assert_equal(frame.style('display', '::before'), 'style-result', 'style should delegate exact arguments')
    assert_equal(frame.run_js('return 1;', 'arg', as_expr=True, timeout=2), 'doc-js-result',
                 'normal JS should run in the frame document')
    assert_equal(frame.run_js('this.scrollIntoView();', timeout=2), 'frame-js-result',
                 'scrollIntoView JS should run on the iframe element')
    assert_equal(frame.parent(2, index=3, timeout=4), 'parent-result',
                 'parent should delegate traversal arguments')
    assert_equal(frame.prev('t:p', index=2, timeout=3, ele_only=False), 'prev-result',
                 'prev should delegate traversal arguments')
    assert_equal(frame.next('t:p', index=2, timeout=3, ele_only=False), 'next-result',
                 'next should delegate traversal arguments')
    assert_equal(frame.before('t:p', index=2, timeout=3, ele_only=False), 'before-result',
                 'before should delegate traversal arguments')
    assert_equal(frame.after('t:p', index=2, timeout=3, ele_only=False), 'after-result',
                 'after should delegate traversal arguments')
    assert_equal(frame.prevs('t:p', timeout=3, ele_only=False), ['prevs-result'],
                 'prevs should delegate traversal arguments')
    assert_equal(frame.nexts('t:p', timeout=3, ele_only=False), ['nexts-result'],
                 'nexts should delegate traversal arguments')
    assert_equal(frame.befores('t:p', timeout=3, ele_only=False), ['befores-result'],
                 'befores should delegate traversal arguments')
    assert_equal(frame.afters('t:p', timeout=3, ele_only=False), ['afters-result'],
                 'afters should delegate traversal arguments')
    assert_equal(frame.get_screenshot('/tmp', 'frame.png', as_bytes='png'), b'frame-image',
                 'get_screenshot should return the backing element result')

    frame._timeouts = None
    del frame._timeouts
    frame._d_set_runtime_settings()
    assert_equal(frame._timeouts.as_dict, {'base': 2, 'page_load': 4, 'script': 6},
                 'frame runtime settings should copy target timeouts')
    assert_equal((frame.retry_times, frame.retry_interval), (3, .2),
                 'frame runtime settings should copy retry settings')
    assert_equal(frame._download_path, '/tmp/target-downloads',
                 'frame runtime settings should copy the target download path')
    assert_equal(frame._auto_handle_alert, True, 'frame runtime settings should copy alert handling')
    assert_equal(frame._load_mode, 'eager', 'same-domain frames should copy the target load mode')
    frame._is_diff_domain = True
    frame._d_set_runtime_settings()
    assert_equal(frame._load_mode, 'normal', 'cross-domain frames should force normal load mode')

    class BrokenDocument:
        def _run_js(self, script, *args, **kwargs):
            raise JavaScriptError('context unavailable')

    frame.doc_ele = BrokenDocument()
    assert_equal(frame.url, None, 'frame url should return None when its JS context is unavailable')

    removed_frames = []
    reloads = []
    stops = []
    frame._browser = SimpleNamespace(_tabs=SimpleNamespace(remove_frame=removed_frames.append))
    frame._stop_messenger = lambda: stops.append(True)
    frame._reload = lambda: reloads.append(True)
    frame._frame_id = 'frame-1'
    with _preserved_dict(ChromiumFrame._Frames):
        ChromiumFrame._Frames['frame-1'] = frame
        frame._onFrameDetached(frameId='frame-1', reason='remove')
        assert_equal(removed_frames, ['frame-1'], 'removed frames should leave browser bookkeeping')
        assert_equal(stops, [True], 'removed frames should stop their messenger')
        assert_false('frame-1' in ChromiumFrame._Frames,
                     'removed frames should leave the singleton cache')
        frame._onFrameDetached(frameId='frame-1', reason='swap')
        assert_equal(reloads, [True], 'swapped frames should trigger reload bookkeeping')
