"""Feature: deterministic browser and shared-tool helper contracts."""
from __future__ import annotations

import random
import socket
from contextlib import contextmanager
from json import dump, load
from pathlib import Path
from queue import Queue
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import DrissionPage._base.driver as driver_module
import DrissionPage._functions.browser as browser_helpers
import DrissionPage._functions.tools as tools
from DrissionPage._base.driver import Driver, ThreadSafeDict
from DrissionPage.errors import (
    AlertExistsError,
    BrowserConnectError,
    CDPError,
    ContextLostError,
    CookieFormatError,
    ElementLostError,
    IncorrectURLError,
    JavaScriptError,
    NoRectError,
    PageDisconnectedError,
    StorageError,
    WaitTimeoutError,
)
from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = 'browser_helper_contracts'
REQUIRES_BROWSER = False


def run(ctx):
    test_launch_argument_contracts()
    test_preference_contracts()
    test_flag_contracts()
    test_connection_contracts()
    test_process_invocation_contracts()
    test_port_and_folder_contracts()
    test_wait_and_error_contracts()
    test_driver_contracts()


@contextmanager
def _replaced(target, **replacements):
    originals = {name: getattr(target, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(target, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(target, name, value)


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


def test_launch_argument_contracts():
    with TemporaryDirectory(prefix='dp-browser-args-') as tmp:
        root = Path(tmp)
        user_data = root / 'relative-user-data'
        extension = root / 'extension'
        extension.mkdir()
        extension_file = root / 'extension.zip'
        extension_file.write_bytes(b'zip')

        opt = _option(
            arguments=[
                '--headless=new',
                '--headless=new',
                '--remote-debugging-port=1111',
                '--disable-extensions-except=/ignored',
                '--load-extension=/ignored',
                f'--user-data-dir={user_data}',
                '--user-agent=contract-agent',
            ],
            extensions=[extension],
            _ua_set=False,
        )
        args, resolved_user_data = browser_helpers.get_launch_args(opt)

        assert_equal(resolved_user_data, user_data.resolve(), 'user-data path should be absolute')
        assert_true(opt._ua_set, 'explicit user-agent should mark the option as configured')
        assert_equal(args.count('--headless=new'), 1, 'duplicate launch arguments should collapse')
        assert_in(f'--user-data-dir={user_data.resolve()}', args, 'normalized user-data argument missing')
        assert_in(f'--disable-extensions-except={extension.resolve()}', args,
                  'extension allow-list argument mismatch')
        assert_in(f'--load-extension={extension.resolve()}', args, 'extension load argument mismatch')
        assert_false(any(arg.startswith('--remote-debugging-port=') for arg in args),
                     'caller-supplied debugging port should be filtered')
        assert_false(any('/ignored' in arg for arg in args), 'caller-supplied extension switches should be filtered')

        file_error = _assert_raises(
            ValueError,
            browser_helpers.get_launch_args,
            _option(arguments=[], extensions=[extension_file], _ua_set=False),
        )
        assert_in(str(extension_file.resolve()), str(file_error), 'file extension error should identify the path')

        missing = root / 'missing-extension'
        missing_error = _assert_raises(
            FileNotFoundError,
            browser_helpers.get_launch_args,
            _option(arguments=[], extensions=[missing], _ua_set=False),
        )
        assert_in(str(missing), str(missing_error), 'missing extension error should identify the path')


def test_preference_contracts():
    with TemporaryDirectory(prefix='dp-browser-prefs-') as tmp:
        user_data = Path(tmp)
        prefs_file = user_data / 'Profile 2' / 'Preferences'
        prefs_file.parent.mkdir(parents=True)
        with prefs_file.open('w', encoding='utf-8') as file:
            dump({'download': {'prompt_for_download': True, 'obsolete': 1}, 'keep': 'value'}, file)

        opt = _option(
            arguments=['--profile-directory=Profile 2'],
            user_data_path=str(user_data),
            preferences={
                'download.prompt_for_download': False,
                'download.default_directory': '/tmp/downloads',
                'profile.default_content_setting_values.notifications': 2,
            },
            _prefs_to_del=['download.obsolete', 'missing.branch'],
        )
        browser_helpers.set_prefs(opt)
        with prefs_file.open(encoding='utf-8') as file:
            prefs = load(file)

        assert_equal(
            prefs,
            {
                'download': {'prompt_for_download': False, 'default_directory': '/tmp/downloads'},
                'keep': 'value',
                'profile': {'default_content_setting_values': {'notifications': 2}},
            },
            'preference merge/delete contract mismatch',
        )

        default_file = user_data / 'invalid' / 'Default' / 'Preferences'
        default_file.parent.mkdir(parents=True)
        default_file.write_text('{invalid json', encoding='utf-8')
        invalid_opt = _option(
            user_data_path=str(user_data / 'invalid'),
            preferences={'browser.enabled': True},
        )
        browser_helpers.set_prefs(invalid_opt)
        with default_file.open(encoding='utf-8') as file:
            assert_equal(load(file), {'browser': {'enabled': True}},
                         'invalid preferences JSON should be replaced with configured preferences')

        absent_root = user_data / 'no-op'
        browser_helpers.set_prefs(_option(user_data_path=str(absent_root)))
        assert_false(absent_root.exists(), 'empty preference changes should not create a profile directory')


def test_flag_contracts():
    with TemporaryDirectory(prefix='dp-browser-flags-') as tmp:
        user_data = Path(tmp)
        state_file = user_data / 'Local State'
        with state_file.open('w', encoding='utf-8') as file:
            dump({
                'browser': {'enabled_labs_experiments': ['existing@old', 'plain-flag']},
                'unrelated': {'kept': True},
            }, file)

        browser_helpers.set_flags(_option(
            user_data_path=str(user_data),
            flags={'existing': 'new', 'added': None},
        ))
        with state_file.open(encoding='utf-8') as file:
            state = load(file)
        assert_equal(state['browser']['enabled_labs_experiments'],
                     ['existing@new', 'plain-flag', 'added'],
                     'flags should preserve order while replacing values and adding switches')
        assert_equal(state['unrelated'], {'kept': True}, 'unrelated local state should survive flag updates')

        browser_helpers.set_flags(_option(
            user_data_path=str(user_data),
            clear_file_flags=True,
            flags={'only': 'enabled'},
        ))
        with state_file.open(encoding='utf-8') as file:
            state = load(file)
        assert_equal(state['browser']['enabled_labs_experiments'], ['only@enabled'],
                     'clear_file_flags should discard persisted experiments')

        state_file.write_text('not json', encoding='utf-8')
        browser_helpers.set_flags(_option(user_data_path=str(user_data), flags={'fresh': None}))
        with state_file.open(encoding='utf-8') as file:
            assert_equal(load(file), {'browser': {'enabled_labs_experiments': ['fresh']}},
                         'invalid local-state JSON should be rebuilt')


def test_connection_contracts():
    calls = []

    def using(ip, port):
        calls.append(('using', ip, port))
        return True

    def connected(ip, port):
        calls.append(('connect', ip, port))
        return True

    opt = SimpleNamespace(is_auto_port=False, address='http://localhost:9222', is_existing_only=False)
    with _replaced(browser_helpers, port_is_using=using, test_connect=connected):
        assert_equal(browser_helpers.connect_browser(opt), None,
                     'reachable existing browser should be attached without launching')
    assert_equal(calls, [('using', '127.0.0.1', '9222'), ('connect', '127.0.0.1', '9222')],
                 'HTTP localhost address normalization mismatch')

    remote = SimpleNamespace(is_auto_port=False, address='https://10.2.3.4:9333', is_existing_only=False)
    with _replaced(browser_helpers, port_is_using=lambda ip, port: False,
                   test_connect=lambda ip, port: False):
        error = _assert_raises(BrowserConnectError, browser_helpers.connect_browser, remote)
    assert_equal(error._kwargs['ADDRESS'], '10.2.3.4:9333', 'remote connection error address mismatch')

    existing_only = SimpleNamespace(is_auto_port=False, address='127.0.0.1:9444', is_existing_only=True)
    with _replaced(browser_helpers, port_is_using=lambda ip, port: False,
                   test_connect=lambda ip, port: False):
        error = _assert_raises(BrowserConnectError, browser_helpers.connect_browser, existing_only)
    assert_equal(error._kwargs['ADDRESS'], '127.0.0.1:9444', 'existing-only error address mismatch')

    with TemporaryDirectory(prefix='dp-browser-connect-') as tmp:
        root = Path(tmp)
        executable = root / 'chrome'
        executable.write_bytes(b'')
        launch_calls = []
        setup_calls = []

        class FixedPortFinder:
            def __init__(self, path):
                assert_equal(path, str(root), 'auto-port finder should receive configured temp path')

            def get_port(self):
                return 9888

        class LaunchOption:
            is_auto_port = True
            tmp_path = str(root)
            arguments = ['--headless=new']
            extensions = []
            browser_path = str(executable)
            _browser_path = str(executable)
            system_user_path = False
            _old_browser = False
            _new_env = True
            _auto_port = True
            preferences = {'browser.enabled': True}
            _prefs_to_del = []
            flags = {'contract': None}
            clear_file_flags = False
            user_data_path = None

            def set_user_data_path(self, value):
                self.user_data_path = str(value)

        launch_opt = LaunchOption()
        with _replaced(
            browser_helpers,
            PortFinder=FixedPortFinder,
            ensure_del_dir=lambda path: setup_calls.append(('delete', Path(path))) or True,
            set_prefs=lambda opt: setup_calls.append(('prefs', opt.user_data_path)),
            set_flags=lambda opt: setup_calls.append(('flags', opt.user_data_path)),
            _run_browser=lambda port, path, args: launch_calls.append((port, path, list(args))),
            test_connect=lambda ip, port: setup_calls.append(('connect', ip, port)) or True,
        ):
            launch_args = browser_helpers.connect_browser(launch_opt)

        expected_user = root / 'DrissionPage' / 'autoPortData' / '9888'
        assert_equal(launch_opt._address, '127.0.0.1:9888', 'auto-port launch should persist the chosen address')
        assert_equal(Path(launch_opt.user_data_path), expected_user.resolve(),
                     'auto-port launch should configure an isolated user-data directory')
        assert_in('--headless=new', launch_args, 'configured browser switch should reach the launch process')
        assert_in(f'--user-data-dir={expected_user.resolve()}', launch_args,
                  'derived user-data switch should reach the launch process')
        assert_equal(launch_calls, [(9888, str(executable), launch_args)],
                     'browser launch boundary should receive the selected port, executable, and switches')
        assert_equal(setup_calls, [
            ('delete', expected_user),
            ('prefs', str(expected_user.resolve())),
            ('flags', str(expected_user.resolve())),
            ('connect', '127.0.0.1', 9888),
        ], 'auto-port setup order mismatch')

    sessions = []

    class Response:
        def __init__(self, payload):
            self.payload = payload
            self.closed = False

        def json(self):
            return self.payload

        def close(self):
            self.closed = True

    class FakeSession:
        def __init__(self):
            self.trust_env = True
            self.keep_alive = True
            self.closed = False
            self.calls = []
            self.response = Response({'webSocketDebuggerUrl': 'ws://127.0.0.1/devtools/browser/1'})
            sessions.append(self)

        def get(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return self.response

        def close(self):
            self.closed = True

    with _replaced(browser_helpers, Session=FakeSession,
                   wait_until=lambda func, timeout: func()):
        assert_true(browser_helpers.test_connect('127.0.0.1', 9555),
                    'debug endpoint with browser websocket should connect')
    session = sessions[-1]
    assert_false(session.trust_env, 'connection probe should ignore environment proxies')
    assert_false(session.keep_alive, 'connection probe should disable keep-alive')
    assert_equal(session.calls,
                 [(('http://127.0.0.1:9555/json/version',),
                   {'timeout': 10, 'headers': {'Connection': 'close'}})],
                 'debug endpoint request mismatch')
    assert_true(session.response.closed, 'successful probe should close its response')
    assert_true(session.closed, 'successful probe should close its session')

    class FailingSession(FakeSession):
        def get(self, *args, **kwargs):
            raise OSError('unreachable')

    with _replaced(browser_helpers, Session=FailingSession,
                   wait_until=lambda func, timeout: func()):
        assert_false(browser_helpers.test_connect('127.0.0.1', 9556),
                     'failed debug endpoint should report false')
    assert_true(sessions[-1].closed, 'failed probe should still close its session')


def test_process_invocation_contracts():
    calls = []

    def fake_popen(arguments, **kwargs):
        calls.append((arguments, kwargs))
        return 'process'

    with TemporaryDirectory(prefix='dp-browser-process-') as tmp:
        browser_dir = Path(tmp) / 'bundle'
        browser_dir.mkdir()
        with _replaced(browser_helpers, Popen=fake_popen):
            result = browser_helpers._run_browser(9666, str(browser_dir), ['--headless=new', '--no-first-run'])
        assert_equal(result, 'process', 'process wrapper should return Popen result')
        assert_equal(calls[0][0],
                     [str(browser_dir / 'chrome'), '--remote-debugging-port=9666',
                      '--headless=new', '--no-first-run'],
                     'browser process arguments mismatch')
        assert_equal(calls[0][1],
                     {'shell': False, 'stdout': browser_helpers.DEVNULL, 'stderr': browser_helpers.DEVNULL},
                     'browser process isolation options mismatch')

        def missing_popen(*args, **kwargs):
            raise FileNotFoundError('missing')

        with _replaced(browser_helpers, Popen=missing_popen):
            _assert_raises(FileNotFoundError, browser_helpers._run_browser, 9777, '/missing/chrome', [])


def test_port_and_folder_contracts():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    try:
        assert_true(tools.port_is_using('127.0.0.1', port), 'listening local socket should be detected')
    finally:
        listener.close()
    assert_false(tools.port_is_using('127.0.0.1', port), 'closed local socket should be available')

    with TemporaryDirectory(prefix='dp-browser-ports-') as tmp:
        auto_dir = Path(tmp) / 'DrissionPage' / 'autoPortData'
        stale = auto_dir / '47000'
        occupied = auto_dir / '47001'
        stale.mkdir(parents=True)
        occupied.mkdir()

        original_used = tools.PortFinder.used_port
        original_prev = tools.PortFinder.prev_time
        original_checked = tools.PortFinder.checked_paths
        tools.PortFinder.used_port = {47002}
        tools.PortFinder.prev_time = 0
        tools.PortFinder.checked_paths = set()
        ports = iter((47002, 47001, 47003))

        def fake_using(ip, candidate):
            return int(candidate) == 47001

        try:
            with _replaced(tools, port_is_using=fake_using), _replaced(random, randint=lambda *scope: next(ports)):
                finder = tools.PortFinder(tmp)
                assert_false(stale.exists(), 'stale auto-port data directory should be removed')
                assert_true(occupied.exists(), 'active auto-port data directory should be retained')
                assert_equal(finder.get_port((47000, 47004)), 47003,
                             'port finder should skip used, reserved, and listening ports')
                assert_in(47003, tools.PortFinder.used_port, 'allocated port should be reserved in-process')
        finally:
            tools.PortFinder.used_port = original_used
            tools.PortFinder.prev_time = original_prev
            tools.PortFinder.checked_paths = original_checked

        folder = Path(tmp) / 'clean'
        folder.mkdir()
        (folder / 'remove.txt').write_text('remove', encoding='utf-8')
        (folder / 'keep.txt').write_text('keep', encoding='utf-8')
        (folder / 'nested').mkdir()
        (folder / 'nested' / 'file.txt').write_text('remove', encoding='utf-8')
        tools.clean_folder(folder, ignore=['keep.txt'])
        assert_equal(sorted(item.name for item in folder.iterdir()), ['keep.txt'],
                     'folder cleanup should preserve only ignored entries')

        removable = Path(tmp) / 'removable'
        removable.mkdir()
        assert_true(tools.ensure_del_dir(removable), 'existing directory should be deleted')
        assert_false(removable.exists(), 'deleted directory should not remain')
        assert_true(tools.ensure_del_dir(Path(tmp) / 'absent'), 'missing directory should count as deleted')

    times = iter((0.0, 0.0, 6.0))
    sleeps = []
    with _replaced(tools, perf_counter=lambda: next(times),
                   rmtree=lambda path: (_ for _ in ()).throw(PermissionError('busy')),
                   sleep=lambda gap: sleeps.append(gap)):
        with TemporaryDirectory(prefix='dp-browser-busy-') as tmp:
            assert_false(tools.ensure_del_dir(tmp), 'persistent deletion errors should time out')
    assert_equal(sleeps, [.01], 'deletion retry should use the documented polling gap')

    assert_equal(tools.get_browser_progress_id(SimpleNamespace(pid=1234), '127.0.0.1:9222'), 1234,
                 'known process should expose its pid directly')


def test_wait_and_error_contracts():
    values = iter((None, None, 'ready'))
    assert_equal(tools.wait_until(lambda suffix: next(values), timeout=None, gap=0, suffix='ignored'),
                 'ready', 'unbounded wait should poll until the result is not None')
    assert_equal(tools.wait_until(lambda: False, timeout=0), False,
                 'false should be a completed result rather than a timeout')
    assert_equal(tools.wait_until(lambda: None, timeout=0), None,
                 'zero timeout should return immediately when no result exists')
    _assert_raises(WaitTimeoutError, tools.wait_until, lambda: None, timeout=0, err_txt='not ready')

    browser = SimpleNamespace(version='Chrome/140')
    mappings = (
        ('Cannot find context with specified id', ContextLostError, {}),
        ('Could not find node with given id', ElementLostError, {}),
        ('connection disconnected', PageDisconnectedError, {}),
        ('alert exists.', AlertExistsError, {}),
        ('Node does not have a layout object', NoRectError, {}),
        ('Cannot take screenshot with 0 height.', NoRectError, {}),
        ('Cannot navigate to invalid URL', IncorrectURLError, {'url': 'bad://url'}),
        ('Frame corresponds to an opaque origin and its storage key cannot be serialized', StorageError, {}),
        ('Sanitizing cookie failed', CookieFormatError, {'cookies': []}),
        ('Given expression does not evaluate to a function', JavaScriptError,
         {'functionDeclaration': 'not a function'}),
    )
    for error_text, expected_type, args in mappings:
        result = {'error': error_text, 'method': 'Runtime.callFunctionOn', 'args': args}
        error = _assert_raises(expected_type, tools.raise_error, result, browser)
        assert_equal(error._kwargs['INFO'], error_text, f'{expected_type.__name__} should retain CDP error text')

    invalid_header = {
        'error': 'Invalid header name',
        'method': 'Network.setExtraHTTPHeaders',
        'args': {'headers': {'bad\nname': 'value'}},
    }
    _assert_raises(ValueError, tools.raise_error, invalid_header, browser)

    missing_method = {'error': "'Page.missingMethod' wasn't found", 'method': 'Page.missingMethod', 'args': {}}
    _assert_raises(RuntimeError, tools.raise_error, missing_method, browser)
    timeout_result = {'error': 'timeout', 'method': 'Page.navigate', 'args': {'url': 'https://example.test'}}
    _assert_raises(TimeoutError, tools.raise_error, timeout_result, browser)
    unknown = {'error': 'new protocol error', 'method': 'Page.example', 'args': {'value': 1}}
    _assert_raises(CDPError, tools.raise_error, unknown, browser)
    _assert_raises(RuntimeError, tools.raise_error, unknown, browser, user=True)
    assert_true(tools.raise_error(unknown, browser, ignore=True) is unknown,
                'ignore=True should return the original protocol result')
    disconnected = {'error': 'connection disconnected', 'method': 'Page.enable', 'args': {}}
    assert_true(tools.raise_error(disconnected, browser, ignore=PageDisconnectedError) is disconnected,
                'matching ignored error type should return the original result')


def test_driver_contracts():
    mapping = ThreadSafeDict()
    mapping['key'] = 'value'
    assert_equal(mapping['key'], 'value', 'thread-safe mapping item lookup mismatch')
    assert_equal(mapping.get('missing', 'fallback'), 'fallback', 'thread-safe mapping default mismatch')
    mapping.pop('key', None)
    assert_equal(mapping.get('key'), None, 'thread-safe mapping pop should remove the item')
    mapping['one'] = 1
    mapping.clear()
    assert_equal(mapping.get('one'), None, 'thread-safe mapping clear should remove all items')

    stopped = object.__new__(Driver)
    stopped.is_running = False
    assert_equal(stopped.run('Page.enable'), {'error': 'connection disconnected'},
                 'stopped driver should reject commands without sending')

    sent = []
    active = object.__new__(Driver)
    active.is_running = True
    active._cur_id = 7
    active._send = lambda message, timeout, ws_id: (
        sent.append((message, timeout, ws_id)) or {'id': ws_id, 'result': {'ok': True}}
    )
    assert_equal(active.run('Runtime.evaluate', _timeout=2, _session_id='session-1', expression='1 + 1'),
                 {'ok': True}, 'driver should unwrap successful CDP results')
    assert_equal(sent, [({
        'id': 8,
        'method': 'Runtime.evaluate',
        'params': {'expression': '1 + 1'},
        'sessionId': 'session-1',
    }, 2, 8)], 'driver command envelope mismatch')

    active._send = lambda message, timeout, ws_id: {
        'error': {'message': 'protocol failed', 'data': {'code': 1}}
    }
    assert_equal(active.run('Page.navigate', _timeout=3, url='bad'), {
        'error': 'protocol failed',
        'method': 'Page.navigate',
        'args': {'url': 'bad'},
        'data': {'code': 1},
        'timeout': 3,
    }, 'driver should normalize CDP error responses')

    class WebSocket:
        def __init__(self):
            self.messages = []
            self.closed = False

        def send(self, message):
            self.messages.append(message)

        def close(self):
            self.closed = True

    websocket = WebSocket()
    sender = object.__new__(Driver)
    sender._ws = websocket
    sender.method_results = ThreadSafeDict()
    assert_equal(sender._send({'id': 1, 'method': 'Page.enable'}, timeout=0, ws_id=1),
                 {'id': 1, 'result': {}}, 'zero-timeout send should acknowledge immediately')
    assert_equal(websocket.messages, ['{"id": 1, "method": "Page.enable"}'],
                 'zero-timeout send should serialize the exact command')

    owner = SimpleNamespace(disconnects=0)
    owner._on_disconnect = lambda: setattr(owner, 'disconnects', owner.disconnects + 1)
    closing = object.__new__(Driver)
    closing.is_running = True
    closing._ws = websocket
    closing.method_results = ThreadSafeDict()
    closing.method_results[1] = Queue()
    closing._session_owner = {'session-1': object()}
    closing.alert_flag = {'session-1'}
    closing.owner = owner
    closing._stop()
    assert_false(closing.is_running, 'driver stop should clear running state')
    assert_true(websocket.closed, 'driver stop should close websocket')
    assert_equal(closing._ws, None, 'driver stop should release websocket reference')
    assert_equal(closing.method_results.get(1), None, 'driver stop should clear pending results')
    assert_equal(closing._session_owner, {}, 'driver stop should clear session owners')
    assert_equal(closing.alert_flag, set(), 'driver stop should clear alert state')
    assert_equal(owner.disconnects, 1, 'driver stop should notify owner exactly once')
    closing._stop()
    assert_equal(owner.disconnects, 1, 'stopping an already stopped driver should be idempotent')

    sessions = []

    class HttpResponse:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    class HttpSession:
        def __init__(self):
            self.trust_env = True
            self.keep_alive = True
            self.closed = False
            self.response = HttpResponse()
            self.calls = []
            sessions.append(self)

        def get(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return self.response

        def close(self):
            self.closed = True

    with _replaced(driver_module, Session=HttpSession):
        response = Driver.get('http://127.0.0.1:9222/json/version')
    session = sessions[0]
    assert_true(response is session.response, 'driver HTTP helper should return the response object')
    assert_false(session.trust_env, 'driver HTTP helper should ignore environment proxies')
    assert_false(session.keep_alive, 'driver HTTP helper should disable keep-alive')
    assert_equal(session.calls,
                 [(('http://127.0.0.1:9222/json/version',), {'headers': {'Connection': 'close'}})],
                 'driver HTTP request mismatch')
    assert_true(response.closed, 'driver HTTP helper should close its response')
    assert_true(session.closed, 'driver HTTP helper should close its session')
