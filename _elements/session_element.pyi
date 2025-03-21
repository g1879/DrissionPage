# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union, List, Tuple, Optional

from lxml.html import HtmlElement

from .._base.base import DrissionElement, BaseElement
from .._elements.chromium_element import ChromiumElement
from .._functions.elements import SessionElementsList
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.session_page import SessionPage


class SessionElement(DrissionElement):
    """静态元素对象"""

    def __init__(self, ele: HtmlElement, owner: Union[SessionPage, None] = None):
        self._inner_ele: HtmlElement = ...
        self.owner: SessionPage = ...
        self.page: SessionPage = ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str],
                 index: int = 1,
                 timeout: float = None) -> SessionElement:
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 不起实际作用
        :return: SessionElement对象或属性、文本
        """
        ...

    def __repr__(self) -> str: ...

    def __eq__(self, other: SessionElement) -> bool: ...

    @property
    def inner_ele(self) -> HtmlElement: ...

    @property
    def tag(self) -> str:
        """返回元素类型"""
        ...

    @property
    def html(self) -> str:
        """返回outerHTML文本"""
        ...

    @property
    def inner_html(self) -> str:
        """返回元素innerHTML文本"""
        ...

    @property
    def attrs(self) -> dict:
        """返回元素所有属性及值"""
        ...

    @property
    def text(self) -> str:
        """返回元素内文本"""
        ...

    @property
    def raw_text(self) -> str:
        """返回未格式化处理的元素内文本"""
        ...

    def parent(self,
               level_or_loc: Union[tuple, str, int] = 1,
               index: int = 1,
               timeout: float = None) -> SessionElement:
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果
        :param timeout: 此参数不起实际作用
        :return: 上级元素对象
        """
        ...

    def child(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[SessionElement, str]:
        """返回当前元素的一个符合条件的直接子元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本
        """
        ...

    def prev(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[SessionElement, str]:
        """返回当前元素前面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素
        """
        ...

    def next(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[SessionElement, str]:
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素
        """
        ...

    def before(self,
               locator: Union[Tuple[str, str], str, int] = '',
               index: int = 1,
               timeout: float = None,
               ele_only: bool = True) -> Union[SessionElement, str]:
        """返回文档中当前元素前面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        ...

    def after(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[SessionElement, str]:
        """返回文档中此当前元素后面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        ...

    def children(self,
                 locator: Union[Tuple[str, str], str] = '',
                 timeout: float = None,
                 ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]:
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        ...

    def prevs(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]:
        """返回当前元素前面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点文本组成的列表
        """
        ...

    def nexts(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]:
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点文本组成的列表
        """
        ...

    def befores(self,
                locator: Union[Tuple[str, str], str] = '',
                timeout: float = None,
                ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]:
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        ...

    def afters(self,
               locator: Union[Tuple[str, str], str] = '',
               timeout: float = None,
               ele_only: bool = True) -> Union[SessionElementsList, List[Union[SessionElement, str]]]:
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 此参数不起实际作用
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        ...

    def attr(self, name: str) -> Optional[str]:
        """返回attribute属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        ...

    def ele(self,
            locator: Union[Tuple[str, str], str],
            index: int = 1,
            timeout: float = None) -> SessionElement:
        """返回当前元素下级符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 不起实际作用
        :return: SessionElement对象或属性、文本
        """
        ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> SessionElementsList:
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用
        :return: SessionElement对象或属性、文本组成的列表
        """
        ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str] = None,
              index: int = 1) -> SessionElement:
        """返回当前元素下级符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :return: SessionElement对象或属性、文本
        """
        ...

    def s_eles(self, locator: Union[Tuple[str, str], str]) -> SessionElementsList:
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本组成的列表
        """
        ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str],
                       timeout: float,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = None) -> Union[SessionElement, SessionElementsList]:
        """返回当前元素下级符合条件的子元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和父类对应
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: MixTab用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: SessionElement对象
        """
        ...

    def _get_ele_path(self, xpath: bool = True) -> str:
        """获取css路径或xpath路径
        :param xpath: 用xpath还是css
        :return: css路径或xpath路径
        """
        ...


def make_session_ele(html_or_ele: Union[str, SessionElement, SessionPage, ChromiumElement, BaseElement, ChromiumFrame,
ChromiumBase],
                     loc: Union[str, Tuple[str, str]] = None,
                     index: Optional[int] = 1,
                     method: Optional[str] = None) -> Union[SessionElement, SessionElementsList, str, float]:
    """从接收到的对象或html文本中查找元素，返回SessionElement对象
    如要直接从html生成SessionElement而不在下级查找，loc输入None即可
    :param html_or_ele: html文本、BaseParser对象
    :param loc: 定位元组或字符串，为None时不在下级查找，返回根元素
    :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个，None获取所有
    :param method: 调用此方法的方法
    :return: 返回SessionElement元素或列表，或属性文本
    """
    ...
