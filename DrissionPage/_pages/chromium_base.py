# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from json import loads, JSONDecodeError
from os.path import sep
from pathlib import Path
from re import findall
from threading import Thread
from time import perf_counter, sleep

from DrissionRecord.tools import make_valid_name

from .._base.base import BasePage, Messenger
from .._configs.session_options import SessionOptions
from .._elements.chromium_element import run_js, make_chromium_eles, find_by_ax, wait_for_ele
from .._elements.none_element import NoneElement
from .._elements.session_element import make_session_ele
from .._functions.cookies import CookiesList
from .._functions.elements import SessionElementsList, get_frame, ChromiumElementsList
from .._functions.locator import get_loc, quotes_escape
from .._functions.settings import Settings as _S
from .._functions.tools import wait_until
from .._functions.web import location_in_viewport, NavResult
from .._units.actions import Actions
from .._units.console import Console
from .._units.listener import Listener
from .._units.rect import TabRect
from .._units.screencast import Screencast
from .._units.scroller import PageScroller
from .._units.setter import ChromiumBaseSetter
from .._units.states import PageStates
from .._units.waiter import BaseWaiter
from ..errors import (ContextLostError, CDPError, PageDisconnectedError, ElementLostError, JavaScriptError,
                      BrowserConnectError, LocatorError)


