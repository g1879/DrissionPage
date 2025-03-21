# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from os import popen
from pathlib import Path
from threading import Lock
from typing import Union, Tuple

from .._base.chromium import Chromium
from .._pages.chromium_base import ChromiumBase


class PortFinder(object):
    used_port: set = ...
    prev_time: float = ...
    lock: Lock = ...
    tmp_dir: Path = ...
    checked_paths: set = ...

    def __init__(self, path: Union[str, Path] = None):
        """
        :param path: 临时文件保存路径，为None时使用系统临时文件夹
        """
        ...

    @staticmethod
    def get_port(scope: Tuple[int, int] = None) -> Tuple[int, str]:
        """查找一个可用端口
        :param scope: 指定端口范围，不含最后的数字，为None则使用[9600-59600)
        :return: 可以使用的端口和用户文件夹路径组成的元组
        """
        ...


def port_is_using(ip: str, port: Union[str, int]) -> bool:
    """检查端口是否被占用
    :param ip: 浏览器地址
    :param port: 浏览器端口
    :return: bool
    """
    ...


def clean_folder(folder_path: Union[str, Path], ignore: Union[tuple, list] = None) -> None:
    """清空一个文件夹，除了ignore里的文件和文件夹
    :param folder_path: 要清空的文件夹路径
    :param ignore: 忽略列表
    :return: None
    """
    ...


def show_or_hide_browser(tab: ChromiumBase, hide: bool = True) -> None:
    """执行显示或隐藏浏览器窗口
    :param tab: ChromiumTab对象
    :param hide: 是否隐藏
    :return: None
    """
    ...


def get_browser_progress_id(progress: Union[popen, None], address: str) -> Union[str, None]:
    """获取浏览器进程id
    :param progress: 已知的进程对象，没有时传入None
    :param address: 浏览器管理地址，含端口
    :return: 进程id或None
    """
    ...


def get_hwnds_from_pid(pid: Union[str, int], title: str) -> list:
    """通过PID查询句柄ID
    :param pid: 进程id
    :param title: 窗口标题
    :return: 进程句柄组成的列表
    """
    ...


def wait_until(function: callable, kwargs: dict = None, timeout: float = 10):
    """等待传入的方法返回值不为假
    :param function: 要执行的方法
    :param kwargs: 方法参数
    :param timeout: 超时时间（秒）
    :return: 执行结果，超时抛出TimeoutError
    """
    ...


def configs_to_here(save_name: Union[Path, str] = None) -> None:
    """把默认ini文件复制到当前目录
    :param save_name: 指定文件名，为None则命名为'dp_configs.ini'
    :return: None
    """
    ...


def raise_error(result: dict, browser: Chromium, ignore=None, user: bool = False) -> None:
    """抛出error对应报错
    :param result: 包含error的dict
    :param browser: 浏览器对象
    :param ignore: 要忽略的错误
    :param user: 是否用户调用的
    :return: None
    """
    ...
