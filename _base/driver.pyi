# -*- coding: utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from queue import Queue
from threading import Thread
from typing import Union, Callable, Dict, Optional

from requests import Response
from websocket import WebSocket

from .._base.chromium import Chromium


class Driver(object):
    id: str
    address: str
    type: str
    owner = ...
    alert_flag: bool
    _websocket_url: str
    _cur_id: int
    _ws: Optional[WebSocket]
    _recv_th: Thread
    _handle_event_th: Thread
    _handle_immediate_event_th: Optional[Thread]
    is_running: bool
    event_handlers: dict
    immediate_event_handlers: dict
    method_results: dict
    event_queue: Queue
    immediate_event_queue: Queue

    def __init__(self, tab_id: str, tab_type: str, address: str, owner=None):
        """
        :param tab_id: 标签页id
        :param tab_type: 标签页类型
        :param address: 浏览器连接地址
        :param owner: 创建这个驱动的对象
        """
        ...

    def _send(self, message: dict, timeout: float = None) -> dict:
        """发送信息到浏览器，并返回浏览器返回的信息
        :param message: 发送给浏览器的数据
        :param timeout: 超时时间，为None表示无限
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

    def run(self, _method: str, **kwargs) -> dict:
        """执行cdp方法
        :param _method: cdp方法名
        :param kwargs: cdp参数
        :return: 执行结果
        """
        ...

    def start(self) -> bool:
        """启动连接"""
        ...

    def stop(self) -> bool:
        """中断连接"""
        ...

    def _stop(self) -> None:
        """中断连接"""
        ...

    def set_callback(self, event: str, callback: Union[Callable, None], immediate: bool = False) -> None:
        """绑定cdp event和回调方法
        :param event: cdp event
        :param callback: 绑定到cdp event的回调方法
        :param immediate: 是否要立即处理的动作
        :return: None
        """
        ...


class BrowserDriver(Driver):
    BROWSERS: Dict[str, Driver] = ...
    owner: Chromium = ...

    def __new__(cls, tab_id: str, tab_type: str, address: str, owner: Chromium): ...

    def __init__(self, tab_id: str, tab_type: str, address: str, owner: Chromium): ...

    @staticmethod
    def get(url) -> Response:
        """
        :param url: 要访问的链接
        :return: Response对象
        """
        ...
