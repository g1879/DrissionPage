# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from time import sleep, perf_counter

from .._functions.locator import is_selenium_loc
from .._functions.settings import Settings as _S
from .._functions.tools import wait_until
from ..errors import WaitTimeoutError, NoRectError


class OriginWaiter(object):
    def __init__(self, owner):
        self._owner = owner

    def __call__(self, second, scope=None):
        if scope is None:
            sleep(second)
        else:
            from random import uniform
            sleep(uniform(second, scope))
        return self._owner


class BrowserContextWaiter(OriginWaiter):
    def new_tab(self, timeout=None, curr_tab=None, raise_err=None):
        return self._new_tab(context_id=self._owner._context_id, timeout=timeout, curr_tab=curr_tab,
                             raise_err=raise_err)

    def _new_tab(self, context_id, timeout=None, curr_tab=None, raise_err=None):
        def do():
            if curr_tab != self._owner._browser._tabs.get_newest_tab(context_id):
                return self._owner._browser._tabs.get_newest_tab(context_id)
            return None

        if not curr_tab:
            curr_tab = self._owner._browser._tabs.get_newest_tab(context_id)
        elif hasattr(curr_tab, '_type'):
            curr_tab = curr_tab.tab_id
        if timeout is None:
            timeout = self._owner._browser.timeout

        err_txt = (_S._lang.join(_S._lang.WAITING_FAILED_, _S._lang.NEW_TAB, timeout)
                   if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None) else None)
        r = wait_until(do, timeout=timeout, err_txt=err_txt)
        return r if r is not None else False


class BrowserWaiter(BrowserContextWaiter):
    def download_begin(self, timeout=None, cancel_it=False):
        if not self._owner._dl_mgr._running:
            raise RuntimeError(_S._lang.joinn(_S._lang.NEED_DOWNLOAD_PATH, TIP=_S._lang.SET_DOWNLOAD_PATH))
        self._owner._dl_mgr.set_flag('browser', False if cancel_it else True)
        if timeout is None:
            timeout = self._owner.timeout
        return wait_mission(self._owner, 'browser', timeout)

    def downloads_done(self, timeout=None, cancel_if_timeout=True):
        if not self._owner._dl_mgr._running:
            raise RuntimeError(_S._lang.joinn(_S._lang.NEED_DOWNLOAD_PATH, TIP=_S._lang.SET_DOWNLOAD_PATH))

        def do():
            if self._owner._messenger_running:
                return True if not self._owner._dl_mgr._missions else None
            return False

        r = wait_until(do, timeout=timeout, gap=.5)
        if r is not None:
            return r
        if cancel_if_timeout:
            for m in list(self._owner._dl_mgr._missions.values()):
                m.cancel()
        return False


