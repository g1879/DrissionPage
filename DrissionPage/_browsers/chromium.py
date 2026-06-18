# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from re import match
from threading import Lock
from time import sleep

from requests import Session

from .chromium_context import ChromiumContext
from .._base.base import Messenger
from .._base.driver import Driver, DebugDriver
from .._configs.chromium_options import ChromiumOptions
from .._functions.browser import connect_browser
from .._functions.cookies import CookiesList
from .._functions.settings import Settings as _S
from .._functions.tools import ensure_del_dir, wait_until
from .._functions.web import get_proxy_info
from .._pages.chromium_base import Timeout
from .._pages.chromium_tab import ChromiumTab
from .._units.downloader import DownloadManager
from .._units.listener import BrowserListener
from .._units.setter import BrowserSetter
from .._units.states import BrowserStates
from .._units.waiter import BrowserWaiter
from ..errors import BrowserConnectError, PageDisconnectedError, CDPError, IncorrectURLError


class Chromium(Messenger):
    _BROWSERS = {}
    _lock = Lock()

    def __new__(cls, addr_or_opts=None, session_options=None):
        with cls._lock:
            opt = handle_options(addr_or_opts)
            is_headless, browser_id, command_lines, ws_only, driver, incognito, guest = run_browser(opt)
            if browser_id in cls._BROWSERS:
                return cls._BROWSERS[browser_id]
            o = object.__new__(cls)
            o._driver = driver
            o._chromium_options = opt
            o._is_headless = is_headless
            o._incognito = incognito
            o._guest = guest
            o._ws_only = ws_only
            o._browser_id = browser_id
            o._is_exists, o._command_lines = (False, command_lines) if command_lines else (True, '')
            cls._BROWSERS[browser_id] = o
            return o

    def __init__(self, addr_or_opts=None, session_options=None):
        if hasattr(self, '_created'):
            return
        self._created = True

        super().__init__()
        self._type = 'Chromium'
        self._browser = self  # 用于Messenger兼容
        self._set = None
        self._listener = None
        self._wait = None
        self._states = None
        self._timeouts = Timeout(**self._chromium_options.timeouts)
        self._load_mode = self._chromium_options.load_mode
        self._download_path = str(Path(self._chromium_options.download_path).resolve())
        self._auto_handle_alert = None
        self._none_ele_return_value = False
        self._none_ele_value = None
        self.retry_times = self._chromium_options.retry_times
        self.retry_interval = self._chromium_options.retry_interval
        self.address = self._chromium_options.address
        self._ws_address = self._driver.address
        self._disconnect_flag = False
        self._event_handlers = {'Target.targetDestroyed': [self._onTargetDestroyed],
                                'Target.targetCreated': [self._onTargetCreated],
                                'Target.detachedFromTarget': [self._onDetachedFromTarget]}
        self._context = None
        self._tabs = Tabs()
        self._driver.owner = self

        if (not self._ws_only
                and (not self._chromium_options._ua_set and self._is_headless != self._chromium_options.is_headless)
                or (self._is_exists and self._chromium_options._new_env)):
            self.quit(3, True)
            connect_browser(self._chromium_options)
            s = Session()
            s.trust_env = False
            s.keep_alive = False
            ws = s.get(f'http://{self.address}/json/version', headers={'Connection': 'close'})
            self._ws_address = ws.json()['webSocketDebuggerUrl']
            self._driver = Driver(self._ws_address, self) if _S._debug is None else DebugDriver(self._ws_address, self)
            self._browser_id = _get_browser_id(self._driver, self._incognito or self._guest)
            ws.close()
            s.close()
            self._is_exists = False
            self._tabs = Tabs()

        self._context_id = self._browser_id
        self._default_context = True
        self._start_messenger()
        self._driver.add_session_owner(None, self)
        self._driver.owner = self

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
        self._dl_mgr = DownloadManager(self)
        # if not self._command_lines:
        #     self._command_lines = get_command_line(self)
        # self._can_access_form = '--disable-site-isolation-trials' in self._command_lines
        self._session_options = session_options
        if self._chromium_options.proxy:
            self._tabs.set_proxy('main', (self._chromium_options.proxy_url, self._chromium_options.proxy_usr,
                                          self._chromium_options.proxy_pwd, self._chromium_options.proxy))

        if 'chrome://privacy-sandbox-dialog/notice' in str(self._run_cdp('Target.getTargets')):
            tab = self.get_tab(url='chrome://privacy-sandbox-dialog/notice')
            if tab:
                close_privacy_dialog(tab)

    @property
    def context(self):
        if not self._context:
            self._context = ChromiumContext(self, self._browser_id)
        return self._context

    @property
    def id(self):
        return self._browser_id

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
    def listen(self):
        if self._listener is None:
            self._listener = BrowserListener(self)
        return self._listener

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
    def tab_ids(self):
        return self._tab_ids(self._browser_id)

    @property
    def latest_tab(self):
        ids = self.tab_ids
        if ids:
            return self._get_tab(self._browser_id, id_or_num=ids[0], as_id=not _S.singleton_tab_obj)
        t = self.new_tab()
        return t if _S.singleton_tab_obj else t.tab_id

    def _tab_ids(self, context_id):
        tabs = [i['targetId'] for i in self._run_cdp('Target.getTargets')['targetInfos']
                if i['browserContextId'] == context_id and i['type'] in ('page', 'webview')
                and not i['url'].startswith(('devtools://', 'chrome://newtab-footer'))]
        return tabs if self._ws_only else [i['id'] for i in self._driver.get(f'http://{self.address}/json').json()
                                           if i['id'] in tabs]

    def cookies(self, all_info=False):
        return self._cookies(all_info=all_info, context_id=None)

    def _cookies(self, all_info=False, context_id=None):
        if context_id:
            cks = self._run_cdp('Storage.getCookies', browserContextId=context_id)['cookies']
        else:
            cks = self._run_cdp('Storage.getCookies')['cookies']
        r = cks if all_info else [{'name': c['name'], 'value': c['value'], 'domain': c['domain']} for c in cks]
        return CookiesList(r)

    def new_context(self, proxy=None, proxy_bypass=None, auto_close=True):
        args = {'disposeOnDetach': auto_close}
        if proxy:
            url, usr, pwd, full = get_proxy_info(proxy)
        else:
            url, usr, pwd, full = self._tabs.get_proxy('main')

        if url:
            args['proxyServer'] = url
            if proxy_bypass:
                if not isinstance(proxy_bypass, str):
                    proxy_bypass = ';'.join(proxy_bypass)
                args['proxyBypassList'] = proxy_bypass

        cid = self._run_cdp('Target.createBrowserContext', **args)['browserContextId']
        if proxy:
            self._tabs.set_proxy(cid, (url, usr, pwd, full))

        if self._dl_mgr._running:
            self._run_cdp('Browser.setDownloadBehavior', downloadPath=self._download_path,
                          behavior='allowAndName', eventsEnabled=True, browserContextId=cid)

        return ChromiumContext(self, cid)

    def new_tab(self, url=None, new_window=False, background=False, hidden=False):
        return self._new_tab(url=url, new_window=new_window, background=background, hidden=hidden,
                             context_id=self._browser_id)

    def _new_tab(self, url=None, new_window=False, background=False, hidden=False, context_id=None, is_browser=True):
        kwargs = {'url': ''}
        if hidden:
            kwargs['hidden'] = True
        else:
            if new_window:
                kwargs['newWindow'] = True
            if background:
                kwargs['background'] = True
        if context_id:
            kwargs['browserContextId'] = context_id

        if self.states.is_incognito or self.states.is_guest and is_browser:
            return _new_tab_by_js(self, url, new_window, context_id)
        else:
            try:
                tab = self._run_cdp('Target.createTarget', **kwargs)['targetId']
            except CDPError:
                return _new_tab_by_js(self, url, new_window, context_id)

        if not hidden:
            while self.states.is_alive:
                if tab in self._tabs.target_ids:
                    break
                sleep(.01)
            else:
                raise BrowserConnectError(_S._lang.BROWSER_DISCONNECTED)
        tab = ChromiumTab(self, tab, context_id)
        if url:
            tab.get(url)
        return tab

    def get_tab(self, id_or_num=None, title=None, url=None, tab_type='page', as_id=False):
        return self._get_tab(self._browser_id, id_or_num=id_or_num, title=title,
                             url=url, tab_type=tab_type, as_id=as_id)

    def get_tabs(self, title=None, url=None, tab_type='page'):
        return self._get_tabs(self._browser_id, title=title, url=url, tab_type=tab_type, as_id=False)

    def close_tabs(self, tabs_or_ids, others=False):
        if isinstance(tabs_or_ids, str):
            tabs = {tabs_or_ids}
        elif isinstance(tabs_or_ids, ChromiumTab):
            tabs = {tabs_or_ids.tab_id}
        elif isinstance(tabs_or_ids, (list, tuple)):
            tabs = set(i.tab_id if isinstance(i, ChromiumTab) else i for i in tabs_or_ids)
        else:
            raise ValueError(_S._lang.joinn(_S._lang.INCORRECT_TYPE_, 'tabs_or_ids',
                                            ALLOW_TYPE=_S._lang.TAB_OR_ID, CURR_VAL=tabs_or_ids))

        all_tabs = set(self.tab_ids)
        if others:
            tabs = all_tabs - tabs

        if len(all_tabs - tabs) > 0:
            for tab in tabs:
                self._close_tab(tab=tab)
        else:
            self.quit()

    def _close_tab(self, tab):
        if isinstance(tab, str):
            tab = self.get_tab(tab)
        tab._run_cdp('Target.closeTarget', targetId=tab.tab_id)
        while tab.tab_id in self._tabs.target_ids:
            sleep(.01)

    def activate_tab(self, id_ind_tab):
        try:
            if isinstance(id_ind_tab, int):
                id_ind_tab += -1 if id_ind_tab else 1
                id_ind_tab = self.tab_ids[id_ind_tab]
            elif isinstance(id_ind_tab, ChromiumTab):
                id_ind_tab = id_ind_tab.tab_id
            self._run_cdp('Target.activateTarget', targetId=id_ind_tab)
        except (PageDisconnectedError, IndexError):
            raise RuntimeError(_S._lang.joinn(_S._lang.NO_SUCH_TAB))

    def reconnect(self):
        self._disconnect_flag = True
        self._driver.stop()
        self._driver = Driver(self._ws_address, self) if _S._debug is None else DebugDriver(self._ws_address, self)
        self._run_cdp('Target.setDiscoverTargets', discover=True)
        self._disconnect_flag = False

    def clear_cache(self, cache=True, cookies=True):
        if cache:
            self.latest_tab._run_cdp('Network.clearBrowserCache')

        if cookies:
            self._run_cdp('Storage.clearCookies')

    def quit(self, timeout=5, force=False, del_data=False):
        pids = None
        for tab in self._tabs.objects:
            tab._stop_messenger()
        self._tabs.clear()
        try:
            if force:
                pids = [pid['id'] for pid in self._run_cdp('SystemInfo.getProcessInfo')['processInfo']]
            self._run_cdp('Browser.close')
        except PageDisconnectedError:
            pass
        self._stop_messenger()

        if not self.address.startswith('127.0.0.1'):
            return

        def do():
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
            return ok if ok else None

        if pids:
            from psutil import Process
            for pid in pids:
                try:
                    Process(pid).kill()
                except:
                    pass

            from os import popen
            from platform import system
            wait_until(do, timeout=timeout)

        if self._chromium_options.is_auto_port or del_data:
            ensure_del_dir(self._chromium_options.user_data_path)

    def _attach(self, target_id):
        sid = self._run_cdp('Target.attachToTarget', targetId=target_id, flatten=True).get('sessionId')
        if not sid:
            raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2)
        return sid

    def _detach(self, session_id):
        try:
            self._run_cdp('Target.detachFromTarget', sessionId=session_id, _timeout=0, _ignore=True)
        except:
            pass
        self._driver.remove_session_owner(session_id)

    def _get_session_id(self, target_id, obj=None):
        if not target_id:
            return None
        sid = self._tabs._tab_first_session.pop(target_id, None)
        if not sid:
            sid = self._attach(target_id)
        self._tabs.add(sid, target_id, obj=obj)
        if obj:
            self._driver.add_session_owner(sid, obj)
        return sid

    def _get_tab(self, context_id, id_or_num=None, title=None, url=None, tab_type='page', as_id=False):
        tab_ids = [t for t in self._run_cdp('Target.getTargets')['targetInfos'] if t['browserContextId'] == context_id]
        if not self._ws_only:
            tab_ids = [t for t in self._driver.get(f'http://{self.address}/json').json()
                       if t['id'] in [i['targetId'] for i in tab_ids]]
        if not tab_ids:
            raise RuntimeError(_S._lang.joinn(_S._lang.NO_TAB))

        if id_or_num is not None:
            if isinstance(id_or_num, int):
                id_or_num = tab_ids[id_or_num - 1 if id_or_num > 0 else id_or_num]
            elif isinstance(id_or_num, ChromiumTab):
                return id_or_num.tab_id if as_id else ChromiumTab(self, id_or_num.tab_id, context_id)
            else:
                j = self._run_cdp('Target.getTargets')['targetInfos']
                if id_or_num not in [i['targetId'] for i in j if i['browserContextId'] == context_id]:
                    raise RuntimeError(_S._lang.joinn(_S._lang.NO_SUCH_TAB, ARG=id_or_num, ALL_TABS=tab_ids))

        elif title == url is None and tab_type == 'page':
            id_or_num = tab_ids[0]['id']

        else:
            tabs = self._get_tabs(context_id, title=title, url=url, tab_type=tab_type, as_id=True)
            if tabs:
                id_or_num = tabs[0]
            else:
                raise RuntimeError(_S._lang.joinn(_S._lang.NO_SUCH_TAB,
                                                  ARGS={'id_or_num': id_or_num, 'title': title, 'url': url,
                                                        'tab_type': tab_type}))

        return id_or_num if as_id else ChromiumTab(self, id_or_num, context_id)

    def _get_tabs(self, context_id, title=None, url=None, tab_type='page', as_id=False):
        tabs = [t for t in self._run_cdp('Target.getTargets')['targetInfos'] if t['browserContextId'] == context_id]
        if self._ws_only:
            _id = 'targetId'
        else:
            tabs = [t for t in self._driver.get(f'http://{self.address}/json').json()
                    if t['id'] in [i['targetId'] for i in tabs]]
            _id = 'id'
        if not tabs:
            raise RuntimeError(_S._lang.joinn(_S._lang.NO_TAB))

        if isinstance(tab_type, str):
            tab_type = {tab_type}
        elif isinstance(tab_type, (list, tuple, set)):
            tab_type = set(tab_type)
        elif tab_type is not None:
            raise ValueError(_S._lang.joinn(_S._lang.INCORRECT_TYPE_, 'tab_type',
                                            ALLOW_TYPE='set, list, tuple, str, None', CURR_VAL=tab_type))

        tabs = [i for i in tabs if ((title is None or title in i['title']) and (url is None or url in i['url'])
                                    and (tab_type is None or i['type'] in tab_type))]

        return [tab[_id] for tab in tabs] if as_id else [ChromiumTab(self, tab[_id], context_id) for tab in tabs]

    def _onTargetCreated(self, **kwargs):
        if kwargs['targetInfo']['type'] == 'page' and not kwargs['targetInfo']['url'].startswith('devtools://'):
            tab_id = kwargs['targetInfo']['targetId']
            self._tabs.add_frame(tab_id, tab_id)
            sid = self._attach(tab_id)
            cid = kwargs['targetInfo'].get('browserContextId', self._context_id)
            self._tabs.add(sid, tab_id, context_id=cid, opener=kwargs['targetInfo'].get('openerId'))
            self._tabs._tab_first_session[tab_id] = sid
            self._tabs.set_newest_tab(cid, tab_id)

    def _onTargetDestroyed(self, **kwargs):
        tab_id = kwargs['targetId']
        self._dl_mgr.clear_tab_info(tab_id)
        self._tabs.stop_target(target_id=tab_id)
        if self._listener:
            self._listener._caught.pop(tab_id, None)

    def _onDetachedFromTarget(self, **kwargs):
        self._tabs.stop_session(kwargs['sessionId'])
        self._driver.remove_session_owner(kwargs['sessionId'])

    def _on_disconnect(self):
        if not self._disconnect_flag:
            Chromium._BROWSERS.pop(self.id, None)
            if self._chromium_options.is_auto_port:
                ensure_del_dir(self._chromium_options.user_data_path)
        self._stop_messenger()
        if self._listener:
            self._listener.listening = False

    def _stop(self):
        self._stop_messenger()
        self._driver.stop()


