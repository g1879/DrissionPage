# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from queue import Queue
from typing import Optional, Iterable, List, Union, Any

from .._pages.chromium_base import ChromiumBase


class Console(object):
    listening: bool = ...
    _owner: ChromiumBase = ...
    _caught: Optional[Queue] = ...
    _not_enabled: bool = ...

    def __init__(self, owner: ChromiumBase) -> None:
        """
        :param owner: 页面对象
        """
        ...

    @property
    def messages(self) -> List[ConsoleData]:
        """以list方式返回获取到的信息，返回后会清空列表"""
        ...

    def start(self) -> None:
        """开启console监听"""
        ...

    def stop(self) -> None:
        """停止监听，清空已监听到的列表"""
        ...

    def clear(self) -> None:
        """清空已获取但未返回的信息"""
        ...

    def wait(self, timeout: float = None) -> Union[ConsoleData, False]:
        """等待一条信息
        :param timeout: 超时时间（秒）
        :return: ConsoleData对象
        """
        ...

    def steps(self, timeout: Optional[float] = None) -> Iterable[ConsoleData]:
        """每监听到一个信息就返回，用于for循环
        :param timeout: 等待一个信息的超时时间，为None无限等待
        :return: None
        """
        ...

    def _console(self, **kwargs) -> None: ...


class ConsoleData(object):
    __slots__ = ('_data', 'source', 'level', 'text', 'url', 'line', 'column')

    def __init__(self, data: dict) -> None: ...

    def __getattr__(self, item: str) -> str: ...

    @property
    def body(self) -> Any: ...
