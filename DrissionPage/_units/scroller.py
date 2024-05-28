# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from time import sleep, perf_counter


class Scroller(object):
    """用于滚动的对象"""

    def __init__(self, ele):
        """
        :param ele: 元素对象
        """
        self._driver = ele
        self.t1 = self.t2 = 'this'
        self._wait_complete = False

    def _run_js(self, js):
        js = js.format(self.t1, self.t2, self.t2)
        self._driver.run_js(js)
        self._wait_scrolled()

    def to_top(self):
        """滚动到顶端，水平位置不变"""
        self._run_js('{}.scrollTo({}.scrollLeft, 0);')

    def to_bottom(self):
        """滚动到底端，水平位置不变"""
        self._run_js('{}.scrollTo({}.scrollLeft, {}.scrollHeight);')

    def to_half(self):
        """滚动到垂直中间位置，水平位置不变"""
        self._run_js('{}.scrollTo({}.scrollLeft, {}.scrollHeight/2);')

    def to_rightmost(self):
        """滚动到最右边，垂直位置不变"""
        self._run_js('{}.scrollTo({}.scrollWidth, {}.scrollTop);')

    def to_leftmost(self):
        """滚动到最左边，垂直位置不变"""
        self._run_js('{}.scrollTo(0, {}.scrollTop);')

    def to_location(self, x, y):
        """滚动到指定位置
        :param x: 水平距离
        :param y: 垂直距离
        :return: None
        """
        self._run_js(f'{{}}.scrollTo({x}, {y});')

    def up(self, pixel=300):
        """向上滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        pixel = -pixel
        self._run_js(f'{{}}.scrollBy(0, {pixel});')

    def down(self, pixel=300):
        """向下滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        self._run_js(f'{{}}.scrollBy(0, {pixel});')

    def left(self, pixel=300):
        """向左滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        pixel = -pixel
        self._run_js(f'{{}}.scrollBy({pixel}, 0);')

    def right(self, pixel=300):
        """向右滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        self._run_js(f'{{}}.scrollBy({pixel}, 0);')

    def _wait_scrolled(self):
        """等待滚动结束"""
        if not self._wait_complete:
            return

        owner = self._driver.owner if self._driver._type == 'ChromiumElement' else self._driver
        r = owner.run_cdp('Page.getLayoutMetrics')
        x = r['layoutViewport']['pageX']
        y = r['layoutViewport']['pageY']

        end_time = perf_counter() + owner.timeout
        while perf_counter() < end_time:
            sleep(.1)
            r = owner.run_cdp('Page.getLayoutMetrics')
            x1 = r['layoutViewport']['pageX']
            y1 = r['layoutViewport']['pageY']

            if x == x1 and y == y1:
                break

            x = x1
            y = y1


class ElementScroller(Scroller):
    def to_see(self, center=None):
        """滚动页面直到元素可见
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        self._driver.owner.scroll.to_see(self._driver, center=center)

    def to_center(self):
        """元素尽量滚动到视口中间"""
        self._driver.owner.scroll.to_see(self._driver, center=True)


class PageScroller(Scroller):
    def __init__(self, owner):
        """
        :param owner: 页面对象
        """
        super().__init__(owner)
        self.t1 = 'window'
        self.t2 = 'document.documentElement'

    def to_see(self, loc_or_ele, center=None):
        """滚动页面直到元素可见
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        ele = self._driver._ele(loc_or_ele)
        self._to_see(ele, center)

    def _to_see(self, ele, center):
        """执行滚动页面直到元素可见
        :param ele: 元素对象
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        txt = 'true' if center else 'false'
        ele.run_js(f'this.scrollIntoViewIfNeeded({txt});')
        if center or (center is not False and ele.states.is_covered):
            ele.run_js('''function getWindowScrollTop() {let scroll_top = 0;
                    if (document.documentElement && document.documentElement.scrollTop) {
                      scroll_top = document.documentElement.scrollTop;
                    } else if (document.body) {scroll_top = document.body.scrollTop;}
                    return scroll_top;}
            const { top, height } = this.getBoundingClientRect();
                    const elCenter = top + height / 2;
                    const center = window.innerHeight / 2;
                    window.scrollTo({top: getWindowScrollTop() - (center - elCenter),
                    behavior: 'instant'});''')
        self._wait_scrolled()


class FrameScroller(PageScroller):
    def __init__(self, frame):
        """
        :param frame: ChromiumFrame对象
        """
        super().__init__(frame.doc_ele)
        self.t1 = self.t2 = 'this.documentElement'

    def to_see(self, loc_or_ele, center=None):
        """滚动页面直到元素可见
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        ele = loc_or_ele if loc_or_ele._type == 'ChromiumElement' else self._driver._ele(loc_or_ele)
        self._to_see(ele, center)
