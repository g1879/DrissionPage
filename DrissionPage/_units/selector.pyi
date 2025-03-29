# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union, Tuple, List, Optional

from .._elements.chromium_element import ChromiumElement


class SelectElement(object):
    _ele: ChromiumElement = ...
    def __init__(self, ele: ChromiumElement):
        """
        :param ele: <select>元素对象
        """
        ...

    def __call__(self,
                 text_or_index: Union[str, int, list, tuple],
                 timeout: float = None) -> ChromiumElement:
        """选定下拉列表中子元素
        :param text_or_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param timeout: 超时时间（秒），不输入默认实用页面超时时间
        :return: <select>元素对象
        """
        ...

    @property
    def is_multi(self) -> bool:
        """返回是否多选表单"""
        ...

    @property
    def options(self) -> List[ChromiumElement]:
        """返回所有选项元素组成的列表"""
        ...

    @property
    def selected_option(self) -> Optional[ChromiumElement]:
        """返回第一个被选中的<option>元素"""
        ...

    @property
    def selected_options(self) -> List[ChromiumElement]:
        """返回所有被选中的<option>元素列表"""
        ...

    def all(self) -> ChromiumElement:
        """全选"""
        ...

    def invert(self) -> ChromiumElement:
        """反选"""
        ...

    def clear(self) -> ChromiumElement:
        """清除所有已选项"""
        ...

    def by_text(self,
                text: Union[str, list, tuple],
                timeout: float = None) -> ChromiumElement:
        """此方法用于根据text值选择项。当元素是多选列表时，可以接收list或tuple
        :param text: text属性值，传入list或tuple可选择多项
        :param timeout: 超时时间（秒），为None默认使用页面超时时间
        :return: <select>元素对象
        """
        ...

    def by_value(self,
                 value: Union[str, list, tuple],
                 timeout: float = None) -> ChromiumElement:
        """此方法用于根据value值选择项。当元素是多选列表时，可以接收list或tuple
        :param value: value属性值，传入list或tuple可选择多项
        :param timeout: 超时时间，为None默认使用页面超时时间
        :return: <select>元素对象
        """
        ...

    def by_index(self,
                 index: Union[int, list, tuple],
                 timeout: float = None) -> ChromiumElement:
        """此方法用于根据index值选择项。当元素是多选列表时，可以接收list或tuple
        :param index: 序号，从1开始，可传入负数获取倒数第几个，传入list或tuple可选择多项
        :param timeout: 超时时间，为None默认使用页面超时时间
        :return: <select>元素对象
        """
        ...

    def by_locator(self,
                   locator: Union[Tuple[str, str], str],
                   timeout: float = None) -> ChromiumElement:
        """用定位符选择指定的项
        :param locator: 定位符
        :param timeout: 超时时间
        :return: <select>元素对象
        """
        ...

    def by_option(self, 
                  option: Union[ChromiumElement, List[ChromiumElement], Tuple[ChromiumElement]]) -> ChromiumElement:
        """选中单个或多个<option>元素
        :param option: <option>元素或它们组成的列表
        :return: <select>元素对象
        """
        ...

    def cancel_by_text(self,
                       text: Union[str, list, tuple],
                       timeout: float = None) -> ChromiumElement:
        """此方法用于根据text值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param text: 文本，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: <select>元素对象
        """
        ...

    def cancel_by_value(self,
                        value: Union[str, list, tuple],
                        timeout: float = None) -> ChromiumElement:
        """此方法用于根据value值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param value: value属性值，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: <select>元素对象
        """
        ...

    def cancel_by_index(self,
                        index: Union[int, list, tuple],
                        timeout: float = None) -> ChromiumElement:
        """此方法用于根据index值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param index: 序号，从1开始，可传入负数获取倒数第几个，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: <select>元素对象
        """
        ...

    def cancel_by_locator(self,
                          locator: Union[Tuple[str, str], str],
                          timeout: float = None) -> ChromiumElement:
        """用定位符取消选择指定的项
        :param locator: 定位符
        :param timeout: 超时时间
        :return: <select>元素对象
        """
        ...

    def cancel_by_option(self,
                         option: Union[ChromiumElement, List[ChromiumElement], 
                                 Tuple[ChromiumElement]]) -> ChromiumElement:
        """取消选中单个或多个<option>元素
        :param option: <option>元素或它们组成的列表
        :return: <select>元素对象
        """
        ...

    def _by_loc(self,
                loc: Union[str, Tuple[str, str]],
                timeout: float = None,
                cancel: bool = False) -> ChromiumElement:
        """用定位符取消选择指定的项
        :param loc: 定位符
        :param timeout: 超时时间
        :param cancel: 是否取消选择
        :return: <select>元素对象
        """
        ...

    def _select(self,
                condition: Union[str, int, list, tuple] = None,
                para_type: str = 'text',
                cancel: bool = False,
                timeout: float = None) -> ChromiumElement:
        """选定或取消选定下拉列表中子元素
        :param condition: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param cancel: 是否取消选择
        :return: <select>元素对象
        """
        ...

    def _text_value(self,
                    condition: Union[list, set],
                    para_type: str,
                    mode: str,
                    timeout: float) -> ChromiumElement:
        """执行text和value搜索
        :param condition: 条件set
        :param para_type: 参数类型，可选 'text'、'value'
        :param mode: 'true' 或 'false'
        :param timeout: 超时时间
        :return: <select>元素对象
        """
        ...

    def _index(self, condition: set, mode: str, timeout: float) -> ChromiumElement:
        """执行index搜索
        :param condition: 条件set
        :param mode: 'true' 或 'false'
        :param timeout: 超时时间
        :return: <select>元素对象
        """
        ...

    def _select_options(self, 
                        option: Union[ChromiumElement, List[ChromiumElement], Tuple[ChromiumElement]],
                        mode: str) -> ChromiumElement:
        """选中或取消某个选项
        :param option: options元素对象
        :param mode: 选中还是取消
        :return: <select>元素对象
        """
        ...

    def _dispatch_change(self) -> None:
        """触发修改动作"""
        ...
