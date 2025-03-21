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

from DataRecorder.tools import make_valid_name

from .._base.base import BasePage
from .._elements.chromium_element import run_js, make_chromium_eles
from .._elements.none_element import NoneElement
from .._elements.session_element import make_session_ele
from .._functions.cookies import CookiesList
from .._functions.elements import SessionElementsList, get_frame, ChromiumElementsList
from .._functions.locator import get_loc
from .._functions.settings import Settings as _S
from .._functions.tools import raise_error
from .._functions.web import location_in_viewport
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

__ERROR__ = 'error'


class ChromiumBase(BasePage):
    def __init__(self, browser, target_id=None):
        super().__init__()
        self._browser = browser
        self._is_loading = None
        self._root_id = None  # object id
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
        if not hasattr(self, '_listener'):
            self._listener = None

        self._d_set_runtime_settings()
        self._connect_browser(target_id)

    def __call__(self, locator, index=1, timeout=None):
        return self.ele(locator, index, timeout)

    def _d_set_runtime_settings(self):
        pass

    def _connect_browser(self, target_id=None):
        self._is_reading = False

        if not target_id:
            tabs = self.browser._driver.get(f'http://{self.browser.address}/json').json()
            tabs = [(i['id'], i['url']) for i in tabs
                    if i['type'] in ('page', 'webview') and not i['url'].startswith('devtools://')]
            dialog = None
            if len(tabs) > 1:
                for k, t in enumerate(tabs):
                    if t[1] == 'chrome://privacy-sandbox-dialog/notice':
                        dialog = k
                    elif not target_id:
                        target_id = t[0]

                    if target_id and dialog is not None:
                        break

                if dialog is not None:
                    close_privacy_dialog(self, tabs[dialog][0])

            else:
                target_id = tabs[0][0]

        self._driver_init(target_id)
        if self._js_ready_state == 'complete' and self._ready_state is None:
            self._get_document()
            self._ready_state = 'complete'

    def _driver_init(self, target_id):
        self._is_loading = True
        self._driver = self.browser._get_driver(target_id, self)

        self._alert = Alert(self._auto_handle_alert)
        self._driver.set_callback('Page.javascriptDialogOpening', self._on_alert_open, immediate=True)
        self._driver.set_callback('Page.javascriptDialogClosed', self._on_alert_close)

        self._driver.run('DOM.enable')
        self._driver.run('Page.enable')
        self._driver.run('Emulation.setFocusEmulationEnabled', enabled=True)

        r = self._run_cdp('Page.getFrameTree')
        for i in findall(r"'id': '(.*?)'", str(r)):
            self.browser._frames[i] = self.tab_id
        if not hasattr(self, '_frame_id'):
            self._frame_id = r['frameTree']['frame']['id']

        self._driver.set_callback('Page.frameStartedLoading', self._onFrameStartedLoading)
        self._driver.set_callback('Page.frameNavigated', self._onFrameNavigated)
        self._driver.set_callback('Page.domContentEventFired', self._onDomContentEventFired)
        self._driver.set_callback('Page.loadEventFired', self._onLoadEventFired)
        self._driver.set_callback('Page.frameStoppedLoading', self._onFrameStoppedLoading)
        self._driver.set_callback('Page.frameAttached', self._onFrameAttached)
        self._driver.set_callback('Page.frameDetached', self._onFrameDetached)

    def _get_document(self, timeout=10):
        if self._is_reading:
            return
        self._is_reading = True
        timeout = max(timeout, 2)
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            try:
                b_id = self._run_cdp('DOM.getDocument', _timeout=timeout)['root']['backendNodeId']
                timeout = end_time - perf_counter()
                timeout = 1 if timeout <= 1 else timeout
                self._root_id = self._run_cdp('DOM.resolveNode', backendNodeId=b_id,
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
                self.browser._frames[i] = self.tab_id

        self._is_loading = False
        self._is_reading = False
        return result

    def _onFrameDetached(self, **kwargs):
        self.browser._frames.pop(kwargs['frameId'], None)

    def _onFrameAttached(self, **kwargs):
        self.browser._frames[kwargs['frameId']] = self.tab_id

    def _onFrameStartedLoading(self, **kwargs):
        self.browser._frames[kwargs['frameId']] = self.tab_id
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
            if kwargs.get('type', None) == 'BackForwardCacheRestore':
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
        self.browser._frames[kwargs['frameId']] = self.tab_id
        if kwargs['frameId'] == self._frame_id:
            if self._doc_got is False:
                self._get_document(self._load_end_time - perf_counter() - .1)
            self._ready_state = 'complete'

    def _onFileChooserOpened(self, **kwargs):
        if self._upload_list:
            if 'backendNodeId' not in kwargs:
                raise RuntimeError(_S._lang.join(_S._lang.CANNOT_INPUT_FILE))
            files = self._upload_list if kwargs['mode'] == 'selectMultiple' else self._upload_list[:1]
            self._run_cdp('DOM.setFileInputFiles', files=files, backendNodeId=kwargs['backendNodeId'])

            self.driver.set_callback('Page.fileChooserOpened', None)
            self._run_cdp('Page.setInterceptFileChooserDialog', enabled=False)
            self._upload_list = None

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
        return self._run_cdp('DOM.getOuterHTML', objectId=self._root_id)['outerHTML']

    @property
    def json(self):
        try:
            return loads(self('t:pre', timeout=.5).text)
        except JSONDecodeError:
            return None

    @property
    def tab_id(self):
        return self.driver.id

    @property
    def _target_id(self):
        return self.driver.id

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
        r = self.driver.run(cmd, **cmd_args)
        return r if __ERROR__ not in r else raise_error(r, self.browser, user=True)

    def run_cdp_loaded(self, cmd, **cmd_args):
        self.wait.doc_loaded()
        r = self.driver.run(cmd, **cmd_args)
        return r if __ERROR__ not in r else raise_error(r, self.browser, user=True)

    def _run_cdp(self, cmd, **cmd_args):
        ignore = cmd_args.pop('_ignore', None)
        r = self.driver.run(cmd, **cmd_args)
        return r if __ERROR__ not in r else raise_error(r, self.browser, ignore)

    def _run_cdp_loaded(self, cmd, **cmd_args):
        self.wait.doc_loaded()
        return self._run_cdp(cmd, **cmd_args)

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

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None):
        retry, interval, is_file = self._before_connect(url, retry, interval)
        self._url_available = self._d_connect(self._url, times=retry, interval=interval,
                                              show_errmsg=show_errmsg, timeout=timeout)
        return self._url_available

    def cookies(self, all_domains=False, all_info=False):
        txt = 'Storage' if all_domains else 'Network'
        cookies = self._run_cdp_loaded(f'{txt}.getCookies')['cookies']

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
            loc = get_loc(locator)[1]
        elif locator._type in ('ChromiumElement', 'ChromiumFrame'):
            return locator
        else:
            raise LocatorError(ALLOW_TYPE=_S._lang.ELE_OR_LOC, CURR_VAL=locator)

        self.wait.doc_loaded()
        end_time = perf_counter() + timeout

        search_ids = []
        timeout = .5 if timeout <= 0 else timeout
        result = self.driver.run('DOM.performSearch', query=loc, _timeout=timeout, includeUserAgentShadowDOM=True)
        if not result or __ERROR__ in result:
            num = 0
        else:
            num = result['resultCount']
            search_ids.append(result['searchId'])

        while True:
            if num > 0:
                from_index = index_arg = 0
                if index is None:
                    end_index = num
                    index_arg = None
                elif index < 0:
                    from_index = index + num
                    end_index = from_index + 1
                else:
                    from_index = index - 1
                    end_index = from_index + 1

                if from_index <= num - 1:
                    nIds = self._driver.run('DOM.getSearchResults', searchId=result['searchId'],
                                            fromIndex=from_index, toIndex=end_index)
                    if __ERROR__ not in nIds:
                        if nIds['nodeIds'][0] != 0:
                            r = make_chromium_eles(self, _ids=nIds['nodeIds'], index=index_arg,
                                                   is_obj_id=False, ele_only=True)
                            if r is not False:
                                break

                    elif nIds[__ERROR__] == 'connection disconnected':
                        raise PageDisconnectedError

            if perf_counter() >= end_time:
                return NoneElement(self) if index is not None else ChromiumElementsList(owner=self)

            sleep(.01)
            timeout = end_time - perf_counter()
            timeout = .5 if timeout <= 0 else timeout
            result = self.driver.run('DOM.performSearch', query=loc, _timeout=timeout, includeUserAgentShadowDOM=True)
            if result and __ERROR__ not in result:
                num = result['resultCount']
                search_ids.append(result['searchId'])
            elif result and result[__ERROR__] == 'connection disconnected':
                raise PageDisconnectedError

        for _id in search_ids:
            self._driver.run('DOM.discardSearchResults', searchId=_id)

        return r

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

    def add_ele(self, html_or_info, insert_to=None, before=None):
        if isinstance(html_or_info, str):
            insert_to = self.ele(insert_to) if insert_to else self.ele('t:body')
            args = [html_or_info, insert_to]
            if before:
                args.append(self.ele(before))
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
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_VAL_, 'html_or_info', ALLOW_TYPE='html, tuple',
                                           TIP=_S._lang.NEW_ELE_INFO, CURR_VAL=html_or_info))

        try:
            ele = self._run_js(js, *args)
        except JavaScriptError:
            raise RuntimeError(_S._lang.join(_S._lang.DICT_TO_NEW_ELE))
        return ele

    def get_frame(self, loc_ind_ele, timeout=None):
        return get_frame(self, loc_ind_ele=loc_ind_ele, timeout=timeout)

    def get_frames(self, locator=None, timeout=None):
        locator = locator or 'xpath://*[name()="iframe" or name()="frame"]'
        frames = self._ele(locator, timeout=timeout, index=None, raise_err=False)
        return ChromiumElementsList(self, frames)

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
        if session_storage or local_storage:
            self._run_cdp_loaded('DOMStorage.enable')
            i = self._run_cdp('Storage.getStorageKeyForFrame', frameId=self._frame_id)['storageKey']
            if session_storage:
                self._run_cdp('DOMStorage.clear', storageId={'storageKey': i, 'isLocalStorage': False})
            if local_storage:
                self._run_cdp('DOMStorage.clear', storageId={'storageKey': i, 'isLocalStorage': True})
            self._run_cdp_loaded('DOMStorage.disable')

        if cache:
            self._run_cdp_loaded('Network.clearBrowserCache')

        if cookies:
            self._run_cdp_loaded('Network.clearBrowserCookies')

    def disconnect(self):
        if self._driver:
            self._disconnect_flag = True
            self._driver.stop()
            self.browser._all_drivers.get(self._driver.id, set()).discard(self._driver)
            self._disconnect_flag = False

    def reconnect(self, wait=0):
        t_id = self._target_id
        self.disconnect()
        sleep(wait)
        self.browser.reconnect()
        self._driver = self.browser._get_driver(t_id, self)
        self._driver_init(t_id)
        self._get_document()

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
        self.driver.run('Page.handleJavaScriptDialog', **d)
        return res_text

    def _on_alert_open(self, **kwargs):
        self._alert.activated = True
        self._alert.text = kwargs['message']
        self._alert.type = kwargs['type']
        self._alert.defaultPrompt = kwargs.get('defaultPrompt', None)
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
        if timeout is None:
            timeout = self.timeouts.page_load
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if self._ready_state == 'complete':
                return True
            elif self._load_mode == 'eager' and self._ready_state in ('interactive',
                                                                      'complete') and not self._is_loading:
                return True

            sleep(.01)

        try:
            self.stop_loading()
        except CDPError:
            pass
        return False

    def _d_connect(self, to_url, times=0, interval=1, show_errmsg=False, timeout=None):
        err = None
        self._is_loading = True
        timeout = timeout if timeout is not None else self.timeouts.page_load
        for t in range(times + 1):
            err = None
            end_time = perf_counter() + timeout
            try:
                result = self._run_cdp('Page.navigate', frameId=self._frame_id, url=to_url, _timeout=timeout)
                if 'errorText' in result:
                    err = ConnectionError(_S._lang.join(_S._lang.CONNECT_ERR, INFO=result['errorText']))
            except TimeoutError:
                err = TimeoutError(_S._lang.join(_S._lang.TIMEOUT_, _S._lang.PAGE_CONNECT, timeout))

            if err:
                if t < times:
                    sleep(interval)
                    if show_errmsg:
                        print(f'{_S._lang.RETRY}{t + 1} {to_url}')
                end_time1 = end_time - perf_counter()
                while self._ready_state not in ('loading', 'complete') and perf_counter() < end_time1:  # 等待出错信息显示
                    sleep(.01)
                self.stop_loading()
                continue

            if self._load_mode == 'none':
                return True

            yu = end_time - perf_counter()
            ok = self._wait_loaded(1 if yu <= 0 else yu)
            if not ok:
                err = TimeoutError(_S._lang.join(_S._lang.TIMEOUT_, _S._lang.PAGE_CONNECT, timeout))
                if t < times:
                    sleep(interval)
                    if show_errmsg:
                        print(f'{_S._lang.RETRY}{t + 1} {to_url}')
                continue

            if not err:
                break

        if err:
            if show_errmsg:
                raise err if err is not None else ConnectionError(_S._lang.join(_S._lang.CONNECT_ERR))
            return False

        return True

    def _get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None,
                        full_page=False, left_top=None, right_bottom=None, ele=None):
        if as_bytes:
            if as_bytes is True:
                pic_type = 'png'
            else:
                if as_bytes not in ('jpg', 'jpeg', 'png', 'webp'):
                    raise ValueError(_S._lang.join(_S._lang.INCORRECT_VAL_, 'as_bytes',
                                                   ALLOW_VAL='"jpg", "jpeg", "png", "webp"', CURR_VAL=as_bytes))
                pic_type = 'jpeg' if as_bytes == 'jpg' else as_bytes

        elif as_base64:
            if as_base64 is True:
                pic_type = 'png'
            else:
                if as_base64 not in ('jpg', 'jpeg', 'png', 'webp'):
                    raise ValueError(_S._lang.join(_S._lang.INCORRECT_VAL_, 'as_base64',
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
                raise RuntimeError(_S._lang.join(_S._lang.ZERO_PAGE_SIZE))
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
        return str(path.absolute())


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


def close_privacy_dialog(page, tid):
    """关闭隐私声明弹窗
    :param page: ChromiumBase对象
    :param tid: tab id
    :return: None
    """
    try:
        driver = page.browser._get_driver(tid)
        driver.run('Runtime.enable')
        driver.run('DOM.enable')
        driver.run('DOM.getDocument')
        sid = driver.run('DOM.performSearch', query='//*[name()="privacy-sandbox-notice-dialog-app"]',
                         includeUserAgentShadowDOM=True)['searchId']
        r = driver.run('DOM.getSearchResults', searchId=sid, fromIndex=0, toIndex=1)['nodeIds'][0]
        end_time = perf_counter() + 3
        while perf_counter() < end_time:
            try:
                r = driver.run('DOM.describeNode', nodeId=r)['node']['shadowRoots'][0]['backendNodeId']
                break
            except KeyError:
                pass
            sleep(.05)
        driver.run('DOM.discardSearchResults', searchId=sid)
        r = driver.run('DOM.resolveNode', backendNodeId=r)['object']['objectId']
        r = driver.run('Runtime.callFunctionOn', objectId=r,
                       functionDeclaration='function(){return this.getElementById("ackButton");}')['result']['objectId']
        driver.run('Runtime.callFunctionOn', objectId=r, functionDeclaration='function(){return this.click();}')
        driver.close()

    except:
        pass
