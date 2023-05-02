# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from os import sep
from os.path import basename
from pathlib import Path
from time import perf_counter, sleep

from .base import DrissionElement, BaseElement
from .commons.constants import FRAME_ELEMENT, NoneElement, Settings
from .commons.keys import keys_to_typing, keyDescriptionForString, keyDefinitions
from .commons.locator import get_loc
from .commons.web import make_absolute_link, get_ele_txt, format_html, is_js_func, location_in_viewport, offset_scroll
from .errors import ContextLossError, ElementLossError, JavaScriptError, NoRectError, ElementNotFoundError, \
    CallMethodError, NoResourceError, CanNotClickError
from .session_element import make_session_ele


class ChromiumElement(DrissionElement):
    """控制浏览器元素的对象"""

    def __init__(self, page, node_id=None, obj_id=None, backend_id=None):
        """node_id、obj_id和backend_id必须至少传入一个
        :param page: 元素所在ChromePage页面对象
        :param node_id: cdp中的node id
        :param obj_id: js中的object id
        :param backend_id: backend id
        """
        super().__init__(page)
        self._select = None
        self._scroll = None
        self._locations = None
        self._set = None
        self._states = None
        self._pseudo = None
        self._click = None
        self._tag = None
        self._wait = None

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
            raise ElementLossError

        self._ids = ChromiumElementIds(self)
        doc = self.run_js('return this.ownerDocument;')
        self._doc_id = doc['objectId'] if doc else None

    def __repr__(self):
        attrs = self.attrs
        attrs = [f"{attr}='{attrs[attr]}'" for attr in attrs]
        return f'<ChromiumElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: ChromiumElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    @property
    def tag(self):
        """返回元素tag"""
        if self._tag is None:
            self._tag = self.page.run_cdp('DOM.describeNode',
                                          backendNodeId=self._backend_id)['node']['localName'].lower()
        return self._tag

    @property
    def html(self):
        """返回元素outerHTML文本"""
        return self.page.run_cdp('DOM.getOuterHTML', backendNodeId=self._backend_id)['outerHTML']

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        return self.run_js('return this.innerHTML;')

    @property
    def attrs(self):
        """返回元素所有attribute属性"""
        try:
            attrs = self.page.run_cdp('DOM.getAttributes', nodeId=self._node_id)['attributes']
            return {attrs[i]: attrs[i + 1] for i in range(0, len(attrs), 2)}
        except CallMethodError:  # 文档根元素不能调用此方法
            return {}

    @property
    def text(self):
        """返回元素内所有文本，文本已格式化"""
        return get_ele_txt(make_session_ele(self.html))

    @property
    def raw_text(self):
        """返回未格式化处理的元素内文本"""
        return self.prop('innerText')

    # -----------------d模式独有属性-------------------
    @property
    def ids(self):
        """返回获取内置id的对象"""
        return self._ids

    @property
    def size(self):
        """返回元素宽和高组成的元组"""
        model = self.page.run_cdp('DOM.getBoxModel', backendNodeId=self._backend_id)['model']
        return model['width'], model['height']

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
            self._states = ChromiumElementStates(self)
        return self._states

    @property
    def pseudo(self):
        """返回用于获取伪元素内容的对象"""
        if self._pseudo is None:
            self._pseudo = Pseudo(self)
        return self._pseudo

    @property
    def location(self):
        """返回元素左上角的绝对坐标"""
        return self.locations.location

    @property
    def locations(self):
        """返回用于获取元素位置的对象"""
        if self._locations is None:
            self._locations = Locations(self)
        return self._locations

    @property
    def shadow_root(self):
        """返回当前元素的shadow_root元素对象"""
        info = self.page.run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
        if not info.get('shadowRoots', None):
            return None

        return ChromiumShadowRoot(self, backend_id=info['shadowRoots'][0]['backendNodeId'])

    @property
    def sr(self):
        """返回当前元素的shadow_root元素对象"""
        return self.shadow_root

    @property
    def scroll(self):
        """用于滚动滚动条的对象"""
        if self._scroll is None:
            self._scroll = ChromiumElementScroll(self)
        return self._scroll

    @property
    def click(self):
        """返回用于点击的对象"""
        if self._click is None:
            self._click = Click(self)
        return self._click

    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = ChromiumElementWaiter(self.page, self)
        return self._wait

    @property
    def select(self):
        """返回专门处理下拉列表的Select类，非下拉列表元素返回False"""
        if self._select is None:
            if self.tag != 'select':
                self._select = False
            else:
                self._select = ChromiumSelect(self)

        return self._select

    def parent(self, level_or_loc=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :return: 上级元素对象
        """
        return super().parent(level_or_loc)

    def child(self, filter_loc='', index=1, timeout=0, ele_only=True):
        """返回当前元素的一个符合条件的直接子元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本
        """
        return super().child(index, filter_loc, timeout, ele_only=ele_only)

    def prev(self, filter_loc='', index=1, timeout=0, ele_only=True):
        """返回当前元素前面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本
        """
        return super().prev(index, filter_loc, timeout, ele_only=ele_only)

    def next(self, filter_loc='', index=1, timeout=0, ele_only=True):
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本
        """
        return super().next(index, filter_loc, timeout, ele_only=ele_only)

    def before(self, filter_loc='', index=1, timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的第一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        return super().before(index, filter_loc, timeout, ele_only=ele_only)

    def after(self, filter_loc='', index=1, timeout=None, ele_only=True):
        """返回文档中此当前元素后面符合条件的第一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        return super().after(index, filter_loc, timeout, ele_only=ele_only)

    def children(self, filter_loc='', timeout=0, ele_only=True):
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        return super().children(filter_loc, timeout, ele_only=ele_only)

    def prevs(self, filter_loc='', timeout=0, ele_only=True):
        """返回当前元素前面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return super().prevs(filter_loc, timeout, ele_only=ele_only)

    def nexts(self, filter_loc='', timeout=0, ele_only=True):
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return super().nexts(filter_loc, timeout, ele_only=ele_only)

    def befores(self, filter_loc='', timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        return super().befores(filter_loc, timeout, ele_only=ele_only)

    def afters(self, filter_loc='', timeout=None, ele_only=True):
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        return super().afters(filter_loc, timeout, ele_only=ele_only)

    def attr(self, attr):
        """返回一个attribute属性值
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        attrs = self.attrs
        if attr == 'href':  # 获取href属性时返回绝对url
            link = attrs.get('href', None)
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link
            else:
                return make_absolute_link(link, self.page)

        elif attr == 'src':
            return make_absolute_link(attrs.get('src', None), self.page)

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

    def remove_attr(self, attr):
        """删除元素一个attribute属性
        :param attr: 属性名
        :return: None
        """
        self.run_js(f'this.removeAttribute("{attr}");')

    def prop(self, prop):
        """获取一个property属性值
        :param prop: 属性名
        :return: 属性值文本
        """
        p = self.page.run_cdp('Runtime.getProperties', objectId=self._obj_id)['result']
        for i in p:
            if i['name'] == prop:
                if 'value' not in i or 'value' not in i['value']:
                    return None

                value = i['value']['value']
                return format_html(value) if isinstance(value, str) else value

    def run_js(self, script, *args, as_expr=False):
        """对本元素执行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: 运行的结果
        """
        return run_js(self, script, as_expr, self.page.timeouts.script, args)

    def run_async_js(self, script, *args, as_expr=False):
        """以异步方式对本元素执行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: None
        """
        from threading import Thread
        Thread(target=run_js, args=(self, script, as_expr, self.page.timeouts.script, args, True)).start()

    def ele(self, loc_or_str, timeout=None):
        """返回当前元素下级符合条件的第一个元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本
        """
        return self._ele(loc_or_str, timeout)

    def eles(self, loc_or_str, timeout=None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_str=None):
        """查找第一个符合条件的元素，以SessionElement形式返回
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        if self.tag in FRAME_ELEMENT:
            return make_session_ele(self.inner_html, loc_or_str)
        return make_session_ele(self, loc_or_str)

    def s_eles(self, loc_or_str=None):
        """查找所有符合条件的元素，以SessionElement列表形式返回
        :param loc_or_str: 定位符
        :return: SessionElement或属性、文本组成的列表
        """
        if self.tag in FRAME_ELEMENT:
            return make_session_ele(self.inner_html, loc_or_str, single=False)
        return make_session_ele(self, loc_or_str, single=False)

    def _find_elements(self, loc_or_str, timeout=None, single=True, relative=False, raise_err=None):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或文本、属性或其组成的列表
        """
        return find_in_chromium_ele(self, loc_or_str, single, timeout, relative=relative)

    def style(self, style, pseudo_ele=''):
        """返回元素样式属性值，可获取伪元素属性值
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"' if pseudo_ele.startswith(':') else f', "::{pseudo_ele}"'
        js = f'return window.getComputedStyle(this{pseudo_ele}).getPropertyValue("{style}");'
        return self.run_js(js)

    def get_src(self, timeout=None):
        """返回元素src资源，base64的会转为bytes返回，其它返回str
        :param timeout: 等待资源加载的超时时间
        :return: 资源内容
        """
        timeout = self.page.timeout if timeout is None else timeout
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" '
                  '&& this.naturalWidth > 0 && typeof this.naturalHeight != "undefined" '
                  '&& this.naturalHeight > 0')
            end_time = perf_counter() + timeout
            while not self.run_js(js) and perf_counter() < end_time:
                sleep(.1)

        result = None
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            src = self.prop('currentSrc')
            if not src:
                continue

            node = self.page.run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
            frame = node.get('frameId', None)
            frame = frame or self.page.tab_id

            try:
                result = self.page.run_cdp('Page.getResourceContent', frameId=frame, url=src)
                break
            except CallMethodError:
                sleep(.1)

        if not result:
            return None

        if result['base64Encoded']:
            from base64 import b64decode
            data = b64decode(result['content'])
        else:
            data = result['content']
        return data

    def save(self, path=None, rename=None, timeout=None):
        """保存图片或其它有src属性的元素的资源
        :param path: 文件保存路径，为None时保存到当前文件夹
        :param rename: 文件名称，为None时从资源url获取
        :param timeout: 等待资源加载的超时时间
        :return: None
        """
        data = self.get_src(timeout=timeout)
        if not data:
            raise NoResourceError

        path = path or '.'
        rename = rename or basename(self.prop('currentSrc'))
        write_type = 'wb' if isinstance(data, bytes) else 'w'

        Path(path).mkdir(parents=True, exist_ok=True)
        with open(f'{path}{sep}{rename}', write_type) as f:
            f.write(data)

    def get_screenshot(self, path=None, as_bytes=None, as_base64=None):
        """对当前元素截图，可保存到文件，或以字节方式返回
        :param path: 完整路径，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :return: 图片完整路径或字节文本
        """
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" '
                  '&& this.naturalWidth > 0 && typeof this.naturalHeight != "undefined" '
                  '&& this.naturalHeight > 0')
            end_time = perf_counter() + self.page.timeout
            while not self.run_js(js) and perf_counter() < end_time:
                sleep(.1)

        self.scroll.to_see(center=True)
        sleep(1)
        left, top = self.location
        width, height = self.size
        left_top = (left, top)
        right_bottom = (left + width, top + height)
        if not path:
            path = f'{self.tag}.jpg'
        return self.page._get_screenshot(path, as_bytes=as_bytes, as_base64=as_base64, full_page=False,
                                         left_top=left_top, right_bottom=right_bottom, ele=self)

    def input(self, vals, clear=True):
        """输入文本或组合键，也可用于输入文件路径到input元素（路径间用\n间隔）
        :param vals: 文本值或按键组合
        :param clear: 输入前是否清空文本框
        :return: None
        """
        if self.tag == 'input' and self.attr('type') == 'file':
            return self._set_file_input(vals)

        if clear and vals not in ('\n', '\ue007'):
            self.clear(by_js=False)
        else:
            self._input_focus()

        # ------------处理字符-------------
        if not isinstance(vals, (tuple, list)):
            vals = (str(vals),)
        modifier, vals = keys_to_typing(vals)

        if modifier != 0:  # 包含修饰符
            for key in vals:
                send_key(self, modifier, key)
            return

        if vals.endswith(('\n', '\ue007')):
            self.page.run_cdp('Input.insertText', text=vals[:-1])
            send_key(self, modifier, '\n')
        else:
            self.page.run_cdp('Input.insertText', text=vals)

    def clear(self, by_js=False):
        """清空元素文本
        :param by_js: 是否用js方式清空，为False则用全选+del模拟输入删除
        :return: None
        """
        if by_js:
            self.run_js("this.value='';")

        else:
            self._input_focus()
            self.input(('\ue009', 'a', '\ue017'), clear=False)

    def _input_focus(self):
        """输入前使元素获取焦点"""
        try:
            self.page.run_cdp('DOM.focus', backendNodeId=self._backend_id)
        except Exception:
            self.click(by_js=None)

    def focus(self):
        """使元素获取焦点"""
        try:
            self.page.run_cdp('DOM.focus', backendNodeId=self._backend_id)
        except Exception:
            self.run_js('this.focus();')

    def hover(self, offset_x=None, offset_y=None):
        """鼠标悬停，可接受偏移量，偏移量相对于元素左上角坐标。不传入x或y值时悬停在元素中点
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        self.page.scroll.to_see(self)
        x, y = offset_scroll(self, offset_x, offset_y)
        self.page.run_cdp('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y)

    def drag(self, offset_x=0, offset_y=0, duration=.5):
        """拖拽当前元素到相对位置
        :param offset_x: x变化值
        :param offset_y: y变化值
        :param duration: 拖动用时，传入0即瞬间到j达
        :return: None
        """
        curr_x, curr_y = self.locations.midpoint
        offset_x += curr_x
        offset_y += curr_y
        self.drag_to((offset_x, offset_y), duration)

    def drag_to(self, ele_or_loc, duration=.5):
        """拖拽当前元素，目标为另一个元素或坐标元组(x, y)
        :param ele_or_loc: 另一个元素或坐标元组，坐标为元素中点的坐标
        :param duration: 拖动用时，传入0即瞬间到j达
        :return: None
        """
        # x, y：目标点坐标
        if isinstance(ele_or_loc, ChromiumElement):
            target_x, target_y = ele_or_loc.locations.midpoint
        elif isinstance(ele_or_loc, (list, tuple)):
            target_x, target_y = ele_or_loc
        else:
            raise TypeError('需要ChromiumElement对象或坐标。')

        current_x, current_y = self.locations.midpoint
        width = target_x - current_x
        height = target_y - current_y

        duration = .02 if duration < .02 else duration
        num = int(duration * 50)

        # 将要经过的点存入列表
        points = [(int(current_x + i * (width / num)), int(current_y + i * (height / num))) for i in range(1, num)]
        points.append((target_x, target_y))

        from .action_chains import ActionChains
        actions = ActionChains(self.page)
        actions.hold(self)

        # 逐个访问要经过的点
        for x, y in points:
            t = perf_counter()
            actions.move(x - current_x, y - current_y)
            current_x, current_y = x, y
            ss = .02 - perf_counter() + t
            if ss > 0:
                sleep(ss)
        actions.release()

    def _get_obj_id(self, node_id=None, backend_id=None):
        """根据传入node id或backend id获取js中的object id
        :param node_id: cdp中的node id
        :param backend_id: backend id
        :return: js中的object id
        """
        if node_id:
            return self.page.run_cdp('DOM.resolveNode', nodeId=node_id)['object']['objectId']
        else:
            return self.page.run_cdp('DOM.resolveNode', backendNodeId=backend_id)['object']['objectId']

    def _get_node_id(self, obj_id=None, backend_id=None):
        """根据传入object id或backend id获取cdp中的node id
        :param obj_id: js中的object id
        :param backend_id: backend id
        :return: cdp中的node id
        """
        if obj_id:
            return self.page.run_cdp('DOM.requestNode', objectId=obj_id)['nodeId']
        else:
            return self.page.run_cdp('DOM.describeNode', backendNodeId=backend_id)['node']['nodeId']

    def _get_backend_id(self, node_id):
        """根据传入node id获取backend id
        :param node_id:
        :return: backend id
        """
        return self.page.run_cdp('DOM.describeNode', nodeId=node_id)['node']['backendNodeId']

    def _get_ele_path(self, mode):
        """返获取绝对的css路径或xpath路径"""
        if mode == 'xpath':
            txt1 = 'var tag = el.nodeName.toLowerCase();'
            txt3 = ''' && sib.nodeName.toLowerCase()==tag'''
            txt4 = '''
            if(nth>1){path = '/' + tag + '[' + nth + ']' + path;}
                    else{path = '/' + tag + path;}'''
            txt5 = '''return path;'''

        elif mode == 'css':
            txt1 = ''
            txt3 = ''
            txt4 = '''path = '>' + ":nth-child(" + nth + ")" + path;'''
            txt5 = '''return path.substr(1);'''

        else:
            raise ValueError(f"mode参数只能是'xpath'或'css'，现在是：'{mode}'。")

        js = '''function(){
        function e(el) {
            if (!(el instanceof Element)) return;
            var path = '';
            while (el.nodeType === Node.ELEMENT_NODE) {
                ''' + txt1 + '''
                    var sib = el, nth = 0;
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
        return f':root{t}' if mode == 'css' else t

    def _set_file_input(self, files):
        """对上传控件写入路径
        :param files: 文件路径列表或字符串，字符串时多个文件用回车分隔
        :return: None
        """
        if isinstance(files, str):
            files = files.split('\n')
        files = [str(Path(i).absolute()) for i in files]
        self.page.run_cdp('DOM.setFileInputFiles', files=files, backendNodeId=self._backend_id)


class ChromiumShadowRoot(BaseElement):
    """ChromiumShadowRoot是用于处理ShadowRoot的类，使用方法和ChromiumElement基本一致"""

    def __init__(self, parent_ele, obj_id=None, backend_id=None):
        """
        :param parent_ele: shadow root 所在父元素
        :param obj_id: js中的object id
        :param backend_id: cdp中的backend id
        """
        super().__init__(parent_ele.page)
        self.parent_ele = parent_ele
        if backend_id:
            self._backend_id = backend_id
            self._obj_id = self._get_obj_id(backend_id)
            self._node_id = self._get_node_id(self._obj_id)
        elif obj_id:
            self._obj_id = obj_id
            self._node_id = self._get_node_id(obj_id)
            self._backend_id = self._get_backend_id(self._node_id)
        self._ids = Ids(self)
        self._states = None

    def __repr__(self):
        return f'<ChromiumShadowRoot in {self.parent_ele}>'

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: DriverElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

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
    def ids(self):
        """返回获取内置id的对象"""
        return self._ids

    @property
    def states(self):
        """返回用于获取元素状态的对象"""
        if self._states is None:
            self._states = ShadowRootStates(self)
        return self._states

    def run_js(self, script, *args, as_expr=False):
        """运行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: 运行的结果
        """
        return run_js(self, script, as_expr, self.page.timeouts.script, args)

    def run_async_js(self, script, *args, as_expr=False):
        """以异步方式执行js代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: None
        """
        from threading import Thread
        Thread(target=run_js, args=(self, script, as_expr, self.page.timeouts.script, args)).start()

    def parent(self, level_or_loc=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :return: ChromiumElement对象
        """
        if isinstance(level_or_loc, int):
            loc = f'xpath:./ancestor-or-self::*[{level_or_loc}]'

        elif isinstance(level_or_loc, (tuple, str)):
            loc = get_loc(level_or_loc, True)

            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')

            loc = f'xpath:./ancestor-or-self::{loc[1].lstrip(". / ")}'

        else:
            raise TypeError('level_or_loc参数只能是tuple、int或str。')

        return self.parent_ele._ele(loc, timeout=0, relative=True, raise_err=False)

    def child(self, filter_loc='', index=1):
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :return: 直接子元素或节点文本组成的列表
        """
        nodes = self.children(filter_loc=filter_loc)
        if not nodes:
            if Settings.raise_ele_not_found:
                raise ElementNotFoundError
            else:
                return NoneElement()

        try:
            return nodes[index - 1]
        except IndexError:
            if Settings.raise_ele_not_found:
                raise ElementNotFoundError
            else:
                return NoneElement()

    def next(self, filter_loc='', index=1):
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param filter_loc: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :return: ChromiumElement对象
        """
        nodes = self.nexts(filter_loc=filter_loc)
        if nodes:
            return nodes[index - 1]
        if Settings.raise_ele_not_found:
            raise ElementNotFoundError
        else:
            return NoneElement()

    def before(self, filter_loc='', index=1):
        """返回文档中当前元素前面符合条件的第一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :return: 本元素前面的某个元素或节点
        """
        nodes = self.befores(filter_loc=filter_loc)
        if nodes:
            return nodes[index - 1]
        if Settings.raise_ele_not_found:
            raise ElementNotFoundError
        else:
            return NoneElement()

    def after(self, filter_loc='', index=1):
        """返回文档中此当前元素后面符合条件的第一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :return: 本元素后面的某个元素或节点
        """
        nodes = self.afters(filter_loc=filter_loc)
        if nodes:
            return nodes[index - 1]
        if Settings.raise_ele_not_found:
            raise ElementNotFoundError
        else:
            return NoneElement()

    def children(self, filter_loc=''):
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :return: 直接子元素或节点文本组成的列表
        """
        if not filter_loc:
            loc = '*'
        else:
            loc = get_loc(filter_loc, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        return self._ele(loc, single=False, relative=True)

    def nexts(self, filter_loc=''):
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选的查询语法
        :return: ChromiumElement对象组成的列表
        """
        loc = get_loc(filter_loc, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./{loc}'
        return self.parent_ele._ele(xpath, single=False, relative=True)

    def befores(self, filter_loc=''):
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :return: 本元素前面的元素或节点组成的列表
        """
        loc = get_loc(filter_loc, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./preceding::{loc}'
        return self.parent_ele._ele(xpath, single=False, relative=True)

    def afters(self, filter_loc=''):
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param filter_loc: 用于筛选的查询语法
        :return: 本元素后面的元素或节点组成的列表
        """
        eles1 = self.nexts(filter_loc)
        loc = get_loc(filter_loc, True)[1].lstrip('./')
        xpath = f'xpath:./following::{loc}'
        return eles1 + self.parent_ele._ele(xpath, single=False, relative=True)

    def ele(self, loc_or_str, timeout=None):
        """返回当前元素下级符合条件的第一个元素
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象
        """
        return self._ele(loc_or_str, timeout)

    def eles(self, loc_or_str, timeout=None):
        """返回当前元素下级所有符合条件的子元素
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_str=None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_str)

    def s_eles(self, loc_or_str):
        """查找所有符合条件的元素以SessionElement列表形式返回，处理复杂页面时效率很高
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象
        """
        return make_session_ele(self, loc_or_str, single=False)

    def _find_elements(self, loc_or_str, timeout=None, single=True, relative=False, raise_err=None):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或其组成的列表
        """
        loc = get_loc(loc_or_str)
        if loc[0] == 'css selector' and str(loc[1]).startswith(':root'):
            loc = loc[0], loc[1][5:]

        timeout = timeout if timeout is not None else self.page.timeout
        t1 = perf_counter()
        eles = make_session_ele(self.html).eles(loc)
        while not eles and perf_counter() - t1 <= timeout:
            eles = make_session_ele(self.html).eles(loc)

        if not eles:
            return NoneElement() if single else eles

        css_paths = [i.css_path[47:] for i in eles]
        if single:
            node_id = self.page.run_cdp('DOM.querySelector', nodeId=self._node_id, selector=css_paths[0])['nodeId']
            return make_chromium_ele(self.page, node_id=node_id) if node_id else NoneElement()

        else:
            results = []
            for i in css_paths:
                node_id = self.page.run_cdp('DOM.querySelector', nodeId=self._node_id, selector=i)['nodeId']
                if node_id:
                    results.append(make_chromium_ele(self.page, node_id=node_id))
            return results

    def _get_node_id(self, obj_id):
        """返回元素node id"""
        return self.page.run_cdp('DOM.requestNode', objectId=obj_id)['nodeId']

    def _get_obj_id(self, back_id):
        """返回元素object id"""
        return self.page.run_cdp('DOM.resolveNode', backendNodeId=back_id)['object']['objectId']

    def _get_backend_id(self, node_id):
        """返回元素object id"""
        r = self.page.run_cdp('DOM.describeNode', nodeId=node_id)['node']
        self._tag = r['localName'].lower()
        return r['backendNodeId']


class Ids(object):
    def __init__(self, ele):
        self._ele = ele

    @property
    def node_id(self):
        """返回元素cdp中的node id"""
        return self._ele._node_id

    @property
    def obj_id(self):
        """返回元素js中的object id"""
        return self._ele._obj_id

    @property
    def backend_id(self):
        """返回backend id"""
        return self._ele._backend_id


class ChromiumElementIds(Ids):
    @property
    def doc_id(self):
        """返回所在document的object id"""
        return self._ele._doc_id


def find_in_chromium_ele(ele, loc, single=True, timeout=None, relative=True):
    """在chromium元素中查找
    :param ele: ChromiumElement对象
    :param loc: 元素定位元组
    :param single: True则返回第一个，False则返回全部
    :param timeout: 查找元素超时时间
    :param relative: WebPage用于标记是否相对定位使用
    :return: 返回ChromiumElement元素或它们组成的列表
    """
    # ---------------处理定位符---------------
    if isinstance(loc, (str, tuple)):
        loc = get_loc(loc)
    else:
        raise ValueError(f"定位符必须为str或长度为2的tuple对象。现在是：{loc}")

    loc_str = loc[1]
    if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
        loc_str = f'.{loc_str}'
    elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>'):
        loc_str = f'{ele.css_path}{loc[1]}'
    loc = loc[0], loc_str

    timeout = timeout if timeout is not None else ele.page.timeout

    # ---------------执行查找-----------------
    if loc[0] == 'xpath':
        return find_by_xpath(ele, loc[1], single, timeout, relative=relative)

    else:
        return find_by_css(ele, loc[1], single, timeout)


def find_by_xpath(ele, xpath, single, timeout, relative=True):
    """执行用xpath在元素中查找元素
    :param ele: 在此元素中查找
    :param xpath: 查找语句
    :param single: 是否只返回第一个结果
    :param timeout: 超时时间
    :param relative: 是否相对定位
    :return: ChromiumElement或其组成的列表
    """
    type_txt = '9' if single else '7'
    node_txt = 'this.contentDocument' if ele.tag in FRAME_ELEMENT and not relative else 'this'
    js = make_js_for_find_ele_by_xpath(xpath, type_txt, node_txt)
    r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele.ids.obj_id,
                                returnByValue=False, awaitPromise=True, userGesture=True)
    if r['result']['type'] == 'string':
        return r['result']['value']

    if 'exceptionDetails' in r:
        if 'The result is not a node set' in r['result']['description']:
            js = make_js_for_find_ele_by_xpath(xpath, '1', node_txt)
            r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele.ids.obj_id,
                                        returnByValue=False, awaitPromise=True, userGesture=True)
            return r['result']['value']
        else:
            raise SyntaxError(f'查询语句错误：\n{r}')

    end_time = perf_counter() + timeout
    while (r['result']['subtype'] == 'null'
           or r['result']['description'] == 'NodeList(0)') and perf_counter() < end_time:
        r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele.ids.obj_id,
                                    returnByValue=False, awaitPromise=True, userGesture=True)

    if single:
        return NoneElement() if r['result']['subtype'] == 'null' \
            else make_chromium_ele(ele.page, obj_id=r['result']['objectId'])

    if r['result']['description'] == 'NodeList(0)':
        return []
    else:
        r = ele.page.run_cdp_loaded('Runtime.getProperties', objectId=r['result']['objectId'],
                                    ownProperties=True)['result']
        return [make_chromium_ele(ele.page, obj_id=i['value']['objectId'])
                if i['value']['type'] == 'object' else i['value']['value']
                for i in r[:-1]]


