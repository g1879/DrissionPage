# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from time import perf_counter, sleep

from .waiter import wait_mission
from .._functions.settings import Settings as _S
from .._functions.web import offset_scroll
from .._units.downloader import TabDownloadSettings
from ..errors import CanNotClickError, CDPError, NoRectError, AlertExistsError


class Clicker(object):
    def __init__(self, ele):
        self._ele = ele

    def __call__(self, by_js=False, timeout=1.5, wait_stop=True):
        return self.left(by_js, timeout, wait_stop)

    def left(self, by_js=False, timeout=1.5, wait_stop=True):
        if self._ele.tag == 'option':
            if not self._ele.states.is_selected:
                self._ele.parent('t:select').select.by_option(self._ele)
            else:
                select = self._ele.parent('t:select')
                if select.select.is_multi:
                    self._ele.parent('t:select').select.cancel_by_option(self._ele)
            return self._ele

        if not by_js:  # 模拟点击
            can_click = False
            if timeout is None:
                timeout = self._ele.timeout
            rect = None
            if timeout == 0:
                try:
                    self._ele.scroll.to_see()
                    if self._ele.states.is_enabled and self._ele.states.is_displayed:
                        rect = self._ele.rect.viewport_corners
                        can_click = True
                except NoRectError:
                    if by_js is False:
                        raise

            else:
                rect = self._ele.states.has_rect
                end_time = perf_counter() + timeout
                while not rect and perf_counter() < end_time:
                    rect = self._ele.states.has_rect
                    sleep(.001)

                if wait_stop and rect:
                    self._ele.wait.stop_moving(timeout=end_time - perf_counter())
                if rect:
                    self._ele.scroll.to_see()
                    rect = self._ele.rect.corners
                    while perf_counter() < end_time:
                        if self._ele.states.is_enabled and self._ele.states.is_displayed:
                            can_click = True
                            break
                        sleep(.001)

                elif by_js is False:
                    raise NoRectError

            if can_click and not self._ele.states.is_in_viewport:
                by_js = True

            elif can_click and (by_js is False or not self._ele.states.is_covered):
                x = rect[1][0] - (rect[1][0] - rect[0][0]) / 2
                y = rect[0][0] + 3
                try:
                    r = self._ele.owner._run_cdp('DOM.getNodeForLocation', x=int(x), y=int(y),
                                                 includeUserAgentShadowDOM=True, ignorePointerEventsNone=True)
                    if r['backendNodeId'] != self._ele._backend_id:
                        vx, vy = self._ele.rect.viewport_midpoint
                    else:
                        vx, vy = self._ele.rect.viewport_click_point

                except CDPError:
                    vx, vy = self._ele.rect.viewport_midpoint

                self._click(vx, vy)
                return self._ele

        if by_js is not False:
            self._ele._run_js('this.click();')
            return self._ele
        if _S.raise_when_click_failed:
            raise CanNotClickError
        return False

    def right(self):
        self._ele.owner.scroll.to_see(self._ele)
        return self._click(*self._ele.rect.viewport_click_point, button='right')

    def middle(self, get_tab=True):
        self._ele.owner.scroll.to_see(self._ele)
        curr_tid = self._ele.tab.browser.tab_ids[0]
        self._click(*self._ele.rect.viewport_click_point, button='middle')
        if get_tab:
            tid = self._ele.tab.browser.wait.new_tab(curr_tab=curr_tid)
            if not tid:
                raise RuntimeError(_S._lang.join(_S._lang.NO_NEW_TAB))
            return self._ele.tab.browser._get_tab(tid, mix=self._ele.tab._type == 'MixTab')

    def at(self, offset_x=None, offset_y=None, button='left', count=1):
        self._ele.owner.scroll.to_see(self._ele)
        if offset_x is None and offset_y is None:
            w, h = self._ele.rect.size
            offset_x = w // 2
            offset_y = h // 2
        return self._click(*offset_scroll(self._ele, offset_x, offset_y), button=button, count=count)

    def multi(self, times=2):
        return self.at(count=times)

    def to_download(self, save_path=None, rename=None, suffix=None, new_tab=None, by_js=False, timeout=None):
        if not self._ele.tab._browser._dl_mgr._running:
            self._ele.tab._browser.set.download_path('.')

        when_file_exists = None
        tmp_path = None
        if self._ele.tab._type.endswith('Page'):
            obj = browser = self._ele.owner._browser
            tid = 'browser'

        elif new_tab:
            obj = browser = self._ele.owner._browser
            tid = 'browser'
            t_settings = TabDownloadSettings(self._ele.owner.tab_id)
            b_settings = TabDownloadSettings('browser')

            when_file_exists = b_settings.when_file_exists
            b_settings.when_file_exists = t_settings.when_file_exists
            b_settings.rename = t_settings.rename
            b_settings.suffix = t_settings.suffix
            t_settings.rename = None
            t_settings.suffix = None
            if not save_path and b_settings.path != t_settings.path:
                tmp_path = b_settings.path
                b_settings.path = t_settings.path

        else:
            obj = self._ele.owner._tab
            browser = obj.browser
            browser._dl_mgr._waiting_tab.add(self._ele.owner.tab_id)
            tid = obj.tab_id

        if save_path:
            tmp_path = obj.download_path
            TabDownloadSettings(tid).path = str(Path(save_path).absolute())
        if rename or suffix:
            obj.set.download_file_name(rename, suffix)
        if timeout is None:
            timeout = obj.timeout

        browser._dl_mgr.set_flag(tid, True)
        self.left(by_js=by_js)
        m = wait_mission(browser, tid, timeout)

        if tmp_path:
            TabDownloadSettings(tid).path = tmp_path
        if when_file_exists:
            browser.set.when_download_file_exists(when_file_exists)
        if m and new_tab:
            self._ele.owner.browser._dl_mgr._tab_missions.setdefault(self._ele.owner.tab_id, set()).add(m)
            m.from_tab = self._ele.owner.tab_id
        browser._dl_mgr._waiting_tab.discard(self._ele.owner.tab_id)
        return m

    def to_upload(self, file_paths, by_js=False):
        self._ele.owner.set.upload_files(file_paths)
        self.left(by_js=by_js)
        self._ele.owner.wait.upload_paths_inputted()

    def for_new_tab(self, by_js=False, timeout=3):
        curr_tid = self._ele.tab.browser._newest_tab_id
        self.left(by_js=by_js)
        tid = self._ele.tab.browser.wait.new_tab(timeout=timeout, curr_tab=curr_tid)
        if not tid:
            raise RuntimeError(_S._lang.join(_S._lang.NO_NEW_TAB))
        return self._ele.tab.browser._get_tab(tid, mix=self._ele.tab._type == 'MixTab')

    def for_url_change(self, text=None, exclude=False, by_js=False, timeout=None):
        if text is None:
            exclude = True
            text = self._ele.tab.url
        self.left(by_js=by_js)
        return True if self._ele.tab.wait.url_change(text=text, exclude=exclude, timeout=timeout) else False

    def for_title_change(self, text=None, exclude=False, by_js=False, timeout=None):
        if text is None:
            exclude = True
            text = self._ele.tab.title
        self.left(by_js=by_js)
        return True if self._ele.tab.wait.title_change(text=text, exclude=exclude, timeout=timeout) else False

    def _click(self, view_x, view_y, button='left', count=1):
        self._ele.owner._run_cdp('Input.dispatchMouseEvent', type='mousePressed', x=view_x,
                                 y=view_y, button=button, clickCount=count, _ignore=AlertExistsError)
        self._ele.owner._run_cdp('Input.dispatchMouseEvent', type='mouseReleased', x=view_x,
                                 y=view_y, button=button, _ignore=AlertExistsError)
        return self._ele
