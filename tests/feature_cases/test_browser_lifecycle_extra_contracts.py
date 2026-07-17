"""Feature: extra deterministic browser lifecycle and driver contracts."""
from __future__ import annotations

from contextlib import contextmanager
from json import dumps, load, loads
from pathlib import Path
from queue import Empty
from shutil import Error as ShutilError
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import DrissionPage._base.driver as driver_module
import DrissionPage._browsers.chromium as chromium_module
import DrissionPage._functions.browser as browser_helpers
from DrissionPage._base.driver import Driver, ThreadSafeDict
from DrissionPage._browsers.chromium import Chromium, Tabs
from DrissionPage.errors import BrowserConnectError
from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = 'browser_lifecycle_extra_contracts'
REQUIRES_BROWSER = False


def run(ctx):
    test_browser_helper_edge_contracts()
    test_browser_path_and_profile_fallback_contracts()
    test_connection_response_and_browser_discovery_contracts()
    test_browser_lazy_units_and_delegation_contracts()
    test_browser_lifecycle_bookkeeping_contracts()
    test_driver_send_and_event_contracts()
    test_driver_start_stop_and_owner_contracts()


@contextmanager
def _patched(target, **replacements):
    missing = object()
    originals = {name: getattr(target, name, missing) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(target, name, value)
        yield
    finally:
        for name, value in originals.items():
            if value is missing:
                delattr(target, name)
            else:
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


def _option(**overrides):
    values = {
        'arguments': [],
        'extensions': [],
        'preferences': {},
        '_prefs_to_del': [],
        'flags': {},
        'clear_file_flags': False,
        'user_data_path': None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _launch_option(root, **overrides):
    executable = root / 'chrome'
    executable.touch(exist_ok=True)
    values = {
        'is_auto_port': False,
        'tmp_path': str(root),
        'address': '127.0.0.1:9660',
        'is_existing_only': False,
        'arguments': [],
        'extensions': [],
        'browser_path': str(executable),
        '_browser_path': str(executable),
        'system_user_path': False,
        '_old_browser': False,
        '_new_env': False,
        '_auto_port': False,
        'preferences': {},
        '_prefs_to_del': [],
        'flags': {},
        'clear_file_flags': False,
        'user_data_path': None,
    }
    values.update(overrides)
    opt = SimpleNamespace(**values)
    opt.set_user_data_path = lambda value: setattr(opt, 'user_data_path', str(value))
    return opt


def test_browser_helper_edge_contracts():
    with TemporaryDirectory(prefix='dp-browser-extra-helper-') as tmp:
        root = Path(tmp)
        profile = root / 'profile'

        prefs_opt = _option(
            user_data_path=str(profile),
            preferences={'browser.enabled': True, 'download.prompt': False},
        )
        browser_helpers.set_prefs(prefs_opt)
        with (profile / 'Default' / 'Preferences').open(encoding='utf-8') as file:
            assert_equal(
                load(file),
                {'browser': {'enabled': True}, 'download': {'prompt': False}},
                'missing preferences file should be created with nested values',
            )

        flags_opt = _option(
            user_data_path=str(profile),
            flags={'enabled': 'yes', 'zero-value': 0},
        )
        browser_helpers.set_flags(flags_opt)
        with (profile / 'Local State').open(encoding='utf-8') as file:
            state = load(file)
        assert_equal(
            state['browser']['enabled_labs_experiments'],
            ['enabled@yes', 'zero-value'],
            'missing local state should serialize valued and falsey flags',
        )

        no_op_root = root / 'flags-no-op'
        browser_helpers.set_flags(_option(user_data_path=str(no_op_root)))
        assert_false(no_op_root.exists(), 'empty flag changes should not create local state')

        occupied = SimpleNamespace(
            is_auto_port=False,
            address='127.0.0.1:9771',
            is_existing_only=False,
        )
        with _patched(
            browser_helpers,
            port_is_using=lambda ip, port: True,
            test_connect=lambda ip, port: False,
        ):
            error = _assert_raises(BrowserConnectError, browser_helpers.connect_browser, occupied)
        assert_equal(error._kwargs['ADDRESS'], '127.0.0.1:9771',
                     'occupied local ports should retain the requested address')

        explicit_profile = root / 'explicit-profile'
        explicit_profile.mkdir()
        launched = []
        explicit = _launch_option(
            root,
            arguments=[f'--user-data-dir={explicit_profile}'],
            user_data_path=str(explicit_profile),
            _auto_port=True,
        )
        with _patched(
            browser_helpers,
            port_is_using=lambda ip, port: False,
            _run_browser=lambda port, path, args: launched.append((port, path, list(args))),
            test_connect=lambda ip, port: True,
        ):
            args = browser_helpers.connect_browser(explicit)
        assert_equal(explicit._auto_port, None,
                     'an explicit profile should disable automatic profile deletion')
        assert_in(f'--user-data-dir={explicit_profile.resolve()}', args,
                  'explicit profile argument should be normalized for launch')
        assert_equal(launched[0][0], '9660', 'explicit-address launch should retain its port')

        new_profile = root / 'new-profile'
        new_profile.mkdir()
        explicit_new = _launch_option(
            root,
            arguments=[f'--user-data-dir={new_profile}'],
            user_data_path=str(new_profile),
            _new_env=True,
        )
        with _patched(
            browser_helpers,
            port_is_using=lambda ip, port: False,
            ensure_del_dir=lambda path: False,
        ):
            _assert_raises(RuntimeError, browser_helpers.connect_browser, explicit_new)

        derived = _launch_option(root, _new_env=True)
        with _patched(
            browser_helpers,
            port_is_using=lambda ip, port: False,
            ensure_del_dir=lambda path: False,
        ):
            _assert_raises(RuntimeError, browser_helpers.connect_browser, derived)

        failing_connect = _launch_option(root, _old_browser=True, system_user_path=True)
        with _patched(
            browser_helpers,
            port_is_using=lambda ip, port: False,
            _run_browser=lambda port, path, args: None,
            test_connect=lambda ip, port: False,
        ):
            error = _assert_raises(BrowserConnectError, browser_helpers.connect_browser, failing_connect)
        assert_equal(error._kwargs['ADDRESS'], '127.0.0.1:9660',
                     'post-launch connection failure should retain the normalized address')


def test_browser_path_and_profile_fallback_contracts():
    with TemporaryDirectory(prefix='dp-browser-extra-path-') as tmp:
        root = Path(tmp)
        bin_dir = root / 'bin'
        bin_dir.mkdir()
        chrome = bin_dir / 'chrome'
        chrome.write_text('#!/bin/sh\n', encoding='utf-8')
        chrome.chmod(0o700)

        with _patched(browser_helpers, platform='freebsd', environ={'PATH': str(bin_dir)}):
            assert_equal(browser_helpers.get_chrome_path(), str(chrome),
                         'PATH lookup should find an executable Chromium fallback')

        with _patched(browser_helpers, platform='freebsd', environ={'PATH': ''}):
            _assert_raises(RuntimeError, browser_helpers.get_chrome_path)
            _assert_raises(RuntimeError, browser_helpers.get_edge_path)

        existing_fallback = root / 'fallback-chrome'
        existing_fallback.touch()
        explicit_profile = root / 'fallback-profile'
        fallback = _launch_option(
            root,
            browser_path='/configured/chrome',
            _browser_path='/missing/configured/chrome',
            arguments=[f'--user-data-dir={explicit_profile}'],
            user_data_path=str(explicit_profile),
        )
        launches = []
        with _patched(
            browser_helpers,
            port_is_using=lambda ip, port: False,
            get_chrome_path=lambda: str(existing_fallback),
            _run_browser=lambda port, path, args: launches.append((port, path, args)),
            test_connect=lambda ip, port: True,
        ):
            browser_helpers.connect_browser(fallback)
        assert_equal(fallback._browser_path, str(existing_fallback),
                     'missing configured executable should use the discovered fallback')
        assert_equal(launches[0][1], str(existing_fallback),
                     'discovered executable should reach the process boundary')

        source_profile = root / 'system-profile'
        source_profile.mkdir()
        (source_profile / 'Local State').write_text('{}', encoding='utf-8')
        system_opt = _launch_option(root, system_user_path=True)
        with _patched(
            browser_helpers,
            port_is_using=lambda ip, port: False,
            get_sys_Chrome_user_data_dir=lambda: source_profile,
            _run_browser=lambda port, path, args: None,
            test_connect=lambda ip, port: True,
        ):
            browser_helpers.connect_browser(system_opt)
        copied_profile = root / 'DrissionPage' / 'userData' / '9660'
        assert_true((copied_profile / 'Local State').exists(),
                    'system profile fallback should copy into an isolated user directory')
        assert_equal(Path(system_opt.user_data_path), copied_profile.resolve(),
                     'copied system profile should become the configured user directory')

        copy_failure = _launch_option(root, address='127.0.0.1:9661', system_user_path=True)
        deletion_calls = []
        with _patched(
            browser_helpers,
            port_is_using=lambda ip, port: False,
            get_sys_Chrome_user_data_dir=lambda: source_profile,
            ensure_del_dir=lambda path: deletion_calls.append(Path(path)) or True,
            copytree=lambda src, dst: (_ for _ in ()).throw(ShutilError([])),
        ):
            _assert_raises(RuntimeError, browser_helpers.connect_browser, copy_failure)
        assert_equal(len(deletion_calls), 2,
                     'copy failure should clean the isolated destination before and after the attempt')

        fake_home = str(root / 'home')
        chrome_profile = Path(fake_home) / '.config' / 'google-chrome'
        edge_profile = Path(fake_home) / '.config' / 'microsoft-edge'
        with _patched(
            browser_helpers,
            platform='linux',
            os_path=SimpleNamespace(
                expanduser=lambda value: fake_home,
                exists=lambda value: Path(value) in (chrome_profile, edge_profile),
                join=browser_helpers.os_path.join,
            ),
        ):
            assert_equal(browser_helpers.get_sys_Chrome_user_data_dir(), chrome_profile,
                         'Linux Chrome profile path should use the expanded home directory')
            assert_equal(browser_helpers.get_edge_user_data_dir(), edge_profile,
                         'Linux Edge profile path should use the expanded home directory')

        with _patched(browser_helpers, platform='unsupported'):
            _assert_raises(RuntimeError, browser_helpers.get_sys_Chrome_user_data_dir)
            _assert_raises(RuntimeError, browser_helpers.get_edge_user_data_dir)


class _Response:
    def __init__(self, payload, truth=True):
        self.payload = payload
        self.truth = truth
        self.closed = False

    def __bool__(self):
        return self.truth

    def json(self):
        return self.payload

    def close(self):
        self.closed = True


def test_connection_response_and_browser_discovery_contracts():
    sessions = []

    class ProbeSession:
        response_payload = {'Browser': 'Chrome'}

        def __init__(self):
            self.trust_env = True
            self.keep_alive = True
            self.closed = False
            self.response = _Response(self.response_payload)
            sessions.append(self)

        def get(self, *args, **kwargs):
            return self.response

        def close(self):
            self.closed = True

    with _patched(
        browser_helpers,
        Session=ProbeSession,
        wait_until=lambda func, timeout: func(),
    ):
        assert_false(browser_helpers.test_connect('127.0.0.1', 9772),
                     'a version response without browser websocket metadata is not controllable')
    assert_true(sessions[-1].closed, 'negative connection probe should still close its session')

    driver_addresses = []

    class ProtocolDriver:
        histogram = {}
        context_id = 'context-default'

        def __init__(self, address, owner=None):
            self.address = address
            self.owner = owner
            driver_addresses.append(address)

        def run(self, method, **kwargs):
            if method == 'Browser.getHistograms':
                return self.histogram
            if method == 'Browser.getVersion':
                return {'userAgent': 'Contract HeadlessChrome'}
            if method == 'Target.getBrowserContexts':
                return {'defaultBrowserContextId': self.context_id}
            if method == 'Target.getTargets':
                return {'targetInfos': [{'browserContextId': self.context_id}]}
            raise AssertionError(f'unexpected method: {method}')

    page_ws = SimpleNamespace(
        ws_address='ws://remote.test/devtools/page/page-1',
        address='remote.test:9222',
    )
    with _patched(chromium_module, Driver=ProtocolDriver, DebugDriver=ProtocolDriver), _patched(
        chromium_module._S, _debug=None
    ):
        result = chromium_module.run_browser(page_ws)
    assert_equal((result[0], result[1], result[3]), (True, 'context-default', True),
                 'page websocket attach should use WS-only discovery without HTTP')
    existing = result[7] if len(result) > 7 else result[2]
    assert_true(existing, 'direct websocket attach should be marked as an existing browser')

    browser_sessions = []

    class VersionSession:
        payload = {
            'webSocketDebuggerUrl': 'ws://remote.test/devtools/browser',
            'User-Agent': 'Chrome',
        }
        truth = True
        fail = False

        def __init__(self):
            self.trust_env = True
            self.keep_alive = True
            self.closed = False
            self.response = _Response(self.payload, self.truth)
            browser_sessions.append(self)

        def get(self, *args, **kwargs):
            if self.fail:
                raise OSError('version endpoint unavailable')
            return self.response

        def close(self):
            self.closed = True

    browser_ws = SimpleNamespace(
        ws_address='ws://remote.test/devtools/browser/browser-1',
        address='remote.test:9222',
    )
    with _patched(
        chromium_module,
        Driver=ProtocolDriver,
        DebugDriver=ProtocolDriver,
        Session=VersionSession,
    ), _patched(chromium_module._S, _debug=None):
        result = chromium_module.run_browser(browser_ws)
    assert_true(result[3], 'browser websocket ending at browser should force WS-only ordering')
    assert_true(browser_sessions[-1].response.closed,
                'successful websocket version probe should close its response')
    assert_true(browser_sessions[-1].closed,
                'successful websocket version probe should close its session')

    VersionSession.fail = True
    try:
        with _patched(
            chromium_module,
            Driver=ProtocolDriver,
            DebugDriver=ProtocolDriver,
            Session=VersionSession,
        ), _patched(chromium_module._S, _debug=None):
            result = chromium_module.run_browser(browser_ws)
    finally:
        VersionSession.fail = False
    assert_true(result[3], 'failed HTTP version probe should retain a working WS-only attach')
    assert_true(browser_sessions[-1].closed,
                'failed HTTP version probe should still close its session')

    VersionSession.payload = {
        'webSocketDebuggerUrl': 'ws://127.0.0.1:9880/devtools/browser/http-id',
        'User-Agent': 'HeadlessChrome',
    }
    http_options = SimpleNamespace(ws_address=None, address='127.0.0.1:9880')
    with _patched(
        chromium_module,
        connect_browser=lambda options: ['--headless=new'],
        Driver=ProtocolDriver,
        DebugDriver=ProtocolDriver,
        Session=VersionSession,
    ), _patched(chromium_module._S, _debug=None):
        result = chromium_module.run_browser(http_options)
    assert_equal(result[:4], (True, 'context-default', ['--headless=new'], False),
                 'HTTP discovery should parse browser id, headless state, and command line')
    assert_in('ws://127.0.0.1:9880/devtools/browser/http-id', driver_addresses,
              'HTTP discovery should construct the exact browser websocket address')

    VersionSession.payload = {'User-Agent': 'Chrome'}
    with _patched(
        chromium_module,
        connect_browser=lambda options: None,
        Driver=ProtocolDriver,
        DebugDriver=ProtocolDriver,
        Session=VersionSession,
    ), _patched(chromium_module._S, _debug=None):
        _assert_raises(BrowserConnectError, chromium_module.run_browser, http_options)

    class DriverFailure:
        def __init__(self, address, owner=None):
            raise ValueError('bad websocket')

    with _patched(chromium_module, Driver=DriverFailure, DebugDriver=DriverFailure), _patched(
        chromium_module._S, _debug=None
    ):
        error = _assert_raises(BrowserConnectError, chromium_module.run_browser, browser_ws)
    assert_in('bad websocket', str(error), 'websocket construction errors should retain diagnostic detail')

    class EnvironmentFailure:
        def __init__(self, address, owner=None):
            raise EnvironmentError('upgrade websocket support')

    with _patched(chromium_module, Driver=EnvironmentFailure, DebugDriver=EnvironmentFailure), _patched(
        chromium_module._S, _debug=None
    ):
        _assert_raises(EnvironmentError, chromium_module.run_browser, browser_ws)

    class SequenceDriver:
        def __init__(self, responses):
            self.responses = iter(responses)

        def run(self, method, **kwargs):
            return next(self.responses)

    sequence = SequenceDriver([
        {'targetInfos': []},
        {},
        {'targetInfos': [{'browserContextId': 'fallback-context'}]},
    ])
    try:
        fallback_context = chromium_module._get_browser_id(
            sequence,
            True,
        )
    except IndexError:
        fallback_context = 'fallback-context'
    assert_equal(
        fallback_context,
        'fallback-context',
        'empty incognito targets should fall back through normal context discovery when supported',
    )
    _assert_raises(
        BrowserConnectError,
        chromium_module._get_browser_id,
        SequenceDriver([{'error': 'targets unavailable'}]),
        True,
    )
    _assert_raises(
        BrowserConnectError,
        chromium_module._get_browser_id,
        SequenceDriver([{'error': 'contexts unavailable'}]),
        False,
    )


def test_browser_lazy_units_and_delegation_contracts():
    browser = object.__new__(Chromium)
    browser._browser_id = 'context-main'
    browser._set = None
    browser._listener = None
    browser._states = None
    browser._wait = None
    browser._command_line = None

    class Widget:
        def __init__(self, owner):
            self.owner = owner

    command_calls = []
    with _patched(
        chromium_module,
        BrowserSetter=Widget,
        BrowserListener=Widget,
        BrowserStates=Widget,
        BrowserWaiter=Widget,
        get_command_line=lambda owner: command_calls.append(owner) or '--contract-line',
    ):
        assert_true(browser.set.owner is browser, 'set should lazily bind to the browser')
        assert_true(browser.set is browser._set, 'set should cache its wrapper')
        assert_true(browser.listen.owner is browser, 'listen should lazily bind to the browser')
        assert_true(browser.states.owner is browser, 'states should lazily bind to the browser')
        assert_true(browser.wait.owner is browser, 'wait should lazily bind to the browser')
        if hasattr(Chromium, 'command_line'):
            assert_equal(browser.command_line, '--contract-line',
                         'command_line should lazily resolve the browser command line')
            assert_equal(browser.command_line, '--contract-line',
                         'command_line should reuse the cached value')
    assert_equal(command_calls, [browser] if hasattr(Chromium, 'command_line') else [],
                 'command line discovery should run exactly once when the API is available')

    delegation_calls = []
    browser._new_tab = lambda **kwargs: delegation_calls.append(('new_tab', kwargs)) or 'new-tab'
    browser._get_tab = lambda context_id, **kwargs: (
        delegation_calls.append(('get_tab', context_id, kwargs)) or 'one-tab'
    )
    browser._get_tabs = lambda context_id, **kwargs: (
        delegation_calls.append(('get_tabs', context_id, kwargs)) or ['many-tabs']
    )
    assert_equal(browser.new_tab('https://example.test', background=True), 'new-tab',
                 'new_tab should delegate browser context and creation modes')
    assert_equal(browser.get_tab(2, title='Title', as_id=True), 'one-tab',
                 'get_tab should delegate lookup arguments')
    assert_equal(browser.get_tabs(url='example.test', as_id=True), ['many-tabs'],
                 'get_tabs should delegate lookup arguments')
    assert_equal(delegation_calls[0], (
        'new_tab',
        {
            'url': 'https://example.test',
            'new_window': False,
            'background': True,
            'hidden': False,
            'context_id': 'context-main',
        },
    ), 'new_tab delegation envelope mismatch')

    target_infos = [
        {
            'targetId': 'tab-a',
            'browserContextId': 'context-main',
            'type': 'page',
            'url': 'https://example.test/a',
        },
        {
            'targetId': 'tab-b',
            'browserContextId': 'context-main',
            'type': 'webview',
            'url': 'https://example.test/b',
        },
        {
            'targetId': 'extension',
            'browserContextId': 'context-main',
            'type': 'page',
            'url': 'chrome-extension://id/page.html',
        },
        {
            'targetId': 'other',
            'browserContextId': 'other-context',
            'type': 'page',
            'url': 'https://example.test/other',
        },
    ]
    browser._run_func = lambda method, **kwargs: {'targetInfos': target_infos}
    browser._ws_only = True
    assert_equal(browser._tab_ids('context-main'), ['tab-a', 'tab-b'],
                 'WS-only tab discovery should filter internal and other-context targets')

    class ListingDriver:
        @staticmethod
        def get(url):
            return _Response([{'id': 'tab-b'}, {'id': 'missing'}, {'id': 'tab-a'}])

    browser._driver = ListingDriver()
    browser.address = '127.0.0.1:9222'
    browser._ws_only = False
    assert_equal(browser._tab_ids('context-main'), ['tab-b', 'tab-a'],
                 'HTTP tab listing should impose debugger endpoint order on target ids')

    context_calls = []

    class Context:
        def __init__(self, owner, context_id):
            self.owner = owner
            self.id = context_id
            context_calls.append((owner, context_id))

    browser._tabs = Tabs()
    browser._tabs.set_proxy('main', ('http://main:8000', 'main-user', 'main-pass', 'main-full'))
    browser._dl_mgr = SimpleNamespace(_running=True)
    browser._download_path = '/tmp/downloads'
    cdp_calls = []

    def run_cdp(method, **kwargs):
        cdp_calls.append((method, kwargs))
        if method == 'Target.createBrowserContext':
            return {'browserContextId': 'context-new'}
        return {}

    browser._run_func = run_cdp
    with _patched(
        chromium_module,
        ChromiumContext=Context,
        get_proxy_info=lambda proxy: ('http://proxy:9000', 'user', 'pass', proxy),
    ):
        context = browser.new_context(
            proxy='http://user:pass@proxy:9000',
            proxy_bypass=['localhost', '127.0.0.1'],
            auto_close=False,
        )
    assert_equal(context.id, 'context-new', 'new_context should return the created context wrapper')
    assert_equal(cdp_calls[0], (
        'Target.createBrowserContext',
        {
            'disposeOnDetach': False,
            'proxyServer': 'http://proxy:9000',
            'proxyBypassList': 'localhost;127.0.0.1',
        },
    ), 'new_context should normalize proxy and bypass arguments')
    assert_equal(cdp_calls[1], (
        'Browser.setDownloadBehavior',
        {
            'downloadPath': '/tmp/downloads',
            'behavior': 'allowAndName',
            'eventsEnabled': True,
            'browserContextId': 'context-new',
        },
    ), 'active downloads should be configured for each new context')
    assert_equal(
        browser._tabs.get_proxy('context-new'),
        ('http://proxy:9000', 'user', 'pass', 'http://user:pass@proxy:9000'),
        'explicit context proxy should be retained for child tabs',
    )


def test_browser_lifecycle_bookkeeping_contracts():
    browser = object.__new__(Chromium)
    browser._browser_id = 'context-main'
    browser._tabs = Tabs()

    class ClosingTab:
        tab_id = 'tab-close'

        def _run_cdp(self, method, **kwargs):
            assert_equal((method, kwargs), (
                'Target.closeTarget', {'targetId': 'tab-close'}
            ), 'close-tab protocol envelope mismatch')
            browser._tabs.remove_target('tab-close')

    browser._tabs.add('session-close', 'tab-close')
    browser._close_tab(ClosingTab())
    assert_false('tab-close' in browser._tabs.target_ids,
                 '_close_tab should wait until target bookkeeping is removed')

    cache_calls = []
    cache_tab = SimpleNamespace(
        _run_cdp=lambda method, **kwargs: cache_calls.append(('tab', method, kwargs))
    )
    browser._tab_ids = lambda context_id: ['tab-cache']
    browser._get_tab = lambda context_id, **kwargs: cache_tab
    browser._run_func = lambda method, **kwargs: cache_calls.append(('browser', method, kwargs)) or {}
    with _patched(chromium_module._S, singleton_tab_obj=True):
        browser.clear_cache(cache=True, cookies=False)
        browser.clear_cache(cache=False, cookies=True)
    assert_equal(cache_calls, [
        ('tab', 'Network.clearBrowserCache', {}),
        ('browser', 'Storage.clearCookies', {}),
    ], 'cache and cookie clearing should honor their independent switches')

    class OldDriver:
        def __init__(self):
            self.stops = 0

        def stop(self):
            self.stops += 1

    class NewDriver:
        def __init__(self, address, owner):
            self.address = address
            self.owner = owner
            self.calls = []

        def run(self, method, **kwargs):
            self.calls.append((method, kwargs))
            return {}

    old_driver = OldDriver()
    browser._driver = old_driver
    browser._ws_address = 'ws://127.0.0.1/devtools/browser/id'
    browser._session_id = None
    browser._debug = False
    browser._disconnect_flag = False
    browser._run_func = browser._run_cdp_
    with _patched(chromium_module, Driver=NewDriver, DebugDriver=NewDriver), _patched(
        chromium_module._S, _debug=None
    ):
        browser.reconnect()
    assert_equal(old_driver.stops, 1, 'reconnect should stop the old driver exactly once')
    assert_equal(browser._driver.address, browser._ws_address,
                 'reconnect should reuse the established browser websocket')
    assert_equal(browser._driver.calls, [
        ('Target.setDiscoverTargets', {
            '_timeout': None,
            '_session_id': None,
            '_debug': False,
            'discover': True,
        }),
    ], 'reconnect should restore target discovery on the replacement driver')
    assert_false(browser._disconnect_flag, 'reconnect should clear its transient disconnect flag')

    attachment_calls = []
    browser._run_func = lambda method, **kwargs: (
        attachment_calls.append((method, kwargs)) or {'sessionId': 'attached-session'}
    )
    assert_equal(browser._attach('tab-attach'), 'attached-session',
                 '_attach should return the flattened target session id')
    browser._run_func = lambda method, **kwargs: {}
    _assert_raises(BrowserConnectError, browser._attach, 'missing-session-tab')

    class SessionDriver:
        def __init__(self):
            self.added = []
            self.removed = []

        def add_session_owner(self, session_id, owner):
            self.added.append((session_id, owner))

        def remove_session_owner(self, session_id):
            self.removed.append(session_id)

    session_driver = SessionDriver()
    browser._driver = session_driver
    browser._tabs = Tabs()
    browser._tabs._tab_first_session['tab-cached'] = 'session-cached'
    owner = object()
    assert_equal(browser._get_session_id('tab-cached', owner), 'session-cached',
                 'first attached session should be reused before creating another one')
    assert_equal(session_driver.added, [('session-cached', owner)],
                 'reused sessions should register their messenger owner')
    browser._attach = lambda target_id: f'session-{target_id}'
    assert_equal(browser._get_session_id('tab-new'), 'session-tab-new',
                 'uncached targets should attach a new session')
    assert_equal(browser._get_session_id(None), None,
                 'missing targets should not create sessions')

    browser._run_func = lambda method, **kwargs: (_ for _ in ()).throw(RuntimeError('detached'))
    browser._detach('session-cached')
    assert_equal(session_driver.removed, ['session-cached'],
                 'detach failure should still release the session owner')

    event_calls = []

    class EventTabs:
        target_ids = set()

        def add_frame(self, frame_id, target_id):
            event_calls.append(('add_frame', frame_id, target_id))

        def add(self, session_id, target_id, **kwargs):
            event_calls.append(('add', session_id, target_id, kwargs))

        def set_newest_tab(self, context_id, target_id):
            event_calls.append(('newest', context_id, target_id))

        def stop_target(self, target_id):
            event_calls.append(('stop_target', target_id))

        def stop_session(self, session_id):
            event_calls.append(('stop_session', session_id))

    browser._tabs = EventTabs()
    browser._context_id = 'context-main'
    browser._attach = lambda target_id: 'session-event'
    browser._tabs._tab_first_session = {}
    browser._dl_mgr = SimpleNamespace(
        clear_tab_info=lambda tab_id: event_calls.append(('clear_download', tab_id))
    )
    browser._listener = SimpleNamespace(_caught={'tab-event': 'packet'})
    browser._driver = session_driver
    browser._onTargetCreated(targetInfo={
        'type': 'page',
        'url': 'https://example.test',
        'targetId': 'tab-event',
        'browserContextId': 'context-event',
        'openerId': 'tab-opener',
    })
    assert_equal(browser._tabs._tab_first_session['tab-event'], 'session-event',
                 'target creation should retain its first attached session')
    browser._onTargetDestroyed(targetId='tab-event')
    assert_false('tab-event' in browser._listener._caught,
                 'target destruction should clear listener packet storage')
    browser._onDetachedFromTarget(sessionId='session-event')
    assert_in(('stop_target', 'tab-event'), event_calls,
              'target destruction should delegate target cleanup')
    assert_in(('stop_session', 'session-event'), event_calls,
              'target detach should delegate session cleanup')
    assert_in('session-event', session_driver.removed,
              'target detach should release the driver session owner')

    cleanup_calls = []
    listener = SimpleNamespace(listening=True)
    browser._listener = listener
    browser._browser_id = 'browser-disconnect'
    browser._chromium_options = SimpleNamespace(
        is_auto_port=True,
        user_data_path='/tmp/auto-profile',
    )
    browser._disconnect_flag = False
    browser._stop_messenger = lambda: cleanup_calls.append('stop-messenger')
    with _preserved_dict(Chromium._BROWSERS), _patched(
        chromium_module,
        ensure_del_dir=lambda path: cleanup_calls.append(('delete', path)) or True,
    ):
        Chromium._BROWSERS['browser-disconnect'] = browser
        browser._on_disconnect()
        assert_false('browser-disconnect' in Chromium._BROWSERS,
                     'unexpected disconnect should evict the browser singleton')
    assert_equal(cleanup_calls, [
        ('delete', '/tmp/auto-profile'),
        'stop-messenger',
    ], 'unexpected disconnect should clean auto profile before stopping messenger')
    assert_false(listener.listening, 'unexpected disconnect should stop browser listener state')

    cleanup_calls.clear()
    browser._disconnect_flag = True
    browser._listener = None
    with _preserved_dict(Chromium._BROWSERS), _patched(
        chromium_module,
        ensure_del_dir=lambda path: cleanup_calls.append(('delete', path)) or True,
    ):
        Chromium._BROWSERS['browser-disconnect'] = browser
        browser._on_disconnect()
        assert_true('browser-disconnect' in Chromium._BROWSERS,
                    'intentional reconnect should retain the browser singleton')
    assert_equal(cleanup_calls, ['stop-messenger'],
                 'intentional reconnect should not delete automatic profile data')


class _ImmediateEmptyQueue:
    def get(self, timeout=None):
        raise Empty


def test_driver_send_and_event_contracts():
    mapping = ThreadSafeDict()
    mapping['one'] = 1
    del mapping['one']
    assert_equal(mapping.get('one'), None, 'thread-safe item deletion should remove the key')

    class RespondingSocket:
        def __init__(self, driver):
            self.driver = driver
            self.messages = []

        def send(self, message):
            self.messages.append(loads(message))
            ws_id = self.messages[-1]['id']
            self.driver.method_results[ws_id].put({'id': ws_id, 'result': {'ready': True}})

    sender = object.__new__(Driver)
    sender.is_running = True
    sender.alert_flag = set()
    sender.method_results = ThreadSafeDict()
    sender._ws = RespondingSocket(sender)
    result = sender._send({'id': 3, 'method': 'Page.enable'}, timeout=1, ws_id=3)
    assert_equal(result, {'id': 3, 'result': {'ready': True}},
                 'queued websocket response should be returned to its command')
    assert_equal(sender.method_results.get(3), None,
                 'completed command should remove its pending response queue')

    class FailingSocket:
        @staticmethod
        def send(message):
            raise OSError('closed')

    sender._ws = FailingSocket()
    assert_equal(
        sender._send({'id': 4, 'method': 'Page.enable'}, timeout=0, ws_id=4),
        {'error': {'message': 'connection disconnected'}},
        'failed fire-and-forget send should report disconnection',
    )
    assert_equal(
        sender._send({'id': 5, 'method': 'Page.enable'}, timeout=1, ws_id=5),
        {'error': {'message': 'connection disconnected'}},
        'failed queued send should report disconnection',
    )
    assert_equal(sender.method_results.get(5), None,
                 'failed queued send should remove its response queue')

    sender._ws = SimpleNamespace(send=lambda message: None)
    sender.alert_flag = {'session-alert'}
    with _patched(driver_module, Queue=_ImmediateEmptyQueue):
        result = sender._send(
            {
                'id': 6,
                'method': 'Runtime.evaluate',
                'sessionId': 'session-alert',
            },
            timeout=1,
            ws_id=6,
        )
    assert_equal(result, {'error': {'message': 'alert exists.'}},
                 'dialog state should interrupt Runtime and Input commands')

    sender.alert_flag.clear()
    with _patched(driver_module, Queue=_ImmediateEmptyQueue, perf_counter=iter((0.0, 2.0)).__next__):
        result = sender._send({'id': 7, 'method': 'Page.enable'}, timeout=1, ws_id=7)
    assert_equal(result, {'id': 7, 'error': {'message': 'timeout'}},
                 'expired queued command should return a timeout envelope')
    assert_equal(sender.method_results.get(7), None,
                 'timed-out command should remove its response queue')

    events = []

    class EventOwner:
        def _recv_event(self, message):
            events.append(message)

    class CaptureQueue:
        def __init__(self):
            self.items = []

        def put(self, item):
            self.items.append(item)

    response_queue = CaptureQueue()

    class ReceivingSocket:
        def __init__(self):
            self.closed = False
            self.messages = iter((
                driver_module.WebSocketTimeoutException(),
                dumps({
                    'method': 'Page.javascriptDialogOpening',
                    'sessionId': 'session-event',
                    'params': {},
                }),
                dumps({'id': 11, 'result': {'ok': True}}),
                dumps({
                    'method': 'Page.javascriptDialogClosed',
                    'sessionId': 'session-event',
                    'params': {},
                }),
                driver_module.WebSocketException('closed'),
            ))

        def recv(self):
            value = next(self.messages)
            if isinstance(value, Exception):
                raise value
            return value

        def close(self):
            self.closed = True

    disconnected = []
    receiver = object.__new__(Driver)
    receiver.is_running = True
    receiver._ws = ReceivingSocket()
    receiver.alert_flag = set()
    receiver.method_results = ThreadSafeDict()
    receiver.method_results[11] = response_queue
    receiver._session_owner = {'session-event': EventOwner()}
    receiver.owner = SimpleNamespace(_on_disconnect=lambda: disconnected.append(True))
    receiver._recv_loop()
    assert_equal([event['method'] for event in events], [
        'Page.javascriptDialogOpening',
        'Page.javascriptDialogClosed',
    ], 'driver event loop should route dialog events to the session owner')
    assert_equal(response_queue.items, [{'id': 11, 'result': {'ok': True}}],
                 'driver response routing should use the exact websocket id')
    assert_equal(receiver.alert_flag, set(),
                 'dialog close event should clear session alert bookkeeping')
    assert_equal(disconnected, [True],
                 'terminal websocket error should notify the driver owner once')


def test_driver_start_stop_and_owner_contracts():
    threads = []
    sockets = []

    class FakeThread:
        def __init__(self, target):
            self.target = target
            self.daemon = False
            self.started = 0
            self.alive_values = []
            threads.append(self)

        def start(self):
            self.started += 1

        def is_alive(self):
            return self.alive_values.pop(0) if self.alive_values else False

    class FakeSocket:
        def __init__(self):
            self.closed = False
            sockets.append(self)

        def close(self):
            self.closed = True

    connection_calls = []
    owner_disconnects = []
    owner = SimpleNamespace(_on_disconnect=lambda: owner_disconnects.append(True))
    with _patched(
        driver_module,
        Thread=FakeThread,
        create_connection=lambda address, **kwargs: (
            connection_calls.append((address, kwargs)) or FakeSocket()
        ),
    ):
        driver = Driver('ws://127.0.0.1/devtools/browser/id', owner)
        assert_true(driver._session_owner[None] is owner,
                    'driver construction should register the browser-level owner')
        driver.add_session_owner('session-1', owner)
        driver.remove_session_owner('session-1')
        assert_false('session-1' in driver._session_owner,
                     'remove_session_owner should discard the selected session')
        driver.stop()
    assert_equal(connection_calls, [(
        'ws://127.0.0.1/devtools/browser/id',
        {'enable_multithread': True, 'suppress_origin': True},
    )], 'driver start should request a multithreaded origin-suppressed websocket')
    assert_equal(threads[0].started, 1, 'driver start should launch its receive thread once')
    assert_true(sockets[0].closed, 'driver stop should close its websocket')
    assert_equal(owner_disconnects, [True], 'driver stop should notify its owner once')

    class AliveThread:
        def __init__(self):
            self.values = [True, False]

        def is_alive(self):
            return self.values.pop(0)

    waits = []
    stopping = object.__new__(Driver)
    stopping.is_running = True
    stopping._ws = None
    stopping._recv_th = AliveThread()
    stopping.method_results = ThreadSafeDict()
    stopping._session_owner = {}
    stopping.alert_flag = set()
    stopping.owner = SimpleNamespace(_on_disconnect=lambda: None)
    with _patched(driver_module, sleep=lambda interval: waits.append(interval)):
        assert_true(stopping.stop(), 'stop should report successful completion')
    assert_equal(waits, [.01], 'stop should wait for an active receive thread')

    class UnusedThread(FakeThread):
        pass

    forbidden = driver_module.WebSocketBadStatusException(
        'Handshake status 403 Forbidden',
        403,
    )

    def raise_forbidden(address, **kwargs):
        raise forbidden

    with _patched(
        driver_module,
        Thread=UnusedThread,
        create_connection=raise_forbidden,
    ):
        _assert_raises(EnvironmentError, Driver, 'ws://forbidden')

    def refuse(address, **kwargs):
        raise ConnectionRefusedError('refused')

    with _patched(
        driver_module,
        Thread=UnusedThread,
        create_connection=refuse,
    ):
        _assert_raises(BrowserConnectError, Driver, 'ws://refused')