class ChromiumBase(BasePage, Messenger):
    def __init__(self, browser, target_id, context_id):
        BasePage.__init__(self)
        Messenger.__init__(self)
        self._browser = browser
        self._driver = self.browser._driver
        self._is_loading = None
        self._root_oid = None  # object id
        self._root_nid = None
        self._root_bid = None
        self._context_id = context_id
        self._default_context = context_id == browser._browser_id
        self._target_id = target_id
        self._frame_id = None
        self._set = None
        self._screencast = None
        self._actions = None
        self._states = None
        self._has_alert = False
        self._ready_state = None
        self._rect = None
        self._wait = None
        self._scroll = None
        self._console = None
        self._upload_list = None
        self._doc_got = False  # 用于在LoadEventFired和FrameStoppedLoading间标记是否已获取doc
        self._auto_handle_alert = None
        self._load_end_time = 0
        self._init_jss = []
        self._disconnect_flag = False
        self._type = 'ChromiumBase'
        self._Accessibility_enabled = False
        if not hasattr(self, '_listener'):
            self._listener = None

        self._event_handlers = {
            'Page.javascriptDialogOpening': [self._on_alert_open],
            'Page.javascriptDialogClosed': [self._on_alert_close],
            'Page.frameStartedLoading': [self._onFrameStartedLoading],
            'Page.frameNavigated': [self._onFrameNavigated],
            'Page.domContentEventFired': [self._onDomContentEventFired],
            'Page.loadEventFired': [self._onLoadEventFired],
            'Page.frameStoppedLoading': [self._onFrameStoppedLoading],
            'Page.frameAttached': [self._onFrameAttached],
            'Page.frameDetached': [self._onFrameDetached],
        }
        self._imm_events = {'Page.javascriptDialogOpening'}
        self._d_set_runtime_settings()
        self._start_messenger()
        self._connect_browser()
        url, usr, pwd, full = self._browser._tabs.get_proxy(self._context_id)
        if usr:
            self._proxy_usr = usr
            self._proxy_pwd = pwd
            self._enable_domain('Fetch', handleAuthRequests=True)
            self._set_callback("Fetch.authRequired", self._onAuthRequired)
            self._set_callback("Fetch.requestPaused", self._onRequestPaused)
        else:
            self._proxy_usr = None
            self._proxy_pwd = None
        self._proxy = full

    def __call__(self, locator, index=1, timeout=None):
        return self.ele(locator, index, timeout)

    def _d_set_runtime_settings(self):
        pass

    def _set_session_options(self, session_or_options=None):
        if session_or_options is None:
            session_or_options = self.browser._session_options or SessionOptions(
                read_file=self.browser._session_options is None)
            if self._proxy:
                session_or_options.set_proxies(self._proxy, self._proxy)
        super()._set_session_options(session_or_options)

    def _connect_browser(self):
        self._is_reading = False
        self._driver_init()
        if self._js_ready_state == 'complete' and self._ready_state is None:
            self._get_document()
            self._ready_state = 'complete'

    def _driver_init(self):
        self._is_loading = True

        self._alert = Alert(self._auto_handle_alert)
        self._enable_domain('Page')
        self._enable_domain('DOM')
        self._run_cdp('Emulation.setFocusEmulationEnabled', enabled=True)

        r = self._run_cdp('Page.getFrameTree')
        for i in findall(r"'id': '(.*?)'", str(r)):
            self.browser._tabs.add_frame(i, self.tab_id)
        if not self._frame_id:
            self._frame_id = r['frameTree']['frame']['id']
        self._inited = True

    def _get_document(self, timeout=10):
        if self._is_reading:
            return None
        self._is_reading = True
        timeout = max(timeout, 2)
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            try:
                root = self._run_cdp('DOM.getDocument', _timeout=timeout)['root']
                self._root_bid = root['backendNodeId']
                self._root_nid = root['nodeId']
                timeout = end_time - perf_counter()
                timeout = 1 if timeout <= 1 else timeout
                self._root_oid = self._run_cdp('DOM.resolveNode', backendNodeId=self._root_bid,
                                               _timeout=timeout)['object']['objectId']
                result = True
                break

            except PageDisconnectedError:
                result = False
                break
            except:
                timeout = end_time - perf_counter()
                timeout = .5 if timeout <= 0 else timeout
            sleep(.05)

        else:
            result = False

        if result:
            r = self._run_cdp('Page.getFrameTree', _ignore=PageDisconnectedError)
            for i in findall(r"'id': '(.*?)'", str(r)):
                self.browser._tabs.add_frame(i, self.tab_id)

        self._is_loading = False
        self._is_reading = False
        return result

    def _onFrameDetached(self, **kwargs):
        self.browser._tabs.remove_frame(kwargs['frameId'])

    def _onFrameAttached(self, **kwargs):
        self.browser._tabs.add_frame(kwargs['frameId'], self.tab_id)

    def _onFrameStartedLoading(self, **kwargs):
        self.browser._tabs.add_frame(kwargs['frameId'], self.tab_id)
        if kwargs['frameId'] == self._frame_id:
            self._doc_got = False
            self._ready_state = 'connecting'
            self._is_loading = True
            self._load_end_time = perf_counter() + self.timeouts.page_load
            if self._load_mode == 'eager':
                t = Thread(target=self._wait_to_stop)
                t.daemon = True
                t.start()

    def _onFrameNavigated(self, **kwargs):
        if kwargs['frame']['id'] == self._frame_id:
            self._doc_got = False
            self._ready_state = 'loading'
            self._is_loading = True
            if kwargs.get('type') == 'BackForwardCacheRestore':
                self._get_document()

    def _onDomContentEventFired(self, **kwargs):
        if self._load_mode == 'eager':
            self._run_cdp('Page.stopLoading')
        if self._get_document(self._load_end_time - perf_counter() - .1):
            self._doc_got = True
        self._ready_state = 'interactive'

    def _onLoadEventFired(self, **kwargs):
        if self._doc_got is False and self._get_document(self._load_end_time - perf_counter() - .1):
            self._doc_got = True
        self._ready_state = 'complete'

    def _onFrameStoppedLoading(self, **kwargs):
        self.browser._tabs.add_frame(kwargs['frameId'], self.tab_id)
        if kwargs['frameId'] == self._frame_id:
            if self._doc_got is False:
                self._get_document(self._load_end_time - perf_counter() - .1)
            self._ready_state = 'complete'

    def _onFileChooserOpened(self, **kwargs):
        if self._upload_list:
            if 'backendNodeId' not in kwargs:
                raise RuntimeError(_S._lang.joinn(_S._lang.CANNOT_INPUT_FILE))
            files = self._upload_list if kwargs['mode'] == 'selectMultiple' else self._upload_list[:1]
            self._run_cdp('DOM.setFileInputFiles', files=files, backendNodeId=kwargs['backendNodeId'])

            self._set_callback('Page.fileChooserOpened', None)
            self._run_cdp('Page.setInterceptFileChooserDialog', enabled=False)
            self._upload_list = None

    def _onAuthRequired(self, **kwargs):
        request_id = kwargs['requestId']
        if kwargs.get('authChallenge', {}).get('source') == 'Proxy':
            auth = {'response': 'ProvideCredentials', 'username': self._proxy_usr, 'password': self._proxy_pwd}
        else:
            auth = {'response': 'Default'}
        self._run_cdp("Fetch.continueWithAuth", requestId=request_id, authChallengeResponse=auth, _ignore=True)

    def _onRequestPaused(self, **kwargs):
        if 'responseErrorReason' in kwargs or 'responseStatusCode' in kwargs:
            self._run_cdp("Fetch.continueResponse", requestId=kwargs['requestId'], _ignore=True)
        else:
            self._run_cdp("Fetch.continueRequest", requestId=kwargs['requestId'], _ignore=True)

    def _wait_to_stop(self):
        end_time = perf_counter() + self.timeouts.page_load
        while perf_counter() < end_time:
            sleep(.02)
        if self._ready_state in ('interactive', 'complete') and self._is_loading:
            self.stop_loading()

    # ----------挂件----------
    @property
    def wait(self):
        if self._wait is None:
            self._wait = BaseWaiter(self)
        return self._wait

    @property
    def set(self):
        if self._set is None:
            self._set = ChromiumBaseSetter(self)
        return self._set

    @property
    def screencast(self):
        if self._screencast is None:
            self._screencast = Screencast(self)
        return self._screencast

    @property
    def actions(self):
        if self._actions is None:
            self._actions = Actions(self)
        self.wait.doc_loaded()
        return self._actions

    @property
    def listen(self):
        if self._listener is None:
            self._listener = Listener(self)
        return self._listener

    @property
    def states(self):
        if self._states is None:
            self._states = PageStates(self)
        return self._states

    @property
    def scroll(self):
        self.wait.doc_loaded()
        if self._scroll is None:
            self._scroll = PageScroller(self)
        return self._scroll

    @property
    def rect(self):
        # self.wait.doc_loaded()
        if self._rect is None:
            self._rect = TabRect(self)
        return self._rect

    @property
    def console(self):
        if self._console is None:
            self._console = Console(self)
        return self._console

    @property
    def timeout(self):
        return self._timeouts.base

    @property
    def timeouts(self):
        return self._timeouts

    # ----------挂件结束----------

    @property
    def browser(self):
        return self._browser

    @property
    def driver(self):
        if self._driver is None:
            raise BrowserConnectError(_S._lang.BROWSER_DISCONNECTED)
        return self._driver

    @property
    def title(self):
        return self._run_cdp_loaded('Target.getTargetInfo', targetId=self._target_id)['targetInfo']['title']

    @property
    def url(self):
        return self._run_cdp_loaded('Target.getTargetInfo', targetId=self._target_id)['targetInfo']['url']

    @property
    def _browser_url(self):
        return self.url

    @property
    def html(self):
        self.wait.doc_loaded()
        return self._run_cdp('DOM.getOuterHTML', objectId=self._root_oid)['outerHTML']

    @property
    def json(self):
        try:
            return loads(self('t:pre', timeout=.5).text)
        except JSONDecodeError:
            return None

    @property
    def tab_id(self):
        return self._target_id

    @property
    def active_ele(self):
        return self._run_js_loaded('return document.activeElement;')

    @property
    def load_mode(self):
        return self._load_mode

    @property
    def user_agent(self):
        return self._run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']

    @property
    def upload_list(self):
        return self._upload_list

    @property
    def session(self):
        if self._session is None:
            self._create_session()
        return self._session

    @property
    def _js_ready_state(self):
        try:
            return self._run_cdp('Runtime.evaluate', expression='document.readyState;', _timeout=3)['result']['value']
        except ContextLostError:
            return None
        except TimeoutError:
            return 'timeout'

    def run_cdp(self, cmd, **cmd_args):
        return self._run_cdp(cmd, _user=True, **cmd_args)

    def run_cdp_loaded(self, cmd, **cmd_args):
        return self._run_cdp_loaded(cmd, _user=True, **cmd_args)

    def _run_cdp_loaded(self, cmd, _ignore=None, _user=False, _timeout=None, **cmd_args):
        self.wait.doc_loaded()
        return self._run_cdp(cmd, _ignore=_ignore, _user=_user, _timeout=_timeout, **cmd_args)

    def run_js(self, script, *args, as_expr=False, timeout=None):
        return self._run_js(script, *args, as_expr=as_expr, timeout=timeout)

    def run_js_loaded(self, script, *args, as_expr=False, timeout=None):
        self.wait.doc_loaded()
        return self._run_js(script, *args, as_expr=as_expr, timeout=timeout)

    def _run_js(self, script, *args, as_expr=False, timeout=None):
        return run_js(self, script, as_expr, self.timeouts.script if timeout is None else timeout, args)

    def _run_js_loaded(self, script, *args, as_expr=False, timeout=None):
        self.wait.doc_loaded()
        return run_js(self, script, as_expr, self.timeouts.script if timeout is None else timeout, args)

    def run_async_js(self, script, *args, as_expr=False):
        run_js(self, script, as_expr, 0, args)

    def get(self, url, retry=None, interval=None, timeout=None, raise_err=False):
        retry, interval, is_file = self._before_connect(url, retry, interval)
        r = self._d_connect(url=self._url, retry=retry, interval=interval, timeout=timeout, raise_err=raise_err)
        self._url_available = r.ok
        return r

    def cookies(self, all_domains=False, all_info=False):
        self.wait.doc_loaded()
        if all_domains:
            if self._default_context:
                cookies = self._browser._run_cdp(f'Storage.getCookies')['cookies']
            else:
                cookies = self._browser._run_cdp(f'Storage.getCookies', browserContextId=self._context_id)['cookies']

        else:
            cookies = self._run_cdp('Network.getCookies')['cookies']

        if all_info:
            r = cookies
        else:
            r = [{'name': cookie['name'], 'value': cookie['value'], 'domain': cookie['domain']} for cookie in cookies]

        return CookiesList(r)

    def ele(self, locator, index=1, timeout=None):
        return self._ele(locator, timeout=timeout, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        return self._ele(locator, timeout=timeout, index=None)

    def s_ele(self, locator=None, index=1, timeout=None):
        if timeout is None:
            timeout = self.timeout
        return (NoneElement(self, method='s_ele()', args={'locator': locator, 'index': index, 'timeout': timeout})
                if locator and not self.wait.eles_loaded(locator, timeout=timeout)
                else make_session_ele(self, locator, index=index, method='s_ele()'))

    def s_eles(self, locator, timeout=None):
        return (make_session_ele(self, locator, index=None)
                if self.wait.eles_loaded(locator, timeout=timeout) else SessionElementsList())

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        if isinstance(locator, (str, tuple)):
            mode, loc = get_loc(locator)
        elif locator._type in ('ChromiumElement', 'ChromiumFrame'):
            return locator
        else:
            raise LocatorError(ALLOW_TYPE=_S._lang.ELE_OR_LOC, CURR_VAL=locator)
        self.wait.doc_loaded()

        if mode == 'ax':
            self._Accessibility_enable()
            bid = self._run_cdp('Accessibility.getRootAXNode', frameId=self._frame_id)['node']['backendDOMNodeId']
            return find_by_ax(self, bid, loc, index, timeout)

        else:
            return find_by_any(self, loc, index, timeout)

    def refresh(self, ignore_cache=False):
        self._is_loading = True
        self._run_cdp('Page.reload', ignoreCache=ignore_cache)
        self.wait.load_start()

    def forward(self, steps=1):
        self._forward_or_back(steps)

    def back(self, steps=1):
        self._forward_or_back(-steps)

    def _forward_or_back(self, steps):
        if steps == 0:
            return

        history = self._run_cdp('Page.getNavigationHistory')
        index = history['currentIndex']
        history = history['entries']
        direction = 1 if steps > 0 else -1
        curr_url = history[index]['url']
        nid = None
        for num in range(abs(steps)):
            for i in history[index::direction]:
                index += direction
                if i['url'] != curr_url:
                    nid = i['id']
                    curr_url = i['url']
                    break

        if nid:
            self._is_loading = True
            self._run_cdp('Page.navigateToHistoryEntry', entryId=nid)

    def stop_loading(self):
        try:
            self._run_cdp('Page.stopLoading')
            end_time = perf_counter() + 5
            while self._ready_state != 'complete' and perf_counter() < end_time:
                sleep(.02)
        except (PageDisconnectedError, CDPError):
            pass
        finally:
            self._ready_state = 'complete'

    def remove_ele(self, loc_or_ele):
        if not loc_or_ele:
            return
        ele = self._ele(loc_or_ele, raise_err=False)
        if ele:
            self._run_cdp('DOM.removeNode', nodeId=ele._node_id, _ignore=ElementLostError)

    def add_ele(self, html_or_info, insert_to=None, before=None):  # 即将废弃
        return self.new_ele(html_or_info=html_or_info, insert_to=insert_to, before=before)

    def new_ele(self, html_or_info, insert_to=None, before=None):
        if isinstance(html_or_info, str):
            insert_to = self.ele(insert_to) if insert_to else self.ele('t:body')
            args = [html_or_info, insert_to]
            if before:
                args.append(insert_to.ele(before))
                js = '''
                     ele = document.createElement(null);
                     arguments[1].insertBefore(ele, arguments[2]);
                     ele.outerHTML = arguments[0];
                     return arguments[2].previousElementSibling;
                     '''
            else:
                js = '''
                     ele = document.createElement(null);
                     arguments[1].appendChild(ele);
                     ele.outerHTML = arguments[0];
                     return arguments[1].lastElementChild;
                     '''

        elif isinstance(html_or_info, tuple):
            args = [html_or_info[0], html_or_info[1]]
            txt = ''
            if insert_to:
                args.append(self.ele(insert_to))
                if before:
                    args.append(self.ele(before))
                    txt = '''
                         arguments[2].insertBefore(ele, arguments[3]);
                         '''
                else:
                    txt = '''
                         arguments[2].appendChild(ele);
                         '''
            js = f'''
                     ele = document.createElement(arguments[0]);
                     for(let k in arguments[1]){{
                        if(k=="innerHTML"){{ele.innerHTML=arguments[1][k]}}
                        else if(k=="innerText"){{ele.innerText=arguments[1][k]}}
                        else{{ele.setAttribute(k, arguments[1][k]);}}
                     }}
                     {txt}
                     return ele;
                     '''

        else:
            raise ValueError(_S._lang.joinn(_S._lang.INCORRECT_VAL_, 'html_or_info', ALLOW_TYPE='html, tuple',
                                            TIP=_S._lang.NEW_ELE_INFO, CURR_VAL=html_or_info))

        try:
            ele = self._run_js(js, *args)
        except JavaScriptError:
            raise RuntimeError(_S._lang.joinn(_S._lang.DICT_TO_NEW_ELE))
        return ele

    def get_frame(self, loc_ind_ele='t:iframe', timeout=None):
        timeout = timeout if timeout is not None else self.timeouts.base
        now = perf_counter()
        end_time = now + timeout
        while now <= end_time:
            try:
                return get_frame(self, loc_ind_ele=loc_ind_ele, timeout=end_time - now)
            except ElementLostError:
                now = perf_counter()
        return NoneElement(self, 'get_frame()', args={'loc_ind_ele': loc_ind_ele, 'timeout': timeout})

    def get_frames(self, locator=None, timeout=None):
        locator = locator or 'xpath://*[name()="iframe" or name()="frame"]'
        return ChromiumElementsList(self, self._ele(locator, timeout=timeout, index=None, raise_err=False))

    def session_storage(self, item=None):
        js = f'sessionStorage.getItem("{item}")' if item else 'sessionStorage'
        return self._run_js_loaded(js, as_expr=True)

    def local_storage(self, item=None):
        js = f'localStorage.getItem("{item}")' if item else 'localStorage'
        return self._run_js_loaded(js, as_expr=True)

    def get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None,
                       full_page=False, left_top=None, right_bottom=None):
        return self._get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                    full_page=full_page, left_top=left_top, right_bottom=right_bottom)

    def add_init_js(self, script):
        js_id = self._run_cdp('Page.addScriptToEvaluateOnNewDocument', source=script,
                              includeCommandLineAPI=True)['identifier']
        self._init_jss.append(js_id)
        return js_id

    def remove_init_js(self, script_id=None):
        if script_id is None:
            for js_id in self._init_jss:
                self._run_cdp('Page.removeScriptToEvaluateOnNewDocument', identifier=js_id)
            self._init_jss.clear()

        elif script_id in self._init_jss:
            self._run_cdp('Page.removeScriptToEvaluateOnNewDocument', identifier=script_id)
            self._init_jss.remove(script_id)

    def clear_cache(self, session_storage=True, local_storage=True, cache=True, cookies=True):
        if session_storage and local_storage and cache and cookies:
            self._run_cdp_loaded("Storage.clearDataForOrigin", origin="*", storageTypes="all")

        if session_storage or local_storage:
            self.wait.doc_loaded()
            self._enable_domain('DOMStorage')
            i = self._run_cdp('Storage.getStorageKeyForFrame', frameId=self._frame_id)['storageKey']
            if session_storage:
                self._run_cdp('DOMStorage.clear', storageId={'storageKey': i, 'isLocalStorage': False})
            if local_storage:
                self._run_cdp('DOMStorage.clear', storageId={'storageKey': i, 'isLocalStorage': True})
            self.wait.doc_loaded()
            self._disable_domain('DOMStorage')

        if cache:
            self._run_cdp_loaded('Network.clearBrowserCache')

        if cookies:
            self._run_cdp_loaded('Network.clearBrowserCookies')

    def disconnect(self):
        self._stop_messenger()
        self._browser._tabs.remove_session(session_id=self._session_id)

    def handle_alert(self, accept=True, send=None, timeout=None, next_one=False):
        if not isinstance(accept, bool):
            return self._handle_alert(accept=accept, send=send, timeout=timeout, next_one=next_one)
        r = self._handle_alert(accept=accept, send=send, timeout=timeout, next_one=next_one)
        while self._has_alert:
            sleep(.0001)
        return r

    def _handle_alert(self, accept=True, send=None, timeout=None, next_one=False):
        if next_one:
            self._alert.handle_next = accept
            self._alert.next_text = send
            return
        if timeout is None:
            timeout = self.timeout
        timeout = .1 if timeout <= 0 else timeout
        end_time = perf_counter() + timeout
        while not self._alert.activated and perf_counter() < end_time:
            sleep(.01)
        if not self._alert.activated:
            return False

        res_text = self._alert.text
        if not isinstance(accept, bool):
            return res_text
        d = {'accept': accept, '_timeout': 0}
        if self._alert.type == 'prompt' and send is not None:
            d['promptText'] = send
        self._run_cdp('Page.handleJavaScriptDialog', **d)
        return res_text

    def _on_alert_open(self, **kwargs):
        self._alert.activated = True
        self._alert.text = kwargs['message']
        self._alert.type = kwargs['type']
        self._alert.defaultPrompt = kwargs.get('defaultPrompt')
        self._alert.response_accept = None
        self._alert.response_text = None
        self._has_alert = True

        if self._alert.auto is not None:
            if self._alert.auto != 'close':
                self._handle_alert(self._alert.auto)
        elif _S.auto_handle_alert is not None:
            self._handle_alert(_S.auto_handle_alert)
        elif self._alert.handle_next is not None:
            self._handle_alert(self._alert.handle_next, self._alert.next_text)
            self._alert.handle_next = None

    def _on_alert_close(self, **kwargs):
        self._alert.activated = False
        self._alert.text = None
        self._alert.type = None
        self._alert.defaultPrompt = None
        self._alert.response_accept = kwargs.get('result')
        self._alert.response_text = kwargs['userInput']
        self._has_alert = False

    def _wait_loaded(self, timeout=None):
        def do():
            return True if (self._ready_state == 'complete' or (self._load_mode == 'eager'
                                                                and self._ready_state in ('interactive', 'complete')
                                                                and not self._is_loading)) else None

        if timeout is None:
            timeout = self.timeouts.page_load
        r = wait_until(do, timeout=timeout)
        if r is not None:
            return r

        try:
            self.stop_loading()
        except CDPError:
            pass
        return False

    def _Accessibility_enable(self):
        if not self._Accessibility_enabled:
            self._enable_domain('Accessibility')
            self._Accessibility_enabled = True

    def _get_status_code(self, **kwargs):
        if kwargs.get('frameId') == self._frame_id and kwargs['type'] == 'Document':
            self._nav_result.status = kwargs['response']['status']
            self._nav_result.url = kwargs['response']['url']
            self._nav_result.headers = kwargs['response']['headers']

    def _get_request(self, **kwargs):
        if kwargs.get('frameId') == self._frame_id and kwargs.get('type') == 'Document':
            self._nav_result.request = kwargs['request']

    def _d_connect(self, url, retry, interval, timeout=None, raise_err=False):
        err = None
        self._is_loading = True
        timeout = timeout if timeout is not None else self.timeouts.page_load
        self._enable_domain('Network')
        self._nav_result = NavResult()
        self._set_callback('Network.responseReceived', self._get_status_code)
        self._set_callback('Network.requestWillBeSent', self._get_request)
        for t in range(retry + 1):
            err = None
            end_time = perf_counter() + timeout
            try:
                result = self._run_cdp('Page.navigate', frameId=self._frame_id, url=url, _timeout=timeout)
                if 'errorText' in result:
                    self._nav_result.status = result['errorText']
                    err = ConnectionError(_S._lang.joinn(_S._lang.CONNECT_ERR, INFO=result['errorText']))
            except TimeoutError:
                self._nav_result.status = 'net::ERR_TIMED_OUT'
                err = TimeoutError(_S._lang.joinn(_S._lang.TIMEOUT_, _S._lang.PAGE_CONNECT, timeout))

            if err:
                if t < retry:
                    sleep(interval)
                end_time1 = end_time - perf_counter()
                while self._ready_state not in ('loading', 'complete') and perf_counter() < end_time1:  # 等待出错信息显示
                    sleep(.01)
                self.stop_loading()
                continue

            if self._load_mode == 'none':
                self._remove_callback('Network.responseReceived', self._get_status_code)
                self._remove_callback('Network.requestWillBeSent', self._get_request)
                self._disable_domain('Network')
                return self._nav_result

            yu = end_time - perf_counter()
            ok = self._wait_loaded(1 if yu <= 0 else yu)
            if not ok:
                err = TimeoutError(_S._lang.joinn(_S._lang.TIMEOUT_, _S._lang.PAGE_CONNECT, timeout))
                if t < retry:
                    sleep(interval)
                continue

            if not err:
                break

        if err and raise_err:
            raise err if err is not None else ConnectionError(_S._lang.joinn(_S._lang.CONNECT_ERR))

        self._remove_callback('Network.responseReceived', self._get_status_code)
        self._remove_callback('Network.requestWillBeSent', self._get_request)
        self._disable_domain('Network')
        return self._nav_result

    def _get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None,
                        full_page=False, left_top=None, right_bottom=None, ele=None):
        if as_bytes:
            if as_bytes is True:
                pic_type = 'png'
            else:
                if as_bytes not in ('jpg', 'jpeg', 'png', 'webp'):
                    raise ValueError(_S._lang.joinn(_S._lang.INCORRECT_VAL_, 'as_bytes',
                                                    ALLOW_VAL='"jpg", "jpeg", "png", "webp"', CURR_VAL=as_bytes))
                pic_type = 'jpeg' if as_bytes == 'jpg' else as_bytes

        elif as_base64:
            if as_base64 is True:
                pic_type = 'png'
            else:
                if as_base64 not in ('jpg', 'jpeg', 'png', 'webp'):
                    raise ValueError(_S._lang.joinn(_S._lang.INCORRECT_VAL_, 'as_base64',
                                                    ALLOW_VAL='"jpg", "jpeg", "png", "webp"', CURR_VAL=as_base64))
                pic_type = 'jpeg' if as_base64 == 'jpg' else as_base64

        else:
            path = str(path).rstrip('\\/') if path else '.'
            if not path.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                if not name:
                    name = f'{self.title}.jpg'
                elif not name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    name = f'{name}.jpg'
                path = f'{path}{sep}{make_valid_name(name)}'

            path = Path(path)
            pic_type = path.suffix.lower()
            pic_type = 'jpeg' if pic_type == '.jpg' else pic_type[1:]

        if full_page:
            width, height = self.rect.size
            if width == 0 or height == 0:
                raise RuntimeError(_S._lang.joinn(_S._lang.ZERO_PAGE_SIZE))
            vp = {'x': 0, 'y': 0, 'width': width, 'height': height, 'scale': 1}
            args = {'format': pic_type, 'captureBeyondViewport': True, 'clip': vp}
        else:
            if left_top or right_bottom:
                if not left_top:
                    left_top = (0, 0)
                if not right_bottom:
                    right_bottom = self.rect.size
                x, y = left_top
                w = right_bottom[0] - x
                h = right_bottom[1] - y

                v = not (location_in_viewport(self, x, y) and
                         location_in_viewport(self, right_bottom[0], right_bottom[1]))
                if v and (self._run_js('return document.body.scrollHeight > window.innerHeight;') and
                          not self._run_js('return document.body.scrollWidth > window.innerWidth;')):
                    x += 10

                vp = {'x': x, 'y': y, 'width': w, 'height': h, 'scale': 1}
                args = {'format': pic_type, 'captureBeyondViewport': v, 'clip': vp}

            else:
                args = {'format': pic_type}

        if pic_type == 'jpeg':
            args['quality'] = 100
        png = self._run_cdp_loaded('Page.captureScreenshot', **args)['data']

        if as_base64:
            return png

        from base64 import b64decode
        png = b64decode(png)

        if as_bytes:
            return png

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(png)
        return str(path.resolve())

    def _download_by_browser(self, url, save_path=None, rename=None, suffix=None, timeout=None, file_exists=None):
        if rename:
            download = rename
            if suffix:
                download = f'{download}.{suffix.lstrip(".")}'
        else:
            download = ''
        e = self.new_ele(('a', {'href': url, 'target': '_blank', 'download': download}))
        m = e.click.to_download(save_path=save_path, rename=rename, suffix=suffix, timeout=timeout, by_js=True,
                                new_tab=True, file_exists=file_exists)
        self._run_cdp('Runtime.callFunctionOn', functionDeclaration='function(){arguments[0].remove();}',
                      arguments=[{'objectId': e._obj_id}], userGesture=True, _timeout=0, _ignore=True)
        return m


