# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from typing import Union


def get_exe_from_port(port: Union[str, int]) -> Union[str, None]: ...


def get_pid_from_port(port: Union[str, int]) -> Union[str, None]: ...


def get_usable_path(path: Union[str, Path]) -> Path: ...


def make_valid_name(full_name: str) -> str: ...


def get_long(txt) -> int: ...


def port_is_using(ip: str, port: Union[str, int]) -> bool: ...


def clean_folder(folder_path: Union[str, Path], ignore: Union[tuple, list] = None) -> None: ...


def unzip(zip_path: str, to_path: str) -> Union[list, None]: ...
