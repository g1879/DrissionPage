# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from copy import copy
from math import ceil, floor
from re import search, findall, DOTALL
from threading import Thread
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
from ..errors import CDPError, ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError


# Keep OOPIF viewport expansion below common browser bitmap/GPU limits.
_MAX_SCREENSHOT_VIEWPORT_SIDE = 16384


class _FrameScreenshotContext(object):
    def __init__(self, owner, frames):
        self.owner = owner
        self.frames = frames
        self._tab_scroll = None
        self._frame_states = []
        self._has_device_metrics = False

    def save_tab_scroll(self):
        if self._tab_scroll is None:
            self._tab_scroll = self.owner.tab._run_js('return [window.pageXOffset, window.pageYOffset];')

    def save_frame(self, frame):
        style = frame.frame_ele._run_js('''return {
            attr: this.getAttribute('style'),
            width: this.style.getPropertyValue('width'),
            widthPriority: this.style.getPropertyPriority('width'),
            height: this.style.getPropertyValue('height'),
            heightPriority: this.style.getPropertyPriority('height')
        };''')
        scroll = frame._run_js('return [window.pageXOffset, window.pageYOffset];')
        self._frame_states.append({'frame': frame, 'style': style, 'scroll': scroll})

    def set_device_metrics(self, width, height):
        self._has_device_metrics = True
        self.owner.tab._run_cdp('Emulation.setDeviceMetricsOverride', width=width, height=height,
                                deviceScaleFactor=self.owner.tab._run_js('return window.devicePixelRatio;'),
                                mobile=False)

    def restore(self):
        self._clear_device_metrics()
        self.owner._wait_animation_frame(self.owner.tab)
        self._restore_frame_styles()
        self._restore_frame_scrolls()
        self._restore_tab_scroll()

    def _clear_device_metrics(self):
        if not self._has_device_metrics:
            return
        try:
            self.owner.tab._run_cdp('Emulation.clearDeviceMetricsOverride', _ignore=True)
        except (ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError):
            pass

    def _restore_frame_styles(self):
        for state in reversed(self._frame_states):
            try:
                state['frame'].frame_ele._run_js('''const original = arguments[0] || {};

                function styleWithoutSize(styleText) {
                    const tmp = document.createElement('div');
                    if (styleText !== null && typeof styleText !== 'undefined') {
                        tmp.setAttribute('style', styleText);
                    }
                    tmp.style.removeProperty('width');
                    tmp.style.removeProperty('height');
                    return tmp.getAttribute('style') || '';
                }

                function restoreStyle(name, value, priority) {
                    if (value) { this.style.setProperty(name, value, priority || ''); }
                    else { this.style.removeProperty(name); }
                }

                if (styleWithoutSize(this.getAttribute('style')) === styleWithoutSize(original.attr)) {
                    if (original.attr === null || typeof original.attr === 'undefined') {
                        this.removeAttribute('style');
                    } else {
                        this.setAttribute('style', original.attr);
                    }
                } else {
                    restoreStyle.call(this, 'width', original.width, original.widthPriority);
                    restoreStyle.call(this, 'height', original.height, original.heightPriority);
                }''', state['style'])
            except (ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError):
                pass

    def _restore_frame_scrolls(self):
        for state in reversed(self._frame_states):
            try:
                scroll = state['scroll']
                state['frame']._run_js('window.scrollTo(arguments[0], arguments[1]);', scroll[0], scroll[1])
            except (ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError):
                pass

    def _restore_tab_scroll(self):
        if self._tab_scroll is None:
            return
        try:
            self.owner.tab._run_js('window.scrollTo(arguments[0], arguments[1]);',
                                   self._tab_scroll[0], self._tab_scroll[1])
            self.owner._wait_animation_frame(self.owner.tab)
        except (ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError):
            pass


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
                super().__init__(owner.browser, owner._target_id, owner._context_id)
            else:
                self._is_diff_domain = True
                delattr(self, '_frame_id')
                super().__init__(owner.browser, node['frameId'], owner._context_id)
                obj_id = super()._run_js('document;', as_expr=True)['objectId']
                self.doc_ele = ChromiumElement(self, obj_id=obj_id)
            self._frame_id = node['frameId']

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

    def _driver_init(self):
        try:
            super()._driver_init()
        except:
            if not self.browser._ws_only:
                self.browser._driver.get(f'http://{self._browser.address}/json')
            super()._driver_init()
        # self._set_callback('Inspector.detached', self._onInspectorDetached, immediate=True)
        self._set_callback('Page.frameDetached', self._onFrameDetached, immediate=True)

    def _do_reload(self):
        self._messenger_running = True
        self._is_loading = True
        self._reloading = True
        self._doc_got = False
        self._browser._detach(session_id=self._session_id)
        self._browser._tabs.remove_session(self._session_id)
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
            if self._listener:
                self._listener._to_target(self._target_page.tab_id, self)
            super().__init__(self._browser, self._target_page.tab_id, self._context_id)
            self._frame_id = node['frameId']
            self._browser._tabs.add_frame(self._frame_id, self._target_page.tab_id)

        else:
            self._is_diff_domain = True
            if self._listener:
                self._listener._to_target(node['frameId'], self)
            end_time = perf_counter() + self.timeouts.page_load
            super().__init__(self._browser, node['frameId'], self._context_id)
            self._browser._tabs.add_frame(self._frame_id, self._target_id)
            timeout = end_time - perf_counter()
            if timeout <= 0:
                timeout = .5
            self._wait_loaded(timeout)

        self._type = 'ChromiumFrame'
        self._is_loading = False
        self._reloading = False

    def _reload(self):
        Thread(target=self._do_reload).start()

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

            self._root_oid = self.doc_ele._obj_id

            r = self._run_cdp('Page.getFrameTree', _ignore=PageDisconnectedError)
            for i in findall(r"'id': '(.*?)'", str(r)):
                self.browser._tabs.add_frame(i, self.tab_id)
                return True

        except:
            return False

        finally:
            if not self._reloading:  # 阻止reload时标识
                self._is_loading = False
            self._is_reading = False

    def _onFrameNavigated(self, **kwargs):
        if kwargs['frame']['id'] == self._target_id and not self._is_diff_domain:
            self._stop_messenger()
            return
        super()._onFrameNavigated(**kwargs)

    # def _onInspectorDetached(self, **kwargs):
    #     # 异域转同域或退出
    #     return
    #     self._reload()

    def _onFrameDetached(self, **kwargs):
        if kwargs['frameId'] == self._frame_id:
            if kwargs['reason'] == 'remove':  # iframe被删除
                self.browser._tabs.remove_frame(kwargs['frameId'])
                ChromiumFrame._Frames.pop(kwargs['frameId'], None)
                self._stop_messenger()
            elif kwargs['reason'] == 'swap':  # 同域变异域
                self._reload()

    def _stop_messenger(self):
        super()._stop_messenger()
        if self._is_diff_domain and self._frame_id in str(self.tab._run_cdp('Page.getFrameTree', _ignore=True)):
            self._do_reload()

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
    def css_selector(self):
        return self.frame_ele.css_selector

    @property
    def css_path(self):  # 即将废弃
        return self.frame_ele.css_selector

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

    def _get_screenshot(self, path=None, name=None, as_bytes=None, as_base64=None,
                        full_page=False, left_top=None, right_bottom=None, ele=None):
        if ele is None:
            if not self._is_diff_domain:
                return super().get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                              full_page=full_page, left_top=left_top, right_bottom=right_bottom)
            return self.frame_ele.get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64)

        frames = self._get_screenshot_frame_chain()
        context = _FrameScreenshotContext(self, frames)
        try:
            self._prepare_frame_element_screenshot(ele, context)
            left_top, right_bottom = self._get_ele_screenshot_rect(ele)
            self._ensure_top_viewport_for_screenshot(left_top, right_bottom, context)
            return self.tab.get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                           left_top=left_top, right_bottom=right_bottom)
        finally:
            context.restore()

    def _prepare_frame_element_screenshot(self, ele, context):
        context.save_tab_scroll()

        target = ele
        for frame in context.frames:
            context.save_frame(frame)
            box = self._get_target_document_box(target)
            self._resize_frame_for_screenshot(frame, box)
            self._scroll_frame_to_box(frame, box)
            target = frame.frame_ele

        for frame in reversed(context.frames):
            frame.frame_ele.scroll.to_see(center=False)
        self._wait_screenshot_chain_stable(ele, context.frames)

    def _get_screenshot_frame_chain(self):
        frames = []
        frame = self
        seen = set()
        while getattr(frame, '_type', None) == 'ChromiumFrame':
            if id(frame) in seen:
                break
            seen.add(id(frame))
            frames.append(frame)
            parent_frame = getattr(frame, '_parent_frame', None) or self._get_parent_frame_from_tree(frame)
            if parent_frame:
                frame._parent_frame = parent_frame
            frame = parent_frame or frame._target_page
        return frames

    def _get_parent_frame_from_tree(self, frame):
        frame_id = getattr(frame, '_frame_id', None)
        if not frame_id:
            return None

        parent_id = self._get_frame_parent_map().get(frame_id)
        if parent_id == self.tab.tab_id:
            return None

        if parent_id:
            parent_frame = self._get_cached_frame(parent_id)
            if parent_frame:
                return parent_frame

        self.tab.get_frames(timeout=0)
        if parent_id:
            parent_frame = self._get_cached_frame(parent_id)
            if parent_frame:
                return parent_frame
        return self._get_parent_frame_by_element_context(frame)

    def _get_frame_parent_map(self):
        frame_tree = self.tab._run_cdp('Page.getFrameTree')['frameTree']
        parent_map = {}

        def collect(node):
            frame_info = node.get('frame', {})
            frame_id = frame_info.get('id')
            parent_id = frame_info.get('parentId')
            if frame_id and parent_id:
                parent_map[frame_id] = parent_id
            for child in node.get('childFrames', ()) or ():
                collect(child)

        collect(frame_tree)
        return parent_map

    @staticmethod
    def _get_cached_frame(frame_id):
        frame = ChromiumFrame._Frames.get(frame_id)
        return frame if getattr(frame, '_type', None) == 'ChromiumFrame' else None

    def _get_parent_frame_by_element_context(self, frame):
        for candidate in list(ChromiumFrame._Frames.values()):
            if candidate is frame or getattr(candidate, '_type', None) != 'ChromiumFrame':
                continue
            if candidate.tab is not self.tab:
                continue
            try:
                if candidate._run_js('return Array.from(document.querySelectorAll("iframe,frame"))'
                                     '.includes(arguments[0]);', frame.frame_ele):
                    return candidate
            except (CDPError, ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError):
                pass
        return None

    @staticmethod
    def _get_target_document_box(ele):
        return ele._run_js('''const r = this.getBoundingClientRect();
        return {
            left: r.left + window.pageXOffset,
            top: r.top + window.pageYOffset,
            width: r.width,
            height: r.height
        };''')

    def _resize_frame_for_screenshot(self, frame, box):
        width = max(1, ceil(box['width']))
        height = max(1, ceil(box['height']))
        frame.frame_ele._run_js('''const r = this.getBoundingClientRect();
        const cs = getComputedStyle(this);
        const borderWidth = (parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.borderRightWidth) || 0) + 1;
        const borderHeight = (parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.borderBottomWidth) || 0) + 1;
        this.style.setProperty('width', Math.ceil(Math.max(r.width, arguments[0] + borderWidth)) + 'px', 'important');
        const height = Math.ceil(Math.max(r.height, arguments[1] + borderHeight)) + 'px';
        this.style.setProperty('height', height, 'important');''',
                                  width, height)
        self._wait_animation_frame(frame.frame_ele)
        self._wait_animation_frame(frame)

    @staticmethod
    def _scroll_frame_to_box(frame, box):
        frame._run_js('window.scrollTo(arguments[0], arguments[1]);', box['left'], box['top'])

    def _ensure_top_viewport_for_screenshot(self, left_top, right_bottom, context):
        if not any(frame._is_diff_domain for frame in context.frames):
            return

        viewport_width, viewport_height = self.tab.rect.viewport_size_with_scrollbar
        scroll_x, scroll_y = self.tab.rect.scroll_position
        width = min(_MAX_SCREENSHOT_VIEWPORT_SIDE, max(viewport_width, ceil(right_bottom[0] - scroll_x)))
        height = min(_MAX_SCREENSHOT_VIEWPORT_SIDE, max(viewport_height, ceil(right_bottom[1] - scroll_y)))
        if width <= viewport_width and height <= viewport_height:
            return

        context.set_device_metrics(width, height)
        self._wait_animation_frame(self.tab)

    @staticmethod
    def _wait_animation_frame(item):
        try:
            item._run_js('''return new Promise(resolve => {
                if (typeof requestAnimationFrame === 'function') {
                    requestAnimationFrame(() => requestAnimationFrame(resolve));
                } else {
                    setTimeout(resolve, 0);
                }
            });''', timeout=.5)
        except (TimeoutError, ContextLostError, ElementLostError, PageDisconnectedError, JavaScriptError):
            pass

    def _wait_screenshot_chain_stable(self, ele, frames):
        items = list(frames)
        items.append(self.tab)

        previous = None
        end_time = perf_counter() + .5
        while perf_counter() < end_time:
            for item in items:
                self._wait_animation_frame(item)
            current = self._get_ele_screenshot_rect(ele)
            if current == previous:
                return
            previous = current
            sleep(.02)

    def _get_ele_screenshot_rect(self, ele):
        points = self._get_ele_viewport_points(ele)
        frame = ele.owner
        while getattr(frame, '_type', None) == 'ChromiumFrame' and frame._is_diff_domain:
            points = self._map_frame_points_to_parent(frame, points)
            frame = frame._target_page

        r = self.tab._run_cdp('Page.getLayoutMetrics')['cssVisualViewport']
        sx = r['pageX']
        sy = r['pageY']
        xs = [i[0] + sx for i in points]
        ys = [i[1] + sy for i in points]
        return (floor(min(xs) + 1e-6), floor(min(ys) + 1e-6)), (ceil(max(xs) - 1e-6), ceil(max(ys) - 1e-6))

    @staticmethod
    def _get_ele_viewport_points(ele):
        box = ele.owner._run_cdp('DOM.getBoxModel', backendNodeId=ele._backend_id)['model']['border']
        return [(box[i], box[i + 1]) for i in range(0, 8, 2)]

    @staticmethod
    def _get_frame_viewport_size(frame):
        txt = frame.doc_ele._run_js('return window.innerWidth.toString() + " " + window.innerHeight.toString();')
        width, height = txt.split(' ')
        return float(width), float(height)

    def _map_frame_points_to_parent(self, frame, points):
        content = frame.frame_ele.owner._run_cdp('DOM.getBoxModel',
                                                backendNodeId=frame.frame_ele._backend_id)['model']['content']
        content_points = [(content[i], content[i + 1]) for i in range(0, 8, 2)]
        width, height = self._get_frame_viewport_size(frame)
        if width == 0 or height == 0:
            return content_points
        return [self._map_point_to_quad(x / width, y / height, content_points) for x, y in points]

    @staticmethod
    def _map_point_to_quad(x_rate, y_rate, quad):
        top_left, top_right, bottom_right, bottom_left = quad
        x = (top_left[0] * (1 - x_rate) * (1 - y_rate)
             + top_right[0] * x_rate * (1 - y_rate)
             + bottom_right[0] * x_rate * y_rate
             + bottom_left[0] * (1 - x_rate) * y_rate)
        y = (top_left[1] * (1 - x_rate) * (1 - y_rate)
             + top_right[1] * x_rate * (1 - y_rate)
             + bottom_right[1] * x_rate * y_rate
             + bottom_left[1] * (1 - x_rate) * y_rate)
        return x, y

    def _mark_frame_elements(self, result):
        if getattr(result, '_type', None) == 'ChromiumElement':
            result._frame_owner = self
        elif getattr(result, '_type', None) == 'ChromiumFrame':
            result._parent_frame = self
        elif isinstance(result, list):
            for i in result:
                self._mark_frame_elements(i)
        return result

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        if isinstance(locator, ChromiumElement):
            return self._mark_frame_elements(locator)
        timeout = timeout if timeout is not None else self.timeouts.base
        now = perf_counter()
        end_time = now + timeout
        while now <= end_time:
            try:
                return self._mark_frame_elements(
                    self.doc_ele._ele(locator, index=index, timeout=end_time - now, raise_err=raise_err))
            except ContextLostError:
                now = perf_counter()
        return self._mark_frame_elements(self.doc_ele._ele(locator, index=index, timeout=0, raise_err=raise_err))

    def _is_inner_frame(self):
        end_time = perf_counter() + 3
        while perf_counter() < end_time:
            try:
                return self._frame_id in str(self._target_page._run_cdp('Page.getFrameTree')['frameTree'])
            except:
                pass
        return False
