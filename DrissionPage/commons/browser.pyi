# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union

from DrissionPage.configs.chromium_options import ChromiumOptions
from DrissionPage.configs.driver_options import DriverOptions


def connect_browser(option: Union[ChromiumOptions, DriverOptions]) -> tuple: ...


def get_launch_args(opt: Union[ChromiumOptions, DriverOptions]) -> list: ...


def set_prefs(opt: Union[ChromiumOptions, DriverOptions]) -> None: ...
