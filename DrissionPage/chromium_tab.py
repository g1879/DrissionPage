# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from .chromium_base import ChromiumBase


class ChromiumTab(ChromiumBase):
    """实现浏览器标签页的类"""

    def __init__(self, page, tab_id=None):
        """初始化                                                      \n
        :param page: ChromiumPage对象
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        """
        self.page = page
        super().__init__(page.address, tab_id, page.timeout)

    def _set_options(self):
        self.set_timeouts(page_load=self.page.timeouts.page_load,
                          script=self.page.timeouts.script,
                          implicit=self.page.timeouts.implicit if self.timeout is None else self.timeout)
        self._page_load_strategy = self.page.page_load_strategy
