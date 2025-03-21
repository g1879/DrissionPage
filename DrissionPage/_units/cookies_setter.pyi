# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from http.cookiejar import Cookie, CookieJar
from typing import Union

from .._base.chromium import Chromium
from .._pages.chromium_base import ChromiumBase
from .._pages.mix_tab import MixTab
from .._pages.session_page import SessionPage
from .._pages.web_page import WebPage


class BrowserCookiesSetter(object):
    _owner: Chromium = ...

    def __init__(self, owner: Chromium):
        """
        :param owner: Chromium对象
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


class WebPageCookiesSetter(CookiesSetter, SessionCookiesSetter):
    _owner: WebPage = ...

    def __init__(self, owner: WebPage):
        """
        :param owner: WebPage对象
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


class MixTabCookiesSetter(CookiesSetter, SessionCookiesSetter):
    _owner: MixTab = ...

    def __init__(self, owner: MixTab):
        """
        :param owner: MixTab对象
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
