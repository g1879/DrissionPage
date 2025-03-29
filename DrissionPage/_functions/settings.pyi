# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Optional, Union, Literal

from .texts import Texts


class Settings(object):
    raise_when_ele_not_found: bool = ...
    raise_when_click_failed: bool = ...
    raise_when_wait_failed: bool = ...
    singleton_tab_obj: bool = ...
    cdp_timeout: float = ...
    browser_connect_timeout: float = ...
    auto_handle_alert: Optional[bool] = ...
    _lang: Texts = ...
    suffixes_list: str = ...

    @classmethod
    def set_raise_when_ele_not_found(cls, on_off: bool = True) -> Settings:
        """设置找不到元素时是否立即抛出异常
        :param on_off: bool表示开或关
        :return: None
        """
        ...

    @classmethod
    def set_raise_when_click_failed(cls, on_off: bool = True) -> Settings:
        """设置点击失败时是否立即抛出异常
        :param on_off: bool表示开或关
        :return: None
        """
        ...

    @classmethod
    def set_raise_when_wait_failed(cls, on_off: bool = True) -> Settings:
        """设置等待失败时是否立即抛出异常
        :param on_off: bool表示开或关
        :return: None
        """
        ...

    @classmethod
    def set_singleton_tab_obj(cls, on_off: bool = True) -> Settings:
        """设置是否开启tab单例模式
        :param on_off: bool表示开或关
        :return: None
        """
        ...

    @classmethod
    def set_cdp_timeout(cls, second: float) -> Settings:
        """设置csp执行超时时间（秒）
        :param second: 超时秒数
        :return: None
        """
        ...

    @classmethod
    def set_browser_connect_timeout(cls, second: float) -> Settings:
        """设置等待浏览器连接超时时间（秒）
        :param second: 超时秒数
        :return: None
        """
        ...

    @classmethod
    def set_auto_handle_alert(cls, accept: Optional[bool] = True) -> Settings:
        """设置是否自动处理js弹出信息
        :param accept: None为不处理，True为接受，False为取消
        :return: None
        """
        ...

    @classmethod
    def set_language(cls, code: Literal['zh_cn', 'en']) -> Settings:
        """设置报错和提示信息使用的语言
        :param code: 表示语言的文本'zh_cn', 'en'
        :return: None
        """
        ...

    @classmethod
    def set_suffixes_list(cls, path: Union[str, Path]) -> Settings:
        """设置用于识别域名后缀的文件路径
        :param path: 文件路径
        :return: None
        """
        ...
