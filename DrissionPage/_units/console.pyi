# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from queue import Queue
from typing import Optional, Iterable, List, Union

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

    def _onEntryAdded(self, **kwargs) -> None: ...

    def _onConsoleAPICalled(self, **kwargs) -> None: ...


class ConsoleData(object):
    __slots__ = ('_data', 'source', 'level', 'text', 'url', 'lineNumber', 'column', 'timestamp',
                 'stackTrace', 'type', 'args')

    def __init__(self, data: dict) -> None: ...

    @property
    def data(self) -> dict:
        """返回完整信息"""
        ...

    @property
    def source(self) -> str:
        """返回信息来源：xml、javascript、network、storage、appcache、rendering、security、deprecation、worker、
            violation、intervention、recommendation、other"""
        ...

    @property
    def level(self) -> str:
        """返回日志条目严重性等级：verbose、info、warning、error"""
        ...

    @property
    def text(self) -> str:
        """返回信息文本"""
        ...

    @property
    def url(self) -> str:
        """返回资源url（如有）"""
        ...

    @property
    def lineNumber(self) -> int:
        """返回js中的行号"""
        ...

    @property
    def timestamp(self) -> float:
        """返回时间戳"""
        ...

    @property
    def stackTrace(self) -> dict:
        """返回js堆栈跟踪"""
        ...

    @property
    def type(self) -> str:
        """返回调用的类型：log、debug、info、error、warning、dir、dirxml、table、trace、clear、startGroup、
            startGroupCollapsed、endGroup、assert、profile、profileEnd、count、timeEnd"""
        ...

    @property
    def args(self) -> List[dict]:
        """返回js调用参数"""
        ...
