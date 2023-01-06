# -*- coding: utf-8 -*-
from functools import partial
from json import dumps, loads
from logging import getLogger
from os import getenv
from threading import Thread, Event

from websocket import WebSocketTimeoutException, WebSocketException, WebSocketConnectionClosedException, \
    create_connection

try:
    import Queue as queue
except ImportError:
    import queue

logger = getLogger(__name__)


class GenericAttr(object):
    def __init__(self, name, tab):
        self.__dict__['name'] = name
        self.__dict__['tab'] = tab

    def __getattr__(self, item):
        method_name = "%s.%s" % (self.name, item)
        event_listener = self.tab.get_listener(method_name)

        if event_listener:
            return event_listener

        return partial(self.tab.call_method, method_name)

    def __setattr__(self, key, value):
        self.tab.set_listener("%s.%s" % (self.name, key), value)


class ChromiumDriver(object):
    status_initial = 'initial'
    status_started = 'started'
    status_stopped = 'stopped'

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.type = kwargs.get("type")
        self.debug = getenv("DEBUG", False)

        self._websocket_url = kwargs.get("webSocketDebuggerUrl")
        self._kwargs = kwargs

        self._cur_id = 1000

        self._ws = None

        self._recv_th = Thread(target=self._recv_loop)
        self._recv_th.daemon = True
        self._handle_event_th = Thread(target=self._handle_event_loop)
        self._handle_event_th.daemon = True

        self._stopped = Event()
        self._started = False
        self.status = self.status_initial

        self.event_handlers = {}
        self.method_results = {}
        self.event_queue = queue.Queue()

    def _send(self, message, timeout=None):
        if 'id' not in message:
            self._cur_id += 1
            message['id'] = self._cur_id

        message_json = dumps(message)

        if self.debug:  # pragma: no cover
            print("SEND > %s" % message_json)

        if not isinstance(timeout, (int, float)) or timeout > 1:
            q_timeout = 1
        else:
            q_timeout = timeout / 2.0

        try:
            self.method_results[message['id']] = queue.Queue()

            # just raise the exception to user
            self._ws.send(message_json)

            while not self._stopped.is_set():
                try:
                    if isinstance(timeout, (int, float)):
                        if timeout < q_timeout:
                            q_timeout = timeout

                        timeout -= q_timeout

                    return self.method_results[message['id']].get(timeout=q_timeout)
                except queue.Empty:
                    if isinstance(timeout, (int, float)) and timeout <= 0:
                        raise TimeoutError(f"调用{message['method']}超时。")

                    continue

            # raise UserAbortException("User abort, call stop() when calling %s" % message['method'])
        finally:
            self.method_results.pop(message['id'], None)

    def _recv_loop(self):
        while not self._stopped.is_set():
            try:
                self._ws.settimeout(1)
                message_json = self._ws.recv()
                message = loads(message_json)
            except WebSocketTimeoutException:
                continue
            except (WebSocketException, OSError, WebSocketConnectionClosedException):
                if not self._stopped.is_set():
                    # logger.error("websocket exception", exc_info=True)
                    self._stopped.set()
                return

            if self.debug:  # pragma: no cover
                print('< RECV %s' % message_json)

            if "method" in message:
                self.event_queue.put(message)

            elif "id" in message:
                if message["id"] in self.method_results:
                    self.method_results[message['id']].put(message)
            # else:  # pragma: no cover
            #     warn("unknown message: %s" % message)

    def _handle_event_loop(self):
        while not self._stopped.is_set():
            try:
                event = self.event_queue.get(timeout=1)
            except queue.Empty:
                continue

            if event['method'] in self.event_handlers:
                try:
                    self.event_handlers[event['method']](**event['params'])
                except Exception as e:
                    logger.error("callback %s exception" % event['method'], exc_info=True)

            self.event_queue.task_done()

    def __getattr__(self, item):
        attr = GenericAttr(item, self)
        setattr(self, item, attr)
        return attr

    def call_method(self, _method, *args, **kwargs):
        if not self._started:
            raise RuntimeError("不能在启动前调用方法。")

        if args:
            raise CallMethodException("参数必须是key=value形式。")

        if self._stopped.is_set():
            raise RuntimeError("Driver已经停止。")

        timeout = kwargs.pop("_timeout", None)
        result = self._send({"method": _method, "params": kwargs}, timeout=timeout)
        if 'result' not in result and 'error' in result:
            raise CallMethodException(f"调用方法：{_method} 错误：{result['error']['message']}")

        return result['result']

    def start(self):
        if self._started:
            return False

        if not self._websocket_url:
            raise RuntimeError("已存在另一个连接。")

        self._started = True
        self.status = self.status_started
        self._stopped.clear()
        self._ws = create_connection(self._websocket_url, enable_multithread=True)
        self._recv_th.start()
        self._handle_event_th.start()
        return True

    def stop(self):
        if self._stopped.is_set():
            return False

        if not self._started:
            raise RuntimeError("Driver正在运行。")

        self.status = self.status_stopped
        self._stopped.set()
        if self._ws:
            self._ws.close()
        return True

    def set_listener(self, event, callback):
        if not callback:
            return self.event_handlers.pop(event, None)

        if not callable(callback):
            raise RuntimeError("方法不能调用。")

        self.event_handlers[event] = callback
        return True

    def get_listener(self, event):
        return self.event_handlers.get(event, None)

    def del_all_listeners(self):
        self.event_handlers = {}
        return True

    def wait(self, timeout=None):
        if not self._started:
            raise RuntimeError("Driver仍未运行。")

        if timeout:
            return self._stopped.wait(timeout)

        self._recv_th.join()
        self._handle_event_th.join()
        return True

    def __str__(self):
        return f"<ChromiumDriver {self.id}>"

    __repr__ = __str__


class CallMethodException(Exception):
    pass