class BaseWaiter(OriginWaiter):
    def ele_deleted(self, loc_or_ele, timeout=None, raise_err=None):
        ele = self._owner._ele(loc_or_ele, raise_err=False, timeout=0)
        return ele.wait.deleted(timeout, raise_err=raise_err) if ele else True

    def ele_displayed(self, loc_or_ele, timeout=None, raise_err=None):
        if timeout is None:
            timeout = self._owner.timeout
        end_time = perf_counter() + timeout
        ele = self._owner._ele(loc_or_ele, raise_err=False, timeout=timeout)
        if not ele:
            if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
                raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.ELE_DISPLAYED, timeout)
            else:
                return False
        return ele.wait.displayed(end_time - perf_counter(), raise_err=raise_err)

    def ele_hidden(self, loc_or_ele, timeout=None, raise_err=None):
        if timeout is None:
            timeout = self._owner.timeout
        end_time = perf_counter() + timeout
        ele = self._owner._ele(loc_or_ele, raise_err=False, timeout=timeout)
        timeout = end_time - perf_counter()
        if timeout <= 0:
            if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
                raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.ELE_DISPLAYED, timeout)
            else:
                return False
        return ele.wait.hidden(timeout, raise_err=raise_err)

    def eles_loaded(self, locators, timeout=None, any_one=False, raise_err=None):
        def do_find_one(locs, owner):
            for loc in locs:
                if owner._ele(loc, timeout=0, raise_err=False):
                    return True
            return None

        def do_find_all(locs, owner):
            for loc in locs:
                if not owner._ele(loc, timeout=0, raise_err=False):
                    return None
            return True

        if isinstance(locators, str) or is_selenium_loc(locators):
            locators = [locators]
        func = do_find_one if any_one else do_find_all

        if timeout is None:
            timeout = self._owner.timeout

        err_txt = (_S._lang.join(_S._lang.WAITING_FAILED_, _S._lang.ELE_LOADED, timeout, LOCATOR=locators)
                   if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None) else None)
        r = wait_until(func, timeout=timeout, err_txt=err_txt, locs=locators, owner=self._owner)
        return r if r is not None else False

    def load_start(self, timeout=None, raise_err=None):
        return self._loading(timeout=timeout, gap=.002, raise_err=raise_err)

    def doc_loaded(self, timeout=None, raise_err=None):
        return self._loading(timeout=timeout, start=False, raise_err=raise_err)

    def upload_paths_inputted(self, timeout=None):
        def do():
            if self._owner._messenger_running:
                return True if not self._owner._upload_list else None
            return False

        if timeout is None:
            timeout = self._owner.timeout
        r = wait_until(do, timeout=timeout)
        return r if r is not None else False

    def download_begin(self, timeout=None, cancel_it=False):
        if not self._owner.browser._dl_mgr._running:
            raise RuntimeError(_S._lang.joinn(_S._lang.NEED_DOWNLOAD_PATH, TIP=_S._lang.SET_DOWNLOAD_PATH))
        self._owner.browser._dl_mgr.set_flag(self._owner.tab_id, False if cancel_it else True)
        if timeout is None:
            timeout = self._owner.timeout
        return wait_mission(self._owner.browser, self._owner.tab_id, timeout)

    def url_change(self, text, exclude=False, timeout=None, raise_err=None):
        return self._owner if self._change('url', text, exclude, timeout, raise_err) else False

    def title_change(self, text, exclude=False, timeout=None, raise_err=None):
        return self._owner if self._change('title', text, exclude, timeout, raise_err) else False

    def _change(self, arg, text, exclude=False, timeout=None, raise_err=None):
        if timeout is None:
            timeout = self._owner.timeout
        err_txt = (_S._lang.join(_S._lang.WAITING_FAILED_, arg, timeout)
                   if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None) else None)
        r = wait_until(self._do, timeout=timeout, err_txt=err_txt, arg=arg, text=text, exclude=exclude)
        return r if r is not None else False

    def _do(self, arg, text, exclude):
        v = self._owner._run_cdp('Target.getTargetInfo', targetId=self._owner._target_id)['targetInfo'][arg]
        return True if (not exclude and text in v) or (exclude and text not in v) else None

    def _loading(self, timeout=None, start=True, gap=.01, raise_err=None):
        def do():
            return True if self._owner._is_loading == start else None

        if timeout is None:
            timeout = self._owner.timeout

        err_txt = (_S._lang.join(_S._lang.WAITING_FAILED_, _S._lang.PAGE_LOADED, timeout)
                   if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None) else None)
        r = wait_until(do, timeout=timeout, err_txt=err_txt)
        return r if r is not None else False


class ChromiumTabWaiter(BaseWaiter):
    def downloads_done(self, timeout=None, cancel_if_timeout=True):
        if not self._owner.browser._dl_mgr._running:
            raise RuntimeError(_S._lang.joinn(_S._lang.NEED_DOWNLOAD_PATH, TIP=_S._lang.SET_DOWNLOAD_PATH))
        if not timeout:
            while self._owner.browser._dl_mgr.get_tab_missions(self._owner.tab_id):
                sleep(.5)
            return self._owner

        def do():
            return self._owner if not self._owner.browser._dl_mgr.get_tab_missions(self._owner.tab_id) else None

        r = wait_until(do, timeout=timeout, gap=.5)
        if r is not None:
            return r
        if cancel_if_timeout:
            for m in self._owner.browser._dl_mgr.get_tab_missions(self._owner.tab_id):
                m.cancel()
        return False

    def alert_closed(self, timeout=None):
        if timeout is None:
            while not self._owner.states.has_alert:
                sleep(.2)
            while self._owner.states.has_alert:
                sleep(.2)

        else:
            end_time = perf_counter() + timeout
            while not self._owner.states.has_alert and perf_counter() < end_time:
                sleep(.2)
            while self._owner.states.has_alert and perf_counter() < end_time:
                sleep(.2)

        return False if self._owner.states.has_alert else self._owner


