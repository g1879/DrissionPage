# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from .._functions.web import location_in_viewport
from ..errors import CDPError, NoRectError, PageDisconnectedError, ElementLostError


class ElementStates(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    @property
    def is_selected(self):
        """返回列表元素是否被选择"""
        return self._ele.run_js('return this.selected;')

    @property
    def is_checked(self):
        """返回元素是否被选择"""
        return self._ele.run_js('return this.checked;')

    @property
    def is_displayed(self):
        """返回元素是否显示"""
        return not (self._ele.style('visibility') == 'hidden' or
                    self._ele.run_js('return this.offsetParent === null;')
                    or self._ele.style('display') == 'none' or self._ele.property('hidden'))

    @property
    def is_enabled(self):
        """返回元素是否可用"""
        return not self._ele.run_js('return this.disabled;')

    @property
    def is_alive(self):
        """返回元素是否仍在DOM中"""
        try:
            return self._ele.owner.run_cdp('DOM.describeNode',
                                           backendNodeId=self._ele._backend_id)['node']['nodeId'] != 0
        except ElementLostError:
            return False

    @property
    def is_in_viewport(self):
        """返回元素是否出现在视口中，以元素click_point为判断"""
        x, y = self._ele.rect.click_point
        return location_in_viewport(self._ele.owner, x, y) if x else False

    @property
    def is_whole_in_viewport(self):
        """返回元素是否整个都在视口内"""
        x1, y1 = self._ele.rect.location
        w, h = self._ele.rect.size
        x2, y2 = x1 + w, y1 + h
        return location_in_viewport(self._ele.owner, x1, y1) and location_in_viewport(self._ele.owner, x2, y2)

    @property
    def is_covered(self):
        """返回元素是否被覆盖，与是否在视口中无关，如被覆盖返回覆盖元素的backend id，否则返回False"""
        lx, ly = self._ele.rect.click_point
        try:
            bid = self._ele.owner.run_cdp('DOM.getNodeForLocation', x=int(lx), y=int(ly)).get('backendNodeId')
            return bid if bid != self._ele._backend_id else False
        except CDPError:
            return False

    @property
    def is_clickable(self):
        """返回元素是否可被模拟点击，从是否有大小、是否可用、是否显示、是否响应点击判断，不判断是否被遮挡"""
        return self.has_rect and self.is_enabled and self.is_displayed and self._ele.style('pointer-events') != 'none'

    @property
    def has_rect(self):
        """返回元素是否拥有位置和大小，没有返回False，有返回四个角在页面中坐标组成的列表"""
        try:
            return self._ele.rect.corners
        except NoRectError:
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
            return self._ele.owner.run_cdp('DOM.describeNode',
                                           backendNodeId=self._ele._backend_id)['node']['nodeId'] != 0
        except ElementLostError:
            return False


class PageStates(object):
    """Page对象、Tab对象使用"""

    def __init__(self, owner):
        """
        :param owner: ChromiumBase对象
        """
        self._owner = owner

    @property
    def is_loading(self):
        """返回页面是否在加载状态"""
        return self._owner._is_loading

    @property
    def is_alive(self):
        """返回页面对象是否仍然可用"""
        try:
            self._owner.run_cdp('Page.getLayoutMetrics')
            return True
        except PageDisconnectedError:
            return False

    @property
    def ready_state(self):
        """返回当前页面加载状态，'connecting' 'loading' 'interactive' 'complete'"""
        return self._owner._ready_state

    @property
    def has_alert(self):
        """返回当前页面是否存在弹窗"""
        return self._owner._has_alert


class FrameStates(object):
    def __init__(self, frame):
        """
        :param frame: ChromiumFrame对象
        """
        self._frame = frame

    @property
    def is_loading(self):
        """返回页面是否在加载状态"""
        return self._frame._is_loading

    @property
    def is_alive(self):
        """返回frame元素是否可用，且里面仍挂载有frame"""
        try:
            node = self._frame._target_page.run_cdp('DOM.describeNode',
                                                    backendNodeId=self._frame._frame_ele._backend_id)['node']
        except (ElementLostError, PageDisconnectedError):
            return False
        return 'frameId' in node

    @property
    def ready_state(self):
        """返回加载状态"""
        return self._frame._ready_state

    @property
    def is_displayed(self):
        """返回iframe是否显示"""
        return not (self._frame.frame_ele.style('visibility') == 'hidden'
                    or self._frame.frame_ele.run_js('return this.offsetParent === null;')
                    or self._frame.frame_ele.style('display') == 'none')

    @property
    def has_alert(self):
        """返回当前页面是否存在弹窗"""
        return self._frame._has_alert
