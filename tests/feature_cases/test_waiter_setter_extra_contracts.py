"""Feature: complementary waiter, setter, click, download, and screencast contracts."""
from __future__ import annotations

from base64 import b64encode
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import DrissionPage._units.downloader as downloader_module
import DrissionPage._units.screencast as screencast_module
import DrissionPage._units.setter as setter_module
import DrissionPage._units.waiter as waiter_module
from DrissionPage._functions.settings import Settings
from DrissionPage._units.clicker import Clicker
from DrissionPage._units.downloader import DownloadManager, DownloadMission, TabDownloadSettings
from DrissionPage._units.screencast import Screencast
from DrissionPage._units.setter import (
    BrowserSetter,
    ChromiumBaseSetter,
    ChromiumElementSetter,
    ChromiumFrameSetter,
    ChromiumTabSetter,
    LoadMode,
    SessionPageSetter,
    WindowSetter,
)
from DrissionPage._units.waiter import BaseWaiter, BrowserWaiter, ElementWaiter, OriginWaiter, wait_mission
from DrissionPage.errors import CDPError, CanNotClickError, ElementLostError, JavaScriptError, NoRectError, WaitTimeoutError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = 'waiter_setter_extra_contracts'
REQUIRES_BROWSER = False


def run(ctx):
    test_waiter_failure_and_cleanup_contracts()
    test_setter_failure_and_routing_contracts()
    test_clicker_failure_and_download_contracts()
    test_downloader_cleanup_contracts()
    test_screencast_loop_contracts()


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


@contextmanager
def _isolated_download_settings(path):
    originals = dict(TabDownloadSettings.TABS)
    TabDownloadSettings.TABS.clear()
    try:
        TabDownloadSettings('browser').path = str(path)
        yield
    finally:
        TabDownloadSettings.TABS.clear()
        TabDownloadSettings.TABS.update(originals)


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


def test_waiter_failure_and_cleanup_contracts():
    slept = []
    owner = object()
    with _replaced(waiter_module, sleep=slept.append):
        assert_true(OriginWaiter(owner)(0.25) is owner, 'origin wait should return its owner')
    assert_equal(slept, [0.25], 'origin wait should delegate the exact duration')

    stopped_manager = SimpleNamespace(_running=False)
    stopped_browser = SimpleNamespace(_dl_mgr=stopped_manager)
    _assert_raises(RuntimeError, BrowserWaiter(stopped_browser).download_begin, timeout=0)
    _assert_raises(RuntimeError, BrowserWaiter(stopped_browser).downloads_done, timeout=0)

    mission = SimpleNamespace(canceled=0)

    def cancel():
        mission.canceled += 1

    mission.cancel = cancel
    manager = SimpleNamespace(_running=True, _missions={'mission': mission})
    browser = SimpleNamespace(_dl_mgr=manager, _messenger_running=True)
    with _replaced(waiter_module, wait_until=lambda *args, **kwargs: None):
        assert_false(BrowserWaiter(browser).downloads_done(timeout=1),
                     'timed-out browser downloads should report failure')
        assert_false(BrowserWaiter(browser).downloads_done(timeout=1, cancel_if_timeout=False),
                     'timeout without cancellation should still report failure')
    assert_equal(mission.canceled, 1, 'only the cancel-enabled timeout should cancel pending missions')

    missing_owner = SimpleNamespace(timeout=1, _ele=lambda *args, **kwargs: None)
    base_waiter = BaseWaiter(missing_owner)
    assert_false(base_waiter.ele_displayed('#missing', timeout=1),
                 'missing displayed element should return False by default')
    _assert_raises(WaitTimeoutError, base_waiter.ele_displayed, '#missing', timeout=1, raise_err=True)

    hidden_owner = SimpleNamespace(
        timeout=1,
        _ele=lambda *args, **kwargs: SimpleNamespace(wait=SimpleNamespace(hidden=lambda *args, **kwargs: True)),
    )
    ticks = iter((10.0, 11.0))
    with _replaced(waiter_module, perf_counter=lambda: next(ticks)):
        assert_false(BaseWaiter(hidden_owner).ele_hidden('#late', timeout=1),
                     'element lookup consuming the timeout should report failure')
    ticks = iter((20.0, 21.0))
    with _replaced(waiter_module, perf_counter=lambda: next(ticks)):
        _assert_raises(WaitTimeoutError, BaseWaiter(hidden_owner).ele_hidden, '#late', timeout=1, raise_err=True)

    element = SimpleNamespace(
        timeout=0,
        states=SimpleNamespace(is_alive=True, is_enabled=False, is_displayed=False),
        rect=SimpleNamespace(size=(10, 20), location=(2, 3)),
    )
    element_waiter = ElementWaiter(element)
    assert_true(element_waiter.disabled_or_deleted(timeout=0) is element,
                'disabled_or_deleted should return an already disabled element')
    assert_true(element_waiter.hidden(timeout=0) is element, 'hidden should return an already hidden element')
    with _replaced(waiter_module, wait_until=lambda *args, **kwargs: None):
        _assert_raises(WaitTimeoutError, element_waiter.displayed, timeout=0, raise_err=True)
    with _replaced(waiter_module, sleep=lambda second: None):
        assert_true(element_waiter.stop_moving(timeout=0, gap=0) is element,
                    'stable immediate geometry should satisfy stop_moving')

    class MissingRect:
        @property
        def size(self):
            raise NoRectError

    no_rect = SimpleNamespace(timeout=0, rect=MissingRect())
    _assert_raises(NoRectError, ElementWaiter(no_rect).stop_moving, timeout=0, gap=0)

    flags = {'tab': True}
    disconnected_manager = SimpleNamespace(
        get_flag=lambda tab_id: flags.get(tab_id),
        set_flag=lambda tab_id, value: flags.__setitem__(tab_id, value),
    )
    disconnected = SimpleNamespace(_messenger_running=False, _dl_mgr=disconnected_manager)
    assert_false(wait_mission(disconnected, 'tab', 0), 'disconnected mission wait should fail immediately')
    assert_true(flags['tab'] is None, 'mission wait should clear its coordination flag on failure')

    failing_frame = SimpleNamespace(run_js=lambda script: (_ for _ in ()).throw(JavaScriptError('lost')))
    assert_equal(waiter_module.get_frame_title(failing_frame), '',
                 'frame title lookup should degrade to an empty string on script failure')


