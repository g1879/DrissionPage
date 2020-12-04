# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   session_element.py
"""
import re
from typing import Union, List, Tuple
from urllib.parse import urlparse, urljoin, urlunparse

from cssselect import SelectorSyntaxError
from lxml.etree import tostring, XPathEvalError
from lxml.html import HtmlElement, fromstring

from .common import DrissionElement, str_to_loc, translate_loc, format_html


class SessionElement(DrissionElement):
    """session模式的元素对象，包装了一个lxml的Element对象，并封装了常用功能"""

    def __init__(self, ele: HtmlElement, page=None):
        super().__init__(ele, page)

    def __repr__(self):
        attrs = [f"{attr}='{self.attrs[attr]}'" for attr in self.attrs]
        return f'<SessionElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, loc_or_str: Union[Tuple[str, str], str], mode: str = 'single'):
        """实现查找元素的简化写法                                     \n
        例：ele2 = ele1('@id=ele_id')                               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param mode: 'single' 或 'all'，对应查找一个或全部
        :return: SessionElement对象
        """
        return self.ele(loc_or_str, mode)

    @property
    def html(self) -> str:
        """返回元素outerHTML文本"""
        # tostring()会把跟紧元素的文本节点也带上，因此要去掉
        html = format_html(tostring(self._inner_ele, method="html").decode())
        return html[:html.rfind('>') + 1]

    @property
    def inner_html(self) -> str:
        """返回元素innerHTML文本"""
        r = re.match(r'<.*?>(.*)</.*?>', self.html, flags=re.DOTALL)
        return '' if not r else r.group(1)

    @property
    def tag(self) -> str:
        """返回元素类型"""
        return self._inner_ele.tag

    @property
    def attrs(self) -> dict:
        """返回元素所有属性及值"""
        return {attr: self.attr(attr) for attr, val in self.inner_ele.items()}

    @property
    def text(self) -> str:
        """返回元素内所有文本"""
        return str(self._inner_ele.text_content())

    @property
    def link(self) -> str:
        """返回href或src绝对url"""
        return self.attr('href') or self.attr('src')

    @property
    def css_path(self) -> str:
        """返回css path路径"""
        return self._get_ele_path('css')

    @property
    def xpath(self) -> str:
        """返回xpath路径"""
        return self._get_ele_path('xpath')

    @property
    def parent(self):
        """返回父级元素"""
        return self.parents()

    @property
    def next(self):
        """返回后一个兄弟元素"""
        return self._get_brother(1, 'ele', 'next')

    @property
    def prev(self):
        """返回前一个兄弟元素"""
        return self._get_brother(1, 'ele', 'prev')

    def texts(self, text_node_only: bool = False) -> list:
        """返回元素内所有直接子节点的文本，包括元素和文本节点   \n
        :param text_node_only: 是否只返回文本节点
        :return: 文本列表
        """
        if text_node_only:
            return self.eles('xpath:/text()')
        else:
            texts = []

            for node in self.eles('xpath:/node()'):
                if isinstance(node, str):
                    text = node
                else:
                    text = node.text

                if text:
                    texts.append(text)

            return texts

    def parents(self, num: int = 1):
        """返回上面第num级父元素                                         \n
        :param num: 第几级父元素
        :return: SessionElement对象
        """
        return self.ele(f'xpath:..{"/.." * (num - 1)}')

    def nexts(self, num: int = 1, mode: str = 'ele'):
        """返回后面第num个兄弟元素或节点                                  \n
        :param num: 后面第几个兄弟元素或节点
        :param mode: 'ele', 'node' 或 'text'，匹配元素、节点、或文本节点
        :return: SessionElement对象
        """
        return self._get_brother(num, mode, 'next')

    def prevs(self, num: int = 1, mode: str = 'ele'):
        """返回前面第num个兄弟元素或节点                                  \n
        :param num: 前面第几个兄弟元素或节点
        :param mode: 'ele', 'node' 或 'text'，匹配元素、节点、或文本节点
        :return: SessionElement对象
        """
        return self._get_brother(num, mode, 'prev')

    def attr(self, attr: str) -> Union[str, None]:
        """返回属性值                           \n
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        # 获取href属性时返回绝对url
        if attr == 'href':
            link = self.inner_ele.get('href')

            # 若为链接为None、js或邮件，直接返回
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link

            # 其它情况直接返回绝对url
            else:
                return self._make_absolute(link)

        elif attr == 'src':
            return self._make_absolute(self.inner_ele.get('src'))

        elif attr in ['text', 'innerText']:
            return self.text

        elif attr == 'outerHTML':
            return self.html

        elif attr == 'innerHTML':
            return self.inner_html

        else:
            return self.inner_ele.get(attr)

    def ele(self, loc_or_str: Union[Tuple[str, str], str], mode: str = None):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个                                    \n
        示例：                                                                                           \n
        - 用loc元组查找：                                                                                 \n
            ele.ele((By.CLASS_NAME, 'ele_class')) - 返回第一个class为ele_class的子元素                     \n
        - 用查询字符串查找：                                                                               \n
            查找方式：属性、tag name和属性、文本、xpath、css selector、id、class                             \n
            @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串           \n
            ele.ele('.ele_class')                       - 返回第一个 class 为 ele_class 的子元素            \n
            ele.ele('.:ele_class')                      - 返回第一个 class 中含有 ele_class 的子元素         \n
            ele.ele('#ele_id')                          - 返回第一个 id 为 ele_id 的子元素                  \n
            ele.ele('#:ele_id')                         - 返回第一个 id 中含有 ele_id 的子元素               \n
            ele.ele('@class:ele_class')                 - 返回第一个class含有ele_class的子元素              \n
            ele.ele('@name=ele_name')                   - 返回第一个name等于ele_name的子元素                \n
            ele.ele('@placeholder')                     - 返回第一个带placeholder属性的子元素               \n
            ele.ele('tag:p')                            - 返回第一个<p>子元素                              \n
            ele.ele('tag:div@class:ele_class')          - 返回第一个class含有ele_class的div子元素           \n
            ele.ele('tag:div@class=ele_class')          - 返回第一个class等于ele_class的div子元素           \n
            ele.ele('tag:div@text():some_text')         - 返回第一个文本含有some_text的div子元素             \n
            ele.ele('tag:div@text()=some_text')         - 返回第一个文本等于some_text的div子元素             \n
            ele.ele('text:some_text')                   - 返回第一个文本含有some_text的子元素                \n
            ele.ele('some_text')                        - 返回第一个文本含有some_text的子元素（等价于上一行）  \n
            ele.ele('text=some_text')                   - 返回第一个文本等于some_text的子元素                \n
            ele.ele('xpath://div[@class="ele_class"]')  - 返回第一个符合xpath的子元素                        \n
            ele.ele('css:div.ele_class')                - 返回第一个符合css selector的子元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param mode: 'single' 或 'all‘，对应查找一个或全部
        :return: SessionElement对象
        """
        if isinstance(loc_or_str, (str, tuple)):
            if isinstance(loc_or_str, str):
                loc_or_str = str_to_loc(loc_or_str)
            else:
                if len(loc_or_str) != 2:
                    raise ValueError("Len of loc_or_str must be 2 when it's a tuple.")
                loc_or_str = translate_loc(loc_or_str)
        else:
            raise ValueError('Argument loc_or_str can only be tuple or str.')

        element = self
        loc_str = loc_or_str[1]

        if loc_or_str[0] == 'xpath' and loc_or_str[1].lstrip().startswith('/'):
            loc_str = f'.{loc_str}'

        # 若css以>开头，表示找元素的直接子元素，要用page以绝对路径才能找到
        if loc_or_str[0] == 'css selector' and loc_or_str[1].lstrip().startswith('>'):
            loc_str = f'{self.css_path}{loc_or_str[1]}'
            element = self.page

        loc_or_str = loc_or_str[0], loc_str

        return execute_session_find(element, loc_or_str, mode)

    def eles(self, loc_or_str: Union[Tuple[str, str], str]):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本                                              \n
        示例：                                                                                          \n
        - 用loc元组查找：                                                                                \n
            ele.eles((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的子元素                     \n
        - 用查询字符串查找：                                                                              \n
            查找方式：属性、tag name和属性、文本、xpath、css selector、id、class                             \n
            @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串           \n
            ele.eles('.ele_class')                       - 返回所有 class 为 ele_class 的子元素            \n
            ele.eles('.:ele_class')                      - 返回所有 class 中含有 ele_class 的子元素         \n
            ele.eles('#ele_id')                          - 返回所有 id 为 ele_id 的子元素                  \n
            ele.eles('#:ele_id')                         - 返回所有 id 中含有 ele_id 的子元素               \n
            ele.eles('@class:ele_class')                 - 返回所有class含有ele_class的子元素              \n
            ele.eles('@name=ele_name')                   - 返回所有name等于ele_name的子元素                \n
            ele.eles('@placeholder')                     - 返回所有带placeholder属性的子元素               \n
            ele.eles('tag:p')                            - 返回所有<p>子元素                              \n
            ele.eles('tag:div@class:ele_class')          - 返回所有class含有ele_class的div子元素           \n
            ele.eles('tag:div@class=ele_class')          - 返回所有class等于ele_class的div子元素           \n
            ele.eles('tag:div@text():some_text')         - 返回所有文本含有some_text的div子元素             \n
            ele.eles('tag:div@text()=some_text')         - 返回所有文本等于some_text的div子元素             \n
            ele.eles('text:some_text')                   - 返回所有文本含有some_text的子元素                \n
            ele.eles('some_text')                        - 返回所有文本含有some_text的子元素（等价于上一行）  \n
            ele.eles('text=some_text')                   - 返回所有文本等于some_text的子元素                \n
            ele.eles('xpath://div[@class="ele_class"]')  - 返回所有符合xpath的子元素                        \n
            ele.eles('css:div.ele_class')                - 返回所有符合css selector的子元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象组成的列表
        """
        return self.ele(loc_or_str, mode='all')

    # -----------------私有函数-------------------
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

    def _get_ele_path(self, mode) -> str:
        """获取css路径或xpath路径
        :param mode: 'css' 或 'xpath'
        :return: css路径或xpath路径
        """
        path_str = ''
        ele = self

        while ele:
            ele_id = ele.attr('id')

            if ele_id:
                return f'#{ele_id}{path_str}' if mode == 'css' else f'//{ele.tag}[@id="{ele_id}"]{path_str}'
            else:

                if mode == 'css':
                    brothers = len(ele.eles(f'xpath:./preceding-sibling::*'))
                    path_str = f'>:nth-child({brothers + 1}){path_str}'
                else:
                    brothers = len(ele.eles(f'xpath:./preceding-sibling::{ele.tag}'))
                    path_str = f'/{ele.tag}[{brothers + 1}]{path_str}' if brothers > 0 else f'/{ele.tag}{path_str}'

                ele = ele.parent

        return path_str[1:] if mode == 'css' else path_str

    def _get_brother(self, num: int = 1, mode: str = 'ele', direction: str = 'next'):
        """返回前面第num个兄弟元素或节点                                     \n
        :param num: 前面第几个兄弟元素或节点
        :param mode: 'ele', 'node' 或 'text'，匹配元素、节点、或文本节点
        :param direction: 'next' 或 'prev'，查找的方向
        :return: DriverElement对象或字符串
        """
        # 查找节点的类型
        if mode == 'ele':
            node_txt = '*'
        elif mode == 'node':
            node_txt = 'node()'
        elif mode == 'text':
            node_txt = 'text()'
        else:
            raise ValueError(f"Argument mode can only be 'node' ,'ele' or 'text', not '{mode}'.")

        # 查找节点的方向
        if direction == 'next':
            direction_txt = 'following'
        elif direction == 'prev':
            direction_txt = 'preceding'
        else:
            raise ValueError(f"Argument direction can only be 'next' or 'prev', not '{direction}'.")

        # 获取节点
        ele_or_node = self.ele(f'xpath:./{direction_txt}-sibling::{node_txt}[{num}]')

        # 跳过元素间的换行符
        while ele_or_node == '\n':
            num += 1
            ele_or_node = self.ele(f'xpath:./{direction_txt}-sibling::{node_txt}[{num}]')

        return ele_or_node


