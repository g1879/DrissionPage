# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from ._pages.chromium_page import ChromiumPage
from ._pages.session_page import SessionPage
from ._pages.web_page import WebPage

# 启动配置类
from ._configs.chromium_options import ChromiumOptions
from ._configs.session_options import SessionOptions

__all__ = ['ChromiumPage', 'ChromiumOptions', 'SessionOptions', 'SessionPage', 'WebPage', '__version__']
__version__ = '4.0.5.4'
