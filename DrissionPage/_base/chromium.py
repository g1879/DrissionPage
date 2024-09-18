# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path
from shutil import rmtree
from threading import Lock
from time import sleep, perf_counter

from requests import Session
from websocket import WebSocketBadStatusException

from .driver import BrowserDriver, Driver
from .._configs.chromium_options import ChromiumOptions
from .._functions.browser import connect_browser
from .._functions.cookies import CookiesList
from .._functions.settings import Settings
from .._functions.tools import PortFinder
from .._functions.tools import raise_error
from .._pages.chromium_base import Timeout
from .._pages.chromium_tab import ChromiumTab
from .._pages.mix_tab import MixTab
from .._units.downloader import DownloadManager
from .._units.setter import BrowserSetter
from .._units.states import BrowserStates
from .._units.waiter import BrowserWaiter
from ..errors import BrowserConnectError, CDPError
from ..errors import PageDisconnectedError

__ERROR__ = 'error'


class Chromium(object):
    _BROWSERS = {}
    _lock = Lock()

    def __new__(cls, addr_or_opts=None, session_options=None):
        opt = handle_options(addr_or_opts)
        is_headless, browser_id, is_exists = run_browser(opt)
        with cls._lock:
            if browser_id in cls._BROWSERS:
                r = cls._BROWSERS[browser_id]
                while not hasattr(r, '_driver'):
                    sleep(.1)
                return r
        r = object.__new__(cls)
        r._chromium_options = opt
        r._is_headless = is_headless
        r._is_exists = is_exists
        r.id = browser_id
        cls._BROWSERS[browser_id] = r
        return r

    def __init__(self, addr_or_opts=None, session_options=None):
        if hasattr(self, '_created'):
            return
        self._created = True

        self._type = 'Chromium'
        self._frames = {}
        self._drivers = {}
        self._all_drivers = {}

        self._set = None
        self._wait = None
        self._states = None
        self._timeouts = Timeout(**self._chromium_options.timeouts)
        self._load_mode = self._chromium_options.load_mode
        self._download_path = str(Path(self._chromium_options.download_path).absolute())
        self._auto_handle_alert = None
        self.retry_times = self._chromium_options.retry_times
        self.retry_interval = self._chromium_options.retry_interval
        self.address = self._chromium_options.address
        self._disconnect_flag = False
        self._driver = BrowserDriver(self.id, 'browser', self.address, self)

        if ((not self._chromium_options._ua_set and self._is_headless != self._chromium_options.is_headless)
                or (self._is_exists and self._chromium_options._new_env)):
            self.quit(3, True)
            connect_browser(self._chromium_options)
            s = Session()
            s.trust_env = False
            s.keep_alive = False
            ws = s.get(f'http://{self._chromium_options.address}/json/version', headers={'Connection': 'close'})
            self.id = ws.json()['webSocketDebuggerUrl'].split('/')[-1]
            self._driver = BrowserDriver(self.id, 'browser', self.address, self)
            ws.close()
            s.close()
            self._is_exists = False
            self._frames = {}
            self._drivers = {}
            self._all_drivers = {}

        self.version = self._run_cdp('Browser.getVersion')['product']

        self._process_id = None
        try:
            r = self._run_cdp('SystemInfo.getProcessInfo')
            for i in r.get('processInfo', []):
                if i['type'] == 'browser':
                    self._process_id = i['id']
                    break
        except:
            pass

        self._run_cdp('Target.setDiscoverTargets', discover=True)
        self._driver.set_callback('Target.targetDestroyed', self._onTargetDestroyed)
        self._driver.set_callback('Target.targetCreated', self._onTargetCreated)
        self._dl_mgr = DownloadManager(self)

        self._session_options = session_options

    @property
    def user_data_path(self):
        return self._chromium_options.user_data_path

    @property
    def process_id(self):
        return self._process_id

    @property
    def timeout(self):
        return self._timeouts.base

    @property
    def timeouts(self):
        return self._timeouts

    @property
    def load_mode(self):
        return self._load_mode

    @property
    def download_path(self):
        return self._download_path

    @property
    def set(self):
        if self._set is None:
            self._set = BrowserSetter(self)
        return self._set

    @property
    def states(self):
        if self._states is None:
            self._states = BrowserStates(self)
        return self._states

    @property
    def wait(self):
        if self._wait is None:
            self._wait = BrowserWaiter(self)
        return self._wait

    @property
    def tabs_count(self):
        j = self._run_cdp('Target.getTargets')['targetInfos']  # 不要改用get，避免卡死
        return len([i for i in j if i['type'] in ('page', 'webview') and not i['url'].startswith('devtools://')])

    @property
    def tab_ids(self):
        j = self._driver.get(f'http://{self.address}/json').json()  # 不要改用cdp，因为顺序不对
        return [i['id'] for i in j if i['type'] in ('page', 'webview') and not i['url'].startswith('devtools://')]

    @property
    def latest_tab(self):
        return self._get_tab(id_or_num=self.tab_ids[0], as_id=not Settings.singleton_tab_obj)

    def cookies(self, all_info=False):
        cks = self._run_cdp(f'Storage.getCookies')['cookies']
        r = cks if all_info else [{'name': c['name'], 'value': c['value'], 'domain': c['domain']} for c in cks]
        return CookiesList(r)

    def new_tab(self, url=None, new_window=False, background=False, new_context=False):
        return self._new_tab(True, url=url, new_window=new_window, background=background, new_context=new_context)

    def get_tab(self, id_or_num=None, title=None, url=None, tab_type='page'):
        t = self._get_tab(id_or_num=id_or_num, title=title, url=url, tab_type=tab_type, mix=True, as_id=False)
        if t._type != 'MixTab':
            raise RuntimeError('该标签页已有非MixTab版本，如需多对象公用请用Settings设置singleton_tab_obj为False。')
        return t

    def get_tabs(self, title=None, url=None, tab_type='page'):
        return self._get_tabs(title=title, url=url, tab_type=tab_type, mix=True, as_id=False)

    def close_tabs(self, tabs_or_ids=None, others=False):
        all_tabs = set(self.tab_ids)
        if isinstance(tabs_or_ids, str):
            tabs = {tabs_or_ids}
        elif isinstance(tabs_or_ids, ChromiumTab):
            tabs = {tabs_or_ids.tab_id}
        elif tabs_or_ids is None:
            tabs = {self.tab_ids[0]}
        elif isinstance(tabs_or_ids, (list, tuple)):
            tabs = set(i.tab_id if isinstance(i, ChromiumTab) else i for i in tabs_or_ids)
        else:
            raise TypeError('tabs_or_ids参数只能传入标签页对象或id。')

        if others:
            tabs = all_tabs - tabs

        end_len = len(set(all_tabs) - set(tabs))
        if end_len <= 0:
            self.quit()
            return

        for tab in tabs:
            self._onTargetDestroyed(targetId=tab)
            self._driver.run('Target.closeTarget', targetId=tab)
            sleep(.2)
        end_time = perf_counter() + 3
        while self.tabs_count != end_len and perf_counter() < end_time:
            sleep(.1)

    def activate_tab(self, id_ind_tab):
        if isinstance(id_ind_tab, int):
            id_ind_tab += -1 if id_ind_tab else 1
            id_ind_tab = self.tab_ids[id_ind_tab]
        elif isinstance(id_ind_tab, ChromiumTab):
            id_ind_tab = id_ind_tab.tab_id
        self._run_cdp('Target.activateTarget', targetId=id_ind_tab)

    def reconnect(self):
        self._disconnect_flag = True
        self._driver.stop()
        BrowserDriver.BROWSERS.pop(self.id)
        self._driver = BrowserDriver(self.id, 'browser', self.address, self)
        self._run_cdp('Target.setDiscoverTargets', discover=True)
        self._driver.set_callback('Target.targetDestroyed', self._onTargetDestroyed)
        self._driver.set_callback('Target.targetCreated', self._onTargetCreated)
        self._disconnect_flag = False

    def clear_cache(self, cache=True, cookies=True):
        if cache:
            self.latest_tab.run_cdp('Network.clearBrowserCache')

        if cookies:
            self._run_cdp('Storage.clearCookies')

    def quit(self, timeout=5, force=False, del_data=False):
        try:
            self._run_cdp('Browser.close')
        except PageDisconnectedError:
            pass
        self._driver.stop()

        drivers = list(self._all_drivers.values())
        for tab in drivers:
            for driver in tab:
                driver.stop()

        if force:
            pids = None
            try:
                pids = [pid['id'] for pid in self._run_cdp('SystemInfo.getProcessInfo')['processInfo']]
            except:
                pass

            if pids:
                from psutil import Process
                for pid in pids:
                    try:
                        Process(pid).kill()
                    except:
                        pass

                from os import popen
                from platform import system
                end_time = perf_counter() + timeout
                while perf_counter() < end_time:
                    ok = True
                    for pid in pids:
                        txt = f'tasklist | findstr {pid}' if system().lower() == 'windows' else f'ps -ef | grep {pid}'
                        p = popen(txt)
                        sleep(.05)
                        try:
                            if f'  {pid} ' in p.read():
                                ok = False
                                break
                        except TypeError:
                            pass

                    if ok:
                        break

        if del_data and not self._chromium_options.is_auto_port and self._chromium_options.user_data_path:
            path = Path(self._chromium_options.user_data_path)
            rmtree(path, True)

    def _new_tab(self, mix=True, url=None, new_window=False, background=False, new_context=False):
        obj = MixTab if mix else ChromiumTab
        tab = None
        if new_context:
            tab = self._run_cdp('Target.createBrowserContext')['browserContextId']

        kwargs = {'url': ''}
        if new_window:
            kwargs['newWindow'] = True
        if background:
            kwargs['background'] = True
        if tab:
            kwargs['browserContextId'] = tab

        if self.states.is_incognito():
            return _new_tab_by_js(self, url, obj, new_window)
        else:
            try:
                tab = self._run_cdp('Target.createTarget', **kwargs)['targetId']
            except CDPError:
                return _new_tab_by_js(self, url, obj, new_window)

        while tab not in self._drivers:
            sleep(.1)
        tab = obj(self, tab)
        if url:
            tab.get(url)
        return tab

    def _get_tab(self, id_or_num=None, title=None, url=None, tab_type='page', mix=True, as_id=False):
        if id_or_num is not None:
            if isinstance(id_or_num, int):
                id_or_num = self.tab_ids[id_or_num - 1 if id_or_num > 0 else id_or_num]
            elif isinstance(id_or_num, ChromiumTab):
                return id_or_num.tab_id if as_id else ChromiumTab(self, id_or_num.tab_id)
            elif id_or_num not in [i['id'] for i in self._driver.get(f'http://{self.address}/json').json()]:
                raise ValueError(f'没有找到标签页{id_or_num}，所有标签页：{self.tab_ids}')

        elif title == url is None and tab_type == 'page':
            id_or_num = self.tab_ids[0]

        else:
            tabs = self._get_tabs(title=title, url=url, tab_type=tab_type, as_id=True)
            if tabs:
                id_or_num = tabs[0]
            else:
                return None

        if as_id:
            return id_or_num
        with self._lock:
            return MixTab(self, id_or_num) if mix else ChromiumTab(self, id_or_num)

    def _get_tabs(self, title=None, url=None, tab_type='page', mix=True, as_id=False):
        tabs = self._driver.get(f'http://{self.address}/json').json()  # 不要改用cdp

        if isinstance(tab_type, str):
            tab_type = {tab_type}
        elif isinstance(tab_type, (list, tuple, set)):
            tab_type = set(tab_type)
        elif tab_type is not None:
            raise TypeError('tab_type只能是set、list、tuple、str、None。')

        tabs = [i for i in tabs if ((title is None or title in i['title']) and (url is None or url in i['url'])
                                    and (tab_type is None or i['type'] in tab_type))]
        if as_id:
            return [tab['id'] for tab in tabs]
        with self._lock:
            if mix:
                return [MixTab(self, tab['id']) for tab in tabs]
            else:
                return [ChromiumTab(self, tab['id']) for tab in tabs]

    def _run_cdp(self, cmd, **cmd_args):
        ignore = cmd_args.pop('_ignore', None)
        r = self._driver.run(cmd, **cmd_args)
        return r if __ERROR__ not in r else raise_error(r, ignore)

    def _get_driver(self, tab_id, owner=None):
        d = self._drivers.pop(tab_id, None)
        if not d:
            d = Driver(tab_id, 'page', self.address)
        d.owner = owner
        self._all_drivers.setdefault(tab_id, set()).add(d)
        return d

    def _onTargetCreated(self, **kwargs):
        if (kwargs['targetInfo']['type'] in ('page', 'webview')
                and kwargs['targetInfo']['targetId'] not in self._all_drivers
                and not kwargs['targetInfo']['url'].startswith('devtools://')):
            try:
                tab_id = kwargs['targetInfo']['targetId']
                d = Driver(tab_id, 'page', self.address)
                self._drivers[tab_id] = d
                self._all_drivers.setdefault(tab_id, set()).add(d)
            except WebSocketBadStatusException:
                pass

    def _onTargetDestroyed(self, **kwargs):
        tab_id = kwargs['targetId']
        self._dl_mgr.clear_tab_info(tab_id)
        for key in [k for k, i in self._frames.items() if i == tab_id]:
            self._frames.pop(key, None)
        for d in self._all_drivers.get(tab_id, tuple()):
            d.stop()
        self._drivers.pop(tab_id, None)
        self._all_drivers.pop(tab_id, None)

    def _on_disconnect(self):
        if not self._disconnect_flag:
            Chromium._BROWSERS.pop(self.id, None)
            if self._chromium_options.is_auto_port and self._chromium_options.user_data_path:
                path = Path(self._chromium_options.user_data_path)
                end_time = perf_counter() + 7
                while perf_counter() < end_time:
                    if not path.exists():
                        break
                    try:
                        rmtree(path)
                        break
                    except (PermissionError, FileNotFoundError, OSError):
                        pass
                    sleep(.03)