def execute_session_find(page_or_ele,
                         loc: Tuple[str, str],
                         mode: str = 'single', ) -> Union[SessionElement, List[SessionElement], str, None]:
    """执行session模式元素的查找                              \n
    页面查找元素及元素查找下级元素皆使用此方法                   \n
    :param page_or_ele: SessionPage对象或SessionElement对象
    :param loc: 元素定位元组
    :param mode: 'single' 或 'all'，对应获取第一个或全部
    :return: 返回SessionElement元素或列表
    """
    mode = mode or 'single'
    if mode not in ['single', 'all']:
        raise ValueError(f"Argument mode can only be 'single' or 'all', not '{mode}'.")

    # 根据传入对象类型获取页面对象和lxml元素对象
    if isinstance(page_or_ele, SessionElement):
        page = page_or_ele.page
        page_or_ele = page_or_ele.inner_ele
    else:  # 传入的是SessionPage对象
        page = page_or_ele
        page_or_ele = fromstring(page_or_ele.html)

    try:
        # 用lxml内置方法获取lxml的元素对象列表
        if loc[0] == 'xpath':
            ele = page_or_ele.xpath(loc[1])

        # 用css selector获取元素对象列表
        else:
            ele = page_or_ele.cssselect(loc[1])

        # 把lxml元素对象包装成SessionElement对象并按需要返回第一个或全部
        if mode == 'single':
            ele = ele[0] if ele else None

            if isinstance(ele, HtmlElement):
                return SessionElement(ele, page)
            elif isinstance(ele, str):
                return ele
            else:
                return None

        elif mode == 'all':
            return [SessionElement(e, page) if isinstance(e, HtmlElement) else e for e in ele if e != '\n']

    except XPathEvalError:
        raise SyntaxError(f'Invalid xpath syntax. {loc}')

    except SelectorSyntaxError:
        raise SyntaxError(f'Invalid css selector syntax. {loc}')
