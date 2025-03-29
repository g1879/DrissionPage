# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Optional, Tuple

from .._base.base import DrissionElement, BaseParser
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_page import ChromiumPage
from .._pages.chromium_tab import ChromiumTab


def get_ele_txt(e: DrissionElement) -> str:
    """获取元素内所有文本
    :param e: 元素对象
    :return: 元素内所有文本
    """
    ...


def format_html(text: str) -> str:
    """处理html编码字符
    :param text: html文本
    :return: 格式化后的html文本
    """
    ...


def location_in_viewport(page: ChromiumBase, loc_x: float, loc_y: float) -> bool:
    """判断给定的坐标是否在视口中          |n
    :param page: ChromePage对象
    :param loc_x: 页面绝对坐标x
    :param loc_y: 页面绝对坐标y
    :return: bool
    """
    ...


def offset_scroll(ele: ChromiumElement, offset_x: float, offset_y: float) -> Tuple[int, int]:
    """接收元素及偏移坐标，把坐标滚动到页面中间，返回该点坐标
    有偏移量时以元素左上角坐标为基准，没有时以click_point为基准
    :param ele: 元素对象
    :param offset_x: 偏移量x
    :param offset_y: 偏移量y
    :return: 相对坐标
    """
    ...


def make_absolute_link(link: str, baseURI: str = None) -> str:
    """获取绝对url
    :param link: 超链接
    :param baseURI: 页面或iframe的url
    :return: 绝对链接
    """
    ...


def is_js_func(func: str) -> bool:
    """检查文本是否js函数"""
    ...


def get_blob(page: ChromiumBase, url: str, as_bytes: bool = True) -> bytes:
    """获取知道blob资源
    :param page: 资源所在页面对象
    :param url: 资源url
    :param as_bytes: 是否以字节形式返回
    :return: 资源内容
    """
    ...


def save_page(tab: Union[ChromiumPage, ChromiumTab],
              path: Union[Path, str, None] = None,
              name: Optional[str] = None,
              as_pdf: bool = False,
              kwargs: dict = None) -> Union[bytes, str]:
    """把当前页面保存为文件，如果path和name参数都为None，只返回文本
    :param tab: Tab或Page对象
    :param path: 保存路径，为None且name不为None时保存在当前路径
    :param name: 文件名，为None且path不为None时用title属性值
    :param as_pdf: 为Ture保存为pdf，否则为mhtml且忽略kwargs参数
    :param kwargs: pdf生成参数
    :return: as_pdf为True时返回bytes，否则返回文件文本
    """
    ...


def get_mhtml(page: Union[ChromiumPage, ChromiumTab],
              path: Optional[Path] = None,
              name: Optional[str] = None) -> Union[bytes, str]:
    """把当前页面保存为mhtml文件，如果path和name参数都为None，只返回mhtml文本
    :param page: 要保存的页面对象
    :param path: 保存路径，为None且name不为None时保存在当前路径
    :param name: 文件名，为None且path不为None时用title属性值
    :return: mhtml文本
    """
    ...


def get_pdf(page: Union[ChromiumPage, ChromiumTab],
            path: Optional[Path] = None,
            name: Optional[str] = None,
            kwargs: dict = None) -> Union[bytes, str]:
    """把当前页面保存为pdf文件，如果path和name参数都为None，只返回字节
    :param page: 要保存的页面对象
    :param path: 保存路径，为None且name不为None时保存在当前路径
    :param name: 文件名，为None且path不为None时用title属性值
    :param kwargs: pdf生成参数
    :return: pdf文本
    """
    ...


def tree(ele_or_page: BaseParser,
         text: Union[int, bool] = False,
         show_js: bool = False,
         show_css: bool = False) -> None:
    """把页面或元素对象DOM结构打印出来
    :param ele_or_page: 页面或元素对象
    :param text: 是否打印文本，输入数字可指定打印文本长度上线
    :param show_js: 打印文本时是否包含<script>内文本，text参数为False时无效
    :param show_css: 打印文本时是否包含<style>内文本，text参数为False时无效
    :return: None
    """
    ...


def format_headers(txt: str) -> dict:
    """从浏览器复制的文本生成dict格式headers，文本用换行分隔
    :param txt: 从浏览器复制的原始文本格式headers
    :return: dict格式headers
    """
    ...