def test_setter_failure_and_routing_contracts():
    session = SimpleNamespace(
        hooks=None,
        params=None,
        cert=None,
        stream=None,
        trust_env=None,
        max_redirects=None,
    )
    response = SimpleNamespace(encoding='old')
    session_owner = SimpleNamespace(
        _downloader=None,
        _encoding='default',
        response=response,
        session=session,
    )
    session_setter = SessionPageSetter(session_owner)
    session_setter.encoding('latin-1', set_all=False)
    session_setter.hooks({'response': ['hook']})
    session_setter.params({'page': 2})
    session_setter.cert(('cert.pem', 'key.pem'))
    session_setter.stream(True)
    session_setter.trust_env(False)
    session_setter.max_redirects(7)
    assert_equal(session_owner._encoding, 'default', 'response-only encoding should preserve the owner default')
    assert_equal(response.encoding, 'latin-1', 'response-only encoding should update the current response')
    assert_equal(
        (session.hooks, session.params, session.cert, session.stream, session.trust_env, session.max_redirects),
        ({'response': ['hook']}, {'page': 2}, ('cert.pem', 'key.pem'), True, False, 7),
        'session passthrough setters should preserve exact values',
    )

    download_calls = []
    browser_owner = SimpleNamespace(
        _download_path=None,
        _auto_handle_alert=False,
        _dl_mgr=SimpleNamespace(
            set_path=lambda tab, path: download_calls.append(('path', tab, path)),
            set_file_exists=lambda tab, mode: download_calls.append(('exists', tab, mode)),
        ),
    )
    browser_setter = BrowserSetter(browser_owner)
    browser_setter.auto_handle_alert(on_off=None)
    browser_setter.download_path(None)
    browser_setter.when_download_file_exists('o')
    assert_true(browser_owner._auto_handle_alert is None, 'None alert policy should disable automatic handling')
    assert_equal(download_calls[-1], ('exists', 'browser', 'overwrite'),
                 'browser file-exists aliases should normalize before delegation')
    _assert_raises(ValueError, browser_setter.when_download_file_exists, 'replace')

    chromium_owner = SimpleNamespace(
        timeouts=SimpleNamespace(base=1, page_load=2, script=3),
        scroll=SimpleNamespace(_wait_complete=False),
        _enable_domain=lambda domain: None,
        _run_cdp=lambda method, **kwargs: None,
    )
    chromium_setter = ChromiumBaseSetter(chromium_owner)
    chromium_setter.blocked_urls(None)
    _assert_raises(ValueError, chromium_setter.blocked_urls, {'https://blocked.test'})

    class RecoveringElementOwner:
        def __init__(self):
            self.calls = []

        def _run_cdp(self, method, **kwargs):
            self.calls.append((method, kwargs))
            if len(self.calls) == 1:
                raise ElementLostError

    recovering_owner = RecoveringElementOwner()
    recovering_element = SimpleNamespace(owner=recovering_owner, _node_id=4)

    def refresh_id():
        recovering_element._node_id = 9

    recovering_element._refresh_id = refresh_id
    ChromiumElementSetter(recovering_element).attr('role', 'button')
    assert_equal(
        [call[1]['nodeId'] for call in recovering_owner.calls],
        [4, 9],
        'lost element attribute writes should refresh and retry with the new node id',
    )

    broken_style = SimpleNamespace(
        _run_js=lambda script: (_ for _ in ()).throw(JavaScriptError('script failed')),
    )
    _assert_raises(RuntimeError, ChromiumElementSetter(broken_style).style, 'color', 'red')

    frame_calls = []
    frame_set = SimpleNamespace(
        attr=lambda name, value: frame_calls.append(('attr', name, value)),
        property=lambda **kwargs: frame_calls.append(('property', kwargs)),
        style=lambda **kwargs: frame_calls.append(('style', kwargs)),
    )
    frame = SimpleNamespace(frame_ele=SimpleNamespace(set=frame_set))
    frame_setter = ChromiumFrameSetter(frame)
    frame_setter.attr('title', 'frame')
    frame_setter.property('value', 'one')
    frame_setter.style('display', 'block')
    assert_equal(frame_calls[0], ('attr', 'title', 'frame'), 'frame attributes should delegate to frame_ele.set')
    assert_equal(frame_calls[1], ('property', {'name': 'value', 'value': 'one'}),
                 'frame properties should preserve named delegation arguments')

    load_owner = SimpleNamespace(_load_mode='normal')
    LoadMode(load_owner).eager()
    assert_equal(load_owner._load_mode, 'eager', 'eager load mode should update the owner')
    _assert_raises(ValueError, LoadMode(load_owner), 'fast')

    tab_download_calls = []
    tab_owner = SimpleNamespace(
        timeouts=SimpleNamespace(base=1, page_load=2, script=3),
        _timeout=1,
        scroll=SimpleNamespace(_wait_complete=False),
        browser=SimpleNamespace(_dl_mgr=SimpleNamespace(
            set_rename=lambda tab, name, suffix: tab_download_calls.append(('rename', tab, name, suffix)),
            set_file_exists=lambda tab, mode: tab_download_calls.append(('exists', tab, mode)),
        )),
        tab_id='tab-7',
    )
    tab_setter = ChromiumTabSetter(tab_owner)
    tab_setter.timeouts(base=8)
    tab_setter.download_file_name('report', 'csv')
    tab_setter.when_download_file_exists('s')
    assert_equal((tab_owner.timeouts.base, tab_owner._timeout), (8, 8),
                 'tab base timeout should update both timeout views')
    assert_equal(tab_download_calls, [('rename', 'tab-7', 'report', 'csv'), ('exists', 'tab-7', 'skip')],
                 'tab download setters should target the owning tab and normalize aliases')

    class RetryingWindowOwner:
        def __init__(self):
            self.calls = 0
            self.fail_bounds = False

        def _run_cdp(self, method, **kwargs):
            if method == 'Browser.getWindowForTarget':
                self.calls += 1
                if self.calls == 1:
                    raise CDPError('retry')
                return {'windowId': 3, 'bounds': {'windowState': 'normal'}}
            if self.fail_bounds:
                raise CDPError('cannot set bounds')

    window_owner = RetryingWindowOwner()
    slept = []
    with _replaced(setter_module, sleep=slept.append):
        window = WindowSetter(window_owner)
    assert_equal((window._window_id, slept), (3, [0.02]), 'window info should retry after a transient CDP error')
    window_owner.fail_bounds = True
    _assert_raises(RuntimeError, window._perform, {'windowState': 'maximized'})


