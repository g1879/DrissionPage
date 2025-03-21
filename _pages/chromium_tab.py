# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from copy import copy
from time import sleep

from .._functions.settings import Settings
from .._functions.web import save_page
from .._pages.chromium_base import ChromiumBase
from .._units.setter import TabSetter
from .._units.waiter import TabWaiter


class ChromiumTab(ChromiumBase):
    _TABS = {}

    def __new__(cls, browser, tab_id):
        if Settings.singleton_tab_obj and tab_id in cls._TABS:
            r = cls._TABS[tab_id]
            while not hasattr(r, '_frame_id'):
                sleep(.05)
            return r
        r = object.__new__(cls)
        cls._TABS[tab_id] = r
        return r

    def __init__(self, browser, tab_id):
        if Settings.singleton_tab_obj and hasattr(self, '_created'):
            return
        self._created = True

        super().__init__(browser, tab_id)
        self._tab = self
        self._type = 'ChromiumTab'

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

    def close(self, others=False):
        if others:
            self.browser.close_tabs(self.tab_id, others=True)
        else:
            self.browser._close_tab(self)

    @property
    def set(self):
        if self._set is None:
            self._set = TabSetter(self)
        return self._set

    @property
    def wait(self):
        if self._wait is None:
            self._wait = TabWaiter(self)
        return self._wait

    def save(self, path=None, name=None, as_pdf=False, **kwargs):
        return save_page(self, path, name, as_pdf, kwargs)

    def _on_disconnect(self):
        if not self._disconnect_flag:
            ChromiumTab._TABS.pop(self.tab_id, None)
