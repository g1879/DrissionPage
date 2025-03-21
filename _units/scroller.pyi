# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union

from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._pages.chromium_tab import ChromiumTab
from .._pages.mix_tab import MixTab
from .._pages.web_page import WebPage


class Scroller(object):
    _owner: Union[ChromiumBase, ChromiumElement] = ...
    _t1: str = ...
    _t2: str = ...
    _wait_complete: bool = ...

    def __init__(self, owner: Union[ChromiumBase, ChromiumElement]):
        """
        :param owner: 元素对象或页面对象
        """
        ...

    def __call__(self, pixel: int = 300) -> None:
        """向下滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def to_top(self) -> None:
        """滚动到顶端，水平位置不变"""
        ...

    def to_bottom(self) -> None:
        """滚动到底端，水平位置不变"""
        ...

    def to_half(self) -> None:
        """滚动到垂直中间位置，水平位置不变"""
        ...

    def to_rightmost(self) -> None:
        """滚动到最右边，垂直位置不变"""
        ...

    def to_leftmost(self) -> None:
        """滚动到最左边，垂直位置不变"""
        ...

    def to_location(self, x: int, y: int) -> None:
        """滚动到指定位置
        :param x: 水平距离
        :param y: 垂直距离
        :return: None
        """
        ...

    def up(self, pixel: int = 300) -> None:
        """向上滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def down(self, pixel: int = 300) -> None:
        """向下滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def left(self, pixel: int = 300) -> None:
        """向左滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def right(self, pixel: int = 300) -> None:
        """向右滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def _run_js(self, js: str): ...

    def _wait_scrolled(self) -> None:
        """等待滚动结束"""
        ...


class ElementScroller(Scroller):
    _owner: ChromiumElement = ...

    def __init__(self, owner: ChromiumElement):
        """
        :param owner: 元素对象
        """
        ...

    def to_see(self, center: Union[bool, None] = None) -> ChromiumElement:
        """滚动页面直到元素可见
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        ...

    def to_center(self) -> ChromiumElement:
        """元素尽量滚动到视口中间"""
        ...

    def to_top(self) -> ChromiumElement:
        """滚动到顶端，水平位置不变"""
        ...

    def to_bottom(self) -> ChromiumElement:
        """滚动到底端，水平位置不变"""
        ...

    def to_half(self) -> ChromiumElement:
        """滚动到垂直中间位置，水平位置不变"""
        ...

    def to_rightmost(self) -> ChromiumElement:
        """滚动到最右边，垂直位置不变"""
        ...

    def to_leftmost(self) -> ChromiumElement:
        """滚动到最左边，垂直位置不变"""
        ...

    def to_location(self, x: int, y: int) -> ChromiumElement:
        """滚动到指定位置
        :param x: 水平距离
        :param y: 垂直距离
        :return: None
        """
        ...

    def up(self, pixel: int = 300) -> ChromiumElement:
        """向上滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def down(self, pixel: int = 300) -> ChromiumElement:
        """向下滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def left(self, pixel: int = 300) -> ChromiumElement:
        """向左滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def right(self, pixel: int = 300) -> ChromiumElement:
        """向右滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...


class PageScroller(Scroller):
    _owner: Union[ChromiumBase, ChromiumElement] = ...

    def __init__(self, owner: Union[ChromiumBase, ChromiumElement]):
        """
        :param owner: 页面对象
        """
        ...

    def to_see(self,
               loc_or_ele: Union[str, tuple, ChromiumElement],
               center: Union[bool, None] = None) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """滚动页面直到元素可见
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        ...

    def to_top(self) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """滚动到顶端，水平位置不变"""
        ...

    def to_bottom(self) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """滚动到底端，水平位置不变"""
        ...

    def to_half(self) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """滚动到垂直中间位置，水平位置不变"""
        ...

    def to_rightmost(self) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """滚动到最右边，垂直位置不变"""
        ...

    def to_leftmost(self) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """滚动到最左边，垂直位置不变"""
        ...

    def to_location(self, x: int, y: int) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """滚动到指定位置
        :param x: 水平距离
        :param y: 垂直距离
        :return: None
        """
        ...

    def up(self, pixel: int = 300) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """向上滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def down(self, pixel: int = 300) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """向下滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def left(self, pixel: int = 300) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """向左滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def right(self, pixel: int = 300) -> Union[ChromiumTab, MixTab, ChromiumPage, WebPage]:
        """向右滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def _to_see(self, ele: ChromiumElement, center: Union[bool, None]) -> None:
        """执行滚动页面直到元素可见
        :param ele: 元素对象
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        ...


class FrameScroller(PageScroller):
    _owner: ChromiumElement = ...

    def __init__(self, owner: ChromiumFrame): ...

    def to_see(self,
               loc_or_ele: Union[str, tuple, ChromiumElement],
               center: Union[bool, None] = None) -> ChromiumFrame:
        """滚动页面直到元素可见
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :param center: 是否尽量滚动到页面正中，为None时如果被遮挡，则滚动到页面正中
        :return: None
        """
        ...

    def to_top(self) -> ChromiumFrame:
        """滚动到顶端，水平位置不变"""
        ...

    def to_bottom(self) -> ChromiumFrame:
        """滚动到底端，水平位置不变"""
        ...

    def to_half(self) -> ChromiumFrame:
        """滚动到垂直中间位置，水平位置不变"""
        ...

    def to_rightmost(self) -> ChromiumFrame:
        """滚动到最右边，垂直位置不变"""
        ...

    def to_leftmost(self) -> ChromiumFrame:
        """滚动到最左边，垂直位置不变"""
        ...

    def to_location(self, x: int, y: int) -> ChromiumFrame:
        """滚动到指定位置
        :param x: 水平距离
        :param y: 垂直距离
        :return: None
        """
        ...

    def up(self, pixel: int = 300) -> ChromiumFrame:
        """向上滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def down(self, pixel: int = 300) -> ChromiumFrame:
        """向下滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def left(self, pixel: int = 300) -> ChromiumFrame:
        """向左滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...

    def right(self, pixel: int = 300) -> ChromiumFrame:
        """向右滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        ...
