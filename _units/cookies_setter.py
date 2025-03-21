# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from .._functions.cookies import set_tab_cookies, set_session_cookies, set_browser_cookies
from .._functions.settings import Settings as _S


class BrowserCookiesSetter(object):
    def __init__(self, owner):
        self._owner = owner

    def __call__(self, cookies):
        set_browser_cookies(self._owner, cookies)

    def clear(self):
        self._owner._run_cdp('Storage.clearCookies')


class CookiesSetter(BrowserCookiesSetter):
    def __call__(self, cookies):
        set_tab_cookies(self._owner, cookies)

    def remove(self, name, url=None, domain=None, path=None):
        d = {'name': name}
        if url is not None:
            d['url'] = url
        if domain is not None:
            d['domain'] = domain
        if not url and not domain:
            d['url'] = self._owner.url
            if not d['url'].startswith('http'):
                raise ValueError(_S._lang.join(_S._lang.NEED_DOMAIN))
        if path is not None:
            d['path'] = path
        self._owner._run_cdp('Network.deleteCookies', **d)

    def clear(self):
        self._owner._run_cdp('Network.clearBrowserCookies')


class SessionCookiesSetter(object):
    def __init__(self, owner):
        self._owner = owner

    def __call__(self, cookies):
        set_session_cookies(self._owner.session, cookies)

    def remove(self, name):
        self._owner.session.cookies.set(name, None)

    def clear(self):
        self._owner.session.cookies.clear()


class WebPageCookiesSetter(CookiesSetter):
    def __call__(self, cookies):
        if self._owner.mode == 'd' and self._owner._has_driver:
            super().__call__(cookies)
        elif self._owner.mode == 's' and self._owner._has_session:
            set_session_cookies(self._owner.session, cookies)

    def remove(self, name, url=None, domain=None, path=None):
        if self._owner.mode == 'd' and self._owner._has_driver:
            super().remove(name, url, domain, path)
        elif self._owner.mode == 's' and self._owner._has_session:
            if url or domain or path:
                raise ValueError(_S._lang.join(_S._lang.D_MODE_ONLY))
            self._owner.session.cookies.set(name, None)

    def clear(self):
        if self._owner.mode == 'd' and self._owner._has_driver:
            super().clear()
        elif self._owner.mode == 's' and self._owner._has_session:
            self._owner.session.cookies.clear()


class MixTabCookiesSetter(CookiesSetter):
    def __call__(self, cookies):
        if self._owner._d_mode and self._owner._driver.is_running:
            super().__call__(cookies)
        elif not self._owner._d_mode and self._owner._session:
            set_session_cookies(self._owner.session, cookies)

    def remove(self, name, url=None, domain=None, path=None):
        if self._owner._d_mode and self._owner._driver.is_running:
            super().remove(name, url, domain, path)
        elif not self._owner._d_mode and self._owner._session:
            if url or domain or path:
                raise ValueError(_S._lang.join(_S._lang.D_MODE_ONLY))
            self._owner.session.cookies.set(name, None)

    def clear(self):
        if self._owner._d_mode and self._owner._driver.is_running:
            super().clear()
        elif not self._owner._d_mode and self._owner._session:
            self._owner.session.cookies.clear()
