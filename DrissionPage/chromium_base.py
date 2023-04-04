# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from base64 import b64decode
from json import loads, JSONDecodeError
from os import sep
from pathlib import Path
from re import search
from threading import Thread
from time import perf_counter, sleep, time
from warnings import warn

from FlowViewer.listener import ResponseData
from requests import Session

from .base import BasePage
from .chromium_driver import ChromiumDriver
from .chromium_element import ChromiumScroll, ChromiumElement, run_js, make_chromium_ele
from .commons.constants import HANDLE_ALERT_METHOD, ERROR, NoneElement
from .commons.locator import get_loc
from .commons.tools import get_usable_path, clean_folder
from .commons.web import set_browser_cookies
from .errors import ContextLossError, ElementLossError, AlertExistsError, CallMethodError, TabClosedError, \
    NoRectError, BrowserConnectError
from .session_element import make_session_ele


class ChromiumBase(BasePage):
    """标签页、frame、页面基类"""

    def __init__(self, address, tab_id=None, timeout=None):
        """
        :param address: 浏览器 ip:port
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :param timeout: 超时时间
        """
        self._is_loading = None
        self._root_id = None  # object id
        self._debug = False
        self._debug_recorder = None
        self._tab_obj = None
        self._set = None
        self._screencast = None

        if isinstance(address, int) or (isinstance(address, str) and address.isdigit()):
            address = f'127.0.0.1:{address}'

        self._set_start_options(address, None)
        self._set_runtime_settings()
        self._connect_browser(tab_id)
        timeout = timeout if timeout is not None else self.timeouts.implicit
        super().__init__(timeout)

    def _set_start_options(self, address, none):
        """设置浏览器启动属性
        :param address: 'ip:port'
        :param none: 用于后代继承
        :return: None
        """
        self.address = address.replace('localhost', '127.0.0.1').lstrip('http://').lstrip('https://')

    def _set_runtime_settings(self):
        self._timeouts = Timeout(self)
        self._page_load_strategy = 'normal'

    def _connect_browser(self, tab_id=None):
        """连接浏览器，在第一次时运行
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :return: None
        """
        self._chromium_init()
        if not tab_id:
            json = self._control_session.get(f'http://{self.address}/json').json()
            tab_id = [i['id'] for i in json if i['type'] == 'page']
            if not tab_id:
                raise BrowserConnectError('浏览器连接失败，可能是浏览器版本原因。')
            tab_id = tab_id[0]
        self._driver_init(tab_id)
        self._get_document()
        self._first_run = False

    def _chromium_init(self):
        """浏览器初始设置"""
        self._control_session = Session()
        self._control_session.keep_alive = False
        self._first_run = True
        self._is_reading = False
        self._upload_list = None
        self._wait = None
        self._scroll = None

    def _driver_init(self, tab_id):
        """新建页面、页面刷新、切换标签页后要进行的cdp参数初始化
        :param tab_id: 要跳转到的标签页id
        :return: None
        """
        self._is_loading = True
        self._tab_obj = ChromiumDriver(tab_id=tab_id, tab_type='page', address=self.address)

        self._tab_obj.start()
        self._tab_obj.DOM.enable()
        self._tab_obj.Page.enable()

        self._tab_obj.Page.frameStoppedLoading = self._onFrameStoppedLoading
        self._tab_obj.Page.frameStartedLoading = self._onFrameStartedLoading
        self._tab_obj.DOM.documentUpdated = self._onDocumentUpdated
        self._tab_obj.Page.loadEventFired = self._onLoadEventFired
        self._tab_obj.Page.frameNavigated = self._onFrameNavigated

    def _get_document(self):
        """刷新cdp使用的document数据"""
        if not self._is_reading:
            self._is_reading = True

            if self._debug:
                print('获取document')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '获取document', '开始'))

            try:  # 遇到过网站在标签页关闭时触发读取文档导致错误，屏蔽掉
                self._wait_loaded()
            except TabClosedError:
                return

            end_time = perf_counter() + 10
            while perf_counter() < end_time:
                try:
                    b_id = self.run_cdp('DOM.getDocument')['root']['backendNodeId']
                    self._root_id = self.run_cdp('DOM.resolveNode', backendNodeId=b_id)['object']['objectId']
                    if self._debug_recorder:
                        self._debug_recorder.add_data((perf_counter(), '信息', f'root_id：{self._root_id}'))
                    break

                except Exception:
                    if self._debug:
                        print('重试获取document')
                        if self._debug_recorder:
                            self._debug_recorder.add_data((perf_counter(), 'err', '读取root_id出错'))

                    sleep(.1)

            else:
                raise RuntimeError('获取document失败。')

            if self._debug:
                print('获取document结束')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '获取document', '结束'))

            self._is_loading = False
            self._is_reading = False

    def _wait_loaded(self, timeout=None):
        """等待页面加载完成
        :param timeout: 超时时间
        :return: 是否成功，超时返回False
        """
        timeout = timeout if timeout is not None else self.timeouts.page_load

        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            state = self.ready_state
            if state is None:  # 存在alert的情况
                return None

            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), 'waiting', state))

            if state == 'complete':
                return True
            elif self.page_load_strategy == 'eager' and state in ('interactive', 'complete'):
                self.stop_loading()
                return True
            elif self.page_load_strategy == 'none':
                self.stop_loading()
                return True
            sleep(.1)

        self.stop_loading()
        return False

    def _onFrameStartedLoading(self, **kwargs):
        """页面开始加载时触发"""
        if kwargs['frameId'] == self.tab_id:
            self._is_loading = True

            if self._debug:
                print('页面开始加载 FrameStartedLoading')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '加载流程', 'FrameStartedLoading'))

    def _onFrameStoppedLoading(self, **kwargs):
        """页面加载完成后触发"""
        if kwargs['frameId'] == self.tab_id and self._first_run is False and self._is_loading:
            if self._debug:
                print('页面停止加载 FrameStoppedLoading')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '加载流程', 'FrameStoppedLoading'))

            self._get_document()

    def _onLoadEventFired(self, **kwargs):
        """在页面刷新、变化后重新读取页面内容"""
        if self._debug:
            print('loadEventFired')
            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), '加载流程', 'loadEventFired'))

        self._get_document()

    def _onDocumentUpdated(self, **kwargs):
        """页面跳转时触发"""
        if self._debug:
            print('documentUpdated')
            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), '加载流程', 'documentUpdated'))

    def _onFrameNavigated(self, **kwargs):
        """页面跳转时触发"""
        if kwargs['frame'].get('parentId', None) == self.tab_id and self._first_run is False and self._is_loading:
            self._is_loading = True
            if self._debug:
                print('navigated')
                if self._debug_recorder:
                    self._debug_recorder.add_data((perf_counter(), '加载流程', 'navigated'))

    def _onFileChooserOpened(self, **kwargs):
        """文件选择框打开时触发"""
        if self._upload_list:
            files = self._upload_list if kwargs['mode'] == 'selectMultiple' else self._upload_list[:1]
            self.run_cdp('DOM.setFileInputFiles', files=files, backendNodeId=kwargs['backendNodeId'])

            self.driver.Page.fileChooserOpened = None
            self.run_cdp('Page.setInterceptFileChooserDialog', enabled=False)
            self._upload_list = None

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele = page('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: ChromiumElement对象
        """
        return self.ele(loc_or_str, timeout)

    @property
    def driver(self):
        """返回用于控制浏览器的ChromiumDriver对象"""
        if self._tab_obj is None:
            raise RuntimeError('浏览器已关闭或链接已断开。')
        return self._tab_obj

    @property
    def is_loading(self):
        """返回页面是否正在加载状态"""
        return self._is_loading

    @property
    def is_alive(self):
        """返回页面对象是否仍然可用"""
        try:
            self.run_cdp('Page.getLayoutMetrics')
            return True
        except TabClosedError:
            return False

    @property
    def title(self):
        """返回当前页面title"""
        return self.run_cdp_loaded('Target.getTargetInfo', targetId=self.tab_id)['targetInfo']['title']

    @property
    def url(self):
        """返回当前页面url"""
        return self.run_cdp_loaded('Target.getTargetInfo', targetId=self.tab_id)['targetInfo']['url']

    @property
    def _browser_url(self):
        """用于被WebPage覆盖"""
        return self.url

    @property
    def html(self):
        """返回当前页面html文本"""
        return self.run_cdp_loaded('DOM.getOuterHTML', objectId=self._root_id)['outerHTML']

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
        return self.driver.id if self.driver.status == 'started' else ''

    @property
    def ready_state(self):
        """返回当前页面加载状态，'loading' 'interactive' 'complete'，有弹出框时返回None"""
        try:
            return self.run_cdp('Runtime.evaluate', expression='document.readyState;')['result']['value']
        except (AlertExistsError, TypeError):
            return None

    @property
    def size(self):
        """返回页面总宽高，格式：(宽, 高)"""
        r = self.run_cdp_loaded('Page.getLayoutMetrics')['contentSize']
        return r['width'], r['height']

    @property
    def active_ele(self):
        """返回当前焦点所在元素"""
        return self.run_js_loaded('return document.activeElement;')

    @property
    def page_load_strategy(self):
        """返回页面加载策略，有3种：'none'、'normal'、'eager'"""
        return self._page_load_strategy

    @property
    def scroll(self):
        """返回用于滚动滚动条的对象"""
        self.wait.load_complete()
        if self._scroll is None:
            self._scroll = ChromiumPageScroll(self)
        return self._scroll

    @property
    def timeouts(self):
        """返回timeouts设置"""
        return self._timeouts

    @property
    def upload_list(self):
        """返回等待上传文件列表"""
        return self._upload_list

    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = ChromiumBaseWaiter(self)
        return self._wait

    @property
    def set(self):
        """返回用于等待的对象"""
        if self._set is None:
            self._set = ChromiumBaseSetter(self)
        return self._set

    @property
    def screencast(self):
        """返回用于录屏的对象"""
        if self._screencast is None:
            self._screencast = Screencast(self)
        return self._screencast

    def run_cdp(self, cmd, **cmd_args):
        """执行Chrome DevTools Protocol语句
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        if self.driver.has_alert and cmd != HANDLE_ALERT_METHOD:
            raise AlertExistsError

        r = self.driver.call_method(cmd, **cmd_args)
        if ERROR not in r:
            return r

        error = r[ERROR]
        if error == 'Cannot find context with specified id':
            raise ContextLossError
        elif error in ('Could not find node with given id', 'Could not find object with given id',
                       'No node with given id found', 'Node with given id does not belong to the document'):
            raise ElementLossError
        elif error == 'tab closed':
            raise TabClosedError
        elif error == 'alert exists':
            pass
        elif error in ('Node does not have a layout object', 'Could not compute box model.'):
            raise NoRectError
        elif r['type'] == 'call_method_error':
            raise CallMethodError(f'\n错误：{r["error"]}\nmethod：{r["method"]}\nargs：{r["args"]}')
        else:
            raise RuntimeError(r)

    def run_cdp_loaded(self, cmd, **cmd_args):
        """执行Chrome DevTools Protocol语句，执行前等待页面加载完毕
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        self.wait.load_complete()
        return self.run_cdp(cmd, **cmd_args)

    def run_js(self, script, *args, as_expr=False):
        """运行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: 运行的结果
        """
        return run_js(self, script, as_expr, self.timeouts.script, args)

    def run_js_loaded(self, script, *args, as_expr=False):
        """运行javascript代码，执行前等待页面加载完毕
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: 运行的结果
        """
        self.wait.load_complete()
        return run_js(self, script, as_expr, self.timeouts.script, args)

    def run_async_js(self, script, *args, as_expr=False):
        """以异步方式执行js代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: None
        """
        from threading import Thread
        Thread(target=run_js, args=(self, script, as_expr, self.timeouts.script, args)).start()

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None):
        """访问url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param timeout: 连接超时时间
        :return: 目标url是否可用
        """
        retry, interval = self._before_connect(url, retry, interval)
        self._url_available = self._d_connect(self._url,
                                              times=retry,
                                              interval=interval,
                                              show_errmsg=show_errmsg,
                                              timeout=timeout)
        return self._url_available

    def get_cookies(self, as_dict=False, all_domains=False, all_info=False):
        """获取cookies信息
        :param as_dict: 为True时返回由{name: value}键值对组成的dict，为True时返回list且all_info无效
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

    def ele(self, loc_or_ele, timeout=None):
        """获取第一个符合条件的元素对象
        :param loc_or_ele: 定位符或元素对象
        :param timeout: 查找超时时间
        :return: ChromiumElement对象
        """
        return self._ele(loc_or_ele, timeout=timeout)

    def eles(self, loc_or_str, timeout=None):
        """获取所有符合条件的元素对象
        :param loc_or_str: 定位符或元素对象
        :param timeout: 查找超时时间
        :return: ChromiumElement对象组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_ele=None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_ele)

    def s_eles(self, loc_or_str):
        """查找所有符合条件的元素以SessionElement列表形式返回
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象组成的列表
        """
        return make_session_ele(self, loc_or_str, single=False)

    def _find_elements(self, loc_or_ele, timeout=None, single=True, relative=False, raise_err=None):
        """执行元素查找
        :param loc_or_ele: 定位符或元素对象
        :param timeout: 查找超时时间
        :param single: 是否只返回第一个
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或元素对象组成的列表
        """
        if isinstance(loc_or_ele, (str, tuple)):
            loc = get_loc(loc_or_ele)[1]
        elif isinstance(loc_or_ele, ChromiumElement) or str(type(loc_or_ele)).endswith(".ChromiumFrame'>"):
            return loc_or_ele
        else:
            raise ValueError('loc_or_str参数只能是tuple、str、ChromiumElement类型。')

        ok = False
        nodeIds = None

        timeout = timeout if timeout is not None else self.timeout
        end_time = perf_counter() + timeout

        try:
            search_result = self.run_cdp_loaded('DOM.performSearch', query=loc, includeUserAgentShadowDOM=True)
            count = search_result['resultCount']
        except ContextLossError:
            search_result = None
            count = 0

        while True:
            if count > 0:
                count = 1 if single else count
                try:
                    nodeIds = self.run_cdp_loaded('DOM.getSearchResults', searchId=search_result['searchId'],
                                                  fromIndex=0, toIndex=count)
                    if nodeIds['nodeIds'][0] != 0:
                        ok = True

                except Exception:
                    pass

            if ok:
                try:
                    if single:
                        return make_chromium_ele(self, node_id=nodeIds['nodeIds'][0])
                    else:
                        return [make_chromium_ele(self, node_id=i) for i in nodeIds['nodeIds']]

                except ElementLossError:
                    ok = False

            try:
                search_result = self.run_cdp_loaded('DOM.performSearch', query=loc, includeUserAgentShadowDOM=True)
                count = search_result['resultCount']
            except ContextLossError:
                pass

            if perf_counter() >= end_time:
                return NoneElement() if single else []

            sleep(.1)

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
        curr_url = history[index]['userTypedURL']
        nid = None
        for num in range(abs(steps)):
            for i in history[index::direction]:
                index += direction
                if i['userTypedURL'] != curr_url:
                    nid = i['id']
                    curr_url = i['userTypedURL']
                    break

        if nid:
            self._is_loading = True
            self.run_cdp('Page.navigateToHistoryEntry', entryId=nid)

    def stop_loading(self):
        """页面停止加载"""
        if self._debug:
            print('停止页面加载')
            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), '操作', '停止页面加载'))

        self.run_cdp('Page.stopLoading')
        while self.ready_state not in ('complete', None):
            sleep(.1)

    def remove_ele(self, loc_or_ele):
        """从页面上删除一个元素
        :param loc_or_ele: 元素对象或定位符
        :return: None
        """
        if not loc_or_ele:
            return
        ele = self._ele(loc_or_ele, raise_err=False)
        if ele:
            self.run_cdp('DOM.removeNode', nodeId=ele.ids.node_id)

    def get_frame(self, loc_ind_ele, timeout=None):
        """获取页面中一个frame对象，可传入定位符、iframe序号、ChromiumFrame对象，序号从1开始
        :param loc_ind_ele: 定位符、iframe序号、ChromiumFrame对象
        :param timeout: 查找元素超时时间
        :return: ChromiumFrame对象
        """
        if isinstance(loc_ind_ele, str):
            if not loc_ind_ele.startswith(('.', '#', '@', 't:', 't=', 'tag:', 'tag=', 'tx:', 'tx=', 'tx^', 'tx$',
                                           'text:', 'text=', 'text^', 'text$', 'xpath:', 'xpath=', 'x:', 'x=', 'css:',
                                           'css=', 'c:', 'c=')):
                loc_ind_ele = f'xpath://*[(name()="iframe" or name()="frame") and ' \
                              f'(@name="{loc_ind_ele}" or @id="{loc_ind_ele}")]'
            ele = self._ele(loc_ind_ele, timeout=timeout)
            if ele and not str(type(ele)).endswith(".ChromiumFrame'>"):
                raise TypeError('该定位符不是指向frame元素。')
            return ele

        elif isinstance(loc_ind_ele, tuple):
            ele = self._ele(loc_ind_ele, timeout=timeout)
            if ele and not str(type(ele)).endswith(".ChromiumFrame'>"):
                raise TypeError('该定位符不是指向frame元素。')
            return ele

        elif isinstance(loc_ind_ele, int):
            if loc_ind_ele < 1:
                raise ValueError('序号必须大于0。')
            xpath = f'xpath:(//*[name()="frame" or name()="iframe"])[{loc_ind_ele}]'
            return self._ele(xpath, timeout=timeout)

        elif str(type(loc_ind_ele)).endswith(".ChromiumFrame'>"):
            return loc_ind_ele

        else:
            raise TypeError('必须传入定位符、iframe序号、id、name、ChromiumFrame对象其中之一。')

    def get_frames(self, loc=None, timeout=None):
        """获取所有符号条件的frame对象
        :param loc: 定位符，为None时返回所有
        :param timeout: 查找超时时间
        :return: ChromiumFrame对象组成的列表
        """
        loc = loc or 'xpath://*[name()="iframe" or name()="frame"]'
        frames = self._ele(loc, timeout=timeout, single=False, raise_err=False)
        return [i for i in frames if str(type(i)).endswith(".ChromiumFrame'>")]

    def get_session_storage(self, item=None):
        """获取sessionStorage信息，不设置item则获取全部
        :param item: 要获取的项，不设置则返回全部
        :return: sessionStorage一个或所有项内容
        """
        if item:
            js = f'sessionStorage.getItem("{item}");'
            return self.run_js_loaded(js, as_expr=True)
        else:
            js = '''
            var dp_ls_len = sessionStorage.length;
            var dp_ls_arr = new Array();
            for(var i = 0; i < dp_ls_len; i++) {
                var getKey = sessionStorage.key(i);
                var getVal = sessionStorage.getItem(getKey);
                dp_ls_arr[i] = {'key': getKey, 'val': getVal}
            }
            return dp_ls_arr;
            '''
            return {i['key']: i['val'] for i in self.run_js_loaded(js)}

    def get_local_storage(self, item=None):
        """获取localStorage信息，不设置item则获取全部
        :param item: 要获取的项目，不设置则返回全部
        :return: localStorage一个或所有项内容
        """
        if item:
            js = f'localStorage.getItem("{item}");'
            return self.run_js_loaded(js, as_expr=True)
        else:
            js = '''
            var dp_ls_len = localStorage.length;
            var dp_ls_arr = new Array();
            for(var i = 0; i < dp_ls_len; i++) {
                var getKey = localStorage.key(i);
                var getVal = localStorage.getItem(getKey);
                dp_ls_arr[i] = {'key': getKey, 'val': getVal}
            }
            return dp_ls_arr;
            '''
            return {i['key']: i['val'] for i in self.run_js_loaded(js)}

    def get_screenshot(self, path=None, as_bytes=None, as_base64=None,
                       full_page=False, left_top=None, right_bottom=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 完整路径，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :return: 图片完整路径或字节文本
        """
        return self._get_screenshot(path=path, as_bytes=as_bytes, as_base64=as_base64,
                                    full_page=full_page, left_top=left_top, right_bottom=right_bottom)

    def clear_cache(self, session_storage=True, local_storage=True, cache=True, cookies=True):
        """清除缓存，可选要清除的项
        :param session_storage: 是否清除sessionStorage
        :param local_storage: 是否清除localStorage
        :param cache: 是否清除cache
        :param cookies: 是否清除cookies
        :return: None
        """
        if session_storage:
            self.run_js('sessionStorage.clear();', as_expr=True)
        if local_storage:
            self.run_js('localStorage.clear();', as_expr=True)
        if cache:
            self.run_cdp_loaded('Network.clearBrowserCache')
        if cookies:
            self.run_cdp_loaded('Network.clearBrowserCookies')

    def _d_connect(self, to_url, times=0, interval=1, show_errmsg=False, timeout=None):
        """尝试连接，重试若干次
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :param timeout: 连接超时时间
        :return: 是否成功，返回None表示不确定
        """
        err = None
        timeout = timeout if timeout is not None else self.timeouts.page_load

        for t in range(times + 1):
            err = None
            result = self.run_cdp('Page.navigate', url=to_url)

            is_timeout = self._wait_loaded(timeout)
            if is_timeout is None:
                return None
            is_timeout = not is_timeout
            self.wait.load_complete()

            if is_timeout:
                err = TimeoutError('页面连接超时。')
            if 'errorText' in result:
                err = ConnectionError(result['errorText'])

            if not err:
                break

            if t < times:
                sleep(interval)
                while self.ready_state not in ('complete', None):
                    sleep(.1)
                if self._debug or show_errmsg:
                    print(f'重试 {to_url}')

        if err:
            if show_errmsg:
                raise err if err is not None else ConnectionError('连接异常。')
            return False

        return True

    def _get_screenshot(self, path=None, as_bytes=None, as_base64=None,
                        full_page=False, left_top=None, right_bottom=None, ele=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 完整路径，后缀可选 'jpg','jpeg','png','webp'
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
                    raise ValueError("只能接收 'jpg', 'jpeg', 'png', 'webp' 四种格式。")
                pic_type = 'jpeg' if as_bytes == 'jpg' else as_bytes

        elif as_base64:
            if as_base64 is True:
                pic_type = 'png'
            else:
                if as_base64 not in ('jpg', 'jpeg', 'png', 'webp'):
                    raise ValueError("只能接收 'jpg', 'jpeg', 'png', 'webp' 四种格式。")
                pic_type = 'jpeg' if as_base64 == 'jpg' else as_base64

        else:
            if not path:
                path = f'{self.title}.jpg'
            path = get_usable_path(path)
            pic_type = path.suffix.lower()
            if pic_type not in ('.jpg', '.jpeg', '.png', '.webp'):
                raise TypeError(f'不支持的文件格式：{pic_type}。')
            pic_type = 'jpeg' if pic_type == '.jpg' else pic_type[1:]

        width, height = self.size
        if full_page:
            vp = {'x': 0, 'y': 0, 'width': width, 'height': height, 'scale': 1}
            png = self.run_cdp_loaded('Page.captureScreenshot', format=pic_type,
                                      captureBeyondViewport=True, clip=vp)['data']
        else:
            if left_top and right_bottom:
                x, y = left_top
                w = right_bottom[0] - x
                h = right_bottom[1] - y
                vp = {'x': x, 'y': y, 'width': w, 'height': h, 'scale': 1}
                png = self.run_cdp_loaded('Page.captureScreenshot', format=pic_type,
                                          captureBeyondViewport=False, clip=vp)['data']
            else:
                png = self.run_cdp_loaded('Page.captureScreenshot', format=pic_type)['data']

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

    # ------------------准备废弃----------------------
    def wait_loading(self, timeout=None):
        """阻塞程序，等待页面进入加载状态
        :param timeout: 超时时间
        :return: 等待结束时是否进入加载状态
        """
        warn("wait_loading()方法即将弃用，请用wait.load_start()方法代替。", DeprecationWarning)
        return self.wait.load_start(timeout)

    def scroll_to_see(self, loc_or_ele):
        """滚动页面直到元素可见
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串（详见ele函数注释）
        :return: None
        """
        warn("scroll_to_see()方法即将弃用，请用scroll.to_see()方法代替。", DeprecationWarning)
        self.scroll.to_see(loc_or_ele)

    def set_timeouts(self, implicit=None, page_load=None, script=None):
        """设置超时时间，单位为秒
        :param implicit: 查找元素超时时间
        :param page_load: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: None
        """
        warn("set_timeouts()方法即将弃用，请用set.timeouts()方法代替。", DeprecationWarning)
        self.set.timeouts(implicit, page_load, script)

    def set_session_storage(self, item, value):
        """设置或删除某项sessionStorage信息
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        warn("set_session_storage()方法即将弃用，请用set.session_storage()方法代替。", DeprecationWarning)
        return self.set.session_storage(item, value)

    def set_local_storage(self, item, value):
        """设置或删除某项localStorage信息
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        warn("set_local_storage()方法即将弃用，请用set.local_storage()方法代替。", DeprecationWarning)
        return self.set.local_storage(item, value)

    def set_user_agent(self, ua, platform=None):
        """为当前tab设置user agent，只在当前tab有效
        :param ua: user agent字符串
        :param platform: platform字符串
        :return: None
        """
        warn("set_user_agent()方法即将弃用，请用set.user_agent()方法代替。", DeprecationWarning)
        self.set.user_agent(ua, platform)

    def set_cookies(self, cookies):
        """设置cookies值
        :param cookies: cookies信息
        :return: None
        """
        warn("set_cookies()方法即将弃用，请用set.cookies()方法代替。", DeprecationWarning)
        self.set.cookies(cookies)

    def set_headers(self, headers: dict) -> None:
        """设置固定发送的headers
        :param headers: dict格式的headers数据
        :return: None
        """
        warn("set_headers()方法即将弃用，请用set.headers()方法代替。", DeprecationWarning)
        self.set.headers(headers)

    @property
    def set_page_load_strategy(self):
        """返回用于设置页面加载策略的对象"""
        warn("set_page_load_strategy()方法即将弃用，请用set.load_strategy.xxxx()方法代替。", DeprecationWarning)
        return self.set.load_strategy


class ChromiumBaseSetter(object):
    def __init__(self, page):
        self._page = page

    @property
    def load_strategy(self):
        """返回用于设置页面加载策略的对象"""
        return PageLoadStrategy(self._page)

    @property
    def scroll(self):
        """返回用于设置页面滚动设置的对象"""
        return PageScrollSetter(self._page.scroll)

    def retry_times(self, times):
        """设置连接失败重连次数"""
        self._page.retry_times = times

    def retry_interval(self, interval):
        """设置连接失败重连间隔"""
        self._page.retry_interval = interval

    def timeouts(self, implicit=None, page_load=None, script=None):
        """设置超时时间，单位为秒
        :param implicit: 查找元素超时时间
        :param page_load: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: None
        """
        if implicit is not None:
            self._page.timeouts.implicit = implicit

        if page_load is not None:
            self._page.timeouts.page_load = page_load

        if script is not None:
            self._page.timeouts.script = script

    def user_agent(self, ua, platform=None):
        """为当前tab设置user agent，只在当前tab有效
        :param ua: user agent字符串
        :param platform: platform字符串
        :return: None
        """
        keys = {'userAgent': ua}
        if platform:
            keys['platform'] = platform
        self._page.run_cdp('Emulation.setUserAgentOverride', **keys)

    def session_storage(self, item, value):
        """设置或删除某项sessionStorage信息
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        js = f'sessionStorage.removeItem("{item}");' if item is False else f'sessionStorage.setItem("{item}","{value}");'
        return self._page.run_js_loaded(js, as_expr=True)

    def local_storage(self, item, value):
        """设置或删除某项localStorage信息
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        js = f'localStorage.removeItem("{item}");' if item is False else f'localStorage.setItem("{item}","{value}");'
        return self._page.run_js_loaded(js, as_expr=True)

    def cookies(self, cookies):
        """设置cookies值
        :param cookies: cookies信息
        :return: None
        """
        set_browser_cookies(self._page, cookies)

    def upload_files(self, files):
        """等待上传的文件路径
        :param files: 文件路径列表或字符串，字符串时多个文件用回车分隔
        :return: None
        """
        if not self._page._upload_list:
            self._page.driver.Page.fileChooserOpened = self._page._onFileChooserOpened
            self._page.run_cdp('Page.setInterceptFileChooserDialog', enabled=True)

        if isinstance(files, str):
            files = files.split('\n')
        self._page._upload_list = [str(Path(i).absolute()) for i in files]

    def headers(self, headers: dict) -> None:
        """设置固定发送的headers
        :param headers: dict格式的headers数据
        :return: None
        """
        self._page.run_cdp('Network.enable')
        self._page.run_cdp('Network.setExtraHTTPHeaders', headers=headers)


class ChromiumBaseWaiter(object):
    def __init__(self, page_or_ele):
        """
        :param page_or_ele: 页面对象或元素对象
        """
        self._driver = page_or_ele
        self._listener = None

    def ele_delete(self, loc_or_ele, timeout=None):
        """等待元素从DOM中删除
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间，默认读取页面超时时间
        :return: 是否等待成功
        """
        if isinstance(loc_or_ele, (str, tuple)):
            ele = self._driver._ele(loc_or_ele, timeout=.3, raise_err=False)
            return ele.wait.delete(timeout) if ele else True
        return loc_or_ele.wait.delete(timeout)

    def ele_display(self, loc_or_ele, timeout=None):
        """等待元素变成显示状态
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间，默认读取页面超时时间
        :return: 是否等待成功
        """
        ele = self._driver._ele(loc_or_ele, raise_err=False)
        return ele.wait.display(timeout)

    def ele_hidden(self, loc_or_ele, timeout=None):
        """等待元素变成隐藏状态
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间，默认读取页面超时时间
        :return: 是否等待成功
        """
        ele = self._driver._ele(loc_or_ele, raise_err=False)
        return ele.wait.hidden(timeout)

    def load_start(self, timeout=None):
        """等待页面开始加载
        :param timeout: 超时时间，为None时使用页面timeout属性
        :return: 是否等待成功
        """
        return self._loading(timeout=timeout, gap=.002)

    def load_complete(self, timeout=None):
        """等待页面开始加载
        :param timeout: 超时时间，为None时使用页面timeout属性
        :return: 是否等待成功
        """
        return self._loading(timeout=timeout, start=False)

    def upload_paths_inputted(self):
        """等待自动填写上传文件路径"""
        while self._driver._upload_list:
            sleep(.01)

    def _loading(self, timeout=None, start=True, gap=.01):
        """等待页面开始加载或加载完成
        :param timeout: 超时时间，为None时使用页面timeout属性
        :param start: 等待开始还是结束
        :param gap: 间隔秒数
        :return: 是否等待成功
        """
        if timeout != 0:
            timeout = self._driver.timeout if timeout in (None, True) else timeout
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                if self._driver.is_loading == start:
                    return True
                sleep(gap)
            return False

    def set_targets(self, targets, is_regex=False):
        """指定要等待的数据包
        :param targets: 要匹配的数据包url特征，可用list等传入多个
        :param is_regex: 设置的target是否正则表达式
        :return: None
        """
        if not self._listener:
            self._listener = NetworkListener(self._driver)
        self._listener.set_targets(targets, is_regex)

    def data_packets(self, targets=None, timeout=None, any_one=False):
        """等待指定数据包加载完成
        :param targets: 要匹配的数据包url特征，可用list等传入多个
        :param timeout: 超时时间，为None则使用页面对象timeout
        :param any_one: 多个target时，是否全部监听到才结束，为True时监听到一个目标就结束
        :return: ResponseData对象或监听结果字典
        """
        if not self._listener:
            self._listener = NetworkListener(self._driver)
        return self._listener.listen(targets, timeout, any_one)

    def stop_listening(self):
        """停止监听数据包"""
        if not self._listener:
            self._listener = NetworkListener(self._driver)
        self._listener.stop()


class NetworkListener(object):
    def __init__(self, page):
        self._page = page
        self._targets = None
        self._is_regex = False
        self._results = {}
        self._single = False
        self._requests = {}

    def set_targets(self, targets, is_regex=False):
        """指定要等待的数据包
        :param targets: 要匹配的数据包url特征，可用list等传入多个
        :param is_regex: 设置的target是否正则表达式
        :return: None
        """
        if not isinstance(targets, (str, list, tuple, set)):
            raise TypeError('targets只能是str、list、tuple、set。')
        self._is_regex = is_regex
        if isinstance(targets, str):
            self._targets = {targets}
            self._single = True
        else:
            self._targets = set(targets)
            self._single = False
        self._page.run_cdp('Network.enable')
        if targets is not None:
            self._page.driver.Network.requestWillBeSent = self._requestWillBeSent
            self._page.driver.Network.responseReceived = self._response_received
            self._page.driver.Network.loadingFinished = self._loading_finished
        else:
            self.stop_listening()

    def stop(self):
        """停止监听数据包"""
        self._page.run_cdp('Network.disable')
        self._page.driver.Network.requestWillBeSent = None
        self._page.driver.Network.responseReceived = None
        self._page.driver.Network.loadingFinished = None

    def listen(self, targets=None, timeout=None, any_one=False):
        """等待指定数据包加载完成
        :param targets: 要匹配的数据包url特征，可用list等传入多个
        :param timeout: 超时时间，为None则使用页面对象timeout
        :param any_one: 多个target时，是否全部监听到才结束，为True时监听到一个目标就结束
        :return: ResponseData对象或监听结果字典
        """
        if self._targets is None and targets is None:
            targets = ''
        if targets is not None:
            self.set_targets(targets, is_regex=self._is_regex)
        self._results = {}

        timeout = timeout if timeout is not None else self._page.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if self._results and (any_one or set(self._results) == self._targets):
                break
            sleep(.1)

        self._requests = {}
        if not self._results:
            return False
        return list(self._results.values())[0] if self._single else self._results

    def _response_received(self, **kwargs):
        """接收到返回信息时处理方法"""
        if kwargs['requestId'] in self._requests:
            self._requests[kwargs['requestId']]['response'] = kwargs['response']

    def _loading_finished(self, **kwargs):
        """请求完成时处理方法"""
        request_id = kwargs['requestId']
        if request_id in self._requests:
            try:
                body = self._page.run_cdp('Network.getResponseBody', requestId=request_id)['body']
            except:
                body = None

            request = self._requests[request_id]
            target = request['target']
            rd = ResponseData(request_id, request['response'],
                              body, self._page.tab_id, target)
            rd.postData = request['post_data']
            rd._requestHeaders = request['request_headers']
            self._results[target] = rd

    def _requestWillBeSent(self, **kwargs):
        """接收到请求时的回调函数"""
        for target in self._targets:
            if (self._is_regex and search(target, kwargs['request']['url'])) or (
                    not self._is_regex and target in kwargs['request']['url']):
                self._requests[kwargs['requestId']] = {'target': target,
                                                       'post_data': kwargs['request'].get('postData', None),
                                                       'request_headers': kwargs['request']['headers']}
                break


class ChromiumPageScroll(ChromiumScroll):
    def __init__(self, page):
        """
        :param page: 页面对象
        """
        super().__init__(page)
        self.t1 = 'window'
        self.t2 = 'document.documentElement'

    def to_see(self, loc_or_ele, center=False):
        """滚动页面直到元素可见
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :param center: 是否尽量滚动到页面正中
        :return: None
        """
        ele = self._driver._ele(loc_or_ele)
        self._to_see(ele, center)

    def _to_see(self, ele, center):
        """执行滚动页面直到元素可见
        :param ele: 元素对象
        :param center: 是否尽量滚动到页面正中
        :return: None
        """
        if center:
            ele.run_js('this.scrollIntoViewIfNeeded();')
            self._wait_scrolled()
            return

        ele.run_js('this.scrollIntoViewIfNeeded(false);')
        if ele.states.is_covered:
            ele.run_js('this.scrollIntoViewIfNeeded();')
        self._wait_scrolled()


class Timeout(object):
    """用于保存d模式timeout信息的类"""

    def __init__(self, page, implicit=None, page_load=None, script=None):
        """
        :param page: ChromiumBase页面
        :param implicit: 默认超时时间
        :param page_load: 页面加载超时时间
        :param script: js超时时间
        """
        self._page = page
        self.implicit = 10 if implicit is None else implicit
        self.page_load = 30 if page_load is None else page_load
        self.script = 30 if script is None else script

    def __repr__(self):
        return str({'implicit': self.implicit, 'page_load': self.page_load, 'script': self.script})


class PageLoadStrategy(object):
    """用于设置页面加载策略的类"""

    def __init__(self, page):
        """
        :param page: ChromiumBase对象
        """
        self._page = page

    def __call__(self, value):
        """设置加载策略
        :param value: 可选 'normal', 'eager', 'none'
        :return: None
        """
        if value.lower() not in ('normal', 'eager', 'none'):
            raise ValueError("只能选择 'normal', 'eager', 'none'。")
        self._page._page_load_strategy = value

    def normal(self):
        """设置页面加载策略为normal"""
        self._page._page_load_strategy = 'normal'

    def eager(self):
        """设置页面加载策略为eager"""
        self._page._page_load_strategy = 'eager'

    def none(self):
        """设置页面加载策略为none"""
        self._page._page_load_strategy = 'none'


class PageScrollSetter(object):
    def __init__(self, scroll):
        self._scroll = scroll

    def wait_complete(self, on_off=True):
        """设置滚动命令后是否等待完成
        :param on_off: 开或关
        :return: None
        """
        if not isinstance(on_off, bool):
            raise TypeError('on_off必须为bool。')
        self._scroll._wait_complete = on_off

    def smooth(self, on_off=True):
        """设置页面滚动是否平滑滚动
        :param on_off: 开或关
        :return: None
        """
        if not isinstance(on_off, bool):
            raise TypeError('on_off必须为bool。')
        b = 'smooth' if on_off else 'auto'
        self._scroll._driver.run_js(f'document.documentElement.style.setProperty("scroll-behavior","{b}");')
        self._scroll._wait_complete = on_off


class Screencast(object):
    def __init__(self, page):
        self._page = page
        self._path = None
        self._running = False
        self._enable = False
        self._mode = 'video'

    @property
    def set_mode(self):
        """返回用于设置录屏幕式的对象"""
        return ScreencastMode(self)

    def start(self, save_path=None):
        """开始录屏
        :param save_path: 录屏保存位置
        :return: None
        """
        self.set_save_path(save_path)
        if self._path is None:
            raise ValueError('save_path必须设置。')
        clean_folder(self._path)
        if self._mode.startswith('frugal'):
            self._page.driver.Page.screencastFrame = self._onScreencastFrame
            self._page.run_cdp('Page.startScreencast', everyNthFrame=1, quality=100)

        elif not self._mode.startswith('js'):
            self._running = True
            self._enable = True
            Thread(target=self._run).start()

        else:
            js = '''
            async function () {
                stream = await navigator.mediaDevices.getDisplayMedia({video: true, audio: true})
                mime = MediaRecorder.isTypeSupported("video/webm; codecs=vp9")
                               ? "video/webm; codecs=vp9"
                               : "video/webm"
                mediaRecorder = new MediaRecorder(stream, {mimeType: mime})
                DrissionPage_Screencast_chunks = []
                mediaRecorder.addEventListener('dataavailable', function(e) {
                    DrissionPage_Screencast_blob_ok = false;
                    DrissionPage_Screencast_chunks.push(e.data);
                    DrissionPage_Screencast_blob_ok = true;
                })
                mediaRecorder.start()
                
                mediaRecorder.addEventListener('stop', function(){
                    while(DrissionPage_Screencast_blob_ok==false){}
                    DrissionPage_Screencast_blob = new Blob(DrissionPage_Screencast_chunks, 
                                                            {type: DrissionPage_Screencast_chunks[0].type});
                })
              }
            '''
            print('请手动选择要录制的目标。')
            self._page.run_js('var DrissionPage_Screencast_blob;var DrissionPage_Screencast_blob_ok=false;')
            self._page.run_js(js)

    def stop(self, video_name=None):
        """停止录屏
        :param video_name: 视频文件名，为None时以当前时间名命
        :return: 文件路径
        """
        if video_name and not video_name.endswith('mp4'):
            video_name = f'{video_name}.mp4'
        name = f'{time()}.mp4' if not video_name else video_name
        path = f'{self._path}{sep}{name}'

        if self._mode.startswith('js'):
            self._page.run_js('mediaRecorder.stop();', as_expr=True)
            while not self._page.run_js('return DrissionPage_Screencast_blob_ok;'):
                sleep(.1)
            blob = self._page.run_js('return DrissionPage_Screencast_blob;')
            uuid = self._page.run_cdp('IO.resolveBlob', objectId=blob['result']['objectId'])['uuid']
            data = self._page.run_cdp('IO.read', handle=f'blob:{uuid}')['data']
            with open(path, 'wb') as f:
                f.write(b64decode(data))
            return path

        if self._mode.startswith('frugal'):
            self._page.driver.Page.screencastFrame = None
            self._page.run_cdp('Page.stopScreencast')
        else:
            self._enable = False
            while self._running:
                sleep(.1)

        if self._mode.endswith('imgs'):
            return str(Path(self._path).absolute())

        if not str(video_name).isascii() or not str(self._path).isascii():
            raise TypeError('转换成视频仅支持英文路径和文件名。')

        try:
            from cv2 import VideoWriter, imread
            from numpy import fromfile, uint8
        except ModuleNotFoundError:
            raise ModuleNotFoundError('请先安装cv2，pip install opencv-python')

        pic_list = Path(self._path).glob('*.jpg')
        img = imread(str(next(pic_list)))
        imgInfo = img.shape
        size = (imgInfo[1], imgInfo[0])

        # if video_name and not video_name.endswith('mp4'):
        #     video_name = f'{video_name}.mp4'
        # name = f'{time()}.mp4' if not video_name else video_name
        videoWrite = VideoWriter(path, 14, 5, size)

        for i in pic_list:
            img = imread(str(i))
            videoWrite.write(img)

        clean_folder(self._path, ignore=(name,))
        return f'{self._path}{sep}{name}'

    def set_save_path(self, save_path=None):
        """设置保存路径
        :param save_path: 保存路径
        :return: None
        """
        if save_path:
            save_path = Path(save_path)
            if save_path.exists() and save_path.is_file():
                raise TypeError('save_path必须指定文件夹。')
            save_path.mkdir(parents=True, exist_ok=True)
            self._path = save_path

    def _run(self):
        """非节俭模式运行方法"""
        self._running = True
        while self._enable:
            p = self._path / f'{time()}.jpg'
            self._page.get_screenshot(path=p)
            sleep(.04)
        self._running = False

    def _onScreencastFrame(self, **kwargs):
        """节俭模式运行方法"""
        with open(f'{self._path}\\{kwargs["metadata"]["timestamp"]}.jpg', 'wb') as f:
            f.write(b64decode(kwargs['data']))
        self._page.run_cdp('Page.screencastFrameAck', sessionId=kwargs['sessionId'])


class ScreencastMode(object):
    def __init__(self, screencast):
        self._screencast = screencast

    def video_mode(self):
        self._screencast._mode = 'video'

    def frugal_video_mode(self):
        self._screencast._mode = 'frugal_video'

    def js_video_mode(self):
        self._screencast._mode = 'js_video'

    def frugal_imgs_mode(self):
        self._screencast._mode = 'frugal_imgs'

    def imgs_mode(self):
        self._screencast._mode = 'imgs'
