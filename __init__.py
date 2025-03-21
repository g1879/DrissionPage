# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.

允许任何人以个人身份使用或分发本项目源代码，但仅限于学习和合法非盈利目的。
个人或组织如未获得版权持有人授权，不得将本项目以源代码或二进制形式用于商业行为。

使用本项目需满足以下条款，如使用过程中出现违反任意一项条款的情形，授权自动失效。
* 禁止将DrissionPage应用到任何可能违反当地法律规定和道德约束的项目中
* 禁止将DrissionPage用于任何可能有损他人利益的项目中
* 禁止将DrissionPage用于攻击与骚扰行为
* 遵守Robots协议，禁止将DrissionPage用于采集法律或系统Robots协议不允许的数据

使用DrissionPage发生的一切行为均由使用人自行负责。
因使用DrissionPage进行任何行为所产生的一切纠纷及后果均与版权持有人无关，
版权持有人不承担任何使用DrissionPage带来的风险和损失。
版权持有人不对DrissionPage可能存在的缺陷导致的任何损失负任何责任。
"""
from ._base.chromium import Chromium
from ._configs.chromium_options import ChromiumOptions
from ._configs.session_options import SessionOptions
from ._pages.chromium_page import ChromiumPage
from ._pages.session_page import SessionPage
from ._pages.web_page import WebPage
from .version import __version__
