# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from time import sleep

from .chromium_tab import ChromiumTab
from .._browsers.chromium import Chromium
from .._functions.settings import Settings
from .._units.setter import ChromiumPageSetter
from .._units.waiter import ChromiumPageWaiter


class ChromiumPage(ChromiumTab):
    _PAGES = {}

    def __new__(cls, addr_or_opts=None, tab_id=None):
        browser = Chromium(addr_or_opts=addr_or_opts)
        if browser.id in cls._PAGES:
            r = cls._PAGES[browser.id]
            while not hasattr(r, '_inited'):
                sleep(.05)
            return r

        r = object.__new__(cls)
        r._browser = browser
        cls._PAGES[browser.id] = r
        return r

    def __init__(self, addr_or_opts=None, tab_id=None):
        self.tab = self
        if not tab_id:
            tab_id = self._browser._get_tab(as_id=True, context_id=self.browser._browser_id)
        ChromiumTab.__init__(self, self._browser, tab_id, context_id=self.browser._browser_id)
        self._type = 'ChromiumPage'
        self._tab = self
        self._browser._dl_mgr._page_id = self.tab_id

    def __repr__(self):
        return f'<ChromiumPage browser_id={self._browser.id} tab_id={self.tab_id}>'

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
    def tabs_count(self):
        return self._browser.tabs_count

    @property
    def tab_ids(self):
        return self._browser.tab_ids

    @property
    def latest_tab(self):
        return self._browser._get_tab(id_or_num=self.tab_ids[0], as_id=not Settings.singleton_tab_obj,
                                      context_id=self.browser._browser_id)

    @property
    def process_id(self):
        return self._browser.process_id

    @property
    def browser_version(self):
        return self._browser.version

    @property
    def address(self):
        return self._browser.address

    def get_tab(self, id_or_num=None, title=None, url=None, tab_type='page', as_id=False):
        return self._browser._get_tab(id_or_num=id_or_num, title=title, url=url,
                                      tab_type=tab_type, as_id=as_id, context_id=self.browser._browser_id)

    def get_tabs(self, title=None, url=None, tab_type='page', as_id=False):
        return self._browser._get_tabs(title=title, url=url, tab_type=tab_type, as_id=as_id)

    def new_tab(self, url=None, new_window=False, background=False, hidden=False):
        return self._browser.new_tab(url=url, new_window=new_window, background=background, hidden=hidden)

    def activate_tab(self, id_ind_tab):
        self._browser.activate_tab(id_ind_tab)

    def close_tabs(self, tabs_or_ids, others=False):
        self._browser.close_tabs(tabs_or_ids=tabs_or_ids, others=others)

    def quit(self, timeout=5, force=True, del_data=False):
        self._browser.quit(timeout, force, del_data=del_data)

    def _on_disconnect(self):
        ChromiumPage._PAGES.pop(self._browser.id, None)
