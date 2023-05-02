# -*- coding: utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from queue import Queue
from threading import Thread, Event
from typing import Union, Callable


class GenericAttr(object):
    def __init__(self, name: str, tab: ChromiumDriver): ...

    def __getattr__(self, item: str) -> Callable: ...

    def __setattr__(self, key: str, value: Callable) -> None: ...


class ChromiumDriver(object):
    _INITIAL_: str
    _STARTED_: str
    _STOPPED_: str
    id: str
    address: str
    type: str
    debug: bool
    has_alert: bool
    _websocket_url: str
    _cur_id: int
    _ws = None
    _recv_th: Thread
    _handle_event_th: Thread
    _stopped: Event
    _started: bool
    status: str
    event_handlers: dict
    method_results: dict
    event_queue: Queue

    def __init__(self, tab_id: str, tab_type: str, address: str): ...

    def _send(self, message: dict, timeout: float = None) -> dict: ...

    def _recv_loop(self) -> None: ...

    def _handle_event_loop(self) -> None: ...

    def __getattr__(self, item: str) -> Callable: ...

    def call_method(self, _method: str, *args, **kwargs) -> dict: ...

    def start(self) -> bool: ...

    def stop(self) -> bool: ...

    def set_listener(self, event: str, callback: Union[Callable, None]) -> Union[Callable, None, bool]: ...

    def get_listener(self, event: str) -> Union[Callable, None]: ...

    def __str__(self) -> str: ...
