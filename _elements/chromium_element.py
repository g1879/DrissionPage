# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from json import loads
from os.path import basename
from pathlib import Path
from platform import system
from re import search
from time import perf_counter, sleep

from DataRecorder.tools import get_usable_path, make_valid_name

from .none_element import NoneElement
from .session_element import make_session_ele
from .._base.base import DrissionElement, BaseElement
from .._functions.elements import ChromiumElementsList, SessionElementsList
from .._functions.keys import input_text_or_keys, Keys
from .._functions.locator import get_loc, locator_to_tuple
from .._functions.settings import Settings as _S
from .._functions.web import make_absolute_link, get_ele_txt, format_html, is_js_func, get_blob
from .._units.clicker import Clicker
from .._units.rect import ElementRect
from .._units.scroller import ElementScroller
from .._units.selector import SelectElement
from .._units.setter import ChromiumElementSetter
from .._units.states import ElementStates, ShadowRootStates
from .._units.waiter import ElementWaiter
from ..errors import (ContextLostError, ElementLostError, JavaScriptError, CDPError, NoResourceError,
                      AlertExistsError, NoRectError, LocatorError)

__FRAME_ELEMENT__ = ('iframe', 'frame')


class ChromiumElement(DrissionElement):

    def __init__(self, owner, node_id=None, obj_id=None, backend_id=None):
        super().__init__(owner)
        self.tab = self.owner._tab
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

    def __call__(self, locator, index=1, timeout=None):
        return self.ele(locator, index=index, timeout=timeout)

    def __repr__(self):
        attrs = [f"{k}='{v}'" for k, v in self.attrs.items()]
        return f'<ChromiumElement {self.tag} {" ".join(attrs)}>'

    def __eq__(self, other):
        return self._backend_id == getattr(other, '_backend_id', None)

    @property
    def tag(self):
        if self._tag is None:
            self._tag = self.owner._run_cdp('DOM.describeNode',
                                            backendNodeId=self._backend_id)['node']['localName'].lower()
        return self._tag

    @property
    def html(self):
        return self.owner._run_cdp('DOM.getOuterHTML', backendNodeId=self._backend_id)['outerHTML']

    @property
    def inner_html(self):
        return self._run_js('return this.innerHTML;')

    @property
    def attrs(self):
        try:
            attrs = self.owner._run_cdp('DOM.getAttributes', nodeId=self._node_id)['attributes']
            return {attrs[i]: attrs[i + 1] for i in range(0, len(attrs), 2)}
        except ElementLostError:
            self._refresh_id()
            attrs = self.owner._run_cdp('DOM.getAttributes', nodeId=self._node_id)['attributes']
            return {attrs[i]: attrs[i + 1] for i in range(0, len(attrs), 2)}
        except CDPError:  # 文档根元素不能调用此方法
            return {}

    @property
    def text(self):
        return get_ele_txt(make_session_ele(self.html))

    @property
    def raw_text(self):
        return self.property('innerText')

    # -----------------d模式独有属性-------------------
    @property
    def set(self):
        if self._set is None:
            self._set = ChromiumElementSetter(self)
        return self._set

    @property
    def states(self):
        if self._states is None:
            self._states = ElementStates(self)
        return self._states

    @property
    def pseudo(self):
        if self._pseudo is None:
            self._pseudo = Pseudo(self)
        return self._pseudo

    @property
    def rect(self):
        if self._rect is None:
            self._rect = ElementRect(self)
        return self._rect

    @property
    def sr(self):
        end_time = perf_counter() + self.timeout
        while perf_counter() < end_time:
            info = self.owner._run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
            if info.get('shadowRoots', None):
                return ShadowRoot(self, backend_id=info['shadowRoots'][0]['backendNodeId'])
        return None

    @property
    def shadow_root(self):
        return self.sr

    @property
    def scroll(self):
        if self._scroll is None:
            self._scroll = ElementScroller(self)
        return self._scroll

    @property
    def click(self):
        if self._clicker is None:
            self._clicker = Clicker(self)
        return self._clicker

    @property
    def wait(self):
        if self._wait is None:
            self._wait = ElementWaiter(self)
        return self._wait

    @property
    def select(self):
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
        is_checked = self.states.is_checked
        if by_js:
            js = None
            if is_checked and uncheck:
                js = 'this.checked=false'
            elif not is_checked and not uncheck:
                js = 'this.checked=true'
            if js:
                self._run_js(js)
                self._run_js('this.dispatchEvent(new Event("change", {bubbles: true}));')

        else:
            if (is_checked and uncheck) or (not is_checked and not uncheck):
                self.click()

        return self

    def parent(self, level_or_loc=1, index=1, timeout=0):
        return super().parent(level_or_loc, index, timeout=timeout)

    def child(self, locator='', index=1, timeout=None, ele_only=True):
        return super().child(locator, index, timeout, ele_only=ele_only)

    def prev(self, locator='', index=1, timeout=None, ele_only=True):
        return super().prev(locator, index, timeout, ele_only=ele_only)

    def next(self, locator='', index=1, timeout=None, ele_only=True):
        return super().next(locator, index, timeout, ele_only=ele_only)

    def before(self, locator='', index=1, timeout=None, ele_only=True):
        return super().before(locator, index, timeout, ele_only=ele_only)

    def after(self, locator='', index=1, timeout=None, ele_only=True):
        return super().after(locator, index, timeout, ele_only=ele_only)

    def children(self, locator='', timeout=None, ele_only=True):
        return ChromiumElementsList(self.owner, super().children(locator, timeout, ele_only=ele_only))

    def prevs(self, locator='', timeout=None, ele_only=True):
        return ChromiumElementsList(self.owner, super().prevs(locator, timeout, ele_only=ele_only))

    def nexts(self, locator='', timeout=None, ele_only=True):
        return ChromiumElementsList(self.owner, super().nexts(locator, timeout, ele_only=ele_only))

    def befores(self, locator='', timeout=None, ele_only=True):
        return ChromiumElementsList(self.owner, super().befores(locator, timeout, ele_only=ele_only))

    def afters(self, locator='', timeout=None, ele_only=True):
        return ChromiumElementsList(self.owner, super().afters(locator, timeout, ele_only=ele_only))

    def over(self, timeout=None):
        if timeout is None:
            timeout = self.timeout
        bid = self.states.is_covered
        end_time = perf_counter() + timeout
        while not bid and perf_counter() < end_time:
            bid = self.states.is_covered
        return (ChromiumElement(owner=self.owner, backend_id=bid)
                if bid else NoneElement(page=self.owner, method='over()', args={'timeout': timeout}))

    def offset(self, locator=None, x=None, y=None, timeout=None):
        if locator and not (isinstance(locator, str) and not locator.startswith(
                ('x:', 'xpath:', 'x=', 'xpath=', 'c:', 'css:', 'c=', 'css='))):
            raise LocatorError(ALLOW_TYPE=_S._lang.STR_ONLY, CURR_VAL=locator)

        if x == y is None:
            x, y = self.rect.midpoint
            x = int(x)
            y = int(y)
        else:
            nx, ny = self.rect.location
            nx += x if x else 0
            ny += y if y else 0
            x = int(nx)
            y = int(ny)
        loc_data = locator_to_tuple(locator) if locator else None
        if timeout is None:
            timeout = self.timeout
        end_time = perf_counter() + timeout
        try:
            ele = ChromiumElement(owner=self.owner,
                                  backend_id=self.owner._run_cdp('DOM.getNodeForLocation', x=x, y=y,
                                                                 includeUserAgentShadowDOM=True,
                                                                 ignorePointerEventsNone=False)['backendNodeId'])
        except CDPError:
            ele = False
        if ele and (loc_data is None or _check_ele(ele, loc_data)):
            return ele

        while perf_counter() < end_time:
            try:
                ele = ChromiumElement(owner=self.owner,
                                      backend_id=self.owner._run_cdp('DOM.getNodeForLocation', x=x, y=y,
                                                                     includeUserAgentShadowDOM=True,
                                                                     ignorePointerEventsNone=False)['backendNodeId'])
            except CDPError:
                ele = False

            if ele and (loc_data is None or _check_ele(ele, loc_data)):
                return ele
            sleep(.01)

        return NoneElement(page=self.owner, method='offset()',
                           args={'locator': locator, 'offset_x': x, 'offset_y': y, 'timeout': timeout})

    def east(self, loc_or_pixel=None, index=1):
        return self._get_relative_eles(mode='east', locator=loc_or_pixel, index=index)

    def south(self, loc_or_pixel=None, index=1):
        return self._get_relative_eles(mode='south', locator=loc_or_pixel, index=index)

    def west(self, loc_or_pixel=None, index=1):
        return self._get_relative_eles(mode='west', locator=loc_or_pixel, index=index)

    def north(self, loc_or_pixel=None, index=1):
        return self._get_relative_eles(mode='north', locator=loc_or_pixel, index=index)

    def _get_relative_eles(self, mode='north', locator=None, index=1):
        if locator and not (isinstance(locator, str) and not locator.startswith(
                ('x:', 'xpath:', 'x=', 'xpath=', 'c:', 'css:', 'c=', 'css=')) or isinstance(locator, int)):
            raise LocatorError(ALLOW_TYPE=_S._lang.STR_ONLY, CURR_VAL=locator)
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
                                       backend_id=self.owner._run_cdp('DOM.getNodeForLocation',
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
                bid = self.owner._run_cdp('DOM.getNodeForLocation', **cdp_data)['backendNodeId']
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

    def attr(self, name):
        attrs = self.attrs
        if name == 'href':
            link = attrs.get('href')
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link
            else:
                return make_absolute_link(link, self.property('baseURI'))

        elif name == 'src':
            return make_absolute_link(attrs.get('src'), self.property('baseURI'))

        elif name == 'text':
            return self.text

        elif name == 'innerText':
            return self.raw_text

        elif name in ('html', 'outerHTML'):
            return self.html

        elif name == 'innerHTML':
            return self.inner_html

        else:
            return attrs.get(name, None)

    def remove_attr(self, name):
        self._run_js(f'this.removeAttribute("{name}");')
        return self

    def property(self, name):
        try:
            value = self._run_js(f'return this.{name};')
            return format_html(value) if isinstance(value, str) else value
        except:
            return None

    def run_js(self, script, *args, as_expr=False, timeout=None):
        return self._run_js(script, *args, as_expr=as_expr, timeout=timeout)

    def _run_js(self, script, *args, as_expr=False, timeout=None):
        return run_js(self, script, as_expr, self.owner.timeouts.script if timeout is None else timeout, args)

    def run_async_js(self, script, *args, as_expr=False):
        run_js(self, script, as_expr, 0, args)

    def ele(self, locator, index=1, timeout=None):
        return self._ele(locator, timeout, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        return self._ele(locator, timeout=timeout, index=None)

    def s_ele(self, locator=None, index=1, timeout=None):
        return (make_session_ele(self, locator, index=index, method='s_ele()')
                if locator is None or self.ele(locator, index=index, timeout=timeout)
                else NoneElement(self.owner, method='s_ele()', args={'locator': locator, 'index': index}))

    def s_eles(self, locator=None, timeout=None):
        return (make_session_ele(self, locator, index=None)
                if self.ele(locator, timeout=timeout) else SessionElementsList())

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        return find_in_chromium_ele(self, locator, index, timeout, relative=relative)

    def style(self, style, pseudo_ele=''):
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"'
        return self._run_js(f'return window.getComputedStyle(this{pseudo_ele}).getPropertyValue("{style}");')

    def src(self, timeout=None, base64_to_bytes=True):
        if timeout is None:
            timeout = self.timeout
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" '
                  '&& this.naturalWidth > 0 && typeof this.naturalHeight != "undefined" '
                  '&& this.naturalHeight > 0')
            end_time = perf_counter() + timeout
            while not self._run_js(js) and perf_counter() < end_time:
                sleep(.05)

        src = self.attr('href') if self.tag == 'link' else self.attr('src')
        if not src:
            raise RuntimeError(_S._lang.join(_S._lang.NO_SRC_ATTR))
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
                src = self.attr('href') if self.tag == 'link' else self.property('currentSrc') or self.property('src')
                if not src:
                    sleep(.01)
                    continue

                node = self.owner._run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
                frame = node.get('frameId', None) or self.owner._frame_id

                try:
                    result = self.owner._run_cdp('Page.getResourceContent', frameId=frame, url=src)
                    break
                except CDPError:
                    pass
                sleep(.05)

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
        if self.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" && this.naturalWidth > 0 '
                  '&& typeof this.naturalHeight != "undefined" && this.naturalHeight > 0')
            end_time = perf_counter() + self.timeout
            while not self._run_js(js) and perf_counter() < end_time:
                sleep(.05)
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
        if self.tag == 'input' and self.attr('type') == 'file':
            return self._set_file_input(vals)

        if by_js:
            if clear:
                self.clear(True)
            if isinstance(vals, (list, tuple)):
                vals = ''.join([str(i) for i in vals])
            self.set.property('value', str(vals))
            self._run_js('this.dispatchEvent(new Event("change", {bubbles: true}));')
            return self

        self.wait.clickable(wait_moved=False, timeout=.5)
        if clear and vals not in ('\n', '\ue007', '\ue006'):
            self.clear(by_js=False)
        else:
            self._input_focus()

        if isinstance(vals, str) and vals not in ('\ue003', '\ue017', '\ue010', '\ue011',
                                                  '\ue012', '\ue013', '\ue014', '\ue015',):
            input_text_or_keys(self.owner, vals)
        else:
            self.owner.actions.type(vals)

        return self

    def clear(self, by_js=False):
        if by_js or system().lower() in ('macos', 'darwin'):
            self._run_js("this.value='';")
            self._run_js('this.dispatchEvent(new Event("change", {bubbles: true}));')
            return self

        self._input_focus()
        self.input((Keys.CTRL_A, Keys.DEL), clear=False)
        return self

    def _input_focus(self):
        try:
            self.owner._run_cdp('DOM.focus', backendNodeId=self._backend_id)
        except Exception:
            self.click(by_js=None)

    def focus(self):
        try:
            self.owner._run_cdp('DOM.focus', backendNodeId=self._backend_id)
        except Exception:
            self._run_js('this.focus();')
        return self

    def hover(self, offset_x=None, offset_y=None):
        self.owner.actions.move_to(self, offset_x=offset_x, offset_y=offset_y, duration=.1)
        return self

    def drag(self, offset_x=0, offset_y=0, duration=.5):
        curr_x, curr_y = self.rect.midpoint
        offset_x += curr_x
        offset_y += curr_y
        self.drag_to((offset_x, offset_y), duration)
        return self

    def drag_to(self, ele_or_loc, duration=.5):
        if isinstance(ele_or_loc, ChromiumElement):
            ele_or_loc = ele_or_loc.rect.midpoint
        elif not isinstance(ele_or_loc, (list, tuple)):
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'ele_or_loc',
                                           ALLOW_TYPE=_S._lang.ELE_LOC_FORMAT, CURR_VAL=ele_or_loc))
        self.owner.actions.hold(self).move_to(ele_or_loc, duration=duration).release()
        return self

    def _get_obj_id(self, node_id=None, backend_id=None):
        if node_id:
            return self.owner._run_cdp('DOM.resolveNode', nodeId=node_id)['object']['objectId']
        else:
            return self.owner._run_cdp('DOM.resolveNode', backendNodeId=backend_id)['object']['objectId']

    def _get_node_id(self, obj_id=None, backend_id=None):
        if obj_id:
            return self.owner._run_cdp('DOM.requestNode', objectId=obj_id)['nodeId']
        else:
            n = self.owner._run_cdp('DOM.describeNode', backendNodeId=backend_id)['node']
            self._tag = n['localName']
            return n['nodeId']

    def _get_backend_id(self, node_id):
        n = self.owner._run_cdp('DOM.describeNode', nodeId=node_id)['node']
        self._tag = n['localName']
        return n['backendNodeId']

    def _refresh_id(self):
        self._obj_id = self._get_obj_id(backend_id=self._backend_id)
        self._node_id = self._get_node_id(obj_id=self._obj_id)

    def _get_ele_path(self, xpath=True):
        if xpath:
            txt1 = 'let tag = el.nodeName.toLowerCase();'
            txt3 = ''' && sib.nodeName.toLowerCase()===tag'''
            txt4 = '''path = '/' + tag + '[' + nth + ']' + path;'''
            txt5 = '''return path;'''

        else:
            txt1 = '''
            let i = el.getAttribute("id");
            if (i){path = '>' + el.tagName.toLowerCase() + "#" + i + path;
            el = el.parentNode;
            continue;}
            '''
            txt3 = ''
            txt4 = '''path = '>' + el.tagName.toLowerCase() + ":nth-child(" + nth + ")" + path;'''
            txt5 = '''return path.substr(1);'''

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
        return self._run_js(js)

    def _set_file_input(self, files):
        if isinstance(files, str):
            files = files.split('\n')
        files = [str(Path(i).absolute()) for i in files]
        self.owner._run_cdp('DOM.setFileInputFiles', files=files, backendNodeId=self._backend_id)
        return self


