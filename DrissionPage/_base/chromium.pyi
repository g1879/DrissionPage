# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from threading import Lock
from typing import List, Optional, Set, Dict, Union, Tuple, Literal, Any

from .driver import BrowserDriver, Driver
from .._configs.chromium_options import ChromiumOptions
from .._configs.session_options import SessionOptions
from .._functions.cookies import CookiesList
from .._pages.chromium_base import Timeout, ChromiumBase
from .._pages.chromium_tab import ChromiumTab
from .._pages.mix_tab import MixTab
from .._units.downloader import DownloadManager
from .._units.setter import BrowserSetter
from .._units.states import BrowserStates
from .._units.waiter import BrowserWaiter


class Chromium(object):
    _BROWSERS: dict = ...
    _lock: Lock = ...

    id: str = ...
    address: str = ...
    version: str = ...
    retry_times: int = ...
    retry_interval: float = ...

    _set: Optional[BrowserSetter] = ...
    _wait: Optional[BrowserWaiter] = ...
    _states: Optional[BrowserStates] = ...
    _chromium_options: ChromiumOptions = ...
    _session_options: SessionOptions = ...
    _driver: BrowserDriver = ...
    _frames: dict = ...
    _drivers: Dict[str, Driver] = ...
    _all_drivers: Dict[str, Set[Driver]] = ...
    _relation: Dict[str, Optional[str]] = ...
    _process_id: Optional[int] = ...
    _dl_mgr: DownloadManager = ...
    _timeouts: Timeout = ...
    _load_mode: str = ...
    _download_path: str = ...
    _auto_handle_alert: Optional[bool] = ...
    _is_exists: bool = ...
    _is_headless: bool = ...
    _disconnect_flag: bool = ...
    _none_ele_return_value: bool = ...
    _none_ele_value: Any = ...
    _newest_tab_id: Optional[str] = ...

    def __new__(cls,
                addr_or_opts: Union[str, int, ChromiumOptions] = None,
                session_options: Union[SessionOptions, None, False] = None):
        """
        :param addr_or_opts: 浏览器地址:端口、ChromiumOptions对象或端口数字（int）
        :param session_options: 使用双模Tab时使用的默认Session配置，为None使用ini文件配置，为False不从ini读取
        """
        ...

    def __init__(self, addr_or_opts: Union[str, int, ChromiumOptions] = None,
                 session_options: Union[SessionOptions, None, False] = None):
        """
        :param addr_or_opts: 浏览器地址:端口、ChromiumOptions对象或端口数字（int）
        :param session_options: 使用双模Tab时使用的默认Session配置，为None使用ini文件配置，为False不从ini读取
        """
        ...

    @property
    def user_data_path(self) -> str:
        """返回用户文件夹路径"""
        ...

    @property
    def process_id(self) -> Optional[int]:
        """返回浏览器进程id"""
        ...

    @property
    def timeout(self) -> float:
        """返回基础超时设置"""
        ...

    @property
    def timeouts(self) -> Timeout:
        """返回所有超时设置"""
        ...

    @property
    def load_mode(self) -> Literal['none', 'normal', 'eager']:
        """返回页面加载模式，包括 'none', 'normal', 'eager' 三种"""
        ...

    @property
    def download_path(self) -> str:
        """返回默认下载路径"""
        ...

    @property
    def set(self) -> BrowserSetter:
        """返回用于设置的对象"""
        ...

    @property
    def states(self) -> BrowserStates:
        """返回用于获取状态的对象"""
        ...

    @property
    def wait(self) -> BrowserWaiter:
        """返回用于等待的对象"""
        ...

    @property
    def tabs_count(self) -> int:
        """返回标签页数量，只统计page、webview类型"""
        ...

    @property
    def tab_ids(self) -> List[str]:
        """返回所有标签页id组成的列表，只统计page、webview类型"""
        ...

    @property
    def latest_tab(self) -> Union[MixTab, str]:
        """返回最新的标签页，最新标签页指最后创建或最后被激活的
        当Settings.singleton_tab_obj==True时返回Tab对象，否则返回tab id"""
        ...

    def cookies(self, all_info: bool = False) -> CookiesList:
        """以list格式返回所有域名的cookies
        :param all_info: 是否返回所有内容，False则只返回name, value, domain
        :return: cookies组成的列表
        """
        ...

    def new_tab(self,
                url: str = None,
                new_window: bool = False,
                background: bool = False,
                new_context: bool = False) -> MixTab:
        """新建一个标签页
        :param url: 新标签页跳转到的网址，为None时新建空标签页
        :param new_window: 是否在新窗口打开标签页，隐身模式下无效
        :param background: 是否不激活新标签页，隐身模式和访客模式及new_window为True时无效
        :param new_context: 是否创建独立环境，隐身模式和访客模式下无效
        :return: 新标签页对象
        """
        ...

    def get_tab(self,
                id_or_num: Union[str, int] = None,
                title: str = None,
                url: str = None,
                tab_type: Union[str, list, tuple] = 'page',
                as_id: bool = False) -> Union[MixTab, str]:
        """获取一个标签页对象，id_or_num不为None时，后面几个参数无效
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
                 as_id: bool = False) -> List[MixTab, str]:
        """查找符合条件的tab，返回它们组成的列表，title和url是与关系
        :param title: 要匹配title的文本
        :param url: 要匹配url的文本
        :param tab_type: tab类型，可用列表输入多个
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: Tab对象列表
        """
        ...

    def close_tabs(self,
                   tabs_or_ids: Union[str, ChromiumTab, List[Union[str, ChromiumTab]],
                   Tuple[Union[str, ChromiumTab]]],
                   others: bool = False) -> None:
        """关闭传入的标签页，可传入多个
        :param tabs_or_ids: 指定的标签页对象或id，可用列表或元组传入多个
        :param others: 是否关闭指定标签页之外的
        :return: None
        """
        ...

    def _close_tab(self, tab: Union[ChromiumBase, str]):
        """关闭一个标签页
        :param tab: 标签页对象或id
        :return: None
        """

    def activate_tab(self, id_ind_tab: Union[int, str, ChromiumTab]) -> None:
        """使一个标签页显示到前端
        :param id_ind_tab: 标签页id（str）、Tab对象或标签页序号（int），序号从1开始
        :return: None
        """
        ...

    def reconnect(self) -> None:
        """断开重连"""
        ...

    def clear_cache(self, cache: bool = True, cookies: bool = True) -> None:
        """清除缓存，可选要清除的项
        :param cache: 是否清除cache
        :param cookies: 是否清除cookies
        :return: None
        """
        ...

    def quit(self, timeout: float = 5, force: bool = False, del_data: bool = False) -> None:
        """关闭浏览器
        :param timeout: 等待浏览器关闭超时时间（秒）
        :param force: 是否立刻强制终止进程
        :param del_data: 是否删除用户文件夹
        :return: None
        """
        ...

    def _new_tab(self,
                 mix: bool = True,
                 url: str = None,
                 new_window: bool = False,
                 background: bool = False,
                 new_context: bool = False) -> Union[ChromiumTab, MixTab]:
        """新建一个标签页
        :param mix: 是否创建MixTab
        :param url: 新标签页跳转到的网址
        :param new_window: 是否在新窗口打开标签页
        :param background: 是否不激活新标签页，如new_window为True则无效
        :param new_context: 是否创建新的上下文
        :return: 新标签页对象
        """
        ...

    def _get_tab(self,
                 id_or_num: Union[str, int] = None,
                 title: str = None,
                 url: str = None,
                 tab_type: Union[str, list, tuple] = 'page',
                 mix: bool = True,
                 as_id: bool = False) -> Union[ChromiumTab, str]:
        """获取一个标签页对象，id_or_num不为None时，后面几个参数无效
        :param id_or_num: 要获取的标签页id或序号，序号从1开始，可传入负数获取倒数第几个，不是视觉排列顺序，而是激活顺序
        :param title: 要匹配title的文本，模糊匹配，为None则匹配所有
        :param url: 要匹配url的文本，模糊匹配，为None则匹配所有
        :param tab_type: tab类型，可用列表输入多个，如 'page', 'iframe' 等，为None则匹配所有
        :param mix: 是否返回可切换模式的Tab对象
        :param as_id: 是否返回标签页id而不是标签页对象，mix=False时无效
        :return: Tab对象
        """
        ...

    def _get_tabs(self,
                  title: str = None,
                  url: str = None,
                  tab_type: Union[str, list, tuple] = 'page',
                  mix: bool = True,
                  as_id: bool = False) -> List[ChromiumTab, str]:
        """查找符合条件的tab，返回它们组成的列表，title和url是与关系
        :param title: 要匹配title的文本
        :param url: 要匹配url的文本
        :param tab_type: tab类型，可用列表输入多个
        :param mix: 是否返回可切换模式的Tab对象
        :param as_id: 是否返回标签页id而不是标签页对象，mix=False时无效
        :return: Tab对象列表
        """
        ...

    def _run_cdp(self, cmd, **cmd_args) -> dict:
        """执行Chrome DevTools Protocol语句
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        ...

    def _get_driver(self, tab_id: str, owner=None) -> Driver:
        """新建并返回指定tab id的Driver
        :param tab_id: 标签页id
        :param owner: 使用该驱动的对象
        :return: Driver对象
        """
        ...

    def _onTargetCreated(self, **kwargs): ...

    def _onTargetDestroyed(self, **kwargs): ...

    def _on_disconnect(self): ...