class _ClickOwner:
    def __init__(self, states=None):
        self.cdp_calls = []
        self.js_calls = []
        self.states = states

    def _run_cdp(self, method, **kwargs):
        self.cdp_calls.append((method, kwargs))
        if method == 'DOM.getNodeForLocation':
            return {'backendNodeId': 42}
        return {}


class _ClickElement:
    tag = 'button'
    timeout = 0
    _backend_id = 42

    def __init__(self):
        self.owner = _ClickOwner()
        self.scroll = SimpleNamespace(to_see=lambda: None)
        self.states = SimpleNamespace(
            is_enabled=True,
            is_displayed=True,
            is_in_viewport=True,
            is_covered=False,
        )
        self.rect = SimpleNamespace(
            viewport_corners=((1, 2), (5, 2), (5, 7), (1, 7)),
            viewport_click_point=(3, 4),
            viewport_midpoint=(4, 5),
            size=(4, 5),
        )
        self.wait = SimpleNamespace(has_rect=lambda **kwargs: self.rect.viewport_corners,
                                    clickable=lambda **kwargs: self)
        self.js_calls = []

    def _run_js(self, script):
        self.js_calls.append(script)


def test_clicker_failure_and_download_contracts():
    disabled = _ClickElement()
    disabled.states.is_enabled = False
    assert_false(Clicker(disabled).left(timeout=0), 'disabled immediate click should report failure')
    with _replaced(Settings, raise_when_click_failed=True):
        _assert_raises(CanNotClickError, Clicker(disabled).left, timeout=0)

    outside = _ClickElement()
    outside.states.is_in_viewport = False
    assert_true(Clicker(outside).left(timeout=0) is outside,
                'out-of-viewport simulated click should use the JS fallback')
    assert_equal(outside.js_calls, ['this.click();'], 'viewport fallback should issue one native JS click')

    cdp_fallback = _ClickElement()

    def cdp_call(method, **kwargs):
        if method == 'DOM.getNodeForLocation':
            raise CDPError('hit test unavailable')
        cdp_fallback.owner.cdp_calls.append((method, kwargs))

    cdp_fallback.owner._run_cdp = cdp_call
    assert_true(Clicker(cdp_fallback).left(timeout=0) is cdp_fallback,
                'CDP hit-test failure should fall back to the viewport midpoint')
    assert_equal(cdp_fallback.owner.cdp_calls[0][1]['x'], 4,
                 'CDP fallback click should use the midpoint x coordinate')
    assert_equal(cdp_fallback.owner.cdp_calls[0][1]['y'], 5,
                 'CDP fallback click should use the midpoint y coordinate')

    missing_rect = _ClickElement()
    missing_rect.wait.has_rect = lambda **kwargs: False
    _assert_raises(NoRectError, Clicker(missing_rect).left, timeout=1)

    no_tab = _ClickElement()
    no_tab.owner.scroll = SimpleNamespace(to_see=lambda ele: None)
    no_tab.tab = SimpleNamespace(
        _context_id='context',
        browser=SimpleNamespace(
            _tabs=SimpleNamespace(get_newest_tab=lambda context_id: 'current'),
            wait=SimpleNamespace(_new_tab=lambda *args, **kwargs: False),
        ),
    )
    _assert_raises(RuntimeError, Clicker(no_tab).middle)
    _assert_raises(RuntimeError, Clicker(no_tab).for_new_tab, timeout=0)

    with TemporaryDirectory(prefix='dp-click-download-extra-') as tmp:
        root = Path(tmp)
        with _isolated_download_settings(root / 'browser'):
            _check_click_download(root, new_tab=False)
            _check_click_download(root, new_tab=True)