class Timeout(object):
    def __init__(self, base=None, page_load=None, script=None):
        self.base = 10 if base is None else base
        self.page_load = 30 if page_load is None else page_load
        self.script = 30 if script is None else script

    def __repr__(self):
        return str({'base': self.base, 'page_load': self.page_load, 'script': self.script})

    @property
    def as_dict(self):
        return {'base': self.base, 'page_load': self.page_load, 'script': self.script}


class Alert(object):
    def __init__(self, auto=None):
        self.activated = False
        self.text = None
        self.type = None
        self.defaultPrompt = None
        self.response_accept = None
        self.response_text = None
        self.handle_next = None
        self.next_text = None
        self.auto = auto


def do_find_syntax(page, loc, ind):
    r = page._run_cdp('DOM.performSearch', query=loc, includeUserAgentShadowDOM=True, _ignore=True)
    searchId = r.get('searchId')
    resultCount = r.get('resultCount')
    if not resultCount or (ind and resultCount < abs(ind)):
        page._run_cdp('DOM.discardSearchResults', searchId=searchId, _timeout=0, _ignore=True)
        return None

    r = page._run_cdp('DOM.getSearchResults', searchId=searchId, _ignore=True,
                      fromIndex=0, toIndex=resultCount).get('nodeIds')
    if not r or not r[0]:
        return None

    if ind is None:
        r = make_chromium_eles(page, _ids=r, index=None, id_type='node_id', ele_only=True)

    else:
        eles = []
        got = 0
        for i in r:
            n = page._run_cdp('DOM.describeNode', _ignore=True, nodeId=i).get('node')
            if not n:
                page._run_cdp('DOM.discardSearchResults', searchId=searchId, _timeout=0, _ignore=True)
                return None
            if n['nodeName'] not in ('#text', '#comment'):
                eles.append(i)
                got += 1
                if (0 < ind == got) or (not ind and got == 1):
                    break
        if not got:
            return None
        r = make_chromium_eles(page, _ids=eles, index=ind, id_type='node_id')

    page._run_cdp('DOM.discardSearchResults', searchId=searchId, _timeout=0, _ignore=True)
    return None if r is False else r


def find_by_any(page, loc, index, timeout):
    return wait_for_ele(do_find_any, target=page, timeout=timeout, index=index, page=page, loc=loc,
                        xpath=f'//*/text()[contains(., {quotes_escape(loc)})]/..', ind=index)


def do_find_any(page, loc, xpath, ind):
    return do_find_syntax(page, loc, ind) or do_find_syntax(page, xpath, ind)
