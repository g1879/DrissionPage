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
        """返回元素所有属性及值"""
        attrs = dict()
        for attr in self.inner_ele.attrs:
            attrs[attr] = self.attr(attr)
        return attrs

    @property
    def text(self) -> str:
        """返回元素内所有文本"""
        return unescape(self._inner_ele.text).replace('\xa0', ' ')

    def texts(self, text_node_only: bool = False) -> List[str]:
        nodes = self.eles('xpath:./*/node()')
        if text_node_only:
            return [x for x in nodes if isinstance(x, str)]
        else:
            return [x if isinstance(x, str) else x.text for x in nodes]

    @property
    def html(self) -> str:
        """返回元素innerHTML文本"""
        html = unescape(self._inner_ele.html).replace('\xa0', ' ')
        r = re.match(r'<.*?>(.*)</.*?>', html, flags=re.DOTALL)
        return None if not r else r.group(1)

    @property
    def tag(self) -> str:
        """返回元素类型"""
        return self._inner_ele.tag

    @property
    def css_path(self) -> str:
        """返回css path路径"""
        return self._get_ele_path('css')

    @property
    def xpath(self) -> str:
        """返回xpath路径"""
        return self._get_ele_path('xpath')

    def _get_ele_path(self, mode):
        """获取css路径或xpath路径"""
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

    @property
    def parent(self):
        """返回父级元素"""
        return self.parents()

    @property
    def next(self):
        """返回后一个兄弟元素"""
        return self.nexts()

    @property
    def prev(self):
        """返回前一个兄弟元素"""
        return self.prevs()

    def parents(self, num: int = 1):
        """返回上面第num级父元素                                                         \n
        requests_html的Element打包了lxml的元素对象，从lxml元素对象读取上下级关系后再重新打包  \n
        :param num: 第几级父元素
        :return: SessionElement对象
        """
        return self.ele(f'xpath:..{"/.." * (num - 1)}')

    def nexts(self, num: int = 1):
        """返回后面第num个兄弟元素      \n
        :param num: 后面第几个兄弟元素
        :return: SessionElement对象
        """
        return self.ele(f'xpath:./following-sibling::*[{num}]')

    def prevs(self, num: int = 1):
        """返回前面第num个兄弟元素        \n
        :param num: 前面第几个兄弟元素
        :return: SessionElement对象
        """
        return self.ele(f'xpath:./preceding-sibling::*[{num}]')

    def ele(self, loc_or_str: Union[tuple, str], mode: str = None, show_errmsg: bool = False):
        """返回当前元素下级符合条件的子元素，默认返回第一个                                                 \n
        示例：                                                                                           \n
        - 用loc元组查找：                                                                                 \n
            ele.ele((By.CLASS_NAME, 'ele_class')) - 返回第一个class为ele_class的子元素                       \n
        - 用查询字符串查找：                                                                               \n
            查找方式：属性、tag name和属性、文本、xpath、css selector                                        \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                          \n
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
        :param show_errmsg: 出现异常时是否打印信息
        :return: SessionElement对象
        """
        if isinstance(loc_or_str, str):
            loc_or_str = get_loc_from_str(loc_or_str)
        elif isinstance(loc_or_str, tuple) and len(loc_or_str) == 2:
            loc_or_str = translate_loc_to_xpath(loc_or_str)
        else:
            raise TypeError('Type of loc_or_str can only be tuple or str.')

        loc_str = None
        if loc_or_str[0] == 'xpath':
            loc_str = loc_or_str[1] if loc_or_str[1].startswith(('.', '/')) else f'.//{loc_or_str[1]}'
            loc_str = loc_str if loc_str.startswith('.') else f'.{loc_str}'
        elif loc_or_str[0] == 'css selector':
            # Element的html是包含自己的，要如下处理，使其只检索下级的
            loc_str = loc_or_str[1] if loc_or_str[1][0] in '>, ' else f' {loc_or_str[1]}'
            loc_str = f':root>{self.tag}{loc_str}'
        loc_or_str = loc_or_str[0], loc_str

        return execute_session_find(self.inner_ele, loc_or_str, mode, show_errmsg)
        # return execute_session_find(self, loc_or_str, mode, show_errmsg)

    def eles(self, loc_or_str: Union[tuple, str], show_errmsg: bool = False):
        """返回当前元素下级所有符合条件的子元素                                                           \n
        示例：                                                                                          \n
        - 用loc元组查找：                                                                                \n
            ele.eles((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的子元素                     \n
        - 用查询字符串查找：                                                                              \n
            查找方式：属性、tag name和属性、文本、xpath、css selector                                       \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                         \n
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
        :param show_errmsg: 出现异常时是否打印信息
        :return: SessionElement对象组成的列表
        """
        if not isinstance(loc_or_str, tuple) and not isinstance(loc_or_str, str):
            raise TypeError('Type of loc_or_str can only be tuple or str.')
        return self.ele(loc_or_str, mode='all', show_errmsg=show_errmsg)

    def attr(self, attr: str) -> Union[str, None]:
        """返回属性值                           \n
        :param attr: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        try:
            if attr == 'href':
                # 如直接获取attr只能获取相对地址
                link = self._inner_ele.attrs['href']
                if link.lower().startswith(('javascript:', 'mailto:')):
                    return link
                elif link.startswith('#'):
                    if '#' in self.inner_ele.url:
                        return re.sub(r'#.*', link, self.inner_ele.url)
                    else:
                        return f'{self.inner_ele.url}{link}'
                elif link.startswith('?'):  # 避免当相对URL以?开头时requests-html丢失参数的bug
                    if '?' in self.inner_ele.url:
                        return re.sub(r'\?.*', link, self.inner_ele.url)
                    else:
                        return f'{self.inner_ele.url}{link}'
                else:
                    for link in self._inner_ele.absolute_links:
                        return link
            elif attr == 'src':
                return self._inner_ele._make_absolute(self._inner_ele.attrs['src'])
            elif attr == 'class':
                return ' '.join(self._inner_ele.attrs['class'])
            elif attr == 'text':
                return self.text
            elif attr == 'outerHTML':
                return self.inner_ele.html
            elif attr == 'innerHTML':
                return self.html
            else:
                return self._inner_ele.attrs[attr]
        except:
            return None


def execute_session_find(page_or_ele: BaseParser,
                         # def execute_session_find(page_or_ele,
                         loc: tuple,
                         mode: str = 'single',
                         show_errmsg: bool = False) -> Union[SessionElement, List[SessionElement]]:
    """执行session模式元素的查找                           \n
    页面查找元素及元素查找下级元素皆使用此方法                \n
    :param page_or_ele: request_html的页面或元素对象
    :param loc: 元素定位元组
    :param mode: 'single' 或 'all'，对应获取第一个或全部
    :param show_errmsg: 出现异常时是否显示错误信息
    :return: 返回SessionElement元素或列表
    """
    mode = mode or 'single'
    if mode not in ['single', 'all']:
        raise ValueError("Argument mode can only be 'single' or 'all'.")
    loc_by, loc_str = loc
    try:
        ele = None
        if loc_by == 'xpath':
            if 'PyQuery' in str(type(page_or_ele.element)):
                # 从页面查找。
                ele = page_or_ele.xpath(loc_str)
            elif 'HtmlElement' in str(type(page_or_ele.element)):
                # 从元素查找。这样区分是为了能找到上级元素
                try:
                    elements = page_or_ele.element.xpath(loc_str)
                    ele = [Element(element=e, url=page_or_ele.url) for e in elements]
                except AttributeError:
                    ele = page_or_ele.xpath(loc_str)
        else:  # 用css selector获取
            ele = page_or_ele.find(loc_str)

        if mode == 'single':
            ele = ele[0] if ele else None
            return SessionElement(ele) if isinstance(ele, Element) else ele
        elif mode == 'all':
            return [SessionElement(e) if isinstance(e, Element) else e for e in ele]
    except:
        if show_errmsg:
            print('Element(s) not found.', loc)
            raise
        return [] if mode == 'all' else None
