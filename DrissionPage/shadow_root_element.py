#!/usr/bin/env python
# -*- coding:utf-8 -*-
from html import unescape
from re import split as re_SPLIT
from typing import Union, Any

from selenium.webdriver.remote.webelement import WebElement

from .common import DrissionElement
from .driver_element import execute_driver_find


class ShadowRootElement(DrissionElement):
    def __init__(self, inner_ele: WebElement, parent_ele, timeout: float = 10):
        super().__init__(inner_ele)
        self.parent_ele = parent_ele
        self.timeout = timeout
        self._driver = inner_ele.parent

    def __repr__(self):
        return f'<ShadowRootElement in {self.parent_ele} >'

    @property
    def driver(self):
        """返回控制元素的WebDriver对象"""
        return self._driver

    @property
    def tag(self):
        return 'shadow-root'

    @property
    def html(self):
        return unescape(self.inner_ele.get_attribute('innerHTML')).replace('\xa0', ' ')

    @property
    def parent(self):
        return self.parent_ele

    def parents(self, num: int = 1):
        """返回上面第num级父元素              \n
        :param num: 第几级父元素
        :return: DriverElement对象
        """
        loc = 'xpath', f'.{"/.." * (num - 1)}'
        return self.parent_ele.ele(loc, timeout=0.01, show_errmsg=False)

    @property
    def next(self):
        """返回后一个兄弟元素"""
        return self.nexts()

    def nexts(self, num: int = 1):
        """返回后面第num个兄弟元素      \n
        :param num: 后面第几个兄弟元素
        :return: DriverElement对象
        """
        loc = 'css selector', f':nth-child({num})'
        return self.parent_ele.ele(loc)

    def ele(self,
            loc_or_str: Union[tuple, str],
            mode: str = 'single',
            timeout: float = None,
            show_errmsg: bool = False):
        """返回当前元素下级符合条件的子元素，默认返回第一个                                                  \n
        示例：                                                                                           \n
        - 用loc元组查找：                                                                                 \n
            ele.ele((By.CLASS_NAME, 'ele_class')) - 返回第一个class为ele_class的子元素                     \n
        - 用查询字符串查找：                                                                               \n
            查找方式：属性、tag name和属性、文本、css selector                                              \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                        \n
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
            ele.ele('css:div.ele_class')                - 返回第一个符合css selector的子元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param mode: 'single' 或 'all'，对应查找一个或全部
        :param timeout: 查找元素超时时间
        :param show_errmsg: 出现异常时是否打印信息
        :return: DriverElement对象
        """
        if isinstance(loc_or_str, str):
            loc_or_str = get_css_from_str(loc_or_str)
        elif isinstance(loc_or_str, tuple) and len(loc_or_str) == 2:
            if loc_or_str[0] == 'xpath':
                raise ValueError('不支持xpath')
        else:
            raise ValueError('Argument loc_or_str can only be tuple or str.')

        timeout = timeout or self.timeout
        if loc_or_str[0] == 'css selector':
            return execute_driver_find(self.inner_ele, loc_or_str, mode, show_errmsg, timeout)
        elif loc_or_str[0] == 'text':
            return self._find_eles_by_text(loc_or_str[1], loc_or_str[2], loc_or_str[3], mode)

    def eles(self,
             loc_or_str: Union[tuple, str],
             timeout: float = None,
             show_errmsg: bool = False):
        """返回当前元素下级所有符合条件的子元素                                                            \n
        示例：                                                                                          \n
        - 用loc元组查找：                                                                                \n
            ele.eles((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的子元素                     \n
        - 用查询字符串查找：                                                                              \n
            查找方式：属性、tag name和属性、文本、css selector                                              \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                       \n
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
            ele.eles('css:div.ele_class')                - 返回所有符合css selector的子元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param show_errmsg: 出现异常时是否打印信息
        :return: DriverElement对象组成的列表
        """
        return self.ele(loc_or_str, mode='all', show_errmsg=show_errmsg, timeout=timeout)

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
        except:
            return False

    def _find_eles_by_text(self, text: str, tag: str = '', match: str = 'exact', mode: str = 'single'):
        """根据文本获取页面元素                               \n
        :param text: 文本字符串
        :param tag: tag name
        :param match: 'exact' 或 'fuzzy'，对应精确或模糊匹配
        :param mode: 'single' 或 'all'，对应匹配一个或全部
        :return: 返回DriverElement对象或组成的列表
        """
        eles = self.run_script('return arguments[0].querySelectorAll("*")')  # 获取所有元素
        from .driver_element import DriverElement
        results = []
        for ele in eles:  # 遍历所有元素，找到符合条件的
            if tag and tag != ele.tag_name:
                continue
            txt = self.driver.execute_script(
                'if(arguments[0].firstChild!=null){return arguments[0].firstChild.nodeValue}', ele)
            txt = txt or ''
            if text == '' or match == 'exact':  # 匹配没有文本的元素或精确匹配
                if text == txt:
                    if mode == 'single':
                        return DriverElement(ele)
                    elif mode == 'all':
                        results.append(DriverElement(ele))
            elif match == 'fuzzy':  # 模糊匹配
                if text in txt:
                    if mode == 'single':
                        return DriverElement(ele)
                    elif mode == 'all':
                        results.append(DriverElement(ele))
        return None if mode == 'single' else results


