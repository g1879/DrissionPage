# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Union, Tuple, List, Optional, Literal

from .._elements.chromium_element import ShadowRoot, ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame


class ElementStates(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    @property
    def is_selected(self) -> bool: ...

    @property
    def is_checked(self) -> bool: ...

    @property
    def is_displayed(self) -> bool: ...

    @property
    def is_enabled(self) -> bool: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def is_in_viewport(self) -> bool: ...

    @property
    def is_whole_in_viewport(self) -> bool: ...

    @property
    def is_covered(self) -> Union[Literal[False], int]: ...

    @property
    def is_clickable(self) -> bool: ...

    @property
    def has_rect(self) -> Union[Literal[False], List[Tuple[float, float]]]: ...


class ShadowRootStates(object):
    def __init__(self, ele: ShadowRoot):
        """
        :param ele: ChromiumElement
        """
        self._ele: ShadowRoot = ...

    @property
    def is_enabled(self) -> bool: ...

    @property
    def is_alive(self) -> bool: ...


class PageStates(object):
    def __init__(self, owner: ChromiumBase):
        self._owner: ChromiumBase = ...

    @property
    def is_loading(self) -> bool: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def ready_state(self) -> Optional[str]: ...

    @property
    def has_alert(self) -> bool: ...


class FrameStates(object):
    def __init__(self, frame: ChromiumFrame):
        self._frame: ChromiumFrame = ...

    @property
    def is_loading(self) -> bool: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def ready_state(self) -> str: ...

    @property
    def is_displayed(self) -> bool: ...

    @property
    def has_alert(self) -> bool: ...
