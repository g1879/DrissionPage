# -*- coding:utf-8 -*-
from pathlib import Path
from typing import Literal, Union, Tuple, List, Any

from _pages.session_page import SessionPage
from .._elements.chromium_element import ChromiumElement
from .._elements.session_element import SessionElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame

PIC_TYPE = Literal['jpg', 'jpeg', 'png', 'webp', True]


class Getter(object):
    _obj = ...

    def __init__(self, obj): ...


class ChromiumElementGetter(Getter):
    _obj: ChromiumElement = ...

    def screenshot(self,
                   path: [str, Path] = None,
                   name: str = None,
                   as_bytes: PIC_TYPE = None,
                   as_base64: PIC_TYPE = None,
                   scroll_to_center: bool = True) -> Union[str, bytes]: ...

    def attribute(self, name: str) -> Union[str, None]: ...

    def property(self, name: str) -> Union[str, int, None]: ...

    def style(self, style: str, pseudo_ele: str = '') -> str: ...

    def source(self, timeout: float = None, base64_to_bytes: bool = True) -> Union[bytes, str, None]: ...


class SessionElementGetter(Getter):
    _obj: SessionElement = ...

    def attribute(self, name: str) -> str: ...


class ChromiumBaseGetter(Getter):
    _obj: ChromiumBase = ...

    def __call__(self, url: str, show_errmsg: bool = False, retry: int = None,
                 interval: float = None, timeout: float = None) -> Union[None, bool]: ...

    def cookies(self, as_dict: bool = False, all_domains: bool = False,
                all_info: bool = False) -> Union[list, dict]: ...

    def frame(self, loc_ind_ele: Union[str, int, tuple, ChromiumFrame], timeout: float = None) -> ChromiumFrame: ...

    def frames(self, locator: Union[str, tuple] = None, timeout: float = None) -> List[ChromiumFrame]: ...

    def session_storage(self, item: str = None) -> Union[str, dict, None]: ...

    def local_storage(self, item: str = None) -> Union[str, dict, None]: ...

    def screenshot(self, path: [str, Path] = None, name: str = None, as_bytes: PIC_TYPE = None,
                   as_base64: PIC_TYPE = None, full_page: bool = False, left_top: Tuple[int, int] = None,
                   right_bottom: Tuple[int, int] = None) -> Union[str, bytes]: ...


class ChromiumFrameGetter(ChromiumBaseGetter):
    _obj: ChromiumFrame = ...

    def screenshot(self, path=None, name=None, as_bytes=None, as_base64=None) -> Union[str, bytes]: ...


class SessionPageGetter(Getter):
    _obj: SessionPage = ...

    def __call__(self,
                 url: Union[Path, str],
                 show_errmsg: bool | None = False,
                 retry: int | None = None,
                 interval: float | None = None,
                 timeout: float | None = None,
                 params: dict | None = ...,
                 data: Union[dict, str, None] = ...,
                 json: Union[dict, str, None] = ...,
                 headers: dict | None = ...,
                 cookies: Any | None = ...,
                 files: Any | None = ...,
                 auth: Any | None = ...,
                 allow_redirects: bool = ...,
                 proxies: dict | None = ...,
                 hooks: Any | None = ...,
                 stream: Any | None = ...,
                 verify: Any | None = ...,
                 cert: Any | None = ...) -> bool: ...

    def cookies(self,
                as_dict: bool = False,
                all_domains: bool = False,
                all_info: bool = False) -> Union[dict, list]: ...
