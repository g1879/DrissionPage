# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Union, List, Optional, Iterable

from .._base.base import BaseParser
from .._elements.chromium_element import ChromiumElement
from .._elements.session_element import SessionElement


def get_eles(locators: Union[List[str], tuple],
             owner: BaseParser,
             any_one: bool = False,
             first_ele: bool = True,
             timeout: float = 10) -> dict: ...


class SessionElementsList(list):
    _page = ...

    def __init__(self, page=None, *args): ...

    @property
    def get(self) -> Getter: ...

    @property
    def filter(self) -> SessionFilter: ...

    @property
    def filter_one(self) -> SessionFilterOne: ...

    def __next__(self) -> SessionElement: ...


class ChromiumElementsList(SessionElementsList):

    @property
    def filter(self) -> ChromiumFilter: ...

    @property
    def filter_one(self) -> ChromiumFilterOne: ...

    def search(self,
               displayed: Optional[bool] = None,
               checked: Optional[bool] = None,
               selected: Optional[bool] = None,
               enabled: Optional[bool] = None,
               clickable: Optional[bool] = None,
               have_rect: Optional[bool] = None,
               have_text: Optional[bool] = None) -> ChromiumFilter: ...

    def search_one(self,
                   index: int = 1,
                   displayed: Optional[bool] = None,
                   checked: Optional[bool] = None,
                   selected: Optional[bool] = None,
                   enabled: Optional[bool] = None,
                   clickable: Optional[bool] = None,
                   have_rect: Optional[bool] = None,
                   have_text: Optional[bool] = None) -> ChromiumElement: ...

    def __next__(self) -> ChromiumElement: ...


class SessionFilterOne(object):
    _list: SessionElementsList = ...
    _index: int = ...

    def __init__(self, _list: SessionElementsList, index: int = 1): ...

    def __call__(self, index: int = 1) -> SessionFilterOne: ...

    def attr(self, name: str, value: str, equal: bool = True) -> SessionElement: ...

    def text(self, text: str, fuzzy: bool = True, contain: bool = True) -> SessionElement: ...

    def _get_attr(self,
                  name: str,
                  value: str,
                  method: str,
                  equal: bool = True) -> SessionElement: ...


class SessionFilter(SessionFilterOne):

    def __iter__(self) -> Iterable[SessionElement]: ...

    def __next__(self) -> SessionElement: ...

    def __len__(self) -> int: ...

    def __getitem__(self, item: int) -> SessionElement: ...

    @property
    def get(self) -> Getter: ...

    def attr(self, name: str, value: str, equal: bool = True) -> SessionFilter: ...

    def text(self, text: str, fuzzy: bool = True, contain: bool = True) -> SessionFilter: ...

    def _get_attr(self,
                  name: str,
                  value: str,
                  method: str,
                  equal: bool = True) -> SessionFilter: ...


class ChromiumFilterOne(SessionFilterOne):
    _list: ChromiumElementsList = ...

    def __init__(self, _list: ChromiumElementsList): ...

    def __call__(self, index: int = 1) -> ChromiumFilterOne: ...

    def displayed(self, equal: bool = True) -> ChromiumElement: ...

    def checked(self, equal: bool = True) -> ChromiumElement: ...

    def selected(self, equal: bool = True) -> ChromiumElement: ...

    def enabled(self, equal: bool = True) -> ChromiumElement: ...

    def clickable(self, equal: bool = True) -> ChromiumElement: ...

    def have_rect(self, equal: bool = True) -> ChromiumElement: ...

    def style(self, name: str, value: str, equal: bool = True) -> ChromiumElement: ...

    def property(self,
                 name: str,
                 value: str, equal: bool = True) -> ChromiumElement: ...

    def attr(self, name: str, value: str, equal: bool = True) -> ChromiumElement: ...

    def text(self, text: str, fuzzy: bool = True, contain: bool = True) -> ChromiumElement: ...

    def _get_attr(self,
                  name: str,
                  value: str,
                  method: str, equal: bool = True) -> ChromiumElement: ...

    def _any_state(self, name: str, equal: bool = True) -> ChromiumElement: ...


class ChromiumFilter(ChromiumFilterOne):

    def __iter__(self) -> Iterable[ChromiumElement]: ...

    def __next__(self) -> ChromiumElement: ...

    def __len__(self) -> int: ...

    def __getitem__(self, item: int) -> ChromiumElement: ...

    @property
    def get(self) -> Getter: ...

    def displayed(self, equal: bool = True) -> ChromiumFilter: ...

    def checked(self, equal: bool = True) -> ChromiumFilter: ...

    def selected(self, equal: bool = True) -> ChromiumFilter: ...

    def enabled(self, equal: bool = True) -> ChromiumFilter: ...

    def clickable(self, equal: bool = True) -> ChromiumFilter: ...

    def have_rect(self, equal: bool = True) -> ChromiumFilter: ...

    def style(self, name: str, value: str, equal: bool = True) -> ChromiumFilter: ...

    def property(self,
                 name: str,
                 value: str, equal: bool = True) -> ChromiumFilter: ...

    def attr(self, name: str, value: str, equal: bool = True) -> ChromiumFilter: ...

    def text(self, text: str, fuzzy: bool = True, contain: bool = True) -> ChromiumFilter: ...

    def search(self,
               displayed: Optional[bool] = None,
               checked: Optional[bool] = None,
               selected: Optional[bool] = None,
               enabled: Optional[bool] = None,
               clickable: Optional[bool] = None,
               have_rect: Optional[bool] = None,
               have_text: Optional[bool] = None) -> ChromiumFilter: ...

    def search_one(self,
                   index: int = 1,
                   displayed: Optional[bool] = None,
                   checked: Optional[bool] = None,
                   selected: Optional[bool] = None,
                   enabled: Optional[bool] = None,
                   clickable: Optional[bool] = None,
                   have_rect: Optional[bool] = None,
                   have_text: Optional[bool] = None) -> ChromiumElement: ...

    def _get_attr(self,
                  name: str,
                  value: str,
                  method: str, equal: bool = True) -> ChromiumFilter: ...

    def _any_state(self, name: str, equal: bool = True) -> ChromiumFilter: ...


class Getter(object):
    _list: SessionElementsList = ...

    def __init__(self, _list: SessionElementsList): ...

    def links(self) -> List[str]: ...

    def texts(self) -> List[str]: ...

    def attrs(self, name: str) -> List[str]: ...
