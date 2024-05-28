# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Union

from .._configs.chromium_options import ChromiumOptions


def connect_browser(option: ChromiumOptions) -> bool: ...


def get_launch_args(opt: ChromiumOptions) -> list: ...


def set_prefs(opt: ChromiumOptions) -> None: ...


def set_flags(opt: ChromiumOptions) -> None: ...


def test_connect(ip: str, port: Union[int, str], timeout: float = 30) -> None: ...


def get_chrome_path(ini_path: str) -> Union[str, None]: ...
