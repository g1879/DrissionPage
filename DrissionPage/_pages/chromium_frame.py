# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from copy import copy
from re import search, findall, DOTALL
from time import sleep, perf_counter

from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._units.listener import FrameListener
from .._units.rect import FrameRect
from .._units.scroller import FrameScroller
from .._units.setter import ChromiumFrameSetter
from .._units.states import FrameStates
from .._units.waiter import FrameWaiter
from ..errors import ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError


class ChromiumFrame(ChromiumBase):
    def __init__(self, owner, ele, info=None):
        """
        :param owner: frame所在的页面对象
        :param ele: frame所在元素
        :param info: frame所在元素信息
        """
        if owner._type in ('ChromiumPage', 'WebPage'):
            self._page = self._target_page = self.tab = owner
            self._browser = owner.browser
        else:  # Tab、Frame
            self._page = owner.page
            self._browser = self._page.browser
            self._target_page = owner
            self.tab = owner.tab if owner._type == 'ChromiumFrame' else owner

        self.address = owner.address
        self._tab_id = owner.tab_id
        self._backend_id = ele._backend_id
        self._frame_ele = ele
        self._states = None
        self._reloading = False

        node = info['node'] if not info else owner.run_cdp('DOM.describeNode', backendNodeId=ele._backend_id)['node']
        self._frame_id = node['frameId']
        if self._is_inner_frame():
            self._is_diff_domain = False
            self.doc_ele = ChromiumElement(self._target_page, backend_id=node['contentDocument']['backendNodeId'])
            super().__init__(owner.address, owner.tab_id, owner.timeout)
        else:
            self._is_diff_domain = True
            delattr(self, '_frame_id')
            super().__init__(owner.address, node['frameId'], owner.timeout)
            obj_id = super().run_js('document;', as_expr=True)['objectId']
            self.doc_ele = ChromiumElement(self, obj_id=obj_id)

        self._rect = None
        self._type = 'ChromiumFrame'
        # end_time = perf_counter() + 2
        # while perf_counter() < end_time:
        #     if self.url not in (None, 'about:blank'):
        #         break
        #     sleep(.1)

    def __call__(self, locator, index=1, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 超时时间（秒）
        :return: ChromiumElement对象或属性、文本
        """
        return self.ele(locator, index=index, timeout=timeout)

    def __eq__(self, other):
        return self._frame_id == getattr(other, '_frame_id', None)

    def __repr__(self):
        attrs = [f"{k}='{v}'" for k, v in self._frame_ele.attrs.items()]
        return f'<ChromiumFrame {self.frame_ele.tag} {" ".join(attrs)}>'

    def _d_set_runtime_settings(self):
        """重写设置浏览器运行参数方法"""
        if not hasattr(self, '_timeouts'):
            self._timeouts = copy(self._target_page.timeouts)
            self.retry_times = self._target_page.retry_times
            self.retry_interval = self._target_page.retry_interval
            self._download_path = self._target_page.download_path
        self._load_mode = self._target_page._load_mode if not self._is_diff_domain else 'normal'

    def _driver_init(self, tab_id, is_init=True):
        """避免出现服务器500错误
        :param tab_id: 要跳转到的标签页id
        :return: None
        """
        try:
            super()._driver_init(tab_id)
        except:
            self.browser.driver.get(f'http://{self.address}/json')
            super()._driver_init(tab_id)
        self._driver.set_callback('Inspector.detached', self._onInspectorDetached, immediate=True)
        self._driver.set_callback('Page.frameDetached', None)
        self._driver.set_callback('Page.frameDetached', self._onFrameDetached, immediate=True)

    def _reload(self):
        """重新获取document"""
        self._is_loading = True
        # d_debug = self.driver._debug
        self._reloading = True
        self._doc_got = False

        self._driver.stop()
        try:
            self._frame_ele = ChromiumElement(self._target_page, backend_id=self._backend_id)
            end_time = perf_counter() + 2
            while perf_counter() < end_time:
                node = self._target_page.run_cdp('DOM.describeNode', backendNodeId=self._frame_ele._backend_id)['node']
                if 'frameId' in node:
                    break
                sleep(.05)

            else:
                return

        except (ElementLostError, PageDisconnectedError):
            return

        if self._is_inner_frame():
            self._is_diff_domain = False
            self.doc_ele = ChromiumElement(self._target_page, backend_id=node['contentDocument']['backendNodeId'])
            self._frame_id = node['frameId']
            if self._listener:
                self._listener._to_target(self._target_page.tab_id, self.address, self)
            super().__init__(self.address, self._target_page.tab_id, self._target_page.timeout)
            # self.driver._debug = d_debug

        else:
            self._is_diff_domain = True
            if self._listener:
                self._listener._to_target(node['frameId'], self.address, self)
            end_time = perf_counter() + self.timeouts.page_load
            super().__init__(self.address, node['frameId'], self._target_page.timeout)
            timeout = end_time - perf_counter()
            if timeout <= 0:
                timeout = .5
            self._wait_loaded(timeout)

        self._is_loading = False
        self._reloading = False

    def _get_document(self, timeout=10):
        """刷新cdp使用的document数据
        :param timeout: 超时时间（秒）
        :return: 是否获取成功
        """
        if self._is_reading:
            return

        self._is_reading = True
        try:
            if self._is_diff_domain is False:
                node = self._target_page.run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
                self.doc_ele = ChromiumElement(self._target_page, backend_id=node['contentDocument']['backendNodeId'])

            else:
                timeout = max(timeout, 2)
                b_id = self.run_cdp('DOM.getDocument', _timeout=timeout)['root']['backendNodeId']
                self.doc_ele = ChromiumElement(self, backend_id=b_id)

            self._root_id = self.doc_ele._obj_id

            r = self.run_cdp('Page.getFrameTree')
            for i in findall(r"'id': '(.*?)'", str(r)):
                self.browser._frames[i] = self.tab_id
                return True

        except:
            return False

        finally:
            if not self._reloading:  # 阻止reload时标识
                self._is_loading = False
            self._is_reading = False

    def _onInspectorDetached(self, **kwargs):
        """异域转同域或退出"""
        self._reload()

    def _onFrameDetached(self, **kwargs):
        """同域变异域"""
        self.browser._frames.pop(kwargs['frameId'], None)
        if kwargs['frameId'] == self._frame_id:
            self._reload()

    # ----------挂件----------
    @property
    def scroll(self):
        """返回用于滚动的对象"""
        self.wait.doc_loaded()
        if self._scroll is None:
            self._scroll = FrameScroller(self)
        return self._scroll

    @property
    def set(self):
        """返回用于设置的对象"""
        if self._set is None:
            self._set = ChromiumFrameSetter(self)
        return self._set

    @property
    def states(self):
        """返回用于获取状态信息的对象"""
        if self._states is None:
            self._states = FrameStates(self)
        return self._states

    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = FrameWaiter(self)
        return self._wait

    @property
    def rect(self):
        """返回获取坐标和大小的对象"""
        if self._rect is None:
            self._rect = FrameRect(self)
        return self._rect

    @property
    def listen(self):
        """返回用于聆听数据包的对象"""
        if self._listener is None:
            self._listener = FrameListener(self)
        return self._listener

    # ----------挂件结束----------

    @property
    def _obj_id(self):
        """返回frame元素的object id"""
        return self.frame_ele._obj_id

    @property
    def _node_id(self):
        """返回cdp中的node id"""
        return self.frame_ele._node_id

    @property
    def page(self):
        """返回所属Page对象"""
        return self._page

    @property
    def owner(self):
        """返回所属页面对象"""
        return self.frame_ele.owner

    @property
    def frame_ele(self):
        """返回总页面上的frame元素"""
        return self._frame_ele

    @property
    def tag(self):
        """返回元素tag"""
        return self.frame_ele.tag

    @property
    def url(self):
        """返回frame当前访问的url"""
        try:
            return self.doc_ele.run_js('return this.location.href;')
        except JavaScriptError:
            return None

    @property
    def html(self):
        """返回元素outerHTML文本"""
        tag = self.tag
        out_html = self._target_page.run_cdp('DOM.getOuterHTML', backendNodeId=self.frame_ele._backend_id)['outerHTML']
        sign = search(rf'<{tag}.*?>', out_html, DOTALL).group(0)
        return f'{sign}{self.inner_html}</{tag}>'

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        return self.doc_ele.run_js('return this.documentElement.outerHTML;')

    @property
    def title(self):
        """返回页面title"""
        r = self._ele('t:title', raise_err=False)
        return r.text if r else None

    @property
    def attrs(self):
        """返回frame元素所有attribute属性"""
        return self.frame_ele.attrs

    @property
    def active_ele(self):
        """返回当前焦点所在元素"""
        return self.doc_ele.run_js('return this.activeElement;')

    @property
    def xpath(self):
        """返回frame的xpath绝对路径"""
        return self.frame_ele.xpath

    @property
    def css_path(self):
        """返回frame的css selector绝对路径"""
        return self.frame_ele.css_path

    @property
    def tab_id(self):
        """返回frame所在tab的id"""
        return self._tab_id

    @property
    def download_path(self):
        return self._download_path

    @property
    def _js_ready_state(self):
        """返回当前页面加载状态，'loading' 'interactive' 'complete'"""
        if self._is_diff_domain:
            return super()._js_ready_state

        else:
            try:
                return self.doc_ele.run_js('return this.readyState;')
            except ContextLostError:
                try:
                    node = self.run_cdp('DOM.describeNode', backendNodeId=self.frame_ele._backend_id)['node']
                    doc = ChromiumElement(self._target_page, backend_id=node['contentDocument']['backendNodeId'])
                    return doc.run_js('return this.readyState;')
                except:
                    return None

    def refresh(self):
        """刷新frame页面"""
        self.doc_ele.run_js('this.location.reload();')

    def property(self, name):
        """返回frame元素一个property属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        return self.frame_ele.property(name)

    def attr(self, name):
        """返回frame元素一个attribute属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        return self.frame_ele.attr(name)

    def remove_attr(self, name):
        """删除frame元素attribute属性
        :param name: 属性名
        :return: None
        """
        self.frame_ele.remove_attr(name)

    def run_js(self, script, *args, as_expr=False, timeout=None):
        """运行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        if script.startswith('this.scrollIntoView'):
            return self.frame_ele.run_js(script, *args, as_expr=as_expr, timeout=timeout)
        else:
            return self.doc_ele.run_js(script, *args, as_expr=as_expr, timeout=timeout)

    def parent(self, level_or_loc=1, index=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，1开始，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果，1开始
        :return: 上级元素对象
        """
        return self.frame_ele.parent(level_or_loc, index)

    def prev(self, locator='', index=1, timeout=0, ele_only=True):
        """返回当前元素前面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点
        """
        return self.frame_ele.prev(locator, index, timeout, ele_only=ele_only)

    def next(self, locator='', index=1, timeout=0, ele_only=True):
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点
        """
        return self.frame_ele.next(locator, index, timeout, ele_only=ele_only)

    def before(self, locator='', index=1, timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        return self.frame_ele.before(locator, index, timeout, ele_only=ele_only)

    def after(self, locator='', index=1, timeout=None, ele_only=True):
        """返回文档中此当前元素后面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        return self.frame_ele.after(locator, index, timeout, ele_only=ele_only)

    def prevs(self, locator='', timeout=0, ele_only=True):
        """返回当前元素前面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点文本组成的列表
        """
        return self.frame_ele.prevs(locator, timeout, ele_only=ele_only)

    def nexts(self, locator='', timeout=0, ele_only=True):
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点文本组成的列表
        """
        return self.frame_ele.nexts(locator, timeout, ele_only=ele_only)

    def befores(self, locator='', timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        return self.frame_ele.befores(locator, timeout, ele_only=ele_only)

    def afters(self, locator='', timeout=None, ele_only=True):
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        return self.frame_ele.afters(locator, timeout, ele_only=ele_only)

    def get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 文件保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :return: 图片完整路径或字节文本
        """
        return self.frame_ele.get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64)

    def _get_screenshot(self, path=None, name=None, as_bytes: [bool, str] = None, as_base64: [bool, str] = None,
                        full_page=False, left_top=None, right_bottom=None, ele=None):
        """实现截图
        :param path: 文件保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :param ele: 为异域iframe内元素截图设置
        :return: 图片完整路径或字节文本
        """
        if not self._is_diff_domain:
            return super().get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                          full_page=full_page, left_top=left_top, right_bottom=right_bottom)

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
            if path and path.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                pic_type = path.rsplit('.', 1)[-1]

            elif name and name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                pic_type = name.rsplit('.', 1)[-1]

            else:
                pic_type = 'jpeg'

            if pic_type == 'jpg':
                pic_type = 'jpeg'

        self.frame_ele.scroll.to_see(center=True)
        self.scroll.to_see(ele, center=True)
        cx, cy = ele.rect.viewport_location
        w, h = ele.rect.size
        img_data = f'data:image/{pic_type};base64,{self.frame_ele.get_screenshot(as_base64=True)}'
        body = self.tab('t:body')
        first_child = body('c::first-child')
        if not isinstance(first_child, ChromiumElement):
            first_child = first_child.frame_ele
        js = f'''
        img = document.createElement('img');
        img.src = "{img_data}";
        img.style.setProperty("z-index",9999999);
        img.style.setProperty("position","fixed");
        arguments[0].insertBefore(img, this);
        return img;'''
        new_ele = first_child.run_js(js, body)
        new_ele.scroll.to_see(center=True)
        top = int(self.frame_ele.style('border-top').split('px')[0])
        left = int(self.frame_ele.style('border-left').split('px')[0])

        r = self.tab.run_cdp('Page.getLayoutMetrics')['visualViewport']
        sx = r['pageX']
        sy = r['pageY']
        r = self.tab.get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                    left_top=(cx + left + sx, cy + top + sy),
                                    right_bottom=(cx + w + left + sx, cy + h + top + sy))
        self.tab.remove_ele(new_ele)
        return r

    def _find_elements(self, locator, timeout=None, index=1, relative=False, raise_err=None):
        """在frame内查找单个元素
        :param locator: 定位符或元素对象
        :param timeout: 查找超时时间（秒）
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象
        """
        if isinstance(locator, ChromiumElement):
            return locator
        self.wait.doc_loaded()
        return self.doc_ele._ele(locator, index=index, timeout=timeout,
                                 raise_err=raise_err) if index is not None else self.doc_ele.eles(locator, timeout)

    def _is_inner_frame(self):
        """返回当前frame是否同域"""
        return self._frame_id in str(self._target_page.run_cdp('Page.getFrameTree')['frameTree'])
