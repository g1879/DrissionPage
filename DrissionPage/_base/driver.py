# -*- coding: utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from json import dumps, loads, JSONDecodeError
from queue import Queue, Empty
from threading import Thread, Event
from time import perf_counter, sleep

from requests import Session
from websocket import (WebSocketTimeoutException, WebSocketConnectionClosedException, create_connection,
                       WebSocketException, WebSocketBadStatusException)

from .._functions.settings import Settings
from ..errors import PageDisconnectedError


class Driver(object):
    def __init__(self, tab_id, tab_type, address, owner=None):
        """
        :param tab_id: 标签页id
        :param tab_type: 标签页类型
        :param address: 浏览器连接地址
        :param owner: 创建这个驱动的对象
        """
        self.id = tab_id
        self.address = address
        self.type = tab_type
        self.owner = owner
        # self._debug = False
        self.alert_flag = False  # 标记alert出现，跳过一条请求后复原

        self._websocket_url = f'ws://{address}/devtools/{tab_type}/{tab_id}'
        self._cur_id = 0
        self._ws = None

        self._recv_th = Thread(target=self._recv_loop)
        self._handle_event_th = Thread(target=self._handle_event_loop)
        self._recv_th.daemon = True
        self._handle_event_th.daemon = True
        self._handle_immediate_event_th = None

        self._stopped = Event()

        self.event_handlers = {}
        self.immediate_event_handlers = {}
        self.method_results = {}
        self.event_queue = Queue()
        self.immediate_event_queue = Queue()

        self.start()

    def _send(self, message, timeout=None):
        """发送信息到浏览器，并返回浏览器返回的信息
        :param message: 发送给浏览器的数据
        :param timeout: 超时时间，为None表示无限
        :return: 浏览器返回的数据
        """
        self._cur_id += 1
        ws_id = self._cur_id
        message['id'] = ws_id
        message_json = dumps(message)

        # if self._debug:
        #     if self._debug is True or (isinstance(self._debug, str) and
        #                                message.get('method', '').startswith(self._debug)):
        #         print(f'发> {message_json}')
        #     elif isinstance(self._debug, (list, tuple, set)):
        #         for m in self._debug:
        #             if message.get('method', '').startswith(m):
        #                 print(f'发> {message_json}')
        #                 break

        end_time = perf_counter() + timeout if timeout is not None else None
        self.method_results[ws_id] = Queue()
        try:
            self._ws.send(message_json)
            if timeout == 0:
                self.method_results.pop(ws_id, None)
                return {'id': ws_id, 'result': {}}

        except (OSError, WebSocketConnectionClosedException):
            self.method_results.pop(ws_id, None)
            return {'error': {'message': 'connection disconnected'}, 'type': 'connection_error'}

        while not self._stopped.is_set():
            try:
                result = self.method_results[ws_id].get(timeout=.2)
                self.method_results.pop(ws_id, None)
                return result

            except Empty:
                if self.alert_flag and message['method'].startswith(('Input.', 'Runtime.')):
                    return {'error': {'message': 'alert exists.'}, 'type': 'alert_exists'}

                if timeout is not None and perf_counter() > end_time:
                    self.method_results.pop(ws_id, None)
                    return {'error': {'message': 'alert exists.'}, 'type': 'alert_exists'} \
                        if self.alert_flag else {'error': {'message': 'timeout'}, 'type': 'timeout'}

                continue

        return {'error': {'message': 'connection disconnected'}, 'type': 'connection_error'}

    def _recv_loop(self):
        """接收浏览器信息的守护线程方法"""
        while not self._stopped.is_set():
            try:
                # self._ws.settimeout(1)
                msg_json = self._ws.recv()
                msg = loads(msg_json)
            except WebSocketTimeoutException:
                continue
            except (WebSocketException, OSError, WebSocketConnectionClosedException, JSONDecodeError):
                self._stop()
                return

            # if self._debug:
            #     if self._debug is True or 'id' in msg or (isinstance(self._debug, str)
            #                                               and msg.get('method', '').startswith(self._debug)):
            #         print(f'<收 {msg_json}')
            #     elif isinstance(self._debug, (list, tuple, set)):
            #         for m in self._debug:
            #             if msg.get('method', '').startswith(m):
            #                 print(f'<收 {msg_json}')
            #                 break

            if 'method' in msg:
                if msg['method'].startswith('Page.javascriptDialog'):
                    self.alert_flag = msg['method'].endswith('Opening')
                function = self.immediate_event_handlers.get(msg['method'])
                if function:
                    self._handle_immediate_event(function, msg['params'])
                else:
                    self.event_queue.put(msg)

            elif msg.get('id') in self.method_results:
                self.method_results[msg['id']].put(msg)

            # elif self._debug:
            #     print(f'未知信息：{msg}')

    def _handle_event_loop(self):
        """当接收到浏览器信息，执行已绑定的方法"""
        while not self._stopped.is_set():
            try:
                event = self.event_queue.get(timeout=1)
            except Empty:
                continue

            function = self.event_handlers.get(event['method'])
            if function:
                function(**event['params'])

            self.event_queue.task_done()

    def _handle_immediate_event_loop(self):
        while not self._stopped.is_set() and not self.immediate_event_queue.empty():
            function, kwargs = self.immediate_event_queue.get(timeout=1)
            try:
                function(**kwargs)
            except PageDisconnectedError:
                pass

    def _handle_immediate_event(self, function, kwargs):
        """处理立即执行的动作
        :param function: 要运行下方法
        :param kwargs: 方法参数
        :return: None
        """
        self.immediate_event_queue.put((function, kwargs))
        if self._handle_immediate_event_th is None or not self._handle_immediate_event_th.is_alive():
            self._handle_immediate_event_th = Thread(target=self._handle_immediate_event_loop)
            self._handle_immediate_event_th.daemon = True
            self._handle_immediate_event_th.start()

    def run(self, _method, **kwargs):
        """执行cdp方法
        :param _method: cdp方法名
        :param kwargs: cdp参数
        :return: 执行结果
        """
        if self._stopped.is_set():
            return {'error': 'connection disconnected', 'type': 'connection_error'}

        timeout = kwargs.pop('_timeout', Settings.cdp_timeout)
        result = self._send({'method': _method, 'params': kwargs}, timeout=timeout)
        if 'result' not in result and 'error' in result:
            kwargs['_timeout'] = timeout
            return {'error': result['error']['message'], 'type': result.get('type', 'call_method_error'),
                    'method': _method, 'args': kwargs}
        else:
            return result['result']

    def start(self):
        """启动连接"""
        self._stopped.clear()
        try:
            self._ws = create_connection(self._websocket_url, enable_multithread=True, suppress_origin=True)
        except WebSocketBadStatusException as e:
            if 'Handshake status 403 Forbidden' in str(e):
                raise RuntimeError('请升级websocket-client库。')
            else:
                return
        self._recv_th.start()
        self._handle_event_th.start()
        return True

    def stop(self):
        """中断连接"""
        self._stop()
        while self._handle_event_th.is_alive() or self._recv_th.is_alive():
            sleep(.1)
        return True

    def _stop(self):
        """中断连接"""
        if self._stopped.is_set():
            return False

        self._stopped.set()
        if self._ws:
            self._ws.close()
            self._ws = None

        # try:
        #     while not self.event_queue.empty():
        #         event = self.event_queue.get_nowait()
        #         function = self.event_handlers.get(event['method'])
        #         if function:
        #             function(**event['params'])
        #         sleep(.1)
        # except:
        #     pass

        self.event_handlers.clear()
        self.method_results.clear()
        self.event_queue.queue.clear()

        if hasattr(self.owner, '_on_disconnect'):
            self.owner._on_disconnect()

    def set_callback(self, event, callback, immediate=False):
        """绑定cdp event和回调方法
        :param event: cdp event
        :param callback: 绑定到cdp event的回调方法
        :param immediate: 是否要立即处理的动作
        :return: None
        """
        handler = self.immediate_event_handlers if immediate else self.event_handlers
        if callback:
            handler[event] = callback
        else:
            handler.pop(event, None)


class BrowserDriver(Driver):
    BROWSERS = {}

    def __new__(cls, tab_id, tab_type, address, owner):
        if tab_id in cls.BROWSERS:
            return cls.BROWSERS[tab_id]
        return object.__new__(cls)

    def __init__(self, tab_id, tab_type, address, owner):
        if hasattr(self, '_created'):
            return
        self._created = True
        BrowserDriver.BROWSERS[tab_id] = self
        super().__init__(tab_id, tab_type, address, owner)
        self._control_session = Session()
        self._control_session.trust_env = False

    def __repr__(self):
        return f'<BrowserDriver {self.id}>'

    def get(self, url):
        r = self._control_session.get(url, headers={'Connection': 'close'})
        r.close()
        return r
