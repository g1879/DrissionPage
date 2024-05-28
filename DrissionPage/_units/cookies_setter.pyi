# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from http.cookiejar import Cookie, CookieJar
from typing import Union

from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_tab import WebPageTab
from .._pages.session_page import SessionPage
from .._pages.web_page import WebPage


class CookiesSetter(object):
    _owner: ChromiumBase

    def __init__(self, page: ChromiumBase): ...

    def __call__(self, cookies: Union[CookieJar, Cookie, list, tuple, str, dict]) -> None: ...

    def remove(self, name: str, url: str = None, domain: str = None, path: str = None) -> None: ...

    def clear(self) -> None: ...


class SessionCookiesSetter(object):
    _owner: SessionPage

    def __init__(self, page: SessionPage): ...

    def __call__(self, cookies: Union[CookieJar, Cookie, list, tuple, str, dict]) -> None: ...

    def remove(self, name: str) -> None: ...

    def clear(self) -> None: ...


class WebPageCookiesSetter(CookiesSetter, SessionCookiesSetter):
    _owner: Union[WebPage, WebPageTab]

    def __init__(self, page: SessionPage): ...

    def __call__(self, cookies: Union[CookieJar, Cookie, list, tuple, str, dict]) -> None: ...

    def remove(self, name: str, url: str = None, domain: str = None, path: str = None) -> None: ...

    def clear(self) -> None: ...
