# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from time import sleep, perf_counter

from ..errors import AlertExistsError
from .._functions.keys import modifierBit, keyDescriptionForString, input_text_or_keys, Keys, keyDefinitions
from .._functions.web import location_in_viewport


class Actions:
    """用于实现动作链的类"""

    def __init__(self, owner):
        """
        :param owner: ChromiumBase对象
        """
        self.owner = owner
        self._dr = owner.driver
        self.modifier = 0  # 修饰符，Alt=1, Ctrl=2, Meta/Command=4, Shift=8
        self.curr_x = 0  # 视口坐标
        self.curr_y = 0
        self._holding = 'left'

    def move_to(self, ele_or_loc, offset_x=0, offset_y=0, duration=.5):
        """鼠标移动到元素中点，或页面上的某个绝对坐标。可设置偏移量
        当带偏移量时，偏移量相对于元素左上角坐标
        :param ele_or_loc: 元素对象、绝对坐标或文本定位符，坐标为tuple(int, int)形式
        :param offset_x: 偏移量x
        :param offset_y: 偏移量y
        :param duration: 拖动用时，传入0即瞬间到达
        :return: self
        """
        is_loc = False
        if isinstance(ele_or_loc, (tuple, list)):
            is_loc = True
            lx = ele_or_loc[0] + offset_x
            ly = ele_or_loc[1] + offset_y
        elif isinstance(ele_or_loc, str) or ele_or_loc._type == 'ChromiumElement':
            ele_or_loc = self.owner(ele_or_loc)
            self.owner.scroll.to_see(ele_or_loc)
            x, y = ele_or_loc.rect.location if offset_x or offset_y else ele_or_loc.rect.midpoint
            lx = x + offset_x
            ly = y + offset_y
        else:
            raise TypeError('ele_or_loc参数只能接受坐标(x, y)或ChromiumElement对象。')

        if not location_in_viewport(self.owner, lx, ly):
            # 把坐标滚动到页面中间
            clientWidth = self.owner.run_js('return document.body.clientWidth;')
            clientHeight = self.owner.run_js('return document.body.clientHeight;')
            self.owner.scroll.to_location(lx - clientWidth // 2, ly - clientHeight // 2)

        # 这样设计为了应付那些不随滚动条滚动的元素
        if is_loc:
            cx, cy = location_to_client(self.owner, lx, ly)
        else:
            x, y = ele_or_loc.rect.viewport_location if offset_x or offset_y \
                else ele_or_loc.rect.viewport_midpoint
            cx = x + offset_x
            cy = y + offset_y

        ox = cx - self.curr_x
        oy = cy - self.curr_y
        self.move(ox, oy, duration)
        return self

    def move(self, offset_x=0, offset_y=0, duration=.5):
        """鼠标相对当前位置移动若干位置
        :param offset_x: 偏移量x
        :param offset_y: 偏移量y
        :param duration: 拖动用时，传入0即瞬间到达
        :return: self
        """
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

    def click(self, on_ele=None):
        """点击鼠标左键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        self._hold(on_ele, 'left').wait(.05)._release('left')
        return self

    def r_click(self, on_ele=None):
        """点击鼠标右键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        self._hold(on_ele, 'right').wait(.05)._release('right')
        return self

    def m_click(self, on_ele=None):
        """点击鼠标中键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        self._hold(on_ele, 'middle').wait(.05)._release('middle')
        return self

    def db_click(self, on_ele=None):
        """双击鼠标左键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        self._hold(on_ele, 'left', 2).wait(.05)._release('left')
        return self

    def hold(self, on_ele=None):
        """按住鼠标左键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        self._hold(on_ele, 'left')
        return self

    def release(self, on_ele=None):
        """释放鼠标左键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._release('left')
        return self

    def r_hold(self, on_ele=None):
        """按住鼠标右键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        self._hold(on_ele, 'right')
        return self

    def r_release(self, on_ele=None):
        """释放鼠标右键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._release('right')
        return self

    def m_hold(self, on_ele=None):
        """按住鼠标中键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        self._hold(on_ele, 'middle')
        return self

    def m_release(self, on_ele=None):
        """释放鼠标中键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: self
        """
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._release('middle')
        return self

    def _hold(self, on_ele=None, button='left', count=1):
        """按下鼠标按键
        :param on_ele: ChromiumElement元素或文本定位符
        :param button: 要按下的按键
        :param count: 点击次数
        :return: self
        """
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._dr.run('Input.dispatchMouseEvent', type='mousePressed', button=button, clickCount=count,
                     x=self.curr_x, y=self.curr_y, modifiers=self.modifier)
        self._holding = button
        return self

    def _release(self, button):
        """释放鼠标按键
        :param button: 要释放的按键
        :return: self
        """
        self._dr.run('Input.dispatchMouseEvent', type='mouseReleased', button=button, clickCount=1,
                     x=self.curr_x, y=self.curr_y, modifiers=self.modifier)
        self._holding = 'left'
        return self

    def scroll(self, delta_y=0, delta_x=0, on_ele=None):
        """滚动鼠标滚轮，可先移动到元素上
        :param delta_y: 滚轮变化值y
        :param delta_x: 滚轮变化值x
        :param on_ele: ChromiumElement元素
        :return: self
        """
        if on_ele:
            self.move_to(on_ele, duration=.2)
        self._dr.run('Input.dispatchMouseEvent', type='mouseWheel', x=self.curr_x, y=self.curr_y,
                     deltaX=delta_x, deltaY=delta_y, modifiers=self.modifier)
        return self

    def up(self, pixel):
        """鼠标向上移动若干像素
        :param pixel: 鼠标移动的像素值
        :return: self
        """
        return self.move(0, -pixel)

    def down(self, pixel):
        """鼠标向下移动若干像素
        :param pixel: 鼠标移动的像素值
        :return: self
        """
        return self.move(0, pixel)

    def left(self, pixel):
        """鼠标向左移动若干像素
        :param pixel: 鼠标移动的像素值
        :return: self
        """
        return self.move(-pixel, 0)

    def right(self, pixel):
        """鼠标向右移动若干像素
        :param pixel: 鼠标移动的像素值
        :return: self
        """
        return self.move(pixel, 0)

    def key_down(self, key):
        """按下键盘上的按键，
        :param key: 使用Keys获取的按键，或'DEL'形式按键名称
        :return: self
        """
        key = getattr(Keys, key.upper(), key)
        if key in ('\ue009', '\ue008', '\ue00a', '\ue03d'):  # 如果上修饰符，添加到变量
            self.modifier |= modifierBit.get(key, 0)
            return self

        data = self._get_key_data(key, 'keyDown')
        data['_ignore'] = AlertExistsError
        self.owner.run_cdp('Input.dispatchKeyEvent', **data)
        return self

    def key_up(self, key):
        """提起键盘上的按键
        :param key: 按键，特殊字符见Keys
        :return: self
        """
        key = getattr(Keys, key.upper(), key)
        if key in ('\ue009', '\ue008', '\ue00a', '\ue03d'):  # 如果上修饰符，添加到变量
            self.modifier ^= modifierBit.get(key, 0)
            return self

        data = self._get_key_data(key, 'keyUp')
        data['_ignore'] = AlertExistsError
        self.owner.run_cdp('Input.dispatchKeyEvent', **data)
        return self

    def type(self, keys):
        """用模拟键盘按键方式输入文本，可输入字符串，也可输入组合键
        :param keys: 要按下的按键，特殊字符和多个文本可用list或tuple传入
        :return: self
        """
        modifiers = []
        for i in keys:
            for character in i:
                if character in keyDefinitions:
                    self.key_down(character)
                    if character in ('\ue009', '\ue008', '\ue00a', '\ue03d'):
                        modifiers.append(character)
                    else:
                        self.key_up(character)

                else:
                    self.owner.run_cdp('Input.dispatchKeyEvent', type='char', text=character)

        for m in modifiers:
            self.key_up(m)
        return self

    def input(self, text):
        """输入文本，也可输入组合键，组合键用tuple形式输入
        :param text: 文本值或按键组合
        :return: self
        """
        input_text_or_keys(self.owner, text)
        return self

    def wait(self, second, scope=None):
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: None
        """
        self.owner.wait(second=second, scope=scope)
        return self

    def _get_key_data(self, key, action):
        """获取用于发送的按键信息
        :param key: 按键
        :param action: 'keyDown' 或 'keyUp'
        :return: 按键信息
        """
        description = keyDescriptionForString(self.modifier, key)
        text = description['text']
        if action != 'keyUp':
            action = 'keyDown' if text else 'rawKeyDown'
        return {'type': action,
                'modifiers': self.modifier,
                'windowsVirtualKeyCode': description['keyCode'],
                'code': description['code'],
                'key': description['key'],
                'text': text,
                'autoRepeat': False,
                'unmodifiedText': text,
                'location': description['location'],
                'isKeypad': description['location'] == 3}


def location_to_client(page, lx, ly):
    """绝对坐标转换为视口坐标"""
    scroll_x = page.run_js('return document.documentElement.scrollLeft;')
    scroll_y = page.run_js('return document.documentElement.scrollTop;')
    return lx - scroll_x, ly - scroll_y
