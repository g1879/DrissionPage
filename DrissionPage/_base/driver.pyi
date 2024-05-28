# -*- coding: utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from queue import Queue
from threading import Thread, Event
from typing import Union, Callable, Dict, Optional

from requests import Response, Session
from websocket import WebSocket

from .browser import Browser


class GenericAttr(object):
    def __init__(self, name: str, tab: Driver): ...

    def __getattr__(self, item: str) -> Callable: ...

    def __setattr__(self, key: str, value: Callable) -> None: ...


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
    _stopped: Event
    event_handlers: dict
    immediate_event_handlers: dict
    method_results: dict
    event_queue: Queue
    immediate_event_queue: Queue

    def __init__(self, tab_id: str, tab_type: str, address: str, owner=None): ...

    def _send(self, message: dict, timeout: float = None) -> dict: ...

    def _recv_loop(self) -> None: ...

    def _handle_event_loop(self) -> None: ...

    def _handle_immediate_event_loop(self): ...

    def _handle_immediate_event(self, function: Callable, kwargs: dict): ...

    def run(self, _method: str, **kwargs) -> dict: ...

    def start(self) -> bool: ...

    def stop(self) -> bool: ...

    def _stop(self) -> None: ...

    def set_callback(self, event: str, callback: Union[Callable, None], immediate: bool = False) -> None: ...


class BrowserDriver(Driver):
    BROWSERS: Dict[str, Driver] = ...
    owner: Browser = ...
    _control_session: Session = ...

    def __new__(cls, tab_id: str, tab_type: str, address: str, owner: Browser): ...

    def __init__(self, tab_id: str, tab_type: str, address: str, owner: Browser): ...

    def get(self, url) -> Response: ...
