# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path
from typing import Any, Union, Tuple, Optional

from requests import Session, Response
from requests.structures import CaseInsensitiveDict

from .._base.base import BasePage
from .._configs.session_options import SessionOptions
from .._elements.session_element import SessionElement
from .._functions.elements import SessionElementsList
from .._units.setter import SessionPageSetter


class SessionPage(BasePage):
    def __init__(self,
                 session_or_options: Union[Session, SessionOptions] = None,
                 timeout: float = None):
        self._headers: Optional[CaseInsensitiveDict] = ...
        self._session: Session = ...
        self._session_options: SessionOptions = ...
        self._url: str = ...
        self._response: Response = ...
        self._url_available: bool = ...
        self.timeout: float = ...
        self.retry_times: int = ...
        self.retry_interval: float = ...
        self._set: SessionPageSetter = ...
        self._encoding: str = ...
        self._page: SessionPage = ...

    def _s_set_start_options(self, session_or_options: Union[Session, SessionOptions]) -> None: ...

    def _s_set_runtime_settings(self) -> None: ...

    def _create_session(self) -> None: ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str, SessionElement],
                 index: int = 1,
                 timeout: float = None) -> SessionElement: ...

    # -----------------共有属性和方法-------------------
    @property
    def title(self) -> str: ...

    @property
    def url(self) -> str: ...

    @property
    def _session_url(self) -> str: ...

    @property
    def raw_data(self) -> Union[str, bytes]: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> Union[dict, None]: ...

    @property
    def user_agent(self) -> str: ...

    @property
    def download_path(self) -> str: ...

    def get(self,
            url: Union[Path, str],
            show_errmsg: bool | None = False,
            retry: int | None = None,
            interval: float | None = None,
            timeout: float | None = None,
            params: dict | None = ...,
            data: Union[dict, str, None] = ...,
            json: Union[dict, str, None] = ...,
            headers: Union[dict, str, None] = ...,
            cookies: Any | None = ...,
            files: Any | None = ...,
            auth: Any | None = ...,
            allow_redirects: bool = ...,
            proxies: dict | None = ...,
            hooks: Any | None = ...,
            stream: Any | None = ...,
            verify: Any | None = ...,
            cert: Any | None = ...) -> bool: ...

    def ele(self,
            locator: Union[Tuple[str, str], str, SessionElement],
            index: int = 1,
            timeout: float = None) -> SessionElement: ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> SessionElementsList: ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str, SessionElement] = None,
              index: int = 1) -> SessionElement: ...

    def s_eles(self, loc: Union[Tuple[str, str], str]) -> SessionElementsList: ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str, SessionElement],
                       timeout: float = None,
                       index: Optional[int] = 1,
                       relative: bool = True,
                       raise_err: bool = None) -> Union[SessionElement, SessionElementsList]: ...

    def cookies(self,
                as_dict: bool = False,
                all_domains: bool = False,
                all_info: bool = False) -> Union[dict, list]: ...

    # ----------------session独有属性和方法-----------------------
    @property
    def session(self) -> Session: ...

    @property
    def response(self) -> Response: ...

    @property
    def encoding(self) -> str: ...

    @property
    def set(self) -> SessionPageSetter: ...

    def post(self,
             url: str,
             show_errmsg: bool = False,
             retry: int | None = None,
             interval: float | None = None,
             data: Union[dict, str, None] = ...,
             timeout: float | None = ...,
             params: dict | None = ...,
             json: Union[dict, str, None] = ...,
             headers: Union[dict, str, None] = ...,
             cookies: Any | None = ...,
             files: Any | None = ...,
             auth: Any | None = ...,
             allow_redirects: bool = ...,
             proxies: dict | None = ...,
             hooks: Any | None = ...,
             stream: Any | None = ...,
             verify: Any | None = ...,
             cert: Any | None = ...) -> bool: ...

    def close(self) -> None: ...

    def _s_connect(self,
                   url: str,
                   mode: str,
                   show_errmsg: bool = False,
                   retry: int = None,
                   interval: float = None,
                   **kwargs) -> bool: ...

    def _make_response(self,
                       url: str,
                       mode: str = 'get',
                       retry: int = None,
                       interval: float = None,
                       show_errmsg: bool = False,
                       **kwargs) -> tuple: ...


def check_headers(kwargs: Union[dict, CaseInsensitiveDict],
                  headers: Union[dict, CaseInsensitiveDict],
                  arg: str) -> bool: ...


def set_charset(response: Response) -> Response: ...
