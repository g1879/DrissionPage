# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union, Tuple, List, Optional

from .._browsers.chromium import Chromium
from .._configs.chromium_options import ChromiumOptions
from .._pages.chromium_tab import ChromiumTab
from .._units.rect import TabRect
from .._units.setter import ChromiumPageSetter
from .._units.waiter import ChromiumPageWaiter


class ChromiumPage(ChromiumTab):
    """用于管理浏览器和一个标签页的类"""
    _PAGES: dict = ...
    tab: ChromiumPage = ...
    _browser: Chromium = ...
    _rect: Optional[TabRect] = ...
    _is_exist: bool = ...

    def __repr__(self) -> str: ...

    def __new__(cls,
                addr_or_opts: Union[str, int, ChromiumOptions] = None,
                tab_id: str = None):
        """
        :param addr_or_opts: 浏览器地址:端口、ws地址、ChromiumOptions对象或端口数字（int）
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        """
        ...

    def __init__(self,
                 addr_or_opts: Union[str, int, ChromiumOptions] = None,
                 tab_id: str = None):
        """
        :param addr_or_opts: 浏览器地址:端口、ws地址、ChromiumOptions对象或端口数字（int）
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        """
        ...

    @property
    def set(self) -> ChromiumPageSetter:
        """返回用于设置的对象"""
        ...

    @property
    def wait(self) -> ChromiumPageWaiter:
        """返回用于等待的对象"""
        ...

    @property
    def tabs_count(self) -> int:
        """返回标签页数量"""
        ...

    @property
    def tab_ids(self) -> List[str]:
        """返回所有标签页id组成的列表"""
        ...

    @property
    def latest_tab(self) -> Union[ChromiumTab, ChromiumPage, str]:
        """返回最新的标签页，最新标签页指最后创建或最后被激活的
        当Settings.singleton_tab_obj==True时返回Tab对象，否则返回tab id"""
        ...

    @property
    def process_id(self) -> Optional[int]:
        """返回浏览器进程id"""
        ...

    @property
    def browser_version(self) -> str:
        """返回所控制的浏览器版本号"""
        ...

    @property
    def address(self) -> str:
        """返回浏览器地址ip:port"""
        ...

    def get_tab(self,
                id_or_num: Union[str, ChromiumTab, int] = None,
                title: str = None,
                url: str = None,
                tab_type: Union[str, list, tuple] = 'page',
                as_id: bool = False) -> Union[ChromiumTab, str, None]:
        """获取一个标签页对象，id_or_num不为None时，后面几个参数无效
        :param id_or_num: 要获取的标签页id或序号，序号从1开始，可传入负数获取倒数第几个，不是视觉排列顺序，而是激活顺序
        :param title: 要匹配title的文本，模糊匹配，为None则匹配所有
        :param url: 要匹配url的文本，模糊匹配，为None则匹配所有
        :param tab_type: tab类型，可用列表输入多个，如 'page', 'iframe' 等，为None则匹配所有
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: ChromiumTab对象
        """
        ...

    def get_tabs(self,
                 title: str = None,
                 url: str = None,
                 tab_type: Union[str, list, tuple] = 'page',
                 as_id: bool = False) -> Union[List[ChromiumTab], List[str]]:
        """查找符合条件的tab，返回它们组成的列表
        :param title: 要匹配title的文本，模糊匹配，为None则匹配所有
        :param url: 要匹配url的文本，模糊匹配，为None则匹配所有
        :param tab_type: tab类型，可用列表输入多个，如 'page', 'iframe' 等，为None则匹配所有
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: ChromiumTab对象组成的列表
        """
        ...

    def new_tab(self,
                url: str = None,
                new_window: bool = False,
                background: bool = False,
                hidden: bool = False) -> ChromiumTab:
        """新建一个标签页
        :param url: 新标签页跳转到的网址
        :param new_window: 是否在新窗口打开标签页
        :param background: 是否不激活新标签页，如new_window为True则无效
        :param hidden: 是否隐藏
        :return: 新标签页对象
        """
        ...

    def activate_tab(self,
                     id_ind_tab: Union[int, str, ChromiumTab]) -> None:
        """使标签页变为活动状态
        :param id_ind_tab: 标签页id（str）、Tab对象或标签页序号（int），序号从1开始
        :return: None
        """
        ...

    def close_tabs(self,
                   tabs_or_ids: Union[str, ChromiumTab, List[Union[str, ChromiumTab]],
                                Tuple[Union[str, ChromiumTab]]],
                   others: bool = False) -> None:
        """关闭传入的标签页，可传入多个
        :param tabs_or_ids: 要关闭的标签页对象或id，可传入列表或元组
        :param others: 是否关闭指定标签页之外的
        :return: None
        """
        ...

    def quit(self,
             timeout: float = 5,
             force: bool = True,
             del_data: bool = False) -> None:
        """关闭浏览器
        :param timeout: 等待浏览器关闭超时时间（秒）
        :param force: 关闭超时是否强制终止进程
        :param del_data: 是否删除用户文件夹
        :return: None
        """
        ...

    def _on_disconnect(self) -> None:
        """浏览器退出时执行"""
        ...