def handle_options(addr_or_opts):
    """设置浏览器启动属性
    :param addr_or_opts: 'ip:port'、ChromiumOptions、Driver
    :return: 返回ChromiumOptions对象
    """
    if not addr_or_opts:
        _chromium_options = ChromiumOptions(addr_or_opts)
        if _chromium_options.is_auto_port:
            port, path = PortFinder(_chromium_options.tmp_path).get_port(_chromium_options.is_auto_port)
            _chromium_options.set_address(f'127.0.0.1:{port}')
            _chromium_options.set_user_data_path(path)
            _chromium_options.auto_port(scope=_chromium_options.is_auto_port)

    elif isinstance(addr_or_opts, ChromiumOptions):
        if addr_or_opts.is_auto_port:
            port, path = PortFinder(addr_or_opts.tmp_path).get_port(addr_or_opts.is_auto_port)
            addr_or_opts.set_address(f'127.0.0.1:{port}')
            addr_or_opts.set_user_data_path(path)
            addr_or_opts.auto_port(scope=addr_or_opts.is_auto_port)
        _chromium_options = addr_or_opts

    elif isinstance(addr_or_opts, str):
        _chromium_options = ChromiumOptions()
        _chromium_options.set_address(addr_or_opts)

    elif isinstance(addr_or_opts, int):
        _chromium_options = ChromiumOptions()
        _chromium_options.set_local_port(addr_or_opts)

    else:
        raise TypeError('只能接收ip:port格式或ChromiumOptions类型参数。')

    return _chromium_options


