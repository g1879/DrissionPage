# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Union, List, Tuple, Optional

from lxml.html import HtmlElement

from .._base.base import DrissionElement, BaseElement
from .._elements.chromium_element import ChromiumElement
from .._functions.elements import SessionElementsList
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.session_page import SessionPage


class SessionElement(DrissionElement):

    def __init__(self, ele: HtmlElement, owner: Union[SessionPage, None] = None):
        self._inner_ele: HtmlElement = ...
        self.owner: SessionPage = ...
        self.page: SessionPage = ...

    @property
    def inner_ele(self) -> HtmlElement: ...

    def __repr__(self) -> str: ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str],
                 index: int = 1,
                 timeout: float = None) -> SessionElement: ...

    def __eq__(self, other: SessionElement) -> bool: ...

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

    def parent(self,
               level_or_loc: Union[tuple, str, int] = 1,
               index: int = 1) -> SessionElement: ...

    def child(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[SessionElement, str]: ...

    def prev(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[SessionElement, str]: ...

    def next(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[SessionElement, str]: ...

    def before(self,
               locator: Union[Tuple[str, str], str, int] = '',
               index: int = 1,
               timeout: float = None,
               ele_only: bool = True) -> Union[SessionElement, str]: ...

    def after(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[SessionElement, str]: ...

    def children(self,
                 locator: Union[Tuple[str, str], str] = '',
                 timeout: float = None,
                 ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]: ...

    def prevs(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]: ...

    def nexts(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]: ...

    def befores(self,
                locator: Union[Tuple[str, str], str] = '',
                timeout: float = None,
                ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]: ...

    def afters(self,
               locator: Union[Tuple[str, str], str] = '',
               timeout: float = None,
               ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]: ...

    def attr(self, name: str) -> Optional[str]: ...

    def ele(self,
            locator: Union[Tuple[str, str], str],
            index: int = 1,
            timeout: float = None) -> SessionElement: ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> SessionElementsList: ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str] = None,
              index: int = 1) -> SessionElement: ...

    def s_eles(self, locator: Union[Tuple[str, str], str]) -> SessionElementsList: ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str],
                       timeout: float = None,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = None) -> Union[SessionElement, SessionElementsList]: ...

    def _get_ele_path(self, mode: str) -> str: ...


def make_session_ele(html_or_ele: Union[str, SessionElement, SessionPage, ChromiumElement, BaseElement, ChromiumFrame,
ChromiumBase],
                     loc: Union[str, Tuple[str, str]] = None,
                     index: Optional[int] = 1,
                     method: Optional[str] = None) -> Union[SessionElement, SessionElementsList]: ...
