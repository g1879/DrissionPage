# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from time import sleep, perf_counter


class Scroller(object):
    """用于滚动的对象"""

    def __init__(self, owner):
        self._owner = owner
        self._t1 = self._t2 = 'this'
        self._wait_complete = False

    def __call__(self, pixel=300):
        return self.down(pixel)

    def _run_js(self, js):
        js = js.format(self._t1, self._t2, self._t2)
        self._owner._run_js(js)
        self._wait_scrolled()

    def to_top(self):
        self._run_js('{}.scrollTo({}.scrollLeft, 0);')
        return self._owner

    def to_bottom(self):
        self._run_js('{}.scrollTo({}.scrollLeft, {}.scrollHeight);')
        return self._owner

    def to_half(self):
        self._run_js('{}.scrollTo({}.scrollLeft, {}.scrollHeight/2);')
        return self._owner

    def to_rightmost(self):
        self._run_js('{}.scrollTo({}.scrollWidth, {}.scrollTop);')
        return self._owner

    def to_leftmost(self):
        self._run_js('{}.scrollTo(0, {}.scrollTop);')
        return self._owner

    def to_location(self, x, y):
        self._run_js(f'{{}}.scrollTo({x}, {y});')
        return self._owner

    def up(self, pixel=300):
        pixel = -pixel
        self._run_js(f'{{}}.scrollBy(0, {pixel});')
        return self._owner

    def down(self, pixel=300):
        self._run_js(f'{{}}.scrollBy(0, {pixel});')
        return self._owner

    def left(self, pixel=300):
        pixel = -pixel
        self._run_js(f'{{}}.scrollBy({pixel}, 0);')
        return self._owner

    def right(self, pixel=300):
        self._run_js(f'{{}}.scrollBy({pixel}, 0);')
        return self._owner

    def _wait_scrolled(self):
        if not self._wait_complete:
            return

        owner = self._owner.owner if self._owner._type == 'ChromiumElement' else self._owner
        r = owner._run_cdp('Page.getLayoutMetrics')
        x = r['layoutViewport']['pageX']
        y = r['layoutViewport']['pageY']

        end_time = perf_counter() + owner.timeout
        while perf_counter() < end_time:
            sleep(.02)
            r = owner._run_cdp('Page.getLayoutMetrics')
            x1 = r['layoutViewport']['pageX']
            y1 = r['layoutViewport']['pageY']

            if x == x1 and y == y1:
                break

            x = x1
            y = y1


class ElementScroller(Scroller):
    def to_see(self, center=None):
        self._owner.owner.scroll.to_see(self._owner, center=center)
        return self._owner

    def to_center(self):
        self._owner.owner.scroll.to_see(self._owner, center=True)
        return self._owner


class PageScroller(Scroller):
    def __init__(self, owner):
        super().__init__(owner)
        self._t1 = 'window'
        self._t2 = 'document.documentElement'

    def to_see(self, loc_or_ele, center=None):
        ele = self._owner._ele(loc_or_ele)
        self._to_see(ele, center)
        return self._owner

    def _to_see(self, ele, center):
        txt = 'true' if center else 'false'
        ele._run_js(f'this.scrollIntoViewIfNeeded({txt});')
        if center or (center is not False and ele.states.is_covered):
            ele._run_js('''function getWindowScrollTop() {let scroll_top = 0;
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
    def __init__(self, owner):
        """
        :param owner: ChromiumFrame对象
        """
        super().__init__(owner.doc_ele)
        self._t1 = self._t2 = 'this.documentElement'

    def to_see(self, loc_or_ele, center=None):
        ele = self._owner._ele(loc_or_ele)
        self._to_see(ele, center)
        return self._owner
