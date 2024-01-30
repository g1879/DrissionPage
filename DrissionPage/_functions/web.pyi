# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from http.cookiejar import Cookie
from typing import Union

from requests import Session
from requests.cookies import RequestsCookieJar

from .._base.base import BasePage, DrissionElement
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase


def get_ele_txt(e: DrissionElement) -> str: ...


def format_html(text: str) -> str: ...


def location_in_viewport(page: ChromiumBase, loc_x: float, loc_y: float) -> bool: ...


def offset_scroll(ele: ChromiumElement, offset_x: float, offset_y: float) -> tuple: ...


def make_absolute_link(link: str, baseURI: str = None) -> str: ...


def is_js_func(func: str) -> bool: ...


def cookie_to_dict(cookie: Union[Cookie, str, dict]) -> dict: ...


def cookies_to_tuple(cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> tuple: ...


def set_session_cookies(session: Session, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...


def set_browser_cookies(page: ChromiumBase, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...


def is_cookie_in_driver(page: ChromiumBase, cookie: dict) -> bool: ...


def get_blob(page: ChromiumBase, url: str, as_bytes: bool = True) -> bytes: ...
