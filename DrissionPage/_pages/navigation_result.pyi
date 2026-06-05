# -*- coding:utf-8 -*-
from typing import Optional


class NavigationResult(object):
    url: str
    loaded: bool
    final_url: Optional[str]
    status: Optional[int]
    from_performance: bool

    def __init__(self,
                 url: str,
                 loaded: bool,
                 final_url: Optional[str] = None,
                 status: Optional[int] = None,
                 from_performance: bool = False): ...

    def __bool__(self) -> bool: ...

    @property
    def ok(self) -> bool: ...

    @property
    def http_error(self) -> bool: ...
