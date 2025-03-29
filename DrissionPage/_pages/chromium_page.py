# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from time import sleep

from .._base.chromium import Chromium
from .._functions.settings import Settings
from .._functions.web import save_page
from .._pages.chromium_base import ChromiumBase
from .._units.setter import ChromiumPageSetter
from .._units.waiter import ChromiumPageWaiter


class ChromiumPage(ChromiumBase):
    _PAGES = {}

    def __new__(cls, addr_or_opts=None, tab_id=None, timeout=None):
        # 即将废弃timeout
        browser = Chromium(addr_or_opts=addr_or_opts)
        if browser.id in cls._PAGES:
            r = cls._PAGES[browser.id]
            while not hasattr(r, '_frame_id'):
                sleep(.05)
            return r

        r = object.__new__(cls)
        r._browser = browser
        cls._PAGES[browser.id] = r
        return r

    def __init__(self, addr_or_opts=None, tab_id=None, timeout=None):
        # 即将废弃timeout
        if hasattr(self, '_created'):
            return
        self._created = True

        self.tab = self
        super().__init__(self.browser, tab_id)
        self._type = 'ChromiumPage'
        self.set.timeouts(base=timeout)  # 即将废弃
        self._tab = self
        self._browser._dl_mgr._page_id = self.tab_id

    def __repr__(self):
        return f'<ChromiumPage browser_id={self.browser.id} tab_id={self.tab_id}>'

    def _d_set_runtime_settings(self):
        """设置运行时用到的属性"""
        self._timeouts = self.browser.timeouts
        self._load_mode = self.browser._load_mode
        self._download_path = self.browser.download_path
        self.retry_times = self.browser.retry_times
        self.retry_interval = self.browser.retry_interval
        self._auto_handle_alert = self.browser._auto_handle_alert

    @property
    def set(self):
        if self._set is None:
            self._set = ChromiumPageSetter(self)
        return self._set

    @property
    def wait(self):
        if self._wait is None:
            self._wait = ChromiumPageWaiter(self)
        return self._wait

    @property
    def browser(self):
        return self._browser

    @property
    def tabs_count(self):
        return self.browser.tabs_count

    @property
    def tab_ids(self):
        return self.browser.tab_ids

    @property
    def latest_tab(self):
        return self.browser._get_tab(id_or_num=self.tab_ids[0], as_id=not Settings.singleton_tab_obj)

    @property
    def process_id(self):
        return self.browser.process_id

    @property
    def browser_version(self):
        return self._browser.version

    @property
    def address(self):
        return self.browser.address

    @property
    def download_path(self):
        return self.browser.download_path

    def save(self, path=None, name=None, as_pdf=False, **kwargs):
        return save_page(self, path, name, as_pdf, kwargs)

    def get_tab(self, id_or_num=None, title=None, url=None, tab_type='page', as_id=False):
        return self.browser._get_tab(id_or_num=id_or_num, title=title, url=url,
                                     tab_type=tab_type, mix=False, as_id=as_id)

    def get_tabs(self, title=None, url=None, tab_type='page', as_id=False):
        return self.browser._get_tabs(title=title, url=url, tab_type=tab_type, mix=False, as_id=as_id)

    def new_tab(self, url=None, new_window=False, background=False, new_context=False):
        return self.browser._new_tab(False, url=url, new_window=new_window,
                                     background=background, new_context=new_context)

    def activate_tab(self, id_ind_tab):
        self.browser.activate_tab(id_ind_tab)

    def close(self):
        self.browser._close_tab(self)

    def close_tabs(self, tabs_or_ids, others=False):
        self.browser.close_tabs(tabs_or_ids=tabs_or_ids, others=others)

    def quit(self, timeout=5, force=True, del_data=False):
        self.browser.quit(timeout, force, del_data=del_data)

    def _on_disconnect(self):
        ChromiumPage._PAGES.pop(self._browser.id, None)
