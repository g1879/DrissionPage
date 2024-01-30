# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Optional

from .._elements.chromium_element import ChromiumElement


class Clicker(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    def __call__(self, by_js: Optional[bool] = False, timeout: float = 1.5, wait_stop: bool = True) -> bool: ...

    def left(self, by_js: Optional[bool] = False, timeout: float = 1.5, wait_stop: bool = True) -> bool: ...

    def right(self) -> None: ...

    def middle(self) -> None: ...

    def at(self, offset_x: float = None, offset_y: float = None, button: str = 'left', count: int = 1) -> None: ...

    def multi(self, times: int = 2) -> None: ...

    def _click(self, client_x: float, client_y: float, button: str = 'left', count: int = 1) -> None: ...
