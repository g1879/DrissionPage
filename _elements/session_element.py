# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from html import unescape
from re import match, sub, DOTALL, search

from lxml.etree import tostring
from lxml.html import HtmlElement, fromstring

from .none_element import NoneElement
from .._base.base import DrissionElement, BasePage, BaseElement
from .._functions.elements import SessionElementsList
from .._functions.locator import get_loc
from .._functions.settings import Settings as _S
from .._functions.web import get_ele_txt, make_absolute_link
from ..errors import LocatorError


class SessionElement(DrissionElement):

    def __init__(self, ele, owner=None):
        """初始化对象
        :param ele: 被包装的HtmlElement元素
        :param owner: 元素所在页面对象，如果是从 html 文本生成的元素，则为 None
        """
        super().__init__(owner)
        self._inner_ele = ele
        self._type = 'SessionElement'

    def __repr__(self):
        attrs = [f"{k}='{v}'" for k, v in self.attrs.items()]
        return f'<SessionElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, locator, index=1, timeout=None):
        return self.ele(locator, index=index)

    def __eq__(self, other):
        return self.xpath == getattr(other, 'xpath', None)

    @property
    def inner_ele(self):
        return self._inner_ele

    @property
    def tag(self):
        return self._inner_ele.tag

    @property
    def html(self):
        html = tostring(self._inner_ele, method="html").decode()
        return unescape(html[:html.rfind('>') + 1])  # tostring()会把跟紧元素的文本节点也带上，因此要去掉

    @property
    def inner_html(self):
        r = match(r'<.*?>(.*)</.*?>', self.html, flags=DOTALL)
        return '' if not r else r.group(1)

    @property
    def attrs(self):
        r = {}
        for attr, val in self.inner_ele.items():
            r[attr] = val if attr.lower in ('href', 'src') else self.attr(attr)
        return r

    @property
    def text(self):
        return get_ele_txt(self)

    @property
    def raw_text(self):
        return str(self._inner_ele.text_content())

    def parent(self, level_or_loc=1, index=1, timeout: float = None):
        return super().parent(level_or_loc, index)

    def child(self, locator='', index=1, timeout=None, ele_only=True):
        return super().child(locator, index, timeout, ele_only=ele_only)

    def prev(self, locator='', index=1, timeout=None, ele_only=True):
        return super().prev(locator, index, timeout, ele_only=ele_only)

    def next(self, locator='', index=1, timeout=None, ele_only=True):
        return super().next(locator, index, timeout, ele_only=ele_only)

    def before(self, locator='', index=1, timeout=None, ele_only=True):
        return super().before(locator, index, timeout, ele_only=ele_only)

    def after(self, locator='', index=1, timeout=None, ele_only=True):
        return super().after(locator, index, timeout, ele_only=ele_only)

    def children(self, locator='', timeout=0, ele_only=True):
        return SessionElementsList(self.owner, super().children(locator, timeout, ele_only=ele_only))

    def prevs(self, locator='', timeout=None, ele_only=True):
        return SessionElementsList(self.owner, super().prevs(locator, timeout, ele_only=ele_only))

    def nexts(self, locator='', timeout=None, ele_only=True):
        return SessionElementsList(self.owner, super().nexts(locator, timeout, ele_only=ele_only))

    def befores(self, locator='', timeout=None, ele_only=True):
        return SessionElementsList(self.owner, super().befores(locator, timeout, ele_only=ele_only))

    def afters(self, locator='', timeout=None, ele_only=True):
        return SessionElementsList(self.owner, super().afters(locator, timeout, ele_only=ele_only))

    def attr(self, name):
        if name == 'href':
            link = self.inner_ele.get('href')
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link
            else:
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
            return self.inner_ele.get(name.lower())

    def ele(self, locator, index=1, timeout=None):
        return self._ele(locator, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        return self._ele(locator, index=None)

    def s_ele(self, locator=None, index=1):
        return self._ele(locator, index=index, method='s_ele()')

    def s_eles(self, locator):
        return self._ele(locator, index=None)

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        return make_session_ele(self, locator, index=index)

    def _get_ele_path(self, xpath=True):
        if xpath:
            return self._inner_ele.getroottree().getpath(self._inner_ele)

        path_str = ''
        ele = self
        while ele:
            id_ = ele.attr('id')
            if id_:
                path_str = f'>{ele.tag}#{id_}{path_str}'
            else:
                path_str = f'>{ele.tag}:nth-child({len(ele.eles("xpath:./preceding-sibling::*")) + 1}){path_str}'
            ele = ele.parent()

        return path_str[1:]


def make_session_ele(html_or_ele, loc=None, index=1, method=None):
    # ---------------处理定位符---------------
    if not loc:
        if isinstance(html_or_ele, SessionElement):
            return html_or_ele
        loc = ('xpath', '.')

    elif isinstance(loc, (str, tuple)):
        loc = get_loc(loc)

    else:
        raise LocatorError(ALLOW_VAL=_S._lang.LOC_FORMAT, CURR_VAL=loc)

    # ---------------根据传入对象类型获取页面对象和lxml元素对象---------------
    the_type = getattr(html_or_ele, '_type', None)
    # 直接传入html文本
    if isinstance(html_or_ele, str):
        page = None
        html_or_ele = fromstring(html_or_ele)

    # SessionElement
    elif the_type == 'SessionElement':
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

    elif the_type == 'ChromiumElement':
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
            doc = html_or_ele._run_js('return this.ownerDocument;')
            html_or_ele._doc_id = doc['objectId'] if doc else False

        if html_or_ele._doc_id:
            html = html_or_ele.owner._run_cdp('DOM.getOuterHTML', objectId=html_or_ele._doc_id)['outerHTML']
        else:
            html = html_or_ele.owner.html
        html_or_ele = fromstring(html)
        html_or_ele = html_or_ele.xpath(xpath)[0]

    elif the_type == 'ChromiumFrame':
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
        raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'html_or_ele',
                                       ALLOW_TYPE=_S._lang.HTML_ELE_TYPE, CURR_VAL=html_or_ele))

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
            r = SessionElementsList(owner=page)
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
            raise LocatorError(_S._lang.INVALID_XPATH_, loc)
        elif 'Expected selector' in str(e):
            raise LocatorError(_S._lang.INVALID_CSS_, loc)

        raise e
