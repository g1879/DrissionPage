# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from typing import Union


def get_loc(loc: Union[tuple, str], translate_css: bool = False) -> tuple: ...


def str_to_loc(loc: str) -> tuple: ...


def translate_loc(loc: tuple) -> tuple: ...
