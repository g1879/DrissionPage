# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   shadow_root_element.py
"""
from re import split as re_SPLIT
from typing import Union, Any, Tuple, List

from selenium.webdriver.remote.webelement import WebElement

from .base import BaseElement
from .driver_element import make_driver_ele, DriverElement
from .session_element import make_session_ele


class ShadowRootElement(BaseElement):
    """ShadowRootElement是用于处理ShadowRoot的类，使用方法和DriverElement基本一致"""

    def __init__(self, inner_ele: WebElement, parent_ele: DriverElement):
        super().__init__(inner_ele, parent_ele.page)
        self.parent_ele = parent_ele

    def __repr__(self) -> str:
        return f'<ShadowRootElement in {self.parent_ele} >'

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = None) -> Union[DriverElement, List[DriverElement], str]:
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
        """返回内部的html文本"""
        return self.inner_ele.get_attribute('innerHTML')

    @property
    def parent(self) -> DriverElement:
        """shadow-root所依赖的父元素"""
        return self.parent_ele

    def parents(self, num: int = 1) -> DriverElement:
        """返回上面第num级父元素              \n
        :param num: 第几级父元素
        :return: DriverElement对象
        """
        loc = 'xpath', f'.{"/.." * (num - 1)}'
        return self.parent_ele.ele(loc, timeout=0.1)

    def nexts(self, num: int = 1) -> DriverElement:
        """返回后面第num个兄弟元素      \n
        :param num: 后面第几个兄弟元素
        :return: DriverElement对象
        """
        loc = 'css selector', f':nth-child({num})'
        return self.parent_ele.ele(loc, timeout=0.1)

    def ele(self,
            loc_or_str: Union[Tuple[str, str], str],
            timeout: float = None) -> Union[DriverElement, List[DriverElement]]:
        """返回当前元素下级符合条件的第一个元素，默认返回                                   \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :return: DriverElement对象或属性、文本
        """
        return self._ele(loc_or_str, timeout)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[DriverElement]:
        """返回当前元素下级所有符合条件的子元素                                              \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :return: DriverElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_ele=None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高                 \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_ele)

    def s_eles(self, loc_or_ele):
        """查找所有符合条件的元素以SessionElement列表形式返回，处理复杂页面时效率很高                 \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_ele, single=False)

    def _ele(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None,
             single: bool = True) -> Union[DriverElement, List[DriverElement]]:
        """返回当前元素下级符合条件的子元素，默认返回第一个                                                    \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :return: DriverElement对象
        """
        if isinstance(loc_or_str, str):
            loc_or_str = str_to_css_loc(loc_or_str)
        elif isinstance(loc_or_str, tuple) and len(loc_or_str) == 2:
            if loc_or_str[0] == 'xpath':
                raise ValueError('不支持xpath。')
        else:
            raise ValueError('loc_or_str参数只能是tuple或str类型。')

        if loc_or_str[0] == 'css selector':
            return make_driver_ele(self, loc_or_str, single, timeout)
        elif loc_or_str[0] == 'text':
            return self._find_eles_by_text(loc_or_str[1], loc_or_str[2], loc_or_str[3], single)

    def run_script(self, script: str, *args) -> Any:
        """执行js代码，传入自己为第一个参数  \n
        :param script: js文本
        :param args: 传入的参数
        :return: js执行结果
        """
        return self.inner_ele.parent.execute_script(script, self.inner_ele, *args)

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

    # ----------------ShadowRootElement独有方法-----------------------
    def _find_eles_by_text(self,
                           text: str,
                           tag: str = '',
                           match: str = 'exact',
                           single: bool = True) -> Union[DriverElement, List[DriverElement]]:
        """根据文本获取页面元素                               \n
        :param text: 文本字符串
        :param tag: tag name
        :param match: 'exact' 或 'fuzzy'，对应精确或模糊匹配
        :param single: True则返回第一个，False则返回全部
        :return: 返回DriverElement对象或组成的列表
        """
        # 获取所有元素
        eles = self.run_script('return arguments[0].querySelectorAll("*")')
        results = []

        # 遍历所有元素，找到符合条件的
        for ele in eles:
            if tag and tag != ele.tag_name:
                continue

            txt = self.page.driver.execute_script(
                'if(arguments[0].firstChild!=null){return arguments[0].firstChild.nodeValue}', ele)
            txt = txt or ''

            # 匹配没有文本的元素或精确匹配
            if text == '' or match == 'exact':
                if text == txt:

                    if single:
                        return DriverElement(ele, self.page)
                    else:
                        results.append(DriverElement(ele, self.page))

            # 模糊匹配
            elif match == 'fuzzy':
                if text in txt:

                    if single:
                        return DriverElement(ele, self.page)
                    else:
                        results.append(DriverElement(ele, self.page))

        return None if single else results


def str_to_css_loc(loc: str) -> tuple:
    """处理元素查找语句                                                                              \n
    查找方式：属性、tag name及属性、文本、css selector                                              \n
    @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串           \n
    """
    loc_by = 'css selector'

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

    elif loc.startswith(('x:', 'x=', 'xpath:', 'xpath=')):
        raise ValueError('不支持xpath。')

    # 根据属性查找
    if loc.startswith('@'):
        r = re_SPLIT(r'([:=])', loc[1:], maxsplit=1)

        if len(r) == 3:
            mode = '=' if r[1] == '=' else '*='
            loc_str = f'*[{r[0]}{mode}{r[2]}]'
        else:
            loc_str = f'*[{loc[1:]}]'

    # 根据tag name查找
    elif loc.startswith(('tag=', 'tag:')):
        if '@' not in loc[4:]:
            loc_str = f'{loc[4:]}'

        else:
            at_lst = loc[4:].split('@', maxsplit=1)
            r = re_SPLIT(r'([:=])', at_lst[1], maxsplit=1)

            if len(r) == 3:
                if r[0] in ('text()', 'tx()'):
                    match = 'exact' if r[1] == '=' else 'fuzzy'
                    return 'text', r[2], at_lst[0], match
                mode = '=' if r[1] == '=' else '*='
                loc_str = f'{at_lst[0]}[{r[0]}{mode}"{r[2]}"]'
            else:
                loc_str = f'{at_lst[0]}[{r[0]}]'

    # 用css selector查找
    elif loc.startswith(('css=', 'css:')):
        loc_str = loc[4:]

    # 根据文本查找
    elif loc.startswith(('text=', 'text:')):
        match = 'exact' if loc[4] == '=' else 'fuzzy'
        return 'text', loc[5:], '', match

    # 根据文本模糊查找
    else:
        return 'text', loc, '', 'fuzzy'

    return loc_by, loc_str
