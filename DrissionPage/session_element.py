# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   session_element.py
"""
from re import match, DOTALL
from typing import Union, List, Tuple
from urllib.parse import urlparse, urljoin, urlunparse

from lxml.etree import tostring
from lxml.html import HtmlElement, fromstring

from .base import DrissionElement, BasePage, BaseElement
from .common import get_ele_txt, get_loc


class SessionElement(DrissionElement):
    """session模式的元素对象，包装了一个lxml的Element对象，并封装了常用功能"""

    def __init__(self, ele: HtmlElement, page=None):
        """初始化对象                                                          \n
        :param ele: 被包装的HtmlElement元素
        :param page: 元素所在页面对象，如果是从 html 文本生成的元素，则为 None
        """
        super().__init__(ele, page)

    def __repr__(self) -> str:
        attrs = [f"{attr}='{self.attrs[attr]}'" for attr in self.attrs]
        return f'<SessionElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, loc_or_str: Union[Tuple[str, str], str], timeout=None):
        """在内部查找元素                                                  \n
        例：ele2 = ele1('@id=ele_id')                                    \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本
        """
        return self.ele(loc_or_str)

    @property
    def tag(self) -> str:
        """返回元素类型"""
        return self._inner_ele.tag

    @property
    def html(self) -> str:
        """返回outerHTML文本"""
        html = tostring(self._inner_ele, method="html").decode()
        return html[:html.rfind('>') + 1]  # tostring()会把跟紧元素的文本节点也带上，因此要去掉

    @property
    def inner_html(self) -> str:
        """返回元素innerHTML文本"""
        r = match(r'<.*?>(.*)</.*?>', self.html, flags=DOTALL)
        return '' if not r else r.group(1)

    @property
    def attrs(self) -> dict:
        """返回元素所有属性及值"""
        return {attr: self.attr(attr) for attr, val in self.inner_ele.items()}

    @property
    def text(self) -> str:
        """返回元素内所有文本"""
        return get_ele_txt(self)

    @property
    def raw_text(self) -> str:
        """返回未格式化处理的元素内文本"""
        return str(self._inner_ele.text_content())

    def attr(self, attr: str) -> Union[str, None]:
        """返回attribute属性值                           \n
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        # 获取href属性时返回绝对url
        if attr == 'href':
            link = self.inner_ele.get('href')
            # 若为链接为None、js或邮件，直接返回
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link

            else:  # 其它情况直接返回绝对url
                return self._make_absolute(link)

        elif attr == 'src':
            return self._make_absolute(self.inner_ele.get('src'))

        elif attr == 'text':
            return self.text

        elif attr == 'innerText':
            return self.raw_text

        elif attr in ('html', 'outerHTML'):
            return self.html

        elif attr == 'innerHTML':
            return self.inner_html

        else:
            return self.inner_ele.get(attr)

    def ele(self, loc_or_str: Union[Tuple[str, str], str], timeout=None):
        """返回当前元素下级符合条件的第一个元素、属性或节点文本                      \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_str)

    def eles(self, loc_or_str: Union[Tuple[str, str], str], timeout=None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本                       \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, single=False)

    def s_ele(self, loc_or_str: Union[Tuple[str, str], str] = None):
        """返回当前元素下级符合条件的第一个元素、属性或节点文本                       \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_str)

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本                       \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, single=False)

    def _ele(self, loc_or_str: Union[Tuple[str, str], str], timeout=None, single: bool = True):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个           \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和父类对应
        :param single: True则返回第一个，False则返回全部
        :return: SessionElement对象
        """
        return make_session_ele(self, loc_or_str, single)

    def _get_ele_path(self, mode) -> str:
        """获取css路径或xpath路径
        :param mode: 'css' 或 'xpath'
        :return: css路径或xpath路径
        """
        path_str = ''
        ele = self

        while ele:
            if mode == 'css':
                brothers = len(ele.eles(f'xpath:./preceding-sibling::*'))
                path_str = f'>:nth-child({brothers + 1}){path_str}'
            else:
                brothers = len(ele.eles(f'xpath:./preceding-sibling::{ele.tag}'))
                path_str = f'/{ele.tag}[{brothers + 1}]{path_str}' if brothers > 0 else f'/{ele.tag}{path_str}'

            ele = ele.parent()

        return f':root{path_str[1:]}' if mode == 'css' else path_str

    # ----------------session独有方法-----------------------
    def _make_absolute(self, link) -> str:
        """获取绝对url
        :param link: 超链接
        :return: 绝对链接
        """
        if not link:
            return link

        parsed = urlparse(link)._asdict()

        # 相对路径，与页面url拼接并返回
        if not parsed['netloc']:  # 相对路径，与
            return urljoin(self.page.url, link)

        # 绝对路径但缺少协议，从页面url获取协议并修复
        if not parsed['scheme']:
            parsed['scheme'] = urlparse(self.page.url).scheme
            parsed = tuple(v for v in parsed.values())
            return urlunparse(parsed)

        # 绝对路径且不缺协议，直接返回
        return link


def make_session_ele(html_or_ele: Union[str, BaseElement, BasePage],
                     loc: Union[str, Tuple[str, str]] = None,
                     single: bool = True) -> Union[SessionElement, List[SessionElement], str, None]:
    """从接收到的对象或html文本中查找元素，返回SessionElement对象                 \n
    如要直接从html生成SessionElement而不在下级查找，loc输入None即可               \n
    :param html_or_ele: html文本、BaseParser对象
    :param loc: 定位元组或字符串，为None时不在下级查找，返回根元素
    :param single: True则返回第一个，False则返回全部
    :return: 返回SessionElement元素或列表，或属性文本
    """
    # ---------------处理定位符---------------
    if not loc:
        if isinstance(html_or_ele, SessionElement):
            return html_or_ele if single else [html_or_ele]

        loc = ('xpath', '.')

    elif isinstance(loc, (str, tuple)):
        loc = get_loc(loc)

    else:
        raise ValueError("定位符必须为str或长度为2的tuple。")

    # ---------------根据传入对象类型获取页面对象和lxml元素对象---------------
    if isinstance(html_or_ele, SessionElement):  # SessionElement
        page = html_or_ele.page

        loc_str = loc[1]
        if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
            loc_str = f'.{loc[1]}'
            html_or_ele = html_or_ele.inner_ele

        # 若css以>开头，表示找元素的直接子元素，要用page以绝对路径才能找到
        elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>'):
            loc_str = f'{html_or_ele.css_path}{loc[1]}'
            if html_or_ele.page:
                html_or_ele = fromstring(html_or_ele.page.html)
            else:  # 接收html文本，无page的情况
                html_or_ele = fromstring(html_or_ele('xpath:/ancestor::*').html)

        else:
            html_or_ele = html_or_ele.inner_ele

        loc = loc[0], loc_str

    elif isinstance(html_or_ele, DrissionElement):  # DriverElement
        loc_str = loc[1]
        if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
            loc_str = f'.{loc[1]}'
        elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>'):
            loc_str = f'{html_or_ele.css_path}{loc[1]}'
        loc = loc[0], loc_str

        # 获取整个页面html再定位到当前元素，以实现查找上级元素
        page = html_or_ele.page
        xpath = html_or_ele.xpath
        html_or_ele = fromstring(html_or_ele.page.html)
        html_or_ele = html_or_ele.xpath(xpath)[0]

    elif isinstance(html_or_ele, BasePage):  # MixPage, DriverPage 或 SessionPage
        page = html_or_ele
        html_or_ele = fromstring(html_or_ele.html)

    elif isinstance(html_or_ele, str):  # 直接传入html文本
        page = None
        html_or_ele = fromstring(html_or_ele)

    elif isinstance(html_or_ele, BaseElement):  # ShadowRootElement
        page = html_or_ele.page
        html_or_ele = fromstring(html_or_ele.html)

    else:
        raise TypeError('html_or_ele参数只能是元素、页面对象或html文本。')

    # ---------------执行查找-----------------
    try:
        if loc[0] == 'xpath':  # 用lxml内置方法获取lxml的元素对象列表
            ele = html_or_ele.xpath(loc[1])
        else:  # 用css selector获取元素对象列表
            ele = html_or_ele.cssselect(loc[1])

        if not isinstance(ele, list):  # 结果不是列表，如数字
            return ele

        # 把lxml元素对象包装成SessionElement对象并按需要返回第一个或全部
        if single:
            ele = ele[0] if ele else None
            if isinstance(ele, HtmlElement):
                return SessionElement(ele, page)
            elif isinstance(ele, str):
                return ele
            else:
                return None

        else:  # 返回全部
            return [SessionElement(e, page) if isinstance(e, HtmlElement) else e for e in ele if e != '\n']

    except Exception as e:
        if 'Invalid expression' in str(e):
            raise SyntaxError(f'无效的xpath语句：{loc}')
        elif 'Expected selector' in str(e):
            raise SyntaxError(f'无效的css select语句：{loc}')

        raise e
