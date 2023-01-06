# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union, List, Tuple

from lxml.html import HtmlElement

from .base import DrissionElement, BaseElement
from .chromium_base import ChromiumBase
from .chromium_element import ChromiumElement
from .chromium_frame import ChromiumFrame
from .driver_element import DriverElement
from .session_page import SessionPage


class SessionElement(DrissionElement):

    def __init__(self, ele: HtmlElement, page: Union[SessionPage, None] = ...):
        self._inner_ele: HtmlElement = ...
        self.page: SessionPage = ...

    @property
    def inner_ele(self) -> HtmlElement: ...

    def __repr__(self) -> str: ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = ...) -> Union['SessionElement', str, None]: ...

    @property
    def tag(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def inner_html(self) -> str: ...

    @property
    def attrs(self) -> dict: ...

    @property
    def text(self) -> str: ...

    @property
    def raw_text(self) -> str: ...

    def parent(self, level_or_loc: Union[tuple, str, int] = ...) -> Union['SessionElement', None]: ...

    def prev(self,
             index: int = ...,
             filter_loc: Union[tuple, str] = ...,
             timeout: float = ...) -> Union['SessionElement', str, None]: ...

    def next(self,
             index: int = ...,
             filter_loc: Union[tuple, str] = ...,
             timeout: float = ...) -> Union['SessionElement', str, None]: ...

    def before(self,
               index: int = ...,
               filter_loc: Union[tuple, str] = ...,
               timeout: float = ...) -> Union['SessionElement', str, None]: ...

    def after(self,
              index: int = ...,
              filter_loc: Union[tuple, str] = ...,
              timeout: float = ...) -> Union['SessionElement', str, None]: ...

    def prevs(self,
              filter_loc: Union[tuple, str] = ...,
              timeout: float = ...) -> List[Union['SessionElement', str]]: ...

    def nexts(self,
              filter_loc: Union[tuple, str] = ...,
              timeout: float = ...) -> List[Union['SessionElement', str]]: ...

    def befores(self,
                filter_loc: Union[tuple, str] = ...,
                timeout: float = ...) -> List[Union['SessionElement', str]]: ...

    def afters(self,
               filter_loc: Union[tuple, str] = ...,
               timeout: float = ...) -> List[Union['SessionElement', str]]: ...

    def attr(self, attr: str) -> Union[str, None]: ...

    def ele(self,
            loc_or_str: Union[Tuple[str, str], str],
            timeout: float = ...) -> Union['SessionElement', str, None]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = ...) -> List[Union['SessionElement', str]]: ...

    def s_ele(self,
              loc_or_str: Union[Tuple[str, str], str] = ...) -> Union['SessionElement', str, None]: ...

    def s_eles(self,
               loc_or_str: Union[Tuple[str, str], str] = ...) -> List[Union['SessionElement', str]]: ...

    def _ele(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = ...,
             single: bool = ...,
             relative: bool = ...) -> Union['SessionElement', str, None, List[Union['SessionElement', str]]]: ...

    def _get_ele_path(self, mode: str) -> str: ...


def make_session_ele(html_or_ele: Union[str, SessionElement, SessionPage, ChromiumElement, DriverElement, BaseElement,
                                        ChromiumFrame, ChromiumBase],
                     loc: Union[str, Tuple[str, str]] = ...,
                     single: bool = ...) -> Union[SessionElement, str, None, List[Union[SessionElement, str]]]: ...
