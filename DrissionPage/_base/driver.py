# -*- coding: utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from json import dumps, loads, JSONDecodeError
from queue import Queue, Empty
from threading import Thread, Lock
from time import perf_counter, sleep

from requests import Session
from requests import adapters
from websocket import (WebSocketTimeoutException, WebSocketConnectionClosedException, create_connection,
                       WebSocketException, WebSocketBadStatusException)

from .._functions.settings import Settings as _S
from ..errors import BrowserConnectError

adapters.DEFAULT_RETRIES = 5


class ThreadSafeDict:
    def __init__(self):
        self._dict = {}
        self._lock = Lock()

    def __getitem__(self, k):
        with self._lock:
            return self._dict[k]

    def __setitem__(self, k, v):
        with self._lock:
            self._dict[k] = v

    def __delitem__(self, k):
        with self._lock:
            del self._dict[k]

    def get(self, k, default=None):
        with self._lock:
            return self._dict.get(k, default)

    def pop(self, item, default):
        with self._lock:
            self._dict.pop(item, default)

    def clear(self):
        with self._lock:
            self._dict.clear()


class Driver(object):
    def __init__(self, address, owner=None):
        self.address = address
        self.owner = owner
        self.alert_flag = set()  # 标记alert出现，跳过一条请求后复原

        self._cur_id = 0
        self._ws = None

        self._recv_th = Thread(target=self._recv_loop)
        self._recv_th.daemon = True
        self._session_owner = {}

        self.is_running = False
        self.method_results = ThreadSafeDict()
        self.event_queue = Queue()

        if owner:
            self.add_session_owner(None, owner)

        self.start()

    def _send(self, message, timeout, ws_id):
        if not timeout:
            try:
                self._ws.send(dumps(message))
                return {'id': ws_id, 'result': {}}
            except (OSError, WebSocketConnectionClosedException):
                return {'error': {'message': 'connection disconnected'}}

        self.method_results[ws_id] = Queue()
        try:
            self._ws.send(dumps(message))
        except (OSError, WebSocketConnectionClosedException):
            self.method_results.pop(ws_id, None)
            return {'error': {'message': 'connection disconnected'}}

        end_time = perf_counter() + timeout
        while self.is_running:
            try:
                result = self.method_results[ws_id].get(timeout=.2)
                self.method_results.pop(ws_id, None)
                return result

            except Empty:
                if (self.alert_flag and message['sessionId'] in self.alert_flag
                        and message['method'].startswith(('Input.', 'Runtime.'))):
                    return {'error': {'message': 'alert exists.'}}

                if timeout is not None and perf_counter() > end_time:
                    self.method_results.pop(ws_id, None)
                    return {'id': ws_id, 'error': {'message': 'timeout'}}

        return {'error': {'message': 'connection disconnected'}}

    def _recv_loop(self):
        while self.is_running:
            try:
                msg = loads(self._ws.recv())
            except WebSocketTimeoutException:
                continue
            except (WebSocketException, OSError, WebSocketConnectionClosedException, JSONDecodeError):
                self._stop()
                return

            if 'method' in msg:
                if msg['method'].startswith('Page.javascriptDialog'):
                    sid = msg.get('sessionId')
                    if sid:
                        (self.alert_flag.add if msg['method'].endswith('Opening') else self.alert_flag.discard)(sid)
                self._session_owner.get(msg.get('sessionId'), NoSession)._recv_event(msg)

            else:
                r = self.method_results.get(msg.get('id'))
                if r:
                    r.put(msg)

    def add_session_owner(self, session_id, obj):
        self._session_owner[session_id] = obj

    def remove_session_owner(self, session_id):
        self._session_owner.pop(session_id, None)

    def run(self, _method, _timeout=None, _session_id=None, _debug=False, **kwargs):
        if not self.is_running:
            return {'error': 'connection disconnected'}

        if _timeout is None:
            _timeout = _S.cdp_timeout

        self._cur_id += 1
        ws_id = self._cur_id
        result = self._send(({'id': ws_id, 'method': _method, 'params': kwargs, 'sessionId': _session_id}
                             if _session_id else {'id': ws_id, 'method': _method, 'params': kwargs}),
                            timeout=_timeout, ws_id=ws_id)
        if 'error' in result:
            return {'error': result['error']['message'], 'method': _method,
                    'args': kwargs, 'data': result['error'].get('data'), 'timeout': _timeout}
        else:
            return result['result']

    def start(self):
        self.is_running = True
        try:
            self._ws = create_connection(self.address, enable_multithread=True, suppress_origin=True)
        except WebSocketBadStatusException as e:
            if 'Handshake status 403 Forbidden' in str(e):
                raise EnvironmentError(_S._lang.joinn(_S._lang.UPGRADE_WS))
            else:
                raise
        except ConnectionRefusedError:
            raise BrowserConnectError(_S._lang.BROWSER_NOT_EXIST)
        self._recv_th.start()
        return True

    def stop(self):
        self._stop()
        while self._recv_th.is_alive():
            sleep(.01)
        return True

    def _stop(self):
        if not self.is_running:
            return

        self.is_running = False
        if self._ws:
            self._ws.close()
            self._ws = None

        self.method_results.clear()
        self._session_owner.clear()
        self.alert_flag.clear()
        self.owner._on_disconnect()

    @staticmethod
    def get(url):
        s = Session()
        s.trust_env = False
        s.keep_alive = False
        r = s.get(url, headers={'Connection': 'close'})
        r.close()
        s.close()
        return r


class DebugDriver(Driver):
    def __init__(self, address, owner=None):
        super().__init__(address, owner=owner)
        self._debug = False if _S._debug is None else _S._debug

    def run(self, _method, _timeout=None, _session_id=None, _debug=False, **kwargs):
        if not self.is_running:
            return {'error': 'connection disconnected'}

        if _timeout is None:
            _timeout = _S.cdp_timeout

        self._cur_id += 1
        ws_id = self._cur_id
        msg = ({'id': ws_id, 'method': _method, 'params': kwargs, 'sessionId': _session_id}
               if _session_id else {'id': ws_id, 'method': _method, 'params': kwargs})

        _debug = _debug or self._debug
        show = False
        if _debug and (_debug is True or msg['method'].startswith(_debug)):
            print(f'发 {msg}')
            show = True
        result = self._send(msg, timeout=_timeout, ws_id=ws_id)
        if show:
            print(f'回 {result}')
        if 'error' in result and 'result' not in result:
            return {'error': result['error']['message'], 'method': _method,
                    'args': kwargs, 'data': result['error'].get('data'), 'timeout': _timeout}
        else:
            return result['result']

    def _recv_loop(self):
        while self.is_running:
            try:
                msg = loads(self._ws.recv())
            except WebSocketTimeoutException:
                continue
            except (WebSocketException, OSError, WebSocketConnectionClosedException, JSONDecodeError):
                self._stop()
                return

            if 'method' in msg:
                if self._debug and (self._debug is True or msg['method'].startswith(self._debug)):
                    print(f'收 {msg}')
                if msg['method'].startswith('Page.javascriptDialog'):
                    sid = msg.get('sessionId')
                    if sid:
                        (self.alert_flag.add if msg['method'].endswith('Opening') else self.alert_flag.discard)(sid)
                self._session_owner.get(msg.get('sessionId'), NoSession)._debug_recv_event(msg)

            else:
                r = self.method_results.get(msg.get('id'))
                if r:
                    r.put(msg)


class NoSession(object):
    @classmethod
    def _recv_event(cls, msg):
        pass

    @classmethod
    def _debug_recv_event(cls, msg):
        pass
