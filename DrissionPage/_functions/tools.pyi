# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from os import popen
from pathlib import Path
from threading import Lock
from typing import Union, Tuple

from .._pages.chromium_base import ChromiumBase


class PortFinder(object):
    used_port: dict = ...
    lock: Lock = ...
    tmp_dir: Path = ...

    def __init__(self, path: Union[str, Path] = None): ...

    @staticmethod
    def get_port(scope: Tuple[int, int] = None) -> Tuple[int, str]: ...


def port_is_using(ip: str, port: Union[str, int]) -> bool: ...


def clean_folder(folder_path: Union[str, Path], ignore: Union[tuple, list] = None) -> None: ...


def show_or_hide_browser(page: ChromiumBase, hide: bool = True) -> None: ...


def get_browser_progress_id(progress: Union[popen, None], address: str) -> Union[str, None]: ...


def get_hwnds_from_pid(pid: Union[str, int], title: str) -> list: ...


def wait_until(function: callable, kwargs: dict = None, timeout: float = 10): ...


def configs_to_here(file_name: Union[Path, str] = None) -> None: ...


def raise_error(result: dict, ignore=None) -> None: ...
