# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from .chromium_tab import ChromiumTab
from .._base.base import BasePage
from .._configs.session_options import SessionOptions
from .._functions.cookies import set_session_cookies, set_tab_cookies
from .._functions.settings import Settings as _S
from .._pages.session_page import SessionPage
from .._units.setter import MixTabSetter


class MixTab(SessionPage, ChromiumTab, BasePage):
    def __init__(self, browser, tab_id):
        if _S.singleton_tab_obj and hasattr(self, '_created'):
            return
        self._d_mode = True
        self._session_options = None
        self._headers = None
        self._response = None
        self._session = None
        self._encoding = None
        self._timeout = 10
        super(SessionPage, self).__init__(browser=browser, tab_id=tab_id)
        self._type = 'MixTab'

    def __call__(self, locator, index=1, timeout=None):
        return super(SessionPage, self).__call__(locator, index=index, timeout=timeout) if self._d_mode \
            else super().__call__(locator, index=index)

    def __repr__(self):
        return f'<MixTab browser_id={self.browser.id} tab_id={self.tab_id}>'

    @property
    def set(self):
        if self._set is None:
            self._set = MixTabSetter(self)
        return self._set

    @property
    def url(self):
        return self._browser_url if self._d_mode else self._session_url

    @property
    def _browser_url(self):
        return super(SessionPage, self).url if self._driver else None

    @property
    def title(self):
        return super(SessionPage, self).title if self._d_mode else super().title

    @property
    def raw_data(self):
        return super(SessionPage, self).html if self._d_mode else super().raw_data

    @property
    def html(self):
        return super(SessionPage, self).html if self._d_mode else super().html

    @property
    def json(self):
        return super(SessionPage, self).json if self._d_mode else super().json

    @property
    def response(self):
        return self._response

    @property
    def mode(self):
        return 'd' if self._d_mode else 's'

    @property
    def user_agent(self):
        return super(SessionPage, self).user_agent if self._d_mode else super().user_agent

    @property
    def _session_url(self):
        return self._response.url if self._response else None

    @property
    def timeout(self):
        return self.timeouts.base if self._d_mode else self._timeout

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        if self._d_mode:
            if kwargs:
                raise ValueError(_S._lang.join(_S._lang.S_MODE_ONLY, ARGS=", ".join(kwargs.keys())))
            return super(SessionPage, self).get(url, show_errmsg, retry, interval, timeout)

        if timeout is None:
            timeout = self.timeouts.page_load
        return super().get(url, show_errmsg, retry, interval, timeout, **kwargs)

    def post(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        if self.mode == 'd':
            self.cookies_to_session()
        if timeout is None:
            kwargs['timeout'] = self.timeouts.page_load
        if self._session is None:
            self._create_session()
        super().post(url, show_errmsg, retry, interval, **kwargs)
        return self.response

    def ele(self, locator, index=1, timeout=None):
        return (super(SessionPage, self).ele(locator, index=index, timeout=timeout)
                if self._d_mode else super().ele(locator, index=index))

    def eles(self, locator, timeout=None):
        return super(SessionPage, self).eles(locator, timeout=timeout) if self._d_mode else super().eles(locator)

    def s_ele(self, locator=None, index=1, timeout=None):
        return (super(SessionPage, self).s_ele(locator, index=index, timeout=timeout)
                if self._d_mode else super().s_ele(locator, index=index, timeout=timeout))

    def s_eles(self, locator, timeout=None):
        return (super(SessionPage, self).s_eles(locator, timeout=timeout)
                if self._d_mode else super().s_eles(locator, timeout=timeout))

    def change_mode(self, mode=None, go=True, copy_cookies=True):
        if mode:
            mode = mode.lower()
        if mode is not None and ((mode == 'd' and self._d_mode) or (mode == 's' and not self._d_mode)):
            return

        self._d_mode = not self._d_mode

        # s模式转d模式
        if self._d_mode:
            if self._driver is None or not self._driver.is_running:
                self._driver_init(self.tab_id)
                self._get_document()

            self._url = super(SessionPage, self).url
            if self._session_url:
                if copy_cookies:
                    self.cookies_to_browser()
                if go:
                    self.get(self._session_url)

            return

        # d模式转s模式
        if self._session is None:
            self._set_session_options(
                self.browser._session_options or SessionOptions(read_file=self.browser._session_options is None))
            self._create_session()

        self._url = self._session_url
        if self._driver:
            if copy_cookies:
                self.cookies_to_session()

            if go:
                url = super(SessionPage, self).url
                if url.startswith('http'):
                    self.get(url)

    def cookies_to_session(self, copy_user_agent=True):
        if not self._session:
            return

        if copy_user_agent:
            user_agent = self._run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']
            self._headers.update({"User-Agent": user_agent})

        set_session_cookies(self.session, super(SessionPage, self).cookies())

    def cookies_to_browser(self):
        if self._driver is None or not self._driver.is_running:
            return
        set_tab_cookies(self, super().cookies())

    def cookies(self, all_domains=False, all_info=False):
        return super(SessionPage, self).cookies(all_domains, all_info) if self._d_mode \
            else super().cookies(all_domains, all_info)

    def close(self, others=False, session=False):
        if others:
            self.browser.close_tabs(self.tab_id, others=True)
        else:
            self.browser._close_tab(self)
        if session and self._session:
            self._session.close()
            if self._response is not None:
                self._response.close()

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        return super(SessionPage, self)._find_elements(locator, timeout=timeout, index=index, relative=relative) \
            if self._d_mode else super()._find_elements(locator, index=index, timeout=timeout)

    def _set_session_options(self, session_or_options=None):
        if session_or_options is None:
            session_or_options = self.browser._session_options or SessionOptions(
                read_file=self.browser._session_options is None)
        super()._set_session_options(session_or_options)
