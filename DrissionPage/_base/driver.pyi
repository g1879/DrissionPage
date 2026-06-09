# -*- coding: utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from threading import Thread, Lock
from typing import Callable, Dict, Optional, Set

from requests import Response
from websocket import WebSocket

from .base import Messenger


class ThreadSafeDict:
    _lock: Lock = ...
    _dict: dict = ...

    def __getitem__(self, k): ...

    def __setitem__(self, k, v): ...

    def __delitem__(self, k): ...

    def get(self, k, default=None): ...

    def pop(self, item, default): ...

    def clear(self): ...


class Driver(object):
    _cur_id: int = ...
    _ws: Optional[WebSocket] = ...
    _recv_th: Thread = ...
    _handle_immediate_event_th: Optional[Thread] = ...
    _session_owner: Dict[str, Messenger] = ...
    address: str
    owner: Messenger = ...
    alert_flag: Set = ...
    is_running: bool = ...
    method_results: ThreadSafeDict = ...

    def __init__(self, address: str, owner: Messenger = None):
        """
        :param address: 浏览器连接地址
        :param owner: 创建这个驱动的对象
        """
        ...

    def _send(self, message: dict, timeout: float, ws_id: int) -> dict:
        """发送信息到浏览器，并返回浏览器返回的信息
        :param message: 发送给浏览器的数据
        :param timeout: 超时时间，为None表示无限
        :param ws_id: 信息id号
        :return: 浏览器返回的数据
        """
        ...

    def _recv_loop(self) -> None:
        """接收浏览器信息的守护线程方法"""
        ...

    def _handle_event_loop(self) -> None:
        """当接收到浏览器信息，执行已绑定的方法"""
        ...

    def _handle_immediate_event_loop(self): ...

    def _handle_immediate_event(self, function: Callable, kwargs: dict):
        """处理立即执行的动作
        :param function: 要运行下方法
        :param kwargs: 方法参数
        :return: None
        """
        ...

    def run(self, _method: str, _timeout: Optional[float] = None, _session_id: Optional[str] = None, **kwargs) -> dict:
        """执行cdp方法
        :param _method: cdp方法名
        :param _timeout: 超时时间
        :param _session_id: session id
        :param kwargs: cdp参数
        :return: 执行结果
        """
        ...

    def add_session_owner(self, session_id: Optional[str], obj: Messenger) -> None: ...

    def remove_session_owner(self, session_id: str) -> None: ...

    def start(self) -> bool:
        """启动连接"""
        ...

    def stop(self) -> bool:
        """中断连接"""
        ...

    def _stop(self) -> None:
        """中断连接"""
        ...

    @staticmethod
    def get(url) -> Response:
        """
        :param url: 要访问的链接
        :return: Response对象
        """
        ...


class DebugDriver(Driver): ...
