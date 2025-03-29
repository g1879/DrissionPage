# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union, List, Optional, Iterable, Dict

from .._base.base import BaseParser
from .._elements.chromium_element import ChromiumElement
from .._elements.session_element import SessionElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.session_page import SessionPage


class SessionElementsList(list):
    _owner: SessionPage = ...

    def __init__(self,
                 owner: SessionPage = None,
                 *args):
        """
        :param owner: 产生元素列表的页面
        :param args:
        """
        ...

    def __next__(self) -> SessionElement: ...

    def __getitem__(self, _i) -> Union[SessionElement, SessionElementsList]: ...

    def __iter__(self) -> List[SessionElement]: ...

    @property
    def get(self) -> Getter:
        """返回用于属性的对象"""
        ...

    @property
    def filter(self) -> SessionFilter:
        """返回用于筛选多个元素的对象"""
        ...

    @property
    def filter_one(self) -> SessionFilterOne:
        """用于筛选单个元素的对象"""
        ...


class ChromiumElementsList(SessionElementsList):
    _owner: ChromiumBase = ...

    def __init__(self,
                 owner: ChromiumBase = None,
                 *args):
        """
        :param owner: 产生元素列表的页面
        :param args:
        """
        ...

    def __next__(self) -> ChromiumElement: ...

    def __getitem__(self, _i) -> Union[ChromiumElement, ChromiumElementsList]: ...

    def __iter__(self) -> List[ChromiumElement]: ...

    @property
    def filter(self) -> ChromiumFilter:
        """返回用于筛选多个元素的对象"""
        ...

    @property
    def filter_one(self) -> ChromiumFilterOne:
        """用于筛选单个元素的对象"""
        ...

    def search(self,
               displayed: Optional[bool] = None,
               checked: Optional[bool] = None,
               selected: Optional[bool] = None,
               enabled: Optional[bool] = None,
               clickable: Optional[bool] = None,
               have_rect: Optional[bool] = None,
               have_text: Optional[bool] = None,
               tag: str = None) -> ChromiumFilter:
        """或关系筛选元素
        :param displayed: 是否显示，bool，None为忽略该项
        :param checked: 是否被选中，bool，None为忽略该项
        :param selected: 是否被选择，bool，None为忽略该项
        :param enabled: 是否可用，bool，None为忽略该项
        :param clickable: 是否可点击，bool，None为忽略该项
        :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
        :param have_text: 是否含有文本，bool，None为忽略该项
        :param tag: 指定的元素类型
        :return: 筛选结果
        """
        ...

    def search_one(self,
                   index: int = 1,
                   displayed: Optional[bool] = None,
                   checked: Optional[bool] = None,
                   selected: Optional[bool] = None,
                   enabled: Optional[bool] = None,
                   clickable: Optional[bool] = None,
                   have_rect: Optional[bool] = None,
                   have_text: Optional[bool] = None,
                   tag: str = None) -> ChromiumElement:
        """或关系筛选元素，获取一个结果
        :param index: 元素序号，从1开始
        :param displayed: 是否显示，bool，None为忽略该项
        :param checked: 是否被选中，bool，None为忽略该项
        :param selected: 是否被选择，bool，None为忽略该项
        :param enabled: 是否可用，bool，None为忽略该项
        :param clickable: 是否可点击，bool，None为忽略该项
        :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
        :param have_text: 是否含有文本，bool，None为忽略该项
        :param tag: 指定的元素类型
        :return: 筛选结果
        """
        ...


