# -*- coding:utf-8 -*-
from typing import Optional, List, Union

from .chromium import Chromium
from .._functions.cookies import CookiesList
from .._pages.chromium_tab import ChromiumTab
from .._units.setter import BrowserContextSetter
from .._units.waiter import BrowserContextWaiter


class ChromiumContext(object):
    _browser: Chromium = ...
    _context_id: str = ...
    _set: Optional[BrowserContextSetter] = ...
    _wait: Optional[BrowserContextWaiter] = ...
    _default_context: bool = ...

    def __init__(self, browser: Chromium, context_id: str):
        """
        :param browser: Chromium对象
        :param context_id: context id
        """
        ...

    @property
    def browser(self) -> Chromium:
        ...

    @property
    def set(self) -> BrowserContextSetter:
        ...

    @property
    def wait(self) -> BrowserContextWaiter:
        ...

    @property
    def tab_ids(self) -> List[str]:
        """返回当前浏览器子环境所有标签页id组成的列表，只统计page、webview类型"""
        ...

    @property
    def latest_tab(self) -> Union[ChromiumTab, str]:
        """返当前认浏览器子环境最新的标签页，最新标签页指最后创建或最后被激活的
        当Settings.singleton_tab_obj==True时返回Tab对象，否则返回tab id"""
        ...

    def cookies(self, all_info=False) -> CookiesList:
        """以list格式返回当前子环境的所有域名的cookies
        :param all_info: 是否返回所有内容，False则只返回name, value, domain
        :return: cookies组成的列表
        """
        ...

    def new_tab(self,
                url: str = None,
                new_window: bool = False,
                background: bool = False,
                hidden: bool = False) -> ChromiumTab:
        """在当前子环境新建一个标签页
        :param url: 新标签页跳转到的网址
        :param new_window: 是否在新窗口打开标签页
        :param background: 是否不激活新标签页，如new_window为True则无效
        :param hidden: 是否隐藏，为True时忽略new_window和background参数
        :return: 新标签页对象
        """
        ...

    def get_tab(self,
                id_or_num: Union[str, int] = None,
                title: str = None,
                url: str = None,
                tab_type: Union[str, list, tuple, None] = 'page',
                as_id: bool = False) -> Union[ChromiumTab, str]:
        """在当前浏览器子环境获取一个标签页对象，id_or_num不为None时，后面几个参数无效
        :param id_or_num: 要获取的标签页id或序号，序号从1开始，可传入负数获取倒数第几个，不是视觉排列顺序，而是激活顺序
        :param title: 要匹配title的文本，模糊匹配，为None则匹配所有
        :param url: 要匹配url的文本，模糊匹配，为None则匹配所有
        :param tab_type: tab类型，可用列表输入多个，如 'page', 'iframe' 等，为None则匹配所有
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: Tab对象
        """
        ...

    def get_tabs(self,
                 title: str = None,
                 url: str = None,
                 tab_type: Union[str, list, tuple] = 'page',
                 as_id: bool = False) -> List[Union[ChromiumTab, str]]:
        """在当前浏览器子环境查找符合条件的tab，返回它们组成的列表，title和url是与关系
        :param title: 要匹配title的文本
        :param url: 要匹配url的文本
        :param tab_type: tab类型，可用列表输入多个
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: Tab对象列表
        """
        ...

    def close(self) -> None:
        """关闭当前浏览器子环境，里面的标签页会同时关闭"""
        ...

    def _run_cdp(self, cmd, _ignore=None, **cmd_args):
        ...
