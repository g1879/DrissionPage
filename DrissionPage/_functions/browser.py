# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from json import load, dump, JSONDecodeError
from os import environ, path as os_path, pathsep, X_OK, access
from pathlib import Path
from shutil import copytree, Error as shutilError
from subprocess import Popen, DEVNULL
from sys import platform
from tempfile import gettempdir

from requests import Session

from .settings import Settings as _S
from .tools import port_is_using, PortFinder, ensure_del_dir, wait_until
from ..errors import BrowserConnectError


def connect_browser(opt):
    if opt.is_auto_port:
        ip = '127.0.0.1'
        port = PortFinder(opt.tmp_path).get_port()
        opt._address = address = f'{ip}:{port}'

    else:
        address = opt.address.replace('localhost', '127.0.0.1')
        if address.startswith('http'):
            address = address.lstrip('htps:/')
        ip, port = address.split(':')
        using = port_is_using(ip, port)
        if ip != '127.0.0.1' or using or opt.is_existing_only:
            if test_connect(ip, port):
                return None
            elif ip != '127.0.0.1':
                raise BrowserConnectError(ADDRESS=address)
            elif using:
                raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR1_, port, port, ADDRESS=address)
            else:  # opt.is_existing_only
                raise BrowserConnectError(_S._lang.BROWSER_CONNECT_ERR2, ADDRESS=address)

    # ----------创建浏览器进程----------
    args, user_path = get_launch_args(opt)

    is_edge = 'edge' in opt.browser_path.lower()
    if not Path(opt._browser_path).exists():
        opt._browser_path = get_edge_path() if is_edge else get_chrome_path()
    if not Path(opt._browser_path).exists():
        FileNotFoundError(_S._lang.BROWSER_EXE_NOT_FOUND)

    if not user_path:
        user_path = (Path(opt.tmp_path or gettempdir()) / 'DrissionPage'
                     / ('autoPortData' if opt.is_auto_port else 'userData') / f'{port}')
        if opt.system_user_path:
            if opt._old_browser:
                user_path = None
            else:
                src_path = get_edge_user_data_dir() if is_edge else get_sys_Chrome_user_data_dir()
                try:
                    ensure_del_dir(user_path)
                    copytree(src_path, user_path)
                except shutilError:
                    ensure_del_dir(user_path)
                    raise RuntimeError(_S._lang.joinn(_S._lang.SYS_BROWSER_ACTIVATED, 'edge' if is_edge else 'Chrome'))

        elif opt.is_auto_port or opt._new_env:
            if not ensure_del_dir(user_path):
                raise RuntimeError(_S._lang.FAILED_TO_DEL_USER_DIR)

        if user_path:
            user_path = user_path.resolve()
            opt.set_user_data_path(user_path)
            args.append(f'--user-data-dir={user_path}')

    else:
        opt._auto_port = None  # 自动端口同时指定了文件夹，结束时不删除文件夹
        if opt._new_env and not ensure_del_dir(user_path):
            raise RuntimeError(_S._lang.FAILED_TO_DEL_USER_DIR)

    set_prefs(opt)
    set_flags(opt)

    _run_browser(port, opt._browser_path, args)

    if not test_connect(ip, port):
        raise BrowserConnectError(ADDRESS=address, USERDATA=opt.user_data_path , TIP=_S._lang.BROWSER_CONNECT_ERR_INFO)
    return args


def get_launch_args(opt):
    # ----------处理arguments-----------
    result = set()
    user_path = None
    for i in opt.arguments:
        if i.startswith(('--disable-extensions-except=', '--load-extension=', '--remote-debugging-port=')):
            continue
        elif i.startswith('--user-data-dir='):
            user_path = Path(i[16:]).resolve()
            i = f'--user-data-dir={user_path}'
        elif i.startswith('--user-agent='):
            opt._ua_set = True
        result.add(i)
    result = list(result)

    # ----------处理插件extensions-------------
    ext = [Path(e) for e in opt.extensions]
    exts = []
    if ext:
        for e in ext:
            if e.is_file():
                raise ValueError(_S._lang.joinn(_S._lang.PLUGIN_NEED_FOLDER, str(e.resolve())))
            elif not e.exists():
                raise FileNotFoundError(_S._lang.joinn(_S._lang.EXT_NOT_FOUND, PATH=e))
            else:
                exts.append(str(e.resolve()))
        ext = ','.join(set(exts))
        result.append(f'--disable-extensions-except={ext}')
        result.append(f'--load-extension={ext}')

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
    s = Session()
    s.trust_env = False
    s.keep_alive = False

    def do():
        try:
            r = s.get(f'http://{ip}:{port}/json/version', timeout=10, headers={'Connection': 'close'})
            if 'webSocketDebuggerUrl' in r.json():
                r.close()
                return True
        except Exception:
            return None

    res = wait_until(do, timeout=_S.browser_connect_timeout)
    s.close()
    return True if res else False


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
        raise FileNotFoundError(_S._lang.joinn(_S._lang.BROWSER_NOT_FOUND))


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


