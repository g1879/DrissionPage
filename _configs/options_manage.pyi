# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from configparser import RawConfigParser
from pathlib import Path
from typing import Any, Optional, Union


class OptionsManager(object):
    """管理配置文件内容的类"""
    ini_path: Optional[Path] = ...
    file_exists: bool = ...
    _conf: RawConfigParser = ...

    def __init__(self, path: Union[Path, str] = None):
        """初始化，读取配置文件，如没有设置临时文件夹，则设置并新建
        :param path: ini文件的路径，为None则找项目文件夹下的，找不到则读取模块文件夹下的
        """
        ...

    def __getattr__(self, item) -> dict:
        """以dict形似返回获取大项信息
        :param item: 项名
        :return: None
        """
        ...

    def get_value(self, section: str, item: str) -> Any:
        """获取配置的值
        :param section: 段名
        :param item: 项名
        :return: 项值
        """
        ...

    def get_option(self, section: str) -> dict:
        """把section内容以字典方式返回
        :param section: 段名
        :return: 段内容生成的字典
        """
        ...

    def set_item(self, section: str, item: str, value: Any) -> None:
        """设置配置值
        :param section: 段名
        :param item: 项名
        :param value: 项值
        :return: None
        """
        ...

    def remove_item(self, section: str, item: str) -> None:
        """删除配置值
        :param section: 段名
        :param item: 项名
        :return: None
        """
        ...

    def save(self, path: str = None) -> str:
        """保存配置文件
        :param path: ini文件的路径，传入 'default' 保存到默认ini文件
        :return: 保存路径
        """
        ...

    def save_to_default(self) -> str:
        """保存当前配置到默认ini文件"""
        ...

    def show(self) -> None:
        """打印所有设置信息"""
        ...
