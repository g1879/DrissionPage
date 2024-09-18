# -*- coding:utf-8 -*-
from queue import Queue
from time import perf_counter, sleep


class Console(object):
    def __init__(self, owner):
        self._owner = owner
        self.listening = False
        self._caught = None

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
        self._owner._driver.set_callback("Console.messageAdded", self._console)
        self._owner._run_cdp("Console.enable")
        self.listening = True

    def stop(self):
        if self.listening:
            self._owner._run_cdp("Console.disable")
            self._owner._driver.set_callback('Console.messageAdded', None)
            self.listening = False

    def clear(self):
        self._caught = Queue(maxsize=0)

    def wait(self, timeout=None):
        if not self.listening:
            raise RuntimeError('监听未启动。')
        if timeout is None:
            while self._owner._driver.is_running and self.listening and not self._caught.qsize():
                sleep(.03)
            return self._caught.get_nowait() if self._caught.qsize() else None

        else:
            end = perf_counter() + timeout
            while self._owner._driver.is_running and self.listening and perf_counter() < end:
                if self._caught.qsize():
                    return self._caught.get_nowait()
                sleep(0.05)
            return False

    def steps(self, timeout=None):
        if timeout is None:
            while self._owner._driver.is_running and self.listening:
                if self._caught.qsize():
                    yield self._caught.get_nowait()
                sleep(0.05)

        else:
            end = perf_counter() + timeout
            while self._owner._driver.is_running and self.listening and perf_counter() < end:
                if self._caught.qsize():
                    yield self._caught.get_nowait()
                sleep(0.05)
            return False

    def _console(self, **kwargs):
        self._caught.put(ConsoleData(kwargs['message']))


class ConsoleData(object):
    __slots__ = ('_data', 'source', 'level', 'text', 'url', 'line', 'column')

    def __init__(self, data):
        self._data = data

    def __getattr__(self, item):
        return self._data.get(item, None)

    def __repr__(self):
        return (f'<ConsoleData source={self.source} level={self.level} text={self.text} url={self.url} '
                f'line={self.line} column={self.column} >')
