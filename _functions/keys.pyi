# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Tuple, Union, Any

from .._pages.chromium_base import ChromiumBase


class Keys:
    """特殊按键"""
    CTRL_A: tuple
    CTRL_C: tuple
    CTRL_X: tuple
    CTRL_V: tuple
    CTRL_Z: tuple
    CTRL_Y: tuple

    NULL: str
    CANCEL: str
    HELP: str
    BACKSPACE: str
    TAB: str
    CLEAR: str
    RETURN: str
    ENTER: str
    SHIFT: str
    CONTROL: str
    CTRL: str
    ALT: str
    PAUSE: str
    ESCAPE: str
    SPACE: str
    PAGE_UP: str
    PAGE_DOWN: str
    END: str
    HOME: str
    LEFT: str
    UP: str
    RIGHT: str
    DOWN: str
    INSERT: str
    DELETE: str
    DEL: str
    SEMICOLON: str
    EQUALS: str

    NUMPAD0: str
    NUMPAD1: str
    NUMPAD2: str
    NUMPAD3: str
    NUMPAD4: str
    NUMPAD5: str
    NUMPAD6: str
    NUMPAD7: str
    NUMPAD8: str
    NUMPAD9: str
    MULTIPLY: str
    ADD: str
    SUBTRACT: str
    DECIMAL: str
    DIVIDE: str

    F1: str
    F2: str
    F3: str
    F4: str
    F5: str
    F6: str
    F7: str
    F8: str
    F9: str
    F10: str
    F11: str
    F12: str

    META: str
    COMMAND: str


keyDefinitions: dict = ...
modifierBit: dict = ...


def keys_to_typing(value: Union[str, int, list, tuple]) -> Tuple[int, str]:
    """把要输入的内容连成字符串，去掉其中 ctrl 等键。
        返回的modifier表示是否有按下组合键"""
    ...


def make_input_data(modifiers: int,
                    key: str,
                    key_up: bool = False) -> dict:
    """
    :param modifiers: 功能键设置
    :param key: 按键字符
    :param key_up: 是否提起
    :return: None
    """
    ...


def send_key(page: ChromiumBase, modifier: int, key: str) -> None:
    """发送一个字，在键盘中的字符触发按键，其它直接发送文本
    :param page: 动作所在页面
    :param modifier: 功能键信息
    :param key: 要是输入的按键
    :return: None
    """
    ...


def input_text_or_keys(page: ChromiumBase, text_or_keys: Any) -> None:
    """输入文本，也可输入组合键，组合键用tuple形式输入
    :param page: ChromiumBase对象
    :param text_or_keys: 文本值或按键组合
    :return: self
    """
    ...
