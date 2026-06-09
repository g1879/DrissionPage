# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from copy import copy
from threading import Lock
from time import sleep

from .._functions.cookies import set_session_cookies, set_tab_cookies
from .._functions.settings import Settings as _S
from .._functions.web import save_page
from .._pages.chromium_base import ChromiumBase
from .._pages.session_page import SessionPage
from .._units.setter import ChromiumTabSetter
from .._units.waiter import ChromiumTabWaiter


class ChromiumTab(ChromiumBase, SessionPage):
    _TABS = {}
    _lock = Lock()

    def __new__(cls, browser, tab_id, context_id):
        with cls._lock:
            if _S.singleton_tab_obj and tab_id in cls._TABS:
                r = cls._TABS[tab_id]
                while not hasattr(r, '_inited'):
                    sleep(.01)
                return r
            r = object.__new__(cls)
            cls._TABS[tab_id] = r
            return r

    def __init__(self, browser, tab_id, context_id):
        if _S.singleton_tab_obj and hasattr(self, '_created'):
            return
        self._created = True
        self._d_mode = True
        self._mode_obj = super()
        self._response = None
        self._encoding = None
        super().__init__(browser, tab_id, context_id)
        self._tab = self
        self._type = 'ChromiumTab'

    def __call__(self, locator, index=1, timeout=None):
        return self._mode_obj.__call__(locator, index=index, timeout=timeout)

    def __repr__(self):
        return f'<ChromiumTab browser_id={self.browser.id} tab_id={self.tab_id}>'

    def _d_set_runtime_settings(self):
        self._timeouts = copy(self.browser.timeouts)
        self.retry_times = self.browser.retry_times
        self.retry_interval = self.browser.retry_interval
        self._load_mode = self.browser._load_mode
        self._download_path = self.browser.download_path
        self._auto_handle_alert = self.browser._auto_handle_alert
        self._none_ele_return_value = self.browser._none_ele_return_value
        self._none_ele_value = self.browser._none_ele_value

    @property
    def set(self):
        if self._set is None:
            self._set = ChromiumTabSetter(self)
        return self._set

    @property
    def wait(self):
        if self._wait is None:
            self._wait = ChromiumTabWaiter(self)
        return self._wait

    @property
    def url(self):
        return self._browser_url if self._d_mode else self._session_url

    @property
    def _browser_url(self):
        return super().url if self._messenger_running else None

    @property
    def title(self):
        return self._mode_obj.title

    @property
    def raw_data(self):
        return self._mode_obj.html if self._d_mode else self._mode_obj.raw_data

    @property
    def html(self):
        return self._mode_obj.html

    @property
    def json(self):
        return self._mode_obj.json

    @property
    def response(self):
        return self._response

    @property
    def mode(self):
        return 'd' if self._d_mode else 's'

    @property
    def user_agent(self):
        return self._mode_obj.user_agent

    @property
    def _session_url(self):
        return self._response.url if self._response else None

    @property
    def timeout(self):
        return self.timeouts.base if self._d_mode else self._timeout

    def activate(self):
        self.browser._run_cdp('Target.activateTarget', targetId=self._target_id)

    def get(self, url, retry=None, interval=None, timeout=None, raise_err=False, **kwargs):
        if self._d_mode:
            if kwargs:
                raise ValueError(_S._lang.joinn(_S._lang.S_MODE_ONLY, ARGS=", ".join(kwargs.keys())))
            return self._mode_obj.get(url=url, retry=retry, interval=interval, timeout=timeout, raise_err=raise_err)

        if timeout is None:
            timeout = self.timeouts.page_load
        return self._mode_obj.get(url=url, retry=retry, interval=interval, timeout=timeout,
                                  raise_err=raise_err, **kwargs)

    def post(self, url, retry=None, interval=None, timeout=None, raise_err=False, **kwargs):
        if self.mode == 'd':
            self.cookies_to_session()
        if timeout is None:
            kwargs['timeout'] = self.timeouts.page_load
        if self._session is None:
            self._create_session()
        return self._mode_obj.post(url=url, retry=retry, interval=interval, raise_err=raise_err, **kwargs)

    def ele(self, locator, index=1, timeout=None):
        return self._mode_obj.ele(locator, index=index, timeout=timeout)

    def eles(self, locator, timeout=None):
        return self._mode_obj.eles(locator, timeout=timeout)

    def s_ele(self, locator=None, index=1, timeout=None):
        return self._mode_obj.s_ele(locator, index=index, timeout=timeout)

    def s_eles(self, locator, timeout=None):
        return self._mode_obj.s_eles(locator, timeout=timeout)

    def change_mode(self, mode=None, go=True, copy_cookies=True):
        if mode:
            mode = mode.lower()
        if (mode == 'd' and self._d_mode) or (mode == 's' and not self._d_mode):
            return

        self._d_mode = not self._d_mode
        self._mode_obj = super() if self._d_mode else super(ChromiumBase, self)

        # s模式转d模式
        if self._d_mode:
            if not self._messenger_running:
                self._driver_init()
                self._get_document()

            self._url = super().url
            if self._session_url:
                if copy_cookies:
                    self.cookies_to_browser()
                if go:
                    self.get(self._session_url)

            return

        # d模式转s模式
        if self._session is None:
            self._set_session_options()
            self._create_session()

        self._url = self._session_url
        if self._messenger_running:
            if copy_cookies:
                self.cookies_to_session()
            if go:
                url = super().url
                if url.startswith('http'):
                    self.get(url)

    def cookies_to_session(self, copy_user_agent=True):
        if not self._session:
            return

        if copy_user_agent:
            user_agent = self._run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']
            self._headers.update({"User-Agent": user_agent})

        set_session_cookies(self.session, super().cookies())

    def cookies_to_browser(self):
        if not self._messenger_running:
            return
        set_tab_cookies(self, super(ChromiumBase, self).cookies())

    def cookies(self, all_domains=False, all_info=False):
        return self._mode_obj.cookies(all_domains, all_info)

    def close(self, others=False, session=False):
        if others:
            self.browser.close_tabs(self.tab_id, others=True)
        else:
            self.browser._close_tab(self)
        if session and self._session and not others:
            self._session.close()
            if self._response is not None:
                self._response.close()

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        return self._mode_obj._find_elements(locator, timeout=timeout, index=index, relative=relative)

    def save(self, path=None, name=None, as_pdf=False, **kwargs):
        return save_page(self, path, name, as_pdf, kwargs)

    def _on_disconnect(self):
        if not self._disconnect_flag:
            ChromiumTab._TABS.pop(self.tab_id, None)