def _check_click_download(root, new_tab):
    class FlagManager:
        def __init__(self):
            self._running = True
            self._waiting_tab = set()
            self._tab_missions = {}
            self.flags = {}

        def set_flag(self, tab_id, value):
            self.flags[tab_id] = value

        def get_flag(self, tab_id):
            return self.flags.get(tab_id)

    manager = FlagManager()
    restored_modes = []
    browser = SimpleNamespace(
        _dl_mgr=manager,
        _messenger_running=True,
        timeout=0,
        download_path=str(root / 'browser'),
    )

    def restore_mode(mode):
        TabDownloadSettings('browser').when_file_exists = mode
        restored_modes.append(mode)

    browser.set = SimpleNamespace(when_download_file_exists=restore_mode)
    rename_calls = []
    tab = SimpleNamespace(
        tab_id='tab-1',
        timeout=0,
        browser=browser,
        _browser=browser,
        download_path=str(root / 'original-tab'),
        set=SimpleNamespace(download_file_name=lambda name, suffix: rename_calls.append((name, suffix))),
    )
    class ImmediateMission:
        _when_file_exists = 'rename'
        from_tab = None

    mission = ImmediateMission()
    element = _ClickElement()
    element.tab = tab
    element.owner = SimpleNamespace(tab_id='tab-1', _tab=tab, _browser=browser, browser=browser)

    def trigger_download(script):
        active_tab = 'browser' if manager.get_flag('browser') is True else 'tab-1'
        manager.set_flag(active_tab, mission)

    element._run_js = trigger_download
    tab_settings = TabDownloadSettings('tab-1')
    tab_settings.path = str(root / 'tab-specific')
    tab_settings.rename = 'prepared'
    tab_settings.suffix = 'txt'
    tab_settings.when_file_exists = 'skip'

    if new_tab:
        browser_settings = TabDownloadSettings('browser')
        original_browser_path = browser_settings.path
        original_mode = browser_settings.when_file_exists
        result = Clicker(element).to_download(new_tab=True, by_js=True, timeout=0)
        assert_equal(browser_settings.path, original_browser_path,
                     'new-tab download should restore the browser download path')
        assert_equal(restored_modes, [original_mode],
                     'new-tab download should restore the browser file-exists policy')
        assert_true(mission in manager._tab_missions['tab-1'],
                    'new-tab mission should be indexed under the initiating tab')
        assert_equal(mission.from_tab, 'tab-1', 'new-tab mission should retain its initiating tab')
    else:
        result = Clicker(element).to_download(
            save_path=root / 'requested',
            rename='renamed',
            suffix='bin',
            by_js=True,
            timeout=0,
            file_exists='o',
        )
        assert_equal(tab_settings.path, tab.download_path,
                     'tab download should restore the tab configured download path')
        assert_equal(rename_calls, [('renamed', 'bin')], 'click download should delegate rename and suffix')
        assert_equal(mission._when_file_exists, 'overwrite',
                     'click download should normalize the file-exists alias on the mission')

    assert_true(result is mission, 'click download should return the immediate mission')
    assert_true(manager.get_flag('browser' if new_tab else 'tab-1') is None,
                'mission completion should clear the download coordination flag')
    assert_false('tab-1' in manager._waiting_tab, 'click download should clear its waiting-tab marker')