class ShadowRoot(BaseElement):

    def __init__(self, parent_ele, obj_id=None, backend_id=None):
        super().__init__(parent_ele.owner)
        self.tab = self.owner._tab
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

    def __call__(self, locator, index=1, timeout=None):
        return self.ele(locator, index=index, timeout=timeout)

    def __repr__(self):
        return f'<ShadowRoot in {self.parent_ele}>'

    def __eq__(self, other):
        return self._backend_id == getattr(other, '_backend_id', None)

    @property
    def tag(self):
        return 'shadow-root'

    @property
    def html(self):
        return f'<shadow_root>{self.inner_html}</shadow_root>'

    @property
    def inner_html(self):
        return self._run_js('return this.innerHTML;')

    @property
    def states(self):
        if self._states is None:
            self._states = ShadowRootStates(self)
        return self._states

    def run_js(self, script, *args, as_expr=False, timeout=None):
        return self._run_js(script, *args, as_expr=as_expr, timeout=timeout)

    def _run_js(self, script, *args, as_expr=False, timeout=None):
        return run_js(self, script, as_expr, self.owner.timeouts.script if timeout is None else timeout, args)

    def run_async_js(self, script, *args, as_expr=False, timeout=None):
        from threading import Thread
        Thread(target=run_js, args=(self, script, as_expr,
                                    self.owner.timeouts.script if timeout is None else timeout, args)).start()

    def parent(self, level_or_loc=1, index=1, timeout=0):
        if isinstance(level_or_loc, int):
            loc = f'xpath:./ancestor-or-self::*[{level_or_loc}]'

        elif isinstance(level_or_loc, (tuple, str)):
            loc = get_loc(level_or_loc, True)

            if loc[0] == 'css selector':
                raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)

            loc = f'xpath:./ancestor-or-self::{loc[1].lstrip(". / ")}[{index}]'

        else:
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'level_or_loc',
                                           ALLOW_TYPE=_S._lang.LOC_OR_IND, CURR_VAL=level_or_loc))

        return self.parent_ele._ele(loc, timeout=timeout, relative=True, raise_err=False, method='parent()')

    def child(self, locator='', index=1, timeout=None):
        if not locator:
            loc = '*'
        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        ele = self._ele(loc, index=index, relative=True, timeout=timeout)

        return ele if ele else NoneElement(self.owner, 'child()',
                                           {'locator': locator, 'index': index, 'timeout': timeout})

    def next(self, locator='', index=1, timeout=None):
        loc = get_loc(locator, True)
        if loc[0] == 'css selector':
            raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./{loc}'
        ele = self.parent_ele._ele(xpath, index=index, relative=True, timeout=timeout)

        return ele if ele else NoneElement(self.owner, 'next()',
                                           {'locator': locator, 'index': index, 'timeout': timeout})

    def before(self, locator='', index=1, timeout=None):
        loc = get_loc(locator, True)
        if loc[0] == 'css selector':
            raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./preceding::{loc}'
        ele = self.parent_ele._ele(xpath, index=index, relative=True, timeout=timeout)

        return ele if ele else NoneElement(self.owner, 'before()',
                                           {'locator': locator, 'index': index, 'timeout': timeout})

    def after(self, locator='', index=1, timeout=None):
        nodes = self.afters(locator=locator, timeout=timeout)
        return nodes[index - 1] if nodes else NoneElement(self.owner, 'after()',
                                                          {'locator': locator, 'index': index, 'timeout': timeout})

    def children(self, locator='', timeout=None):
        if not locator:
            loc = '*'
        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        return self._ele(loc, index=None, relative=True, timeout=timeout)

    def nexts(self, locator='', timeout=None):
        loc = get_loc(locator, True)
        if loc[0] == 'css selector':
            raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./{loc}'
        return self.parent_ele._ele(xpath, index=None, relative=True, timeout=timeout)

    def befores(self, locator='', timeout=None):
        loc = get_loc(locator, True)
        if loc[0] == 'css selector':
            raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./preceding::{loc}'
        return self.parent_ele._ele(xpath, index=None, relative=True, timeout=timeout)

    def afters(self, locator='', timeout=None):
        eles1 = self.nexts(locator)
        loc = get_loc(locator, True)[1].lstrip('./')
        xpath = f'xpath:./following::{loc}'
        return eles1 + self.parent_ele._ele(xpath, index=None, relative=True, timeout=timeout)

    def ele(self, locator, index=1, timeout=None):
        return self._ele(locator, timeout, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        return self._ele(locator, timeout=timeout, index=None)

    def s_ele(self, locator=None, index=1, timeout=None):
        return (make_session_ele(self, locator, index=index, method='s_ele()')
                if locator is None or self.ele(locator, index=index, timeout=timeout)
                else NoneElement(self.owner, method='s_ele()', args={'locator': locator, 'index': index}))

    def s_eles(self, locator, timeout=None):
        return (make_session_ele(self, locator, index=None)
                if self.ele(locator, timeout=timeout) else SessionElementsList())

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        loc = get_loc(locator, css_mode=False)
        if loc[0] == 'css selector' and str(loc[1]).startswith(':root'):
            loc = loc[0], loc[1][5:]

        def do_find():
            if loc[0] == 'css selector':
                if index == 1:
                    nod_id = self.owner._run_cdp('DOM.querySelector', nodeId=self._node_id, selector=loc[1])['nodeId']
                    if nod_id:
                        r = make_chromium_eles(self.owner, _ids=nod_id, is_obj_id=False)
                        return None if r is False else r

                else:
                    nod_ids = self.owner._run_cdp('DOM.querySelectorAll',
                                                  nodeId=self._node_id, selector=loc[1])['nodeIds']
                    r = make_chromium_eles(self.owner, _ids=nod_ids, index=index, is_obj_id=False)
                    return None if r is False else r

            else:
                eles = make_session_ele(self, loc, index=None)
                if isinstance(eles, (float, str, int)):
                    return eles
                elif not eles:
                    return None

                css = []
                for i in eles:
                    if hasattr(i, 'css_path'):
                        c = i.css_path
                        if c in ('html:nth-child(1)', 'html:nth-child(1)>body:nth-child(1)',
                                 'html:nth-child(1)>body:nth-child(1)>shadow_root:nth-child(1)'):
                            continue
                        elif c.startswith('html:nth-child(1)>body:nth-child(1)>shadow_root:nth-child(1)'):
                            c = c[61:]
                        css.append((True, c))

                    else:
                        css.append((False, i))

                if index is not None:
                    try:
                        c = css[index - 1]
                        if c[0] is False:
                            return c[1]
                        node_id = self.owner._run_cdp('DOM.querySelector', nodeId=self._node_id,
                                                      selector=c[1])['nodeId']
                        r = make_chromium_eles(self.owner, _ids=node_id, is_obj_id=False)
                        return None if r is False else r

                    except IndexError:
                        return None

                else:
                    r = []
                    for i in css:
                        if i[0] is False:
                            r.append(i[1])

                        else:
                            node_id = self.owner._run_cdp('DOM.querySelector', nodeId=self._node_id,
                                                          selector=i[1])['nodeId']
                            if node_id:
                                e = make_chromium_eles(self.owner, _ids=node_id, is_obj_id=False)
                                if e is False:
                                    return None
                                r.append(e)

                    return None if not r else r

        end_time = perf_counter() + timeout
        result = do_find()
        while result is None and perf_counter() <= end_time:
            sleep(.01)
            result = do_find()

        if result or isinstance(result, (str, float, int)):
            return result
        return NoneElement(self.owner) if index is not None else ChromiumElementsList(self.owner)

    def _get_node_id(self, obj_id):
        return self.owner._run_cdp('DOM.requestNode', objectId=obj_id)['nodeId']

    def _get_obj_id(self, back_id):
        return self.owner._run_cdp('DOM.resolveNode', backendNodeId=back_id)['object']['objectId']

    def _get_backend_id(self, node_id):
        r = self.owner._run_cdp('DOM.describeNode', nodeId=node_id)['node']
        self._tag = r['localName'].lower()
        return r['backendNodeId']


def find_in_chromium_ele(ele, locator, index=1, timeout=None, relative=True):
    # ---------------处理定位符---------------
    if isinstance(locator, (str, tuple)):
        loc = get_loc(locator)
    else:
        raise LocatorError(ALLOW_TYPE=_S._lang.LOC_FORMAT, CURR_VAL=locator)

    loc_str = loc[1]
    if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
        loc_str = f'.{loc_str}'
    elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>'):
        loc_str = f'{ele.css_path}{loc[1]}'
    loc = loc[0], loc_str

    if timeout is None:
        timeout = ele.timeout

    # ---------------执行查找-----------------
    if loc[0] == 'xpath':
        return find_by_xpath(ele, loc[1], index, timeout, relative=relative)

    else:
        return find_by_css(ele, loc[1], index, timeout)


def find_by_xpath(ele, xpath, index, timeout, relative=True):
    type_txt = '9' if index == 1 else '7'
    node_txt = 'this.contentDocument' if ele.tag in __FRAME_ELEMENT__ and not relative else 'this'
    js = make_js_for_find_ele_by_xpath(xpath, type_txt, node_txt)
    ele.owner.wait.doc_loaded()

    def do_find():
        res = ele.owner._run_cdp('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                 returnByValue=False, awaitPromise=True, userGesture=True)
        if res['result']['type'] == 'string':
            return res['result']['value']
        if 'exceptionDetails' in res:
            if 'The result is not a node set' in res['result']['description']:
                js1 = make_js_for_find_ele_by_xpath(xpath, '1', node_txt)
                res = ele.owner._run_cdp('Runtime.callFunctionOn', functionDeclaration=js1, objectId=ele._obj_id,
                                         returnByValue=False, awaitPromise=True, userGesture=True)
                return res['result']['value']
            elif 'is not a valid XPath expression' in res['result']['description']:
                raise LocatorError(_S._lang.INVALID_XPATH_, xpath)
            else:
                raise LocatorError(_S._lang.FIND_ELE_ERR, INFO=res)

        if res['result']['subtype'] == 'null' or res['result']['description'] in ('NodeList(0)', 'Array(0)'):
            return None

        if index == 1:
            r = make_chromium_eles(ele.owner, _ids=res['result']['objectId'], is_obj_id=True)
            return None if r is False else r

        else:
            res = ele.owner._run_cdp('Runtime.getProperties', objectId=res['result']['objectId'],
                                     ownProperties=True)['result'][:-1]
            if index is None:
                r = ChromiumElementsList(owner=ele.owner)
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
        sleep(.01)
        result = do_find()

    if result:
        return result
    return NoneElement(ele.owner) if index is not None else ChromiumElementsList(owner=ele.owner)


def find_by_css(ele, selector, index, timeout):
    selector = selector.replace('"', r'\"')
    find_all = '' if index == 1 else 'All'
    node_txt = 'this.contentDocument' if ele.tag in ('iframe', 'frame', 'shadow-root') else 'this'
    js = f'function(){{return {node_txt}.querySelector{find_all}("{selector}");}}'

    ele.owner.wait.doc_loaded()

    def do_find():
        res = ele.owner._run_cdp('Runtime.callFunctionOn', functionDeclaration=js, objectId=ele._obj_id,
                                 returnByValue=False, awaitPromise=True, userGesture=True)

        if 'exceptionDetails' in res:
            if 'is not a valid selector' in res['result']['description']:
                raise LocatorError(_S._lang.INVALID_CSS_, selector)
            else:
                raise LocatorError(_S._lang.FIND_ELE_ERR, INFO=res)
        if res['result']['subtype'] == 'null' or res['result']['description'] in ('NodeList(0)', 'Array(0)'):
            return None

        if index == 1:
            r = make_chromium_eles(ele.owner, _ids=res['result']['objectId'], is_obj_id=True)
            return None if r is False else r

        else:
            obj_ids = [i['value']['objectId'] for i in ele.owner._run_cdp('Runtime.getProperties',
                                                                          objectId=res['result']['objectId'],
                                                                          ownProperties=True)['result']]
            r = make_chromium_eles(ele.owner, _ids=obj_ids, index=index, is_obj_id=True)
            return None if r is False else r

    end_time = perf_counter() + timeout
    result = do_find()
    while result is None and perf_counter() < end_time:
        sleep(.01)
        result = do_find()

    if result:
        return result
    return NoneElement(ele.owner) if index is not None else ChromiumElementsList(owner=ele.owner)


def make_chromium_eles(page, _ids, index=1, is_obj_id=True, ele_only=False):
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
        nodes = ChromiumElementsList(owner=page)
        for obj_id in _ids:
            # if obj_id == 0:
            #     continue
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
            raise RuntimeError(_S._lang.join(_S._lang.JS_RUNTIME_ERR))

    if page.states.has_alert:
        raise AlertExistsError

    try:
        if Path(script).exists():
            with open(script, 'r', encoding='utf-8') as f:
                script = f.read()
    except (OSError, ValueError):
        pass

    end_time = perf_counter() + timeout
    try:
        if as_expr:
            res = page._run_cdp('Runtime.evaluate', expression=script, returnByValue=False,
                                awaitPromise=True, userGesture=True, _timeout=timeout, _ignore=AlertExistsError)

        else:
            args = args or ()
            if not is_js_func(script):
                script = f'function(){{{script}}}'
            res = page._run_cdp('Runtime.callFunctionOn', functionDeclaration=script, objectId=obj_id,
                                arguments=[convert_argument(arg) for arg in args], returnByValue=False,
                                awaitPromise=True, userGesture=True, _timeout=timeout, _ignore=AlertExistsError)
    except TimeoutError:
        raise TimeoutError(_S._lang.join(_S._lang.TIMEOUT_, _S._lang.RUN_JS, timeout))
    except ContextLostError:
        raise ContextLostError() if is_page else ElementLostError()

    if not res:  # _timeout=0或js激活alert时
        return None

    exceptionDetails = res.get('exceptionDetails')
    if exceptionDetails:
        raise JavaScriptError(JS=script, INFO=exceptionDetails)

    try:
        return parse_js_result(page, page_or_ele, res.get('result'), end_time)
    except Exception:
        from DrissionPage import __version__
        raise RuntimeError(_S._lang.join(_S._lang.JS_RESULT_ERR, INFO=res, JS=script, TIP=_S._lang.FEEDBACK))


def parse_js_result(page, ele, result, end_time):
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
            r = page._run_cdp('Runtime.getProperties', objectId=result['objectId'], ownProperties=True)['result']
            return [parse_js_result(page, ele, result=i['value'], end_time=end_time) for i in r if i['name'].isdigit()]

        elif result.get('className') == 'Blob':
            data = page._run_cdp('IO.read',
                                 handle=f"blob:{page._run_cdp('IO.resolveBlob', objectId=result['objectId'])['uuid']}")[
                'data']
            return data

        elif 'objectId' in result:
            timeout = end_time - perf_counter()
            if timeout < 0:
                return
            js = 'function(){return JSON.stringify(this);}'
            r = page._run_cdp('Runtime.callFunctionOn', functionDeclaration=js, objectId=result['objectId'],
                              returnByValue=False, awaitPromise=True, userGesture=True, _ignore=AlertExistsError,
                              _timeout=timeout)
            return loads(parse_js_result(page, ele, r['result'], end_time))

        else:
            return result.get('value', result)

    elif the_type == 'undefined':
        return None

    elif the_type == 'function':
        return result['description']

    else:
        return result['value']


def convert_argument(arg):
    if isinstance(arg, ChromiumElement):
        return {'objectId': arg._obj_id}

    elif isinstance(arg, (int, float, str, bool, dict)):
        return {'value': arg}

    from math import inf
    if arg == inf:
        return {'unserializableValue': 'Infinity'}
    elif arg == -inf:
        return {'unserializableValue': '-Infinity'}

    raise TypeError(_S._lang.join(_S._lang.UNSUPPORTED_ARG_TYPE_, arg, type(arg)))


class Pseudo(object):
    def __init__(self, ele):
        self._ele = ele

    @property
    def before(self):
        for i in ('::before', ':before', 'before'):
            r = self._ele.style('content', i)
            if r != 'content':
                return r
        return r

    @property
    def after(self):
        for i in ('::after', ':after', 'after'):
            r = self._ele.style('content', i)
            if r != 'content':
                return r
        return r


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
