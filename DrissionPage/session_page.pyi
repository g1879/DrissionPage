# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Any, Union, Tuple, List

from DownloadKit import DownloadKit
from requests import Session, Response
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict

from .base import BasePage
from .session_element import SessionElement
from .config import SessionOptions


class SessionPage(BasePage):
    def __init__(self,
                 session_or_options: Union[Session, SessionOptions] = ...,
                 timeout: float = ...):
        self._session: Session = ...
        self._url: str = ...
        self._response: Response = ...
        self._download_kit: DownloadKit = ...
        self._url_available: bool = ...
        self.timeout: float = ...
        self.retry_times: int = ...
        self.retry_interval: float = ...

    def _create_session(self, Session_or_Options: Union[Session, SessionOptions]) -> None: ...

    def _set_session(self, data: dict) -> None: ...

    def set_cookies(self, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...

    def set_headers(self, headers: dict) -> None: ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, SessionElement],
                 timeout: float = ...) -> Union[SessionElement, str, None]: ...

    # -----------------共有属性和方法-------------------

    @property
    def url(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> Union[dict, None]: ...

    def get(self,
            url: str,
            show_errmsg: bool | None = ...,
            retry: int | None = ...,
            interval: float | None = ...,
            timeout: float | None = ...,
            params: dict | None = ...,
            data: Union[dict, str, None] = ...,
            json: Union[dict, str, None] = ...,
            headers: dict | None = ...,
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
            loc_or_ele: Union[Tuple[str, str], str, SessionElement],
            timeout: float = ...) -> Union[SessionElement, str, None]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = ...) -> List[Union[SessionElement, str]]: ...

    def s_ele(self,
              loc_or_ele: Union[Tuple[str, str], str, SessionElement] = ...) -> Union[SessionElement, str, None]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = ...) -> List[Union[SessionElement, str]]: ...

    def _ele(self,
             loc_or_ele: Union[Tuple[str, str], str, SessionElement],
             timeout: float = ...,
             single: bool = ...) -> Union[SessionElement, str, None, List[Union[SessionElement, str]]]: ...

    def get_cookies(self,
                    as_dict: bool = ...,
                    all_domains: bool = ...) -> Union[dict, list]: ...

    # ----------------session独有属性和方法-----------------------
    @property
    def session(self) -> Session: ...

    @property
    def response(self) -> Response: ...

    @property
    def download(self) -> DownloadKit: ...

    def post(self,
             url: str,
             show_errmsg: bool | None = ...,
             retry: int | None = ...,
             interval: float | None = ...,
             timeout: float | None = ...,
             params: dict | None = ...,
             data: Union[dict, str, None] = ...,
             json: Union[dict, str, None] = ...,
             headers: dict | None = ...,
             cookies: Any | None = ...,
             files: Any | None = ...,
             auth: Any | None = ...,
             allow_redirects: bool = ...,
             proxies: dict | None = ...,
             hooks: Any | None = ...,
             stream: Any | None = ...,
             verify: Any | None = ...,
             cert: Any | None = ...) -> bool: ...

    def _s_connect(self,
                   url: str,
                   mode: str,
                   data: Union[dict, str, None] = ...,
                   show_errmsg: bool = ...,
                   retry: int = ...,
                   interval: float = ...,
                   **kwargs) -> bool: ...

    def _make_response(self,
                       url: str,
                       mode: str = ...,
                       data: Union[dict, str] = ...,
                       retry: int = ...,
                       interval: float = ...,
                       show_errmsg: bool = ...,
                       **kwargs) -> tuple: ...


def check_headers(kwargs: Union[dict, CaseInsensitiveDict], headers: Union[dict, CaseInsensitiveDict],
                  arg: str) -> bool: ...


def set_charset(response: Response) -> Response: ...