def find_by_css(ele, selector, single, timeout):
    """执行用css selector在元素中查找元素
    :param ele: 在此元素中查找
    :param selector: 查找语句
    :param single: 是否只返回第一个结果
    :param timeout: 超时时间
    :return: ChromiumElement或其组成的列表
    """
    selector = selector.replace('"', r'\"')
    find_all = '' if single else 'All'
    node_txt = 'this.contentDocument' if ele.tag in ('iframe', 'frame', 'shadow-root') else 'this'
    js = f'function(){{return {node_txt}.querySelector{find_all}("{selector}");}}'
    r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele.ids.obj_id,
                                returnByValue=False, awaitPromise=True, userGesture=True)

    end_time = perf_counter() + timeout
    while ('exceptionDetails' in r or r['result']['subtype'] == 'null' or
           r['result']['description'] == 'NodeList(0)') and perf_counter() < end_time:
        r = ele.page.run_cdp_loaded('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele.ids.obj_id,
                                    returnByValue=False, awaitPromise=True, userGesture=True)

    if 'exceptionDetails' in r:
        raise SyntaxError(f'查询语句错误：\n{r}')

    if single:
        return NoneElement() if r['result']['subtype'] == 'null' \
            else make_chromium_ele(ele.page, obj_id=r['result']['objectId'])

    if r['result']['description'] == 'NodeList(0)':
        return []
    else:
        r = ele.page.run_cdp_loaded('Runtime.getProperties', objectId=r['result']['objectId'],
                                    ownProperties=True)['result']
        return [make_chromium_ele(ele.page, obj_id=i['value']['objectId']) for i in r]