def handle_options(addr_or_opts):
    if isinstance(addr_or_opts, ChromiumOptions):
        return addr_or_opts

    elif not addr_or_opts:
        return ChromiumOptions(False)

    elif isinstance(addr_or_opts, str) and ':' in addr_or_opts:
        return ChromiumOptions().set_address(addr_or_opts)

    elif isinstance(addr_or_opts, int):
        return ChromiumOptions().set_local_port(addr_or_opts)

    else:
        raise ValueError(_S._lang.joinn(_S._lang.INCORRECT_VAL_, 'addr_or_opts',
                                        ALLOW_TYPE=_S._lang.IP_OR_OPTIONS, CURR_VAL=addr_or_opts))


def run_browser(options):
    ws_only = False
    if options.ws_address:
        try:
            driver = Driver(options.ws_address, None) if _S._debug is None else DebugDriver(options.ws_address, None)
        except EnvironmentError:
            raise
        except Exception as e:
            raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2, INFO=str(e))
        info = str(driver.run('Browser.getHistograms'))
        incognito = "'Browser.WindowCount.Incognito'" in info
        guest = "'Browser.WindowCount.Guest'" in info
        browser_id = _get_browser_id(driver, incognito or guest)
        is_headless = 'headless' in driver.run('Browser.getVersion', _debug=_S._debug)['userAgent'].lower()
        if 'devtools/browser' not in options.ws_address:
            return is_headless, browser_id, True, True, driver, incognito, guest

        s = Session()
        s.trust_env = False
        s.keep_alive = False
        try:
            ws = s.get(f'http://{options.address}/json/version', headers={'Connection': 'close'}, timeout=2)
            if not ws:
                ws_only = True
            else:
                if ws.json()['webSocketDebuggerUrl'].endswith('browser'):
                    ws_only = True
                ws.close()
        except:
            ws_only = True
        s.close()
        return is_headless, browser_id, True, ws_only, driver, incognito, guest

    command_lines = connect_browser(options)
    try:
        s = Session()
        s.trust_env = False
        s.keep_alive = False
        ws = s.get(f'http://{options.address}/json/version', headers={'Connection': 'close'}, timeout=2)
        if not ws and not options.ws_address:
            raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2)
        j = ws.json()
        browser_id = j['webSocketDebuggerUrl'].split('/')[-1]
        is_headless = 'headless' in j['User-Agent'].lower()
        if j['webSocketDebuggerUrl'].endswith('browser'):
            ws_only = True
        ws.close()
        s.close()
    except KeyError:
        raise BrowserConnectError(_S._lang.BROWSER_NOT_FOR_CONTROL)
    except:
        raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2)
    driver = (Driver(f'ws://{options.address}/devtools/browser/{browser_id}', None) if _S._debug is None
              else DebugDriver(f'ws://{options.address}/devtools/browser/{browser_id}', None))

    info = str(driver.run('Browser.getHistograms'))
    incognito = "'Browser.WindowCount.Incognito'" in info
    guest = "'Browser.WindowCount.Guest'" in info
    browser_id = _get_browser_id(driver, incognito or guest)
    return is_headless, browser_id, command_lines, ws_only, driver, incognito, guest


