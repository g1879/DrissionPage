# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from json import load, dump, JSONDecodeError
from os import environ
from pathlib import Path
from shutil import rmtree
from subprocess import Popen, DEVNULL
from tempfile import gettempdir
from time import perf_counter, sleep

from requests import Session

from .settings import Settings as _S
from .tools import port_is_using
from .._configs.options_manage import OptionsManager
from ..errors import BrowserConnectError


def connect_browser(option):
    address = option.address.replace('localhost', '127.0.0.1').lstrip('htps:/')
    browser_path = option.browser_path

    ip, port = address.split(':')
    using = port_is_using(ip, port)
    if ip != '127.0.0.1' or using or option.is_existing_only:
        if test_connect(ip, port):
            return True
        elif ip != '127.0.0.1':
            raise BrowserConnectError(ADDRESS=address)
        elif using:
            raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR1_, port, port, ADDRESS=address)
        else:  # option.is_existing_only
            raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2, ADDRESS=address)

    # ----------创建浏览器进程----------
    args, user_path = get_launch_args(option)
    if option._new_env:
        rmtree(user_path, ignore_errors=True)
    set_prefs(option)
    set_flags(option)
    try:
        _run_browser(port, browser_path, args)

    # 传入的路径找不到，主动在ini文件、注册表、系统变量中找
    except FileNotFoundError:
        browser_path = get_chrome_path(option.ini_path)
        if not browser_path:
            raise FileNotFoundError(_S._lang.join(_S._lang.BROWSER_EXE_NOT_FOUND))
        _run_browser(port, browser_path, args)

    if not test_connect(ip, port):
        raise BrowserConnectError(ADDRESS=address, TIP=_S._lang.BROWSER_CONNECT_ERR_INFO)
    return False


def get_launch_args(opt):
    # ----------处理arguments-----------
    result = set()
    user_path = False
    for i in opt.arguments:
        if i.startswith(('--load-extension=', '--remote-debugging-port=')):
            continue
        elif i.startswith('--user-data-dir') and not opt.system_user_path:
            user_path = f'--user-data-dir={Path(i[16:]).absolute()}'
            result.add(user_path)
            continue
        elif i.startswith('--user-agent='):
            opt._ua_set = True
        result.add(i)

    if not user_path and not opt.system_user_path:
        port = opt.address.split(':')[-1] if opt.address else '0'
        p = Path(opt.tmp_path) if opt.tmp_path else Path(gettempdir()) / 'DrissionPage'
        path = p / 'userData' / port
        path.mkdir(parents=True, exist_ok=True)
        user_path = path.absolute()
        opt.set_user_data_path(user_path)
        result.add(f'--user-data-dir={user_path}')

    result = list(result)

    # ----------处理插件extensions-------------
    ext = [str(Path(e).absolute()) for e in opt.extensions]
    if ext:
        ext = ','.join(set(ext))
        ext = f'--load-extension={ext}'
        result.append(ext)

    return result, user_path


def set_prefs(opt):
    if not opt.user_data_path or (not opt.preferences and not opt._prefs_to_del):
        return
    prefs = opt.preferences
    del_list = opt._prefs_to_del

    user = 'Default'
    for arg in opt.arguments:
        if arg.startswith('--profile-directory'):
            user = arg.split('=')[-1].strip()
            break

    prefs_file = Path(opt.user_data_path) / user / 'Preferences'

    if not prefs_file.exists():
        prefs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(prefs_file, 'w') as f:
            f.write('{}')

    with open(prefs_file, "r", encoding='utf-8') as f:
        try:
            prefs_dict = load(f)
        except JSONDecodeError:
            prefs_dict = {}

        for pref in prefs:
            value = prefs[pref]
            pref = pref.split('.')
            _make_leave_in_dict(prefs_dict, pref, 0, len(pref))
            _set_value_to_dict(prefs_dict, pref, value)

        for pref in del_list:
            _remove_arg_from_dict(prefs_dict, pref)

    with open(prefs_file, 'w', encoding='utf-8') as f:
        dump(prefs_dict, f)


def set_flags(opt):
    if not opt.user_data_path or (not opt.clear_file_flags and not opt.flags):
        return

    state_file = Path(opt.user_data_path) / 'Local State'

    if not state_file.exists():
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w') as f:
            f.write('{}')

    with open(state_file, "r", encoding='utf-8') as f:
        try:
            states_dict = load(f)
        except JSONDecodeError:
            states_dict = {}
        states_dict.setdefault('browser', {}).setdefault('enabled_labs_experiments', [])
        flags_list = [] if opt.clear_file_flags else states_dict['browser']['enabled_labs_experiments']
        flags_dict = {}
        for i in flags_list:
            f = str(i).split('@', 1)
            flags_dict[f[0]] = None if len(f) == 1 else f[1]

        for k, i in opt.flags.items():
            flags_dict[k] = i

        states_dict['browser']['enabled_labs_experiments'] = [f'{k}@{i}' if i else k for k, i in flags_dict.items()]

    with open(state_file, 'w', encoding='utf-8') as f:
        dump(states_dict, f)


