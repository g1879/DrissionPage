# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union, Tuple, List, Optional, Literal

from .._base.chromium import Chromium
from .._elements.chromium_element import ShadowRoot, ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame


class ElementStates(object):
    _ele: ChromiumElement = ...

    def __init__(self, ele: ChromiumElement):
        """
        :param ele: ChromiumElement
        """
        ...

    @property
    def is_selected(self) -> bool:
        """返回列表元素是否被选择"""
        ...

    @property
    def is_checked(self) -> bool:
        """返回元素是否被选择"""
        ...

    @property
    def is_displayed(self) -> bool:
        """返回元素是否显示"""
        ...

    @property
    def is_enabled(self) -> bool:
        """返回元素是否可用"""
        ...

    @property
    def is_alive(self) -> bool:
        """返回元素是否仍在DOM中"""
        ...

    @property
    def is_in_viewport(self) -> bool:
        """返回元素是否出现在视口中，以元素click_point为判断"""
        ...

    @property
    def is_whole_in_viewport(self) -> bool:
        """返回元素是否整个都在视口内"""
        ...

    @property
    def is_covered(self) -> Union[Literal[False], int]:
        """返回元素是否被覆盖，与是否在视口中无关，如被覆盖返回覆盖元素的backend id，否则返回False"""
        ...

    @property
    def is_clickable(self) -> bool:
        """返回元素是否可被模拟点击，从是否有大小、是否可用、是否显示、是否响应点击判断，不判断是否被遮挡"""
        ...

    @property
    def has_rect(self) -> Union[Literal[False], List[Tuple[float, float]]]:
        """返回元素是否拥有位置和大小，没有返回False，有返回四个角在页面中坐标组成的列表"""
        ...


class ShadowRootStates(object):
    _ele: ShadowRoot = ...

    def __init__(self, ele: ShadowRoot):
        """
        :param ele: ChromiumElement
        """
        ...

    @property
    def is_enabled(self) -> bool:
        """返回元素是否可用"""
        ...

    @property
    def is_alive(self) -> bool:
        """返回元素是否仍在DOM中"""
        ...


class BrowserStates(object):
    _browser: Chromium = ...
    _incognito: Optional[bool] = ...

    def __init__(self, browser: Chromium):
        """
        :param browser: Chromium对象
        """
        ...

    @property
    def is_alive(self) -> bool:
        """返回浏览器是否仍可用"""
        ...

    @property
    def is_headless(self) -> bool:
        """返回浏览器是否无头模式"""
        ...

    @property
    def is_existed(self) -> bool:
        """返回浏览器是否接管的"""
        ...

    @property
    def is_incognito(self) -> bool:
        """返回浏览器是否无痕模式"""
        ...


class PageStates(object):
    _owner: ChromiumBase = ...

    def __init__(self, owner: ChromiumBase):
        """
        :param owner: ChromiumBase对象
        """
        ...

    @property
    def is_loading(self) -> bool:
        """返回页面是否在加载状态"""
        ...

    @property
    def is_alive(self) -> bool:
        """返回页面对象是否仍然可用"""
        ...

    @property
    def ready_state(self) -> Optional[str]:
        """返回当前页面加载状态，'connecting' 'loading' 'interactive' 'complete'"""
        ...

    @property
    def has_alert(self) -> bool:
        """返回当前页面是否存在弹窗"""
        ...

    @property
    def is_headless(self) -> bool:
        """返回浏览器是否无头模式"""
        ...

    @property
    def is_existed(self) -> bool:
        """返回浏览器是否接管的"""
        ...

    @property
    def is_incognito(self) -> bool:
        """返回浏览器是否无痕模式"""
        ...


class FrameStates(object):
    _frame: ChromiumFrame = ...

    def __init__(self, frame: ChromiumFrame):
        """
        :param frame: ChromiumFrame对象
        """
        ...

    @property
    def is_loading(self) -> bool:
        """返回页面是否在加载状态"""
        ...

    @property
    def is_alive(self) -> bool:
        """返回frame元素是否可用，且里面仍挂载有frame"""
        ...

    @property
    def ready_state(self) -> str:
        """返回加载状态"""
        ...

    @property
    def is_displayed(self) -> bool:
        """返回iframe是否显示"""
        ...

    @property
    def has_alert(self) -> bool:
        """返回当前页面是否存在弹窗"""
        ...
