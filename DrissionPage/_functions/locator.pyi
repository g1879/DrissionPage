# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from typing import Union


def locator_to_tuple(loc: str) -> dict: ...


def is_loc(text: str) -> bool: ...


def get_loc(loc: Union[tuple, str], translate_css: bool = False, css_mode: bool = False) -> tuple: ...


def str_to_xpath_loc(loc: str) -> tuple: ...


def str_to_css_loc(loc: str) -> tuple: ...


def translate_loc(loc: tuple) -> tuple: ...


def translate_css_loc(loc: tuple) -> tuple: ...


def css_trans(txt: str) -> str: ...