def make_chromium_ele(page, node_id=None, obj_id=None):
    """根据node id或object id生成相应元素对象
    :param page: ChromiumPage对象
    :param node_id: 元素的node id
    :param obj_id: 元素的object id
    :return: ChromiumElement对象或ChromiumFrame对象
    """
    if node_id:
        node = page.run_cdp('DOM.describeNode', nodeId=node_id)
        if node['node']['nodeName'] in ('#text', '#comment'):
            return node['node']['nodeValue']
        backend_id = node['node']['backendNodeId']
        obj_id = page.run_cdp('DOM.resolveNode', nodeId=node_id)['object']['objectId']

    elif obj_id:
        node = page.run_cdp('DOM.describeNode', objectId=obj_id)
        if node['node']['nodeName'] in ('#text', '#comment'):
            return node['node']['nodeValue']
        backend_id = node['node']['backendNodeId']
        node_id = node['node']['nodeId']

    else:
        raise ElementLossError

    ele = ChromiumElement(page, obj_id=obj_id, node_id=node_id, backend_id=backend_id)
    if ele.tag in FRAME_ELEMENT:
        from .chromium_frame import ChromiumFrame
        ele = ChromiumFrame(page, ele)

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
var a=new Array();
for(var i = 0; i <e.snapshotLength ; i++){
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
    js = f'function(){{var e=document.evaluate(\'{xpath}\',{node_txt},null,{type_txt},null);\n{for_txt}\n{return_txt}}}'

    return js


def run_js(page_or_ele, script, as_expr=False, timeout=None, args=None):
    """运行javascript代码
    :param page_or_ele: 页面对象或元素对象
    :param script: js文本
    :param as_expr: 是否作为表达式运行，为True时args无效
    :param timeout: 超时时间
    :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
    :return: js执行结果
    """
    if isinstance(page_or_ele, (ChromiumElement, ChromiumShadowRoot)):
        page = page_or_ele.page
        obj_id = page_or_ele.ids.obj_id
        is_page = False
    else:
        page = page_or_ele
        obj_id = page_or_ele._root_id
        is_page = True

    try:
        if as_expr:
            res = page.run_cdp('Runtime.evaluate', expression=script, returnByValue=False,
                               awaitPromise=True, userGesture=True, timeout=timeout * 1000)

        else:
            args = args or ()
            if not is_js_func(script):
                script = f'function(){{{script}}}'
            res = page.run_cdp('Runtime.callFunctionOn', functionDeclaration=script, objectId=obj_id,
                               arguments=[convert_argument(arg) for arg in args], returnByValue=False,
                               awaitPromise=True, userGesture=True)

    except ContextLossError:
        if is_page:
            raise ContextLossError('页面已被刷新，请尝试等待页面加载完成再执行操作。')
        else:
            raise ElementLossError('原来获取到的元素对象已不在页面内。')

    if res is None and page.driver.has_alert:  # 存在alert的情况
        return None

    exceptionDetails = res.get('exceptionDetails')
    if exceptionDetails:
        raise JavaScriptError(f'\njavascript运行错误：\n{script}\n错误信息: \n{exceptionDetails}')

    try:
        return parse_js_result(page, page_or_ele, res.get('result'))
    except Exception:
        return res


def parse_js_result(page, ele, result):
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
                return ChromiumShadowRoot(ele, obj_id=result['objectId'])
            elif class_name == 'HTMLDocument':
                return result
            else:
                return make_chromium_ele(page, obj_id=result['objectId'])

        elif sub_type == 'array':
            r = page.run_cdp('Runtime.getProperties', objectId=result['objectId'],
                             ownProperties=True)['result']
            return [parse_js_result(page, ele, result=i['value']) for i in r[:-1]]

        elif 'objectId' in result and result['className'].lower() == 'object':  # dict
            r = page.run_cdp('Runtime.getProperties', objectId=result['objectId'],
                             ownProperties=True)['result']
            return {i['name']: parse_js_result(page, ele, result=i['value']) for i in r}

        else:
            return result['value']

    elif the_type == 'undefined':
        return None

    else:
        return result['value']


def convert_argument(arg):
    """把参数转换成js能够接收的形式"""
    if isinstance(arg, ChromiumElement):
        return {'objectId': arg.ids.obj_id}

    elif isinstance(arg, (int, float, str, bool)):
        return {'value': arg}

    from math import inf
    if arg == inf:
        return {'unserializableValue': 'Infinity'}
    if arg == -inf:
        return {'unserializableValue': '-Infinity'}


def send_enter(ele):
    """发送回车"""
    data = {'type': 'keyDown', 'modifiers': 0, 'windowsVirtualKeyCode': 13, 'code': 'Enter', 'key': 'Enter',
            'text': '\r', 'autoRepeat': False, 'unmodifiedText': '\r', 'location': 0, 'isKeypad': False}

    ele.page.run_cdp('Input.dispatchKeyEvent', **data)
    data['type'] = 'keyUp'
    ele.page.run_cdp('Input.dispatchKeyEvent', **data)


def send_key(ele, modifier, key):
    """发送一个字，在键盘中的字符触发按键，其它直接发送文本"""
    if key not in keyDefinitions:
        ele.page.run_cdp('Input.insertText', text=key)

    else:
        description = keyDescriptionForString(modifier, key)
        text = description['text']
        data = {'type': 'keyDown' if text else 'rawKeyDown',
                'modifiers': modifier,
                'windowsVirtualKeyCode': description['keyCode'],
                'code': description['code'],
                'key': description['key'],
                'text': text,
                'autoRepeat': False,
                'unmodifiedText': text,
                'location': description['location'],
                'isKeypad': description['location'] == 3}

        ele.page.run_cdp('Input.dispatchKeyEvent', **data)
        data['type'] = 'keyUp'
        ele.page.run_cdp('Input.dispatchKeyEvent', **data)


class ChromiumElementStates(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    @property
    def is_selected(self):
        """返回元素是否被选择"""
        return self._ele.run_js('return this.selected;')

    @property
    def is_checked(self):
        """返回元素是否被选择"""
        return self._ele.run_js('return this.checked;')

    @property
    def is_displayed(self):
        """返回元素是否显示"""
        return not (self._ele.style('visibility') == 'hidden'
                    or self._ele.run_js('return this.offsetParent === null;')
                    or self._ele.style('display') == 'none')

    @property
    def is_enabled(self):
        """返回元素是否可用"""
        return not self._ele.run_js('return this.disabled;')

    @property
    def is_alive(self):
        """返回元素是否仍在DOM中"""
        try:
            d = self._ele.attrs
            return True
        except Exception:
            return False

    @property
    def is_in_viewport(self):
        """返回元素是否出现在视口中，以元素可以接受点击的点为判断"""
        x, y = self._ele.locations.click_point
        return location_in_viewport(self._ele.page, x, y) if x else False

    @property
    def is_covered(self):
        """返回元素是否被覆盖，与是否在视口中无关"""
        lx, ly = self._ele.locations.click_point
        try:
            r = self._ele.page.run_cdp('DOM.getNodeForLocation', x=lx, y=ly)
        except CallMethodError:
            return False

        if r.get('backendNodeId') != self._ele.ids.backend_id:
            return True

        return False


class ShadowRootStates(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    @property
    def is_enabled(self):
        """返回元素是否可用"""
        return not self._ele.run_js('return this.disabled;')

    @property
    def is_alive(self):
        """返回元素是否仍在DOM中"""
        try:
            self._ele.page.run_cdp('DOM.describeNode', backendNodeId=self._ele.ids.backend_id)
            return True
        except Exception:
            return False


class ChromiumElementSetter(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    def attr(self, attr, value):
        """设置元素attribute属性
        :param attr: 属性名
        :param value: 属性值
        :return: None
        """
        self._ele.page.run_cdp('DOM.setAttributeValue', nodeId=self._ele.ids.node_id, name=attr, value=str(value))

    def prop(self, prop, value):
        """设置元素property属性
        :param prop: 属性名
        :param value: 属性值
        :return: None
        """
        value = value.replace('"', r'\"')
        self._ele.run_js(f'this.{prop}="{value}";')

    def innerHTML(self, html):
        """设置元素innerHTML
        :param html: html文本
        :return: None
        """
        self.prop('innerHTML', html)


class Locations(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    @property
    def location(self):
        """返回元素左上角的绝对坐标"""
        cl = self.viewport_location
        return self._get_page_coord(cl[0], cl[1])

    @property
    def midpoint(self):
        """返回元素中间点的绝对坐标"""
        cl = self.viewport_midpoint
        return self._get_page_coord(cl[0], cl[1])

    @property
    def click_point(self):
        """返回元素接受点击的点的绝对坐标"""
        cl = self.viewport_click_point
        return self._get_page_coord(cl[0], cl[1])

    @property
    def viewport_location(self):
        """返回元素左上角在视口中的坐标"""
        m = self._get_viewport_rect('border')
        return int(m[0]), int(m[1])

    @property
    def viewport_midpoint(self):
        """返回元素中间点在视口中的坐标"""
        m = self._get_viewport_rect('border')
        return int(m[0] + (m[2] - m[0]) // 2), int(m[3] + (m[5] - m[3]) // 2)

    @property
    def viewport_click_point(self):
        """返回元素接受点击的点视口坐标"""
        m = self._get_viewport_rect('padding')
        return int(self.viewport_midpoint[0]), int(m[1]) + 1

    @property
    def screen_location(self):
        """返回元素左上角在屏幕上坐标，左上角为(0, 0)"""
        vx, vy = self._ele.page.rect.viewport_location
        ex, ey = self.viewport_location
        return vx + ex, ey + vy

    @property
    def screen_midpoint(self):
        """返回元素中点在屏幕上坐标，左上角为(0, 0)"""
        vx, vy = self._ele.page.rect.viewport_location
        ex, ey = self.viewport_midpoint
        return vx + ex, ey + vy

    @property
    def screen_click_point(self):
        """返回元素中点在屏幕上坐标，左上角为(0, 0)"""
        vx, vy = self._ele.page.rect.viewport_location
        ex, ey = self.viewport_click_point
        return vx + ex, ey + vy

    def _get_viewport_rect(self, quad):
        """按照类型返回在可视窗口中的范围
        :param quad: 方框类型，margin border padding
        :return: 四个角坐标，大小为0时返回None
        """
        return self._ele.page.run_cdp('DOM.getBoxModel', backendNodeId=self._ele.ids.backend_id)['model'][quad]

    def _get_page_coord(self, x, y):
        """根据视口坐标获取绝对坐标"""
        # js = 'return document.documentElement.scrollLeft+" "+document.documentElement.scrollTop;'
        # xy = self._ele.run_js(js)
        # sx, sy = xy.split(' ')
        r = self._ele.page.run_cdp_loaded('Page.getLayoutMetrics')['visualViewport']
        sx = r['pageX']
        sy = r['pageY']
        return x + sx, y + sy


class Click(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    def __call__(self, by_js=False, timeout=1):
        """点击元素
        如果遇到遮挡，可选择是否用js点击
        :param by_js: 是否用js点击，为None时先用模拟点击，遇到遮挡改用js，为True时直接用js点击，为False时只用模拟点击
        :param timeout: 模拟点击的超时时间，等待元素可见、不被遮挡、进入视口
        :return: 是否点击成功
        """
        return self.left(by_js, timeout)

    def left(self, by_js=False, timeout=1):
        """点击元素，可选择是否用js点击
        :param by_js: 是否用js点击，为None时先用模拟点击，遇到遮挡改用js，为True时直接用js点击，为False时只用模拟点击
        :param timeout: 模拟点击的超时时间，等待元素可见、不被遮挡、进入视口
        :return: 是否点击成功
        """
        if not by_js:
            try:
                self._ele.scroll.to_see()
                can_click = False

                timeout = self._ele.page.timeout if timeout is None else timeout
                if timeout == 0:
                    if self._ele.states.is_in_viewport and self._ele.states.is_enabled and self._ele.states.is_displayed:
                        can_click = True
                else:
                    end_time = perf_counter() + timeout
                    while perf_counter() < end_time:
                        if self._ele.states.is_in_viewport and self._ele.states.is_enabled and self._ele.states.is_displayed:
                            can_click = True
                            break

                if not self._ele.states.is_in_viewport:
                    by_js = True

                elif can_click and (by_js is False or not self._ele.states.is_covered):
                    client_x, client_y = self._ele.locations.viewport_midpoint if self._ele.tag == 'input' \
                        else self._ele.locations.viewport_click_point
                    self._click(client_x, client_y)
                    return True

            except NoRectError:
                by_js = True

        if by_js is not False:
            self._ele.run_js('this.click();')
            return True

        if Settings.raise_click_failed:
            raise CanNotClickError
        return False

    def right(self):
        """右键单击"""
        self._ele.page.scroll.to_see(self._ele)
        x, y = self._ele.locations.viewport_click_point
        self._click(x, y, 'right')

    def middle(self):
        """中键单击"""
        self._ele.page.scroll.to_see(self._ele)
        x, y = self._ele.locations.viewport_click_point
        self._click(x, y, 'middle')

    def at(self, offset_x=None, offset_y=None, button='left', count=1):
        """带偏移量点击本元素，相对于左上角坐标。不传入x或y值时点击元素中间点
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :param button: 点击哪个键，可选 left, middle, right, back, forward
        :param count: 点击次数
        :return: None
        """
        self._ele.page.scroll.to_see(self._ele)
        if offset_x is None and offset_y is None:
            w, h = self._ele.size
            offset_x = w // 2
            offset_y = h // 2
        x, y = offset_scroll(self._ele, offset_x, offset_y)
        self._click(x, y, button, count)

    def twice(self):
        """双击元素"""
        self.at(count=2)

    def _click(self, client_x, client_y, button='left', count=1):
        """实施点击
        :param client_x: 视口中的x坐标
        :param client_y: 视口中的y坐标
        :param button: 'left' 'right' 'middle'  'back' 'forward'
        :param count: 点击次数
        :return: None
        """
        self._ele.page.run_cdp('Input.dispatchMouseEvent', type='mousePressed',
                               x=client_x, y=client_y, button=button, clickCount=count)
        # sleep(.05)
        self._ele.page.run_cdp('Input.dispatchMouseEvent', type='mouseReleased',
                               x=client_x, y=client_y, button=button)


class ChromiumScroll(object):
    """用于滚动的对象"""

    def __init__(self, ele):
        """
        :param ele: 元素对象
        """
        self._driver = ele
        self.t1 = self.t2 = 'this'
        self._wait_complete = False

    def _run_js(self, js):
        js = js.format(self.t1, self.t2, self.t2)
        self._driver.run_js(js)
        self._wait_scrolled()

    def to_top(self):
        """滚动到顶端，水平位置不变"""
        self._run_js('{}.scrollTo({}.scrollLeft, 0);')

    def to_bottom(self):
        """滚动到底端，水平位置不变"""
        self._run_js('{}.scrollTo({}.scrollLeft, {}.scrollHeight);')

    def to_half(self):
        """滚动到垂直中间位置，水平位置不变"""
        self._run_js('{}.scrollTo({}.scrollLeft, {}.scrollHeight/2);')

    def to_rightmost(self):
        """滚动到最右边，垂直位置不变"""
        self._run_js('{}.scrollTo({}.scrollWidth, {}.scrollTop);')

    def to_leftmost(self):
        """滚动到最左边，垂直位置不变"""
        self._run_js('{}.scrollTo(0, {}.scrollTop);')

    def to_location(self, x, y):
        """滚动到指定位置
        :param x: 水平距离
        :param y: 垂直距离
        :return: None
        """
        self._run_js(f'{{}}.scrollTo({x}, {y});')

    def up(self, pixel=300):
        """向上滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        pixel = -pixel
        self._run_js(f'{{}}.scrollBy(0, {pixel});')

    def down(self, pixel=300):
        """向下滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        self._run_js(f'{{}}.scrollBy(0, {pixel});')

    def left(self, pixel=300):
        """向左滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        pixel = -pixel
        self._run_js(f'{{}}.scrollBy({pixel}, 0);')

    def right(self, pixel=300):
        """向右滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        self._run_js(f'{{}}.scrollBy({pixel}, 0);')

    def _wait_scrolled(self):
        if not self._wait_complete:
            return

        page = self._driver.page if isinstance(self._driver, ChromiumElement) else self._driver
        r = page.run_cdp('Page.getLayoutMetrics')
        x = r['layoutViewport']['pageX']
        y = r['layoutViewport']['pageY']

        while True:
            sleep(.1)
            r = page.run_cdp('Page.getLayoutMetrics')
            x1 = r['layoutViewport']['pageX']
            y1 = r['layoutViewport']['pageY']

            if x == x1 and y == y1:
                break

            x = x1
            y = y1


class ChromiumElementScroll(ChromiumScroll):
    def to_see(self, center=False):
        """滚动页面直到元素可见
        :param center: 是否尽量滚动到页面正中
        :return: None
        """
        self._driver.page.scroll.to_see(self._driver, center=center)


class ChromiumSelect(object):
    """ChromiumSelect 类专门用于处理 d 模式下 select 标签"""

    def __init__(self, ele):
        """
        :param ele: select 元素对象
        """
        if ele.tag != 'select':
            raise TypeError("select方法只能在<select>元素使用。")

        self._ele = ele

    def __call__(self, text_or_index, timeout=None):
        """选定下拉列表中子元素
        :param text_or_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: None
        """
        para_type = 'index' if isinstance(text_or_index, int) else 'text'
        timeout = timeout if timeout is not None else self._ele.page.timeout
        return self._select(text_or_index, para_type, timeout=timeout)

    @property
    def is_multi(self):
        """返回是否多选表单"""
        return self._ele.attr('multiple') is not None

    @property
    def options(self):
        """返回所有选项元素组成的列表"""
        return self._ele.eles('xpath://option')

    @property
    def selected_option(self):
        """返回第一个被选中的option元素
        :return: ChromiumElement对象或None
        """
        ele = self._ele.run_js('return this.options[this.selectedIndex];')
        return ele

    @property
    def selected_options(self):
        """返回所有被选中的option元素列表
        :return: ChromiumElement对象组成的列表
        """
        return [x for x in self.options if x.states.is_selected]

    def all(self):
        """全选"""
        if not self.is_multi:
            raise TypeError("只能在多选菜单执行此操作。")
        return self._by_loc('tag:option', 1, False)

    def invert(self):
        """反选"""
        if not self.is_multi:
            raise TypeError("只能对多项选框执行反选。")
        change = False
        for i in self.options:
            change = True
            mode = 'false' if i.states.is_selected else 'true'
            i.run_js(f'this.selected={mode};')
        if change:
            self._dispatch_change()

    def clear(self):
        """清除所有已选项"""
        if not self.is_multi:
            raise TypeError("只能在多选菜单执行此操作。")
        return self._by_loc('tag:option', 1, True)

    def by_text(self, text, timeout=None):
        """此方法用于根据text值选择项。当元素是多选列表时，可以接收list或tuple
        :param text: text属性值，传入list或tuple可选择多项
        :param timeout: 超时时间，为None默认使用页面超时时间
        :return: 是否选择成功
        """
        return self._select(text, 'text', False, timeout)

    def by_value(self, value, timeout=None):
        """此方法用于根据value值选择项。当元素是多选列表时，可以接收list或tuple
        :param value: value属性值，传入list或tuple可选择多项
        :param timeout: 超时时间，为None默认使用页面超时时间
        :return: 是否选择成功
        """
        return self._select(value, 'value', False, timeout)

    def by_index(self, index, timeout=None):
        """此方法用于根据index值选择项。当元素是多选列表时，可以接收list或tuple
        :param index: 序号，0开始，传入list或tuple可选择多项
        :param timeout: 超时时间，为None默认使用页面超时时间
        :return: 是否选择成功
        """
        return self._select(index, 'index', False, timeout)

    def by_loc(self, loc, timeout=None):
        """用定位符选择指定的项
        :param loc: 定位符
        :param timeout: 超时时间
        :return: 是否选择成功
        """
        return self._by_loc(loc, timeout)

    def cancel_by_text(self, text, timeout=None):
        """此方法用于根据text值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param text: 文本，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        return self._select(text, 'text', True, timeout)

    def cancel_by_value(self, value, timeout=None):
        """此方法用于根据value值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param value: value属性值，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        return self._select(value, 'value', True, timeout)

    def cancel_by_index(self, index, timeout=None):
        """此方法用于根据index值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param index: 序号，0开始，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        return self._select(index, 'index', True, timeout)

    def cancel_by_loc(self, loc, timeout=None):
        """用定位符取消选择指定的项
        :param loc: 定位符
        :param timeout: 超时时间
        :return: 是否选择成功
        """
        return self._by_loc(loc, timeout, True)

    def _by_loc(self, loc, timeout=None, cancel=False):
        """用定位符取消选择指定的项
        :param loc: 定位符
        :param timeout: 超时时间
        :param cancel: 是否取消选择
        :return: 是否选择成功
        """
        eles = self._ele.eles(loc, timeout)
        if not eles:
            return False

        mode = 'false' if cancel else 'true'
        if self.is_multi:
            for ele in eles:
                ele.run_js(f'this.selected={mode};')
            self._dispatch_change()
            return True

        eles[0].run_js(f'this.selected={mode};')
        self._dispatch_change()
        return True

    def _select(self, condition, para_type='text', cancel=False, timeout=None):
        """选定或取消选定下拉列表中子元素
        :param condition: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param cancel: 是否取消选择
        :return: 是否选择成功
        """
        if not self.is_multi and isinstance(condition, (list, tuple)):
            raise TypeError('单选列表只能传入str格式。')

        mode = 'false' if cancel else 'true'
        timeout = timeout if timeout is not None else self._ele.page.timeout
        condition = {condition} if isinstance(condition, (str, int)) else set(condition)

        if para_type in ('text', 'value'):
            return self._text_value(condition, para_type, mode, timeout)
        elif para_type == 'index':
            return self._index(condition, mode, timeout)

    def _text_value(self, condition, para_type, mode, timeout):
        """执行text和value搜索
        :param condition: 条件set
        :param para_type: 参数类型，可选 'text'、'value'
        :param mode: 'true' 或 'false'
        :param timeout: 超时时间
        :return: 是否选择成功
        """
        ok = False
        text_len = len(condition)
        eles = []
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if para_type == 'text':
                eles = [i for i in self.options if i.text in condition]
            elif para_type == 'value':
                eles = [i for i in self.options if i.attr('value') in condition]

            if len(eles) >= text_len:
                ok = True
                break

        if ok:
            for i in eles:
                i.run_js(f'this.selected={mode};')

            self._dispatch_change()
            return True

        return False

    def _index(self, condition, mode, timeout):
        """执行index搜索
        :param condition: 条件set
        :param mode: 'true' 或 'false'
        :param timeout: 超时时间
        :return: 是否选择成功
        """
        ok = False
        condition = [int(i) for i in condition]
        text_len = max(condition)
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if len(self.options) >= text_len:
                ok = True
                break

        if ok:
            eles = self.options
            for i in condition:
                eles[i - 1].run_js(f'this.selected={mode};')

            self._dispatch_change()
            return True

        return False

    def _dispatch_change(self):
        """触发修改动作"""
        self._ele.run_js('this.dispatchEvent(new UIEvent("change"));')


class ChromiumElementWaiter(object):
    """等待元素在dom中某种状态，如删除、显示、隐藏"""

    def __init__(self, page, ele):
        """等待元素在dom中某种状态，如删除、显示、隐藏
        :param page: 元素所在页面
        :param ele: 要等待的元素
        """
        self._page = page
        self._ele = ele

    def delete(self, timeout=None):
        """等待元素从dom删除
        :param timeout: 超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        return self._wait_state('is_alive', False, timeout)

    def display(self, timeout=None):
        """等待元素从dom显示
        :param timeout: 超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        return self._wait_state('is_displayed', True, timeout)

    def hidden(self, timeout=None):
        """等待元素从dom隐藏
        :param timeout: 超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        return self._wait_state('is_displayed', False, timeout)

    def covered(self, timeout=None):
        """等待当前元素被遮盖
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        return self._wait_state('is_covered', True, timeout)

    def not_covered(self, timeout=None):
        """等待当前元素被遮盖
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        return self._wait_state('is_covered', False, timeout)

    def enabled(self, timeout=None):
        """等待当前元素变成可用
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        return self._wait_state('is_enabled', True, timeout)

    def disabled(self, timeout=None):
        """等待当前元素变成可用
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        return self._wait_state('is_enabled', False, timeout)

    def disabled_or_delete(self, timeout=None):
        """等待当前元素变成不可用或从DOM移除
        :param timeout:超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        if timeout is None:
            timeout = self._page.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if not self._ele.states.is_enabled or not self._ele.states.is_alive:
                return True
            sleep(.05)

        return False

    def _wait_state(self, attr, mode=False, timeout=None):
        """等待元素某个bool状态到达指定状态
        :param attr: 状态名称
        :param mode: True或False
        :param timeout: 超时时间，为None使用元素所在页面timeout属性
        :return: 是否等待成功
        """
        if timeout is None:
            timeout = self._page.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if self._ele.states.__getattribute__(attr) == mode:
                return True
            sleep(.05)

        return False


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