def test_downloader_cleanup_contracts():
    with TemporaryDirectory(prefix='dp-downloader-extra-') as tmp:
        root = Path(tmp)
        with _isolated_download_settings(root):
            browser = SimpleNamespace(
                download_path=str(root),
                _download_path=str(root),
                _context_id='default',
                _messenger_running=True,
                _set_callback=lambda event, callback: None,
                _run_cdp=lambda method, **kwargs: {},
                _tabs=SimpleNamespace(
                    get_context_id=lambda frame_id: 'default',
                    frame_ids={'frame-child': 'child-tab'},
                    openers={'child-tab': 'source-tab'},
                ),
            )
            manager = DownloadManager(browser)
            mission = DownloadMission(
                manager, 'default', 'child-tab', 'done-id', str(root), 'done.txt',
                'https://example.test/done', str(root), 'rename',
            )
            mission.from_tab = 'source-tab'
            mission.state = 'canceled'
            manager._missions[mission.id] = mission
            manager._tab_missions = {'child-tab': {mission}, 'source-tab': {mission}}
            manager.set_done(mission, 'completed', final_path=root / 'done.txt')
            assert_equal(mission.state, 'canceled', 'set_done should preserve an earlier canceled state')
            assert_true(mission.is_done, 'set_done should mark terminal missions done')
            assert_false(mission in manager._tab_missions['child-tab'],
                         'set_done should remove the destination-tab mission index')
            assert_false(mission in manager._tab_missions['source-tab'],
                         'set_done should remove the source-tab mission index')
            assert_false(mission.id in manager.missions, 'set_done should remove the global mission index')

            source_settings = TabDownloadSettings('source-tab')
            source_settings.path = str(root)
            source_settings.suffix = 'log'
            manager._waiting_tab.add('source-tab')
            manager._onDownloadWillBegin(
                guid='opener-id',
                frameId='frame-child',
                suggestedFilename='trace.txt',
                url='https://example.test/trace',
            )
            opener_mission = manager.missions['opener-id']
            assert_equal((opener_mission.name, opener_mission.from_tab), ('trace.log', 'source-tab'),
                         'opener download should apply source-tab suffix and ownership')
            assert_true(opener_mission in manager.get_tab_missions('source-tab'),
                        'opener download should be indexed under its source tab')
            manager._onDownloadProgress(guid='opener-id', state='canceled')
            assert_true(opener_mission.is_done, 'terminal progress should finalize the mission')
            assert_equal(opener_mission.state, 'canceled', 'terminal progress should retain canceled state')
            assert_false(opener_mission in manager.get_tab_missions('source-tab'),
                         'terminal progress should clean the source-tab index')

            default_cancel = DownloadMission(
                manager, 'default', 'tab', 'cancel-id', str(root), 'cancel.txt',
                'https://example.test/cancel', str(root), 'rename',
            )
            manager.cancel(default_cancel)
            assert_equal(default_cancel.state, 'canceled', 'default-context cancel should update mission state')

            cancel_calls = []
            timeout_manager = SimpleNamespace(
                _browser=SimpleNamespace(_messenger_running=True),
                cancel=lambda item: cancel_calls.append(item),
            )
            timed_out = DownloadMission(
                timeout_manager, 'default', 'tab', 'timeout-id', str(root), 'timeout.txt',
                'https://example.test/timeout', str(root), 'rename',
            )
            with _replaced(downloader_module, wait_until=lambda *args, **kwargs: None):
                assert_false(timed_out.wait(show=False, timeout=0),
                             'timed-out mission without a final path should return False')
            assert_equal(cancel_calls, [timed_out], 'timed-out mission should cancel itself by default')

            disconnected_cancels = []
            disconnected_manager = SimpleNamespace(
                _browser=SimpleNamespace(_messenger_running=False),
                cancel=lambda item: disconnected_cancels.append(item),
            )
            disconnected = DownloadMission(
                disconnected_manager, 'default', 'tab', 'offline-id', str(root), 'offline.txt',
                'https://example.test/offline', str(root), 'rename',
            )
            assert_false(disconnected.wait(show=False, timeout=0),
                         'disconnected mission wait should return False immediately')
            assert_equal(disconnected_cancels, [],
                         'an explicit disconnect result should not be treated as a timeout cancellation')


