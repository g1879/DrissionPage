# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from time import sleep, perf_counter

from .._functions.keys import modifierBit, make_input_data, input_text_or_keys, Keys
from .._functions.settings import Settings as _S
from .._functions.web import location_in_viewport


class Actions:

    def __init__(self, owner):
        self.owner = owner
        self._dr = owner.driver
        self.modifier = 0  # 修饰符，Alt=1, Ctrl=2, Meta/Command=4, Shift=8
        self.curr_x = 0  # 视口坐标
        self.curr_y = 0
        self._holding = 'left'

    def move_to(self, ele_or_loc, offset_x=None, offset_y=None, duration=.5):
        is_loc = False
        mid_point = offset_x == offset_y is None
        if offset_x is None:
            offset_x = 0
        if offset_y is None:
            offset_y = 0
        if isinstance(ele_or_loc, (tuple, list)):
            is_loc = True
            lx = ele_or_loc[0] + offset_x
            ly = ele_or_loc[1] + offset_y
        elif isinstance(ele_or_loc, str) or ele_or_loc._type == 'ChromiumElement':
            ele_or_loc = self.owner(ele_or_loc)
            self.owner.scroll.to_see(ele_or_loc)
            x, y = ele_or_loc.rect.midpoint if mid_point else ele_or_loc.rect.location
            lx = x + offset_x
            ly = y + offset_y
        else:
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'ele_or_loc',
                                           ALLOW_TYPE=_S._lang.ELE_LOC_FORMAT, CURR_VAL=ele_or_loc))

        if not location_in_viewport(self.owner, lx, ly):
            # 把坐标滚动到页面中间
            clientWidth = self.owner._run_js('return document.body.clientWidth;')
            clientHeight = self.owner._run_js('return document.body.clientHeight;')
            self.owner.scroll.to_location(lx - clientWidth // 2, ly - clientHeight // 2)

        # 这样设计为了应付那些不随滚动条滚动的元素
        if is_loc:
            cx, cy = location_to_client(self.owner, lx, ly)
        else:
            x, y = ele_or_loc.rect.viewport_midpoint if mid_point else ele_or_loc.rect.viewport_location
            cx = x + offset_x
            cy = y + offset_y

        ox = cx - self.curr_x
        oy = cy - self.curr_y
        self.move(ox, oy, duration)
        return self

    def move(self, offset_x=0, offset_y=0, duration=.5):
        duration = .02 if duration < .02 else duration
        num = int(duration * 50)

        points = [(self.curr_x + i * (offset_x / num),
                   self.curr_y + i * (offset_y / num)) for i in range(1, num)]
        points.append((self.curr_x + offset_x, self.curr_y + offset_y))

        for x, y in points:
            t = perf_counter()
            self.curr_x = x
            self.curr_y = y
            self._dr.run('Input.dispatchMouseEvent', type='mouseMoved', button=self._holding,
                         x=self.curr_x, y=self.curr_y, modifiers=self.modifier)
            ss = .02 - perf_counter() + t
            if ss > 0:
                sleep(ss)

        return self

    def click(self, on_ele=None, times=1):
        self._hold(on_ele, 'left', times).wait(.05)._release('left')
        return self

    def r_click(self, on_ele=None, times=1):
        self._hold(on_ele, 'right', times).wait(.05)._release('right')
        return self

    def m_click(self, on_ele=None, times=1):
        self._hold(on_ele, 'middle', times).wait(.05)._release('middle')
        return self

    def hold(self, on_ele=None):
        self._hold(on_ele, 'left')
        return self

    def release(self, on_ele=None):
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._release('left')
        return self

    def r_hold(self, on_ele=None):
        self._hold(on_ele, 'right')
        return self

    def r_release(self, on_ele=None):
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._release('right')
        return self

    def m_hold(self, on_ele=None):
        self._hold(on_ele, 'middle')
        return self

    def m_release(self, on_ele=None):
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._release('middle')
        return self

    def _hold(self, on_ele=None, button='left', count=1):
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._dr.run('Input.dispatchMouseEvent', type='mousePressed', button=button, clickCount=count,
                     x=self.curr_x, y=self.curr_y, modifiers=self.modifier)
        self._holding = button
        return self

    def _release(self, button):
        self._dr.run('Input.dispatchMouseEvent', type='mouseReleased', button=button, clickCount=1,
                     x=self.curr_x, y=self.curr_y, modifiers=self.modifier)
        self._holding = 'left'
        return self

    def scroll(self, delta_y=0, delta_x=0, on_ele=None):
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._dr.run('Input.dispatchMouseEvent', type='mouseWheel', x=self.curr_x, y=self.curr_y,
                     deltaX=delta_x, deltaY=delta_y, modifiers=self.modifier)
        return self

    def up(self, pixel):
        return self.move(0, -pixel)

    def down(self, pixel):
        return self.move(0, pixel)

    def left(self, pixel):
        return self.move(-pixel, 0)

    def right(self, pixel):
        return self.move(pixel, 0)

    def key_down(self, key):
        key = getattr(Keys, key.upper(), key)
        if key in ('\ue009', '\ue008', '\ue00a', '\ue03d'):  # 如果上修饰符，添加到变量
            self.modifier |= modifierBit.get(key, 0)
            return self

        data = make_input_data(self.modifier, key, False)
        if not data:
            raise ValueError(_S._lang.join(_S._lang.NO_SUCH_KEY_, key))
        self.owner._run_cdp('Input.dispatchKeyEvent', **data)
        return self

    def key_up(self, key):
        key = getattr(Keys, key.upper(), key)
        if key in ('\ue009', '\ue008', '\ue00a', '\ue03d'):  # 如果上修饰符，添加到变量
            self.modifier ^= modifierBit.get(key, 0)
            return self

        data = make_input_data(self.modifier, key, True)
        if not data:
            raise ValueError(_S._lang.join(_S._lang.NO_SUCH_KEY_, key))
        self.owner._run_cdp('Input.dispatchKeyEvent', **data)
        return self

    def type(self, keys, interval=0):
        modifiers = []
        if not isinstance(keys, (str, tuple, list)):
            keys = str(keys)
        for i in keys:
            for character in i:
                if character in ('\ue009', '\ue008', '\ue00a', '\ue03d'):
                    self.modifier |= modifierBit.get(character, 0)
                    modifiers.append(character)
                data = make_input_data(self.modifier, character, False)
                if data:
                    self.owner._run_cdp('Input.dispatchKeyEvent', **data)
                    if character not in ('\ue009', '\ue008', '\ue00a', '\ue03d'):
                        data['type'] = 'keyUp'
                        self.owner._run_cdp('Input.dispatchKeyEvent', **data)

                else:
                    self.owner._run_cdp('Input.dispatchKeyEvent', type='char', text=character)
                sleep(interval)

        for m in modifiers:
            self.key_up(m)
        return self

    def input(self, text):
        input_text_or_keys(self.owner, text)
        return self

    def wait(self, second, scope=None):
        self.owner.wait(second=second, scope=scope)
        return self


def location_to_client(page, lx, ly):
    scroll_x = page._run_js('return document.documentElement.scrollLeft;')
    scroll_y = page._run_js('return document.documentElement.scrollTop;')
    return lx - scroll_x, ly - scroll_y
