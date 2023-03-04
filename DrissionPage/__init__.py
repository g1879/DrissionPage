# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
# 常用页面类
from .chromium_page import ChromiumPage
from .session_page import SessionPage
from .web_page import WebPage

# 启动配置类
from .configs.chromium_options import ChromiumOptions
from .configs.session_options import SessionOptions

# 旧版页面类和启动配置类
try:
    from .mixpage.mix_page import MixPage
    from .mixpage.drission import Drission
    from .configs.driver_options import DriverOptions
except ModuleNotFoundError:
    pass
