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
from .common import make_absolute_link, get_loc, get_ele_txt, format_html, is_js_func, _location_in_viewport
from .keys import _keys_to_typing, _keyDescriptionForString, _keyDefinitions
from .session_element import make_session_ele

__FRAME_ELEMENT__ = ('iframe', 'frame')


class ChromiumElement(DrissionElement):
    """ChromePage页面对象中的元素对象"""

    def __init__(self, page, node_id=None, obj_id=None, backend_id=None):
        """初始化，node_id和obj_id必须至少传入一个                       \n
        :param page: 元素所在ChromePage页面对象
        :param node_id: cdp中的node id
        :param obj_id: js中的object id
        :param backend_id: backend id
        """
        super().__init__(page)
        self._select = None
        self._scroll = None
        self._tag = None

        if node_id:
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
            raise RuntimeError('元素可能已失效。')

        doc = self.run_script('return this.ownerDocument;')
        self._doc_id = doc['objectId'] if doc else None

    def __repr__(self):
        attrs = self.attrs
        attrs = [f"{attr}='{attrs[attr]}'" for attr in attrs]
        return f'<ChromiumElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素                                             \n
        例：ele2 = ele1('@id=ele_id')                               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: ChromiumElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    @property
    def tag(self):
        """返回元素tag"""
        if self._tag is None:
            self._tag = self.page.run_cdp('DOM.describeNode', nodeId=self._node_id, not_change=True)['node'][
                'localName'].lower()
        return self._tag

    @property
    def html(self):
        """返回元素outerHTML文本"""
        return self.page.run_cdp('DOM.getOuterHTML', nodeId=self._node_id, not_change=True)['outerHTML']

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        return self.run_script('return this.innerHTML;')

    @property
    def attrs(self):
        """返回元素所有attribute属性"""
        attrs = self.page.run_cdp('DOM.getAttributes', nodeId=self._node_id, not_change=True)['attributes']
        attrs_len = len(attrs)
        return {attrs[i]: attrs[i + 1] for i in range(0, attrs_len, 2)}

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
    def obj_id(self):
        """返回js中的object id"""
        return self._obj_id

    @property
    def node_id(self):
        """返回cdp中的node id"""
        return self._node_id

    @property
    def backend_id(self):
        """返回backend id"""
        return self._backend_id

    @property
    def doc_id(self):
        """返回所在document的object id"""
        return self._doc_id

    @property
    def size(self):
        """返回元素宽和高"""
        try:
            model = self.page.run_cdp('DOM.getBoxModel', nodeId=self._node_id, not_change=True)['model']
            return model['height'], model['width']
        except Exception:
            return 0, 0

    @property
    def client_location(self):
        """返回元素左上角在视口中的坐标"""
        m = self._get_client_rect('border')
        return (m[0], m[1]) if m else (0, 0)

    @property
    def client_midpoint(self):
        """返回元素中间点在视口中的坐标"""
        m = self._get_client_rect('border')
        return (m[0] + (m[2] - m[0]) // 2, m[3] + (m[5] - m[3]) // 2) if m else (0, 0)

    @property
    def location(self):
        """返回元素左上角的绝对坐标"""
        cl = self.client_location
        return self._get_absolute_rect(cl[0], cl[1]) if cl else (0, 0)

    @property
    def midpoint(self):
        """返回元素中间点的绝对坐标"""
        cl = self.client_midpoint
        return self._get_absolute_rect(cl[0], cl[1]) if cl else (0, 0)

    @property
    def _client_click_point(self):
        """返回元素左上角可接受点击的点视口坐标"""
        m = self._get_client_rect('padding')
        return (self.client_midpoint[0], m[1]) if m else (0, 0)

    @property
    def _click_point(self):
        """返回元素左上角可接受点击的点的绝对坐标"""
        cl = self._client_click_point
        return self._get_absolute_rect(cl[0], cl[1]) if cl else (0, 0)

    @property
    def shadow_root(self):
        """返回当前元素的shadow_root元素对象"""
        info = self.page.run_cdp('DOM.describeNode', nodeId=self.node_id, not_change=True)['node']
        if not info.get('shadowRoots', None):
            return None

        return ChromiumShadowRootElement(self, backend_id=info['shadowRoots'][0]['backendNodeId'])

    @property
    def sr(self):
        """返回当前元素的shadow_root元素对象"""
        return self.shadow_root

    @property
    def pseudo_before(self):
        """返回当前元素的::before伪元素内容"""
        return self.style('content', 'before')

    @property
    def pseudo_after(self):
        """返回当前元素的::after伪元素内容"""
        return self.style('content', 'after')

    @property
    def scroll(self):
        """用于滚动滚动条的对象"""
        if self._scroll is None:
            self._scroll = ChromiumScroll(self)
        return self._scroll

    def parent(self, level_or_loc=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位              \n
        :param level_or_loc: 第几级父元素，或定位符
        :return: 上级元素对象
        """
        return super().parent(level_or_loc)

    def prev(self, filter_loc='', index=1, timeout=0):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        return super().prev(index, filter_loc, timeout)

    def next(self, filter_loc='', index=1, timeout=0):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        return super().next(index, filter_loc, timeout)

    def before(self, filter_loc='', index=1, timeout=None):
        """返回当前元素前面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的某个元素或节点
        """
        return super().before(index, filter_loc, timeout)

    def after(self, filter_loc='', index=1, timeout=None):
        """返回当前元素后面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :param timeout: 查找元素的超时时间
        :return: 本元素后面的某个元素或节点
        """
        return super().after(index, filter_loc, timeout)

    def prevs(self, filter_loc='', timeout=0):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        return super().prevs(filter_loc, timeout)

    def nexts(self, filter_loc='', timeout=0):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        return super().nexts(filter_loc, timeout)

    def befores(self, filter_loc='', timeout=None):
        """返回当前元素后面符合条件的全部兄弟元素或节点组成的列表，可用查询语法筛选。查找范围不限兄弟元素，而是整个DOM文档        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的元素或节点组成的列表
        """
        return super().befores(filter_loc, timeout)

    def wait_ele(self, loc_or_ele, timeout=None):
        """返回用于等待子元素到达某个状态的等待器对象                    \n
        :param loc_or_ele: 可以是元素、查询字符串、loc元组
        :param timeout: 等待超时时间
        :return: 用于等待的ElementWaiter对象
        """
        return ChromiumElementWaiter(self, loc_or_ele, timeout)

    @property
    def select(self):
        """返回专门处理下拉列表的Select类，非下拉列表元素返回False"""
        if self._select is None:
            if self.tag != 'select':
                self._select = False
            else:
                self._select = ChromiumSelect(self)

        return self._select

    @property
    def is_selected(self):
        """返回元素是否被选择"""
        return self.run_script('return this.selected;')

    @property
    def is_displayed(self):
        """返回元素是否显示"""
        return not (self.style('visibility') == 'hidden'
                    or self.run_script('return this.offsetParent === null;')
                    or self.style('display') == 'none')

    @property
    def is_enabled(self):
        """返回元素是否可用"""
        return not self.run_script('return this.disabled;')

    @property
    def is_alive(self):
        """返回元素是否仍在DOM中"""
        try:
            d = self.attrs
            return True
        except Exception:
            return False

    @property
    def is_in_viewport(self):
        """返回元素是否出现在视口中，以元素可以接受点击的点为判断"""
        x, y = self.location
        return _location_in_viewport(self.page, x, y) if x else False

    def attr(self, attr):
        """返回attribute属性值                           \n
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

    def set_attr(self, attr, value):
        """设置元素attribute属性          \n
        :param attr: 属性名
        :param value: 属性值
        :return: None
        """
        self.run_script(f'this.setAttribute(arguments[0], arguments[1]);', False, attr, str(value))

    def remove_attr(self, attr):
        """删除元素attribute属性          \n
        :param attr: 属性名
        :return: None
        """
        self.run_script(f'this.removeAttribute("{attr}");')

    def prop(self, prop):
        """获取property属性值            \n
        :param prop: 属性名
        :return: 属性值文本
        """
        p = self.page.run_cdp('Runtime.getProperties', objectId=self._obj_id, not_change=True)['result']
        for i in p:
            if i['name'] == prop:
                if 'value' not in i or 'value' not in i['value']:
                    return None

                return format_html(i['value']['value'])

    def set_prop(self, prop, value):
        """设置元素property属性          \n
        :param prop: 属性名
        :param value: 属性值
        :return: None
        """
        value = value.replace('"', r'\"')
        self.run_script(f'this.{prop}="{value}";')

    def set_innerHTML(self, html):
        """设置元素innerHTML        \n
        :param html: html文本
        :return: None
        """
        self.set_prop('innerHTML', html)

    def run_script(self, script, as_expr=False, *args):
        """运行javascript代码                                                 \n
        :param script: js文本
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
        :return: 运行的结果
        """
        return run_script(self, script, as_expr, self.page.timeouts.script, args, True)

    def run_async_script(self, script, as_expr=False, *args):
        """以异步方式执行js代码                                                 \n
        :param script: js文本
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[2]...
        :return: None
        """
        from threading import Thread
        Thread(target=run_script, args=(self, script, as_expr, self.page.timeouts.script, args, True)).start()

    def ele(self, loc_or_str, timeout=None):
        """返回当前元素下级符合条件的第一个元素、属性或节点文本                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本
        """
        return self._ele(loc_or_str, timeout)

    def eles(self, loc_or_str, timeout=None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_str=None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高        \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        if self.tag in ('iframe', 'frame'):
            return make_session_ele(self.inner_html, loc_or_str)
        return make_session_ele(self, loc_or_str)

    def s_eles(self, loc_or_str=None):
        """查找所有符合条件的元素以SessionElement列表形式返回                         \n
        :param loc_or_str: 定位符
        :return: SessionElement或属性、文本组成的列表
        """
        if self.tag in ('iframe', 'frame'):
            return make_session_ele(self.inner_html, loc_or_str, single=False)
        return make_session_ele(self, loc_or_str, single=False)

    def _ele(self, loc_or_str, timeout=None, single=True, relative=False):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个                                      \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :return: ChromiumElement对象或文本、属性或其组成的列表
        """
        return find_in_chromium_ele(self, loc_or_str, single, timeout, relative=relative)

    def style(self, style, pseudo_ele=''):
        """返回元素样式属性值，可获取伪元素属性值                \n
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"' if pseudo_ele.startswith(':') else f', "::{pseudo_ele}"'
        js = f'return window.getComputedStyle(this{pseudo_ele}).getPropertyValue("{style}");'
        return self.run_script(js)

    def get_src(self):
        """返回元素src资源，base64的会转为bytes返回，其它返回str"""
        src = self.attr('src')
        if not src:
            return None

        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" '
                  '&& this.naturalWidth > 0 && typeof this.naturalHeight != "undefined" '
                  '&& this.naturalHeight > 0')
            end_time = perf_counter() + self.page.timeout
            while not self.run_script(js) and perf_counter() < end_time:
                sleep(.1)

        node = self.page.run_cdp('DOM.describeNode', nodeId=self._node_id, not_change=True)['node']
        frame = node.get('frameId', None)
        frame = frame or self.page.tab_id
        try:
            result = self.page.driver.Page.getResourceContent(frameId=frame, url=src)
        except Exception:
            return None

        if result['base64Encoded']:
            from base64 import b64decode
            data = b64decode(result['content'])
        else:
            data = result['content']
        return data

    def save(self, path=None, rename=None):
        """保存图片或其它有src属性的元素的资源                                \n
        :param path: 文件保存路径，为None时保存到当前文件夹
        :param rename: 文件名称，为None时从资源url获取
        :return: None
        """
        data = self.get_src()
        if not data:
            raise TypeError('该元素无可保存的内容或保存失败。')

        path = path or '.'
        rename = rename or basename(self.attr('src'))
        write_type = 'wb' if isinstance(data, bytes) else 'w'

        Path(path).mkdir(parents=True, exist_ok=True)
        with open(f'{path}{sep}{rename}', write_type) as f:
            f.write(data)

    def get_screenshot(self, path=None, as_bytes=None):
        """对当前元素截图                                                                            \n
        :param path: 完整路径，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否已字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :return: 图片完整路径或字节文本
        """
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" '
                  '&& this.naturalWidth > 0 && typeof this.naturalHeight != "undefined" '
                  '&& this.naturalHeight > 0')
            end_time = perf_counter() + self.page.timeout
            while not self.run_script(js) and perf_counter() < end_time:
                sleep(.1)

        left, top = self.location
        height, width = self.size
        left_top = (left, top)
        right_bottom = (left + width, top + height)
        return self.page.get_screenshot(path, as_bytes=as_bytes, full_page=False,
                                        left_top=left_top, right_bottom=right_bottom)

    def input(self, vals, clear=True):
        """输入文本或组合键，也可用于输入文件路径到input元素（文件间用\n间隔）                          \n
        :param vals: 文本值或按键组合
        :param clear: 输入前是否清空文本框
        :return: None
        """
        if self.tag == 'input' and self.attr('type') == 'file':
            return self._set_file_input(vals)

        try:
            self.page.run_cdp('DOM.focus', nodeId=self._node_id, not_change=True)
        except Exception:
            self.click(by_js=True)

        if clear:
            self.clear(by_js=True)

        # ------------处理字符-------------
        if not isinstance(vals, (tuple, list)):
            vals = (str(vals),)
        modifier, vals = _keys_to_typing(vals)

        if modifier != 0:  # 包含修饰符
            for key in vals:
                _send_key(self, modifier, key)
            return

        if vals.endswith('\n'):
            self.page.driver.Input.insertText(text=vals[:-1])
            _send_key(self, modifier, '\n')
        else:
            self.page.driver.Input.insertText(text=vals)

    def _set_file_input(self, files):
        """设置上传控件值
        :param files: 文件路径列表或字符串，字符串时多个文件用回车分隔
        :return: None
        """
        if isinstance(files, str):
            files = files.split('\n')
        self.page.run_cdp('DOM.setFileInputFiles', files=files, nodeId=self._node_id, not_change=True)

    def clear(self, by_js=False):
        """清空元素文本                                    \n
        :param by_js: 是否用js方式清空
        :return: None
        """
        if by_js:
            self.run_script("this.value='';")

        else:
            self.input(('\ue009', 'a', '\ue017'), clear=False)

    def click(self, by_js=None, retry=False, timeout=.2, wait_loading=0):
        """点击元素                                                                      \n
        如果遇到遮挡，会重新尝试点击直到超时，若都失败就改用js点击                                \n
        :param by_js: 是否用js点击，为True时直接用js点击，为False时重试失败也不会改用js
        :param retry: 遇到其它元素遮挡时，是否重试
        :param timeout: 尝试点击的超时时间，不指定则使用父页面的超时时间，retry为True时才生效
        :param wait_loading: 等待页面进入加载状态超时时间
        :return: 是否点击成功
        """

        def do_it(cx, cy, lx, ly):
            """无遮挡返回True，有遮挡返回False，无元素返回None"""
            try:
                r = self.page.driver.DOM.getNodeForLocation(x=lx, y=ly)
            except Exception:
                return None

            if retry and r.get('nodeId') != self._node_id:
                return False

            self._click(cx, cy)
            return True

        if not by_js:
            self.page.scroll_to_see(self)
            if self.is_in_viewport:
                client_x, client_y = self._client_click_point
                if client_x:
                    loc_x, loc_y = self._click_point

                    click = do_it(client_x, client_y, loc_x, loc_y)
                    if click:
                        self.page.wait_loading(wait_loading)
                        return True

                    timeout = timeout if timeout is not None else self.page.timeout
                    end_time = perf_counter() + timeout
                    while click is False and perf_counter() < end_time:
                        click = do_it(client_x, client_y, loc_x, loc_y)

                    if click is not None:
                        self.page.wait_loading(wait_loading)
                        return True

        if by_js is not False:
            self.run_script('this.click();')
            self.page.wait_loading(wait_loading)
            return True

        return False

    def click_at(self, offset_x=None, offset_y=None, button='left'):
        """带偏移量点击本元素，相对于左上角坐标。不传入x或y值时点击元素左上角可接受点击的点    \n
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :param button: 左键还是右键
        :return: None
        """
        x, y = _offset_scroll(self, offset_x, offset_y)
        self._click(x, y, button)

    def r_click(self):
        """右键单击"""
        self.page.scroll_to_see(self)
        x, y = self._client_click_point
        self._click(x, y, 'right')

    def m_click(self):
        """中键单击"""
        self.page.scroll_to_see(self)
        x, y = self._client_click_point
        self._click(x, y, 'middle')

    def r_click_at(self, offset_x=None, offset_y=None):
        """带偏移量右键单击本元素，相对于左上角坐标。不传入x或y值时点击元素中点    \n
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        self.click_at(offset_x, offset_y, 'right')

    def _click(self, client_x, client_y, button='left'):
        """实施点击                        \n
        :param client_x: 视口中的x坐标
        :param client_y: 视口中的y坐标
        :param button: 'left' 或 'right'
        :return: None
        """
        self.page.driver.Input.dispatchMouseEvent(type='mousePressed', x=client_x, y=client_y, button=button,
                                                  clickCount=1)
        sleep(.05)
        self.page.driver.Input.dispatchMouseEvent(type='mouseReleased', x=client_x, y=client_y, button=button)

    def hover(self, offset_x=None, offset_y=None):
        """鼠标悬停，可接受偏移量，偏移量相对于元素左上角坐标。不传入x或y值时悬停在元素中点    \n
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        x, y = _offset_scroll(self, offset_x, offset_y)
        self.page.driver.Input.dispatchMouseEvent(type='mouseMoved', x=x, y=y)

    def drag(self, offset_x=0, offset_y=0, speed=40, shake=True):
        """拖拽当前元素到相对位置                   \n
        :param offset_x: x变化值
        :param offset_y: y变化值
        :param speed: 拖动的速度，传入0即瞬间到达
        :param shake: 是否随机抖动
        :return: None
        """
        curr_x, curr_y = self.midpoint
        offset_x += curr_x
        offset_y += curr_y
        self.drag_to((offset_x, offset_y), speed, shake)

    def drag_to(self, ele_or_loc, speed=40, shake=True):
        """拖拽当前元素，目标为另一个元素或坐标元组                     \n
        :param ele_or_loc: 另一个元素或坐标元组，坐标为元素中点的坐标
        :param speed: 拖动的速度，传入0即瞬间到达
        :param shake: 是否随机抖动
        :return: None
        """
        # x, y：目标点坐标
        if isinstance(ele_or_loc, ChromiumElement):
            target_x, target_y = ele_or_loc.midpoint
        elif isinstance(ele_or_loc, (list, tuple)):
            target_x, target_y = ele_or_loc
        else:
            raise TypeError('需要ChromiumElement对象或坐标。')

        current_x, current_y = self.midpoint
        width = target_x - current_x
        height = target_y - current_y
        num = 0 if not speed else int(((abs(width) ** 2 + abs(height) ** 2) ** .5) // speed)

        # 将要经过的点存入列表
        points = [(int(current_x + i * (width / num)), int(current_y + i * (height / num))) for i in range(1, num)]
        points.append((target_x, target_y))

        from .action_chains import ActionChains
        from random import randint
        actions = ActionChains(self.page)
        actions.hold(self)

        # 逐个访问要经过的点
        for x, y in points:
            if shake:
                x += randint(-3, 4)
                y += randint(-3, 4)
            actions.move(x - current_x, y - current_y)
            current_x, current_y = x, y
        actions.release()

    def _get_obj_id(self, node_id=None, backend_id=None):
        """根据传入node id获取js中的object id          \n
        :param node_id: cdp中的node id
        :param backend_id: backend id
        :return: js中的object id
        """
        if node_id:
            return self.page.run_cdp('DOM.resolveNode', nodeId=node_id, not_change=True)['object']['objectId']
        else:
            return self.page.run_cdp('DOM.resolveNode', backendNodeId=backend_id, not_change=True)['object']['objectId']

    def _get_node_id(self, obj_id=None, backend_id=None):
        """根据传入object id获取cdp中的node id          \n
        :param obj_id: js中的object id
        :param backend_id: backend id
        :return: cdp中的node id
        """
        if obj_id:
            return self.page.run_cdp('DOM.requestNode', objectId=obj_id, not_change=True)['nodeId']
        else:
            return self.page.run_cdp('DOM.describeNode', backendNodeId=backend_id, not_change=True)['node']['nodeId']

    def _get_backend_id(self, node_id):
        """根据传入node id获取backend id
        :param node_id:
        :return: backend id
        """
        return self.page.run_cdp('DOM.describeNode', nodeId=node_id, not_change=True)['node']['backendNodeId']

    def _get_ele_path(self, mode):
        """返获取css路径或xpath路径"""
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
        t = self.run_script(js)
        return f':root{t}' if mode == 'css' else t

    def _get_client_rect(self, quad):
        """按照类型返回窗口坐标                             \n
        :param quad: 方框类型，margin border padding
        :return: 四个角坐标，大小为0时返回None
        """
        try:
            return self.page.run_cdp('DOM.getBoxModel', nodeId=self.node_id, not_change=True)['model'][quad]
        except:
            return None

    def _get_absolute_rect(self, x, y):
        """根据绝对坐标获取窗口坐标"""
        js = 'return document.documentElement.scrollLeft+" "+document.documentElement.scrollTop;'
        xy = self.run_script(js)
        sx, sy = xy.split(' ')
        return x + int(float(sx)), y + int(float(sy))


class ChromiumShadowRootElement(BaseElement):
    """ChromiumShadowRootElement是用于处理ShadowRoot的类，使用方法和ChromiumElement基本一致"""

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

    def __repr__(self):
        return f'<ShadowRootElement in {self.parent_ele} >'

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素                                            \n
        例：ele2 = ele1('@id=ele_id')                               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: DriverElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    @property
    def is_enabled(self):
        """返回元素是否可用"""
        return not self.run_script('return this.disabled;')

    @property
    def is_alive(self):
        """返回元素是否仍在DOM中"""
        try:
            self.page.run_cdp('DOM.describeNode', nodeId=self._node_id, not_change=True)
            return True
        except Exception:
            return False

    @property
    def node_id(self):
        """返回元素cdp中的node id"""
        return self._node_id

    @property
    def obj_id(self):
        """返回元素js中的object id"""
        return self._obj_id

    @property
    def backend_id(self):
        """返回backend id"""
        return self._backend_id

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
        return self.run_script('return this.innerHTML;')

    def run_script(self, script, as_expr=False, *args):
        """运行javascript代码                                                 \n
        :param script: js文本
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[2]...
        :return: 运行的结果
        """
        return run_script(self, script, as_expr, self.page.timeouts.script, args)

    def run_async_script(self, script, as_expr=False, *args):
        """以异步方式执行js代码                                                 \n
        :param script: js文本
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param args: 参数，按顺序在js文本中对应argument[0]、argument[2]...
        :return: None
        """
        from threading import Thread
        Thread(target=run_script, args=(self, script, as_expr, self.page.timeouts.script, args)).start()

    def parent(self, level_or_loc=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位              \n
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

        return self.parent_ele._ele(loc, timeout=0, relative=True)

    def next(self, filter_loc='', index=1):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 第几个查询结果元素
        :return: ChromiumElement对象
        """
        nodes = self.nexts(filter_loc=filter_loc)
        return nodes[index - 1] if nodes else None

    def before(self, filter_loc='', index=1):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 前面第几个查询结果元素
        :return: 本元素前面的某个元素或节点
        """
        nodes = self.befores(filter_loc=filter_loc)
        return nodes[index - 1] if nodes else None

    def after(self, filter_loc='', index=1):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param filter_loc: 用于筛选元素的查询语法
        :param index: 后面第几个查询结果元素
        :return: 本元素后面的某个元素或节点
        """
        nodes = self.afters(filter_loc=filter_loc)
        return nodes[index - 1] if nodes else None

    def nexts(self, filter_loc=''):
        """返回后面所有兄弟元素或节点组成的列表        \n
        :param filter_loc: 用于筛选元素的查询语法
        :return: ChromiumElement对象组成的列表
        """
        loc = get_loc(filter_loc, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./{loc}'
        return self.parent_ele._ele(xpath, timeout=0.1, single=False, relative=True)

    def befores(self, filter_loc=''):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :return: 本元素前面的元素或节点组成的列表
        """
        loc = get_loc(filter_loc, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./preceding::{loc}'
        return self.parent_ele._ele(xpath, timeout=0.1, single=False, relative=True)

    def afters(self, filter_loc=''):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :return: 本元素后面的元素或节点组成的列表
        """
        eles1 = self.nexts(filter_loc)
        loc = get_loc(filter_loc, True)[1].lstrip('./')
        xpath = f'xpath:./following::{loc}'
        return eles1 + self.parent_ele._ele(xpath, timeout=0.1, single=False, relative=True)

    def ele(self, loc_or_str, timeout=None):
        """返回当前元素下级符合条件的第一个元素                                   \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象
        """
        return self._ele(loc_or_str, timeout)

    def eles(self, loc_or_str, timeout=None):
        """返回当前元素下级所有符合条件的子元素                                              \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: ChromiumElement对象组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_str=None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_str)

    def s_eles(self, loc_or_str):
        """查找所有符合条件的元素以SessionElement列表形式返回，处理复杂页面时效率很高                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象
        """
        return make_session_ele(self, loc_or_str, single=False)

    def _ele(self, loc_or_str, timeout=None, single=True, relative=False):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
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
            return None if single else eles

        css_paths = [i.css_path[47:] for i in eles]
        if single:
            node_id = self.page.run_cdp('DOM.querySelector',
                                        nodeId=self._node_id, selector=css_paths[0], not_change=True)['nodeId']
            return make_chromium_ele(self.page, node_id=node_id) if node_id else None

        else:
            results = []
            for i in css_paths:
                node_id = self.page.run_cdp('DOM.querySelector',
                                            nodeId=self._node_id, selector=i, not_change=True)['nodeId']
                if node_id:
                    results.append(make_chromium_ele(self.page, node_id=node_id))
            return results

    def _get_node_id(self, obj_id):
        """返回元素node id"""
        return self.page.run_cdp('DOM.requestNode', objectId=obj_id, not_change=True)['nodeId']

    def _get_obj_id(self, back_id):
        """返回元素object id"""
        return self.page.run_cdp('DOM.resolveNode', backendNodeId=back_id, not_change=True)['object']['objectId']

    def _get_backend_id(self, node_id):
        """返回元素object id"""
        return self.page.run_cdp('DOM.describeNode', nodeId=node_id, not_change=True)['node']['backendNodeId']


def find_in_chromium_ele(ele, loc, single=True, timeout=None, relative=True):
    """在chromium元素中查找                                   \n
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
        return _find_by_xpath(ele, loc[1], single, timeout, relative=relative)

    else:
        return _find_by_css(ele, loc[1], single, timeout)


def _find_by_xpath(ele, xpath, single, timeout, relative=True):
    """执行用xpath在元素中查找元素
    :param ele: 在此元素中查找
    :param xpath: 查找语句
    :param single: 是否只返回第一个结果
    :param timeout: 超时时间
    :return: ChromiumElement或其组成的列表
    """
    type_txt = '9' if single else '7'
    node_txt = 'this.contentDocument' if ele.tag in ('iframe', 'frame') and not relative else 'this'
    js = _make_js_for_find_ele_by_xpath(xpath, type_txt, node_txt)
    r = ele.page.run_cdp('Runtime.callFunctionOn',
                         functionDeclaration=js, objectId=ele.obj_id, returnByValue=False, awaitPromise=True,
                         userGesture=True)
    if r['result']['type'] == 'string':
        return r['result']['value']

    if 'exceptionDetails' in r:
        if 'The result is not a node set' in r['result']['description']:
            js = _make_js_for_find_ele_by_xpath(xpath, '1', node_txt)
            r = ele.page.run_cdp('Runtime.callFunctionOn',
                                 functionDeclaration=js, objectId=ele.obj_id, returnByValue=False, awaitPromise=True,
                                 userGesture=True)
            return r['result']['value']
        else:
            raise SyntaxError(f'查询语句错误：\n{r}')

    end_time = perf_counter() + timeout
    while (r['result']['subtype'] == 'null'
           or r['result']['description'] == 'NodeList(0)') and perf_counter() < end_time:
        r = ele.page.run_cdp('Runtime.callFunctionOn',
                             functionDeclaration=js, objectId=ele.obj_id, returnByValue=False, awaitPromise=True,
                             userGesture=True)

    if single:
        return None if r['result']['subtype'] == 'null' else make_chromium_ele(ele.page, obj_id=r['result']['objectId'])

    if r['result']['description'] == 'NodeList(0)':
        return []
    else:
        r = ele.page.driver.Runtime.getProperties(objectId=r['result']['objectId'], ownProperties=True)['result']
        return [make_chromium_ele(ele.page, obj_id=i['value']['objectId'])
                if i['value']['type'] == 'object' else i['value']['value']
                for i in r[:-1]]


def _find_by_css(ele, selector, single, timeout):
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
    r = ele.page.run_cdp('Runtime.callFunctionOn',
                         functionDeclaration=js, objectId=ele.obj_id, returnByValue=False, awaitPromise=True,
                         userGesture=True)
    if 'exceptionDetails' in r:
        raise SyntaxError(f'查询语句错误：\n{r}')

    end_time = perf_counter() + timeout
    while (r['result']['subtype'] == 'null'
           or r['result']['description'] == 'NodeList(0)') and perf_counter() < end_time:
        r = ele.page.run_cdp('Runtime.callFunctionOn',
                             functionDeclaration=js, objectId=ele.obj_id, returnByValue=False, awaitPromise=True,
                             userGesture=True)

    if single:
        return None if r['result']['subtype'] == 'null' else make_chromium_ele(ele.page, obj_id=r['result']['objectId'])

    if r['result']['description'] == 'NodeList(0)':
        return []
    else:
        r = ele.page.driver.Runtime.getProperties(objectId=r['result']['objectId'], ownProperties=True)['result']
        return [make_chromium_ele(ele.page, obj_id=i['value']['objectId']) for i in r]


def make_chromium_ele(page, node_id=None, obj_id=None):
    """根据node id或object id生成相应元素对象          \n
    :param page: ChromiumPage对象
    :param node_id: 元素的node id
    :param obj_id: 元素的object id
    :return: ChromiumElement对象或ChromiumFrame对象
    """
    ele = ChromiumElement(page, obj_id=obj_id, node_id=node_id)
    if ele.tag in ('iframe', 'frame'):
        from .chromium_frame import ChromiumFrame
        ele = ChromiumFrame(page, ele)

    return ele


def _make_js_for_find_ele_by_xpath(xpath, type_txt, node_txt):
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

    js = f'function(){{var e=document.evaluate(\'{xpath}\',{node_txt},null,{type_txt},null);\n{for_txt}\n{return_txt}}}'

    return js


def run_script(page_or_ele, script, as_expr=False, timeout=None, args=None, not_change=False):
    """运行javascript代码                                                 \n
    :param page_or_ele: 页面对象或元素对象
    :param script: js文本
    :param as_expr: 是否作为表达式运行，为True时args无效
    :param timeout: 超时时间
    :param args: 参数，按顺序在js文本中对应argument[0]、argument[1]...
    :param not_change: 执行时是否切换页面对象模式
    :return: js执行结果
    """
    if isinstance(page_or_ele, (ChromiumElement, ChromiumShadowRootElement)):
        page = page_or_ele.page
        obj_id = page_or_ele.obj_id
    else:
        page = page_or_ele
        obj_id = page_or_ele._root_id

    if as_expr:
        res = page.run_cdp('Runtime.evaluate',
                           expression=script,
                           returnByValue=False,
                           awaitPromise=True,
                           userGesture=True,
                           timeout=timeout * 1000,
                           not_change=not_change)

    else:
        args = args or ()
        if not is_js_func(script):
            script = f'function(){{{script}}}'
        res = page.run_cdp('Runtime.callFunctionOn',
                           functionDeclaration=script,
                           objectId=obj_id,
                           arguments=[_convert_argument(arg) for arg in args],
                           returnByValue=False,
                           awaitPromise=True,
                           userGesture=True,
                           not_change=not_change)

    exceptionDetails = res.get('exceptionDetails')
    if exceptionDetails:
        raise RuntimeError(f'javascript错误: {exceptionDetails}')

    try:
        return _parse_js_result(page, page_or_ele, res.get('result'))
    except Exception:
        return res


def _parse_js_result(page, ele, result):
    """解析js返回的结果"""
    if 'unserializableValue' in result:
        return result['unserializableValue']

    the_type = result['type']

    if the_type == 'object':
        sub_type = result['subtype']
        if sub_type == 'null':
            return None

        elif sub_type == 'node':
            class_name = result['className']
            if class_name == 'ShadowRoot':
                return ChromiumShadowRootElement(ele, obj_id=result['objectId'])
            elif class_name == 'HTMLDocument':
                return result
            else:
                return make_chromium_ele(page, obj_id=result['objectId'])

        elif sub_type == 'array':
            r = page.driver.Runtime.getProperties(objectId=result['result']['objectId'], ownProperties=True)['result']
            return [_parse_js_result(page, ele, result=i['value']) for i in r]

        else:
            return result['value']

    elif the_type == 'undefined':
        return None

    else:
        return result['value']


def _convert_argument(arg):
    """把参数转换成js能够接收的形式"""
    if isinstance(arg, ChromiumElement):
        return {'objectId': arg.obj_id}

    elif isinstance(arg, (int, float, str, bool)):
        return {'value': arg}

    from math import inf
    if arg == inf:
        return {'unserializableValue': 'Infinity'}
    if arg == -inf:
        return {'unserializableValue': '-Infinity'}


def _send_enter(ele):
    """发送回车"""
    data = {'type': 'keyDown', 'modifiers': 0, 'windowsVirtualKeyCode': 13, 'code': 'Enter', 'key': 'Enter',
            'text': '\r', 'autoRepeat': False, 'unmodifiedText': '\r', 'location': 0, 'isKeypad': False}

    ele.page.driver.Input.dispatchKeyEvent(**data)
    data['type'] = 'keyUp'
    ele.page.driver.Input.dispatchKeyEvent(**data)


def _send_key(ele, modifier, key):
    """发送一个字，在键盘中的字符触发按键，其它直接发送文本"""
    if key not in _keyDefinitions:
        ele.page.driver.Input.insertText(text=key)

    else:
        description = _keyDescriptionForString(modifier, key)
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

        ele.page.driver.Input.dispatchKeyEvent(**data)
        data['type'] = 'keyUp'
        ele.page.driver.Input.dispatchKeyEvent(**data)


def _offset_scroll(ele, offset_x, offset_y):
    """接收元素及偏移坐标，滚动到偏移坐标，返回该点在视口中的坐标
    :param ele: 元素对象
    :param offset_x: 偏移量x
    :param offset_y: 偏移量y
    :return: 视口中的坐标
    """
    loc_x, loc_y = ele.location
    cp_x, cp_y = ele._click_point
    lx = loc_x + offset_x if offset_x else cp_x
    ly = loc_y + offset_y if offset_y else cp_y

    if not _location_in_viewport(ele.page, lx, ly):
        ele.page.scroll.to_location(lx, ly)
    cl_x, cl_y = ele.client_location
    ccp_x, ccp_y = ele._client_click_point
    cx = cl_x + offset_x if offset_x else ccp_x
    cy = cl_y + offset_y if offset_y else ccp_y
    return cx, cy


class ChromiumScroll(object):
    """用于滚动的对象"""

    def __init__(self, page_or_ele):
        """
        :param page_or_ele: ChromePage或ChromiumElement
        """
        self.page_or_ele = page_or_ele
        if isinstance(page_or_ele, ChromiumElement):
            self.t1 = self.t2 = 'this'
        else:
            self.t1 = 'window'
            self.t2 = 'document.documentElement'

    def _run_script(self, js):
        js = js.format(self.t1, self.t2, self.t2)
        if self.t1 == 'this':  # 在元素上滚动
            self.page_or_ele.run_script(js)
        else:
            self.page_or_ele.run_script(js, as_expr=True)

    def to_top(self):
        """滚动到顶端，水平位置不变"""
        self._run_script('{}.scrollTo({}.scrollLeft,0);')

    def to_bottom(self):
        """滚动到底端，水平位置不变"""
        self._run_script('{}.scrollTo({}.scrollLeft,{}.scrollHeight);')

    def to_half(self):
        """滚动到垂直中间位置，水平位置不变"""
        self._run_script('{}.scrollTo({}.scrollLeft,{}.scrollHeight/2);')

    def to_rightmost(self):
        """滚动到最右边，垂直位置不变"""
        self._run_script('{}.scrollTo({}.scrollWidth,{}.scrollTop);')

    def to_leftmost(self):
        """滚动到最左边，垂直位置不变"""
        self._run_script('{}.scrollTo(0,{}.scrollTop);')

    def to_location(self, x, y):
        """滚动到指定位置                 \n
        :param x: 水平距离
        :param y: 垂直距离
        :return: None
        """
        self._run_script(f'{{}}.scrollTo({x},{y});')

    def up(self, pixel=300):
        """向上滚动若干像素，水平位置不变    \n
        :param pixel: 滚动的像素
        :return: None
        """
        pixel = -pixel
        self._run_script(f'{{}}.scrollBy(0,{pixel});')

    def down(self, pixel=300):
        """向下滚动若干像素，水平位置不变    \n
        :param pixel: 滚动的像素
        :return: None
        """
        self._run_script(f'{{}}.scrollBy(0,{pixel});')

    def left(self, pixel=300):
        """向左滚动若干像素，垂直位置不变    \n
        :param pixel: 滚动的像素
        :return: None
        """
        pixel = -pixel
        self._run_script(f'{{}}.scrollBy({pixel},0);')

    def right(self, pixel=300):
        """向右滚动若干像素，垂直位置不变    \n
        :param pixel: 滚动的像素
        :return: None
        """
        self._run_script(f'{{}}.scrollBy({pixel},0);')


class ChromiumSelect(object):
    """ChromiumSelect 类专门用于处理 d 模式下 select 标签"""

    def __init__(self, ele):
        """初始化                      \n
        :param ele: select 元素对象
        """
        if ele.tag != 'select':
            raise TypeError("select方法只能在<select>元素使用。")

        self._ele = ele

    def __call__(self, text_or_index, timeout=None):
        """选定下拉列表中子元素                                                             \n
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
        multi = self._ele.attr('multiple')
        return multi and multi.lower() != "false"

    @property
    def options(self):
        """返回所有选项元素组成的列表"""
        return self._ele.eles('tag:option')

    @property
    def selected_option(self):
        """返回第一个被选中的option元素        \n
        :return: ChromiumElement对象或None
        """
        ele = self._ele.run_script('return this.options[this.selectedIndex];')
        return ele

    @property
    def selected_options(self):
        """返回所有被选中的option元素列表        \n
        :return: ChromiumElement对象组成的列表
        """
        return [x for x in self.options if x.is_selected]

    def clear(self):
        """清除所有已选项"""
        if not self.is_multi:
            raise NotImplementedError("只能在多选菜单执行此操作。")
        for opt in self.options:
            if opt.is_selected:
                opt.click(by_js=True)

    def by_text(self, text, timeout=None):
        """此方法用于根据text值选择项。当元素是多选列表时，可以接收list或tuple  \n
        :param text: text属性值，传入list或tuple可选择多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否选择成功
        """
        timeout = timeout if timeout is not None else self._ele.page.timeout
        return self._select(text, 'text', False, timeout)

    def by_value(self, value, timeout=None):
        """此方法用于根据value值选择项。当元素是多选列表时，可以接收list或tuple  \n
        :param value: value属性值，传入list或tuple可选择多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否选择成功
        """
        timeout = timeout if timeout is not None else self._ele.page.timeout
        return self._select(value, 'value', False, timeout)

    def by_index(self, index, timeout=None):
        """此方法用于根据index值选择项。当元素是多选列表时，可以接收list或tuple  \n
        :param index: 序号，0开始，传入list或tuple可选择多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否选择成功
        """
        timeout = timeout if timeout is not None else self._ele.page.timeout
        return self._select(index, 'index', False, timeout)

    def cancel_by_text(self, text, timeout=None):
        """此方法用于根据text值取消选择项。当元素是多选列表时，可以接收list或tuple  \n
        :param text: 文本，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        timeout = timeout if timeout is not None else self._ele.page.timeout
        return self._select(text, 'text', True, timeout)

    def cancel_by_value(self, value, timeout=None):
        """此方法用于根据value值取消选择项。当元素是多选列表时，可以接收list或tuple  \n
        :param value: value属性值，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        timeout = timeout if timeout is not None else self._ele.page.timeout
        return self._select(value, 'value', True, timeout)

    def cancel_by_index(self, index, timeout=None):
        """此方法用于根据index值取消选择项。当元素是多选列表时，可以接收list或tuple  \n
        :param index: 序号，0开始，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        timeout = timeout if timeout is not None else self._ele.page.timeout
        return self._select(index, 'index', True, timeout)

    def invert(self):
        """反选"""
        if not self.is_multi:
            raise NotImplementedError("只能对多项选框执行反选。")

        for i in self.options:
            i.click(by_js=True)

    def _select(self, text_value_index=None, para_type='text', deselect=False, timeout=None):
        """选定或取消选定下拉列表中子元素                                                             \n
        :param text_value_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param deselect: 是否取消选择
        :return: 是否选择成功
        """
        if not self.is_multi and isinstance(text_value_index, (list, tuple)):
            raise TypeError('单选下拉列表不能传入list和tuple')

        def do_select():
            if para_type == 'text':
                ele = self._ele(f'tx={text_value_index}', timeout=0)
            elif para_type == 'value':
                ele = self._ele(f'@value={text_value_index}', timeout=0)
            elif para_type == 'index':
                ele = self._ele(f'x:.//option[{int(text_value_index)}]', timeout=0)
            else:
                raise ValueError('para_type参数只能传入"text"、"value"或"index"。')

            if not ele:
                return False

            js = 'false' if deselect else 'true'
            ele.run_script(f'this.selected={js};')

            return True

        if isinstance(text_value_index, (str, int)):
            ok = do_select()
            end_time = perf_counter() + timeout
            while not ok and perf_counter() < end_time:
                sleep(.2)
                ok = do_select()
            return ok

        elif isinstance(text_value_index, (list, tuple)):
            return self._select_multi(text_value_index, para_type, deselect)

        else:
            raise TypeError('只能传入str、int、list和tuple类型。')

    def _select_multi(self,
                      text_value_index=None,
                      para_type='text',
                      deselect=False):
        """选定或取消选定下拉列表中多个子元素                                                             \n
        :param text_value_index: 根据文本、值选或序号择选多项
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param deselect: 是否取消选择
        :return: 是否选择成功
        """
        if para_type not in ('text', 'value', 'index'):
            raise ValueError('para_type参数只能传入“text”、“value”或“index”')

        if not isinstance(text_value_index, (list, tuple)):
            raise TypeError('只能传入list或tuple类型。')

        success = True
        for i in text_value_index:
            if not isinstance(i, (int, str)):
                raise TypeError('列表只能由str或int组成')

            p = 'index' if isinstance(i, int) else para_type
            if not self._select(i, p, deselect):
                success = False

        return success


class ChromiumElementWaiter(object):
    """等待元素在dom中某种状态，如删除、显示、隐藏"""

    def __init__(self, page_or_ele, loc_or_ele, timeout=None):
        """等待元素在dom中某种状态，如删除、显示、隐藏                         \n
        :param page_or_ele: 页面或父元素
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间，默认读取页面超时时间
        """
        if not isinstance(loc_or_ele, (str, tuple, ChromiumElement)):
            raise TypeError('loc_or_ele只能接收定位符或元素对象。')

        self.driver = page_or_ele
        self.loc_or_ele = loc_or_ele
        if timeout is not None:
            self.timeout = timeout
        else:
            self.timeout = page_or_ele.page.timeout if isinstance(page_or_ele, ChromiumElement) else page_or_ele.timeout

    def delete(self):
        """等待元素从dom删除"""
        if isinstance(self.loc_or_ele, ChromiumElement):
            end_time = perf_counter() + self.timeout
            while perf_counter() < end_time:
                if not self.loc_or_ele.is_alive:
                    return True

        ele = self.driver(self.loc_or_ele, timeout=.5)
        if ele is None:
            return True

        end_time = perf_counter() + self.timeout
        while perf_counter() < end_time:
            if not self.loc_or_ele.is_alive:
                return True

        return False

    def display(self):
        """等待元素从dom显示"""
        return self._wait_ele('display')

    def hidden(self):
        """等待元素从dom隐藏"""
        return self._wait_ele('hidden')

    def _wait_ele(self, mode):
        """执行等待
        :param mode: 等待模式
        :return: 是否等待成功
        """
        target = self.driver(self.loc_or_ele)
        if target is None:
            return None

        end_time = perf_counter() + self.timeout
        while perf_counter() < end_time:
            if mode == 'display' and target.is_displayed:
                return True

            elif mode == 'hidden' and not target.is_displayed:
                return True

        return False
