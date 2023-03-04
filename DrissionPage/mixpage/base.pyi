# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from abc import abstractmethod
from typing import Union, Tuple, List


class BaseParser(object):

    def __call__(self, loc_or_str: Union[Tuple[str, str], str]): ...

    def ele(self, loc_or_ele: Union[Tuple[str, str], str, BaseElement], timeout: float = None): ...

    def eles(self, loc_or_str: Union[Tuple[str, str], str], timeout=None): ...

    # ----------------以下属性或方法待后代实现----------------
    @property
    def html(self) -> str: ...

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str, BaseElement]): ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str]): ...

    @abstractmethod
    def _ele(self, loc_or_ele, timeout: float = None, single: bool = True): ...


class BaseElement(BaseParser):

    def __init__(self, page: BasePage = None):
        self.page: BasePage = ...

    # ----------------以下属性或方法由后代实现----------------
    @property
    def tag(self) -> str: ...

    @abstractmethod
    def _ele(self, loc_or_str: Union[Tuple[str, str], str], timeout: float = None, single: bool = True,
             relative: bool = False): ...

    def parent(self, level_or_loc: Union[tuple, str, int] = 1): ...

    def prev(self, index: int = 1) -> None: ...

    def prevs(self) -> None: ...

    def next(self, index: int = 1): ...

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

    def texts(self, text_node_only: bool = False) -> list: ...

    def parent(self, level_or_loc: Union[tuple, str, int] = 1) -> Union[DrissionElement, None]: ...

    def prev(self,
             index: int = 1,
             filter_loc: Union[tuple, str] = '',
             timeout: float = 0) -> Union[DrissionElement, str, None]: ...

    def next(self,
             index: int = 1,
             filter_loc: Union[tuple, str] = '',
             timeout: float = 0) -> Union[DrissionElement, str, None]: ...

    def before(self,
               index: int = 1,
               filter_loc: Union[tuple, str] = '',
               timeout: float = None) -> Union[DrissionElement, str, None]: ...

    def after(self,
              index: int = 1,
              filter_loc: Union[tuple, str] = '',
              timeout: float = None) -> Union[DrissionElement, str, None]: ...

    def prevs(self,
              filter_loc: Union[tuple, str] = '',
              timeout: float = 0) -> List[Union[DrissionElement, str]]: ...

    def nexts(self,
              filter_loc: Union[tuple, str] = '',
              timeout: float = 0) -> List[Union[DrissionElement, str]]: ...

    def befores(self,
                filter_loc: Union[tuple, str] = '',
                timeout: float = None) -> List[Union[DrissionElement, str]]: ...

    def afters(self,
               filter_loc: Union[tuple, str] = '',
               timeout: float = None) -> List[Union[DrissionElement, str]]: ...

    def _get_brothers(self,
                      index: int = None,
                      filter_loc: Union[tuple, str] = '',
                      direction: str = 'following',
                      brother: bool = True,
                      timeout: float = 0.5) -> List[Union[DrissionElement, str]]: ...

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

    def __init__(self, timeout: float = None):
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
    def get_cookies(self, as_dict: bool = False) -> Union[list, dict]: ...

    @abstractmethod
    def get(self,
            url: str,
            show_errmsg: bool = False,
            retry: int = None,
            interval: float = None): ...