def test_screencast_loop_contracts():
    with TemporaryDirectory(prefix='dp-screencast-extra-') as tmp:
        root = Path(tmp)
        screenshot_calls = []
        owner = SimpleNamespace(browser=SimpleNamespace(_chromium_options=SimpleNamespace(tmp_path=None)))
        cast = Screencast(owner)
        cast._path = root
        cast._mode = 'imgs'
        cast._enable = True

        def screenshot(**kwargs):
            screenshot_calls.append(kwargs)
            cast._enable = False

        owner.get_screenshot = screenshot
        slept = []
        with _replaced(screencast_module, sleep=slept.append):
            cast._run()
        assert_false(cast._running, 'screenshot loop should clear its running flag after shutdown')
        assert_equal(len(screenshot_calls), 1, 'immediate shutdown should capture exactly one screenshot')
        assert_equal(screenshot_calls[0]['path'], root, 'image loop should capture into the configured path')
        assert_true(screenshot_calls[0]['name'].endswith('.jpg'), 'image loop should use JPEG frame names')
        assert_equal(slept, [0.04], 'image loop should apply its frame pacing interval')

        frame_root = root / 'tmp-frames'
        frame_root.mkdir()
        cdp_calls = []
        cast._tmp_path = frame_root
        owner._run_cdp = lambda method, **kwargs: cdp_calls.append((method, kwargs))
        cast._onScreencastFrame(
            metadata={'timestamp': 7.5},
            data=b64encode(b'extra-frame').decode(),
            sessionId=17,
        )
        assert_equal((frame_root / '7.5.jpg').read_bytes(), b'extra-frame',
                     'frame callback should prefer the temporary frame path')
        assert_in(('Page.screencastFrameAck', {'sessionId': 17}), cdp_calls,
                  'frame callback should acknowledge the exact screencast session')
