# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from .chromium_base import ChromiumBase
from .chromium_page import ChromiumPage


class ChromiumTab(ChromiumBase):

    def __init__(self, page:ChromiumPage, tab_id: str = ...):
        self.page: ChromiumPage = ...

    def _set_options(self) -> None: ...