class ElementWaiter(OriginWaiter):
    def __init__(self, owner):
        super().__init__(owner)
        self._ele = owner

    @property
    def _timeout(self):
        return self._ele.timeout

    def deleted(self, timeout=None, raise_err=None):
        return bool(self._wait_state('is_alive', False, timeout, raise_err, err_text=_S._lang.ELE_DEL))

    def displayed(self, timeout=None, raise_err=None):
        return self._wait_state('is_displayed', True, timeout, raise_err, err_text=_S._lang.ELE_DISPLAYED)

    def hidden(self, timeout=None, raise_err=None):
        return self._wait_state('is_displayed', False, timeout, raise_err, err_text=_S._lang.ELE_HIDDEN)

    def covered(self, timeout=None, raise_err=None):
        return self._wait_state('is_covered', True, timeout, raise_err, err_text=_S._lang.ELE_COVERED)

    def not_covered(self, timeout=None, raise_err=None):
        return self._wait_state('is_covered', False, timeout, raise_err, err_text=_S._lang.ELE_NOT_COVERED)

    def enabled(self, timeout=None, raise_err=None):
        return self._wait_state('is_enabled', True, timeout, raise_err, err_text=_S._lang.ELE_AVAILABLE)

    def disabled(self, timeout=None, raise_err=None):
        return self._wait_state('is_enabled', False, timeout, raise_err, err_text=_S._lang.ELE_NOT_AVAILABLE)

    def disabled_or_deleted(self, timeout=None, raise_err=None):
        def do():
            return self._ele if not self._ele.states.is_enabled or not self._ele.states.is_alive else None

        if timeout is None:
            timeout = self._timeout

        err_txt = (_S._lang.join(_S._lang.WAITING_FAILED_, _S._lang.ELE_HIDDEN_DEL, timeout)
                   if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None) else None)
        r = wait_until(do, timeout=timeout, err_txt=err_txt)
        return r if r is not None else False

    def clickable(self, wait_stop=None, timeout=None, raise_err=None):
        if timeout is None:
            timeout = self._timeout
        t1 = perf_counter()
        r = self._wait_state('is_clickable', True, timeout, raise_err, err_text=_S._lang.ELE_CLICKABLE)
        r = (self.stop_moving(timeout=timeout - perf_counter() + t1)
             if (_S.wait_stop_before_click if wait_stop is None else wait_stop) and r else r)
        if raise_err and not r:
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.ELE_CLICKABLE, timeout)
        return r

    def has_rect(self, timeout=None, raise_err=None):
        return self._wait_state('has_rect', True, timeout, raise_err, err_text=_S._lang.ELE_HAS_RECT)

    def stop_moving(self, timeout=None, gap=.05, raise_err=None):
        if timeout is None:
            timeout = self._timeout
        end_time = perf_counter() + timeout

        def do():
            try:
                s = self._ele.rect.size
                l = self._ele.rect.location
                return s, l
            except NoRectError:
                return None

        r = wait_until(do, timeout=timeout)
        if r is None:
            raise NoRectError
        else:
            size, location = r

        sleep(gap)
        if self._ele.rect.size == size and self._ele.rect.location == location:
            return self._ele
        while perf_counter() < end_time:
            sleep(gap)
            if self._ele.rect.size == size and self._ele.rect.location == location:
                return self._ele
            size = self._ele.rect.size
            location = self._ele.rect.location

        if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.ELE_STOP_MOVING, timeout)
        else:
            return False

    def _wait_state(self, attr, mode=False, timeout=None, raise_err=None, err_text=None):
        def do():
            a = self._ele.states.__getattribute__(attr)
            return (self._ele if isinstance(a, bool) else a) if (a and mode) or (not a and not mode) else None

        if timeout is None:
            timeout = self._timeout
        r = wait_until(do, timeout=timeout)
        if r is not None:
            return r
        err_text = err_text or _S._lang.ELE_STATE_CHANGED_
        if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_.format(err_text, timeout))
        else:
            return False


class FrameWaiter(BaseWaiter, ElementWaiter):
    def __init__(self, owner):
        super().__init__(owner)
        self._ele = owner.frame_ele

    @property
    def _timeout(self):
        return self._owner.timeout

    def _do(self, arg, text, exclude):
        v = get_frame_title(self._owner) if arg == 'title' else get_frame_url(self._owner)
        return True if (not exclude and text in v) or (exclude and text not in v) else None


def wait_mission(browser, tid, timeout):
    def do():
        if browser._messenger_running:
            v = browser._dl_mgr.get_flag(tid)
            return v if not isinstance(v, bool) else None
        return False

    r = wait_until(do, timeout, gap=.005)
    browser._dl_mgr.set_flag(tid, None)
    return r if r is not None else False


def get_frame_title(page):
    try:
        return page.run_js('return document.title;')
    except:
        return ''


def get_frame_url(page):
    r = page._run_cdp("Page.getFrameTree")
    frames = [{'frame': r['frameTree']['frame']}]
    if 'childFrames' in r['frameTree']:
        frames.extend(r['frameTree']['childFrames'])
    for i in frames:
        if i['frame']['id'] == page._frame_id:
            return i['frame'].get('url')
    return None
