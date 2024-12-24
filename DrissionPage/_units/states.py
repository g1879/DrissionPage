# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from .._functions.web import location_in_viewport
from ..errors import CDPError, NoRectError, PageDisconnectedError, ElementLostError


class ElementStates(object):
    def __init__(self, ele):
        self._ele = ele

    @property
    def is_selected(self):
        return self._ele._run_js('return this.selected;')

    @property
    def is_checked(self):
        return self._ele._run_js('return this.checked;')

    @property
    def is_displayed(self):
        return not (self._ele.style('visibility') == 'hidden'
                    or self._ele.style('display') == 'none'
                    or self._ele.property('hidden'))

    @property
    def is_enabled(self):
        return not self._ele._run_js('return this.disabled;')

    @property
    def is_alive(self):
        try:
            return self._ele.owner._run_cdp('DOM.describeNode',
                                            backendNodeId=self._ele._backend_id)['node']['nodeId'] != 0
        except ElementLostError:
            return False

    @property
    def is_in_viewport(self):
        x, y = self._ele.rect.click_point
        return location_in_viewport(self._ele.owner, x, y) if x else False

    @property
    def is_whole_in_viewport(self):
        x1, y1 = self._ele.rect.location
        w, h = self._ele.rect.size
        x2, y2 = x1 + w, y1 + h
        return location_in_viewport(self._ele.owner, x1, y1) and location_in_viewport(self._ele.owner, x2, y2)

    @property
    def is_covered(self):
        lx, ly = self._ele.rect.click_point
        try:
            bid = self._ele.owner._run_cdp('DOM.getNodeForLocation', x=int(lx), y=int(ly)).get('backendNodeId')
            return bid if bid != self._ele._backend_id else False
        except CDPError:
            return False

    @property
    def is_clickable(self):
        return self.has_rect and self.is_enabled and self.is_displayed and self._ele.style('pointer-events') != 'none'

    @property
    def has_rect(self):
        try:
            return self._ele.rect.corners
        except NoRectError:
            return False


class ShadowRootStates(object):
    def __init__(self, ele):
        self._ele = ele

    @property
    def is_enabled(self):
        return not self._ele._run_js('return this.disabled;')

    @property
    def is_alive(self):
        try:
            return self._ele.owner._run_cdp('DOM.describeNode',
                                            backendNodeId=self._ele._backend_id)['node']['nodeId'] != 0
        except ElementLostError:
            return False


class BrowserStates(object):
    def __init__(self, browser):
        self._browser = browser
        self._incognito = None

    @property
    def is_alive(self):
        return self._browser._driver.is_running

    @property
    def is_headless(self):
        return self._browser._is_headless

    @property
    def is_existed(self):
        return self._browser._is_exists

    @property
    def is_incognito(self):
        if self._incognito is None:
            self._incognito = "'Browser.WindowCount.Incognito'" in str(self._browser._run_cdp('Browser.getHistograms'))
        return self._incognito


class PageStates(object):
    """Page对象、Tab对象使用"""

    def __init__(self, owner):
        self._owner = owner

    @property
    def is_loading(self):
        return self._owner._is_loading

    @property
    def is_alive(self):
        try:
            self._owner._run_cdp('Page.getLayoutMetrics')
            return True
        except PageDisconnectedError:
            return False

    @property
    def ready_state(self):
        return self._owner._ready_state

    @property
    def has_alert(self):
        return self._owner._has_alert

    @property
    def is_headless(self):
        return self._owner.browser.states.is_headless

    @property
    def is_existed(self):
        return self._owner.browser.states.is_existed

    @property
    def is_incognito(self):
        return self._owner.browser.states.is_incognito


class FrameStates(object):
    def __init__(self, frame):
        self._frame = frame

    @property
    def is_loading(self):
        return self._frame._is_loading

    @property
    def is_alive(self):
        try:
            node = self._frame._target_page._run_cdp('DOM.describeNode',
                                                     backendNodeId=self._frame._frame_ele._backend_id)['node']
        except (ElementLostError, PageDisconnectedError):
            return False
        return 'frameId' in node

    @property
    def ready_state(self):
        return self._frame._ready_state

    @property
    def is_displayed(self):
        return not (self._frame.frame_ele.style('visibility') == 'hidden'
                    or self._frame.frame_ele._run_js('return this.offsetParent === null;')
                    or self._frame.frame_ele.style('display') == 'none')

    @property
    def has_alert(self):
        return self._frame._has_alert
