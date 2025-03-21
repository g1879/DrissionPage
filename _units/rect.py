# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""


class ElementRect(object):
    def __init__(self, ele):
        self._ele = ele

    @property
    def corners(self):
        vr = self._get_viewport_rect('border')
        r = self._ele.owner._run_cdp_loaded('Page.getLayoutMetrics')['visualViewport']
        sx = r['pageX']
        sy = r['pageY']
        return [(vr[0] + sx, vr[1] + sy), (vr[2] + sx, vr[3] + sy), (vr[4] + sx, vr[5] + sy), (vr[6] + sx, vr[7] + sy)]

    @property
    def viewport_corners(self):
        r = self._get_viewport_rect('border')
        return (r[0], r[1]), (r[2], r[3]), (r[4], r[5]), (r[6], r[7])

    @property
    def size(self):
        border = self._ele.owner._run_cdp('DOM.getBoxModel', backendNodeId=self._ele._backend_id,
                                          nodeId=self._ele._node_id, objectId=self._ele._obj_id)['model']['border']
        return border[2] - border[0], border[5] - border[1]

    @property
    def location(self):
        return self._get_page_coord(*self.viewport_location)

    @property
    def midpoint(self):
        return self._get_page_coord(*self.viewport_midpoint)

    @property
    def click_point(self):
        return self._get_page_coord(*self.viewport_click_point)

    @property
    def viewport_location(self):
        m = self._get_viewport_rect('border')
        return m[0], m[1]

    @property
    def viewport_midpoint(self):
        m = self._get_viewport_rect('border')
        return m[0] + (m[2] - m[0]) // 2, m[3] + (m[5] - m[3]) // 2

    @property
    def viewport_click_point(self):
        m = self._get_viewport_rect('padding')
        return self.viewport_midpoint[0], m[1] + 3

    @property
    def screen_location(self):
        vx, vy = self._ele.owner.rect.viewport_location
        ex, ey = self.viewport_location
        pr = self._ele.owner._run_js('return window.devicePixelRatio;')
        if getattr(self._ele.owner, '_is_diff_domain', None):
            x, y = self._ele.owner.rect.screen_location
            return ex * pr + x, ey * pr + y
        else:
            return (vx + ex) * pr, (ey + vy) * pr

    @property
    def screen_midpoint(self):
        vx, vy = self._ele.owner.rect.viewport_location
        ex, ey = self.viewport_midpoint
        pr = self._ele.owner._run_js('return window.devicePixelRatio;')
        if getattr(self._ele.owner, '_is_diff_domain', None):
            x, y = self._ele.owner.rect.screen_location
            return ex * pr + x, ey * pr + y
        else:
            return (vx + ex) * pr, (ey + vy) * pr

    @property
    def screen_click_point(self):
        vx, vy = self._ele.owner.rect.viewport_location
        ex, ey = self.viewport_click_point
        pr = self._ele.owner._run_js('return window.devicePixelRatio;')
        if getattr(self._ele.owner, '_is_diff_domain', None):
            x, y = self._ele.owner.rect.screen_location
            return ex * pr + x, ey * pr + y
        else:
            return (vx + ex) * pr, (ey + vy) * pr

    @property
    def scroll_position(self):
        r = self._ele._run_js('return this.scrollLeft.toString() + " " + this.scrollTop.toString();')
        w, h = r.split(' ')
        return int(w), int(h)

    def _get_viewport_rect(self, quad):
        return self._ele.owner._run_cdp('DOM.getBoxModel', backendNodeId=self._ele._backend_id)['model'][quad]

    def _get_page_coord(self, x, y):
        r = self._ele.owner._run_cdp_loaded('Page.getLayoutMetrics')['visualViewport']
        sx = r['pageX']
        sy = r['pageY']
        return x + sx, y + sy


class TabRect(object):
    def __init__(self, owner):
        self._owner = owner

    @property
    def window_state(self):
        return self._get_window_rect()['windowState']

    @property
    def window_location(self):
        r = self._get_window_rect()
        if r['windowState'] in ('maximized', 'fullscreen'):
            return 0, 0
        return r['left'] + 7, r['top']

    @property
    def window_size(self):
        r = self._get_window_rect()
        if r['windowState'] == 'fullscreen':
            return r['width'], r['height']
        elif r['windowState'] == 'maximized':
            return r['width'] - 16, r['height'] - 16
        else:
            return r['width'] - 16, r['height'] - 7

    @property
    def page_location(self):
        w, h = self.viewport_location
        r = self._get_page_rect()['layoutViewport']
        return w - r['pageX'], h - r['pageY']

    @property
    def viewport_location(self):
        w_bl, h_bl = self.window_location
        w_bs, h_bs = self.window_size
        w_vs, h_vs = self.viewport_size_with_scrollbar
        return w_bl + w_bs - w_vs, h_bl + h_bs - h_vs

    @property
    def size(self):
        r = self._get_page_rect()['contentSize']
        return r['width'], r['height']

    @property
    def viewport_size(self):
        r = self._get_page_rect()['visualViewport']
        return r['clientWidth'], r['clientHeight']

    @property
    def viewport_size_with_scrollbar(self):
        r = self._owner._run_js('return window.innerWidth.toString() + " " + window.innerHeight.toString();')
        w, h = r.split(' ')
        return int(w), int(h)

    @property
    def scroll_position(self):
        r = self._get_page_rect()['visualViewport']
        return r['pageX'], r['pageY']

    def _get_page_rect(self):
        return self._owner._run_cdp_loaded('Page.getLayoutMetrics')

    def _get_window_rect(self):
        return self._owner.browser._driver.run('Browser.getWindowForTarget', targetId=self._owner.tab_id)['bounds']


class FrameRect(object):
    """异域iframe使用"""

    def __init__(self, frame):
        self._frame = frame

    @property
    def location(self):
        return self._frame.frame_ele.rect.location

    @property
    def viewport_location(self):
        return self._frame.frame_ele.rect.viewport_location

    @property
    def screen_location(self):
        return self._frame.frame_ele.rect.screen_location

    @property
    def size(self):
        w = self._frame.doc_ele._run_js('return this.body.scrollWidth')
        h = self._frame.doc_ele._run_js('return this.body.scrollHeight')
        return w, h

    @property
    def viewport_size(self):
        return self._frame.frame_ele.rect.size

    @property
    def corners(self):
        return self._frame.frame_ele.rect.corners

    @property
    def viewport_corners(self):
        return self._frame.frame_ele.rect.viewport_corners

    @property
    def scroll_position(self):
        r = self._frame.doc_ele._run_js('return this.documentElement.scrollLeft.toString() + " " '
                                        '+ this.documentElement.scrollTop.toString();')
        w, h = r.split(' ')
        return int(w), int(h)
