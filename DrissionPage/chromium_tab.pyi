# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union, Tuple, Any, List

from DownloadKit import DownloadKit
from requests import Session, Response

from .chromium_base import ChromiumBase, ChromiumBaseSetter
from .chromium_element import ChromiumElement
from .chromium_frame import ChromiumFrame
from .chromium_page import ChromiumPage
from .session_element import SessionElement
from .session_page import SessionPage, SessionPageSetter, DownloadSetter
from .web_page import WebPage


class ChromiumTab(ChromiumBase):

    def __init__(self, page: ChromiumPage, tab_id: str = None):
        self.page: ChromiumPage = ...

    def _set_runtime_settings(self) -> None: ...


class WebPageTab(SessionPage, ChromiumTab):
    def __init__(self, page: WebPage, tab_id: str):
        self.page: WebPage = ...
        self._mode: str = ...
        self._has_driver = ...
        self._has_session = ...
        self._download_set = ...
        self._download_path = ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
                 timeout: float = None) -> Union[ChromiumElement, SessionElement, ChromiumFrame, None]: ...

    @property
    def url(self) -> Union[str, None]: ...

    @property
    def title(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> dict: ...

    @property
    def response(self) -> Response: ...

    @property
    def mode(self) -> str: ...

    @property
    def cookies(self) -> Union[dict, list]: ...

    @property
    def session(self) -> Session: ...

    @property
    def _session_url(self) -> str: ...

    @property
    def timeout(self) -> float: ...

    @timeout.setter
    def timeout(self, second: float) -> None: ...

    def get(self,
            url: str,
            show_errmsg: bool = False,
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
            cert: Any | None = ...) -> Union[bool, None]: ...

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
            timeout: float = None) -> Union[ChromiumElement, SessionElement, ChromiumFrame, str, None]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[ChromiumElement, SessionElement, ChromiumFrame, str]]: ...

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str] = None) \
            -> Union[SessionElement, str, None]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str]) -> List[Union[SessionElement, str]]: ...

    def change_mode(self, mode: str = None, go: bool = True, copy_cookies: bool = True) -> None: ...

    def cookies_to_session(self, copy_user_agent: bool = True) -> None: ...

    def cookies_to_browser(self) -> None: ...

    def get_cookies(self, as_dict: bool = False, all_domains: bool = False) -> Union[dict, list]: ...

    def _get_driver_cookies(self, as_dict: bool = False) -> dict: ...

    # ----------------重写SessionPage的函数-----------------------
    def post(self,
             url: str,
             data: Union[dict, str, None] = None,
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

    @property
    def set(self) -> WebPageTabSetter: ...

    @property
    def download(self) -> DownloadKit: ...

    @property
    def download_set(self) -> WebPageTabDownloadSetter: ...

    def _find_elements(self, loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement, ChromiumFrame],
                       timeout: float = None, single: bool = True, relative: bool = False, raise_err: bool = None) \
            -> Union[ChromiumElement, SessionElement, ChromiumFrame, str, None, List[Union[SessionElement, str]], List[
                Union[ChromiumElement, str, ChromiumFrame]]]: ...


class WebPageTabSetter(ChromiumBaseSetter):
    _page: WebPage = ...
    _session_setter: SessionPageSetter = ...
    _chromium_setter: ChromiumBaseSetter = ...

    def user_agent(self, ua: str, platform: str = None) -> None: ...

    def headers(self, headers: dict) -> None: ...

    def cookies(self, cookies, set_session: bool = False, set_driver: bool = False) -> None: ...


class WebPageTabDownloadSetter(DownloadSetter):
    """用于设置下载参数的类"""

    def __init__(self, page: WebPageTab):
        self._page: WebPageTab = ...

    @property
    def _switched_DownloadKit(self) -> DownloadKit: ...