def test_connect(ip, port):
    end_time = perf_counter() + _S.browser_connect_timeout
    s = Session()
    s.trust_env = False
    s.keep_alive = False
    while perf_counter() < end_time:
        try:
            r = s.get(f'http://{ip}:{port}/json', timeout=10, headers={'Connection': 'close'})
            for tab in r.json():
                if tab['type'] in ('page', 'webview'):
                    r.close()
                    s.close()
                    return True
            r.close()
        except Exception:
            sleep(.2)

    s.close()
    return False


def _run_browser(port, path: str, args) -> Popen:
    """创建浏览器进程
    :param port: 端口号
    :param path: 浏览器路径
    :param args: 启动参数
    :return: 进程对象
    """
    p = Path(path)
    p = str(p / 'chrome') if p.is_dir() else str(path)
    arguments = [p, f'--remote-debugging-port={port}']
    arguments.extend(args)
    try:
        return Popen(arguments, shell=False, stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError:
        raise FileNotFoundError(_S._lang.join(_S._lang.BROWSER_NOT_FOUND))


def _make_leave_in_dict(target_dict: dict, src: list, num: int, end: int) -> None:
    """把prefs中a.b.c形式的属性转为a['b']['c']形式
    :param target_dict: 要处理的字典
    :param src: 属性层级列表[a, b, c]
    :param num: 当前处理第几个
    :param end: src长度
    :return: None
    """
    if num == end:
        return
    if src[num] not in target_dict:
        target_dict[src[num]] = {}
    num += 1
    _make_leave_in_dict(target_dict[src[num - 1]], src, num, end)


def _set_value_to_dict(target_dict: dict, src: list, value) -> None:
    """把a.b.c形式的属性的值赋值到a['b']['c']形式的字典中
    :param target_dict: 要处理的字典
    :param src: 属性层级列表[a, b, c]
    :param value: 属性值
    :return: None
    """
    src = "']['".join(src)
    src = f"target_dict['{src}']=value"
    exec(src)


def _remove_arg_from_dict(target_dict: dict, arg: str) -> None:
    """把a.b.c形式的属性从字典中删除
    :param target_dict: 要处理的字典
    :param arg: 层级属性，形式'a.b.c'
    :return: None
    """
    args = arg.split('.')
    args = [f"['{i}']" for i in args]
    src = ''.join(args)
    src = f"target_dict{src}"
    try:
        exec(src)
        src = ''.join(args[:-1])
        src = f"target_dict{src}.pop({args[-1][1:-1]})"
        exec(src)
    except:
        pass


def get_chrome_path(ini_path):
    # -----------从ini文件中获取--------------
    if ini_path and Path(ini_path).exists():
        path = OptionsManager(ini_path).chromium_options.get('browser_path', None)
        if path and Path(path).is_file():
            return str(path)

    # -----------使用which获取-----------
    from shutil import which
    path = (which('chrome') or which('chromium') or which('google-chrome') or which('google-chrome-stable')
            or which('google-chrome-unstable') or which('google-chrome-beta'))
    if path:
        return path

    # -----------从MAC和Linux默认路径获取-----------
    from platform import system
    sys = system().lower()
    if sys in ('macos', 'darwin'):
        p = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        return p if Path(p).exists() else None

    elif sys == 'linux':
        paths = ('/usr/bin/google-chrome', '/opt/google/chrome/google-chrome',
                 '/user/lib/chromium-browser/chromium-browser')
        for p in paths:
            if Path(p).exists():
                return p
        return None

    elif sys != 'windows':
        return None

    # -----------从注册表中获取--------------
    from winreg import OpenKey, EnumValue, CloseKey, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, KEY_READ
    txt = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'
    try:
        key = OpenKey(HKEY_CURRENT_USER, txt, reserved=0, access=KEY_READ)
        k = EnumValue(key, 0)
        CloseKey(key)
        if k[1]:
            return k[1]

    except (FileNotFoundError, OSError):
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, txt, reserved=0, access=KEY_READ)
            k = EnumValue(key, 0)
            CloseKey(key)
            if k[1]:
                return k[1]

        except (FileNotFoundError, OSError):
            pass

    # -----------从系统变量中获取--------------
    for path in environ.get('PATH', '').split(';'):
        path = Path(path) / 'chrome.exe'
        try:
            if path.exists():
                return str(path)
        except OSError:
            pass
