# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from time import sleep, perf_counter

from .._functions.locator import get_loc
from .._functions.settings import Settings as _S
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


class BrowserWaiter(OriginWaiter):
    def new_tab(self, timeout=None, curr_tab=None, raise_err=None):
        if not curr_tab:
            curr_tab = self._owner._newest_tab_id
        elif hasattr(curr_tab, '_type'):
            curr_tab = curr_tab.tab_id
        if timeout is None:
            timeout = self._owner.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if curr_tab != self._owner._newest_tab_id:
                return self._owner._newest_tab_id
            sleep(.01)

        if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.NEW_TAB, timeout)
        else:
            return False

    def download_begin(self, timeout=None, cancel_it=False):
        if not self._owner._dl_mgr._running:
            raise RuntimeError(_S._lang.join(_S._lang.NEED_DOWNLOAD_PATH, TIP=_S._lang.SET_DOWNLOAD_PATH))
        self._owner._dl_mgr.set_flag('browser', False if cancel_it else True)
        if timeout is None:
            timeout = self._owner.timeout
        return wait_mission(self._owner, 'browser', timeout)

    def downloads_done(self, timeout=None, cancel_if_timeout=True):
        if not self._owner._dl_mgr._running:
            raise RuntimeError(_S._lang.join(_S._lang.NEED_DOWNLOAD_PATH, TIP=_S._lang.SET_DOWNLOAD_PATH))
        if not timeout:
            while self._owner._dl_mgr._missions:
                sleep(.5)
            return True

        else:
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                if not self._owner._dl_mgr._missions:
                    return True
                sleep(.5)

            if self._owner._dl_mgr._missions:
                if cancel_if_timeout:
                    for m in list(self._owner._dl_mgr._missions.values()):
                        m.cancel()
                return False
            else:
                return True


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

        def _find(loc, driver):
            r = driver.run('DOM.performSearch', query=loc, includeUserAgentShadowDOM=True)
            if not r or 'error' in r:
                return False
            elif r['resultCount'] == 0:
                driver.run('DOM.discardSearchResults', searchId=r['searchId'])
                return False
            searchId = r['searchId']
            ids = driver.run('DOM.getSearchResults', searchId=searchId, fromIndex=0,
                             toIndex=r['resultCount'])
            if 'error' in ids:
                return False

            ids = ids['nodeIds']
            res = False
            for i in ids:
                r = driver.run('DOM.describeNode', nodeId=i)
                if 'error' in r or r['node']['nodeName'] in ('#text', '#comment'):
                    continue
                else:
                    res = True
                    break
            driver.run('DOM.discardSearchResults', searchId=searchId)
            return res

        by = ('id', 'xpath', 'link text', 'partial link text', 'name', 'tag name', 'class name', 'css selector')
        locators = ((get_loc(locators)[1],) if (isinstance(locators, str) or isinstance(locators, tuple)
                                                and locators[0] in by and len(locators) == 2)
                    else [get_loc(x)[1] for x in locators])
        method = any if any_one else all

        if timeout is None:
            timeout = self._owner.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if method([_find(l, self._owner.driver) for l in locators]):
                return True
            sleep(.01)
        if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.ELE_LOADED, timeout, LOCATOR=locators)
        else:
            return False

    def load_start(self, timeout=None, raise_err=None):
        return self._loading(timeout=timeout, gap=.002, raise_err=raise_err)

    def doc_loaded(self, timeout=None, raise_err=None):
        return self._loading(timeout=timeout, start=False, raise_err=raise_err)

    def upload_paths_inputted(self):
        end_time = perf_counter() + self._owner.timeout
        while perf_counter() < end_time:
            if not self._owner._upload_list:
                return True
            sleep(.01)
        return False

    def download_begin(self, timeout=None, cancel_it=False):
        if not self._owner.browser._dl_mgr._running:
            raise RuntimeError(_S._lang.join(_S._lang.NEED_DOWNLOAD_PATH, TIP=_S._lang.SET_DOWNLOAD_PATH))
        self._owner.browser._dl_mgr.set_flag(self._owner.tab_id, False if cancel_it else True)
        if timeout is None:
            timeout = self._owner.timeout
        return wait_mission(self._owner.browser, self._owner.tab_id, timeout)

    def url_change(self, text, exclude=False, timeout=None, raise_err=None):
        return self._owner if self._change('url', text, exclude, timeout, raise_err) else False

    def title_change(self, text, exclude=False, timeout=None, raise_err=None):
        return self._owner if self._change('title', text, exclude, timeout, raise_err) else False

    def _change(self, arg, text, exclude=False, timeout=None, raise_err=None):

        def do():
            if arg == 'url':
                v = self._owner._run_cdp('Target.getTargetInfo', targetId=self._owner._target_id)['targetInfo']['url']
            elif arg == 'title':
                v = self._owner._run_cdp('Target.getTargetInfo', targetId=self._owner._target_id)['targetInfo']['title']
            else:
                raise ValueError
            if (not exclude and text in v) or (exclude and text not in v):
                return True

        if do():
            return True

        if timeout is None:
            timeout = self._owner.timeout

        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if do():
                return True
            sleep(.05)

        if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.ARG, timeout, ARG=arg)
        else:
            return False

    def _loading(self, timeout=None, start=True, gap=.01, raise_err=None):
        if timeout is None:
            timeout = self._owner.timeout
        timeout = .1 if timeout <= 0 else timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if self._owner._is_loading == start:
                return True
            sleep(gap)

        if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.PAGE_LOADED, timeout)
        else:
            return False