class SessionFilterOne(object):
    _list: SessionElementsList = ...
    _index: int = ...

    def __init__(self, _list: SessionElementsList):
        """
        :param _list: 元素列表对象
        """
        ...

    def __call__(self, index: int = 1) -> SessionFilterOne:
        """返回结果中第几个元素
        :param index: 元素序号，从1开始
        :return: 对象自身
        """
        ...

    def tag(self, name: str, equal: bool = True) -> SessionElement:
        """筛选某种元素
        :param name: 标签页名称
        :param equal: True表示匹配这种元素，False表示匹配非这种元素
        :return: 筛选结果
        """
        ...

    def attr(self, name: str, value: str, equal: bool = True) -> SessionElement:
        """以是否拥有某个attribute值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        ...

    def text(self, text: str, fuzzy: bool = True, contain: bool = True) -> SessionElement:
        """以是否含有指定文本为条件筛选元素
        :param text: 用于匹配的文本
        :param fuzzy: 是否模糊匹配
        :param contain: 是否包含该字符串，False表示不包含
        :return: 筛选结果
        """
        ...

    def _get_attr(self,
                  name: str,
                  value: str,
                  method: str,
                  equal: bool = True) -> SessionElement:
        """返回通过某个方法可获得某个值的元素
        :param name: 属性名称
        :param value: 属性值
        :param method: 方法名称
        :return: 筛选结果
        """
        ...


class SessionFilter(SessionFilterOne):

    def __iter__(self) -> Iterable[SessionElement]: ...

    def __next__(self) -> SessionElement: ...

    def __len__(self) -> int: ...

    def __getitem__(self, item: int) -> SessionElement: ...

    @property
    def get(self) -> Getter:
        """返回用于获取元素属性的对象"""
        ...

    def tag(self, name: str, equal: bool = True) -> SessionFilter:
        """筛选某种元素
        :param name: 标签页名称
        :param equal: True表示匹配这种元素，False表示匹配非这种元素
        :return: 筛选结果
        """
        ...

    def attr(self, name: str, value: str, equal: bool = True) -> SessionFilter:
        """以是否拥有某个attribute值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        ...

    def text(self, text: str, fuzzy: bool = True, contain: bool = True) -> SessionFilter:
        """以是否含有指定文本为条件筛选元素
        :param text: 用于匹配的文本
        :param fuzzy: 是否模糊匹配
        :param contain: 是否包含该字符串，False表示不包含
        :return: 筛选结果
        """
        ...

    def _get_attr(self,
                  name: str,
                  value: str,
                  method: str,
                  equal: bool = True) -> SessionFilter:
        """返回通过某个方法可获得某个值的元素
        :param name: 属性名称
        :param value: 属性值
        :param method: 方法名称
        :return: 筛选结果
        """
        ...


