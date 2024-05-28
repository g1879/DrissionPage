# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""


class ElementRect(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    @property
    def corners(self):
        """返回元素四个角坐标，顺序：左上、右上、右下、左下，没有大小的元素抛出NoRectError"""
        vr = self._get_viewport_rect('border')
        r = self._ele.owner.run_cdp_loaded('Page.getLayoutMetrics')['visualViewport']
        sx = r['pageX']
        sy = r['pageY']
        return [(vr[0] + sx, vr[1] + sy), (vr[2] + sx, vr[3] + sy), (vr[4] + sx, vr[5] + sy), (vr[6] + sx, vr[7] + sy)]

    @property
    def viewport_corners(self):
        """返回元素四个角视口坐标，顺序：左上、右上、右下、左下，没有大小的元素抛出NoRectError"""
        r = self._get_viewport_rect('border')
        return (r[0], r[1]), (r[2], r[3]), (r[4], r[5]), (r[6], r[7])

    @property
    def size(self):
        """返回元素大小，格式(宽, 高)"""
        border = self._ele.owner.run_cdp('DOM.getBoxModel', backendNodeId=self._ele._backend_id,
                                         nodeId=self._ele._node_id, objectId=self._ele._obj_id)['model']['border']
        return border[2] - border[0], border[5] - border[1]

    @property
    def location(self):
        """返回元素左上角的绝对坐标"""
        cl = self.viewport_location
        return self._get_page_coord(cl[0], cl[1])

    @property
    def midpoint(self):
        """返回元素中间点的绝对坐标"""
        cl = self.viewport_midpoint
        return self._get_page_coord(cl[0], cl[1])

    @property
    def click_point(self):
        """返回元素接受点击的点的绝对坐标"""
        cl = self.viewport_click_point
        return self._get_page_coord(cl[0], cl[1])

    @property
    def viewport_location(self):
        """返回元素左上角在视口中的坐标"""
        m = self._get_viewport_rect('border')
        return m[0], m[1]

    @property
    def viewport_midpoint(self):
        """返回元素中间点在视口中的坐标"""
        m = self._get_viewport_rect('border')
        return m[0] + (m[2] - m[0]) // 2, m[3] + (m[5] - m[3]) // 2

    @property
    def viewport_click_point(self):
        """返回元素接受点击的点视口坐标"""
        m = self._get_viewport_rect('padding')
        return self.viewport_midpoint[0], m[1] + 3

    @property
    def screen_location(self):
        """返回元素左上角在屏幕上坐标，左上角为(0, 0)"""
        vx, vy = self._ele.owner.rect.viewport_location
        ex, ey = self.viewport_location
        pr = self._ele.owner.run_js('return window.devicePixelRatio;')
        return (vx + ex) * pr, (ey + vy) * pr

    @property
    def screen_midpoint(self):
        """返回元素中点在屏幕上坐标，左上角为(0, 0)"""
        vx, vy = self._ele.owner.rect.viewport_location
        ex, ey = self.viewport_midpoint
        pr = self._ele.owner.run_js('return window.devicePixelRatio;')
        return (vx + ex) * pr, (ey + vy) * pr

    @property
    def screen_click_point(self):
        """返回元素中点在屏幕上坐标，左上角为(0, 0)"""
        vx, vy = self._ele.owner.rect.viewport_location
        ex, ey = self.viewport_click_point
        pr = self._ele.owner.run_js('return window.devicePixelRatio;')
        return (vx + ex) * pr, (ey + vy) * pr

    def _get_viewport_rect(self, quad):
        """按照类型返回在可视窗口中的范围
        :param quad: 方框类型，margin border padding
        :return: 四个角坐标
        """
        return self._ele.owner.run_cdp('DOM.getBoxModel', backendNodeId=self._ele._backend_id,
                                       # nodeId=self._ele._node_id, objectId=self._ele._obj_id
                                       )['model'][quad]

    def _get_page_coord(self, x, y):
        """根据视口坐标获取绝对坐标"""
        r = self._ele.owner.run_cdp_loaded('Page.getLayoutMetrics')['visualViewport']
        sx = r['pageX']
        sy = r['pageY']
        return x + sx, y + sy


class TabRect(object):
    def __init__(self, owner):
        """
        :param owner: Page对象和Tab对象
        """
        self._owner = owner

    @property
    def window_state(self):
        """返回窗口状态：normal、fullscreen、maximized、minimized"""
        return self._get_window_rect()['windowState']

    @property
    def window_location(self):
        """返回窗口在屏幕上的坐标，左上角为(0, 0)"""
        r = self._get_window_rect()
        if r['windowState'] in ('maximized', 'fullscreen'):
            return 0, 0
        return r['left'] + 7, r['top']

    @property
    def window_size(self):
        """返回窗口大小"""
        r = self._get_window_rect()
        if r['windowState'] == 'fullscreen':
            return r['width'], r['height']
        elif r['windowState'] == 'maximized':
            return r['width'] - 16, r['height'] - 16
        else:
            return r['width'] - 16, r['height'] - 7

    @property
    def page_location(self):
        """返回页面左上角在屏幕中坐标，左上角为(0, 0)"""
        w, h = self.viewport_location
        r = self._get_page_rect()['layoutViewport']
        return w - r['pageX'], h - r['pageY']

    @property
    def viewport_location(self):
        """返回视口在屏幕中坐标，左上角为(0, 0)"""
        w_bl, h_bl = self.window_location
        w_bs, h_bs = self.window_size
        w_vs, h_vs = self.viewport_size_with_scrollbar
        return w_bl + w_bs - w_vs, h_bl + h_bs - h_vs

    @property
    def size(self):
        """返回页面总宽高，格式：(宽, 高)"""
        r = self._get_page_rect()['contentSize']
        return r['width'], r['height']

    @property
    def viewport_size(self):
        """返回视口宽高，不包括滚动条，格式：(宽, 高)"""
        r = self._get_page_rect()['visualViewport']
        return r['clientWidth'], r['clientHeight']

    @property
    def viewport_size_with_scrollbar(self):
        """返回视口宽高，包括滚动条，格式：(宽, 高)"""
        r = self._owner.run_js('return window.innerWidth.toString() + " " + window.innerHeight.toString();')
        w, h = r.split(' ')
        return int(w), int(h)

    def _get_page_rect(self):
        """获取页面范围信息"""
        return self._owner.run_cdp_loaded('Page.getLayoutMetrics')

    def _get_window_rect(self):
        """获取窗口范围信息"""
        return self._owner.browser.get_window_bounds(self._owner.tab_id)


class FrameRect(object):
    """异域iframe使用"""

    def __init__(self, frame):
        """
        :param frame: ChromiumFrame对象
        """
        self._frame = frame

    @property
    def location(self):
        """返回iframe元素左上角的绝对坐标"""
        return self._frame.frame_ele.rect.location

    @property
    def viewport_location(self):
        """返回元素在视口中坐标，左上角为(0, 0)"""
        return self._frame.frame_ele.rect.viewport_location

    @property
    def screen_location(self):
        """返回元素左上角在屏幕上坐标，左上角为(0, 0)"""
        return self._frame.frame_ele.rect.screen_location

    @property
    def size(self):
        """返回frame内页面尺寸，格式：(宽, 高)"""
        w = self._frame.doc_ele.run_js('return this.body.scrollWidth')
        h = self._frame.doc_ele.run_js('return this.body.scrollHeight')
        return w, h

    @property
    def viewport_size(self):
        """返回视口宽高，格式：(宽, 高)"""
        return self._frame.frame_ele.rect.size

    @property
    def corners(self):
        """返回元素四个角坐标，顺序：左上、右上、右下、左下"""
        return self._frame.frame_ele.rect.corners

    @property
    def viewport_corners(self):
        """返回元素四个角视口坐标，顺序：左上、右上、右下、左下"""
        return self._frame.frame_ele.rect.viewport_corners
