# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union

from .query_locator import Q


def locator_to_tuple(loc: Union[str, Q]) -> dict:
    """解析定位字符串生成dict格式数据
    :param loc: 待处理的字符串
    :return: 格式： {'and': bool, 'args': ['属性名称', '匹配方式', '属性值', 是否否定]}，查询定位符返回 ('query', ast)
    """
    ...


def is_query_loc(loc: Union[str, Q]) -> bool:
    """返回loc是否新引擎查询定位符（Q 对象或 '?' 开头字符串）"""
    ...


def query_to_loc(loc: Union[str, Q]) -> tuple:
    """把 Q / '?' 查询编译为定位元组：pure-xpath 返回 ('xpath', xp)，hybrid 返回 ('query', ast)"""
    ...


def is_str_loc(text: str) -> bool:
    """返回text是否定位符"""
    ...


def is_selenium_loc(loc: tuple) -> bool:
    """返回tuple是否selenium的定位符"""
    ...


def get_loc(loc: Union[tuple, str, Q],
            translate_css: bool = False) -> tuple:
    """接收本库定位语法或selenium定位元组，转换为标准定位元组，可翻译css selector为xpath
    :param loc: 本库定位语法或selenium定位元组
    :param translate_css: 是否翻译css selector为xpath，用于相对定位
    :return: DrissionPage定位元组
    """
    ...


def str_to_xpath_loc(loc: str) -> tuple:
    """处理元素查找语句
    :param loc: 查找语法字符串
    :return: 匹配符元组
    """
    ...


def str_to_css_loc(loc: str) -> tuple:
    """处理元素查找语句
    :param loc: 查找语法字符串
    :return: 匹配符元组
    """
    ...


def quotes_escape(search_str: str) -> str:
    """将"转义，不知何故不能直接用 斜杠 来转义
    :param search_str: 查询字符串
    :return: 把"转义后的字符串
    """
    ...


def translate_loc(loc: tuple) -> tuple:
    """把By类型的loc元组转换为css selector或xpath类型的
    :param loc: By类型的loc元组
    :return: css selector或xpath类型的loc元组
    """
    ...


def translate_css_loc(loc: tuple) -> tuple:
    """把By类型的loc元组转换为css selector或xpath类型的
    :param loc: By类型的loc元组
    :return: css selector或xpath类型的loc元组
    """
    ...


def css_trans(txt: str) -> str:
    """css字符串中特殊字符转义
    :param txt: 要处理的文本
    :return: 处理后的文本
    """
    ...
