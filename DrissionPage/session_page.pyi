# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from typing import Any, Union, Tuple, List

from DownloadKit import DownloadKit
from requests import Session, Response
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict

from .commons.constants import NoneElement
from .base import BasePage
from .chromium_page import ChromiumPage
from .configs.session_options import SessionOptions
from .session_element import SessionElement
from .web_page import WebPage


class SessionPage(BasePage):
    def __init__(self,
                 session_or_options: Union[Session, SessionOptions] = None,
                 timeout: float = None):
        self._session: Session = ...
        self._session_options: SessionOptions = ...
        self._url: str = ...
        self._response: Response = ...
        self._download_path: str = ...
        self._download_set: DownloadSetter = ...
        self._url_available: bool = ...
        self.timeout: float = ...
        self.retry_times: int = ...
        self.retry_interval: float = ...
        self._set: SessionPageSetter = ...

    def _set_start_options(self, session_or_options, none) -> None: ...

    def _create_session(self) -> None: ...

    def _set_runtime_settings(self) -> None: ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, SessionElement],
                 timeout: float = None) -> Union[SessionElement, str, NoneElement]: ...

    # -----------------共有属性和方法-------------------
    @property
    def title(self) -> str: ...

    @property
    def url(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> Union[dict, None]: ...

    @property
    def download_path(self) -> str: ...

    @property
    def download_set(self) -> DownloadSetter: ...

    def get(self,
            url: str,
            show_errmsg: bool | None = False,
            retry: int | None = None,
            interval: float | None = None,
            timeout: float | None = None,
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
            timeout: float = None) -> Union[SessionElement, str, NoneElement]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[SessionElement, str]]: ...

    def s_ele(self,
              loc_or_ele: Union[Tuple[str, str], str, SessionElement] = None) \
            -> Union[SessionElement, str, NoneElement]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str]) -> List[Union[SessionElement, str]]: ...

    def _find_elements(self, loc_or_ele: Union[Tuple[str, str], str, SessionElement],
                       timeout: float = None, single: bool = True, raise_err: bool = None) \
            -> Union[SessionElement, str, NoneElement, List[Union[SessionElement, str]]]: ...

    def get_cookies(self,
                    as_dict: bool = False,
                    all_domains: bool = False) -> Union[dict, list]: ...

    # ----------------session独有属性和方法-----------------------
    @property
    def session(self) -> Session: ...

    @property
    def response(self) -> Response: ...

    @property
    def set(self) -> SessionPageSetter: ...

    @property
    def download(self) -> DownloadKit: ...

    def post(self,
             url: str,
             data: Union[dict, str, None] = ...,
             show_errmsg: bool = False,
             retry: int | None = None,
             interval: float | None = None,
             timeout: float | None = ...,
             params: dict | None = ...,
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
                   data: Union[dict, str, None] = None,
                   show_errmsg: bool = False,
                   retry: int = None,
                   interval: float = None,
                   **kwargs) -> bool: ...

    def _make_response(self,
                       url: str,
                       mode: str = 'get',
                       data: Union[dict, str] = None,
                       retry: int = None,
                       interval: float = None,
                       show_errmsg: bool = False,
                       **kwargs) -> tuple: ...


class SessionPageSetter(object):
    def __init__(self, page: SessionPage):
        self._page: SessionPage = ...

    def timeout(self, second: Union[int, float]) -> None: ...

    def cookies(self, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...

    def headers(self, headers: dict) -> None: ...

    def header(self, attr: str, value: str) -> None: ...

    def user_agent(self, ua: str) -> None: ...

    def proxies(self, http, https=None) -> None: ...

    def auth(self, auth: Union[Tuple[str, str], HTTPBasicAuth, None]) -> None: ...

    def hooks(self, hooks: Union[dict, None]) -> None: ...

    def params(self, params: Union[dict, None]) -> None: ...

    def verify(self, on_off: Union[bool, None]) -> None: ...

    def cert(self, cert: Union[str, Tuple[str, str], None]) -> None: ...

    def stream(self, on_off: Union[bool, None]) -> None: ...

    def trust_env(self, on_off: Union[bool, None]) -> None: ...

    def max_redirects(self, times: Union[int, None]) -> None: ...

    def add_adapter(self, url: str, adapter: HTTPAdapter) -> None: ...


class DownloadSetter(object):
    def __init__(self, page: Union[SessionPage, WebPage, ChromiumPage]):
        self._page: SessionPage = ...
        self._DownloadKit: DownloadKit = ...

    @property
    def DownloadKit(self) -> DownloadKit: ...

    @property
    def if_file_exists(self) -> FileExists: ...

    def split(self, on_off: bool) -> None: ...

    def save_path(self, path: Union[str, Path]): ...


class FileExists(object):
    def __init__(self, setter: DownloadSetter):
        self._setter: DownloadSetter = ...

    def __call__(self, mode: str) -> None: ...

    def skip(self) -> None: ...

    def rename(self) -> None: ...

    def overwrite(self) -> None: ...


def check_headers(kwargs: Union[dict, CaseInsensitiveDict], headers: Union[dict, CaseInsensitiveDict],
                  arg: str) -> bool: ...


def set_charset(response: Response) -> Response: ...
