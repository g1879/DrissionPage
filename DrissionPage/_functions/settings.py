# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path


class Settings(object):
    raise_when_ele_not_found = False
    raise_when_click_failed = False
    raise_when_wait_failed = False
    singleton_tab_obj = True
    cdp_timeout = 30
    browser_connect_timeout = 30
    auto_handle_alert = None
    _suffixes_list = str(Path(__file__).parent.absolute() / 'suffixes.dat').replace('\\', '/')

    @property
    def suffixes_list_path(self):
        return Settings._suffixes_list

    @suffixes_list_path.setter
    def suffixes_list_path(self, path):
        Settings._suffixes_list = str(Path(path).absolute()).replace('\\', '/')