class TabWaiter(BaseWaiter):
    def downloads_done(self, timeout=None, cancel_if_timeout=True):
        if not self._owner.browser._dl_mgr._running:
            raise RuntimeError(_S._lang.join(_S._lang.NEED_DOWNLOAD_PATH, TIP=_S._lang.SET_DOWNLOAD_PATH))
        if not timeout:
            while self._owner.browser._dl_mgr.get_tab_missions(self._owner.tab_id):
                sleep(.5)
            return self._owner

        else:
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                if not self._owner.browser._dl_mgr.get_tab_missions(self._owner.tab_id):
                    return self._owner
                sleep(.5)

            if self._owner.browser._dl_mgr.get_tab_missions(self._owner.tab_id):
                if cancel_if_timeout:
                    for m in self._owner.browser._dl_mgr.get_tab_missions(self._owner.tab_id):
                        m.cancel()
                return False
            else:
                return self._owner

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


class ChromiumPageWaiter(TabWaiter):
    def new_tab(self, timeout=None, raise_err=None):
        return self._owner.browser.wait.new_tab(timeout=timeout, raise_err=raise_err)

    def download_begin(self, timeout=None, cancel_it=False):
        return self._owner.browser.wait.download_begin(timeout=timeout, cancel_it=cancel_it)

    def all_downloads_done(self, timeout=None, cancel_if_timeout=True):
        return self._owner.browser.wait.downloads_done(timeout=timeout, cancel_if_timeout=cancel_if_timeout)


class ElementWaiter(OriginWaiter):
    def __init__(self, owner):
        super().__init__(owner)
        self._ele = owner

    @property
    def _timeout(self):
        return self._ele.timeout

    def deleted(self, timeout=None, raise_err=None):
        return self._wait_state('is_alive', False, timeout, raise_err,
                                err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_DEL, timeout))

    def displayed(self, timeout=None, raise_err=None):
        return self._wait_state('is_displayed', True, timeout, raise_err,
                                err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_DISPLAYED, timeout))

    def hidden(self, timeout=None, raise_err=None):
        return self._wait_state('is_displayed', False, timeout, raise_err,
                                err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_HIDDEN, timeout))

    def covered(self, timeout=None, raise_err=None):
        return self._ele if self._wait_state('is_covered', True, timeout, raise_err,
                                             err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_COVERED,
                                                                                      timeout)) else False

    def not_covered(self, timeout=None, raise_err=None):
        return self._wait_state('is_covered', False, timeout, raise_err,
                                err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_NOT_COVERED, timeout))

    def enabled(self, timeout=None, raise_err=None):
        return self._wait_state('is_enabled', True, timeout, raise_err,
                                err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_AVAILABLE, timeout))

    def disabled(self, timeout=None, raise_err=None):
        return self._wait_state('is_enabled', False, timeout, raise_err,
                                err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_NOT_AVAILABLE, timeout))

    def disabled_or_deleted(self, timeout=None, raise_err=None):
        if not self._ele.states.is_enabled or not self._ele.states.is_alive:
            return self._ele

        if timeout is None:
            timeout = self._timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if not self._ele.states.is_enabled or not self._ele.states.is_alive:
                return self._ele
            sleep(.05)

        if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.ELE_HIDDEN_DEL, timeout)
        else:
            return False

    def clickable(self, wait_moved=True, timeout=None, raise_err=None):
        if timeout is None:
            timeout = self._timeout
        t1 = perf_counter()
        r = self._wait_state('is_clickable', True, timeout, raise_err,
                             err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_CLICKABLE, timeout))
        r = self.stop_moving(timeout=timeout - perf_counter() + t1) if wait_moved and r else r
        if raise_err and not r:
            raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.ELE_CLICKABLE, timeout)
        return r

    def has_rect(self, timeout=None, raise_err=None):
        return self._ele if self._wait_state('has_rect', True, timeout, raise_err,
                                             err_text=_S._lang.WAITING_FAILED_.format(_S._lang.ELE_HAS_RECT,
                                                                                      timeout)) else False

    def stop_moving(self, timeout=None, gap=.1, raise_err=None):
        if timeout is None:
            timeout = self._timeout
        if timeout <= 0:
            timeout = .1

        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            try:
                size = self._ele.states.has_rect
                location = self._ele.rect.location
                break
            except NoRectError:
                pass
            sleep(.005)
        else:
            raise NoRectError

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
        a = self._ele.states.__getattribute__(attr)
        if (a and mode) or (not a and not mode):
            return self._ele if isinstance(a, bool) else a

        if timeout is None:
            timeout = self._timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            a = self._ele.states.__getattribute__(attr)
            if (a and mode) or (not a and not mode):
                return self._ele if isinstance(a, bool) else a
            sleep(.05)

        err_text = err_text or _S._lang.ELE_STATE_CHANGED_.format(timeout)
        if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
            raise WaitTimeoutError(err_text)
        else:
            return False


class FrameWaiter(BaseWaiter, ElementWaiter):
    def __init__(self, owner):
        super().__init__(owner)
        self._ele = owner.frame_ele

    @property
    def _timeout(self):
        return self._owner.timeout


def wait_mission(browser, tid, timeout=None):
    r = False
    end_time = perf_counter() + timeout
    while perf_counter() < end_time:
        v = browser._dl_mgr.get_flag(tid)
        if not isinstance(v, bool):
            r = v
            break
        sleep(.005)

    browser._dl_mgr.set_flag(tid, None)
    return r
