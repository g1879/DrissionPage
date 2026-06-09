# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from queue import Queue
from time import perf_counter, sleep

from .._functions.settings import Settings as _S
from .._functions.tools import wait_until


class Console(object):
    def __init__(self, owner):
        self._owner = owner
        self._caught = None
        self._not_enabled = True
        self.listening = False

    @property
    def messages(self):
        if self._caught is None:
            return []
        lst = []
        while not self._caught.empty():
            lst.append(self._caught.get_nowait())
        return lst

    def start(self):
        self._caught = Queue(maxsize=0)
        self._owner._set_callback("Log.entryAdded", self._onEntryAdded)
        self._owner._set_callback("Runtime.consoleAPICalled", self._onConsoleAPICalled)
        if self._not_enabled:
            self._owner._run_cdp("Log.enable")
            self._owner._run_cdp("Runtime.enable")
            self._not_enabled = False
        self.listening = True

    def stop(self):
        if self.listening:
            self._owner._set_callback('Log.entryAdded', None)
            self._owner._set_callback("Runtime.consoleAPICalled", None)
            self._owner._run_cdp("Log.disable")
            self._owner._run_cdp("Runtime.disable")
            self.listening = False

    def clear(self):
        self._caught = Queue(maxsize=0)

    def wait(self, timeout=None):
        if not self.listening:
            raise RuntimeError(_S._lang.joinn(_S._lang.NOT_LISTENING))

        def do():
            if not self._owner._messenger_running or not self.listening:
                return False
            return self._caught.get_nowait() if self._caught.qsize() else None

        r = wait_until(do, timeout=timeout)
        return r if r is not None else False

    def steps(self, timeout=None):
        if timeout is None:
            while self._owner._messenger_running and self.listening:
                if self._caught.qsize():
                    yield self._caught.get_nowait()
                sleep(0.05)

        else:
            end = perf_counter() + timeout
            while self._owner._messenger_running and self.listening and perf_counter() < end:
                if self._caught.qsize():
                    yield self._caught.get_nowait()
                    end = perf_counter() + timeout
                sleep(0.05)

    def _onEntryAdded(self, **kwargs):
        self._caught.put(ConsoleData(kwargs['entry']))

    def _onConsoleAPICalled(self, **kwargs):
        self._caught.put(ConsoleData(kwargs))


class ConsoleData(object):
    def __init__(self, data):
        self._data = data

    def __getattr__(self, item):
        return self._data.get(item)

    @property
    def data(self):
        return self._data
