# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from .chromium_page import ChromiumPage
from .session_page import SessionPage
from .._base.base import BasePage
from .._configs.chromium_options import ChromiumOptions
from .._configs.session_options import SessionOptions
from .._functions.cookies import set_session_cookies, set_tab_cookies
from .._functions.settings import Settings as _S
from .._units.setter import WebPageSetter


class WebPage(SessionPage, ChromiumPage, BasePage):
    def __new__(cls, mode='d', timeout=None, chromium_options=None, session_or_options=None):
        # 即将废弃timeout
        return super().__new__(cls, chromium_options)

    def __init__(self, mode='d', timeout=None, chromium_options=None, session_or_options=None):
        # 即将废弃timeout
        if hasattr(self, '_created'):
            return

        mode = mode.lower()
        if mode not in ('s', 'd'):
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_VAL_, 'mode', ALLOW_VAL='"s", "d"', CURR_VAL=mode))
        self._d_mode = mode == 'd'
        self._has_driver = True
        self._has_session = True

        super().__init__(session_or_options=session_or_options)
        if not chromium_options:
            chromium_options = ChromiumOptions(read_file=chromium_options)
            chromium_options.set_timeouts(base=self._timeout).set_paths(download_path=self.download_path)
        super(SessionPage, self).__init__(addr_or_opts=chromium_options, timeout=timeout)  # 即将废弃timeout
        self._type = 'WebPage'
        self.change_mode(mode, go=False, copy_cookies=False)

    def __call__(self, locator, index=1, timeout=None):
        if self._d_mode:
            return super(SessionPage, self).__call__(locator, index=index, timeout=timeout)
        return super().__call__(locator, index=index)

    def __repr__(self):
        return f'<WebPage browser_id={self.browser.id} tab_id={self.tab_id}>'

    @property
    def latest_tab(self):
        return self.browser._get_tab(id_or_num=self.tab_ids[0], mix=True, as_id=not _S.singleton_tab_obj)

    @property
    def set(self):
        if self._set is None:
            self._set = WebPageSetter(self)
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
        if self._d_mode:
            return super(SessionPage, self).html if self._has_driver else ''
        return super().raw_data

    @property
    def html(self):
        if self._d_mode:
            return super(SessionPage, self).html if self._has_driver else ''
        return super().html

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
    def session(self):
        if self._session is None:
            self._create_session()
        return self._session

    @property
    def _session_url(self):
        return self._response.url if self._response else None

    @property
    def timeout(self):
        return self.timeouts.base if self._d_mode else self._timeout

    @property
    def download_path(self):
        return self.browser.download_path

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        if self._d_mode:
            return super(SessionPage, self).get(url, show_errmsg, retry, interval, timeout)

        if timeout is None:
            timeout = self.timeouts.page_load if self._has_driver else self.timeout
        return super().get(url, show_errmsg, retry, interval, timeout, **kwargs)

    def post(self, url, show_errmsg=False, retry=None, interval=None, **kwargs):
        if self.mode == 'd':
            self.cookies_to_session()
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

            self._url = None if not self._has_driver else super(SessionPage, self).url
            self._has_driver = True
            if self._session_url:
                if copy_cookies:
                    self.cookies_to_browser()
                if go:
                    self.get(self._session_url)

            return

        # d模式转s模式
        self._has_session = True
        self._url = self._session_url

        if self._has_driver and self._driver.is_running:
            if copy_cookies:
                self.cookies_to_session()
            if go and not self.get(super(SessionPage, self).url):
                raise ConnectionError(_S._lang.join(_S._lang.S_MODE_GET_FAILED))

    def cookies_to_session(self, copy_user_agent=True):
        if not self._has_session:
            return

        if copy_user_agent:
            user_agent = self._run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']
            self._headers.update({"User-Agent": user_agent})

        set_session_cookies(self.session, super(SessionPage, self).cookies())

    def cookies_to_browser(self):
        if not self._has_driver:
            return
        set_tab_cookies(self, super().cookies())

    def cookies(self, all_domains=False, all_info=False):
        return super(SessionPage, self).cookies(all_domains, all_info) if self._d_mode \
            else super().cookies(all_domains, all_info)

    def get_tab(self, id_or_num=None, title=None, url=None, tab_type='page', as_id=False):
        return self.browser._get_tab(id_or_num=id_or_num, title=title, url=url,
                                     tab_type=tab_type, mix=True, as_id=as_id)

    def get_tabs(self, title=None, url=None, tab_type='page', as_id=False):
        return self.browser._get_tabs(title=title, url=url, tab_type=tab_type, mix=True, as_id=as_id)

    def new_tab(self, url=None, new_window=False, background=False, new_context=False):
        return self.browser._new_tab(url=url, new_window=new_window, background=background, new_context=new_context)

    def close_driver(self):
        if self._has_driver:
            self.change_mode('s')
            try:
                self.driver.run('Browser.close')
            except Exception:
                pass
            self._driver.stop()
            self._driver = None
            self._has_driver = None

    def close_session(self):
        if self._has_session:
            self.change_mode('d')
            self._session.close()
            if self._response is not None:
                self._response.close()
            self._session = None
            self._response = None
            self._has_session = None

    def close(self):
        if self._has_driver:
            self.browser._close_tab(self)
        if self._session:
            self._session.close()
            if self._response is not None:
                self._response.close()

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        if self._d_mode:
            return super(SessionPage, self)._find_elements(locator, timeout=timeout, index=index, relative=relative)
        return super()._find_elements(locator, index=index, timeout=timeout)

    def quit(self, timeout=5, force=True, del_data=False):
        if self._has_session:
            self._session.close()
            self._session = None
            self._response = None
            self._has_session = None
        if self._has_driver:
            super(SessionPage, self).quit(timeout, force, del_data=del_data)
            self._driver = None
            self._has_driver = None

    def _set_session_options(self, session_or_options=None):
        if session_or_options is None:
            session_or_options = self.browser._session_options or SessionOptions(
                read_file=self.browser._session_options is None)
        super()._set_session_options(session_or_options)
