# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
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
from .._functions.locator import get_loc, is_loc
from .._functions.settings import Settings
from .._functions.tools import raise_error
from .._functions.web import location_in_viewport
from .._units.actions import Actions
from .._units.listener import Listener
from .._units.rect import TabRect
from .._units.screencast import Screencast
from .._units.scroller import PageScroller
from .._units.setter import ChromiumBaseSetter
from .._units.states import PageStates
from .._units.waiter import BaseWaiter
from ..errors import ContextLostError, CDPError, PageDisconnectedError, ElementLostError

__ERROR__ = 'error'


class ChromiumBase(BasePage):
    """标签页、frame、页面基类"""

    def __init__(self, address, tab_id=None, timeout=None):
        """
        :param address: 浏览器 ip:port
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :param timeout: 超时时间（秒）
        """
        super().__init__()
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
        self._upload_list = None
        self._doc_got = False  # 用于在LoadEventFired和FrameStoppedLoading间标记是否已获取doc
        self._download_path = None
        self._load_end_time = 0
        self._init_jss = []
        self._type = 'ChromiumBase'
        if not hasattr(self, '_listener'):
            self._listener = None

        if isinstance(address, int) or (isinstance(address, str) and address.isdigit()):
            address = f'127.0.0.1:{address}'

        self._d_set_start_options(address)
        self._d_set_runtime_settings()
        self._connect_browser(tab_id)
        if timeout is not None:
            self.timeout = timeout

    def _d_set_start_options(self, address):
        """设置浏览器启动属性
        :param address: 'ip:port'
        :return: None
        """
        self.address = address.replace('localhost', '127.0.0.1').lstrip('http://').lstrip('https://')

    def _d_set_runtime_settings(self):
        self._timeouts = Timeout(self)
        self._load_mode = 'normal'

    def _connect_browser(self, tab_id=None):
        """连接浏览器，在第一次时运行
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :return: None
        """
        self._is_reading = False

        if not tab_id:
            tabs = self.browser.driver.get(f'http://{self.address}/json').json()
            tabs = [(i['id'], i['url']) for i in tabs
                    if i['type'] in ('page', 'webview') and not i['url'].startswith('devtools://')]
            dialog = None
            if len(tabs) > 1:
                for k, t in enumerate(tabs):
                    if t[1] == 'chrome://privacy-sandbox-dialog/notice':
                        dialog = k
                    elif not tab_id:
                        tab_id = t[0]

                    if tab_id and dialog is not None:
                        break

                if dialog is not None:
                    close_privacy_dialog(self, tabs[dialog][0])

            else:
                tab_id = tabs[0][0]

        self._driver_init(tab_id)
        if self._js_ready_state == 'complete' and self._ready_state is None:
            self._get_document()
            self._ready_state = 'complete'

    def _driver_init(self, tab_id):
        """新建页面、页面刷新、切换标签页后要进行的cdp参数初始化
        :param tab_id: 要跳转到的标签页id
        :return: None
        """
        self._is_loading = True
        self._driver = self.browser._get_driver(tab_id, self)

        self._alert = Alert()
        self._driver.set_callback('Page.javascriptDialogOpening', self._on_alert_open, immediate=True)
        self._driver.set_callback('Page.javascriptDialogClosed', self._on_alert_close)

        self._driver.run('DOM.enable')
        self._driver.run('Page.enable')
        self._driver.run('Emulation.setFocusEmulationEnabled', enabled=True)

        r = self.run_cdp('Page.getFrameTree')
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
        """获取页面文档
        :param timeout: 超时时间（秒）
        :return: 是否获取成功
        """
        if self._is_reading:
            return
        self._is_reading = True
        timeout = max(timeout, 2)
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            try:
                b_id = self.run_cdp('DOM.getDocument', _timeout=timeout)['root']['backendNodeId']
                timeout = end_time - perf_counter()
                timeout = 1 if timeout <= 1 else timeout
                self._root_id = self.run_cdp('DOM.resolveNode', backendNodeId=b_id,
                                             _timeout=timeout)['object']['objectId']
                result = True
                break

            except PageDisconnectedError:
                result = False
                break
            except:
                timeout = end_time - perf_counter()
                timeout = .5 if timeout <= 0 else timeout
            sleep(.1)

        else:
            result = False

        if result:
            r = self.run_cdp('Page.getFrameTree')
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
        """页面开始加载时执行"""
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
        """页面跳转时执行"""
        if kwargs['frame']['id'] == self._frame_id:
            self._doc_got = False
            self._ready_state = 'loading'
            self._is_loading = True

    def _onDomContentEventFired(self, **kwargs):
        """在页面刷新、变化后重新读取页面内容"""
        if self._load_mode == 'eager':
            self.run_cdp('Page.stopLoading')
        if self._get_document(self._load_end_time - perf_counter() - .1):
            self._doc_got = True
        self._ready_state = 'interactive'

    def _onLoadEventFired(self, **kwargs):
        """在页面刷新、变化后重新读取页面内容"""
        if self._doc_got is False and self._get_document(self._load_end_time - perf_counter() - .1):
            self._doc_got = True
        self._ready_state = 'complete'

    def _onFrameStoppedLoading(self, **kwargs):
        """页面加载完成后执行"""
        self.browser._frames[kwargs['frameId']] = self.tab_id
        if kwargs['frameId'] == self._frame_id:
            if self._doc_got is False:
                self._get_document(self._load_end_time - perf_counter() - .1)
            self._ready_state = 'complete'

    def _onFileChooserOpened(self, **kwargs):
        """文件选择框打开时执行"""
        if self._upload_list:
            if 'backendNodeId' not in kwargs:
                raise TypeError('该输入框无法接管，请改用对<input>元素输入路径的方法设置。')
            files = self._upload_list if kwargs['mode'] == 'selectMultiple' else self._upload_list[:1]
            self.run_cdp('DOM.setFileInputFiles', files=files, backendNodeId=kwargs['backendNodeId'])

            self.driver.set_callback('Page.fileChooserOpened', None)
            self.run_cdp('Page.setInterceptFileChooserDialog', enabled=False)
            self._upload_list = None

    def __call__(self, locator, index=1, timeout=None):
        """在内部查找元素
        例：ele = page('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 超时时间（秒）
        :return: ChromiumElement对象
        """
        return self.ele(locator, index, timeout)

    def _wait_to_stop(self):
        """eager策略超时时使页面停止加载"""
        end_time = perf_counter() + self.timeouts.page_load
        while perf_counter() < end_time:
            sleep(.1)
        if self._ready_state in ('interactive', 'complete') and self._is_loading:
            self.stop_loading()

    # ----------挂件----------
    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = BaseWaiter(self)
        return self._wait

    @property
    def set(self):
        """返回用于设置的对象"""
        if self._set is None:
            self._set = ChromiumBaseSetter(self)
        return self._set

    @property
    def screencast(self):
        """返回用于录屏的对象"""
        if self._screencast is None:
            self._screencast = Screencast(self)
        return self._screencast

    @property
    def actions(self):
        """返回用于执行动作链的对象"""
        if self._actions is None:
            self._actions = Actions(self)
        self.wait.doc_loaded()
        return self._actions

    @property
    def listen(self):
        """返回用于聆听数据包的对象"""
        if self._listener is None:
            self._listener = Listener(self)
        return self._listener

    @property
    def states(self):
        """返回用于获取状态信息的对象"""
        if self._states is None:
            self._states = PageStates(self)
        return self._states

    @property
    def scroll(self):
        """返回用于滚动滚动条的对象"""
        self.wait.doc_loaded()
        if self._scroll is None:
            self._scroll = PageScroller(self)
        return self._scroll

    @property
    def rect(self):
        """返回获取窗口坐标和大小的对象"""
        # self.wait.doc_loaded()
        if self._rect is None:
            self._rect = TabRect(self)
        return self._rect

    @property
    def timeouts(self):
        """返回timeouts设置"""
        return self._timeouts

    # ----------挂件结束----------

    @property
    def browser(self):
        return self._browser

    @property
    def driver(self):
        """返回用于控制浏览器的Driver对象"""
        if self._driver is None:
            raise RuntimeError('浏览器已关闭或链接已断开。')
        return self._driver

    @property
    def title(self):
        """返回当前页面title"""
        return self.run_cdp_loaded('Target.getTargetInfo', targetId=self._target_id)['targetInfo']['title']

    @property
    def url(self):
        """返回当前页面url"""
        return self.run_cdp_loaded('Target.getTargetInfo', targetId=self._target_id)['targetInfo']['url']

    @property
    def _browser_url(self):
        """用于被WebPage覆盖"""
        return self.url

    @property
    def html(self):
        """返回当前页面html文本"""
        self.wait.doc_loaded()
        return self.run_cdp('DOM.getOuterHTML', objectId=self._root_id)['outerHTML']

    @property
    def json(self):
        """当返回内容是json格式时，返回对应的字典，非json格式时返回None"""
        try:
            return loads(self('t:pre', timeout=.5).text)
        except JSONDecodeError:
            return None

    @property
    def tab_id(self):
        """返回当前标签页id"""
        return self._target_id

    @property
    def _target_id(self):
        """返回当前标签页id"""
        return self.driver.id if not self.driver._stopped.is_set() else ''

    @property
    def active_ele(self):
        """返回当前焦点所在元素"""
        return self.run_js_loaded('return document.activeElement;')

    @property
    def load_mode(self):
        """返回页面加载策略，有3种：'none'、'normal'、'eager'"""
        return self._load_mode

    @property
    def user_agent(self):
        """返回user agent"""
        return self.run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']

    @property
    def upload_list(self):
        """返回等待上传文件列表"""
        return self._upload_list

    @property
    def _js_ready_state(self):
        """返回js获取的ready state信息"""
        try:
            return self.run_cdp('Runtime.evaluate', expression='document.readyState;', _timeout=3)['result']['value']
        except ContextLostError:
            return None
        except TimeoutError:
            return 'timeout'

    def run_cdp(self, cmd, **cmd_args):
        """执行Chrome DevTools Protocol语句
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        ignore = cmd_args.pop('_ignore', None)
        r = self.driver.run(cmd, **cmd_args)
        return r if __ERROR__ not in r else raise_error(r, ignore)

    def run_cdp_loaded(self, cmd, **cmd_args):
        """执行Chrome DevTools Protocol语句，执行前等待页面加载完毕
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        self.wait.doc_loaded()
        return self.run_cdp(cmd, **cmd_args)

    def run_js(self, script, *args, as_expr=False, timeout=None):
        """运行javascript代码
        :param script: js文本或js文件路径
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        return run_js(self, script, as_expr, self.timeouts.script if timeout is None else timeout, args)

    def run_js_loaded(self, script, *args, as_expr=False, timeout=None):
        """运行javascript代码，执行前等待页面加载完毕
        :param script: js文本或js文件路径
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script属性值
        :return: 运行的结果
        """
        self.wait.doc_loaded()
        return run_js(self, script, as_expr, self.timeouts.script if timeout is None else timeout, args)

    def run_async_js(self, script, *args, as_expr=False):
        """以异步方式执行js代码或js文件路径
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: None
        """
        run_js(self, script, as_expr, 0, args)

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None):
        """访问url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param timeout: 连接超时时间（秒），为None时使用页面对象timeouts.page_load属性值
        :return: 目标url是否可用
        """
        retry, interval, is_file = self._before_connect(url, retry, interval)
        self._url_available = self._d_connect(self._url, times=retry, interval=interval,
                                              show_errmsg=show_errmsg, timeout=timeout)
        return self._url_available

    def cookies(self, as_dict=False, all_domains=False, all_info=False):
        """返回cookies信息
        :param as_dict: 为True时以dict格式返回且all_info无效，为False时返回list
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，为False时只返回name、value、domain
        :return: cookies信息
        """
        txt = 'Storage' if all_domains else 'Network'
        cookies = self.run_cdp_loaded(f'{txt}.getCookies')['cookies']

        if as_dict:
            return {cookie['name']: cookie['value'] for cookie in cookies}
        elif all_info:
            return cookies
        else:
            return [{'name': cookie['name'], 'value': cookie['value'], 'domain': cookie['domain']}
                    for cookie in cookies]

    def ele(self, locator, index=1, timeout=None):
        """获取一个符合条件的元素对象
        :param locator: 定位符或元素对象
        :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找超时时间（秒）
        :return: ChromiumElement对象
        """
        return self._ele(locator, timeout=timeout, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        """获取所有符合条件的元素对象
        :param locator: 定位符或元素对象
        :param timeout: 查找超时时间（秒）
        :return: ChromiumElement对象组成的列表
        """
        return self._ele(locator, timeout=timeout, index=None)

    def s_ele(self, locator=None, index=1):
        """查找一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, locator, index=index, method='s_ele()')

    def s_eles(self, locator):
        """查找所有符合条件的元素以SessionElement列表形式返回
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象组成的列表
        """
        return make_session_ele(self, locator, index=None)

    def _find_elements(self, locator, timeout=None, index=1, relative=False, raise_err=None):
        """执行元素查找
        :param locator: 定位符或元素对象
        :param timeout: 查找超时时间（秒）
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或元素对象组成的列表
        """
        if isinstance(locator, (str, tuple)):
            loc = get_loc(locator)[1]
        elif locator._type in ('ChromiumElement', 'ChromiumFrame'):
            return locator
        else:
            raise ValueError('locator参数只能是tuple、str、ChromiumElement类型。')

        self.wait.doc_loaded()
        timeout = timeout if timeout is not None else self.timeout
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
                return NoneElement(self) if index is not None else []

            sleep(.1)
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
        """刷新当前页面
        :param ignore_cache: 是否忽略缓存
        :return: None
        """
        self._is_loading = True
        self.run_cdp('Page.reload', ignoreCache=ignore_cache)
        self.wait.load_start()

    def forward(self, steps=1):
        """在浏览历史中前进若干步
        :param steps: 前进步数
        :return: None
        """
        self._forward_or_back(steps)

    def back(self, steps=1):
        """在浏览历史中后退若干步
        :param steps: 后退步数
        :return: None
        """
        self._forward_or_back(-steps)

    def _forward_or_back(self, steps):
        """执行浏览器前进或后退，会跳过url相同的历史记录
        :param steps: 步数
        :return: None
        """
        if steps == 0:
            return

        history = self.run_cdp('Page.getNavigationHistory')
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
            self.run_cdp('Page.navigateToHistoryEntry', entryId=nid)

    def stop_loading(self):
        """页面停止加载"""
        try:
            self.run_cdp('Page.stopLoading')
            end_time = perf_counter() + 5
            while self._ready_state != 'complete' and perf_counter() < end_time:
                sleep(.1)
        except (PageDisconnectedError, CDPError):
            pass
        finally:
            self._ready_state = 'complete'

    def remove_ele(self, loc_or_ele):
        """从页面上删除一个元素
        :param loc_or_ele: 元素对象或定位符
        :return: None
        """
        if not loc_or_ele:
            return
        ele = self._ele(loc_or_ele, raise_err=False)
        if ele:
            self.run_cdp('DOM.removeNode', nodeId=ele._node_id, _ignore=ElementLostError)

    def add_ele(self, html_or_info, insert_to=None, before=None):
        """新建一个元素
        :param html_or_info: 新元素的html文本或信息。信息格式为：(tag, {attr1: value, ...})
        :param insert_to: 插入到哪个元素中，可接收元素对象和定位符，为None且为html添加到body，不为html不插入
        :param before: 在哪个子节点前面插入，可接收对象和定位符，为None插入到父元素末尾
        :return: 元素对象
        """
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
            raise TypeError('html_or_info参数必须是html文本或tuple，tuple格式为(tag, {name: value})。')

        ele = self.run_js(js, *args)
        return ele

    def get_frame(self, loc_ind_ele, timeout=None):
        """获取页面中一个frame对象
        :param loc_ind_ele: 定位符、iframe序号、ChromiumFrame对象，序号从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒）
        :return: ChromiumFrame对象
        """
        if isinstance(loc_ind_ele, str):
            if not is_loc(loc_ind_ele):
                xpath = f'xpath://*[(name()="iframe" or name()="frame") and ' \
                        f'(@name="{loc_ind_ele}" or @id="{loc_ind_ele}")]'
            else:
                xpath = loc_ind_ele
            ele = self._ele(xpath, timeout=timeout)
            if ele and ele._type != 'ChromiumFrame':
                raise TypeError('该定位符不是指向frame元素。')
            r = ele

        elif isinstance(loc_ind_ele, tuple):
            ele = self._ele(loc_ind_ele, timeout=timeout)
            if ele and ele._type != 'ChromiumFrame':
                raise TypeError('该定位符不是指向frame元素。')
            r = ele

        elif isinstance(loc_ind_ele, int):
            if loc_ind_ele == 0:
                loc_ind_ele = 1
            elif loc_ind_ele < 0:
                loc_ind_ele = f'last()+{loc_ind_ele}+1'
            xpath = f'xpath:(//*[name()="frame" or name()="iframe"])[{loc_ind_ele}]'
            r = self._ele(xpath, timeout=timeout)

        elif loc_ind_ele._type == 'ChromiumFrame':
            r = loc_ind_ele

        else:
            raise TypeError('必须传入定位符、iframe序号、id、name、ChromiumFrame对象其中之一。')

        if isinstance(r, NoneElement):
            r.method = 'get_frame()'
            r.args = {'loc_ind_ele': loc_ind_ele}
        return r

    def get_frames(self, locator=None, timeout=None):
        """获取所有符合条件的frame对象
        :param locator: 定位符，为None时返回所有
        :param timeout: 查找超时时间（秒）
        :return: ChromiumFrame对象组成的列表
        """
        locator = locator or 'xpath://*[name()="iframe" or name()="frame"]'
        frames = self._ele(locator, timeout=timeout, index=None, raise_err=False)
        return [i for i in frames if i._type == 'ChromiumFrame']

    def session_storage(self, item=None):
        """返回sessionStorage信息，不设置item则获取全部
        :param item: 要获取的项，不设置则返回全部
        :return: sessionStorage一个或所有项内容
        """
        js = f'sessionStorage.getItem("{item}")' if item else 'sessionStorage'
        return self.run_js_loaded(js, as_expr=True)

    def local_storage(self, item=None):
        """返回localStorage信息，不设置item则获取全部
        :param item: 要获取的项目，不设置则返回全部
        :return: localStorage一个或所有项内容
        """
        js = f'localStorage.getItem("{item}")' if item else 'localStorage'
        return self.run_js_loaded(js, as_expr=True)

    def get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None,
                       full_page=False, left_top=None, right_bottom=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :return: 图片完整路径或字节文本
        """
        return self._get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                    full_page=full_page, left_top=left_top, right_bottom=right_bottom)

    def add_init_js(self, script):
        """添加初始化脚本，在页面加载任何脚本前执行
        :param script: js文本
        :return: 添加的脚本的id
        """
        js_id = self.run_cdp('Page.addScriptToEvaluateOnNewDocument', source=script,
                             includeCommandLineAPI=True)['identifier']
        self._init_jss.append(js_id)
        return js_id

    def remove_init_js(self, script_id=None):
        """删除初始化脚本，js_id传入None时删除所有
        :param script_id: 脚本的id
        :return: None
        """
        if script_id is None:
            for js_id in self._init_jss:
                self.run_cdp('Page.removeScriptToEvaluateOnNewDocument', identifier=js_id)
            self._init_jss.clear()

        elif script_id in self._init_jss:
            self.run_cdp('Page.removeScriptToEvaluateOnNewDocument', identifier=script_id)
            self._init_jss.remove(script_id)

    def clear_cache(self, session_storage=True, local_storage=True, cache=True, cookies=True):
        """清除缓存，可选要清除的项
        :param session_storage: 是否清除sessionStorage
        :param local_storage: 是否清除localStorage
        :param cache: 是否清除cache
        :param cookies: 是否清除cookies
        :return: None
        """
        if session_storage or local_storage:
            self.run_cdp_loaded('DOMStorage.enable')
            i = self.run_cdp('Storage.getStorageKeyForFrame', frameId=self._frame_id)['storageKey']
            if session_storage:
                self.run_cdp('DOMStorage.clear', storageId={'storageKey': i, 'isLocalStorage': False})
            if local_storage:
                self.run_cdp('DOMStorage.clear', storageId={'storageKey': i, 'isLocalStorage': True})
            self.run_cdp_loaded('DOMStorage.disable')

        if cache:
            self.run_cdp_loaded('Network.clearBrowserCache')

        if cookies:
            self.run_cdp_loaded('Network.clearBrowserCookies')

    def disconnect(self):
        """断开与页面的连接，不关闭页面"""
        if self._driver:
            self.browser.stop_driver(self._driver)

    def reconnect(self, wait=0):
        """断开与页面原来的页面，重新建立连接
        :param wait: 断开后等待若干秒再连接
        :return: None
        """
        t_id = self._target_id
        self.disconnect()
        sleep(wait)
        self.browser.reconnect()
        self._driver = self.browser._get_driver(t_id, self)
        self._driver_init(t_id)
        self._get_document()

    def handle_alert(self, accept=True, send=None, timeout=None, next_one=False):
        """处理提示框，可以自动等待提示框出现
        :param accept: True表示确认，False表示取消，为None不会按按钮但依然返回文本值
        :param send: 处理prompt提示框时可输入文本
        :param timeout: 等待提示框出现的超时时间（秒），为None则使用self.timeout属性的值
        :param next_one: 是否处理下一个出现的提示框，为True时timeout参数无效
        :return: 提示框内容文本，未等到提示框则返回False
        """
        r = self._handle_alert(accept=accept, send=send, timeout=timeout, next_one=next_one)
        if not isinstance(accept, bool):
            return r
        while self._has_alert:
            sleep(.1)
        return r

    def _handle_alert(self, accept=True, send=None, timeout=None, next_one=False):
        """处理提示框，可以自动等待提示框出现
        :param accept: True表示确认，False表示取消，其它值不会按按钮但依然返回文本值
        :param send: 处理prompt提示框时可输入文本
        :param timeout: 等待提示框出现的超时时间（秒），为None则使用self.timeout属性的值
        :param next_one: 是否处理下一个出现的提示框，为True时timeout参数无效
        :return: 提示框内容文本，未等到提示框则返回False
        """
        if next_one:
            self._alert.handle_next = accept
            self._alert.next_text = send
            return

        timeout = self.timeout if timeout is None else timeout
        timeout = .1 if timeout <= 0 else timeout
        end_time = perf_counter() + timeout
        while not self._alert.activated and perf_counter() < end_time:
            sleep(.1)
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
        """alert出现时触发的方法"""
        self._alert.activated = True
        self._alert.text = kwargs['message']
        self._alert.type = kwargs['type']
        self._alert.defaultPrompt = kwargs.get('defaultPrompt', None)
        self._alert.response_accept = None
        self._alert.response_text = None
        self._has_alert = True

        if self._alert.auto is not None:
            self._handle_alert(self._alert.auto)
        elif Settings.auto_handle_alert is not None:
            self._handle_alert(Settings.auto_handle_alert)
        elif self._alert.handle_next is not None:
            self._handle_alert(self._alert.handle_next, self._alert.next_text)
            self._alert.handle_next = None

    def _on_alert_close(self, **kwargs):
        """alert关闭时触发的方法"""
        self._alert.activated = False
        self._alert.text = None
        self._alert.type = None
        self._alert.defaultPrompt = None
        self._alert.response_accept = kwargs.get('result')
        self._alert.response_text = kwargs['userInput']
        self._has_alert = False

    def _wait_loaded(self, timeout=None):
        """等待页面加载完成，超时触发停止加载
        :param timeout: 超时时间（秒）
        :return: 是否成功，超时返回False
        """
        timeout = timeout if timeout is not None else self.timeouts.page_load
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if self._ready_state == 'complete':
                return True
            elif self._load_mode == 'eager' and self._ready_state in ('interactive',
                                                                      'complete') and not self._is_loading:
                return True

            sleep(.1)

        try:
            self.stop_loading()
        except CDPError:
            pass
        return False

    def _d_connect(self, to_url, times=0, interval=1, show_errmsg=False, timeout=None):
        """尝试连接，重试若干次
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :param timeout: 连接超时时间（秒）
        :return: 是否成功，返回None表示不确定
        """
        err = None
        self._is_loading = True
        timeout = timeout if timeout is not None else self.timeouts.page_load
        for t in range(times + 1):
            err = None
            end_time = perf_counter() + timeout
            try:
                result = self.run_cdp('Page.navigate', frameId=self._frame_id, url=to_url, _timeout=timeout)
                if 'errorText' in result:
                    err = ConnectionError(result['errorText'])
            except TimeoutError:
                err = TimeoutError(f'页面连接超时（等待{timeout}秒）。')

            if err:
                if t < times:
                    sleep(interval)
                    if show_errmsg:
                        print(f'重试{t + 1} {to_url}')
                end_time1 = end_time - perf_counter()
                while self._ready_state not in ('loading', 'complete') and perf_counter() < end_time1:  # 等待出错信息显示
                    sleep(.1)
                self.stop_loading()
                continue

            if self._load_mode == 'none':
                return True

            yu = end_time - perf_counter()
            ok = self._wait_loaded(1 if yu <= 0 else yu)
            if not ok:
                err = TimeoutError(f'页面连接超时（等待{timeout}秒）。')
                if t < times:
                    sleep(interval)
                    if show_errmsg:
                        print(f'重试{t + 1} {to_url}')
                continue

            if not err:
                break

        if err:
            if show_errmsg:
                raise err if err is not None else ConnectionError('连接异常。')
            return False

        return True

    def _get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None,
                        full_page=False, left_top=None, right_bottom=None, ele=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :param ele: 为异域iframe内元素截图设置
        :return: 图片完整路径或字节文本
        """
        if as_bytes:
            if as_bytes is True:
                pic_type = 'png'
            else:
                if as_bytes not in ('jpg', 'jpeg', 'png', 'webp'):
                    raise TypeError("只能接收 'jpg', 'jpeg', 'png', 'webp' 四种格式。")
                pic_type = 'jpeg' if as_bytes == 'jpg' else as_bytes

        elif as_base64:
            if as_base64 is True:
                pic_type = 'png'
            else:
                if as_base64 not in ('jpg', 'jpeg', 'png', 'webp'):
                    raise TypeError("只能接收 'jpg', 'jpeg', 'png', 'webp' 四种格式。")
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
                raise RuntimeError('页面大小为0，请尝试等待页面加载完成。')
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
                if v and (self.run_js('return document.body.scrollHeight > window.innerHeight;') and
                          not self.run_js('return document.body.scrollWidth > window.innerWidth;')):
                    x += 10

                vp = {'x': x, 'y': y, 'width': w, 'height': h, 'scale': 1}
                args = {'format': pic_type, 'captureBeyondViewport': v, 'clip': vp}

            else:
                args = {'format': pic_type}

        if pic_type == 'jpeg':
            args['quality'] = 100
        png = self.run_cdp_loaded('Page.captureScreenshot', **args)['data']

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
    """用于保存d模式timeout信息的类"""

    def __init__(self, page, base=None, page_load=None, script=None, implicit=None):
        """
        :param page: ChromiumBase页面
        :param base: 默认超时时间
        :param page_load: 页面加载超时时间
        :param script: js超时时间
        """
        self._page = page
        base = base if base is not None else implicit
        self.base = 10 if base is None else base
        self.page_load = 30 if page_load is None else page_load
        self.script = 30 if script is None else script

    def __repr__(self):
        return str({'base': self.base, 'page_load': self.page_load, 'script': self.script})


class Alert(object):
    """用于保存alert信息的类"""

    def __init__(self):
        self.activated = False
        self.text = None
        self.type = None
        self.defaultPrompt = None
        self.response_accept = None
        self.response_text = None
        self.handle_next = None
        self.next_text = None
        self.auto = None


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
