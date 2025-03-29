# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union, Tuple, Any, Literal

from .._base.driver import Driver
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase

KEYS = Literal['NULL', 'CANCEL', 'HELP', 'BACKSPACE', 'meta',
'TAB', 'CLEAR', 'RETURN', 'ENTER', 'SHIFT', 'CONTROL', 'command ',
'CTRL', 'ALT', 'PAUSE', 'ESCAPE', 'SPACE',
'PAGE_UP', 'PAGE_DOWN', 'END', 'HOME', 'LEFT', 'UP',
'RIGHT', 'DOWN', 'INSERT',
'DELETE', 'DEL', 'SEMICOLON', 'EQUALS', 'NUMPAD0', 'NUMPAD1', 'NUMPAD2',
'NUMPAD3', 'NUMPAD4', 'NUMPAD5', 'NUMPAD6', 'NUMPAD7', 'NUMPAD8', 'NUMPAD9',
'MULTIPLY', 'ADD', 'SUBTRACT', 'DECIMAL', 'DIVIDE', 'F1', 'F2',
'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'META', 'COMMAND ',
'null', 'cancel', 'help', 'backspace', 'tab', 'clear', 'return', 'enter',
'shift', 'control', 'ctrl', 'alt', 'pause',
'escape', 'space', 'page_up', 'page_down', 'end', 'home', 'left', 'up',
'right', 'down', 'insert', 'delete', 'del',
'semicolon', 'equals', 'numpad0', 'numpad1', 'numpad2', 'numpad3', 'numpad4', 'numpad5',
'numpad6', 'numpad7', 'numpad8', 'numpad9', 'multiply', 'add', 'subtract', 'decimal',
'divide', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
'\ue000', '\ue002', '\ue003', '\ue004', '\ue005', '\ue006', '\ue007', '\ue008', '\ue009',
'\ue009', '\ue00a', '\ue00b', '\ue00c', '\ue00d', '\ue00e', '\ue00f', '\ue010', '\ue011',
'\ue012', '\ue013', '\ue014', '\ue015', '\ue016', '\ue017', '\ue017', '\ue018', '\ue019',
'\ue01a', '\ue01b', '\ue01c', '\ue01d', '\ue01e', '\ue01f', '\ue020', '\ue021', '\ue022',
'\ue023', '\ue024', '\ue025', '\ue027', '\ue028', '\ue029', '\ue031', '\ue032', '\ue033', '\ue034',
'\ue035', '\ue036', '\ue037', '\ue038', '\ue039', '\ue03a', '\ue03b', '\ue03c', '\ue03d', '\ue03d',
'`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'q', 'w',
'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\', 'a', 's', 'd', 'f',
'g', 'h', 'j', 'k', 'l', ';', '\'', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',',
'.', '/', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+',
'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', 'A', 'S', 'D',
'F', 'G', 'H', 'J', 'K', 'L', ':', '"', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?'
]


