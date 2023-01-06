# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from abc import abstractmethod
from typing import Union, Tuple, List


class BaseParser(object):

    def __call__(self, loc_or_str: Union[Tuple[str, str], str]): ...

    def ele(self, loc_or_ele: Union[Tuple[str, str], str, BaseElement], timeout:float=...): ...

    def eles(self, loc_or_str: Union[Tuple[str, str], str], timeout=...): ...

    # ----------------以下属性或方法待后代实现----------------
    @property
    def html(self) -> str: ...

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str, BaseElement]): ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str]): ...

    @abstractmethod
    def _ele(self, loc_or_ele, timeout:float=..., single:bool=...): ...


class BaseElement(BaseParser):

    def __init__(self, page: BasePage):
        self.page: BasePage = ...

    # ----------------以下属性或方法由后代实现----------------
    @property
    def tag(self)->str: ...

    @abstractmethod
    def _ele(self, loc_or_str: Union[Tuple[str, str], str], timeout:float=..., single:bool=..., relative:bool=...): ...

    def parent(self, level_or_loc: Union[tuple, str, int] = ...): ...

    def prev(self, index: int = ...) -> None: ...

    def prevs(self) -> None: ...

    def next(self, index: int = ...): ...

    def nexts(self): ...


class DrissionElement(BaseElement):

    def __init__(self,
                 page: BasePage = ...):
        self.page: BasePage = ...

    @property
    def link(self) -> str: ...

    @property
    def css_path(self) -> str: ...

    @property
    def xpath(self) -> str: ...

    @property
    def comments(self) -> list: ...

    def texts(self, text_node_only: bool = ...) -> list: ...

    def parent(self, level_or_loc: Union[tuple, str, int] = ...) -> Union['DrissionElement', None]: ...

    def prev(self,
             index: int = ...,
             filter_loc: Union[tuple, str] = ...,
             timeout: float = ...) -> Union['DrissionElement', str, None]: ...

    def next(self,
             index: int = ...,
             filter_loc: Union[tuple, str] = ...,
             timeout: float = ...) -> Union['DrissionElement', str, None]: ...

    def before(self,
               index: int = ...,
               filter_loc: Union[tuple, str] = ...,
               timeout: float = ...) -> Union['DrissionElement', str, None]: ...

    def after(self,
              index: int = ...,
              filter_loc: Union[tuple, str] = ...,
              timeout: float = ...) -> Union['DrissionElement', str, None]: ...

    def prevs(self,
              filter_loc: Union[tuple, str] = ...,
              timeout: float = ...) -> List[Union['DrissionElement', str]]: ...

    def nexts(self,
              filter_loc: Union[tuple, str] = ...,
              timeout: float = ...) -> List[Union['DrissionElement', str]]: ...

    def befores(self,
                filter_loc: Union[tuple, str] = ...,
                timeout: float = ...) -> List[Union['DrissionElement', str]]: ...

    def afters(self,
               filter_loc: Union[tuple, str] = ...,
               timeout: float = ...) -> List[Union['DrissionElement', str]]: ...

    def _get_brothers(self,
                      index: int = ...,
                      filter_loc: Union[tuple, str] = ...,
                      direction: str = ...,
                      brother: bool = ...,
                      timeout: float = ...) -> List[Union['DrissionElement', str]]: ...

    # ----------------以下属性或方法由后代实现----------------
    @property
    def attrs(self) -> dict: ...

    @property
    def text(self) -> str: ...

    @property
    def raw_text(self) -> str: ...

    @abstractmethod
    def attr(self, attr: str) -> str: ...

    def _get_ele_path(self, mode) -> str: ...


class BasePage(BaseParser):

    def __init__(self, timeout: float = ...):
        self._url_available: bool = ...
        self.retry_times: int = ...
        self.retry_interval: float = ...
        self._timeout = float = ...

    @property
    def title(self) -> Union[str, None]: ...

    @property
    def timeout(self) -> float: ...

    @timeout.setter
    def timeout(self, second: float) -> None: ...

    @property
    def cookies(self) -> dict: ...

    @property
    def url_available(self) -> bool: ...

    def _before_connect(self, url: str, retry: int, interval: float) -> tuple: ...

    # ----------------以下属性或方法由后代实现----------------
    @property
    def url(self) -> str: ...

    @property
    def json(self) -> dict: ...

    @abstractmethod
    def get_cookies(self, as_dict: bool = ...) -> Union[list, dict]: ...

    @abstractmethod
    def get(self,
            url: str,
            show_errmsg: bool = ...,
            retry: int = ...,
            interval: float = ...): ...
