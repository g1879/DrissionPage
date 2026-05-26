# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Optional

from .._configs.chromium_options import ChromiumOptions


def connect_browser(opt: ChromiumOptions) -> Optional[str]:
    """连接浏览器，如浏览器不存在，启动它再连接
    :param opt: ChromiumOptions对象
    :return: 新创建的浏览器返回命令行参数，接管的浏览器返回None
    """
    ...


def get_launch_args(opt: ChromiumOptions) -> list:
    """从ChromiumOptions获取命令行启动参数
    :param opt: ChromiumOptions
    :return: 启动参数列表
    """
    ...


def set_prefs(opt: ChromiumOptions) -> None:
    """处理启动配置中的prefs项，目前只能对已存在文件夹配置
    :param opt: ChromiumOptions
    :return: None
    """
    ...


def set_flags(opt: ChromiumOptions) -> None:
    """处理启动配置中的flags项
    :param opt: ChromiumOptions
    :return: None
    """
    ...


def test_connect(ip: str, port: Union[int, str], timeout: float = 30) -> bool:
    """测试浏览器是否可用
    :param ip: 浏览器ip
    :param port: 浏览器端口
    :param timeout: 超时时间（秒）
    :return: None
    """
    ...


def get_chrome_path() -> Optional[str]:
    """获取chrome可执行文件的路径"""
    ...


def get_edge_path() -> str:
    """获取edge可执行文件路径"""
    ...


def get_sys_Chrome_user_data_dir() -> Path:
    """获取系统Chrome用户文件夹路径"""
    ...


def get_edge_user_data_dir() -> Path:
    """获取系统Chrome用户文件夹路径"""
    ...
