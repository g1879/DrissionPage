# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path
from typing import Union

from .downloader import DownloadMission
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_tab import WebPageTab, ChromiumTab


class Clicker(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    def __call__(self, by_js: Union[bool, str, None] = False, timeout: float = 1.5, wait_stop: bool = True) -> bool: ...

    def left(self, by_js: Union[bool, str, None] = False, timeout: float = 1.5, wait_stop: bool = True) -> bool: ...

    def right(self) -> None: ...

    def middle(self, get_tab: bool = True) -> Union[ChromiumTab, WebPageTab, None]: ...

    def at(self,
           offset_x: float = None,
           offset_y: float = None,
           button: str = 'left',
           count: int = 1) -> None: ...

    def multi(self, times: int = 2) -> None: ...

    def to_download(self,
                    save_path: Union[str, Path] = None,
                    rename: str = None,
                    suffix: str = None,
                    new_tab: bool = False,
                    by_js: bool = False,
                    timeout: float = None) -> DownloadMission: ...

    def to_upload(self, file_paths: Union[str, Path, list, tuple], by_js: bool = False) -> None: ...

    def for_new_tab(self, by_js: bool = False) -> Union[ChromiumTab, WebPageTab]: ...

    def _click(self, client_x: float, client_y: float, button: str = 'left', count: int = 1) -> None: ...