def _get_browser_id(driver, incognito):
    if incognito:
        browser_id = driver.run('Target.getTargets', _debug=_S._debug)
        if 'error' in browser_id:
            raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2, INFO=browser_id['error'])
        return browser_id['targetInfos'][0]['browserContextId']

    browser_id = driver.run('Target.getBrowserContexts', _debug=_S._debug)
    if 'error' in browser_id:
        raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2, INFO=browser_id['error'])
    if 'defaultBrowserContextId' in browser_id:
        browser_id = browser_id['defaultBrowserContextId']
    else:
        browser_id = driver.run('Target.getTargets', _debug=_S._debug)
        if 'error' in browser_id:
            raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2, INFO=browser_id['error'])
        browser_id = browser_id['targetInfos'][0]['browserContextId']
    return browser_id


class Tabs(object):
    def __init__(self, ):
        self._sessions = {}  # {session_id: target_id}
        self._targets = {}  # {target_id: {session_id}}
        self._objects = {}  # {session_id: ChromiumBase}
        self._openers = {}  # {target_id: target_id}
        self._frames = {}  # {frame_id: target_id} 记录某个frame在哪个tab中
        self._contexts = {}  # {target_id: context_id}
        self._context_newest_tab = {}  # {context_id: target_id}
        self._tab_first_session = {}  # {target_id: session:id}
        self._proxies = {}  # {context_id: (url, usr, pwd)}

    @property
    def session_ids(self):
        return self._sessions.keys()

    @property
    def target_ids(self):
        return self._targets.keys()

    @property
    def objects(self):
        return self._objects.values()

    @property
    def frame_ids(self):
        return self._frames

    @property
    def openers(self):
        return self._openers

    def add(self, session_id, target_id, context_id=None, opener=None, obj=None):
        self._sessions[session_id] = target_id
        self._targets.setdefault(target_id, set()).add(session_id)
        if context_id:
            self._contexts[target_id] = context_id
        if opener:
            self._openers[target_id] = opener
        if obj:
            self._objects[session_id] = obj

    def add_obj(self, session_id, obj):
        if session_id in self._sessions:
            self._objects[session_id] = obj

    def add_frame(self, frame_id, target_id):
        self._frames[frame_id] = target_id

    def remove_frame(self, frame_id):
        self._frames.pop(frame_id, None)

    def remove_session(self, session_id):
        s = self._targets.get(self._sessions.get(session_id))
        if s:
            s.discard(session_id)
        self._objects.pop(session_id, None)
        self._sessions.pop(session_id, None)

    def remove_target(self, target_id):
        for session_id in self._targets.get(target_id, set()):
            self._objects.pop(session_id, None)
            self._sessions.pop(session_id, None)
        for fid in [fid for fid, t in self._frames.items() if t == target_id]:
            self._frames.pop(fid, None)
        self._targets.pop(target_id, None)
        self._openers.pop(target_id, None)
        self._tab_first_session.pop(target_id, None)

    def remove_context(self, context_id):
        self._context_newest_tab.pop(context_id, None)
        self._proxies.pop(context_id, None)

    def set_proxy(self, context_id, proxy):
        self._proxies[context_id] = proxy

    def get_proxy(self, context_id):
        return self._proxies.get(context_id, self._proxies.get('main', (None, None, None, None)))

    def set_newest_tab(self, context_id, target_id):
        self._context_newest_tab[context_id] = target_id

    def get_newest_tab(self, context_id):
        return self._context_newest_tab.get(context_id)

    def get_session_ids(self, target_id):
        return self._targets.get(target_id, set())

    def get_target_id(self, session_id):
        return self._sessions.get(session_id)

    def get_context_id(self, target_id=None, frame_id=None):
        if frame_id:
            return self._contexts.get(self._frames.get(frame_id))
        elif target_id:
            return self._contexts.get(target_id)
        return None

    def get_object(self, session_id, default=None):
        return self._objects.get(session_id, default)

    def stop_session(self, session_id):
        obj = self.get_object(session_id=session_id)
        if obj:
            obj._stop_messenger()
        self.remove_session(session_id)

    def stop_target(self, target_id):
        for session_id in self._targets.get(target_id, set()):
            self.stop_session(session_id)
        self.remove_target(target_id)

    def clear(self):
        self._sessions.clear()
        self._targets.clear()
        self._objects.clear()
        self._openers.clear()
        self._frames.clear()
        self._tab_first_session.clear()