class ChromiumFilterOne(SessionFilterOne):
    _list: ChromiumElementsList = ...

    def __init__(self, _list: ChromiumElementsList):
        """
        :param _list: 元素列表对象
        """
        ...

    def __call__(self, index: int = 1) -> ChromiumFilterOne:
        """返回结果中第几个元素
        :param index: 元素序号，从1开始
        :return: 对象自身
        """
        ...

    def tag(self, name: str, equal: bool = True) -> SessionElement:
        """筛选某种元素
        :param name: 标签页名称
        :param equal: True表示匹配这种元素，False表示匹配非这种元素
        :return: 筛选结果
        """
        ...

    def attr(self, name: str, value: str, equal: bool = True) -> ChromiumElement:
        """以是否拥有某个attribute值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        ...

    def text(self,
             text: str,
             fuzzy: bool = True,
             contain: bool = True) -> ChromiumElement:
        """以是否含有指定文本为条件筛选元素
        :param text: 用于匹配的文本
        :param fuzzy: 是否模糊匹配
        :param contain: 是否包含该字符串，False表示不包含
        :return: 筛选结果
        """
        ...

    def displayed(self, equal: bool = True) -> ChromiumElement:
        """以是否显示为条件筛选元素
        :param equal: 是否匹配显示的元素，False匹配不显示的
        :return: 筛选结果
        """
        ...

    def checked(self, equal: bool = True) -> ChromiumElement:
        """以是否被选中为条件筛选元素
        :param equal: 是否匹配被选中的元素，False匹配不被选中的
        :return: 筛选结果
        """
        ...

    def selected(self, equal: bool = True) -> ChromiumElement:
        """以是否被选择为条件筛选元素，用于<select>元素项目
        :param equal: 是否匹配被选择的元素，False匹配不被选择的
        :return: 筛选结果
        """
        ...

    def enabled(self, equal: bool = True) -> ChromiumElement:
        """以是否可用为条件筛选元素
        :param equal: 是否匹配可用的元素，False表示匹配disabled状态的
        :return: 筛选结果
        """
        ...

    def clickable(self, equal: bool = True) -> ChromiumElement:
        """以是否可点击为条件筛选元素
        :param equal: 是否匹配可点击的元素，False表示匹配不是可点击的
        :return: 筛选结果
        """
        ...

    def have_rect(self, equal: bool = True) -> ChromiumElement:
        """以是否有大小为条件筛选元素
        :param equal: 是否匹配有大小的元素，False表示匹配没有大小的
        :return: 筛选结果
        """
        ...

    def style(self, name: str, value: str, equal: bool = True) -> ChromiumElement:
        """以是否拥有某个style值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        ...

    def property(self,
                 name: str,
                 value: str, equal: bool = True) -> ChromiumElement:
        """以是否拥有某个property值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        ...

    def _get_attr(self,
                  name: str,
                  value: str,
                  method: str, equal: bool = True) -> ChromiumElement:
        """返回通过某个方法可获得某个值的元素
        :param name: 属性名称
        :param value: 属性值
        :param method: 方法名称
        :return: 筛选结果
        """
        ...

    def _any_state(self, name: str, equal: bool = True) -> ChromiumElement:
        """
        :param name: 状态名称
        :param equal: 是否是指定状态，False表示否定状态
        :return: 选中的列表
        """
        ...


class ChromiumFilter(ChromiumFilterOne):

    def __iter__(self) -> Iterable[ChromiumElement]: ...

    def __next__(self) -> ChromiumElement: ...

    def __len__(self) -> int: ...

    def __getitem__(self, item: int) -> ChromiumElement: ...

    @property
    def get(self) -> Getter:
        """返回用于获取元素属性的对象"""
        ...

    def tag(self, name: str, equal: bool = True) -> ChromiumFilter:
        """筛选某种元素
        :param name: 标签页名称
        :param equal: True表示匹配这种元素，False表示匹配非这种元素
        :return: 筛选结果
        """
        ...

    def attr(self, name: str, value: str, equal: bool = True) -> ChromiumFilter:
        """以是否拥有某个attribute值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        ...

    def text(self, text: str, fuzzy: bool = True, contain: bool = True) -> ChromiumFilter:
        """以是否含有指定文本为条件筛选元素
        :param text: 用于匹配的文本
        :param fuzzy: 是否模糊匹配
        :param contain: 是否包含该字符串，False表示不包含
        :return: 筛选结果
        """
        ...

    def displayed(self, equal: bool = True) -> ChromiumFilter:
        """以是否显示为条件筛选元素
        :param equal: 是否匹配显示的元素，False匹配不显示的
        :return: 筛选结果
        """
        ...

    def checked(self, equal: bool = True) -> ChromiumFilter:
        """以是否被选中为条件筛选元素
        :param equal: 是否匹配被选中的元素，False匹配不被选中的
        :return: 筛选结果
        """
        ...

    def selected(self, equal: bool = True) -> ChromiumFilter:
        """以是否被选择为条件筛选元素，用于<select>元素项目
        :param equal: 是否匹配被选择的元素，False匹配不被选择的
        :return: 筛选结果
        """
        ...

    def enabled(self, equal: bool = True) -> ChromiumFilter:
        """以是否可用为条件筛选元素
        :param equal: 是否匹配可用的元素，False表示匹配disabled状态的
        :return: 筛选结果
        """
        ...

    def clickable(self, equal: bool = True) -> ChromiumFilter:
        """以是否可点击为条件筛选元素
        :param equal: 是否匹配可点击的元素，False表示匹配不是可点击的
        :return: 筛选结果
        """
        ...

    def have_rect(self, equal: bool = True) -> ChromiumFilter:
        """以是否有大小为条件筛选元素
        :param equal: 是否匹配有大小的元素，False表示匹配没有大小的
        :return: 筛选结果
        """
        ...

    def style(self, name: str, value: str, equal: bool = True) -> ChromiumFilter:
        """以是否拥有某个style值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        ...

    def property(self,
                 name: str,
                 value: str, equal: bool = True) -> ChromiumFilter:
        """以是否拥有某个property值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        ...

    def search_one(self,
                   index: int = 1,
                   displayed: Optional[bool] = None,
                   checked: Optional[bool] = None,
                   selected: Optional[bool] = None,
                   enabled: Optional[bool] = None,
                   clickable: Optional[bool] = None,
                   have_rect: Optional[bool] = None,
                   have_text: Optional[bool] = None,
                   tag: str = None) -> ChromiumElement:
        """或关系筛选元素，获取一个结果
        :param index: 元素序号，从1开始
        :param displayed: 是否显示，bool，None为忽略该项
        :param checked: 是否被选中，bool，None为忽略该项
        :param selected: 是否被选择，bool，None为忽略该项
        :param enabled: 是否可用，bool，None为忽略该项
        :param clickable: 是否可点击，bool，None为忽略该项
        :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
        :param have_text: 是否含有文本，bool，None为忽略该项
        :param tag: 指定的元素类型
        :return: 筛选结果
        """
        ...

    def search(self,
               displayed: Optional[bool] = None,
               checked: Optional[bool] = None,
               selected: Optional[bool] = None,
               enabled: Optional[bool] = None,
               clickable: Optional[bool] = None,
               have_rect: Optional[bool] = None,
               have_text: Optional[bool] = None,
               tag: str = None) -> ChromiumFilter:
        """或关系筛选元素
        :param displayed: 是否显示，bool，None为忽略该项
        :param checked: 是否被选中，bool，None为忽略该项
        :param selected: 是否被选择，bool，None为忽略该项
        :param enabled: 是否可用，bool，None为忽略该项
        :param clickable: 是否可点击，bool，None为忽略该项
        :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
        :param have_text: 是否含有文本，bool，None为忽略该项
        :param tag: 指定的元素类型
        :return: 筛选结果
        """
        ...

    def _get_attr(self,
                  name: str,
                  value: str,
                  method: str, equal: bool = True) -> ChromiumFilter:
        """返回通过某个方法可获得某个值的元素
        :param name: 属性名称
        :param value: 属性值
        :param method: 方法名称
        :return: 筛选结果
        """
        ...

    def _any_state(self, name: str, equal: bool = True) -> ChromiumFilter:
        """
        :param name: 状态名称
        :param equal: 是否是指定状态，False表示否定状态
        :return: 选中的列表
        """
        ...


