# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from copy import copy
from re import search, findall, DOTALL
from time import sleep, perf_counter

from .._elements.chromium_element import ChromiumElement
from .._functions.settings import Settings as _S
from .._pages.chromium_base import ChromiumBase
from .._units.listener import FrameListener
from .._units.rect import FrameRect
from .._units.scroller import FrameScroller
from .._units.setter import ChromiumFrameSetter
from .._units.states import FrameStates
from .._units.waiter import FrameWaiter
from ..errors import ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError


class ChromiumFrame(ChromiumBase):
    _Frames = {}

    def __new__(cls, owner, ele, info=None):
        fid = info['node']['frameId'] if info else owner._run_cdp('DOM.describeNode',
                                                                  backendNodeId=ele._backend_id)['node']['frameId']
        if _S.singleton_tab_obj and fid in cls._Frames:
            r = cls._Frames[fid]
            while not hasattr(r, '_type') or r._type != 'ChromiumFrame':
                sleep(.01)
            return r
        r = object.__new__(cls)
        cls._Frames[fid] = r
        return r

    def __init__(self, owner, ele, info=None):
        if _S.singleton_tab_obj and hasattr(self, '_created'):
            return
        self._created = True

        self._tab = owner._tab
        self._target_page = owner
        self._backend_id = ele._backend_id
        self._frame_ele = ele
        self._reloading = False

        try:
            node = info['node'] if info else owner._run_cdp('DOM.describeNode', backendNodeId=ele._backend_id)['node']
            self._frame_id = node['frameId']
            if self._is_inner_frame():
                self._is_diff_domain = False
                self.doc_ele = ChromiumElement(self._target_page, backend_id=node['contentDocument']['backendNodeId'])
                super().__init__(owner.browser, owner.driver.id)
            else:
                self._is_diff_domain = True
                delattr(self, '_frame_id')
                super().__init__(owner.browser, node['frameId'])
                obj_id = super()._run_js('document;', as_expr=True)['objectId']
                self.doc_ele = ChromiumElement(self, obj_id=obj_id)

        except Exception as e:
            ChromiumFrame._Frames.pop(self._frame_id, None)
            raise e

        self._type = 'ChromiumFrame'

    def __call__(self, locator, index=1, timeout=None):
        return self.ele(locator, index=index, timeout=timeout)

    def __repr__(self):
        attrs = [f"{k}='{v}'" for k, v in self._frame_ele.attrs.items()]
        return f'<ChromiumFrame {self.frame_ele.tag} {" ".join(attrs)}>'

    def __eq__(self, other):
        return self._frame_id == getattr(other, '_frame_id', None)

    def _d_set_runtime_settings(self):
        if not hasattr(self, '_timeouts'):
            self._timeouts = copy(self._target_page.timeouts)
            self.retry_times = self._target_page.retry_times
            self.retry_interval = self._target_page.retry_interval
            self._download_path = self._target_page.download_path
            self._auto_handle_alert = self._target_page._auto_handle_alert
        self._load_mode = self._target_page._load_mode if not self._is_diff_domain else 'normal'

    def _driver_init(self, target_id, is_init=True):
        try:
            super()._driver_init(target_id)
        except:
            self.browser._driver.get(f'http://{self._browser.address}/json')
            super()._driver_init(target_id)
        self._driver.set_callback('Inspector.detached', self._onInspectorDetached, immediate=True)
        self._driver.set_callback('Page.frameDetached', None)
        self._driver.set_callback('Page.frameDetached', self._onFrameDetached, immediate=True)

    def _reload(self):
        self._is_loading = True
        self._reloading = True
        self._doc_got = False

        self._driver.stop()
        try:
            self._frame_ele = ChromiumElement(self._target_page, backend_id=self._backend_id)
            end_time = perf_counter() + 2
            while perf_counter() < end_time:
                node = self._target_page._run_cdp('DOM.describeNode', backendNodeId=self._frame_ele._backend_id)['node']
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
                self._listener._to_target(self._target_page.tab_id, self._browser.address, self)
            super().__init__(self._browser, self._target_page.tab_id)

        else:
            self._is_diff_domain = True
            if self._listener:
                self._listener._to_target(node['frameId'], self._browser.address, self)
            end_time = perf_counter() + self.timeouts.page_load
            super().__init__(self._browser, node['frameId'])
            timeout = end_time - perf_counter()
            if timeout <= 0:
                timeout = .5
            self._wait_loaded(timeout)

        self._is_loading = False
        self._reloading = False

    def _get_document(self, timeout=10):
        if self._is_reading:
            return

        self._is_reading = True
        try:
            if self._is_diff_domain is False:
                node = self._target_page._run_cdp('DOM.describeNode', backendNodeId=self._backend_id)['node']
                self.doc_ele = ChromiumElement(self._target_page, backend_id=node['contentDocument']['backendNodeId'])

            else:
                timeout = max(timeout, 2)
                b_id = self._run_cdp('DOM.getDocument', _timeout=timeout)['root']['backendNodeId']
                self.doc_ele = ChromiumElement(self, backend_id=b_id)

            self._root_id = self.doc_ele._obj_id

            r = self._run_cdp('Page.getFrameTree', _ignore=PageDisconnectedError)
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
        # 异域转同域或退出
        self._reload()

    def _onFrameDetached(self, **kwargs):
        # 同域变异域
        self.browser._frames.pop(kwargs['frameId'], None)
        ChromiumFrame._Frames.pop(kwargs['frameId'], None)
        if kwargs['frameId'] == self._frame_id:
            self._reload()

    # ----------挂件----------
    @property
    def scroll(self):
        self.wait.doc_loaded()
        if self._scroll is None:
            self._scroll = FrameScroller(self)
        return self._scroll

    @property
    def set(self):
        if self._set is None:
            self._set = ChromiumFrameSetter(self)
        return self._set

    @property
    def states(self):
        if self._states is None:
            self._states = FrameStates(self)
        return self._states

    @property
    def wait(self):
        if self._wait is None:
            self._wait = FrameWaiter(self)
        return self._wait

    @property
    def rect(self):
        if self._rect is None:
            self._rect = FrameRect(self)
        return self._rect

    @property
    def listen(self):
        if self._listener is None:
            self._listener = FrameListener(self)
        return self._listener

    # ----------挂件结束----------

    @property
    def _obj_id(self):
        return self.frame_ele._obj_id

    @property
    def _node_id(self):
        return self.frame_ele._node_id

    @property
    def owner(self):
        return self.frame_ele.owner

    @property
    def frame_ele(self):
        return self._frame_ele

    @property
    def tag(self):
        return self.frame_ele.tag

    @property
    def url(self):
        try:
            return self.doc_ele._run_js('return this.location.href;')
        except JavaScriptError:
            return None

    @property
    def html(self):
        tag = self.tag
        out_html = self._target_page._run_cdp('DOM.getOuterHTML', backendNodeId=self.frame_ele._backend_id)['outerHTML']
        sign = search(rf'<{tag}.*?>', out_html, DOTALL).group(0)
        return f'{sign}{self.inner_html}</{tag}>'

    @property
    def inner_html(self):
        return self.doc_ele._run_js('return this.documentElement.outerHTML;')

    @property
    def link(self):
        return self.frame_ele.link

    @property
    def title(self):
        r = self._ele('t:title', raise_err=False)
        return r.text if r else None

    @property
    def attrs(self):
        return self.frame_ele.attrs

    @property
    def active_ele(self):
        return self.doc_ele._run_js('return this.activeElement;')

    @property
    def xpath(self):
        return self.frame_ele.xpath

    @property
    def css_path(self):
        return self.frame_ele.css_path

    @property
    def tab(self):
        return self._tab

    @property
    def tab_id(self):
        return self.tab.tab_id

    @property
    def download_path(self):
        return self._download_path

    @property
    def sr(self):
        return self.frame_ele.sr

    @property
    def shadow_root(self):
        return self.frame_ele.sr

    @property
    def child_count(self):
        return int(self._ele('xpath:count(./*)'))

    @property
    def _js_ready_state(self):
        if self._is_diff_domain:
            return super()._js_ready_state

        else:
            try:
                return self.doc_ele._run_js('return this.readyState;')
            except ContextLostError:
                try:
                    node = self._run_cdp('DOM.describeNode', backendNodeId=self.frame_ele._backend_id)['node']
                    doc = ChromiumElement(self._target_page, backend_id=node['contentDocument']['backendNodeId'])
                    return doc._run_js('return this.readyState;')
                except:
                    return None

    def refresh(self):
        self.doc_ele._run_js('this.location.reload();')

    def property(self, name):
        return self.frame_ele.property(name)

    def attr(self, name):
        return self.frame_ele.attr(name)

    def remove_attr(self, name):
        self.frame_ele.remove_attr(name)

    def style(self, style, pseudo_ele=''):
        return self.frame_ele.style(style=style, pseudo_ele=pseudo_ele)

    def run_js(self, script, *args, as_expr=False, timeout=None):
        return self._run_js(script, *args, as_expr=as_expr, timeout=timeout)

    def _run_js(self, script, *args, as_expr=False, timeout=None):
        if script.startswith('this.scrollIntoView'):
            return self.frame_ele._run_js(script, *args, as_expr=as_expr, timeout=timeout)
        else:
            return self.doc_ele._run_js(script, *args, as_expr=as_expr, timeout=timeout)

    def parent(self, level_or_loc=1, index=1, timeout=0):
        return self.frame_ele.parent(level_or_loc, index, timeout=timeout)

    def prev(self, locator='', index=1, timeout=0, ele_only=True):
        return self.frame_ele.prev(locator, index, timeout, ele_only=ele_only)

    def next(self, locator='', index=1, timeout=0, ele_only=True):
        return self.frame_ele.next(locator, index, timeout, ele_only=ele_only)

    def before(self, locator='', index=1, timeout=None, ele_only=True):
        return self.frame_ele.before(locator, index, timeout, ele_only=ele_only)

    def after(self, locator='', index=1, timeout=None, ele_only=True):
        return self.frame_ele.after(locator, index, timeout, ele_only=ele_only)

    def prevs(self, locator='', timeout=0, ele_only=True):
        return self.frame_ele.prevs(locator, timeout, ele_only=ele_only)

    def nexts(self, locator='', timeout=0, ele_only=True):
        return self.frame_ele.nexts(locator, timeout, ele_only=ele_only)

    def befores(self, locator='', timeout=None, ele_only=True):
        return self.frame_ele.befores(locator, timeout, ele_only=ele_only)

    def afters(self, locator='', timeout=None, ele_only=True):
        return self.frame_ele.afters(locator, timeout, ele_only=ele_only)

    def get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None):
        return self.frame_ele.get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64)

    def _get_screenshot(self, path=None, name=None, as_bytes: [bool, str] = None, as_base64: [bool, str] = None,
                        full_page=False, left_top=None, right_bottom=None, ele=None):
        if not self._is_diff_domain:
            return super().get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                          full_page=full_page, left_top=left_top, right_bottom=right_bottom)

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
        new_ele = first_child._run_js(js, body)
        new_ele.scroll.to_see(center=True)
        top = int(self.frame_ele.style('border-top').split('px')[0])
        left = int(self.frame_ele.style('border-left').split('px')[0])

        r = self.tab._run_cdp('Page.getLayoutMetrics')['visualViewport']
        sx = r['pageX']
        sy = r['pageY']
        r = self.tab.get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                    left_top=(cx + left + sx, cy + top + sy),
                                    right_bottom=(cx + w + left + sx, cy + h + top + sy))
        self.tab.remove_ele(new_ele)
        return r

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        if isinstance(locator, ChromiumElement):
            return locator
        self.wait.doc_loaded()
        return self.doc_ele._ele(locator, index=index, timeout=timeout,
                                 raise_err=raise_err) if index is not None else self.doc_ele.eles(locator, timeout)

    def _is_inner_frame(self):
        return self._frame_id in str(self._target_page._run_cdp('Page.getFrameTree')['frameTree'])