def get_css_from_str(loc: str) -> tuple:
    """处理元素查找语句                                                \n
    查找方式：属性、tag name及属性、文本、css selector                  \n
    =表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串           \n
    =表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串           \n
    示例：                                                            \n
        @class:ele_class - class含有ele_class的元素                    \n
        @class=ele_class - class等于ele_class的元素                    \n
        @class - 带class属性的元素                                     \n
        tag:div - div元素                                              \n
        tag:div@class:ele_class - class含有ele_class的div元素          \n
        tag:div@class=ele_class - class等于ele_class的div元素           \n
        tag:div@text():search_text - 文本含有search_text的div元素        \n
        tag:div@text()=search_text - 文本等于search_text的div元素        \n
        text:search_text - 文本含有search_text的元素                     \n
        text=search_text - 文本等于search_text的元素                     \n
        css:div.ele_class                                               \n
    """
    loc_by = 'css selector'
    if loc.startswith('@'):  # 根据属性查找
        r = re_SPLIT(r'([:=])', loc[1:], maxsplit=1)
        if len(r) == 3:
            mode = '=' if r[1] == '=' else '*='
            loc_str = f'*[{r[0]}{mode}{r[2]}]'
        else:
            loc_str = f'*[{loc[1:]}]'
    elif loc.startswith(('tag=', 'tag:')):  # 根据tag name查找
        if '@' not in loc[4:]:
            loc_str = f'{loc[4:]}'
        else:
            at_lst = loc[4:].split('@', maxsplit=1)
            r = re_SPLIT(r'([:=])', at_lst[1], maxsplit=1)
            if len(r) == 3:
                if r[0] == 'text()':
                    match = 'exact' if r[1] == '=' else 'fuzzy'
                    return 'text', r[2], at_lst[0], match
                mode = '=' if r[1] == '=' else '*='
                loc_str = f'{at_lst[0]}[{r[0]}{mode}"{r[2]}"]'
            else:
                loc_str = f'{at_lst[0]}[{r[0]}]'
    elif loc.startswith(('css=', 'css:')):  # 用css selector查找
        loc_str = loc[4:]
    elif loc.startswith(('xpath=', 'xpath:')):  # 用xpath查找
        raise ValueError('不支持xpath')
    elif loc.startswith(('text=', 'text:')):  # 根据文本查找
        match = 'exact' if loc[4] == '=' else 'fuzzy'
        return 'text', loc[5:], '', match
    else:  # 根据文本模糊查找
        return 'text', loc, '', 'fuzzy'
    return loc_by, loc_str
