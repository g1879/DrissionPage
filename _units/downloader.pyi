# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Dict, Optional, Union, Literal, Set

from .._base.chromium import Chromium
from .._pages.chromium_base import ChromiumBase

FILE_EXISTS = Literal['skip', 'rename', 'overwrite', 's', 'r', 'o']


class DownloadManager(object):
    _browser: Chromium = ...
    _missions: Dict[str, DownloadMission] = ...
    _tab_missions: Dict[str, Set[DownloadMission]] = ...
    _flags: dict = ...
    _waiting_tab: set = ...
    _running: bool = ...
    _tmp_path: str = ...
    _page_id: Optional[str] = ...

    def __init__(self, browser: Chromium):
        """
        :param browser: Browser对象
        """
        ...

    @property
    def missions(self) -> Dict[str, DownloadMission]:
        """返回所有未完成的下载任务"""
        ...

    def set_path(self, tab: Union[str, ChromiumBase], path: str) -> None:
        """设置某个tab的下载路径
        :param tab: 页面对象
        :param path: 下载路径（绝对路径str）
        :return: None
        """
        ...

    @staticmethod
    def set_rename(tab_id: str,
                   rename: str = None,
                   suffix: str = None) -> None:
        """设置某个tab的重命名文件名
        :param tab_id: tab id
        :param rename: 文件名，可不含后缀，会自动使用远程文件后缀
        :param suffix: 后缀名，显式设置后缀名，不使用远程文件后缀
        :return: None
        """
        ...

    @staticmethod
    def set_file_exists(tab_id: str, mode: FILE_EXISTS) -> None:
        """设置某个tab下载文件重名时执行的策略
        :param tab_id: tab id
        :param mode: 下载路径
        :return: None
        """
        ...

    def set_flag(self, tab_id: str, flag: Union[bool, DownloadMission, None]) -> None:
        """设置某个tab的重命名文件名
        :param tab_id: tab id
        :param flag: 等待标志
        :return: None
        """
        ...

    def get_flag(self, tab_id: str) -> Union[bool, DownloadMission, None]:
        """获取tab下载等待标记
        :param tab_id: tab id
        :return: 任务对象或False
        """
        ...

    def get_tab_missions(self, tab_id: str) -> list:
        """获取某个tab正在下载的任务
        :param tab_id:
        :return: 下载任务组成的列表
        """
        ...

    def set_done(self,
                 mission: DownloadMission,
                 state: str,
                 final_path: str = None) -> None:
        """设置任务结束
        :param mission: 任务对象
        :param state: 任务状态
        :param final_path: 最终路径
        :return: None
        """
        ...

    def cancel(self, mission: DownloadMission) -> None:
        """取消任务
        :param mission: 任务对象
        :return: None
        """
        ...

    def skip(self, mission: DownloadMission) -> None:
        """跳过任务
        :param mission: 任务对象
        :return: None
        """
        ...

    def clear_tab_info(self, tab_id: str) -> None:
        """当tab关闭时清除有关信息
        :param tab_id: 标签页id
        :return: None
        """
        ...

    def _onDownloadWillBegin(self, **kwargs) -> None:
        """用于获取弹出新标签页触发的下载任务"""
        ...

    def _onDownloadProgress(self, **kwargs) -> None:
        """下载状态变化时执行"""
        ...


class TabDownloadSettings(object):
    TABS: dict = ...
    tab_id: str = ...
    waiting_flag: Union[bool, dict, None] = ...
    rename: Optional[str] = ...
    suffix: Optional[str] = ...
    path: Optional[str] = ...
    when_file_exists: FILE_EXISTS = ...

    def __init__(self, tab_id: str):
        """
        :param tab_id: tab id
        """
        ...


class DownloadMission(object):
    tab_id: str = ...
    from_tab: Optional[str] = ...
    _mgr: DownloadManager = ...
    url: str = ...
    id: str = ...
    folder: str = ...
    name: str = ...
    state: str = ...
    total_bytes: Optional[int] = ...
    received_bytes: int = ...
    final_path: Optional[str] = ...
    tmp_path: str = ...
    _overwrite: bool = ...
    _is_done: bool = ...

    def __init__(self,
                 mgr: DownloadManager,
                 tab_id: str,
                 _id: str,
                 folder: str,
                 name: str,
                 url: str,
                 tmp_path: str,
                 overwrite: bool):
        """
        :param mgr: BrowserDownloadManager对象
        :param tab_id: 标签页id
        :param _id: 任务id
        :param folder: 最终保存文件夹路径
        :param name: 文件名
        :param url: url
        :param tmp_path: 下载临时路径
        :param overwrite: 是否已存在同名文件，None表示重命名
        """
        ...

    @property
    def rate(self) -> float:
        """以百分比形式返回下载进度"""
        ...

    @property
    def is_done(self) -> bool:
        """返回任务是否在运行中"""
        ...

    def cancel(self) -> None:
        """取消该任务，如任务已完成，删除已下载的文件"""
        ...

    def wait(self,
             show: bool = True,
             timeout=None,
             cancel_if_timeout=True) -> Union[bool, str]:
        """等待任务结束
        :param show: 是否显示下载信息
        :param timeout: 超时时间（秒），为None则无限等待
        :param cancel_if_timeout: 超时时是否取消任务
        :return: 等待成功返回完整路径，否则返回False
        """
        ...
