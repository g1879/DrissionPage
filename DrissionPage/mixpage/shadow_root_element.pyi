# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union, Any, Tuple, List

from selenium.webdriver.remote.webelement import WebElement

from .driver_page import DriverPage
from .mix_page import MixPage
from .base import BaseElement
from .driver_element import DriverElement
from .session_element import SessionElement


class ShadowRootElement(BaseElement):

    def __init__(self, inner_ele: WebElement, parent_ele: DriverElement):
        self._inner_ele: WebElement = ...
        self.parent_ele: DriverElement = ...
        self.page: Union[MixPage, DriverPage] = ...

    @property
    def inner_ele(self) -> WebElement: ...

    def __repr__(self) -> str: ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = None) -> Union[DriverElement, str, None]: ...

    @property
    def tag(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def inner_html(self) -> str: ...

    def parent(self, level_or_loc: Union[str, int] = 1) -> DriverElement: ...

    def next(self,
             index: int = 1,
             filter_loc: Union[tuple, str] = '') -> Union[DriverElement, str, None]: ...

    def before(self,
               index: int = 1,
               filter_loc: Union[tuple, str] = '') -> Union[DriverElement, str, None]: ...

    def after(self,
              index: int = 1,
              filter_loc: Union[tuple, str] = '') -> Union[DriverElement, str, None]: ...

    def nexts(self, filter_loc: Union[tuple, str] = '') -> List[Union[DriverElement, str]]: ...

    def befores(self, filter_loc: Union[tuple, str] = '') -> List[Union[DriverElement, str]]: ...

    def afters(self, filter_loc: Union[tuple, str] = '') -> List[Union[DriverElement, str]]: ...

    def ele(self,
            loc_or_str: Union[Tuple[str, str], str],
            timeout: float = None) -> Union[DriverElement, str, None]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[DriverElement, str]]: ...

    def s_ele(self, loc_or_str: Union[Tuple[str, str], str] = None) -> Union[SessionElement, str, None]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str]) -> List[Union[SessionElement, str]]: ...

    def _ele(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = ...,
             single: bool = ...,
             relative: bool = ...) -> Union[DriverElement, str, None, List[Union[DriverElement, str]]]: ...

    def run_script(self, script: str, *args) -> Any: ...

    def is_enabled(self) -> bool: ...

    def is_valid(self) -> bool: ...
