# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from http.cookiejar import Cookie, CookieJar
from typing import Union, Optional

from .._browsers.chromium import Chromium
from .._browsers.chromium_context import ChromiumContext
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_tab import ChromiumTab
from .._pages.session_page import SessionPage


class BrowserCookiesSetter(object):
    _owner: Union[Chromium, ChromiumContext] = ...

    def __init__(self, owner: Union[Chromium, ChromiumContext]):
        """
        :param owner: Chromium或ChromiumContext对象
        """
        ...

    def __call__(self, cookies: Union[CookieJar, Cookie, list, tuple, str, dict]) -> None:
        """设置一个或多个cookie
        :param cookies: cookies信息
        :return: None
        """
        ...

    def clear(self) -> None:
        """清除cookies"""
        ...


class CookiesSetter(BrowserCookiesSetter):
    _owner: ChromiumBase = ...

    def __init__(self, owner: ChromiumBase):
        """
        :param owner: 页面对象
        """
        ...

    def __call__(self, cookies: Union[CookieJar, Cookie, list, tuple, str, dict]) -> None:
        """设置一个或多个cookie
        :param cookies: cookies信息
        :return: None
        """
        ...

    def remove(self,
               name: str,
               url: str = None,
               domain: str = None,
               path: str = None) -> None:
        """删除一个cookie
        :param name: cookie的name字段
        :param url: cookie的url字段，可选
        :param domain: cookie的domain字段，可选
        :param path: cookie的path字段，可选
        :return: None
        """
        ...

    def clear(self) -> None:
        """清除cookies"""
        ...


class SessionCookiesSetter(object):
    _owner: SessionPage = ...

    def __init__(self, owner: SessionPage):
        """
        :param owner: SessionPage对象
        """
        ...

    def __call__(self, cookies: Union[CookieJar, Cookie, list, tuple, str, dict]) -> None:
        """设置一个或多个cookie
        :param cookies: cookies信息
        :return: None
        """
        ...

    def remove(self, name: str) -> None:
        """删除一个cookie
        :param name: cookie的name字段
        :return: None
        """
        ...

    def clear(self) -> None:
        """清除cookies"""
        ...


class ChromiumTabCookiesSetter(CookiesSetter, SessionCookiesSetter):
    _owner: ChromiumTab = ...

    def __init__(self, owner: ChromiumTab):
        """
        :param owner: ChromiumTab对象
        """
        ...

    def __call__(self, cookies: Union[CookieJar, Cookie, list, tuple, str, dict]) -> None:
        """设置一个或多个cookie
        :param cookies: cookies信息
        :return: None
        """
        ...

    def remove(self,
               name: str,
               url: str = None,
               domain: str = None,
               path: str = None) -> None:
        """删除一个cookie
        :param name: cookie的name字段
        :param url: cookie的url字段，可选，d模式时才有效
        :param domain: cookie的domain字段，可选，d模式时才有效
        :param path: cookie的path字段，可选，d模式时才有效
        :return: None
        """
        ...

    def clear(self) -> None:
        """清除cookies"""
        ...
