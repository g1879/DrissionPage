# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Tuple, Union

from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._pages.chromium_tab import ChromiumTab
from .._pages.mix_tab import MixTab
from .._pages.web_page import WebPage


class ElementRect(object):
    _ele: ChromiumElement = ...
    def __init__(self, ele: ChromiumElement):
        """
        :param ele: ChromiumElement对象
        """
        ...

    @property
    def corners(self) -> Tuple[Tuple[float, float], ...]:
        """返回元素四个角坐标，顺序：左上、右上、右下、左下，没有大小的元素抛出NoRectError"""
        ...

    @property
    def viewport_corners(self) -> Tuple[Tuple[float, float], ...]:
        """返回元素四个角视口坐标，顺序：左上、右上、右下、左下，没有大小的元素抛出NoRectError"""
        ...

    @property
    def size(self) -> Tuple[float, float]:
        """返回元素大小，格式(宽, 高)"""
        ...

    @property
    def location(self) -> Tuple[float, float]:
        """返回元素左上角的绝对坐标"""
        ...

    @property
    def midpoint(self) -> Tuple[float, float]:
        """返回元素中间点的绝对坐标"""
        ...

    @property
    def click_point(self) -> Tuple[float, float]:
        """返回元素接受点击的点的绝对坐标"""
        ...

    @property
    def viewport_location(self) -> Tuple[float, float]:
        """返回元素左上角在视口中的坐标"""
        ...

    @property
    def viewport_midpoint(self) -> Tuple[float, float]:
        """返回元素中间点在视口中的坐标"""
        ...

    @property
    def viewport_click_point(self) -> Tuple[float, float]:
        """返回元素接受点击的点视口坐标"""
        ...

    @property
    def screen_location(self) -> Tuple[float, float]:
        """返回元素左上角在屏幕上坐标，左上角为(0, 0)"""
        ...

    @property
    def screen_midpoint(self) -> Tuple[float, float]:
        """返回元素中点在屏幕上坐标，左上角为(0, 0)"""
        ...

    @property
    def screen_click_point(self) -> Tuple[float, float]:
        """返回元素中点在屏幕上坐标，左上角为(0, 0)"""
        ...

    @property
    def scroll_position(self) -> Tuple[float, float]:
        """返回滚动条位置，格式：(x, y)"""
        ...

    def _get_viewport_rect(self, quad: str) -> Union[list, None]:
        """按照类型返回在可视窗口中的范围
        :param quad: 方框类型，margin border padding
        :return: 四个角坐标
        """
        ...

    def _get_page_coord(self, x: float, y: float) -> Tuple[float, float]:
        """根据视口坐标获取绝对坐标
        :param x: 视口x坐标
        :param y: 视口y坐标
        :return: 坐标元组
        """
        ...


class TabRect(object):
    def __init__(self, owner: ChromiumBase):
        """
        :param owner: Page对象和Tab对象
        """
        self._owner: Union[ChromiumPage, ChromiumTab, WebPage, MixTab] = ...

    @property
    def window_state(self) -> str:
        """返回窗口状态：normal、fullscreen、maximized、minimized"""
        ...

    @property
    def window_location(self) -> Tuple[int, int]:
        """返回窗口在屏幕上的坐标，左上角为(0, 0)"""
        ...

    @property
    def window_size(self) -> Tuple[int, int]:
        """返回窗口大小"""
        ...

    @property
    def page_location(self) -> Tuple[int, int]:
        """返回页面左上角在屏幕中坐标，左上角为(0, 0)"""
        ...

    @property
    def viewport_location(self) -> Tuple[int, int]:
        """返回视口在屏幕中坐标，左上角为(0, 0)"""
        ...

    @property
    def size(self) -> Tuple[int, int]:
        """返回页面总宽高，格式：(宽, 高)"""
        ...

    @property
    def viewport_size(self) -> Tuple[int, int]:
        """返回视口宽高，不包括滚动条，格式：(宽, 高)"""
        ...

    @property
    def viewport_size_with_scrollbar(self) -> Tuple[int, int]:
        """返回视口宽高，包括滚动条，格式：(宽, 高)"""
        ...

    @property
    def scroll_position(self) -> Tuple[int, int]:
        """返回滚动条位置，格式：(x, y)"""
        ...

    def _get_page_rect(self) -> dict:
        """获取页面范围信息"""
        ...

    def _get_window_rect(self) -> dict:
        """获取窗口范围信息"""
        ...


class FrameRect(object):
    _frame: ChromiumFrame = ...

    def __init__(self, frame: ChromiumFrame):
        """
        :param frame: ChromiumFrame对象
        """
        ...

    @property
    def location(self) -> Tuple[float, float]:
        """返回iframe元素左上角的绝对坐标"""
        ...

    @property
    def viewport_location(self) -> Tuple[float, float]:
        """返回元素在视口中坐标，左上角为(0, 0)"""
        ...

    @property
    def screen_location(self) -> Tuple[float, float]:
        """返回元素左上角在屏幕上坐标，左上角为(0, 0)"""
        ...

    @property
    def size(self) -> Tuple[float, float]:
        """返回frame内页面尺寸，格式：(宽, 高)"""
        ...

    @property
    def viewport_size(self) -> Tuple[float, float]:
        """返回视口宽高，格式：(宽, 高)"""
        ...

    @property
    def corners(self) -> Tuple[Tuple[float, float], ...]:
        """返回元素四个角坐标，顺序：左上、右上、右下、左下"""
        ...

    @property
    def viewport_corners(self) -> Tuple[Tuple[float, float], ...]:
        """返回元素四个角视口坐标，顺序：左上、右上、右下、左下"""
        ...

    @property
    def scroll_position(self) -> Tuple[float, float]:
        """返回滚动条位置，格式：(x, y)"""
        ...
