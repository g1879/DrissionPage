# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union

from .._configs.chromium_options import ChromiumOptions


def connect_browser(option: ChromiumOptions) -> bool:
    """连接或启动浏览器
    :param option: ChromiumOptions对象
    :return: 返回是否接管的浏览器
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


def get_chrome_path(ini_path: str) -> Union[str, None]:
    """从ini文件或系统变量中获取chrome可执行文件的路径
    :param ini_path: ini文件路径
    :return: 文件路径
    """
    ...
