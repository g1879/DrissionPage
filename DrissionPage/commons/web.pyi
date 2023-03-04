# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from http.cookiejar import Cookie
from typing import Union

from requests import Session
from requests.cookies import RequestsCookieJar

from DrissionPage.base import DrissionElement, BasePage
from DrissionPage.chromium_element import ChromiumElement


def get_ele_txt(e: DrissionElement) -> str: ...


def format_html(text: str) -> str: ...


def location_in_viewport(page, loc_x: int, loc_y: int) -> bool: ...


def offset_scroll(ele: ChromiumElement, offset_x: int, offset_y: int) -> tuple: ...


def make_absolute_link(link, page: BasePage = None) -> str: ...


def is_js_func(func: str) -> bool: ...


def cookie_to_dict(cookie: Union[Cookie, str, dict]) -> dict: ...


def cookies_to_tuple(cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> tuple: ...


def set_session_cookies(session: Session, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...
