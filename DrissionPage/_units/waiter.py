# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from time import sleep, perf_counter

from .._functions.locator import get_loc
from .._functions.settings import Settings
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
            curr_tab = self._owner.tab_ids[0]
        elif hasattr(curr_tab, '_type'):
            curr_tab = curr_tab.tab_id
        if timeout is None:
            timeout = self._owner.timeout
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            latest_tid = self._owner.tab_ids[0]
            if curr_tab != latest_tid:
                return latest_tid
            sleep(.01)

        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError(f'等待新标签页失败（等待{timeout}秒）。')
        else:
            return False

    def download_begin(self, timeout=None, cancel_it=False):
        if not self._owner._dl_mgr._running:
            raise RuntimeError('此功能需显式设置下载路径才能使用。使用set.download_path()方法、配置对象或ini文件均可。')
        self._owner._dl_mgr.set_flag('browser', False if cancel_it else True)
        if timeout is None:
            timeout = self._owner.timeout

        r = False
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            v = self._owner._dl_mgr.get_flag('browser')
            if not isinstance(v, bool):
                r = v
                break
            sleep(.005)

        self._owner._dl_mgr.set_flag('browser', None)
        return r

    def downloads_done(self, timeout=None, cancel_if_timeout=True):
        if not self._owner._dl_mgr._running:
            raise RuntimeError('此功能需显式设置下载路径（使用set.download_path()方法、配置对象或ini文件均可）。')
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
        timeout = end_time - perf_counter()
        if timeout <= 0 or not ele:
            if raise_err is True or Settings.raise_when_wait_failed is True:
                raise WaitTimeoutError(f'等待元素显示失败（等待{timeout}秒）。')
            else:
                return False
        return ele.wait.displayed(timeout, raise_err=raise_err)

    def ele_hidden(self, loc_or_ele, timeout=None, raise_err=None):
        if timeout is None:
            timeout = self._owner.timeout
        end_time = perf_counter() + timeout
        ele = self._owner._ele(loc_or_ele, raise_err=False, timeout=timeout)
        timeout = end_time - perf_counter()
        if timeout <= 0:
            if raise_err is True or Settings.raise_when_wait_failed is True:
                raise WaitTimeoutError(f'等待元素显示失败（等待{timeout}秒）。')
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
        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError(f'等待元素{locators}加载失败（等待{timeout}秒）。')
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
            raise RuntimeError('此功能需显式设置下载路径（使用set.download_path()方法、配置对象或ini文件均可）。')
        self._owner.browser._dl_mgr.set_flag(self._owner.tab_id, False if cancel_it else True)
        if timeout is None:
            timeout = self._owner.timeout

        r = False
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            v = self._owner.browser._dl_mgr.get_flag(self._owner.tab_id)
            if not isinstance(v, bool):
                r = v
                break
            sleep(.005)

        self._owner.browser._dl_mgr.set_flag(self._owner.tab_id, None)
        return r

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

        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError(f'等待{arg}改变失败（等待{timeout}秒）。')
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

        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError(f'等待页面加载失败（等待{timeout}秒）。')
        else:
            return False


class TabWaiter(BaseWaiter):
    def downloads_done(self, timeout=None, cancel_if_timeout=True):
        if not self._owner.browser._dl_mgr._running:
            raise RuntimeError('此功能需显式设置下载路径（使用set.download_path()方法、配置对象或ini文件均可）。')
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
        return self._wait_state('is_alive', False, timeout, raise_err, err_text='等待元素被删除失败。')

    def displayed(self, timeout=None, raise_err=None):
        return self._wait_state('is_displayed', True, timeout, raise_err, err_text='等待元素显示失败。')

    def hidden(self, timeout=None, raise_err=None):
        return self._wait_state('is_displayed', False, timeout, raise_err, err_text='等待元素隐藏失败。')

    def covered(self, timeout=None, raise_err=None):
        return self._wait_state('is_covered', True, timeout, raise_err, err_text='等待元素被覆盖失败。')

    def not_covered(self, timeout=None, raise_err=None):
        return self._wait_state('is_covered', False, timeout, raise_err, err_text='等待元素不被覆盖失败。')

    def enabled(self, timeout=None, raise_err=None):
        return self._wait_state('is_enabled', True, timeout, raise_err, err_text='等待元素变成可用失败。')

    def disabled(self, timeout=None, raise_err=None):
        return self._wait_state('is_enabled', False, timeout, raise_err, err_text='等待元素变成不可用失败。')

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

        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError(f'等待元素隐藏或被删除失败（等待{timeout}秒）。')
        else:
            return False

    def clickable(self, wait_moved=True, timeout=None, raise_err=None):
        if timeout is None:
            timeout = self._timeout
        t1 = perf_counter()
        r = self._wait_state('is_clickable', True, timeout, raise_err, err_text='等待元素可点击失败（等{}秒）。')
        r = self.stop_moving(timeout=timeout - perf_counter() + t1) if wait_moved and r else r
        if raise_err and not r:
            raise WaitTimeoutError(f'等待元素可点击失败（等{timeout}秒）。')
        return r

    def has_rect(self, timeout=None, raise_err=None):
        return self._wait_state('has_rect', True, timeout, raise_err, err_text='等待元素拥有大小及位置失败（等{}秒）。')

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

        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError(f'等待元素停止运动失败（等待{timeout}秒）。')
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

        err_text = err_text or '等待元素状态改变失败（等待{}秒）。'
        if raise_err is True or Settings.raise_when_wait_failed is True:
            raise WaitTimeoutError(err_text.format(timeout))
        else:
            return False


class FrameWaiter(BaseWaiter, ElementWaiter):
    def __init__(self, owner):
        super().__init__(owner)
        self._ele = owner.frame_ele

    @property
    def _timeout(self):
        return self._owner.timeout