def get_chrome_path():
    system = platform.lower()
    if system.startswith("win"):  # 注册表+常见路径
        from winreg import OpenKey, QueryValue, HKEY_LOCAL_MACHINE
        try:
            reg_paths = [r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
                         r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"]
            for rp in reg_paths:
                try:
                    with OpenKey(HKEY_LOCAL_MACHINE, rp) as key:
                        p = QueryValue(key, None)
                        if p and Path(p).exists():
                            return p
                except Exception:
                    continue
        except ImportError:
            pass

        # 常见默认路径
        local_appdata = environ.get("LOCALAPPDATA", "")
        program_files = environ.get("PROGRAMFILES", "C:\\Program Files")
        program_files_x86 = environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")
        default_paths = [
            Path(local_appdata) / "Google/Chrome/Application/chrome.exe",
            Path(program_files) / "Google/Chrome/Application/chrome.exe",
            Path(program_files_x86) / "Google/Chrome/Application/chrome.exe",
        ]
        for p in default_paths:
            if p.exists():
                return str(p)

    elif system in ('macos', 'darwin'):  # macOS：默认应用路径
        mac_paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                     "/Applications/Chromium.app/Contents/MacOS/Chromium"]
        for p in mac_paths:
            if Path(p).exists():
                return p

    elif system == "linux":  # Linux：常见 bin 路径
        linux_paths = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                       "/usr/bin/chromium", "/usr/bin/chromium-browser", "/snap/bin/chromium"]
        for p in linux_paths:
            if Path(p).exists():
                return p

    # -------------------------- 从 PATH 查找 --------------------------
    # 可执行文件名列表
    if system.startswith('win'):
        exe_names = ["chrome.exe", "google-chrome.exe"]
    else:  # Linux / macOS
        exe_names = ["chrome", "google-chrome", "chromium", "chromium-browser"]

    # 遍历 PATH 目录查找
    path_dirs = environ.get("PATH", "").split(pathsep)
    for d in path_dirs:
        dir_path = Path(d)
        if not dir_path.is_dir():
            continue
        for exe in exe_names:
            exe_path = dir_path / exe
            if exe_path.exists() and exe_path.is_file() and access(exe_path, X_OK):
                return str(exe_path)

    raise RuntimeError(_S._lang.BROWSER_NOT_FOUND)


def get_edge_path():
    system = platform.lower()
    if system.startswith("win"):
        try:
            from winreg import OpenKey, QueryValue, HKEY_LOCAL_MACHINE
            reg_paths = [r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
                         r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"]
            for reg_path in reg_paths:
                try:
                    with OpenKey(HKEY_LOCAL_MACHINE, reg_path) as key:
                        path = QueryValue(key, None)
                        if path and os_path.exists(path):
                            return path
                except FileNotFoundError:
                    continue
        except:
            pass

        # Windows 备用默认路径
        default_win_paths = [
            os_path.join(environ.get("PROGRAMFILES", ""), r"Microsoft\Edge\Application\msedge.exe"),
            os_path.join(environ.get("PROGRAMFILES(X86)", ""), r"Microsoft\Edge\Application\msedge.exe"),
            os_path.join(environ.get("LOCALAPPDATA", ""), r"Microsoft\Edge\Application\msedge.exe"),
        ]
        for p in default_win_paths:
            if os_path.exists(p):
                return p

    elif system in ('macos', 'darwin'):
        mac_paths = ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                     os_path.expanduser("~/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")]
        for p in mac_paths:
            if os_path.exists(p):
                return p

    elif system == "linux":
        linux_paths = ["/usr/bin/microsoft-edge", "/usr/bin/microsoft-edge-stable", "/usr/local/bin/microsoft-edge",
                       "/usr/local/bin/microsoft-edge-stable", os_path.expanduser("~/.local/bin/microsoft-edge"),
                       os_path.expanduser("~/.local/bin/microsoft-edge-stable"), ]
        for p in linux_paths:
            if os_path.exists(p):
                return p

    raise RuntimeError(_S._lang.BROWSER_NOT_FOUND)


def get_sys_Chrome_user_data_dir():
    system = platform.lower()

    if system.startswith("win"):
        local_appdata = environ.get("LOCALAPPDATA")
        if not local_appdata:
            raise RuntimeError(_S._lang.joinn(_S._lang.FAILED_TO_GET_SYS_USER_DATA, 'Chrome'))
        src_path = os_path.join(local_appdata, "Google", "Chrome", "User Data")

    elif system in ('macos', 'darwin'):
        home = os_path.expanduser("~")
        src_path = os_path.join(home, "Library", "Application Support", "Google", "Chrome")

    elif system == "linux":
        home = os_path.expanduser("~")
        src_path = os_path.join(home, ".config", "google-chrome")

    else:
        raise RuntimeError(_S._lang.joinn(_S._lang.FAILED_TO_GET_SYS_USER_DATA, 'Chrome'))

    if not os_path.exists(src_path):
        raise RuntimeError(_S._lang.joinn(_S._lang.FAILED_TO_GET_SYS_USER_DATA, 'Chrome'))

    return Path(src_path)


def get_edge_user_data_dir():
    system = platform.lower()

    if system.startswith("win"):
        local_appdata = environ.get("LOCALAPPDATA")
        if not local_appdata:
            raise RuntimeError(_S._lang.joinn(_S._lang.FAILED_TO_GET_SYS_USER_DATA, 'edge'))
        src_path = os_path.join(local_appdata, "Microsoft", "Edge", "User Data")

    elif system in ('macos', 'darwin'):
        home = os_path.expanduser("~")
        src_path = os_path.join(home, "Library", "Application Support", "Microsoft Edge")

    elif system == "linux":
        home = os_path.expanduser("~")
        src_path = os_path.join(home, ".config", "microsoft-edge")

    else:
        raise RuntimeError(_S._lang.joinn(_S._lang.FAILED_TO_GET_SYS_USER_DATA, 'edge'))

    if not os_path.exists(src_path):
        raise RuntimeError(_S._lang.joinn(_S._lang.FAILED_TO_GET_SYS_USER_DATA, 'edge'))

    return Path(src_path)
