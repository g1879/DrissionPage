# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""

from typing import Tuple, Union

from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._pages.chromium_tab import ChromiumTab, WebPageTab
from .._pages.web_page import WebPage


class ElementRect(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    @property
    def size(self) -> Tuple[float, float]: ...

    @property
    def location(self) -> Tuple[float, float]: ...

    @property
    def midpoint(self) -> Tuple[float, float]: ...

    @property
    def click_point(self) -> Tuple[float, float]: ...

    @property
    def viewport_location(self) -> Tuple[float, float]: ...

    @property
    def viewport_midpoint(self) -> Tuple[float, float]: ...

    @property
    def viewport_click_point(self) -> Tuple[float, float]: ...

    @property
    def screen_location(self) -> Tuple[float, float]: ...

    @property
    def screen_midpoint(self) -> Tuple[float, float]: ...

    @property
    def screen_click_point(self) -> Tuple[float, float]: ...

    @property
    def corners(self) -> Tuple[Tuple[float, float], ...]: ...

    @property
    def viewport_corners(self) -> Tuple[Tuple[float, float], ...]: ...

    def _get_viewport_rect(self, quad: str) -> Union[list, None]: ...

    def _get_page_coord(self, x: float, y: float) -> Tuple[float, float]: ...


class TabRect(object):
    def __init__(self, owner: ChromiumBase):
        self._owner: Union[ChromiumPage, ChromiumTab, WebPage, WebPageTab] = ...

    @property
    def window_state(self) -> str: ...

    @property
    def window_location(self) -> Tuple[int, int]: ...

    @property
    def page_location(self) -> Tuple[int, int]: ...

    @property
    def viewport_location(self) -> Tuple[int, int]: ...

    @property
    def window_size(self) -> Tuple[int, int]: ...

    @property
    def size(self) -> Tuple[int, int]: ...

    @property
    def viewport_size(self) -> Tuple[int, int]: ...

    @property
    def viewport_size_with_scrollbar(self) -> Tuple[int, int]: ...

    def _get_page_rect(self) -> dict: ...

    def _get_window_rect(self) -> dict: ...


class FrameRect(object):
    def __init__(self, frame: ChromiumFrame):
        self._frame: ChromiumFrame = ...

    @property
    def location(self) -> Tuple[float, float]: ...

    @property
    def viewport_location(self) -> Tuple[float, float]: ...

    @property
    def screen_location(self) -> Tuple[float, float]: ...

    @property
    def size(self) -> Tuple[float, float]: ...

    @property
    def viewport_size(self) -> Tuple[float, float]: ...

    @property
    def corners(self) -> Tuple[Tuple[float, float], ...]: ...

    @property
    def viewport_corners(self) -> Tuple[Tuple[float, float], ...]: ...
