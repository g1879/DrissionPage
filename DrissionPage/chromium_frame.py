# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from re import search
from time import sleep

from .chromium_base import ChromiumBase
from .chromium_element import ChromiumElement


class ChromiumFrame(ChromiumBase):
    def __init__(self, page, ele):
        self.page = page
        self.address = page.address
        node = page.run_cdp('DOM.describeNode', nodeId=ele.node_id, not_change=True)['node']
        self.frame_id = node['frameId']
        self._backend_id = ele.backend_id
        self._frame_ele = ele

        if self._is_inner_frame():
            self._is_diff_domain = False
            self.doc_ele = ChromiumElement(self.page, backend_id=node['contentDocument']['backendNodeId'])
            super().__init__(page.address, page.tab_id, page.timeout)
        else:
            self._is_diff_domain = True
            super().__init__(page.address, self.frame_id, page.timeout)
            obj_id = super().run_script('document;', as_expr=True)['objectId']
            self.doc_ele = ChromiumElement(self, obj_id=obj_id)

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素                                             \n
        例：ele2 = ele1('@id=ele_id')                               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: ChromiumElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    def __repr__(self):
        attrs = self.frame_ele.attrs
        attrs = [f"{attr}='{attrs[attr]}'" for attr in attrs]
        return f'<ChromiumFrame {self.frame_ele.tag} {" ".join(attrs)}>'

    def _reload(self):
        self._frame_ele = ChromiumElement(self.page, backend_id=self._backend_id)
        node = self.page.run_cdp('DOM.describeNode', nodeId=self._frame_ele.node_id, not_change=True)['node']

        if self._is_inner_frame():
            self._is_diff_domain = False
            self.doc_ele = ChromiumElement(self.page, backend_id=node['contentDocument']['backendNodeId'])
            super().__init__(self.address, self.page.tab_id, self.page.timeout)
        else:
            self._is_diff_domain = True
            self._tab_obj.stop()
            super().__init__(self.address, self.frame_id, self.page.timeout)
            obj_id = super().run_script('document;', as_expr=True)['objectId']
            self.doc_ele = ChromiumElement(self, obj_id=obj_id)

    def _check_ok(self):
        if self._tab_obj._stopped.is_set():
            self._reload()

        try:
            self._tab_obj.DOM.describeNode(nodeId=self.node_id)
        except:
            self._reload()
            sleep(2)

    def _get_new_document(self):
        """刷新cdp使用的document数据"""
        if not self._is_reading:
            self._is_reading = True

            if self._debug:
                print('---获取document')

            while True:
                try:
                    if self._is_diff_domain is False:
                        node = self.page.run_cdp('DOM.describeNode',
                                                 backendNodeId=self.backend_id, not_change=True)['node']
                        self.doc_ele = ChromiumElement(self.page, backend_id=node['contentDocument']['backendNodeId'])

                    else:
                        b_id = self._tab_obj.DOM.getDocument()['root']['backendNodeId']
                        self.doc_ele = ChromiumElement(self, backend_id=b_id)

                    break

                except Exception:
                    raise
                    pass

            if self._debug:
                print('---获取document结束')

            self._is_loading = False
            self._is_reading = False

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
    def tab_id(self):
        """返回当前标签页id"""
        return self.page.tab_id

    @property
    def backend_id(self):
        """返回cdp中的node id"""
        return self._backend_id

    @property
    def obj_id(self):
        """返回frame元素的object id"""
        return self.frame_ele.obj_id

    @property
    def node_id(self):
        """返回cdp中的node id"""
        return self.frame_ele.node_id

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
        return self.doc_ele.run_script('return this.location.href;')

    @property
    def html(self):
        """返回元素outerHTML文本"""
        self._check_ok()
        tag = self.tag
        out_html = self.page.run_cdp('DOM.getOuterHTML',
                                     nodeId=self.frame_ele.node_id, not_change=True)['outerHTML']
        sign = search(rf'<{tag}.*?>', out_html).group(0)
        return f'{sign}{self.inner_html}</{tag}>'

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        self._check_ok()
        return self.doc_ele.run_script('return this.documentElement.outerHTML;')

    @property
    def title(self):
        """返回页面title"""
        self._check_ok()
        return self.ele('t:title').text

    @property
    def cookies(self):
        """以dict格式返回cookies"""
        self._check_ok()
        return super().cookies if self._is_diff_domain else self.doc_ele.run_script('return this.cookie;')

    @property
    def attrs(self):
        """返回frame元素所有attribute属性"""
        self._check_ok()
        return self.frame_ele.attrs

    @property
    def frame_size(self):
        """返回frame内页面尺寸，格式：(长, 高)"""
        self._check_ok()
        w = self.doc_ele.run_script('return this.body.scrollWidth')
        h = self.doc_ele.run_script('return this.body.scrollHeight')
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
        return self.doc_ele.run_script('return this.activeElement;')

    @property
    def location(self):
        """返回frame元素左上角的绝对坐标"""
        self._check_ok()
        return self.frame_ele.location

    @property
    def is_displayed(self):
        """返回frame元素是否显示"""
        self._check_ok()
        return self.frame_ele.is_displayed

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
                    return self.doc_ele.run_script('return this.readyState;')
                except:
                    pass

    def refresh(self):
        """刷新frame页面"""
        self._check_ok()
        self.doc_ele.run_script('this.location.reload();')

    def attr(self, attr):
        """返回frame元素attribute属性值                           \n
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        self._check_ok()
        return self.frame_ele.attr(attr)

    def set_attr(self, attr, value):
        """设置frame元素attribute属性          \n
        :param attr: 属性名
        :param value: 属性值
        :return: None
        """
        self._check_ok()
        self.frame_ele.set_attr(attr, value)

    def remove_attr(self, attr):
        """删除frame元素attribute属性          \n
        :param attr: 属性名
        :return: None
        """
        self._check_ok()
        self.frame_ele.remove_attr(attr)

    def run_script(self, script, as_expr=False, *args):
        """运行javascript代码                                                 \n
        :param script: js文本
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :return: 运行的结果
        """
        self._check_ok()
        return self.doc_ele.run_script(script, as_expr=as_expr, *args)

    def parent(self, level_or_loc=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位              \n
        :param level_or_loc: 第几级父元素，或定位符
        :return: 上级元素对象
        """
        self._check_ok()
        return self.frame_ele.parent(level_or_loc)

    def prev(self, filter_loc='', index=1, timeout=0):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        self._check_ok()
        return self.frame_ele.prev(filter_loc, index, timeout)

    def next(self, filter_loc='', index=1, timeout=0):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        self._check_ok()
        return self.frame_ele.next(filter_loc, index, timeout)

    def before(self, filter_loc='', index=1, timeout=None):
        """返回当前元素前面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的某个元素或节点
        """
        self._check_ok()
        return self.frame_ele.before(filter_loc, index, timeout)

    def after(self, filter_loc='', index=1, timeout=None):
        """返回当前元素后面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 本元素后面的某个元素或节点
        """
        self._check_ok()
        return self.frame_ele.after(filter_loc, index, timeout)

    def prevs(self, filter_loc='', timeout=0):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        self._check_ok()
        return self.frame_ele.prevs(filter_loc, timeout)

    def nexts(self, filter_loc='', timeout=0):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        self._check_ok()
        return self.frame_ele.nexts(filter_loc, timeout)

    def befores(self, filter_loc='', timeout=None):
        """返回当前元素后面符合条件的全部兄弟元素或节点组成的列表，可用查询语法筛选。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的元素或节点组成的列表
        """
        self._check_ok()
        return self.frame_ele.befores(filter_loc, timeout)

    def _ele(self, loc_or_ele, timeout=None, single=True, relative=False):
        """在frame内查找单个元素                         \n
        :param loc_or_ele: 定位符或元素对象
        :param timeout: 查找超时时间
        :return: ChromiumElement对象
        """
        if isinstance(loc_or_ele, ChromiumElement):
            return loc_or_ele

        while self.is_loading:
            sleep(.05)

        return self.doc_ele.ele(loc_or_ele, timeout) if single else self.doc_ele.eles(loc_or_ele, timeout)

    def _d_connect(self, to_url, times=0, interval=1, show_errmsg=False, timeout=None):
        """尝试连接，重试若干次                            \n
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
            result = self._driver.Page.navigate(url=to_url, frameId=self.frame_id)

            is_timeout = not self._wait_loaded(timeout)
            while self.is_loading:
                sleep(.1)

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
        return self.frame_id in str(self.page.run_cdp('Page.getFrameTree', not_change=True)['frameTree'])
