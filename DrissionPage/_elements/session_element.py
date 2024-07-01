# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from html import unescape
from re import match, sub, DOTALL, search

from lxml.etree import tostring
from lxml.html import HtmlElement, fromstring

from .none_element import NoneElement
from .._base.base import DrissionElement, BasePage, BaseElement
from .._functions.elements import SessionElementsList
from .._functions.locator import get_loc
from .._functions.web import get_ele_txt, make_absolute_link


class SessionElement(DrissionElement):
    """session模式的元素对象，包装了一个lxml的Element对象，并封装了常用功能"""

    def __init__(self, ele, owner=None):
        """初始化对象
        :param ele: 被包装的HtmlElement元素
        :param owner: 元素所在页面对象，如果是从 html 文本生成的元素，则为 None
        """
        super().__init__(owner)
        self._inner_ele = ele
        self._type = 'SessionElement'

    @property
    def inner_ele(self):
        return self._inner_ele

    def __repr__(self):
        attrs = [f"{k}='{v}'" for k, v in self.attrs.items()]
        return f'<SessionElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, locator, index=1, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 不起实际作用
        :return: SessionElement对象或属性、文本
        """
        return self.ele(locator, index=index)

    def __eq__(self, other):
        return self.xpath == getattr(other, 'xpath', None)

    @property
    def tag(self):
        """返回元素类型"""
        return self._inner_ele.tag

    @property
    def html(self):
        """返回outerHTML文本"""
        html = tostring(self._inner_ele, method="html").decode()
        return unescape(html[:html.rfind('>') + 1])  # tostring()会把跟紧元素的文本节点也带上，因此要去掉

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        r = match(r'<.*?>(.*)</.*?>', self.html, flags=DOTALL)
        return '' if not r else r.group(1)

    @property
    def attrs(self):
        """返回元素所有属性及值"""
        return {attr: self.attr(attr) for attr, val in self.inner_ele.items()}

    @property
    def text(self):
        """返回元素内所有文本"""
        return get_ele_txt(self)

    @property
    def raw_text(self):
        """返回未格式化处理的元素内文本"""
        return str(self._inner_ele.text_content())

    def parent(self, level_or_loc=1, index=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果
        :return: 上级元素对象
        """
        return super().parent(level_or_loc, index)

    def child(self, locator='', index=1, timeout=None, ele_only=True):
        """返回当前元素的一个符合条件的直接子元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本
        """
        return super().child(locator, index, timeout, ele_only=ele_only)

    def prev(self, locator='', index=1, timeout=None, ele_only=True):
        """返回当前元素前面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素
        """
        return super().prev(locator, index, timeout, ele_only=ele_only)

    def next(self, locator='', index=1, timeout=None, ele_only=True):
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素
        """
        return super().next(locator, index, timeout, ele_only=ele_only)

    def before(self, locator='', index=1, timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        return super().before(locator, index, timeout, ele_only=ele_only)

    def after(self, locator='', index=1, timeout=None, ele_only=True):
        """返回文档中此当前元素后面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        return super().after(locator, index, timeout, ele_only=ele_only)

    def children(self, locator='', timeout=0, ele_only=True):
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        return SessionElementsList(self.owner, super().children(locator, timeout, ele_only=ele_only))

    def prevs(self, locator='', timeout=None, ele_only=True):
        """返回当前元素前面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点文本组成的列表
        """
        return SessionElementsList(self.owner, super().prevs(locator, timeout, ele_only=ele_only))

    def nexts(self, locator='', timeout=None, ele_only=True):
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点文本组成的列表
        """
        return SessionElementsList(self.owner, super().nexts(locator, timeout, ele_only=ele_only))

    def befores(self, locator='', timeout=None, ele_only=True):
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        return SessionElementsList(self.owner, super().befores(locator, timeout, ele_only=ele_only))

    def afters(self, locator='', timeout=None, ele_only=True):
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        return SessionElementsList(self.owner, super().afters(locator, timeout, ele_only=ele_only))

    def attr(self, name):
        """返回attribute属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        # 获取href属性时返回绝对url
        if name == 'href':
            link = self.inner_ele.get('href')
            # 若为链接为None、js或邮件，直接返回
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link
            else:  # 其它情况直接返回绝对url
                return make_absolute_link(link, self.owner.url) if self.owner else link

        elif name == 'src':
            return make_absolute_link(self.inner_ele.get('src'),
                                      self.owner.url) if self.owner else self.inner_ele.get('src')

        elif name == 'text':
            return self.text

        elif name == 'innerText':
            return self.raw_text

        elif name in ('html', 'outerHTML'):
            return self.html

        elif name == 'innerHTML':
            return self.inner_html

        else:
            return self.inner_ele.get(name)

    def ele(self, locator, index=1, timeout=None):
        """返回当前元素下级符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 不起实际作用
        :return: SessionElement对象或属性、文本
        """
        return self._ele(locator, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(locator, index=None)

    def s_ele(self, locator=None, index=1):
        """返回当前元素下级符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :return: SessionElement对象或属性、文本
        """
        return self._ele(locator, index=index, method='s_ele()')

    def s_eles(self, locator):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(locator, index=None)

    def _find_elements(self, locator, timeout=None, index=1, relative=False, raise_err=None):
        """返回当前元素下级符合条件的子元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和父类对应
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: SessionElement对象
        """
        return make_session_ele(self, locator, index=index)

    def _get_ele_path(self, mode):
        """获取css路径或xpath路径
        :param mode: 'css' 或 'xpath'
        :return: css路径或xpath路径
        """
        path_str = ''
        ele = self

        while ele:
            if mode == 'css':
                brothers = len(ele.eles(f'xpath:./preceding-sibling::*'))
                path_str = f'>{ele.tag}:nth-child({brothers + 1}){path_str}'
            else:
                brothers = len(ele.eles(f'xpath:./preceding-sibling::{ele.tag}'))
                path_str = f'/{ele.tag}[{brothers + 1}]{path_str}' if brothers > 0 else f'/{ele.tag}{path_str}'

            ele = ele.parent()

        return f'{path_str[1:]}' if mode == 'css' else path_str


def make_session_ele(html_or_ele, loc=None, index=1, method=None):
    """从接收到的对象或html文本中查找元素，返回SessionElement对象
    如要直接从html生成SessionElement而不在下级查找，loc输入None即可
    :param html_or_ele: html文本、BaseParser对象
    :param loc: 定位元组或字符串，为None时不在下级查找，返回根元素
    :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个，None获取所有
    :param method: 调用此方法的方法
    :return: 返回SessionElement元素或列表，或属性文本
    """
    # ---------------处理定位符---------------
    if not loc:
        if isinstance(html_or_ele, SessionElement):
            return html_or_ele
        loc = ('xpath', '.')

    elif isinstance(loc, (str, tuple)):
        loc = get_loc(loc)

    else:
        raise ValueError("定位符必须为str或长度为2的tuple。")

    # ---------------根据传入对象类型获取页面对象和lxml元素对象---------------
    # 直接传入html文本
    if isinstance(html_or_ele, str):
        page = None
        html_or_ele = fromstring(html_or_ele)

    # SessionElement
    elif html_or_ele._type == 'SessionElement':
        page = html_or_ele.owner

        loc_str = loc[1]
        if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
            loc_str = f'.{loc[1]}'
            html_or_ele = html_or_ele.inner_ele

        # 若css以>开头，表示找元素的直接子元素，要用page以绝对路径才能找到
        elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>'):
            loc_str = f'{html_or_ele.css_path}{loc[1]}'
            if html_or_ele.owner:
                html_or_ele = fromstring(html_or_ele.owner.html)
            else:  # 接收html文本，无page的情况
                html_or_ele = fromstring(html_or_ele('xpath:/ancestor::*').html)

        else:
            html_or_ele = html_or_ele.inner_ele

        loc = loc[0], loc_str

    elif html_or_ele._type == 'ChromiumElement':
        loc_str = loc[1]
        if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
            loc_str = f'.{loc[1]}'
        elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>'):
            loc_str = f'{html_or_ele.css_path}{loc[1]}'
        loc = loc[0], loc_str

        # 获取整个页面html再定位到当前元素，以实现查找上级元素
        page = html_or_ele.owner
        xpath = html_or_ele.xpath
        # ChromiumElement，兼容传入的元素在iframe内的情况
        if html_or_ele._doc_id is None:
            doc = html_or_ele.run_js('return this.ownerDocument;')
            html_or_ele._doc_id = doc['objectId'] if doc else False

        if html_or_ele._doc_id:
            html = html_or_ele.owner.run_cdp('DOM.getOuterHTML', objectId=html_or_ele._doc_id)['outerHTML']
        else:
            html = html_or_ele.owner.html
        html_or_ele = fromstring(html)
        html_or_ele = html_or_ele.xpath(xpath)[0]

    elif html_or_ele._type == 'ChromiumFrame':
        page = html_or_ele
        html_or_ele = fromstring(html_or_ele.inner_html)

    # 各种页面对象
    elif isinstance(html_or_ele, BasePage):
        page = html_or_ele
        html = html_or_ele.html
        if html.startswith('<?xml '):
            html = sub(r'^<\?xml.*?>', '', html)
        html_or_ele = fromstring(html)

    # ShadowRoot
    elif isinstance(html_or_ele, BaseElement):
        page = html_or_ele.owner
        html = html_or_ele.html
        r = search(r'^<shadow_root>[ \n]*?<html>[ \n]*?(.*?)[ \n]*?</html>[ \n]*?</shadow_root>$', html)
        if r:
            html = r.group(1)
        html_or_ele = fromstring(html)

    else:
        raise TypeError('html_or_ele参数只能是元素、页面对象或html文本。')

    # ---------------执行查找-----------------
    try:
        if loc[0] == 'xpath':  # 用lxml内置方法获取lxml的元素对象列表
            eles = html_or_ele.xpath(loc[1])
        else:  # 用css selector获取元素对象列表
            eles = html_or_ele.cssselect(loc[1])

        if not isinstance(eles, list):  # 结果不是列表，如数字
            return eles

        # 把lxml元素对象包装成SessionElement对象并按需要返回一个或全部
        if index is None:
            r = SessionElementsList(page=page)
            for e in eles:
                if e != '\n':
                    r.append(SessionElement(e, page) if isinstance(e, HtmlElement) else e)
            return r

        else:
            eles_count = len(eles)
            if eles_count == 0 or abs(index) > eles_count:
                return NoneElement(page, method=method, args={'locator': loc, 'index': index})
            if index < 0:
                index = eles_count + index + 1

            ele = eles[index - 1]
            if isinstance(ele, HtmlElement):
                return SessionElement(ele, page)
            elif isinstance(ele, str):
                return ele
            else:
                return NoneElement(page, method=method, args={'locator': loc, 'index': index})

    except Exception as e:
        if 'Invalid expression' in str(e):
            raise SyntaxError(f'无效的xpath语句：{loc}')
        elif 'Expected selector' in str(e):
            raise SyntaxError(f'无效的css select语句：{loc}')

        raise e
