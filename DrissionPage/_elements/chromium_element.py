# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from json import loads
from os.path import basename
from pathlib import Path
from re import search
from time import perf_counter, sleep

from DataRecorder.tools import get_usable_path, make_valid_name

from .none_element import NoneElement
from .session_element import make_session_ele
from .._base.base import DrissionElement, BaseElement
from .._functions.keys import input_text_or_keys
from .._functions.locator import get_loc, locator_to_tuple
from .._functions.elements import ChromiumElementsList
from .._functions.web import make_absolute_link, get_ele_txt, format_html, is_js_func, offset_scroll, get_blob
from .._units.clicker import Clicker
from .._units.rect import ElementRect
from .._units.scroller import ElementScroller
from .._units.selector import SelectElement
from .._units.setter import ChromiumElementSetter
from .._units.states import ElementStates, ShadowRootStates
from .._units.waiter import ElementWaiter
from ..errors import ContextLostError, ElementLostError, JavaScriptError, CDPError, NoResourceError, AlertExistsError, \
    NoRectError

__FRAME_ELEMENT__ = ('iframe', 'frame')


class ChromiumElement(DrissionElement):
    """控制浏览器元素的对象"""

    def __init__(self, owner, node_id=None, obj_id=None, backend_id=None):
        """node_id、obj_id和backend_id必须至少传入一个
        :param owner: 元素所在页面对象
        :param node_id: cdp中的node id
        :param obj_id: js中的object id
        :param backend_id: backend id
        """
        super().__init__(owner)
        self.tab = self.owner.tab
        self._select = None
        self._scroll = None
        self._rect = None
        self._set = None
        self._states = None
        self._pseudo = None
        self._clicker = None
        self._tag = None
        self._wait = None
        self._type = 'ChromiumElement'
        self._doc_id = None

        if node_id and obj_id and backend_id:
            self._node_id = node_id
            self._obj_id = obj_id
            self._backend_id = backend_id
        elif node_id:
            self._node_id = node_id
            self._obj_id = self._get_obj_id(node_id)
            self._backend_id = self._get_backend_id(self._node_id)
        elif obj_id:
            self._node_id = self._get_node_id(obj_id)
            self._obj_id = obj_id
            self._backend_id = self._get_backend_id(self._node_id)
        elif backend_id:
            self._obj_id = self._get_obj_id(backend_id=backend_id)
            self._node_id = self._get_node_id(obj_id=self._obj_id)
            self._backend_id = backend_id
        else:
            raise ElementLostError

    def __repr__(self):
        attrs = [f"{k}='{v}'" for k, v in self.attrs.items()]
        return f'<ChromiumElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, locator, index=1, timeout=None):
        """在内部查找元素
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间（秒）
        :return: ChromiumElement对象或属性、文本
        """
        return self.ele(locator, index=index, timeout=timeout)

    def __eq__(self, other):
        return self._backend_id == getattr(other, '_backend_id', None)

    @property
    def tag(self):
        """返回元素tag"""
        if self._tag is None:
            self._tag = self.owner.run_cdp('DOM.describeNode',
                                           backendNodeId=self._backend_id)['node']['localName'].lower()
        return self._tag

    @property
    def html(self):
        """返回元素outerHTML文本"""
        return self.owner.run_cdp('DOM.getOuterHTML', backendNodeId=self._backend_id)['outerHTML']

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        return self.run_js('return this.innerHTML;')

    @property
    def attrs(self):
        """返回元素所有attribute属性"""
        try:
            attrs = self.owner.run_cdp('DOM.getAttributes', nodeId=self._node_id)['attributes']
            return {attrs[i]: attrs[i + 1] for i in range(0, len(attrs), 2)}
        except ElementLostError:
            self._refresh_id()
            attrs = self.owner.run_cdp('DOM.getAttributes', nodeId=self._node_id)['attributes']
            return {attrs[i]: attrs[i + 1] for i in range(0, len(attrs), 2)}
        except CDPError:  # 文档根元素不能调用此方法
            return {}

    @property
    def text(self):
        """返回元素内所有文本，文本已格式化"""
        return get_ele_txt(make_session_ele(self.html))

    @property
    def raw_text(self):
        """返回未格式化处理的元素内文本"""
        return self.property('innerText')

    # -----------------d模式独有属性-------------------
    @property
    def set(self):
        """返回用于设置元素属性的对象"""
        if self._set is None:
            self._set = ChromiumElementSetter(self)
        return self._set

    @property
    def states(self):
        """返回用于获取元素状态的对象"""
        if self._states is None:
            self._states = ElementStates(self)
        return self._states

    @property
    def pseudo(self):
        """返回用于获取伪元素内容的对象"""
        if self._pseudo is None:
            self._pseudo = Pseudo(self)
        return self._pseudo

    @property
    def rect(self):
        """返回用于获取元素位置的对象"""
        if self._rect is None:
            self._rect = ElementRect(self)
        return self._rect

    @property
    def shadow_root(self):
        """返回当前元素的shadow_root元素对象"""
        info = self.owner.run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
        if not info.get('shadowRoots', None):
            return None

        return ShadowRoot(self, backend_id=info['shadowRoots'][0]['backendNodeId'])

    @property
    def sr(self):
        """返回当前元素的shadow_root元素对象"""
        return self.shadow_root

    @property
    def scroll(self):
        """用于滚动滚动条的对象"""
        if self._scroll is None:
            self._scroll = ElementScroller(self)
        return self._scroll

    @property
    def click(self):
        """返回用于点击的对象"""
        if self._clicker is None:
            self._clicker = Clicker(self)
        return self._clicker

    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = ElementWaiter(self.owner, self)
        return self._wait

    @property
    def select(self):
        """返回专门处理下拉列表的Select类，非下拉列表元素返回False"""
        if self._select is None:
            if self.tag != 'select':
                self._select = False
            else:
                self._select = SelectElement(self)

        return self._select

    @property
    def value(self):
        return self.property('value')

    def check(self, uncheck=False, by_js=False):
        """选中或取消选中当前元素
        :param uncheck: 是否取消选中
        :param by_js: 是否用js执行
        :return: None
        """
        is_checked = self.states.is_checked
        if by_js:
            js = None
            if is_checked and uncheck:
                js = 'this.checked=false'
            elif not is_checked and not uncheck:
                js = 'this.checked=true'
            if js:
                self.run_js(js)
                self.run_js('this.dispatchEvent(new Event("change", {bubbles: true}));')

        else:
            if (is_checked and uncheck) or (not is_checked and not uncheck):
                self.click()

    def parent(self, level_or_loc=1, index=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，1开始，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果，1开始
        :return: 上级元素对象
        """
        return super().parent(level_or_loc, index)

    def child(self, locator='', index=1, timeout=None, ele_only=True):
        """返回当前元素的一个符合条件的直接子元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本
        """
        return super().child(locator, index, timeout, ele_only=ele_only)

    def prev(self, locator='', index=1, timeout=None, ele_only=True):
        """返回当前元素前面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本
        """
        return super().prev(locator, index, timeout, ele_only=ele_only)

    def next(self, locator='', index=1, timeout=None, ele_only=True):
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本
        """
        return super().next(locator, index, timeout, ele_only=ele_only)

    def before(self, locator='', index=1, timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        return super().before(locator, index, timeout, ele_only=ele_only)

    def after(self, locator='', index=1, timeout=None, ele_only=True):
        """返回文档中此当前元素后面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        return super().after(locator, index, timeout, ele_only=ele_only)

    def children(self, locator='', timeout=None, ele_only=True):
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        return ChromiumElementsList(self.owner, super().children(locator, timeout, ele_only=ele_only))

    def prevs(self, locator='', timeout=None, ele_only=True):
        """返回当前元素前面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return ChromiumElementsList(self.owner, super().prevs(locator, timeout, ele_only=ele_only))

    def nexts(self, locator='', timeout=None, ele_only=True):
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return ChromiumElementsList(self.owner, super().nexts(locator, timeout, ele_only=ele_only))

    def befores(self, locator='', timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        return ChromiumElementsList(self.owner, super().befores(locator, timeout, ele_only=ele_only))

    def afters(self, locator='', timeout=None, ele_only=True):
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        return ChromiumElementsList(self.owner, super().afters(locator, timeout, ele_only=ele_only))

    def over(self, timeout=None):
        """获取覆盖在本元素上最上层的元素
        :param timeout: 等待元素出现的超时时间（秒）
        :return: 元素对象
        """
        timeout = timeout if timeout is None else self.owner.timeout
        bid = self.wait.covered(timeout=timeout)
        if bid:
            return ChromiumElement(owner=self.owner, backend_id=bid)
        else:
            return NoneElement(page=self.owner, method='on()', args={'timeout': timeout})

    def offset(self, offset_x, offset_y):
        """获取相对本元素左上角左边指定偏移量位置的元素
        :param offset_x: 横坐标偏移量，向右为正
        :param offset_y: 纵坐标偏移量，向下为正
        :return: 元素对象
        """
        x, y = self.rect.location
        try:
            return ChromiumElement(owner=self.owner,
                                   backend_id=self.owner.run_cdp('DOM.getNodeForLocation', x=x + offset_x,
                                                                 y=y + offset_y, includeUserAgentShadowDOM=True,
                                                                 ignorePointerEventsNone=False)['backendNodeId'])
        except CDPError:
            return NoneElement(page=self.owner, method='offset()', args={'offset_x': offset_x, 'offset_y': offset_y})

    def east(self, loc_or_pixel=None, index=1):
        """获取元素右边某个指定元素
        :param loc_or_pixel: 定位符，只支持str或int，且不支持xpath和css方式，传入int按像素距离获取
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        return self._get_relative_eles(mode='east', locator=loc_or_pixel, index=index)

    def south(self, loc_or_pixel=None, index=1):
        """获取元素下方某个指定元素
        :param loc_or_pixel: 定位符，只支持str或int，且不支持xpath和css方式，传入int按像素距离获取
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        return self._get_relative_eles(mode='south', locator=loc_or_pixel, index=index)

    def west(self, loc_or_pixel=None, index=1):
        """获取元素左边某个指定元素
        :param loc_or_pixel: 定位符，只支持str或int，且不支持xpath和css方式，传入int按像素距离获取
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        return self._get_relative_eles(mode='west', locator=loc_or_pixel, index=index)

    def north(self, loc_or_pixel=None, index=1):
        """获取元素上方某个指定元素
        :param loc_or_pixel: 定位符，只支持str或int，且不支持xpath和css方式，传入int按像素距离获取
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        return self._get_relative_eles(mode='north', locator=loc_or_pixel, index=index)

    def _get_relative_eles(self, mode='north', locator=None, index=1):
        """获取元素下方某个指定元素
        :param locator: 定位符，只支持str或int，且不支持xpath和css方式
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        if locator and not (isinstance(locator, str) and not locator.startswith(
                ('x:', 'xpath:', 'x=', 'xpath=', 'c:', 'css:', 'c=', 'css=')) or isinstance(locator, int)):
            raise ValueError('locator参数只能是str格式且不支持xpath和css形式。')
        rect = self.states.has_rect
        if not rect:
            raise NoRectError

        if mode == 'east':
            cdp_data = {'x': int(rect[1][0]), 'y': int(self.rect.midpoint[1]),
                        'includeUserAgentShadowDOM': True, 'ignorePointerEventsNone': False}
            variable = 'x'
            minus = False
        elif mode == 'south':
            cdp_data = {'x': int(self.rect.midpoint[0]), 'y': int(rect[2][1]),
                        'includeUserAgentShadowDOM': True, 'ignorePointerEventsNone': False}
            variable = 'y'
            minus = False
        elif mode == 'west':
            cdp_data = {'x': int(rect[0][0]), 'y': int(self.rect.midpoint[1]),
                        'includeUserAgentShadowDOM': True, 'ignorePointerEventsNone': False}
            variable = 'x'
            minus = True
        else:  # north
            cdp_data = {'x': int(self.rect.midpoint[0]), 'y': int(rect[0][1]),
                        'includeUserAgentShadowDOM': True, 'ignorePointerEventsNone': False}
            variable = 'y'
            minus = True

        if isinstance(locator, int):
            if minus:
                cdp_data[variable] -= locator
            else:
                cdp_data[variable] += locator
            try:
                return ChromiumElement(owner=self.owner,
                                       backend_id=self.owner.run_cdp('DOM.getNodeForLocation',
                                                                     **cdp_data)['backendNodeId'])
            except CDPError:
                return NoneElement(page=self.owner, method=f'{mode}()', args={'locator': locator})

        num = 0
        value = -8 if minus else 8
        size = self.owner.rect.size
        max_len = size[0] if mode == 'east' else size[1]
        loc_data = locator_to_tuple(locator) if locator else None
        curr_ele = None
        while 0 < cdp_data[variable] < max_len:
            cdp_data[variable] += value
            try:
                bid = self.owner.run_cdp('DOM.getNodeForLocation', **cdp_data)['backendNodeId']
                if bid == curr_ele:
                    continue
                else:
                    curr_ele = bid
                ele = ChromiumElement(self.owner, backend_id=bid)

                if loc_data is None or _check_ele(ele, loc_data):
                    num += 1
                    if num == index:
                        return ele
            except:
                pass

        return NoneElement(page=self.owner, method=f'{mode}()', args={'locator': locator})

    def attr(self, attr):
        """返回一个attribute属性值
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        attrs = self.attrs
        if attr == 'href':  # 获取href属性时返回绝对url
            link = attrs.get('href')
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link
            else:
                return make_absolute_link(link, self.property('baseURI'))

        elif attr == 'src':
            return make_absolute_link(attrs.get('src'), self.property('baseURI'))

        elif attr == 'text':
            return self.text

        elif attr == 'innerText':
            return self.raw_text

        elif attr in ('html', 'outerHTML'):
            return self.html

        elif attr == 'innerHTML':
            return self.inner_html

        else:
            return attrs.get(attr, None)

    def remove_attr(self, name):
        """删除元素一个attribute属性
        :param name: 属性名
        :return: None
        """
        self.run_js(f'this.removeAttribute("{name}");')

    def property(self, name):
        """获取一个property属性值
        :param name: 属性名
        :return: 属性值文本
        """
        try:
            value = self.run_js(f'return this.{name};')
            return format_html(value) if isinstance(value, str) else value
        except:
            return None

    def run_js(self, script, *args, as_expr=False, timeout=None):
        """对本元素执行javascript代码
        :param script: js文本，文本中用this表示本元素
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        return run_js(self, script, as_expr, self.owner.timeouts.script if timeout is None else timeout, args)

    def run_async_js(self, script, *args, as_expr=False):
        """以异步方式对本元素执行javascript代码
        :param script: js文本，文本中用this表示本元素
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: None
        """
        run_js(self, script, as_expr, 0, args)

    def ele(self, locator, index=1, timeout=None):
        """返回当前元素下级符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本
        """
        return self._ele(locator, timeout, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本组成的列表
        """
        return self._ele(locator, timeout=timeout, index=None)

    def s_ele(self, locator=None, index=1):
        """查找一个符合条件的元素，以SessionElement形式返回
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, locator, index=index, method='s_ele()')

    def s_eles(self, locator=None):
        """查找所有符合条件的元素，以SessionElement列表形式返回
        :param locator: 定位符
        :return: SessionElement或属性、文本组成的列表
        """
        return make_session_ele(self, locator, index=None)

    def _find_elements(self, locator, timeout=None, index=1, relative=False, raise_err=None):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒）
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或文本、属性或其组成的列表
        """
        return find_in_chromium_ele(self, locator, index, timeout, relative=relative)

    def style(self, style, pseudo_ele=''):
        """返回元素样式属性值，可获取伪元素属性值
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"' if pseudo_ele.startswith(':') else f', "::{pseudo_ele}"'
        return self.run_js(f'return window.getComputedStyle(this{pseudo_ele}).getPropertyValue("{style}");')

    def src(self, timeout=None, base64_to_bytes=True):
        """返回元素src资源，base64的可转为bytes返回，其它返回str
        :param timeout: 等待资源加载的超时时间（秒）
        :param base64_to_bytes: 为True时，如果是base64数据，转换为bytes格式
        :return: 资源内容
        """
        timeout = self.owner.timeout if timeout is None else timeout
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" '
                  '&& this.naturalWidth > 0 && typeof this.naturalHeight != "undefined" '
                  '&& this.naturalHeight > 0')
            end_time = perf_counter() + timeout
            while not self.run_js(js) and perf_counter() < end_time:
                sleep(.1)

        src = self.attr('src')
        if not src:
            raise RuntimeError('元素没有src值或该值为空。')
        if src.lower().startswith('data:image'):
            if base64_to_bytes:
                from base64 import b64decode
                return b64decode(src.split(',', 1)[-1])
            else:
                return src.split(',', 1)[-1]

        is_blob = src.startswith('blob')
        result = None
        end_time = perf_counter() + timeout
        if is_blob:
            while perf_counter() < end_time:
                result = get_blob(self.owner, src, base64_to_bytes)
                if result:
                    break
                sleep(.05)

        else:
            while perf_counter() < end_time:
                src = self.property('currentSrc')
                if not src:
                    continue

                node = self.owner.run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
                frame = node.get('frameId', None) or self.owner._frame_id

                try:
                    result = self.owner.run_cdp('Page.getResourceContent', frameId=frame, url=src)
                    break
                except CDPError:
                    pass
                sleep(.1)

        if not result:
            return None

        elif is_blob:
            return result

        elif result['base64Encoded'] and base64_to_bytes:
            from base64 import b64decode
            return b64decode(result['content'])
        else:
            return result['content']

    def save(self, path=None, name=None, timeout=None, rename=True):
        """保存图片或其它有src属性的元素的资源
        :param path: 文件保存路径，为None时保存到当前文件夹
        :param name: 文件名称，为None时从资源url获取
        :param timeout: 等待资源加载的超时时间（秒）
        :param rename: 遇到重名文件时是否自动重命名
        :return: 返回保存路径
        """
        data = self.src(timeout=timeout)
        if not data:
            raise NoResourceError

        path = path or '.'
        if not name and self.tag == 'img':
            src = self.attr('src')
            if src.lower().startswith('data:image'):
                r = search(r'data:image/(.*?);base64,', src)
                name = f'img.{r.group(1)}' if r else None
        path = Path(path) / make_valid_name(name or basename(self.property('currentSrc')))
        if not path.suffix:
            path = path.with_suffix('.jpg')
        if rename:
            path = get_usable_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path = path.absolute()
        write_type = 'wb' if isinstance(data, bytes) else 'w'

        with open(path, write_type) as f:
            f.write(data)

        return str(path)

    def get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None, scroll_to_center=True):
        """对当前元素截图，可保存到文件，或以字节方式返回
        :param path: 文件保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param scroll_to_center: 截图前是否滚动到视口中央
        :return: 图片完整路径或字节文本
        """
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" && this.naturalWidth > 0 '
                  '&& typeof this.naturalHeight != "undefined" && this.naturalHeight > 0')
            end_time = perf_counter() + self.owner.timeout
            while not self.run_js(js) and perf_counter() < end_time:
                sleep(.1)
        if scroll_to_center:
            self.scroll.to_see(center=True)

        left, top = self.rect.location
        width, height = self.rect.size
        left_top = (left, top)
        right_bottom = (left + width, top + height)
        if not name:
            name = f'{self.tag}.jpg'

        return self.owner._get_screenshot(path, name, as_bytes=as_bytes, as_base64=as_base64, full_page=False,
                                          left_top=left_top, right_bottom=right_bottom, ele=self)

    def input(self, vals, clear=False, by_js=False):
        """输入文本或组合键，也可用于输入文件路径到input元素（路径间用\n间隔）
        :param vals: 文本值或按键组合
        :param clear: 输入前是否清空文本框
        :param by_js: 是否用js方式输入，不能输入组合键
        :return: None
        """
        if self.tag == 'input' and self.attr('type') == 'file':
            return self._set_file_input(vals)

        if by_js:
            if clear:
                self.clear(True)
            if isinstance(vals, (list, tuple)):
                vals = ''.join([str(i) for i in vals])
            self.set.property('value', str(vals))
            self.run_js('this.dispatchEvent(new Event("change", {bubbles: true}));')
            return

        self.wait.clickable(wait_moved=False, timeout=.5)
        if clear and vals not in ('\n', '\ue007'):
            self.clear(by_js=False)
        else:
            self._input_focus()

        input_text_or_keys(self.owner, vals)

    def clear(self, by_js=False):
        """清空元素文本
        :param by_js: 是否用js方式清空，为False则用全选+del模拟输入删除
        :return: None
        """
        if by_js:
            self.run_js("this.value='';")
            self.run_js('this.dispatchEvent(new Event("change", {bubbles: true}));')
            return

        self._input_focus()
        self.input(('\ue009', 'a', '\ue017'), clear=False)

    def _input_focus(self):
        """输入前使元素获取焦点"""
        try:
            self.owner.run_cdp('DOM.focus', backendNodeId=self._backend_id)
        except Exception:
            self.click(by_js=None)

    def focus(self):
        """使元素获取焦点"""
        try:
            self.owner.run_cdp('DOM.focus', backendNodeId=self._backend_id)
        except Exception:
            self.run_js('this.focus();')

    def hover(self, offset_x=None, offset_y=None):
        """鼠标悬停，可接受偏移量，偏移量相对于元素左上角坐标。不传入x或y值时悬停在元素中点
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        self.owner.scroll.to_see(self)
        x, y = offset_scroll(self, offset_x, offset_y)
        self.owner.run_cdp('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y, _ignore=AlertExistsError)

    def drag(self, offset_x=0, offset_y=0, duration=.5):
        """拖拽当前元素到相对位置
        :param offset_x: x变化值
        :param offset_y: y变化值
        :param duration: 拖动用时，传入0即瞬间到达
        :return: None
        """
        curr_x, curr_y = self.rect.midpoint
        offset_x += curr_x
        offset_y += curr_y
        self.drag_to((offset_x, offset_y), duration)

    def drag_to(self, ele_or_loc, duration=.5):
        """拖拽当前元素，目标为另一个元素或坐标元组(x, y)
        :param ele_or_loc: 另一个元素或坐标元组，坐标为元素中点的坐标
        :param duration: 拖动用时，传入0即瞬间到达
        :return: None
        """
        if isinstance(ele_or_loc, ChromiumElement):
            ele_or_loc = ele_or_loc.rect.midpoint
        elif not isinstance(ele_or_loc, (list, tuple)):
            raise TypeError('需要ChromiumElement对象或坐标。')
        self.owner.actions.hold(self).move_to(ele_or_loc, duration=duration).release()

    def _get_obj_id(self, node_id=None, backend_id=None):
        """根据传入node id或backend id获取js中的object id
        :param node_id: cdp中的node id
        :param backend_id: backend id
        :return: js中的object id
        """
        if node_id:
            return self.owner.run_cdp('DOM.resolveNode', nodeId=node_id)['object']['objectId']
        else:
            return self.owner.run_cdp('DOM.resolveNode', backendNodeId=backend_id)['object']['objectId']

    def _get_node_id(self, obj_id=None, backend_id=None):
        """根据传入object id或backend id获取cdp中的node id
        :param obj_id: js中的object id
        :param backend_id: backend id
        :return: cdp中的node id
        """
        if obj_id:
            return self.owner.run_cdp('DOM.requestNode', objectId=obj_id)['nodeId']
        else:
            n = self.owner.run_cdp('DOM.describeNode', backendNodeId=backend_id)['node']
            self._tag = n['localName']
            return n['nodeId']

    def _get_backend_id(self, node_id):
        """根据传入node id获取backend id
        :param node_id:
        :return: backend id
        """
        n = self.owner.run_cdp('DOM.describeNode', nodeId=node_id)['node']
        self._tag = n['localName']
        return n['backendNodeId']

    def _refresh_id(self):
        """根据backend id刷新其它id"""
        self._obj_id = self._get_obj_id(backend_id=self._backend_id)
        self._node_id = self._get_node_id(obj_id=self._obj_id)

    def _get_ele_path(self, mode):
        """返获取绝对的css路径或xpath路径"""
        if mode == 'xpath':
            txt1 = 'let tag = el.nodeName.toLowerCase();'
            txt3 = ''' && sib.nodeName.toLowerCase()==tag'''
            txt4 = '''
            if(nth>1){path = '/' + tag + '[' + nth + ']' + path;}
                    else{path = '/' + tag + path;}'''
            txt5 = '''return path;'''

        elif mode == 'css':
            txt1 = ''
            txt3 = ''
            txt4 = '''path = '>' + el.tagName.toLowerCase() + ":nth-child(" + nth + ")" + path;'''
            txt5 = '''return path.substr(1);'''

        else:
            raise ValueError(f"mode参数只能是'xpath'或'css'，现在是：'{mode}'。")

        js = '''function(){
        function e(el) {
            if (!(el instanceof Element)) return;
            let path = '';
            while (el.nodeType === Node.ELEMENT_NODE) {
                ''' + txt1 + '''
                    let sib = el, nth = 0;
                    while (sib) {
                        if(sib.nodeType === Node.ELEMENT_NODE''' + txt3 + '''){nth += 1;}
                        sib = sib.previousSibling;
                    }
                    ''' + txt4 + '''
                el = el.parentNode;
            }
            ''' + txt5 + '''
        }
        return e(this);}
        '''
        t = self.run_js(js)
        return f'{t}' if mode == 'css' else t

    def _set_file_input(self, files):
        """对上传控件写入路径
        :param files: 文件路径列表或字符串，字符串时多个文件用回车分隔
        :return: None
        """
        if isinstance(files, str):
            files = files.split('\n')
        files = [str(Path(i).absolute()) for i in files]
        self.owner.run_cdp('DOM.setFileInputFiles', files=files, backendNodeId=self._backend_id)


class ShadowRoot(BaseElement):
    """ShadowRoot是用于处理ShadowRoot的类，使用方法和ChromiumElement基本一致"""

    def __init__(self, parent_ele, obj_id=None, backend_id=None):
        """
        :param parent_ele: shadow root 所在父元素
        :param obj_id: js中的object id
        :param backend_id: cdp中的backend id
        """
        super().__init__(parent_ele.owner)
        self.tab = self.owner.tab
        self.parent_ele = parent_ele
        if backend_id:
            self._backend_id = backend_id
            self._obj_id = self._get_obj_id(backend_id)
            self._node_id = self._get_node_id(self._obj_id)
        elif obj_id:
            self._obj_id = obj_id
            self._node_id = self._get_node_id(obj_id)
            self._backend_id = self._get_backend_id(self._node_id)
        self._states = None
        self._type = 'ShadowRoot'

    def __repr__(self):
        return f'<ShadowRoot in {self.parent_ele}>'

    def __call__(self, locator, index=1, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 超时时间（秒）
        :return: 元素对象或属性、文本
        """
        return self.ele(locator, index=index, timeout=timeout)

    def __eq__(self, other):
        return self._backend_id == getattr(other, '_backend_id', None)

    @property
    def tag(self):
        """返回元素标签名"""
        return 'shadow-root'

    @property
    def html(self):
        """返回outerHTML文本"""
        return f'<shadow_root>{self.inner_html}</shadow_root>'

    @property
    def inner_html(self):
        """返回内部的html文本"""
        return self.run_js('return this.innerHTML;')

    @property
    def states(self):
        """返回用于获取元素状态的对象"""
        if self._states is None:
            self._states = ShadowRootStates(self)
        return self._states

    def run_js(self, script, *args, as_expr=False, timeout=None):
        """运行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        return run_js(self, script, as_expr, self.owner.timeouts.script if timeout is None else timeout, args)

    def run_async_js(self, script, *args, as_expr=False, timeout=None):
        """以异步方式执行js代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: None
        """
        from threading import Thread
        Thread(target=run_js, args=(self, script, as_expr,
                                    self.owner.timeouts.script if timeout is None else timeout, args)).start()

    def parent(self, level_or_loc=1, index=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果
        :return: ChromiumElement对象
        """
        if isinstance(level_or_loc, int):
            loc = f'xpath:./ancestor-or-self::*[{level_or_loc}]'

        elif isinstance(level_or_loc, (tuple, str)):
            loc = get_loc(level_or_loc, True)

            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')

            loc = f'xpath:./ancestor-or-self::{loc[1].lstrip(". / ")}[{index}]'

        else:
            raise TypeError('level_or_loc参数只能是tuple、int或str。')

        return self.parent_ele._ele(loc, timeout=0, relative=True, raise_err=False, method='parent()')

    def child(self, locator='', index=1):
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :return: 直接子元素或节点文本组成的列表
        """
        if not locator:
            loc = '*'
        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        ele = self._ele(loc, index=index, relative=True)

        return ele if ele else NoneElement(self.owner, 'child()', {'locator': locator, 'index': index})

    def next(self, locator='', index=1):
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :return: ChromiumElement对象
        """
        loc = get_loc(locator, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./{loc}'
        ele = self.parent_ele._ele(xpath, index=index, relative=True)

        return ele if ele else NoneElement(self.owner, 'next()', {'locator': locator, 'index': index})

    def before(self, locator='', index=1):
        """返回文档中当前元素前面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :return: 本元素前面的某个元素或节点
        """
        loc = get_loc(locator, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./preceding::{loc}'
        ele = self.parent_ele._ele(xpath, index=index, relative=True)

        return ele if ele else NoneElement(self.owner, 'before()', {'locator': locator, 'index': index})

    def after(self, locator='', index=1):
        """返回文档中此当前元素后面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :return: 本元素后面的某个元素或节点
        """
        nodes = self.afters(locator=locator)
        return nodes[index - 1] if nodes else NoneElement(self.owner, 'after()', {'locator': locator, 'index': index})

    def children(self, locator=''):
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :return: 直接子元素或节点文本组成的列表
        """
        if not locator:
            loc = '*'
        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        return self._ele(loc, index=None, relative=True)

    def nexts(self, locator=''):
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :return: ChromiumElement对象组成的列表
        """
        loc = get_loc(locator, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./{loc}'
        return self.parent_ele._ele(xpath, index=None, relative=True)

    def befores(self, locator=''):
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :return: 本元素前面的元素或节点组成的列表
        """
        loc = get_loc(locator, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./preceding::{loc}'
        return self.parent_ele._ele(xpath, index=None, relative=True)

    def afters(self, locator=''):
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :return: 本元素后面的元素或节点组成的列表
        """
        eles1 = self.nexts(locator)
        loc = get_loc(locator, True)[1].lstrip('./')
        xpath = f'xpath:./following::{loc}'
        return eles1 + self.parent_ele._ele(xpath, index=None, relative=True)

    def ele(self, locator, index=1, timeout=None):
        """返回当前元素下级符合条件的一个元素
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: ChromiumElement对象
        """
        return self._ele(locator, timeout, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        """返回当前元素下级所有符合条件的子元素
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: ChromiumElement对象组成的列表
        """
        return self._ele(locator, timeout=timeout, index=None)

    def s_ele(self, locator=None, index=1):
        """查找一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :return: SessionElement对象或属性、文本
        """
        r = make_session_ele(self, locator, index=index)
        if isinstance(r, NoneElement):
            r.method = 's_ele()'
            r.args = {'locator': locator}
        return r

    def s_eles(self, locator):
        """查找所有符合条件的元素以SessionElement列表形式返回，处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象
        """
        return make_session_ele(self, locator, index=None)

    def _find_elements(self, locator, timeout=None, index=1, relative=False, raise_err=None):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒）
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或其组成的列表
        """
        loc = get_loc(locator, css_mode=False)
        if loc[0] == 'css selector' and str(loc[1]).startswith(':root'):
            loc = loc[0], loc[1][5:]

        def do_find():
            if loc[0] == 'css selector':
                if index == 1:
                    nod_id = self.owner.run_cdp('DOM.querySelector', nodeId=self._node_id, selector=loc[1])['nodeId']
                    if nod_id:
                        r = make_chromium_eles(self.owner, _ids=nod_id, is_obj_id=False)
                        return None if r is False else r

                else:
                    nod_ids = self.owner.run_cdp('DOM.querySelectorAll',
                                                 nodeId=self._node_id, selector=loc[1])['nodeId']
                    r = make_chromium_eles(self.owner, _ids=nod_ids, index=index, is_obj_id=False)
                    return None if r is False else r

            else:
                eles = make_session_ele(self, loc, index=None)
                if not eles:
                    return None

                css = [i.css_path[61:] for i in eles]
                if index is not None:
                    try:
                        node_id = self.owner.run_cdp('DOM.querySelector', nodeId=self._node_id,
                                                     selector=css[index - 1])['nodeId']
                    except IndexError:
                        return None
                    r = make_chromium_eles(self.owner, _ids=node_id, is_obj_id=False)
                    return None if r is False else r
                else:
                    node_ids = [self.owner.run_cdp('DOM.querySelector', nodeId=self._node_id, selector=i)['nodeId']
                                for i in css]
                    if 0 in node_ids:
                        return None
                    r = make_chromium_eles(self.owner, _ids=node_ids, index=index, is_obj_id=False)
                    return None if r is False else r

        timeout = timeout if timeout is not None else self.owner.timeout
        end_time = perf_counter() + timeout
        result = do_find()
        while result is None and perf_counter() <= end_time:
            sleep(.1)
            result = do_find()

        if result:
            return result
        return NoneElement(self.owner) if index is not None else []

    def _get_node_id(self, obj_id):
        """返回元素node id"""
        return self.owner.run_cdp('DOM.requestNode', objectId=obj_id)['nodeId']

    def _get_obj_id(self, back_id):
        """返回元素object id"""
        return self.owner.run_cdp('DOM.resolveNode', backendNodeId=back_id)['object']['objectId']

    def _get_backend_id(self, node_id):
        """返回元素object id"""
        r = self.owner.run_cdp('DOM.describeNode', nodeId=node_id)['node']
        self._tag = r['localName'].lower()
        return r['backendNodeId']


def find_in_chromium_ele(ele, locator, index=1, timeout=None, relative=True):
    """在chromium元素中查找
    :param ele: ChromiumElement对象
    :param locator: 元素定位元组
    :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
    :param timeout: 查找元素超时时间（秒）
    :param relative: WebPage用于标记是否相对定位使用
    :return: 返回ChromiumElement元素或它们组成的列表
    """
    # ---------------处理定位符---------------
    if isinstance(locator, (str, tuple)):
        loc = get_loc(locator)
    else:
        raise ValueError(f"定位符必须为str或长度为2的tuple对象。现在是：{locator}")

    loc_str = loc[1]
    if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
        loc_str = f'.{loc_str}'
    elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>'):
        loc_str = f'{ele.css_path}{loc[1]}'
    loc = loc[0], loc_str

    timeout = timeout if timeout is not None else ele.owner.timeout

    # ---------------执行查找-----------------
    if loc[0] == 'xpath':
        return find_by_xpath(ele, loc[1], index, timeout, relative=relative)

    else:
        return find_by_css(ele, loc[1], index, timeout)


def find_by_xpath(ele, xpath, index, timeout, relative=True):
    """执行用xpath在元素中查找元素
    :param ele: 在此元素中查找
    :param xpath: 查找语句
    :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
    :param timeout: 超时时间（秒）
    :param relative: 是否相对定位
    :return: ChromiumElement或其组成的列表
    """
    type_txt = '9' if index == 1 else '7'
    node_txt = 'this.contentDocument' if ele.tag in __FRAME_ELEMENT__ and not relative else 'this'
    js = make_js_for_find_ele_by_xpath(xpath, type_txt, node_txt)
    ele.owner.wait.doc_loaded()

    def do_find():
        res = ele.owner.run_cdp('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                returnByValue=False, awaitPromise=True, userGesture=True)
        if res['result']['type'] == 'string':
            return res['result']['value']
        if 'exceptionDetails' in res:
            if 'The result is not a node set' in res['result']['description']:
                js1 = make_js_for_find_ele_by_xpath(xpath, '1', node_txt)
                res = ele.owner.run_cdp('Runtime.callFunctionOn', functionDeclaration=js1, objectId=ele._obj_id,
                                        returnByValue=False, awaitPromise=True, userGesture=True)
                return res['result']['value']
            else:
                raise SyntaxError(f'查询语句错误：\n{res}')

        if res['result']['subtype'] == 'null' or res['result']['description'] in ('NodeList(0)', 'Array(0)'):
            return None

        if index == 1:
            r = make_chromium_eles(ele.owner, _ids=res['result']['objectId'], is_obj_id=True)
            return None if r is False else r

        else:
            res = ele.owner.run_cdp('Runtime.getProperties', objectId=res['result']['objectId'],
                                    ownProperties=True)['result'][:-1]
            if index is None:
                r = ChromiumElementsList(page=ele.owner)
                for i in res:
                    if i['value']['type'] == 'object':
                        r.append(make_chromium_eles(ele.owner, _ids=i['value']['objectId'], is_obj_id=True))
                    else:
                        r.append(i['value']['value'])
                return None if False in r else r

            else:
                eles_count = len(res)
                if eles_count == 0 or abs(index) > eles_count:
                    return None

                index1 = eles_count + index + 1 if index < 0 else index
                res = res[index1 - 1]
                if res['value']['type'] == 'object':
                    r = make_chromium_eles(ele.owner, _ids=res['value']['objectId'], is_obj_id=True)
                else:
                    r = res['value']['value']
                return None if r is False else r

    end_time = perf_counter() + timeout
    result = do_find()
    while result is None and perf_counter() < end_time:
        sleep(.1)
        result = do_find()

    if result:
        return result
    return NoneElement(ele.owner) if index is not None else ChromiumElementsList(page=ele.owner)


def find_by_css(ele, selector, index, timeout):
    """执行用css selector在元素中查找元素
    :param ele: 在此元素中查找
    :param selector: 查找语句
    :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
    :param timeout: 超时时间（秒）
    :return: ChromiumElement或其组成的列表
    """
    selector = selector.replace('"', r'\"')
    find_all = '' if index == 1 else 'All'
    node_txt = 'this.contentDocument' if ele.tag in ('iframe', 'frame', 'shadow-root') else 'this'
    js = f'function(){{return {node_txt}.querySelector{find_all}("{selector}");}}'

    ele.owner.wait.doc_loaded()

    def do_find():
        res = ele.owner.run_cdp('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                returnByValue=False, awaitPromise=True, userGesture=True)

        if 'exceptionDetails' in res:
            raise SyntaxError(f'查询语句错误：\n{res}')
        if res['result']['subtype'] == 'null' or res['result']['description'] in ('NodeList(0)', 'Array(0)'):
            return None

        if index == 1:
            r = make_chromium_eles(ele.owner, _ids=res['result']['objectId'], is_obj_id=True)
            return None if r is False else r

        else:
            obj_ids = [i['value']['objectId'] for i in ele.owner.run_cdp('Runtime.getProperties',
                                                                         objectId=res['result']['objectId'],
                                                                         ownProperties=True)['result']]
            r = make_chromium_eles(ele.owner, _ids=obj_ids, index=index, is_obj_id=True)
            return None if r is False else r

    end_time = perf_counter() + timeout
    result = do_find()
    while result is None and perf_counter() < end_time:
        sleep(.1)
        result = do_find()

    if result:
        return result
    return NoneElement(ele.owner) if index is not None else ChromiumElementsList(page=ele.owner)


def make_chromium_eles(page, _ids, index=1, is_obj_id=True, ele_only=False):
    """根据node id或object id生成相应元素对象
    :param page: ChromiumPage对象
    :param _ids: 元素的id列表
    :param index: 获取第几个，为None返回全部
    :param is_obj_id: 传入的id是obj id还是node id
    :param ele_only: 是否只返回ele，在页面查找元素时生效
    :return: 浏览器元素对象或它们组成的列表，生成失败返回False
    """
    if is_obj_id:
        get_node_func = _get_node_by_obj_id
    else:
        get_node_func = _get_node_by_node_id
    if not isinstance(_ids, (list, tuple)):
        _ids = (_ids,)

    if index is not None:  # 获取一个
        if ele_only:
            for obj_id in _ids:
                tmp = get_node_func(page, obj_id, ele_only)
                if tmp is not None:
                    return tmp
            return False

        else:
            obj_id = _ids[index - 1]
            return get_node_func(page, obj_id, ele_only)

    else:  # 获取全部
        nodes = ChromiumElementsList(page=page)
        for obj_id in _ids:
            tmp = get_node_func(page, obj_id, ele_only)
            if tmp is False:
                return False
            elif tmp is not None:
                nodes.append(tmp)
        return nodes


def _get_node_info(page, id_type, _id):
    if not _id:
        return False
    arg = {id_type: _id}
    node = page.driver.run('DOM.describeNode', **arg)
    if 'error' in node:
        return False
    return node


def _get_node_by_obj_id(page, obj_id, ele_only):
    """根据obj id返回元素对象或文本，ele_only时如果是文本返回None，出错返回False"""
    node = _get_node_info(page, 'objectId', obj_id)
    if node is False:
        return False
    if node['node']['nodeName'] in ('#text', '#comment'):
        return None if ele_only else node['node']['nodeValue']
    else:
        return _make_ele(page, obj_id, node)


def _get_node_by_node_id(page, node_id, ele_only):
    """根据node id返回元素对象或文本，ele_only时如果是文本返回None，出错返回False"""
    node = _get_node_info(page, 'nodeId', node_id)
    if node is False:
        return False
    if node['node']['nodeName'] in ('#text', '#comment'):
        return None if ele_only else node['node']['nodeValue']
    else:
        obj_id = page.driver.run('DOM.resolveNode', nodeId=node_id)
        if 'error' in obj_id:
            return False
        obj_id = obj_id['object']['objectId']
        return _make_ele(page, obj_id, node)


def _make_ele(page, obj_id, node):
    ele = ChromiumElement(page, obj_id=obj_id, node_id=node['node']['nodeId'],
                          backend_id=node['node']['backendNodeId'])
    if ele.tag in __FRAME_ELEMENT__:
        from .._pages.chromium_frame import ChromiumFrame
        ele = ChromiumFrame(page, ele, node)
    return ele


def make_js_for_find_ele_by_xpath(xpath, type_txt, node_txt):
    """生成用xpath在元素中查找元素的js文本
    :param xpath: xpath文本
    :param type_txt: 查找类型
    :param node_txt: 节点类型
    :return: js文本
    """
    for_txt = ''

    # 获取第一个元素、节点或属性
    if type_txt == '9':
        return_txt = '''
if(e.singleNodeValue==null){return null;}
else if(e.singleNodeValue.constructor.name=="Text"){return e.singleNodeValue.data;}
else if(e.singleNodeValue.constructor.name=="Attr"){return e.singleNodeValue.nodeValue;}
else if(e.singleNodeValue.constructor.name=="Comment"){return e.singleNodeValue.nodeValue;}
else{return e.singleNodeValue;}'''

    # 按顺序获取所有元素、节点或属性
    elif type_txt == '7':
        for_txt = """
let a=new Array();
for(let i = 0; i <e.snapshotLength ; i++){
if(e.snapshotItem(i).constructor.name=="Text"){a.push(e.snapshotItem(i).data);}
else if(e.snapshotItem(i).constructor.name=="Attr"){a.push(e.snapshotItem(i).nodeValue);}
else if(e.snapshotItem(i).constructor.name=="Comment"){a.push(e.snapshotItem(i).nodeValue);}
else{a.push(e.snapshotItem(i));}}"""
        return_txt = 'return a;'

    elif type_txt == '2':
        return_txt = 'return e.stringValue;'
    elif type_txt == '1':
        return_txt = 'return e.numberValue;'
    else:
        return_txt = 'return e.singleNodeValue;'

    xpath = xpath.replace(r"'", r"\'")
    js = f'function(){{let e=document.evaluate(\'{xpath}\',{node_txt},null,{type_txt},null);\n{for_txt}\n{return_txt}}}'

    return js


def run_js(page_or_ele, script, as_expr, timeout, args=None):
    """运行javascript代码
    :param page_or_ele: 页面对象或元素对象
    :param script: js文本
    :param as_expr: 是否作为表达式运行，为True时args无效
    :param timeout: 超时时间（秒）
    :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
    :return: js执行结果
    """
    if isinstance(page_or_ele, (ChromiumElement, ShadowRoot)):
        is_page = False
        page = page_or_ele.owner
        obj_id = page_or_ele._obj_id
    else:
        is_page = True
        page = page_or_ele
        end_time = perf_counter() + 5
        while perf_counter() < end_time:
            obj_id = page_or_ele._root_id
            if obj_id is not None:
                break
            sleep(.01)
        else:
            raise RuntimeError('js运行环境出错。')

    if page.states.has_alert:
        raise AlertExistsError

    try:
        if Path(script).exists():
            with open(script, 'r', encoding='utf-8') as f:
                script = f.read()
    except OSError:
        pass

    end_time = perf_counter() + timeout
    try:
        if as_expr:
            res = page.run_cdp('Runtime.evaluate', expression=script, returnByValue=False,
                               awaitPromise=True, userGesture=True, _timeout=timeout, _ignore=AlertExistsError)

        else:
            args = args or ()
            if not is_js_func(script):
                script = f'function(){{{script}}}'
            res = page.run_cdp('Runtime.callFunctionOn', functionDeclaration=script, objectId=obj_id,
                               arguments=[convert_argument(arg) for arg in args], returnByValue=False,
                               awaitPromise=True, userGesture=True, _timeout=timeout, _ignore=AlertExistsError)
    except TimeoutError:
        raise TimeoutError(f'执行js超时（等待{timeout}秒）。')
    except ContextLostError:
        raise ContextLostError('页面已被刷新，请尝试等待页面加载完成再执行操作。') if is_page else ElementLostError(
            '原来获取到的元素对象已不在页面内。')

    if not res:  # _timeout=0或js激活alert时
        return None

    exceptionDetails = res.get('exceptionDetails')
    if exceptionDetails:
        raise JavaScriptError(f'\njavascript运行错误：\n{script}\n错误信息: \n{exceptionDetails}')

    try:
        return parse_js_result(page, page_or_ele, res.get('result'), end_time)
    except Exception:
        from DrissionPage import __version__
        raise RuntimeError(f'\njs结果解析错误\n版本：{__version__}\n内容：{res}\njs：{script}\n'
                           f'出现这个错误可能意味着程序有bug，请把错误信息和重现方法告知作者，谢谢。\n'
                           f'报告网站：https://gitee.com/g1879/DrissionPage/issues')


def parse_js_result(page, ele, result, end_time):
    """解析js返回的结果"""
    if 'unserializableValue' in result:
        return result['unserializableValue']

    the_type = result['type']
    if the_type == 'object':
        sub_type = result.get('subtype', None)
        if sub_type == 'null':
            return None

        elif sub_type == 'node':
            class_name = result['className']
            if class_name == 'ShadowRoot':
                return ShadowRoot(ele, obj_id=result['objectId'])
            elif class_name == 'HTMLDocument':
                return result
            else:
                r = make_chromium_eles(page, _ids=result['objectId'])
                if r is False:
                    raise ElementLostError
                return r

        elif sub_type == 'array':
            r = page.run_cdp('Runtime.getProperties', objectId=result['objectId'], ownProperties=True)['result']
            return [parse_js_result(page, ele, result=i['value'], end_time=end_time) for i in r if i['name'].isdigit()]

        elif 'objectId' in result:
            timeout = end_time - perf_counter()
            if timeout < 0:
                return
            js = 'function(){return JSON.stringify(this);}'
            r = page.run_cdp('Runtime.callFunctionOn', functionDeclaration=js, objectId=result['objectId'],
                             returnByValue=False, awaitPromise=True, userGesture=True, _ignore=AlertExistsError,
                             _timeout=timeout)
            return loads(parse_js_result(page, ele, r['result'], end_time))

        else:
            return result.get('value', result)

    elif the_type == 'undefined':
        return None

    else:
        return result['value']


def convert_argument(arg):
    """把参数转换成js能够接收的形式"""
    if isinstance(arg, ChromiumElement):
        return {'objectId': arg._obj_id}

    elif isinstance(arg, (int, float, str, bool, dict)):
        return {'value': arg}

    from math import inf
    if arg == inf:
        return {'unserializableValue': 'Infinity'}
    elif arg == -inf:
        return {'unserializableValue': '-Infinity'}

    raise TypeError(f'不支持参数{arg}的类型：{type(arg)}')


class Pseudo(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    @property
    def before(self):
        """返回当前元素的::before伪元素内容"""
        return self._ele.style('content', 'before')

    @property
    def after(self):
        """返回当前元素的::after伪元素内容"""
        return self._ele.style('content', 'after')


def _check_ele(ele, loc_data):
    """检查元素是否符合loc_data指定的要求
    :param ele: 元素对象
    :param loc_data: 格式： {'and': bool, 'args': ['属性名称', '匹配方式', '属性值', 是否否定]}
    :return: bool
    """
    attrs = ele.attrs
    if loc_data['and']:
        ok = True
        for i in loc_data['args']:
            name, symbol, value, deny = i
            if name == 'tag()':
                arg = ele.tag
                symbol = '='
            elif name == 'text()':
                arg = ele.raw_text
            elif name is None:
                arg = None
            else:
                arg = attrs.get(name, '')

            if ((symbol == '=' and ((deny and arg == value) or (not deny and arg != value)))
                    or (symbol == ':' and ((deny and value in arg) or (not deny and value not in arg)))
                    or (symbol == '^' and ((deny and arg.startswith(value))
                                           or (not deny and not arg.startswith(value))))
                    or (symbol == '$' and ((deny and arg.endswith(value)) or (not deny and not arg.endswith(value))))
                    or (arg is None and attrs)):
                ok = False
                break

    else:
        ok = False
        for i in loc_data['args']:
            name, value, symbol, deny = i
            if name == 'tag()':
                arg = ele.tag
                symbol = '='
            elif name == 'text()':
                arg = ele.text
            elif name is None:
                arg = None
            else:
                arg = attrs.get(name, '')

            if ((symbol == '=' and ((not deny and arg == value) or (deny and arg != value)))
                    or (symbol == ':' and ((not deny and value in arg) or (deny and value not in arg)))
                    or (symbol == '^' and ((not deny and arg.startswith(value))
                                           or (deny and not arg.startswith(value))))
                    or (symbol == '$' and ((not deny and arg.endswith(value)) or (deny and not arg.endswith(value))))
                    or (arg is None and not attrs)):
                ok = True
                break

    return ok