class Actions:
    """用于实现动作链的类"""

    owner: ChromiumBase = ...
    _dr: Driver = ...
    modifier: int = ...
    curr_x: float = ...
    curr_y: float = ...
    _holding: str = ...

    def __init__(self, owner: ChromiumBase):
        """
        :param owner: ChromiumBase对象
        """
        ...

    def move_to(self, ele_or_loc: Union[ChromiumElement, Tuple[float, float], str],
                offset_x: float = 0, offset_y: float = 0, duration: float = .5) -> Actions:
        """鼠标移动到元素中点，或页面上的某个绝对坐标。可设置偏移量
        当带偏移量时，偏移量相对于元素左上角坐标
        :param ele_or_loc: 元素对象、绝对坐标或文本定位符，坐标为tuple(int, int)形式
        :param offset_x: 偏移量x
        :param offset_y: 偏移量y
        :param duration: 拖动用时，传入0即瞬间到达
        :return: 动作链对象本身
        """
        ...

    def move(self, offset_x: float = 0, offset_y: float = 0, duration: float = .5) -> Actions:
        """鼠标相对当前位置移动若干位置
        :param offset_x: 偏移量x
        :param offset_y: 偏移量y
        :param duration: 拖动用时，传入0即瞬间到达
        :return: 动作链对象本身
        """
        ...

    def click(self, on_ele: Union[ChromiumElement, str] = None, times: int = 1) -> Actions:
        """点击鼠标左键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :param times: 点击次数
        :return: 动作链对象本身
        """
        ...

    def r_click(self, on_ele: Union[ChromiumElement, str] = None, times: int = 1) -> Actions:
        """点击鼠标右键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :param times: 点击次数
        :return: 动作链对象本身
        """
        ...

    def m_click(self, on_ele: Union[ChromiumElement, str] = None, times: int = 1) -> Actions:
        """点击鼠标中键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :param times: 点击次数
        :return: 动作链对象本身
        """
        ...

    def hold(self, on_ele: Union[ChromiumElement, str] = None) -> Actions:
        """按住鼠标左键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: 动作链对象本身
        """
        ...

    def release(self, on_ele: Union[ChromiumElement, str] = None) -> Actions:
        """释放鼠标左键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: 动作链对象本身
        """
        ...

    def r_hold(self, on_ele: Union[ChromiumElement, str] = None) -> Actions:
        """按住鼠标右键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: 动作链对象本身
        """
        ...

    def r_release(self, on_ele: Union[ChromiumElement, str] = None) -> Actions:
        """释放鼠标右键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: 动作链对象本身
        """
        ...

    def m_hold(self, on_ele: Union[ChromiumElement, str] = None) -> Actions:
        """按住鼠标中键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: 动作链对象本身
        """
        ...

    def m_release(self, on_ele: Union[ChromiumElement, str] = None) -> Actions:
        """释放鼠标中键，可先移动到元素上
        :param on_ele: ChromiumElement元素或文本定位符
        :return: 动作链对象本身
        """
        ...

    def _hold(self,
              on_ele: Union[ChromiumElement, str] = None,
              button: str = 'left',
              count: int = 1) -> Actions:
        """按下鼠标按键
        :param on_ele: ChromiumElement元素或文本定位符
        :param button: 要按下的按键
        :param count: 点击次数
        :return: 动作链对象本身
        """
        ...

    def _release(self, button: str) -> Actions:
        """释放鼠标按键
        :param button: 要释放的按键
        :return: 动作链对象本身
        """
        ...

    def scroll(self, delta_y: int = 0, delta_x: int = 0,
               on_ele: Union[ChromiumElement, str] = None) -> Actions:
        """滚动鼠标滚轮，可先移动到元素上
        :param delta_y: 滚轮变化值y
        :param delta_x: 滚轮变化值x
        :param on_ele: ChromiumElement元素
        :return: 动作链对象本身
        """
        ...

    def up(self, pixel: int) -> Actions:
        """鼠标向上移动若干像素
        :param pixel: 鼠标移动的像素值
        :return: 动作链对象本身
        """
        ...

    def down(self, pixel: int) -> Actions:
        """鼠标向下移动若干像素
        :param pixel: 鼠标移动的像素值
        :return: 动作链对象本身
        """
        ...

    def left(self, pixel: int) -> Actions:
        """鼠标向左移动若干像素
        :param pixel: 鼠标移动的像素值
        :return: 动作链对象本身
        """
        ...

    def right(self, pixel: int) -> Actions:
        """鼠标向右移动若干像素
        :param pixel: 鼠标移动的像素值
        :return: 动作链对象本身
        """
        ...

    def key_down(self, key: Union[KEYS, str]) -> Actions:
        """按下键盘上的按键，
        :param key: 使用Keys获取的按键，或 'DEL' 形式按键名称
        :return: 动作链对象本身
        """
        ...

    def key_up(self, key: Union[KEYS, str]) -> Actions:
        """提起键盘上的按键
        :param key: 按键，特殊字符见Keys
        :return: 动作链对象本身
        """
        ...

    def type(self,
             keys: Union[KEYS, str, list, tuple],
             interval: float = 0) -> Actions:
        """用模拟键盘按键方式输入文本，可输入字符串，也可输入组合键
        :param keys: 要按下的按键，特殊字符和多个文本可用list或tuple传入
        :param interval: 每个字符之间间隔时间
        :return: 动作链对象本身
        """
        ...

    def input(self, text: Any) -> Actions:
        """输入文本，也可输入组合键，组合键用tuple形式输入
        :param text: 文本值或按键组合
        :return: 动作链对象本身
        """
        ...

    def wait(self, second: float, scope: float = None) -> Actions:
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: None
        """
        ...


def location_to_client(page: ChromiumBase, lx: int, ly: int) -> tuple:
    """绝对坐标转换为视口坐标
    :param page: 页面对象
    :param lx: 绝对坐标x
    :param ly: 绝对坐标y
    :return: 视口坐标元组
    """
    ...
