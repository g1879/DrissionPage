# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   common.py
"""
import re
import shutil
from abc import abstractmethod
from pathlib import Path
from typing import Union

from requests_html import Element
from selenium.webdriver.remote.webelement import WebElement


class DrissionElement(object):
    """SessionElement和DriverElement的基类"""

    def __init__(self, ele: Union[Element, WebElement]):
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
    """处理元素查找语句                                               \n
    查找方式：属性、tag name及属性、文本、xpath、css selector           \n
    =表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串           \n
    示例：                                                            \n
        @class:ele_class - class含有ele_class的元素                    \n
        @class=ele_class - class等于ele_class的元素                    \n
        @class - 带class属性的元素                                     \n
        tag:div - div元素                                              \n
        tag:div@class:ele_class - class含有ele_class的div元素          \n
        tag:div@class=ele_class - class等于ele_class的div元素           \n
        tag:div@text():search_text - 文本含有search_text的div元素        \n
        tag:div@text()=search_text - 文本等于search_text的div元素        \n
        text:search_text - 文本含有search_text的元素                     \n
        text=search_text - 文本等于search_text的元素                     \n
        xpath://div[@class="ele_class"]                                 \n
        css:div.ele_class                                               \n
    """
    loc_by = 'xpath'
    if loc.startswith('@'):  # 根据属性查找
        r = re.split(r'([:=])', loc[1:], maxsplit=1)
        if len(r) == 3:
            mode = 'exact' if r[1] == '=' else 'fuzzy'
            loc_str = _make_xpath_str('*', f'@{r[0]}', r[2], mode)
        else:
            loc_str = f'//*[@{loc[1:]}]'
    elif loc.startswith(('tag=', 'tag:')):  # 根据tag name查找
        if '@' not in loc[4:]:
            loc_str = f'//*[name()="{loc[4:]}"]'
        else:
            at_lst = loc[4:].split('@', maxsplit=1)
            r = re.split(r'([:=])', at_lst[1], maxsplit=1)
            if len(r) == 3:
                mode = 'exact' if r[1] == '=' else 'fuzzy'
                arg_str = r[0] if r[0] == 'text()' else f'@{r[0]}'
                loc_str = _make_xpath_str(at_lst[0], arg_str, r[2], mode)
            else:
                loc_str = f'//*[name()="{at_lst[0]}" and @{r[0]}]'
    elif loc.startswith(('text=', 'text:')):  # 根据文本查找
        if len(loc) > 5:
            mode = 'exact' if loc[4] == '=' else 'fuzzy'
            loc_str = _make_xpath_str('*', 'text()', loc[5:], mode)
        else:
            loc_str = '//*[not(text())]'
    elif loc.startswith(('xpath=', 'xpath:')):  # 用xpath查找
        loc_str = loc[6:]
    elif loc.startswith(('css=', 'css:')):  # 用css selector查找
        loc_by = 'css selector'
        loc_str = loc[4:]
    else:
        if loc:
            loc_str = _make_xpath_str('*', 'text()', loc, 'fuzzy')
        else:
            loc_str = '//*[not(text())]'
    return loc_by, loc_str


def _make_xpath_str(tag: str, arg: str, val: str, mode: str = 'fuzzy') -> str:
    """生成xpath语句"""
    tag_name = '' if tag == '*' else f'name()="{tag}" and '
    if mode == 'exact':
        return f'//*[{tag_name}{arg}={_make_search_str(val)}]'
    else:
        return f"//*[{tag_name}contains({arg},{_make_search_str(val)})]"


def _make_search_str(search_str: str) -> str:
    """将"转义，不知何故不能直接用\""""
    parts = search_str.split('"')
    parts_num = len(parts)
    search_str = 'concat('
    for key, i in enumerate(parts):
        search_str += f'"{i}"'
        search_str += ',' + '\'"\',' if key < parts_num - 1 else ''
    search_str += ',"")'
    return search_str


def translate_loc_to_xpath(loc) -> tuple:
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


def get_available_file_name(folder_path: str, file_name: str) -> str:
    """检查文件是否重名，并返回可以使用的文件名  \n
    :param folder_path: 文件夹路径
    :param file_name: 要检查的文件名
    :return: 可用的文件名
    """
    folder_path = Path(folder_path).absolute()
    file_Path = folder_path.joinpath(file_name)
    while file_Path.exists():
        ext_name = file_Path.suffix
        base_name = file_Path.stem
        num = base_name.split(' ')[-1]
        if num[0] == '(' and num[-1] == ')' and num[1:-1].isdigit():
            num = int(num[1:-1])
            file_name = f'{base_name.replace(f"({num})", "", -1)}({num + 1}){ext_name}'
        else:
            file_name = f'{base_name} (1){ext_name}'
        file_Path = folder_path.joinpath(file_name)
    return file_name


def clean_folder(folder_path: str, ignore: list = None) -> None:
    """清空一个文件夹，除了ignore里的文件和文件夹  \n
    :param folder_path: 要清空的文件夹路径
    :param ignore: 忽略列表
    :return: None
    """
    ignore = [] if not ignore else ignore
    p = Path(folder_path)
    for f in p.iterdir():
        if f.name not in ignore:
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f, True)
