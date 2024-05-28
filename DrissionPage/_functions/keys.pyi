# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Tuple, Dict, Union, Any

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
    BACK_SPACE: str
    TAB: str
    CLEAR: str
    RETURN: str
    ENTER: str
    SHIFT: str
    LEFT_SHIFT: str
    CONTROL: str
    CTRL: str
    LEFT_CONTROL: str
    ALT: str
    LEFT_ALT: str
    PAUSE: str
    ESCAPE: str
    SPACE: str
    PAGE_UP: str
    PAGE_DOWN: str
    END: str
    HOME: str
    LEFT: str
    ARROW_LEFT: str
    UP: str
    ARROW_UP: str
    RIGHT: str
    ARROW_RIGHT: str
    DOWN: str
    ARROW_DOWN: str
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


def keys_to_typing(value: Union[str, int, list, tuple]) -> Tuple[int, str]: ...


def keyDescriptionForString(_modifiers: int, keyString: str) -> Dict: ...


def send_key(page: ChromiumBase, modifier: int, key: str) -> None: ...


def input_text_or_keys(page: ChromiumBase, text_or_keys: Any) -> None: ...
