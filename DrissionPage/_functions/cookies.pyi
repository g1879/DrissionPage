# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from http.cookiejar import Cookie
from typing import Union

from requests import Session
from requests.cookies import RequestsCookieJar

from .._base.chromium import Chromium
from .._pages.chromium_base import ChromiumBase


def cookie_to_dict(cookie: Union[Cookie, str, dict]) -> dict:
    """把Cookie对象转为dict格式
    :param cookie: Cookie对象、字符串或字典
    :return: cookie字典
    """
    ...


def cookies_to_tuple(cookies: Union[RequestsCookieJar, list, tuple, str, dict, Cookie]) -> tuple:
    """把cookies转为tuple格式
    :param cookies: cookies信息，可为CookieJar, list, tuple, str, dict
    :return: 返回tuple形式的cookies
    """
    ...


def set_session_cookies(session: Session,
                        cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None:
    """设置Session对象的cookies
    :param session: Session对象
    :param cookies: cookies信息
    :return: None
    """
    ...


def set_browser_cookies(browser: Chromium,
                        cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None:
    """设置cookies值
    :param browser: 页面对象
    :param cookies: cookies信息
    :return: None
    """
    ...


def set_tab_cookies(page: ChromiumBase,
                    cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None:
    """设置cookies值
    :param page: 页面对象
    :param cookies: cookies信息
    :return: None
    """
    ...


def is_cookie_in_driver(page: ChromiumBase, cookie: dict) -> bool:
    """查询cookie是否在浏览器内
    :param page: BasePage对象
    :param cookie: dict格式cookie
    :return: bool
    """
    ...


def format_cookie(cookie: dict) -> dict:
    """设置cookie为可用格式
    :param cookie: dict格式cookie
    :return: 格式化后的cookie字典
    """
    ...


class CookiesList(list):
    def as_dict(self) -> dict:
        """以dict格式返回，只包含name和value字段"""
        ...

    def as_str(self) -> str:
        """以str格式返回，只包含name和value字段"""
        ...

    def as_json(self) -> str:
        """以json格式返回"""
        ...

    def __next__(self) -> dict: ...
