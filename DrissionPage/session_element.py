# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   session_element.py
"""
import re
from html import unescape
from typing import Union, List

from requests_html import Element, BaseParser

from .common import DrissionElement, get_loc_from_str, translate_loc_to_xpath


class SessionElement(DrissionElement):
    """session模式的元素对象，包装了一个Element对象，并封装了常用功能"""
    def __init__(self, ele: Element):
        super().__init__(ele)

    def __repr__(self):
        attrs = [f"{attr}='{self.attrs[attr]}'" for attr in self.attrs]
        return f'<SessionElement {self.tag} {" ".join(attrs)}>'

    @property
    def attrs(self) -> dict:
        """以字典格式返回元素所有属性的名称和值"""
        attrs = dict(self.inner_ele.attrs)
        for attr in ['class', 'rel']:
            if attr in attrs:
                attrs[attr] = ' '.join(attrs[attr])
        return attrs

    @property
    def text(self) -> str:
        """元素内文本"""
        return unescape(self._inner_ele.text).replace('\xa0', ' ')

    @property
    def html(self) -> str:
        """元素innerHTML"""
        html = unescape(self._inner_ele.html).replace('\xa0', ' ')
        r = re.match(r'<.*?>(.*)</.*?>', html, flags=re.DOTALL)
        return None if not r else r.group(1)

    @property
    def tag(self) -> str:
        """获取标签名"""
        return self._inner_ele.tag

    @property
    def parent(self) -> Union[DrissionElement, None]:
        """requests_html的Element打包了lxml的元素对象，从lxml元素对象读取上下级关系后再重新打包"""
        try:
            return SessionElement(Element(element=self.inner_ele.element.xpath('..')[0], url=self.inner_ele.url))
        except IndexError:
            return None

    @property
    def next(self) -> Union[DrissionElement, None]:
        """requests_html的Element打包了lxml的元素对象，从lxml元素对象读取上下级关系后再重新打包"""
        try:
            return SessionElement(
                Element(element=self.inner_ele.element.xpath('./following-sibling::*[1]')[0], url=self.inner_ele.url))
        except IndexError:
            return None

    @property
    def prev(self) -> Union[DrissionElement, None]:
        """requests_html的Element打包了lxml的元素对象，从lxml元素对象读取上下级关系后再重新打包"""
        try:
            return SessionElement(
                Element(element=self.inner_ele.element.xpath('./preceding-sibling::*[1]')[0], url=self.inner_ele.url))
        except IndexError:
            return None

    def ele(self, loc_or_str: Union[tuple, str], mode: str = None, show_errmsg: bool = False):
        """根据loc获取元素或列表，可用用字符串控制获取方式，可选'@属性名:'、'tag:'、'text:'、'css:'、'xpath:'
        如没有控制关键字，会按字符串文本搜索
        例：ele.find('id:ele_id')，ele.find('首页')
        """
        if isinstance(loc_or_str, str):
            loc_or_str = get_loc_from_str(loc_or_str)
        elif isinstance(loc_or_str, tuple) and len(loc_or_str) == 2:
            loc_or_str = translate_loc_to_xpath(loc_or_str)
        else:
            raise ValueError('loc_or_str must be tuple or str.')

        loc_str = None
        if loc_or_str[0] == 'xpath':
            # Element的html是包含自己的，要如下处理，使其只检索下级的
            loc_str = f'./{self.tag}{loc_or_str[1].lstrip(".")}'
        elif loc_or_str[0] == 'css selector':
            loc_str = f':root>{self.tag}{loc_or_str[1]}'
        loc_or_str = loc_or_str[0], loc_str

        return execute_session_find(self.inner_ele, loc_or_str, mode, show_errmsg)

    def eles(self, loc_or_str: Union[tuple, str], show_errmsg: bool = False):
        return self.ele(loc_or_str, mode='all', show_errmsg=show_errmsg)

    def attr(self, attr: str) -> str:
        """获取属性值"""
        try:
            if attr == 'href':
                # 如直接获取attr只能获取相对地址
                for link in self._inner_ele.absolute_links:
                    return link
            elif attr == 'class':
                class_str = ''
                for key, i in enumerate(self._inner_ele.attrs['class']):
                    class_str += ' ' if key > 0 else ''
                    class_str += i
                return class_str
            elif attr == 'text':
                return self.text
            else:
                return self._inner_ele.attrs[attr]
        except:
            return ''


def execute_session_find(page_or_ele: BaseParser, loc: tuple, mode: str = 'single', show_errmsg: bool = False) \
        -> Union[SessionElement, List[SessionElement]]:
    """执行session模式元素的查找
    页面查找元素及元素查找下级元素皆使用此方法
    :param page_or_ele: session模式页面或元素
    :param loc: 元素定位语句
    :param mode: 'single'或'all'
    :param show_errmsg: 是否显示错误信息
    :return: 返回SessionElement元素或列表
    """
    mode = mode or 'single'
    if mode not in ['single', 'all']:
        raise ValueError("mode must be 'single' or 'all'.")
    loc_by, loc_str = loc
    msg = result = first = None
    try:
        if mode == 'single':
            msg = 'Element not found.'
            first = True
        elif mode == 'all':
            msg = 'Elements not found.'
            first = False

        if loc_by == 'xpath':
            ele = page_or_ele.xpath(loc_str, first=first)
        else:
            ele = page_or_ele.find(loc_str, first=first)

        if mode == 'single':
            result = SessionElement(ele) if ele else None
        elif mode == 'all':
            result = [SessionElement(e) for e in ele]

        return result
    except:
        if show_errmsg:
            print(msg, loc)
            raise
        return [] if mode == 'all' else None
