# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path

from .texts import get_txt_class


class Settings(object):
    raise_when_ele_not_found = False
    raise_when_click_failed = False
    raise_when_wait_failed = False
    singleton_tab_obj = True
    cdp_timeout = 30
    browser_connect_timeout = 30
    auto_handle_alert = None
    suffixes_list = str(Path(__file__).parent.resolve() / 'suffixes.dat').replace('\\', '/')
    wait_stop_before_click = False
    _lang = get_txt_class(None)
    _debug = None  # 为None时不开启，为True或指定目标时全部开启，为False时由Messenger决定

    @classmethod
    def set_wait_stop_before_click(cls, on_off=True):
        cls.wait_stop_before_click = on_off
        return cls

    @classmethod
    def set_raise_when_ele_not_found(cls, on_off=True):
        cls.raise_when_ele_not_found = on_off
        return cls

    @classmethod
    def set_raise_when_click_failed(cls, on_off=True):
        cls.raise_when_click_failed = on_off
        return cls

    @classmethod
    def set_raise_when_wait_failed(cls, on_off=True):
        cls.raise_when_wait_failed = on_off
        return cls

    @classmethod
    def set_singleton_tab_obj(cls, on_off=True):
        cls.singleton_tab_obj = on_off
        return cls

    @classmethod
    def set_cdp_timeout(cls, second):
        cls.cdp_timeout = second
        return cls

    @classmethod
    def set_browser_connect_timeout(cls, second):
        cls.browser_connect_timeout = second
        return cls

    @classmethod
    def set_auto_handle_alert(cls, accept=True):
        cls.auto_handle_alert = accept
        return cls

    @classmethod
    def set_language(cls, code):
        cls._lang = get_txt_class(code)
        return cls

    @classmethod
    def set_suffixes_list(cls, path):
        cls.suffixes_list = str(Path(path).resolve()).replace('\\', '/')
        return cls
