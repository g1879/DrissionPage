# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from re import search
from time import sleep, perf_counter
from warnings import warn

from .chromium_base import ChromiumBase, ChromiumPageScroll, ChromiumBaseSetter
from .chromium_element import ChromiumElement


class ChromiumFrame(ChromiumBase):
    def __init__(self, page, ele):
        self.page = page
        self.address = page.address
        node = page.run_cdp('DOM.describeNode', backendNodeId=ele.ids.backend_id)['node']
        self.frame_id = node['frameId']
        self._backend_id = ele.ids.backend_id
        self._frame_ele = ele
        self._states = None

        if self._is_inner_frame():
            self._is_diff_domain = False
            self.doc_ele = ChromiumElement(self.page, backend_id=node['contentDocument']['backendNodeId'])
            super().__init__(page.address, page.tab_id, page.timeout)
        else:
            self._is_diff_domain = True
            super().__init__(page.address, self.frame_id, page.timeout)
            obj_id = super().run_js('document;', as_expr=True)['objectId']
            self.doc_ele = ChromiumElement(self, obj_id=obj_id)
        self._ids = ChromiumFrameIds(self)

        end_time = perf_counter() + 2
        while perf_counter() < end_time and self.url == 'about:blank':
            sleep(.1)

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: ChromiumElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    def __repr__(self):
        attrs = self.frame_ele.attrs
        attrs = [f"{attr}='{attrs[attr]}'" for attr in attrs]
        return f'<ChromiumFrame {self.frame_ele.tag} {" ".join(attrs)}>'

    def _runtime_settings(self):
        """重写设置浏览器运行参数方法"""
        self._timeouts = self.page.timeouts
        self._page_load_strategy = self.page.page_load_strategy

    def _driver_init(self, tab_id):
        """避免出现服务器500错误
        :param tab_id: 要跳转到的标签页id
        :return: None
        """
        try:
            super()._driver_init(tab_id)
        except:
            self._control_session.get(f'http://{self.address}/json')
            super()._driver_init(tab_id)

    def _reload(self):
        """重新获取document"""
        debug = self._debug
        if debug:
            print('reload')

        self._frame_ele = ChromiumElement(self.page, backend_id=self._backend_id)
        node = self.page.run_cdp('DOM.describeNode', backendNodeId=self._frame_ele.ids.backend_id)['node']

        if self._is_inner_frame():
            self._is_diff_domain = False
            self.doc_ele = ChromiumElement(self.page, backend_id=node['contentDocument']['backendNodeId'])
            super().__init__(self.address, self.page.tab_id, self.page.timeout)
            self._debug = debug
        else:
            self._is_diff_domain = True
            self._tab_obj.stop()
            super().__init__(self.address, self.frame_id, self.page.timeout)
            obj_id = super().run_js('document;', as_expr=True)['objectId']
            self.doc_ele = ChromiumElement(self, obj_id=obj_id)
            self._debug = debug

    def _check_ok(self):
        """用于应付同域异域之间跳转导致元素丢失问题"""
        if self._tab_obj._stopped.is_set():
            self._reload()

        try:
            self.page.run_cdp('DOM.describeNode', nodeId=self.ids.node_id)
        except Exception:
            self._reload()
            # sleep(2)

    def _get_new_document(self):
        """刷新cdp使用的document数据"""
        if not self._is_reading:
            self._is_reading = True

            if self._debug:
                print('---获取document')

            while True:
                try:
                    if self._is_diff_domain is False:
                        node = self.page.run_cdp('DOM.describeNode', backendNodeId=self.ids.backend_id)['node']
                        self.doc_ele = ChromiumElement(self.page, backend_id=node['contentDocument']['backendNodeId'])

                    else:
                        b_id = self.run_cdp('DOM.getDocument')['root']['backendNodeId']
                        self.doc_ele = ChromiumElement(self, backend_id=b_id)

                    break

                except Exception:
                    raise
                    pass

            if self._debug:
                print('---获取document结束')

            self._is_loading = False
            self._is_reading = False

    def _onLoadEventFired(self, **kwargs):
        """在页面刷新、变化后重新读取页面内容"""
        # 用于覆盖父类方法，不能删
        if self._debug:
            print('loadEventFired')
            if self._debug_recorder:
                self._debug_recorder.add_data((perf_counter(), '加载流程', 'loadEventFired'))

    def _onFrameStartedLoading(self, **kwargs):
        """页面开始加载时触发"""
        if kwargs['frameId'] == self.frame_id:
            self._is_loading = True
            if self._debug:
                print('页面开始加载 FrameStartedLoading')

    def _onFrameStoppedLoading(self, **kwargs):
        """页面加载完成后触发"""
        if kwargs['frameId'] == self.frame_id and self._first_run is False and self._is_loading:
            if self._debug:
                print('页面停止加载 FrameStoppedLoading')
            self._get_new_document()

    @property
    def ids(self):
        return self._ids

    @property
    def frame_ele(self):
        """返回总页面上的frame元素"""
        return self._frame_ele

    @property
    def tag(self):
        """返回元素tag"""
        self._check_ok()
        return self.frame_ele.tag

    @property
    def url(self):
        """返回frame当前访问的url"""
        self._check_ok()
        return self.doc_ele.run_js('return this.location.href;')

    @property
    def html(self):
        """返回元素outerHTML文本"""
        self._check_ok()
        tag = self.tag
        out_html = self.page.run_cdp('DOM.getOuterHTML', backendNodeId=self.frame_ele.ids.backend_id)['outerHTML']
        sign = search(rf'<{tag}.*?>', out_html).group(0)
        return f'{sign}{self.inner_html}</{tag}>'

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        self._check_ok()
        return self.doc_ele.run_js('return this.documentElement.outerHTML;')

    @property
    def title(self):
        """返回页面title"""
        self._check_ok()
        r = self._ele('t:title', raise_err=False)
        return r.text if r else None

    @property
    def cookies(self):
        """以dict格式返回cookies"""
        self._check_ok()
        return super().cookies if self._is_diff_domain else self.doc_ele.run_js('return this.cookie;')

    @property
    def attrs(self):
        """返回frame元素所有attribute属性"""
        self._check_ok()
        return self.frame_ele.attrs

    @property
    def frame_size(self):
        """返回frame内页面尺寸，格式：(长, 高)"""
        self._check_ok()
        w = self.doc_ele.run_js('return this.body.scrollWidth')
        h = self.doc_ele.run_js('return this.body.scrollHeight')
        return w, h

    @property
    def size(self):
        """返回frame元素大小"""
        self._check_ok()
        return self.frame_ele.size

    @property
    def active_ele(self):
        """返回当前焦点所在元素"""
        self._check_ok()
        return self.doc_ele.run_js('return this.activeElement;')

    @property
    def location(self):
        """返回frame元素左上角的绝对坐标"""
        self._check_ok()
        return self.frame_ele.location

    @property
    def locations(self):
        """返回用于获取元素位置的对象"""
        return self.frame_ele.locations

    @property
    def xpath(self):
        """返回frame的xpath绝对路径"""
        self._check_ok()
        return self.frame_ele.xpath

    @property
    def css_path(self):
        """返回frame的css selector绝对路径"""
        self._check_ok()
        return self.frame_ele.css_path

    @property
    def ready_state(self):
        """返回当前页面加载状态，'loading' 'interactive' 'complete'"""
        if self._is_diff_domain:
            try:
                return super().ready_state
            except:
                return 'complete'

        else:
            while True:
                try:
                    return self.doc_ele.run_js('return this.readyState;')
                except:
                    pass

    @property
    def scroll(self):
        """返回用于等待的对象"""
        return ChromiumFrameScroll(self)

    @property
    def set(self):
        """返回用于等待的对象"""
        if self._set is None:
            self._set = ChromiumFrameSetter(self)
        return self._set

    @property
    def states(self):
        """返回用于获取状态信息的对象"""
        if self._states is None:
            self._states = ChromiumFrameStates(self)
        return self._states

    def refresh(self):
        """刷新frame页面"""
        self._check_ok()
        self.doc_ele.run_js('this.location.reload();')

    def attr(self, attr):
        """返回frame元素attribute属性值
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        self._check_ok()
        return self.frame_ele.attr(attr)

    def remove_attr(self, attr):
        """删除frame元素attribute属性
        :param attr: 属性名
        :return: None
        """
        self._check_ok()
        self.frame_ele.remove_attr(attr)

    def run_js(self, script, *args, as_expr=False):
        """运行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: 运行的结果
        """
        self._check_ok()
        if script.startswith('this.scrollIntoView'):
            return self.frame_ele.run_js(script, *args, as_expr=as_expr)
        else:
            return self.doc_ele.run_js(script, *args, as_expr=as_expr)

    def parent(self, level_or_loc=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :return: 上级元素对象
        """
        self._check_ok()
        return self.frame_ele.parent(level_or_loc)

    def prev(self, filter_loc='', index=1, timeout=0):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        self._check_ok()
        return self.frame_ele.prev(filter_loc, index, timeout)

    def next(self, filter_loc='', index=1, timeout=0):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        self._check_ok()
        return self.frame_ele.next(filter_loc, index, timeout)

    def before(self, filter_loc='', index=1, timeout=None):
        """返回当前元素前面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元素，而是整个DOM文档
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的某个元素或节点
        """
        self._check_ok()
        return self.frame_ele.before(filter_loc, index, timeout)

    def after(self, filter_loc='', index=1, timeout=None):
        """返回当前元素后面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元素，而是整个DOM文档
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 本元素后面的某个元素或节点
        """
        self._check_ok()
        return self.frame_ele.after(filter_loc, index, timeout)

    def prevs(self, filter_loc='', timeout=0):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        self._check_ok()
        return self.frame_ele.prevs(filter_loc, timeout)

    def nexts(self, filter_loc='', timeout=0):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        self._check_ok()
        return self.frame_ele.nexts(filter_loc, timeout)

    def befores(self, filter_loc='', timeout=None):
        """返回当前元素后面符合条件的全部兄弟元素或节点组成的列表，可用查询语法筛选。查找范围不限兄弟元素，而是整个DOM文档
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的元素或节点组成的列表
        """
        self._check_ok()
        return self.frame_ele.befores(filter_loc, timeout)

    def afters(self, filter_loc='', timeout=None):
        """返回当前元素后面符合条件的全部兄弟元素或节点组成的列表，可用查询语法筛选。查找范围不限兄弟元素，而是整个DOM文档
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的元素或节点组成的列表
        """
        self._check_ok()
        return self.frame_ele.afters(filter_loc, timeout)

    def get_screenshot(self, path=None, as_bytes=None, full_page=False, left_top=None, right_bottom=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 完整路径，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否已字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :return: 图片完整路径或字节文本
        """
        if full_page:
            raise RuntimeError('暂未实现对iframe全页截图功能。')
        if left_top is None and right_bottom is None:
            return self.frame_ele.get_screenshot(path=path, as_bytes=as_bytes)
        else:
            raise RuntimeError('暂未实现对异域iframe内元素截图功能。')

    def _find_elements(self, loc_or_ele, timeout=None, single=True, relative=False, raise_err=None):
        """在frame内查找单个元素
        :param loc_or_ele: 定位符或元素对象
        :param timeout: 查找超时时间
        :param single: True则返回第一个，False则返回全部
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象
        """
        self._check_ok()
        if isinstance(loc_or_ele, ChromiumElement):
            return loc_or_ele

        self.wait.load_complete()

        return self.doc_ele._ele(loc_or_ele, timeout, raise_err=raise_err) \
            if single else self.doc_ele.eles(loc_or_ele, timeout)

    def _d_connect(self, to_url, times=0, interval=1, show_errmsg=False, timeout=None):
        """尝试连接，重试若干次
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :param timeout: 连接超时时间
        :return: 是否成功，返回None表示不确定
        """
        self._check_ok()
        err = None
        timeout = timeout if timeout is not None else self.timeouts.page_load

        for t in range(times + 1):
            err = None
            result = self.driver.Page.navigate(url=to_url, frameId=self.frame_id)

            is_timeout = not self._wait_loaded(timeout)
            sleep(.5)
            self.wait.load_complete()

            if is_timeout:
                err = TimeoutError('页面连接超时。')
            if 'errorText' in result:
                err = ConnectionError(result['errorText'])

            if not err:
                break

            if t < times:
                sleep(interval)
                while self.ready_state != 'complete':
                    sleep(.1)
                if self._debug:
                    print('重试')
                if show_errmsg:
                    print(f'重试 {to_url}')

        if err:
            if show_errmsg:
                raise err if err is not None else ConnectionError('连接异常。')
            return False

        return True

    def _is_inner_frame(self):
        """返回当前frame是否同域"""
        return self.frame_id in str(self.page.run_cdp('Page.getFrameTree')['frameTree'])

    # -------------准备废弃------------
    def set_attr(self, attr, value):
        """设置frame元素attribute属性
        :param attr: 属性名
        :param value: 属性值
        :return: None
        """
        warn("set_attr()方法即将弃用，请用set.attr()方法代替。", DeprecationWarning)
        self.set.attr(attr, value)

    @property
    def is_displayed(self):
        """返回frame元素是否显示"""
        warn("is_displayed属性即将弃用，请用states.is_displayed属性代替。", DeprecationWarning)
        return self.states.is_displayed()

    @property
    def tab_id(self):
        """返回当前标签页id"""
        warn("tab_id属性即将弃用，请用ids.tab_id属性代替。", DeprecationWarning)
        return self.ids.tab_id

    @property
    def backend_id(self):
        """返回cdp中的node id"""
        warn("backend_id属性即将弃用，请用ids.backend_id属性代替。", DeprecationWarning)
        return self.ids.backend_id

    @property
    def obj_id(self):
        """返回frame元素的object id"""
        warn("obj_id属性即将弃用，请用ids.obj_id属性代替。", DeprecationWarning)
        return self.ids.obj_id

    @property
    def node_id(self):
        """返回cdp中的node id"""
        warn("node_id属性即将弃用，请用ids.node_id属性代替。", DeprecationWarning)
        return self.ids.node_id


class ChromiumFrameIds(object):
    def __init__(self, frame):
        self._frame = frame

    @property
    def tab_id(self):
        """返回当前标签页id"""
        return self._frame.page.tab_id

    @property
    def backend_id(self):
        """返回cdp中的node id"""
        return self._frame._backend_id

    @property
    def obj_id(self):
        """返回frame元素的object id"""
        return self._frame.frame_ele.ids.obj_id

    @property
    def node_id(self):
        """返回cdp中的node id"""
        return self._frame.frame_ele.ids.node_id


class ChromiumFrameStates(object):
    def __init__(self, frame):
        self._frame = frame

    def is_displayed(self):
        """返回frame元素是否显示"""
        self._frame._check_ok()
        return self._frame.frame_ele.states.is_displayed


class ChromiumFrameScroll(ChromiumPageScroll):
    def __init__(self, frame):
        """
        :param frame: ChromiumFrame对象
        """
        self._driver = frame.doc_ele
        self.t1 = self.t2 = 'this.documentElement'

    def to_see(self, loc_or_ele):
        """滚动页面直到元素可见
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: None
        """
        ele = loc_or_ele if isinstance(loc_or_ele, ChromiumElement) else self._driver._ele(loc_or_ele)
        ele.run_js('this.scrollIntoView({behavior: "auto", block: "center", inline: "center"});')


class ChromiumFrameSetter(ChromiumBaseSetter):
    def attr(self, attr, value):
        """设置frame元素attribute属性
        :param attr: 属性名
        :param value: 属性值
        :return: None
        """
        self._page._check_ok()
        self._page.frame_ele.set.attr(attr, value)
