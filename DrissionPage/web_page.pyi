# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union, Tuple, List, Any

from DownloadKit import DownloadKit
from requests import Session, Response

from .base import BasePage
from .chromium_element import ChromiumElement
from .chromium_frame import ChromiumFrame
from .chromium_page import ChromiumPage
from .config import DriverOptions, SessionOptions
from .session_element import SessionElement
from .session_page import SessionPage
from .chromium_driver import ChromiumDriver


class WebPage(SessionPage, ChromiumPage, BasePage):

    def __init__(self,
                 mode: str = ...,
                 timeout: float = ...,
                 tab_id: str = ...,
                 driver_or_options: Union[ChromiumDriver, DriverOptions, bool] = ...,
                 session_or_options: Union[Session, SessionOptions, bool] = ...) -> None:
        self._mode: str = ...
        self._has_driver: bool = ...
        self._has_session: bool = ...
        self._session_options: dict = ...
        self._driver_options: DriverOptions = ...
        self._setting_tab_id: str = ...

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
                 timeout: float = ...) -> Union[ChromiumElement, SessionElement, ChromiumFrame, None]: ...

    # -----------------共有属性和方法-------------------
    @property
    def url(self) -> Union[str, None]: ...

    @property
    def html(self) -> str: ...

    @property
    def json(self) -> dict: ...

    @property
    def response(self) -> Response: ...

    @property
    def mode(self) -> str: ...

    @property
    def cookies(self)->Union[dict, list]: ...

    @property
    def session(self) -> Session: ...

    @property
    def driver(self) -> ChromiumDriver: ...

    @property
    def _wait_driver(self) -> ChromiumDriver: ...

    @property
    def _driver(self) -> ChromiumDriver: ...

    @_driver.setter
    def _driver(self, tab: ChromiumDriver): ...

    @property
    def _session_url(self) -> str: ...

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
            cert: Any | None = ...) -> Union[bool, None]: ...

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
            timeout: float = ...) -> Union[ChromiumElement, SessionElement, ChromiumFrame, str, None]: ...

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = ...) -> List[Union[ChromiumElement, SessionElement, ChromiumFrame, str]]: ...

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str] = ...) \
            -> Union[SessionElement, str, None]: ...

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = ...) -> List[Union[SessionElement, str]]: ...

    def change_mode(self, mode: str = ..., go: bool = ..., copy_cookies: bool = ...) -> None: ...

    def cookies_to_session(self, copy_user_agent: bool = ...) -> None: ...

    def cookies_to_driver(self) -> None: ...

    def get_cookies(self, as_dict: bool = ..., all_domains: bool = ...) -> Union[dict, list]: ...

    def _get_driver_cookies(self, as_dict: bool = ...)->dict: ...

    def set_cookies(self, cookies, set_session: bool = ..., set_driver: bool = ...) -> None: ...

    def check_page(self, by_requests: bool = ...) -> Union[bool, None]: ...

    def close_driver(self) -> None: ...

    def close_session(self) -> None: ...

    # ----------------重写SessionPage的函数-----------------------
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

    @property
    def download(self) -> DownloadKit: ...

    def _ele(self,
             loc_or_ele: Union[Tuple[str, str], str, ChromiumElement, SessionElement, ChromiumFrame],
             timeout: float = ..., single: bool = ..., relative: bool = ...) \
            -> Union[ChromiumElement, SessionElement, ChromiumFrame, str, None, List[Union[SessionElement, str]], List[
                Union[ChromiumElement, str, ChromiumFrame]]]: ...

    def _set_driver_options(self, driver_or_Options: Union[ChromiumDriver, DriverOptions]) -> None: ...

    def _set_session_options(self, Session_or_Options:Union[Session, SessionOptions]) -> None: ...

    def quit(self) -> None: ...
