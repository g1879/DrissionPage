# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from .chromium_base import ChromiumBase


class ChromiumTab(ChromiumBase):
    """实现浏览器标签页的类"""

    def __init__(self, page, tab_id=None):
        """
        :param page: ChromiumPage对象
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        """
        self.page = page
        super().__init__(page.address, tab_id, page.timeout)

    def _set_runtime_settings(self):
        """重写设置浏览器运行参数方法"""
        self._timeouts = self.page.timeouts
        self._page_load_strategy = self.page.page_load_strategy
