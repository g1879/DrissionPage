# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Any, Optional

from .._base.base import BasePage


class NoneElement(object):
    _none_ele_value: Any = ...
    _none_ele_return_value: Any = ...
    method: Optional[str] = ...
    args: Optional[dict] = ...

    def __init__(self,
                 page: BasePage = None,
                 method: str = None,
                 args: dict = None):
        """
        :param page: 元素所在页面
        :param method: 查找元素的方法
        :param args: 查找元素的参数
        """
        ...

    def __call__(self, *args, **kwargs) -> NoneElement: ...

    def __repr__(self) -> str: ...

    def __getattr__(self, item: str) -> str: ...

    def __eq__(self, other: Any) -> bool: ...

    def __bool__(self) -> bool: ...
