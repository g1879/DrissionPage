# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   common.py
"""
from abc import abstractmethod
from html import unescape
from pathlib import Path
from re import split as re_SPLIT
from shutil import rmtree
from typing import Union
from zipfile import ZipFile

from lxml.html import HtmlElement
from selenium.webdriver.remote.webelement import WebElement


class DrissionElement(object):
    """SessionElement和DriverElement的基类"""

    def __init__(self, ele: Union[WebElement, HtmlElement], page=None):
        self._inner_ele = ele
        self.page = page

    @property
    def inner_ele(self) -> Union[WebElement, HtmlElement]:
        return self._inner_ele

    @property
    def is_valid(self):
        return True

    # @property
    # def text(self):
    #     return

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

    # @property
    # def css_path(self):
    #     return
    #
    # @property
    # def xpath(self):
    #     return

    @abstractmethod
    def ele(self, loc: Union[tuple, str], mode: str = None):
        pass

    @abstractmethod
    def eles(self, loc: Union[tuple, str]):
        pass

    # @abstractmethod
    # def attr(self, attr: str):
    #     pass


def str_to_loc(loc: str) -> tuple:
    """处理元素查找语句                                                                    \n
    查找方式：属性、tag name及属性、文本、xpath、css selector、id、class                      \n
    @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串    \n
    示例：                                                                                \n
        .ele_class                       - class等于ele_class的元素                        \n
        .:ele_class                      - class含有ele_class的元素                        \n
        #ele_id                          - id等于ele_id的元素                              \n
        #:ele_id                         - id含有ele_id的元素                              \n
        @class:ele_class                 - class含有ele_class的元素                        \n
        @class=ele_class                 - class等于ele_class的元素                        \n
        @class                           - 带class属性的元素                               \n
        tag:div                          - div元素                                        \n
        tag:div@class:ele_class          - class含有ele_class的div元素                     \n
        tag:div@class=ele_class          - class等于ele_class的div元素                     \n
        tag:div@text():search_text       - 文本含有search_text的div元素                     \n
        tag:div@text()=search_text       - 文本等于search_text的div元素                     \n
        text:search_text                 - 文本含有search_text的元素                        \n
        text=search_text                 - 文本等于search_text的元素                        \n
        xpath://div[@class="ele_class"]  - 用xpath查找                                     \n
        css:div.ele_class                - 用css selector查找                              \n
        xpath://div[@class="ele_class"]  - 等同于 x://div[@class="ele_class"]              \n
        css:div.ele_class                - 等同于 c:div.ele_class                          \n
        tag:div                          - 等同于 t:div                                    \n
        text:search_text                 - 等同于 tx:search_text                           \n
        text=search_text                 - 等同于 tx=search_text                           \n
    """
    loc_by = 'xpath'

    # .和#替换为class和id查找
    if loc.startswith('.'):
        if loc.startswith(('.=', '.:',)):
            loc = loc.replace('.', '@class', 1)
        else:
            loc = loc.replace('.', '@class=', 1)

    elif loc.startswith('#'):
        if loc.startswith(('#=', '#:',)):
            loc = loc.replace('#', '@id', 1)
        else:
            loc = loc.replace('#', '@id=', 1)

    elif loc.startswith(('t:', 't=')):
        loc = f'tag:{loc[2:]}'

    elif loc.startswith(('tx:', 'tx=')):
        loc = f'text{loc[2:]}'

    # 根据属性查找
    if loc.startswith('@'):
        r = re_SPLIT(r'([:=])', loc[1:], maxsplit=1)
        if len(r) == 3:
            mode = 'exact' if r[1] == '=' else 'fuzzy'
            loc_str = _make_xpath_str('*', f'@{r[0]}', r[2], mode)
        else:
            loc_str = f'//*[@{loc[1:]}]'

    # 根据tag name查找
    elif loc.startswith(('tag:', 'tag=')):
        if '@' not in loc[4:]:
            loc_str = f'//*[name()="{loc[4:]}"]'
        else:
            at_lst = loc[4:].split('@', maxsplit=1)
            r = re_SPLIT(r'([:=])', at_lst[1], maxsplit=1)
            if len(r) == 3:
                mode = 'exact' if r[1] == '=' else 'fuzzy'
                arg_str = 'text()' if r[0] in ('text()', 'tx()') else f'@{r[0]}'
                loc_str = _make_xpath_str(at_lst[0], arg_str, r[2], mode)
            else:
                loc_str = f'//*[name()="{at_lst[0]}" and @{r[0]}]'

    # 根据文本查找
    elif loc.startswith(('text:', 'text=')):
        if len(loc) > 5:
            mode = 'exact' if loc[4] == '=' else 'fuzzy'
            loc_str = _make_xpath_str('*', 'text()', loc[5:], mode)
        else:
            loc_str = '//*[not(text())]'

    # 用xpath查找
    elif loc.startswith(('xpath:', 'xpath=')):
        loc_str = loc[6:]
    elif loc.startswith(('x:', 'x=')):
        loc_str = loc[2:]

    # 用css selector查找
    elif loc.startswith(('css:', 'css=')):
        loc_by = 'css selector'
        loc_str = loc[4:]
    elif loc.startswith(('c:', 'c=')):
        loc_by = 'css selector'
        loc_str = loc[2:]

    # 根据文本模糊查找
    else:
        if loc:
            loc_str = _make_xpath_str('*', 'text()', loc, 'fuzzy')
        else:
            loc_str = '//*[not(text())]'

    return loc_by, loc_str


def _make_xpath_str(tag: str, arg: str, val: str, mode: str = 'fuzzy') -> str:
    """生成xpath语句                                          \n
    :param tag: 标签名
    :param arg: 属性名
    :param val: 属性值
    :param mode: 'exact' 或 'fuzzy'，对应精确或模糊查找
    :return: xpath字符串
    """
    tag_name = '' if tag == '*' else f'name()="{tag}" and '

    if mode == 'exact':
        return f'//*[{tag_name}{arg}={_make_search_str(val)}]'

    elif mode == 'fuzzy':
        if arg == 'text()':
            tag_name = '' if tag == '*' else f'{tag}/'
            return f'//{tag_name}text()[contains(., {_make_search_str(val)})]/..'
        else:
            return f"//*[{tag_name}contains({arg},{_make_search_str(val)})]"

    else:
        raise ValueError("Argument mode can only be 'exact' or 'fuzzy'.")


def _make_search_str(search_str: str) -> str:
    """将"转义，不知何故不能直接用 \ 来转义 \n
    :param search_str: 查询字符串
    :return: 把"转义后的字符串
    """
    parts = search_str.split('"')
    parts_num = len(parts)
    search_str = 'concat('

    for key, i in enumerate(parts):
        search_str += f'"{i}"'
        search_str += ',' + '\'"\',' if key < parts_num - 1 else ''

    search_str += ',"")'

    return search_str


def format_html(text: str, trans: bool = True) -> str:
    """处理html编码字符"""
    if not text:
        return text

    if trans:
        text = unescape(text)

    return text.replace('\xa0', ' ')


def translate_loc(loc: tuple) -> tuple:
    """把By类型的loc元组转换为css selector或xpath类型的  \n
    :param loc: By类型的loc元组
    :return: css selector或xpath类型的loc元组
    """
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

        if num and num[0] == '(' and num[-1] == ')' and num[1:-1].isdigit():
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
                rmtree(f, True)


def unzip(zip_path: str, to_path: str) -> Union[list, None]:
    """解压下载的chromedriver.zip文件"""
    if not zip_path:
        return

    with ZipFile(zip_path, 'r') as f:
        return [f.extract(f.namelist()[0], path=to_path)]


def get_exe_path_from_port(port: Union[str, int]) -> Union[str, None]:
    """获取端口号第一条进程的可执行文件路径      \n
    :param port: 端口号
    :return: 可执行文件的绝对路径
    """
    from os import popen
    from time import perf_counter
    process = popen(f'netstat -ano |findstr {port}').read().split('\n')[0]
    t = perf_counter()

    while not process and perf_counter() - t < 10:
        process = popen(f'netstat -ano |findstr {port}').read().split('\n')[0]

    processid = process[process.rfind(' ') + 1:]

    if not processid:
        return
    else:
        file_lst = popen(f'wmic process where processid={processid} get executablepath').read().split('\n')
        return file_lst[2].strip() if len(file_lst) > 2 else None
