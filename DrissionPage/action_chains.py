# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from time import sleep

from .commons.keys import modifierBit, keyDescriptionForString
from .commons.web import location_in_viewport


class ActionChains:
    """用于实现动作链的类"""

    def __init__(self, page):
        """
        :param page: ChromiumPage对象
        """
        self.page = page
        self._dr = page.driver
        self.modifier = 0  # 修饰符，Alt=1, Ctrl=2, Meta/Command=4, Shift=8
        self.curr_x = 0  # 视口坐标
        self.curr_y = 0

    def move_to(self, ele_or_loc, offset_x=0, offset_y=0):
        """鼠标移动到元素中点，或页面上的某个绝对坐标。可设置偏移量
        当带偏移量时，偏移量相对于元素左上角坐标
        :param ele_or_loc: 元素对象、绝对坐标或文本定位符，坐标为tuple(int, int)形式
        :param offset_x: 偏移量x
        :param offset_y: 偏移量y
        :return: self
        """
        is_loc = False
        if isinstance(ele_or_loc, (tuple, list)):
            is_loc = True
            lx = ele_or_loc[0] + offset_x
            ly = ele_or_loc[1] + offset_y
        elif isinstance(ele_or_loc, str) or 'ChromiumElement' in str(type(ele_or_loc)):
            ele_or_loc = self.page(ele_or_loc)
            self.page.scroll.to_see(ele_or_loc)
            x, y = ele_or_loc.location if offset_x or offset_y else ele_or_loc.locations.midpoint
            lx = x + offset_x
            ly = y + offset_y
        else:
            raise TypeError('ele_or_loc参数只能接受坐标(x, y)或ChromiumElement对象。')

        if not location_in_viewport(self.page, lx, ly):
            # 把坐标滚动到页面中间
            clientWidth = self.page.run_js('return document.body.clientWidth;')
            clientHeight = self.page.run_js('return document.body.clientHeight;')
            self.page.scroll.to_location(lx - clientWidth // 2, ly - clientHeight // 2)

        # # 这样设计为了应付那些不随滚动条滚动的元素
        if is_loc:
            cx, cy = location_to_client(self.page, lx, ly)
        else:
            x, y = ele_or_loc.locations.viewport_location if offset_x or offset_y \
                else ele_or_loc.locations.viewport_midpoint
            cx = x + offset_x
            cy = y + offset_y

        self._dr.Input.dispatchMouseEvent(type='mouseMoved', x=cx, y=cy, modifiers=self.modifier)
        self.curr_x = cx
        self.curr_y = cy
        return self

    def move(self, offset_x=0, offset_y=0):
        """鼠标相对当前位置移动若干位置
        :param offset_x: 偏移量x
        :param offset_y: 偏移量y
        :return: self
        """
        self.curr_x += offset_x
        self.curr_y += offset_y
        self._dr.Input.dispatchMouseEvent(type='mouseMoved', x=self.curr_x, y=self.curr_y, modifiers=self.modifier)
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
            self.move_to(on_ele)
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
            self.move_to(on_ele)
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
            self.move_to(on_ele)
        self._release('middle')
        return self

    def _hold(self, on_ele=None, button='left'):
        """按下鼠标按键
        :param on_ele: ChromiumElement元素或文本定位符
        :param button: 要按下的按键
        :return: self
        """
        if on_ele:
            self.move_to(on_ele)
        self._dr.Input.dispatchMouseEvent(type='mousePressed', button=button, clickCount=1,
                                          x=self.curr_x, y=self.curr_y, modifiers=self.modifier)
        return self

    def _release(self, button):
        """释放鼠标按键
        :param button: 要释放的按键
        :return: self
        """
        self._dr.Input.dispatchMouseEvent(type='mouseReleased', button=button, clickCount=1,
                                          x=self.curr_x, y=self.curr_y, modifiers=self.modifier)
        return self

    def scroll(self, delta_x=0, delta_y=0, on_ele=None):
        """滚动鼠标滚轮，可先移动到元素上
        :param delta_x: 滚轮变化值x
        :param delta_y: 滚轮变化值y
        :param on_ele: ChromiumElement元素
        :return: self
        """
        if on_ele:
            self.move_to(on_ele)
        self._dr.Input.dispatchMouseEvent(type='mouseWheel', x=self.curr_x, y=self.curr_y,
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
        """按下键盘上的按键
        :param key: 按键，特殊字符见Keys
        :return: self
        """
        if key in ('\ue009', '\ue008', '\ue00a', '\ue03d'):  # 如果上修饰符，添加到变量
            self.modifier |= modifierBit.get(key, 0)
            return self

        data = self._get_key_data(key, 'keyDown')
        self.page.run_cdp('Input.dispatchKeyEvent', **data)
        return self

    def key_up(self, key):
        """提起键盘上的按键
        :param key: 按键，特殊字符见Keys
        :return: self
        """
        if key in ('\ue009', '\ue008', '\ue00a', '\ue03d'):  # 如果上修饰符，添加到变量
            self.modifier ^= modifierBit.get(key, 0)
            return self

        data = self._get_key_data(key, 'keyUp')
        self.page.run_cdp('Input.dispatchKeyEvent', **data)
        return self

    def type(self, text):
        """输入文本
        :param text: 要输入的文本
        :return: self
        """
        for i in text:
            self.key_down(i)
            sleep(.05)
            self.key_up(i)
        return self

    def wait(self, second):
        """等待若干秒"""
        sleep(second)
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
