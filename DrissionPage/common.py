# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   common.py
"""
from abc import abstractmethod
from pathlib import Path
from typing import Union

from requests_html import Element
from selenium.webdriver.remote.webelement import WebElement


class DrissionElement(object):
    def __init__(self, ele):
        self._inner_ele = ele

    @property
    def inner_ele(self) -> Union[WebElement, Element]:
        return self._inner_ele

    @property
    def is_valid(self):
        return True

    @property
    def text(self):
        return

    @property
    def html(self):
        return

    @property
    def tag(self):
        return

    @property
    def parent(self):
        return

    @property
    def next(self):
        return

    @property
    def prev(self):
        return

    @abstractmethod
    def ele(self, loc: tuple, mode: str = None, show_errmsg: bool = True):
        pass

    @abstractmethod
    def eles(self, loc: tuple, show_errmsg: bool = True):
        pass

    @abstractmethod
    def attr(self, attr: str):
        pass


def get_loc_from_str(loc: str) -> tuple:
    loc_item = loc.split(':', 1)
    by = loc_item[0]
    loc_by = 'xpath'
    if by == 'tag' and len(loc_item) == 2:
        loc_str = f'//{loc_item[1]}'
    elif by.startswith('@') and len(loc_item) == 2:
        loc_str = f'//*[{by}="{loc_item[1]}"]'
    elif by.startswith('@') and len(loc_item) == 1:
        loc_str = f'//*[{by}]'
    elif by == 'text' and len(loc_item) == 2:
        loc_str = _make_xpath_search_str(loc_item[1])
    elif by == 'xpath' and len(loc_item) == 2:
        loc_str = loc_item[1]
    elif by == 'css' and len(loc_item) == 2:
        loc_by = 'css selector'
        loc_str = loc_item[1]
    else:
        loc_str = _make_xpath_search_str(by)
    return loc_by, loc_str


def _make_xpath_search_str(search_str: str):
    # 将"转义，不知何故不能直接用\"
    parts = search_str.split('"')
    parts_num = len(parts)
    search_str = 'concat('
    for key, i in enumerate(parts):
        search_str += f'"{i}"'
        search_str += ',' + '\'"\',' if key < parts_num - 1 else ''
    search_str += ',"")'
    return f"//*[contains(text(),{search_str})]"


def translate_loc_to_xpath(loc):
    """把By类型转为xpath或css selector"""
    loc_by = 'xpath'
    loc_str = None
    if loc[0] == 'xpath':
        loc_str = loc[1]
    elif loc[0] == 'css selector':
        loc_by = 'css selector'
        loc_str = loc[1]
    elif loc[0] == 'id':
        loc_str = f'//*[@id="{loc[1]}"]'
    elif loc[0] == 'class name':
        loc_str = f'//*[@class="{loc[1]}"]'
    elif loc[0] == 'link text':
        loc_str = f'//a[text()="{loc[1]}"]'
    elif loc[0] == 'name':
        loc_str = f'//*[@name="{loc[1]}"]'
    elif loc[0] == 'tag name':
        loc_str = f'//{loc[1]}'
    elif loc[0] == 'partial link text':
        loc_str = f'//a[contains(text(),"{loc[1]}")]'
    return loc_by, loc_str


def avoid_duplicate_name(folder_path: str, file_name: str) -> str:
    """检查文件是否重名，并返回可以使用的文件名
    :param folder_path: 文件夹路径
    :param file_name: 要检查的文件名
    :return: 可用的文件名
    """
    file_Path = Path(folder_path).joinpath(file_name)
    while file_Path.exists():
        ext_name = file_Path.suffix
        base_name = file_Path.stem
        num = base_name.split(' ')[-1]
        if num[0] == '(' and num[-1] == ')' and num[1:-1].isdigit():
            num = int(num[1:-1])
            file_name = f'{base_name.replace(f"({num})", "", -1)}({num + 1}){ext_name}'
        else:
            file_name = f'{base_name} (1){ext_name}'
        file_Path = Path(folder_path).joinpath(file_name)
    return file_name