class Getter(object):
    _list: SessionElementsList = ...

    def __init__(self, _list: SessionElementsList):
        """
        :param _list: 元素列表对象
        """
        ...

    def links(self) -> List[str]:
        """返回所有元素的link属性组成的列表"""
        ...

    def texts(self) -> List[str]:
        """返回所有元素的text属性组成的列表"""
        ...

    def attrs(self, name: str) -> List[str]:
        """返回所有元素指定的attr属性组成的列表
        :param name: 属性名称
        :return: 属性文本组成的列表
        """
        ...


def get_eles(locators: Union[str, tuple, List[Union[str, tuple]]],
             owner: BaseParser,
             any_one: bool = False,
             first_ele: bool = True,
             timeout: float = 10) -> Union[Dict[str, ChromiumElement], Dict[str, SessionElement],
Dict[str, List[ChromiumElement]], Dict[str, List[SessionElement]]]:
    """传入多个定位符，获取多个ele
    :param locators: 定位符或它们组成的列表
    :param owner: 页面或元素对象
    :param any_one: 是否找到任何一个即返回
    :param first_ele: 每个定位符是否只获取第一个元素
    :param timeout: 超时时间（秒）
    :return: 多个定位符组成的dict，first_only为False返回列表，否则为元素，无结果的返回False
    """
    ...


def get_frame(owner: BaseParser,
              loc_ind_ele: Union[str, int, tuple, ChromiumFrame, ChromiumElement],
              timeout: float = None) -> ChromiumFrame:
    """获取页面中一个frame对象
    :param owner: 要在其中查找元素的对象
    :param loc_ind_ele: 定位符、iframe序号、ChromiumFrame对象，序号从1开始，可传入负数获取倒数第几个
    :param timeout: 查找元素超时时间（秒）
    :return: ChromiumFrame对象
    """
    ...
