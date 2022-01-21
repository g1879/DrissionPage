# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   shadow_root_element.py
"""
from time import perf_counter
from typing import Union, Any, Tuple, List

from selenium.webdriver.remote.webelement import WebElement

from .base import BaseElement
from .common import get_loc
from .driver_element import make_driver_ele, DriverElement
from .session_element import make_session_ele, SessionElement


class ShadowRootElement(BaseElement):
    """ShadowRootElement是用于处理ShadowRoot的类，使用方法和DriverElement基本一致"""

    def __init__(self, inner_ele: WebElement, parent_ele: DriverElement):
        super().__init__(inner_ele, parent_ele.page)
        self.parent_ele = parent_ele

    def __repr__(self) -> str:
        return f'<ShadowRootElement in {self.parent_ele} >'

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = None) -> Union[DriverElement, str, None]:
        """在内部查找元素                                            \n
        例：ele2 = ele1('@id=ele_id')                               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: DriverElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    @property
    def tag(self) -> str:
        """元素标签名"""
        return 'shadow-root'

    @property
    def html(self) -> str:
        return f'<shadow_root>{self.inner_html}</shadow_root>'

    @property
    def inner_html(self) -> str:
        """返回内部的html文本"""
        shadow_root = WebElement(self.page.driver, self.inner_ele._id)
        return shadow_root.get_attribute('innerHTML')

    def parent(self, level_or_loc: Union[str, int] = 1) -> DriverElement:
        """返回上面某一级父元素，可指定层数或用查询语法定位              \n
        :param level_or_loc: 第几级父元素，或定位符
        :return: DriverElement对象
        """
        if isinstance(level_or_loc, int):
            loc = f'xpath:./ancestor-or-self::*[{level_or_loc}]'

        elif isinstance(level_or_loc, (tuple, str)):
            loc = get_loc(level_or_loc, True)

            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')

            loc = f'xpath:./ancestor-or-self::{loc[1].lstrip(". / ")}'

        else:
            raise TypeError('level_or_loc参数只能是tuple、int或str。')

        return self.parent_ele.ele(loc, timeout=0)

    def next(self,
             index: int = 1,
             filter_loc: Union[tuple, str] = '') -> Union[DriverElement, str, None]:
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param index: 第几个查询结果元素
        :param filter_loc: 用于筛选元素的查询语法
        :return: DriverElement对象
        """
        nodes = self.nexts(filter_loc=filter_loc)
        return nodes[index - 1] if nodes else None

    def before(self,
               index: int = 1,
               filter_loc: Union[tuple, str] = '') -> Union[DriverElement, str, None]:
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param index: 前面第几个查询结果元素
        :param filter_loc: 用于筛选元素的查询语法
        :return: 本元素前面的某个元素或节点
        """
        nodes = self.befores(filter_loc=filter_loc)
        return nodes[index - 1] if nodes else None

    def after(self, index: int = 1,
              filter_loc: Union[tuple, str] = '') -> Union[DriverElement, str, None]:
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个        \n
        :param index: 后面第几个查询结果元素
        :param filter_loc: 用于筛选元素的查询语法
        :return: 本元素后面的某个元素或节点
        """
        nodes = self.afters(filter_loc=filter_loc)
        return nodes[index - 1] if nodes else None

    def nexts(self, filter_loc: Union[tuple, str] = '') -> List[Union[DriverElement, str]]:
        """返回后面所有兄弟元素或节点组成的列表        \n
        :param filter_loc: 用于筛选元素的查询语法
        :return: DriverElement对象组成的列表
        """
        loc = get_loc(filter_loc, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./{loc}'
        return self.parent_ele.eles(xpath, timeout=0.1)

    def befores(self, filter_loc: Union[tuple, str] = '') -> List[Union[DriverElement, str]]:
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :return: 本元素前面的元素或节点组成的列表
        """
        loc = get_loc(filter_loc, True)
        if loc[0] == 'css selector':
            raise ValueError('此css selector语法不受支持，请换成xpath。')

        loc = loc[1].lstrip('./')
        xpath = f'xpath:./preceding::{loc}'
        return self.parent_ele.eles(xpath, timeout=0.1)

    def afters(self, filter_loc: Union[tuple, str] = '') -> List[Union[DriverElement, str]]:
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选        \n
        :param filter_loc: 用于筛选元素的查询语法
        :return: 本元素后面的元素或节点组成的列表
        """
        eles1 = self.nexts(filter_loc)
        loc = get_loc(filter_loc, True)[1].lstrip('./')
        xpath = f'xpath:./following::{loc}'
        return eles1 + self.parent_ele.eles(xpath, timeout=0.1)

    def ele(self,
            loc_or_str: Union[Tuple[str, str], str],
            timeout: float = None) -> Union[DriverElement, str, None]:
        """返回当前元素下级符合条件的第一个元素，默认返回                                   \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: DriverElement对象或属性、文本
        """
        return self._ele(loc_or_str, timeout)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[DriverElement, str]]:
        """返回当前元素下级所有符合条件的子元素                                              \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: DriverElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_ele=None) -> Union[SessionElement, str, None]:
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高                 \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_ele)

    def s_eles(self, loc_or_ele) -> List[Union[SessionElement, str]]:
        """查找所有符合条件的元素以SessionElement列表形式返回，处理复杂页面时效率很高                 \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_ele, single=False)

    def _ele(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None,
             single: bool = True) -> Union[DriverElement, str, None, List[Union[DriverElement, str]]]:
        """返回当前元素下级符合条件的子元素，默认返回第一个                                                    \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :return: DriverElement对象
        """
        # 先转换为sessionElement，再获取所有元素，获取它们的css selector路径，再用路径在页面上执行查找
        loc = get_loc(loc_or_str)
        if loc[0] == 'css selector' and str(loc[1]).startswith(':root'):
            loc = loc[0], loc[1][5:]

        timeout = timeout if timeout is not None else self.page.timeout
        t1 = perf_counter()
        eles = make_session_ele(self.html).eles(loc)
        while not eles and perf_counter() - t1 <= timeout:
            eles = make_session_ele(self.html).eles(loc)

        if not eles:
            return None if single else eles

        css_paths = [i.css_path[47:] for i in eles]

        if single:
            return make_driver_ele(self, f'css:{css_paths[0]}', single, timeout)
        else:
            return [make_driver_ele(self, f'css:{css}', True, timeout) for css in css_paths]

    def run_script(self, script: str, *args) -> Any:
        """执行js代码，传入自己为第一个参数  \n
        :param script: js文本
        :param args: 传入的参数
        :return: js执行结果
        """
        shadow_root = WebElement(self.page.driver, self.inner_ele._id)
        return shadow_root.parent.execute_script(script, shadow_root, *args)

    def is_enabled(self) -> bool:
        """是否可用"""
        return self.inner_ele.is_enabled()

    def is_valid(self) -> bool:
        """用于判断元素是否还能用，应对页面跳转元素不能用的情况"""
        try:
            self.is_enabled()
            return True

        except Exception:
            return False
