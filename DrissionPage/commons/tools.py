# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from re import search, sub
from shutil import rmtree
from zipfile import ZipFile


def get_exe_from_port(port):
    """获取端口号第一条进程的可执行文件路径
    :param port: 端口号
    :return: 可执行文件的绝对路径
    """
    from os import popen

    pid = get_pid_from_port(port)
    if not pid:
        return
    else:
        file_lst = popen(f'wmic process where processid={pid} get executablepath').read().split('\n')
        return file_lst[2].strip() if len(file_lst) > 2 else None


def get_pid_from_port(port):
    """获取端口号第一条进程的pid
    :param port: 端口号
    :return: 进程id
    """
    from platform import system
    if system().lower() != 'windows' or port is None:
        return None

    from os import popen
    from time import perf_counter

    try:  # 避免Anaconda中可能产生的报错
        process = popen(f'netstat -ano |findstr {port}').read().split('\n')[0]

        t = perf_counter()
        while not process and perf_counter() - t < 5:
            process = popen(f'netstat -ano |findstr {port}').read().split('\n')[0]

        return process.split(' ')[-1] or None

    except AttributeError:
        return None


def get_usable_path(path):
    """检查文件或文件夹是否有重名，并返回可以使用的路径
    :param path: 文件或文件夹路径
    :return: 可用的路径，Path对象
    """
    path = Path(path)
    parent = path.parent
    path = parent / make_valid_name(path.name)
    name = path.stem if path.is_file() else path.name
    ext = path.suffix if path.is_file() else ''

    first_time = True

    while path.exists():
        r = search(r'(.*)_(\d+)$', name)

        if not r or (r and first_time):
            src_name, num = name, '1'
        else:
            src_name, num = r.group(1), int(r.group(2)) + 1

        name = f'{src_name}_{num}'
        path = parent / f'{name}{ext}'
        first_time = None

    return path


def make_valid_name(full_name):
    """获取有效的文件名
    :param full_name: 文件名
    :return: 可用的文件名
    """
    # ----------------去除前后空格----------------
    full_name = full_name.strip()

    # ----------------使总长度不大于255个字符（一个汉字是2个字符）----------------
    r = search(r'(.*)(\.[^.]+$)', full_name)  # 拆分文件名和后缀名
    if r:
        name, ext = r.group(1), r.group(2)
        ext_long = len(ext)
    else:
        name, ext = full_name, ''
        ext_long = 0

    while get_long(name) > 255 - ext_long:
        name = name[:-1]

    full_name = f'{name}{ext}'

    # ----------------去除不允许存在的字符----------------
    return sub(r'[<>/\\|:*?\n]', '', full_name)


def get_long(txt):
    """返回字符串中字符个数（一个汉字是2个字符）
    :param txt: 字符串
    :return: 字符个数
    """
    txt_len = len(txt)
    return int((len(txt.encode('utf-8')) - txt_len) / 2 + txt_len)


def port_is_using(ip, port):
    """检查端口是否被占用
    :param ip: 浏览器地址
    :param port: 浏览器端口
    :return: bool
    """
    from socket import socket, AF_INET, SOCK_STREAM
    s = socket(AF_INET, SOCK_STREAM)
    result = s.connect_ex((ip, int(port)))
    s.close()
    return result == 0


def clean_folder(folder_path, ignore=None):
    """清空一个文件夹，除了ignore里的文件和文件夹
    :param folder_path: 要清空的文件夹路径
    :param ignore: 忽略列表
    :return: None
    """
    ignore = [] if not ignore else ignore
    p = Path(folder_path)

    for f in p.iterdir():
        if f.name not in ignore:
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                rmtree(f, True)


def unzip(zip_path, to_path):
    """解压下载的chromedriver.zip文件"""
    if not zip_path:
        return

    with ZipFile(zip_path, 'r') as f:
        return [f.extract(f.namelist()[0], path=to_path)]
