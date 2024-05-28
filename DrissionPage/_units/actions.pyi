# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Union, Tuple, Any, Literal

from .._base.driver import Driver
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase

KEYS = Literal['NULL', 'CANCEL', 'HELP', 'BACKSPACE', 'BACK_SPACE', 'meta',
'TAB', 'CLEAR', 'RETURN', 'ENTER', 'SHIFT', 'LEFT_SHIFT', 'CONTROL', 'command ',
'CTRL', 'LEFT_CONTROL', 'ALT', 'LEFT_ALT', 'PAUSE', 'ESCAPE', 'SPACE',
'PAGE_UP', 'PAGE_DOWN', 'END', 'HOME', 'LEFT', 'ARROW_LEFT', 'UP',
'ARROW_UP', 'RIGHT', 'ARROW_RIGHT', 'DOWN', 'ARROW_DOWN', 'INSERT',
'DELETE', 'DEL', 'SEMICOLON', 'EQUALS', 'NUMPAD0', 'NUMPAD1', 'NUMPAD2',
'NUMPAD3', 'NUMPAD4', 'NUMPAD5', 'NUMPAD6', 'NUMPAD7', 'NUMPAD8', 'NUMPAD9',
'MULTIPLY', 'ADD', 'SUBTRACT', 'DECIMAL', 'DIVIDE', 'F1', 'F2',
'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'META', 'COMMAND ',
'null', 'cancel', 'help', 'backspace', 'back_space', 'tab', 'clear', 'return', 'enter',
'shift', 'left_shift', 'control', 'ctrl', 'left_control', 'alt', 'left_alt', 'pause',
'escape', 'space', 'page_up', 'page_down', 'end', 'home', 'left', 'arrow_left', 'up',
'arrow_up', 'right', 'arrow_right', 'down', 'arrow_down', 'insert', 'delete', 'del',
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

    def __init__(self, owner: ChromiumBase):
        self.owner: ChromiumBase = ...
        self._dr: Driver = ...
        self.modifier: int = ...
        self.curr_x: int = ...
        self.curr_y: int = ...
        self._holding: str = ...

    def move_to(self, ele_or_loc: Union[ChromiumElement, Tuple[float, float], str],
                offset_x: float = 0, offset_y: float = 0, duration: float = .5) -> Actions: ...

    def move(self, offset_x: float = 0, offset_y: float = 0, duration: float = .5) -> Actions: ...

    def click(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def r_click(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def m_click(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def db_click(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def hold(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def release(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def r_hold(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def r_release(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def m_hold(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def m_release(self, on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def _hold(self, on_ele: Union[ChromiumElement, str] = None, button: str = 'left',
              count: int = 1) -> Actions: ...

    def _release(self, button: str) -> Actions: ...

    def scroll(self, delta_y: int = 0, delta_x: int = 0,
               on_ele: Union[ChromiumElement, str] = None) -> Actions: ...

    def up(self, pixel: int) -> Actions: ...

    def down(self, pixel: int) -> Actions: ...

    def left(self, pixel: int) -> Actions: ...

    def right(self, pixel: int) -> Actions: ...

    def key_down(self, key: Union[KEYS, str]) -> Actions: ...

    def key_up(self, key: Union[KEYS, str]) -> Actions: ...

    def type(self, keys: Union[KEYS, str, list, tuple]) -> Actions: ...

    def input(self, text: Any) -> Actions: ...

    def wait(self, second: float, scope: float = None) -> Actions: ...

    def _get_key_data(self, key: str, action: str) -> dict: ...


def location_to_client(page, lx: int, ly: int) -> tuple: ...
