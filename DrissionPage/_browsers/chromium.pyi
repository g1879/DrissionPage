# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from threading import Lock
from typing import List, Optional, Set, Dict, Union, Tuple, Literal, Any, Iterable

from .chromium_context import ChromiumContext
from .._base.base import Messenger
from .._base.driver import Driver
from .._configs.chromium_options import ChromiumOptions
from .._configs.session_options import SessionOptions
from .._functions.cookies import CookiesList
from .._pages.chromium_base import Timeout, ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_tab import ChromiumTab
from .._units.downloader import DownloadManager
from .._units.listener import BrowserListener
from .._units.setter import BrowserSetter
from .._units.states import BrowserStates
from .._units.waiter import BrowserWaiter


class Chromium(Messenger):
    _BROWSERS: dict = ...
    _lock: Lock = ...

    _browser_id: str = ...
    address: str = ...
    _ws_address: str = ...
    _incognito: bool = ...
    _guest: bool = ...
    version: str = ...
    retry_times: int = ...
    retry_interval: float = ...
    _context: Optional[ChromiumContext] = ...
    _context_id: Optional[str] = ...
    _default_context: bool = ...

    _set: Optional[BrowserSetter] = ...
    _listener: Optional[BrowserListener]
    _wait: Optional[BrowserWaiter] = ...
    _states: Optional[BrowserStates] = ...
    _chromium_options: ChromiumOptions = ...
    _session_options: SessionOptions = ...
    _driver: Driver = ...
    _tabs: Tabs = ...
    _process_id: Optional[int] = ...
    _dl_mgr: DownloadManager = ...
    _timeouts: Timeout = ...
    _load_mode: str = ...
    _download_path: str = ...
    _auto_handle_alert: Optional[bool] = ...
    _is_exists: bool = ...
    _is_headless: bool = ...
    _ws_only: bool = ...
    _command_lines: str = ...
    _can_access_form: bool = ...
    _disconnect_flag: bool = ...
    _none_ele_return_value: bool = ...
    _none_ele_value: Any = ...

    def __new__(cls,
                addr_or_opts: Union[str, int, ChromiumOptions] = None,
                session_options: Union[SessionOptions, None, False] = None):
        """
        :param addr_or_opts: 浏览器地址:端口、ws地址、ChromiumOptions对象或端口数字（int）
        :param session_options: 使用双模Tab时使用的默认Session配置，为None使用ini文件配置，为False不从ini读取
        """
        ...

    def __init__(self, addr_or_opts: Union[str, int, ChromiumOptions] = None,
                 session_options: Union[SessionOptions, None, False] = None):
        """
        :param addr_or_opts: 浏览器地址:端口、ws地址、ChromiumOptions对象或端口数字（int）
        :param session_options: 使用双模Tab时使用的默认Session配置，为None使用ini文件配置，为False不从ini读取
        """
        ...

    @property
    def context(self) -> ChromiumContext:
        """返回当前浏览器默认的BrowserContext"""
        ...

    @property
    def id(self) -> str:
        """返回浏览器id"""
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
    def listen(self) -> BrowserListener:
        """返回用于监听网络数据的对象"""
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
    def tab_ids(self) -> List[str]:
        """返回默认浏览器子环境所有标签页id组成的列表，只统计page、webview类型"""
        ...

    @property
    def latest_tab(self) -> Union[ChromiumTab, str]:
        """返回默认浏览器子环境最新的标签页，最新标签页指最后创建或最后被激活的
        当Settings.singleton_tab_obj==True时返回Tab对象，否则返回tab id"""
        ...

    def _tab_ids(self, context_id: str) -> List[str]:
        """执行获取所有id操作
        :param context_id: 指定子环境id
        :return: 标签页id组成的列表
        """
        ...

    def cookies(self, all_info: bool = False) -> CookiesList:
        """以list格式返回默认子环境所有域名的cookies
        :param all_info: 是否返回所有内容，False则只返回name, value, domain
        :return: cookies组成的列表
        """
        ...

    def _cookies(self, all_info: bool = False, context_id: Optional[str] = None) -> CookiesList:
        """以list格式返回指定子环境所有域名的cookies
        :param all_info: 是否返回所有内容，False则只返回name, value, domain
        :param context_id: context id
        :return: cookies组成的列表
        """
        ...

    def new_context(self, proxy: str = None, proxy_bypass: Union[str, List[str]] = None,
                    auto_close: bool = True) -> ChromiumContext:
        """新建一个浏览器子环境
        :param proxy: 代理服务器
        :param proxy_bypass: 不代理的网址，用str传入多个网址时用;分隔
        :param auto_close: 是否随接管结束自动关闭
        :return: ChromiumContext对象
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
        :param hidden: 是否隐藏，为True时忽略new_window和background参数
        :return: 新标签页对象
        """
        ...

    def _new_tab(self,
                 url: str = None,
                 new_window: bool = False,
                 background: bool = False,
                 hidden: bool = False,
                 context_id: str = None,
                 is_browser=True) -> ChromiumTab:
        """新建一个标签页
        :param url: 新标签页跳转到的网址
        :param new_window: 是否在新窗口打开标签页
        :param background: 是否不激活新标签页，如new_window为True则无效
        :param hidden: 是否隐藏，为True时忽略new_window和background参数
        :param context_id: 浏览器子环境id
        :param is_browser: 调用此函数的是否浏览器自己
        :return: 新标签页对象
        """
        ...

    def get_tab(self,
                id_or_num: Union[str, int] = None,
                title: str = None,
                url: str = None,
                tab_type: Union[str, list, tuple, None] = 'page',
                as_id: bool = False) -> Union[ChromiumTab, str]:
        """在默认浏览器子环境获取一个标签页对象，id_or_num不为None时，后面几个参数无效
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
        """在默认浏览器子环境查找符合条件的tab，返回它们组成的列表，title和url是与关系
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

    def _close_tab(self, tab: Union[ChromiumBase, str]) -> None:
        """关闭一个标签页
        :param tab: 标签页对象或id
        :return: None
        """
        ...

    def activate_tab(self, id_ind_tab: Union[int, str, ChromiumTab]) -> None:
        """使默认子环境中一个标签页显示到前端
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

    def _attach(self, target_id: str) -> str:
        """把target附加到连接并返回session id
        :param target_id: target id
        :return: session id
        """
        ...

    def _detach(self, session_id: str) -> None:
        """把session连接移除
        :param session_id: session id
        :return: None
        """
        ...

    def _get_session_id(self, target_id: str, obj: Messenger = None) -> str:
        """对指定target创建一个session并返回其id，
        :param target_id: 指定target的id
        :param obj: 要绑定的Messenger对象
        :return: session id
        """
        ...

    def _get_tab(self,
                 context_id: str,
                 id_or_num: Union[str, int] = None,
                 title: str = None,
                 url: str = None,
                 tab_type: Union[str, list, tuple] = 'page',
                 as_id: bool = False) -> Union[ChromiumTab, str]:
        """获取一个标签页对象，id_or_num不为None时，后面几个参数无效
        :param context_id: context id
        :param id_or_num: 要获取的标签页id或序号，序号从1开始，可传入负数获取倒数第几个，不是视觉排列顺序，而是激活顺序
        :param title: 要匹配title的文本，模糊匹配，为None则匹配所有
        :param url: 要匹配url的文本，模糊匹配，为None则匹配所有
        :param tab_type: tab类型，可用列表输入多个，如 'page', 'iframe' 等，为None则匹配所有
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: Tab对象
        """
        ...

    def _get_tabs(self,
                  context_id: str,
                  title: str = None,
                  url: str = None,
                  tab_type: Union[str, list, tuple] = 'page',
                  as_id: bool = False) -> List[Union[ChromiumTab, str]]:
        """查找符合条件的tab，返回它们组成的列表，title和url是与关系
        :param context_id: context id
        :param title: 要匹配title的文本
        :param url: 要匹配url的文本
        :param tab_type: tab类型，可用列表输入多个
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: Tab对象列表
        """
        ...

    def _onTargetCreated(self, **kwargs): ...

    def _onTargetDestroyed(self, **kwargs): ...

    def _onDetachedFromTarget(self, **kwargs): ...

    def _on_disconnect(self): ...


def handle_options(addr_or_opts: Union[str, ChromiumOptions, Driver]):
    """设置浏览器启动属性
    :param addr_or_opts: 'ip:port'、ChromiumOptions、Driver
    :return: 返回ChromiumOptions对象
    """
    ...


def run_browser(options: ChromiumOptions) -> Tuple[bool, str, Optional[str], bool, Driver, bool, bool]:
    """连接浏览器
    :param options: ChromiumOptions对象
    :return: 返回(是否无头, 浏览器id, 命令行参数（接管的返回None）, 是否只能用ws连接, 浏览器连接驱动, 是否无痕模式, 是否访客模式)
    """
    ...


class Tabs(object):
    _sessions: Dict[str, str] = ...
    _targets: Dict[str, set] = ...
    _objects: Dict[str, ChromiumBase] = ...
    _openers: Dict[str, str] = ...
    _frames: Dict[str, str] = ...
    _contexts: Dict[str, str] = ...
    _context_newest_tab: Dict[str, str] = ...
    _tab_first_session: Dict[str, str] = ...
    _proxies: Dict[str, Tuple[str, str, str, str]] = ...

    def __init__(self):
        """保存tab id、session id、frame与tab关系"""
        ...

    @property
    def session_ids(self) -> Iterable[str]:
        """返回所有保存的session id"""
        ...

    @property
    def target_ids(self) -> Iterable[str]:
        """返回所有保存的target id"""
        ...

    @property
    def objects(self) -> Iterable[ChromiumBase]:
        """返回所有保存的页面对象"""
        ...

    @property
    def frame_ids(self) -> Dict[str, str]:
        """返回所有保存的iframe id"""
        ...

    @property
    def openers(self) -> Dict[str, str]:
        """返回所有保存的被打开页面和父页面的target id"""
        ...

    def add(self, session_id: str, target_id: str, context_id: str = None,
            opener: str = None, obj: ChromiumBase = None) -> None:
        """添加一个target的记录
        :param session_id: 这个target的session id
        :param target_id: 这个target的target id
        :param context_id: 这个target所在的context id
        :param opener: 打开这个target的页面的target id
        :param obj: 这个target的ChromiumBase对象
        :return: None
        """
        ...

    def add_obj(self, session_id: str, obj: ChromiumBase) -> None:
        """登记一个session id对应的ChromiumBase对象
        :param session_id: session id
        :param obj: ChromiumBase对象
        :return: None
        """
        ...

    def remove_target(self, target_id: str) -> None:
        """移除指定标签页及所有相关关系
        :param target_id: target id
        :return: None
        """
        ...

    def set_newest_tab(self, context_id: str, target_id: str) -> None:
        """"""
        ...

    def remove_context(self, context_id: str) -> None:
        """移除指定子环境
        :param context_id: context id
        :return: None
        """
        ...

    def set_proxy(self, context_id: str, proxy: Tuple[str, str, str, str]) -> None:
        """设置指定子环境使用的代理用户名密码
        :param context_id: context id
        :param proxy: (url, usr, pwd, full)
        :return: None
        """
        ...

    def get_proxy(self, context_id: str) -> Optional[Tuple[str, str, str, str]]:
        """获取指定子环境使用的代理信息，如没有设置，获取浏览器设置
        :param context_id: context id
        :return: (url, usr, pwd, full)
        """
        ...

    def get_newest_tab(self, context_id: str) -> str:
        """获取指定子环境中最后创建的tab id
        :param context_id: context id
        :return: 最后创建的tab id
        """
        ...

    def add_frame(self, frame_id: str, target_id: str) -> None:
        """记录一个iframe与target的关系
        :param frame_id: frame id
        :param target_id: 该frame所属target的id
        :return: None
        """
        ...

    def remove_frame(self, frame_id: str) -> None:
        """移除一个frame id与target id的关系
        :param frame_id: frame id
        :return: None
        """
        ...

    def remove_session(self, session_id: str) -> None:
        """移除指定session id
        :param session_id: session id
        :return: None
        """
        ...

    def get_session_ids(self, target_id: str) -> Set[str]:
        """获取指定target下的所有session id
        :param target_id: 指定target id
        :return: session id组成的set
        """
        ...

    def get_target_id(self, session_id: str) -> Optional[str]:
        """获取session_id对应的target id
        :param session_id: 要查找的session id
        :return: target id
        """
        ...

    def get_context_id(self, target_id: str = None, frame_id: str = None) -> Optional[str]:
        """获取对应的context id，只有一个参数生效
        :param target_id: 指定target id
        :param frame_id: 指定frame id
        :return: context id
        """
        ...

    def get_object(self, session_id: str, default: Optional[ChromiumBase] = None) -> Union[ChromiumBase, ChromiumFrame]:
        """获取session_id对应的ChromiumBase对象
        :param session_id: 要查找的session id
        :param default: 没有找到记录时默认返回的结果
        :return: ChromiumBase对象
        """
        ...

    def clear(self) -> None:
        """清空所有记录"""
        ...

    def stop_session(self, session_id: str) -> None:
        """停止session对应对象，删除session记录
        :param session_id: session id
        :return: None
        """
        ...

    def stop_target(self, target_id: str) -> None:
        """停止与target相关的所有对象，删除target记录
        :param target_id: target id
        :return: None
        """
        ...


def get_command_line(browser: Chromium) -> str:
    """获取浏览器命令行参数
    :param browser: Chromium对象
    :return: 命令行参数，获取失败时返回''
    """
    ...


def close_privacy_dialog(tab: ChromiumBase) -> None:
    """关闭隐私声明弹窗
    :param tab: ChromiumBase对象
    :return: None
    """
    ...