def close_privacy_dialog(tab):
    try:
        sid = tab._run_cdp('DOM.performSearch', query='//*[name()="privacy-sandbox-notice-dialog-app"]',
                           includeUserAgentShadowDOM=True)['searchId']
        r = tab._run_cdp('DOM.getSearchResults', searchId=sid, fromIndex=0, toIndex=1)['nodeIds'][0]

        def do():
            try:
                return tab._run_cdp('DOM.describeNode', nodeId=r)['node']['shadowRoots'][0]['backendNodeId']
            except KeyError:
                return None

        wait_until(do, timeout=3)
        tab._run_cdp('DOM.discardSearchResults', searchId=sid)
        r = tab._run_cdp('DOM.resolveNode', backendNodeId=r)['object']['objectId']
        r = tab._run_cdp('Runtime.callFunctionOn', objectId=r,
                         functionDeclaration='function(){return this.getElementById("ackButton");}')['result'][
            'objectId']
        tab._run_cdp('Runtime.callFunctionOn', objectId=r, functionDeclaration='function(){return this.click();}')

    except:
        pass


def _new_tab_by_js(browser: Chromium, url, new_window, context_id):
    tab = browser._get_tab(context_id)
    if url and not match(r'^.*?://.*', url):
        raise IncorrectURLError(_S._lang.INVALID_URL, url=url)
    url = f'"{url}"' if url else '""'
    new = 'target="_new"' if new_window else 'target="_blank"'
    tid = browser._tabs.get_newest_tab(context_id)
    tab.run_js(f'window.open({url}, {new})')
    tid = browser.wait.new_tab(curr_tab=tid)
    return browser._get_tab(context_id, tid)

# def get_command_line(browser):
#     try:
#         t = browser.get_tab(browser._run_cdp('Target.createTarget', url='chrome://version/', hidden=True)['targetId']
#                             , tab_type=None)
#         lines = t.ele('#command_line').text
#         t.close()
#     except:
#         lines = ''
#     return lines
