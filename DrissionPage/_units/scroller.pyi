# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Union

from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase


class Scroller(object):
    def __init__(self, page_or_ele: Union[ChromiumBase, ChromiumElement]):
        self.t1: str = ...
        self.t2: str = ...
        self._driver: Union[ChromiumBase, ChromiumElement] = ...
        self._wait_complete: bool = ...

    def _run_js(self, js: str): ...

    def to_top(self) -> None: ...

    def to_bottom(self) -> None: ...

    def to_half(self) -> None: ...

    def to_rightmost(self) -> None: ...

    def to_leftmost(self) -> None: ...

    def to_location(self, x: int, y: int) -> None: ...

    def up(self, pixel: int = 300) -> None: ...

    def down(self, pixel: int = 300) -> None: ...

    def left(self, pixel: int = 300) -> None: ...

    def right(self, pixel: int = 300) -> None: ...

    def _wait_scrolled(self) -> None: ...


class ElementScroller(Scroller):

    def to_see(self, center: Union[bool, None] = None) -> None: ...

    def to_center(self) -> None: ...


class PageScroller(Scroller):
    def __init__(self, owner: ChromiumBase): ...

    def to_see(self, loc_or_ele: Union[str, tuple, ChromiumElement], center: Union[bool, None] = None) -> None: ...

    def _to_see(self, ele: ChromiumElement, center: Union[bool, None]) -> None: ...


class FrameScroller(PageScroller):
    def __init__(self, frame):
        """
        :param frame: ChromiumFrame对象
        """
        self._driver = frame.doc_ele
        self.t1 = self.t2 = 'this.documentElement'
        self._wait_complete = False

    def to_see(self, loc_or_ele, center=None):
        """滚动页面直到元素可见
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        ele = loc_or_ele if isinstance(loc_or_ele, ChromiumElement) else self._driver._ele(loc_or_ele)
        self._to_see(ele, center)
