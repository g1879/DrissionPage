# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from platform import system
from shutil import rmtree
from tempfile import gettempdir
from threading import Lock
from time import perf_counter, sleep

from .._configs.options_manage import OptionsManager
from .._functions.settings import Settings as _S
from ..errors import (ContextLostError, ElementLostError, PageDisconnectedError, NoRectError, BrowserConnectError,
                      AlertExistsError, IncorrectURLError, StorageError, CookieFormatError, JavaScriptError, CDPError)


class PortFinder(object):
    used_port = set()
    prev_time = 0
    lock = Lock()
    checked_paths = set()

    def __init__(self, path=None):
        tmp = Path(path) if path else Path(gettempdir()) / 'DrissionPage'
        self.tmp_dir = tmp / 'autoPortData'
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        if str(self.tmp_dir.absolute()) not in PortFinder.checked_paths:
            for i in self.tmp_dir.iterdir():
                if i.is_dir() and not port_is_using('127.0.0.1', i.name):
                    rmtree(i, ignore_errors=True)
            PortFinder.checked_paths.add(str(self.tmp_dir.absolute()))

    def get_port(self, scope=None):
        from random import randint
        with PortFinder.lock:
            if PortFinder.prev_time and perf_counter() - PortFinder.prev_time > 60:
                PortFinder.used_port.clear()
            if scope in (True, None):
                scope = (9600, 59600)
            max_times = scope[1] - scope[0]
            times = 0
            while times < max_times:
                times += 1
                port = randint(*scope)
                if port in PortFinder.used_port or port_is_using('127.0.0.1', port):
                    continue
                path = self.tmp_dir / str(port)
                if path.exists():
                    try:
                        rmtree(path)
                    except:
                        continue
                PortFinder.used_port.add(port)
                PortFinder.prev_time = perf_counter()
                return port, str(path)
            raise BrowserConnectError(_S._lang.NO_AVAILABLE_PORT_FOUND)


def port_is_using(ip, port):
    from socket import socket, AF_INET, SOCK_STREAM
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(.1)
    result = s.connect_ex((ip, int(port)))
    s.close()
    return result == 0


def clean_folder(folder_path, ignore=None):
    ignore = [] if not ignore else ignore
    p = Path(folder_path)

    for f in p.iterdir():
        if f.name not in ignore:
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                rmtree(f, True)


def show_or_hide_browser(tab, hide=True):
    if not tab.browser.address.startswith(('127.0.0.1', 'localhost')):
        return

    if system().lower() != 'windows':
        raise EnvironmentError(_S._lang.WIN_SYS_ONLY)

    try:
        from win32gui import ShowWindow
        from win32con import SW_HIDE, SW_SHOW
    except (ImportError, ModuleNotFoundError):
        raise EnvironmentError(_S._lang.join(_S._lang.NEED_LIB_, 'pypiwin32', TIP='pip install pypiwin32'))

    pid = tab.browser.process_id
    if not pid:
        return None
    hds = get_hwnds_from_pid(pid, tab.title)
    sw = SW_HIDE if hide else SW_SHOW
    for hd in hds:
        ShowWindow(hd, sw)


def get_browser_progress_id(progress, address):
    if progress:
        return progress.pid

    from os import popen
    port = address.split(':')[-1]
    txt = ''
    progresses = popen(f'netstat -nao | findstr :{port}').read().split('\n')
    for progress in progresses:
        if 'LISTENING' in progress:
            txt = progress
            break
    if not txt:
        return None

    return txt.split(' ')[-1]


def get_hwnds_from_pid(pid, title):
    try:
        from win32gui import IsWindow, GetWindowText, EnumWindows
        from win32process import GetWindowThreadProcessId
    except (ImportError, ModuleNotFoundError):
        raise EnvironmentError(_S._lang.join(_S._lang.NEED_LIB_, 'win32gui, win32process',
                                             TIP='pip install pypiwin32\npip install win32process'))

    def callback(hwnd, hds):
        if IsWindow(hwnd) and title in GetWindowText(hwnd):
            _, found_pid = GetWindowThreadProcessId(hwnd)
            if str(found_pid) == str(pid):
                hds.append(hwnd)
            return True

    hwnds = []
    EnumWindows(callback, hwnds)
    return hwnds


def wait_until(function, kwargs=None, timeout=10):
    if kwargs is None:
        kwargs = {}
    end_time = perf_counter() + timeout
    while perf_counter() < end_time:
        value = function(**kwargs)
        if value:
            return value
        sleep(.01)
    raise TimeoutError


def configs_to_here(save_name=None):
    om = OptionsManager('default')
    save_name = f'{save_name}.ini' if save_name is not None else 'dp_configs.ini'
    om.save(save_name)


def raise_error(result, browser, ignore=None, user=False):
    error = result['error']
    if error in ('Cannot find context with specified id', 'Inspected target navigated or closed',
                 'No frame with given id found'):
        r = ContextLostError()
    elif error in ('Could not find node with given id', 'Could not find object with given id',
                   'No node with given id found', 'Node with given id does not belong to the document',
                   'No node found for given backend id'):
        r = ElementLostError()
    elif error in ('connection disconnected', 'No target with given id found'):
        r = PageDisconnectedError()
    elif error == 'alert exists.':
        r = AlertExistsError()
    elif error in ('Node does not have a layout object', 'Could not compute box model.'):
        r = NoRectError()
    elif error == 'Cannot navigate to invalid URL':
        r = IncorrectURLError(_S._lang.INVALID_URL, url=result["args"]["url"])
    elif error == 'Frame corresponds to an opaque origin and its storage key cannot be serialized':
        r = StorageError()
    elif error == 'Sanitizing cookie failed':
        r = CookieFormatError(cookies=result["args"])
    elif error == 'Invalid header name':
        r = ValueError(_S._lang.join(_S._lang.INVALID_HEADER_NAME, headers=result["args"]["headers"]))
    elif error == 'Given expression does not evaluate to a function':
        r = JavaScriptError(_S._lang.NOT_A_FUNCTION, JS=result["args"]["functionDeclaration"])
    elif error.endswith("' wasn't found"):
        r = RuntimeError(_S._lang.join(_S._lang.METHOD_NOT_FOUND, BROWSER_VER=browser.version, METHOD=result["method"]))
    elif result['type'] == 'timeout':
        r = TimeoutError(_S._lang.join(_S._lang.NO_RESPONSE, INFO=result["error"],
                                       METHOD=result["method"], ARGS=result["args"]))
    elif result['type'] == 'call_method_error' and not user:
        r = CDPError(_S._lang.UNKNOWN_ERR, INFO=result["error"], METHOD=result["method"],
                     ARGS=result["args"], TIP=_S._lang.FEEDBACK)
    else:
        r = RuntimeError(_S._lang.join(_S._lang.UNKNOWN_ERR, INFO=result, TIP=_S._lang.FEEDBACK))

    if not ignore or not isinstance(r, ignore):
        raise r
