# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union


def locator_to_tuple(loc: str) -> dict:
    """解析定位字符串生成dict格式数据
    :param loc: 待处理的字符串
    :return: 格式： {'and': bool, 'args': ['属性名称', '匹配方式', '属性值', 是否否定]}
    """
    ...


def is_str_loc(text: str) -> bool:
    """返回text是否定位符"""
    ...


def is_selenium_loc(loc: tuple) -> bool:
    """返回tuple是否selenium的定位符"""
    ...


def get_loc(loc: Union[tuple, str],
            translate_css: bool = False,
            css_mode: bool = False) -> tuple:
    """接收本库定位语法或selenium定位元组，转换为标准定位元组，可翻译css selector为xpath
    :param loc: 本库定位语法或selenium定位元组
    :param translate_css: 是否翻译css selector为xpath，用于相对定位
    :param css_mode: 是否尽量用css selector方式
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
