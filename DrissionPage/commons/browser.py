# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from json import load, dump
from pathlib import Path
from subprocess import Popen
from tempfile import gettempdir
from time import perf_counter, sleep

from requests import get as requests_get

from DrissionPage.configs.chromium_options import ChromiumOptions
from DrissionPage.errors import BrowserConnectError
from .tools import port_is_using


def connect_browser(option):
    """连接或启动浏览器
    :param option: DriverOptions对象
    :return: chrome 路径和进程对象组成的元组
    """
    debugger_address = option.debugger_address.replace('localhost', '127.0.0.1').lstrip('http://').lstrip('https://')
    chrome_path = option.browser_path

    ip, port = debugger_address.split(':')
    if ip != '127.0.0.1':
        test_connect(ip, port)
        return None, None

    if port_is_using(ip, port):
        test_connect(ip, port)
        return None, None

    args = get_launch_args(option)
    set_prefs(option)

    # ----------创建浏览器进程----------
    try:
        debugger = _run_browser(port, chrome_path, args)

    # 传入的路径找不到，主动在ini文件、注册表、系统变量中找
    except FileNotFoundError:
        from DrissionPage.easy_set import get_chrome_path
        chrome_path = get_chrome_path(show_msg=False)

        if not chrome_path:
            raise FileNotFoundError('无法找到chrome路径，请手动配置。')

        debugger = _run_browser(port, chrome_path, args)

    test_connect(ip, port)
    return chrome_path, debugger


def get_launch_args(opt):
    """从DriverOptions获取命令行启动参数
    :param opt: DriverOptions或ChromiumOptions
    :return: 启动参数列表
    """
    # ----------处理arguments-----------
    result = set()
    has_user_path = False
    remote_allow = False
    for i in opt.arguments:
        if i.startswith(('--load-extension=', '--remote-debugging-port=')):
            continue
        elif i.startswith('--user-data-dir') and not opt.system_user_path:
            result.add(f'--user-data-dir={Path(i[16:]).absolute()}')
            has_user_path = True
            continue
        elif i.startswith('--remote-allow-origins='):
            remote_allow = True

        result.add(i)

    if not has_user_path and not opt.system_user_path:
        port = opt.debugger_address.split(':')[-1] if opt.debugger_address else '0'
        path = Path(gettempdir()) / 'DrissionPage' / f'userData_{port}'
        path.mkdir(parents=True, exist_ok=True)
        result.add(f'--user-data-dir={path}')

    if not remote_allow:
        result.add('--remote-allow-origins=*')

    result = list(result)

    # ----------处理插件extensions-------------
    ext = opt.extensions if isinstance(opt, ChromiumOptions) else opt._extension_files
    if ext:
        ext = ','.join(set(ext))
        ext = f'--load-extension={ext}'
        result.append(ext)

    return result


def set_prefs(opt):
    """处理启动配置中的prefs项，目前只能对已存在文件夹配置
    :param opt: DriverOptions或ChromiumOptions
    :return: None
    """
    if isinstance(opt, ChromiumOptions):
        prefs = opt.preferences
        del_list = opt._prefs_to_del
    else:
        prefs = opt.experimental_options.get('prefs', [])
        del_list = []

    if not opt.user_data_path:
        return

    args = opt.arguments
    user = 'Default'
    for arg in args:
        if arg.startswith('--profile-directory'):
            user = arg.split('=')[-1].strip()
            break

    prefs_file = Path(opt.user_data_path) / user / 'Preferences'

    if not prefs_file.exists():
        prefs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(prefs_file, 'w') as f:
            f.write('{}')

    with open(prefs_file, "r", encoding='utf-8') as f:
        prefs_dict = load(f)

        for pref in prefs:
            value = prefs[pref]
            pref = pref.split('.')
            _make_leave_in_dict(prefs_dict, pref, 0, len(pref))
            _set_value_to_dict(prefs_dict, pref, value)

        for pref in del_list:
            _remove_arg_from_dict(prefs_dict, pref)

    with open(prefs_file, 'w', encoding='utf-8') as f:
        dump(prefs_dict, f)


def test_connect(ip, port):
    """测试浏览器是否可用
    :param ip: 浏览器ip
    :param port: 浏览器端口
    :return: None
    """
    end_time = perf_counter() + 6
    while perf_counter() < end_time:
        try:
            tabs = requests_get(f'http://{ip}:{port}/json', timeout=10).json()
            for tab in tabs:
                if tab['type'] == 'page':
                    return
        except Exception:
            sleep(.2)

    if ip in ('127.0.0.1', 'localhost'):
        raise BrowserConnectError(f'\n连接浏览器失败，可能原因：\n1、浏览器未启动\n2、{port}端口不是Chromium内核浏览器\n'
                                  f'3、该浏览器未允许控制\n4、和已打开的浏览器冲突\n'
                                  f'请尝试用ChromiumOptions指定别的端口和指定浏览器路径')
    raise BrowserConnectError(f'{ip}:{port}浏览器无法链接。')


def _run_browser(port, path: str, args) -> Popen:
    """创建chrome进程
    :param port: 端口号
    :param path: 浏览器地址
    :param args: 启动参数
    :return: 进程对象
    """
    p = Path(path)
    p = str(p / 'chrome') if p.is_dir() else str(path)
    arguments = [p, f'--remote-debugging-port={port}']
    arguments.extend(args)
    return Popen(arguments, shell=False)


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