def run_browser(chromium_options):
    """连接浏览器"""
    is_exists = connect_browser(chromium_options)
    try:
        s = Session()
        s.trust_env = False
        s.keep_alive = False
        ws = s.get(f'http://{chromium_options.address}/json/version', headers={'Connection': 'close'})
        if not ws:
            raise BrowserConnectError('\n浏览器连接失败，请确认浏览器是否启动。')
        json = ws.json()
        browser_id = json['webSocketDebuggerUrl'].split('/')[-1]
        is_headless = 'headless' in json['User-Agent'].lower()
        ws.close()
        s.close()
    except KeyError:
        raise BrowserConnectError('浏览器版本太旧或此浏览器不支持接管。')
    except:
        raise BrowserConnectError('\n浏览器连接失败，请确认浏览器是否启动。')
    return is_headless, browser_id, is_exists


def _new_tab_by_js(browser: Chromium, url, obj, new_window):
    mix = isinstance(obj, MixTab)
    tab = browser._get_tab(mix=mix)
    url = f'"{url}"' if url else ''
    new = 'target="_new"' if new_window else 'target="_blank"'
    tid = browser.latest_tab.tab_id
    tab.run_js(f'window.open({url}, {new})')
    tid = browser.wait.new_tab(curr_tab=tid)
    return browser._get_tab(tid, mix=mix)
