# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Tuple, Literal, Any, Optional

from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth

from .cookies_setter import SessionCookiesSetter, CookiesSetter, WebPageCookiesSetter, BrowserCookiesSetter
from .scroller import PageScroller
from .._base.base import BasePage
from .._base.chromium import Chromium
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._pages.chromium_tab import ChromiumTab
from .._pages.mix_tab import MixTab
from .._pages.session_page import SessionPage
from .._pages.web_page import WebPage

FILE_EXISTS = Literal['skip', 'rename', 'overwrite', 's', 'r', 'o']


class BaseSetter(object):
    _owner: Union[Chromium, BasePage] = ...

    def __init__(self, owner: Union[Chromium, BasePage]):
        """
        :param owner: BasePage对象
        """
        ...

    def NoneElement_value(self,
                          value: Any = None,
                          on_off: bool = True) -> None:
        """设置空元素是否返回设定值
        :param value: 返回的设定值
        :param on_off: 是否启用
        :return: None
        """
        ...

    def retry_times(self, times: int) -> None:
        """设置连接失败重连次数
        :param times: 重试次数
        :return: None
        """
        ...

    def retry_interval(self, interval: float) -> None:
        """设置连接失败重连间隔（秒）
        :param interval: 重试间隔
        :return: None
        """
        ...

    def download_path(self, path: Union[str, Path, None]) -> None:
        """设置下载路径
        :param path: 下载路径
        :return: None
        """
        ...


class SessionPageSetter(BaseSetter):
    _owner: SessionPage = ...
    _cookies_setter: Optional[SessionCookiesSetter] = ...

    def __init__(self, owner: SessionPage):
        """
        :param owner: SessionPage对象
        """
        ...

    @property
    def cookies(self) -> SessionCookiesSetter:
        """返回用于设置cookies的对象"""
        ...

    def download_path(self, path: Union[str, Path, None]) -> None:
        """设置下载路径
        :param path: 下载路径
        :return: None
        """
        ...

    def timeout(self, second: float) -> None:
        """设置连接超时时间
        :param second: 秒数
        :return: None
        """
        ...

    def encoding(self, encoding: Union[str, None], set_all: bool = True) -> None:
        """设置编码
        :param encoding: 编码名称，如果要取消之前的设置，传入None
        :param set_all: 是否设置对象参数，为False则只设置当前Response
        :return: None
        """
        ...

    def headers(self, headers: Union[str, dict]) -> None:
        """设置通用的headers
        :param headers: dict形式的headers
        :return: None
        """
        ...

    def header(self, name: str, value: str) -> None:
        """设置headers中一个项
        :param name: 设置名称
        :param value: 设置值
        :return: None
        """
        ...

    def user_agent(self, ua: str) -> None:
        """设置user agent
        :param ua: user agent
        :return: None
        """
        ...

    def proxies(self, http: str = None, https: str = None) -> None:
        """设置proxies参数
        :param http: http代理地址
        :param https: https代理地址
        :return: None
        """
        ...

    def auth(self, auth: Union[Tuple[str, str], HTTPBasicAuth, None]) -> None:
        """设置认证元组或对象
        :param auth: 认证元组或对象
        :return: None
        """
        ...

    def hooks(self, hooks: Union[dict, None]) -> None:
        """设置回调方法
        :param hooks: 回调方法
        :return: None
        """
        ...

    def params(self, params: Union[dict, None]) -> None:
        """设置查询参数字典
        :param params: 查询参数字典
        :return: None
        """
        ...

    def verify(self, on_off: Union[bool, None]) -> None:
        """设置是否验证SSL证书
        :param on_off: 是否验证 SSL 证书
        :return: None
        """
        ...

    def cert(self, cert: Union[str, Tuple[str, str], None]) -> None:
        """SSL客户端证书文件的路径(.pem格式)，或('cert', 'key')元组
        :param cert: 证书路径或元组
        :return: None
        """
        ...

    def stream(self, on_off: Union[bool, None]) -> None:
        """设置是否使用流式响应内容
        :param on_off: 是否使用流式响应内容
        :return: None
        """
        ...

    def trust_env(self, on_off: Union[bool, None]) -> None:
        """设置是否信任环境
        :param on_off: 是否信任环境
        :return: None
        """
        ...

    def max_redirects(self, times: Union[int, None]) -> None:
        """设置最大重定向次数
        :param times: 最大重定向次数
        :return: None
        """
        ...

    def add_adapter(self, url: str, adapter: HTTPAdapter) -> None:
        """添加适配器
        :param url: 适配器对应url
        :param adapter: 适配器对象
        :return: None
        """
        ...


class BrowserBaseSetter(BaseSetter):
    """Browser和ChromiumBase设置"""
    _cookies_setter: Optional[CookiesSetter] = ...

    def __init__(self, owner: ChromiumBase):
        """
        :param owner: ChromiumBase对象
        """
        ...

    @property
    def load_mode(self) -> LoadMode:
        """返回用于设置页面加载模式的对象"""
        ...

    def timeouts(self,
                 base=None,
                 page_load=None,
                 script=None) -> None:
        """设置超时时间，单位为秒
        :param base: 基本等待时间，除页面加载和脚本超时，其它等待默认使用
        :param page_load: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: None
        """
        ...


class BrowserSetter(BrowserBaseSetter):
    _owner: Chromium = ...
    _cookies_setter: BrowserCookiesSetter = ...

    def __init__(self, owner: Chromium):
        """
        :param owner: Chromium对象
        """
        ...

    @property
    def cookies(self) -> BrowserCookiesSetter:
        """返回用于设置cookies的对象"""
        ...

    @property
    def window(self)->WindowSetter:...

    def auto_handle_alert(self,
                          on_off: bool = True,
                          accept: bool = True) -> None:
        """设置本浏览器是否启用自动处理弹窗
        :param on_off: bool表示开或关，传入None表示使用Settings设置
        :param accept: bool表示确定还是取消
        :return: None
        """
        ...

    def download_path(self, path: Union[Path, str, None]) -> None:
        """设置下载路径
        :param path: 下载路径
        :return: None
        """
        ...

    def download_file_name(self,
                           name: str = None,
                           suffix: str = None) -> None:
        """设置下一个被下载文件的名称
        :param name: 文件名，可不含后缀，会自动使用远程文件后缀
        :param suffix: 后缀名，显式设置后缀名，不使用远程文件后缀
        :return: None
        """
        ...

    def when_download_file_exists(self, mode: FILE_EXISTS) -> None:
        """设置当存在同名文件时的处理方式
        :param mode: 可在 'rename', 'overwrite', 'skip', 'r', 'o', 's'中选择
        :return: None
        """
        ...


class ChromiumBaseSetter(BrowserBaseSetter):
    _owner: ChromiumBase = ...
    _cookies_setter: CookiesSetter = ...

    def __init__(self, owner): ...

    @property
    def scroll(self) -> PageScrollSetter:
        """返回用于设置页面滚动设置的对象"""
        ...

    @property
    def cookies(self) -> CookiesSetter:
        """返回用于设置cookies的对象"""
        ...

    def headers(self, headers: Union[dict, str]) -> None:
        """设置固定发送的headers
        :param headers: dict格式的headers数据，或从浏览器复制的headers文本（\n分行）
        :return: None
        """
        ...

    def user_agent(self, ua: str, platform: str = None) -> None:
        """为当前tab设置user agent，只在当前tab有效
        :param ua: user agent字符串
        :param platform: platform字符串
        :return: None
        """
        ...

    def session_storage(self, item: str, value: Union[str, bool]) -> None:
        """设置或删除某项sessionStorage信息
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        ...

    def local_storage(self, item: str, value: Union[str, bool]) -> None:
        """设置或删除某项localStorage信息
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        ...

    def upload_files(self, files: Union[str, Path, list, tuple]) -> None:
        """等待上传的文件路径
        :param files: 文件路径列表或字符串，字符串时多个文件用回车分隔
        :return: None
        """
        ...

    def auto_handle_alert(self,
                          on_off: bool = True,
                          accept: bool = True) -> None:
        """设置是否启用自动处理弹窗
        :param on_off: bool表示开或关
        :param accept: bool表示确定还是取消
        :return: None
        """
        ...

    def blocked_urls(self, urls: Union[list, tuple, str, None]) -> None:
        """设置要忽略的url
        :param urls: 要忽略的url，可用*通配符，可输入多个，传入None时清空已设置的内容
        :return: None
        """
        ...


class TabSetter(ChromiumBaseSetter):
    _owner: ChromiumTab = ...

    def __init__(self, owner: ChromiumTab):
        """
        :param owner: 标签页对象
        """
        ...

    @property
    def window(self) -> WindowSetter:
        """返回用于设置浏览器窗口的对象"""
        ...

    def download_path(self, path: Union[str, Path, None]) -> None:
        """设置下载路径
        :param path: 下载路径
        :return: None
        """
        ...

    def download_file_name(self,
                           name: str = None,
                           suffix: str = None) -> None:
        """设置下一个被下载文件的名称
        :param name: 文件名，可不含后缀，会自动使用远程文件后缀
        :param suffix: 后缀名，显式设置后缀名，不使用远程文件后缀
        :return: None
        """
        ...

    def when_download_file_exists(self, mode: FILE_EXISTS) -> None:
        """设置当存在同名文件时的处理方式
        :param mode: 可在 'rename', 'overwrite', 'skip', 'r', 'o', 's'中选择
        :return: None
        """
        ...

    def activate(self) -> None:
        """使标签页处于最前面"""
        ...


class ChromiumPageSetter(TabSetter):
    _owner: ChromiumPage = ...

    def __init__(self, owner: ChromiumPage):
        """
        :param owner: ChromiumPage对象
        """
        ...


class WebPageSetter(ChromiumPageSetter):
    _owner: WebPage = ...
    _session_setter: SessionPageSetter = ...
    _chromium_setter: ChromiumPageSetter = ...

    def __init__(self, owner: WebPage):
        """
        :param owner: WebPage对象
        """
        ...

    @property
    def cookies(self) -> WebPageCookiesSetter:
        """返回用于设置cookies的对象"""
        ...


class MixTabSetter(TabSetter):
    _owner: MixTab = ...
    _session_setter: SessionPageSetter = ...
    _chromium_setter: ChromiumBaseSetter = ...

    def __init__(self, owner: MixTab):
        """
        :param owner: MixTab对象
        """
        ...

    @property
    def cookies(self) -> WebPageCookiesSetter:
        """返回用于设置cookies的对象"""
        ...

    def timeouts(self,
                 base: float = None,
                 page_load: float = None,
                 script: float = None) -> None:
        """设置超时时间，单位为秒
        :param base: 基本等待时间，除页面加载和脚本超时，其它等待默认使用
        :param page_load: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: None
        """
        ...


class ChromiumElementSetter(object):
    _ele: ChromiumElement = ...

    def __init__(self, ele: ChromiumElement):
        """
        :param ele: ChromiumElement
        """
        ...

    def attr(self, name: str, value: str = '') -> None:
        """设置元素attribute属性
        :param name: 属性名
        :param value: 属性值
        :return: None
        """
        ...

    def property(self, name: str, value: str) -> None:
        """设置元素property属性
        :param name: 属性名
        :param value: 属性值
        :return: None
        """
        ...

    def style(self, name: str, value: str) -> None:
        """设置元素style样式
        :param name: 样式名称
        :param value: 样式值
        :return: None
        """
        ...

    def innerHTML(self, html: str) -> None:
        """设置元素innerHTML
        :param html: html文本
        :return: None
        """
        ...

    def value(self, value: str) -> None:
        """设置元素value值
        :param value: value值
        :return: None
        """
        ...


class ChromiumFrameSetter(ChromiumBaseSetter):
    _owner: ChromiumFrame = ...

    def attr(self, name: str, value: str) -> None:
        """设置frame元素attribute属性
        :param name: 属性名
        :param value: 属性值
        :return: None
        """
        ...

    def property(self, name, value) -> None:
        """设置元素property属性
        :param name: 属性名
        :param value: 属性值
        :return: None
        """
        ...

    def style(self, name, value) -> None:
        """设置元素style样式
        :param name: 样式名称
        :param value: 样式值
        :return: None
        """
        ...


class LoadMode(object):
    """用于设置页面加载策略的类"""
    _owner: Union[Chromium, ChromiumBase] = ...

    def __init__(self, owner: Union[Chromium, ChromiumBase]):
        """
        :param owner: ChromiumBase对象
        """
        ...

    def __call__(self, value: Literal['normal', 'eager', 'none']) -> None:
        """设置加载策略
        :param value: 可选 'normal', 'eager', 'none'
        :return: None
        """
        ...

    def normal(self) -> None:
        """设置页面加载策略为normal"""
        ...

    def eager(self) -> None:
        """设置页面加载策略为eager"""
        ...

    def none(self) -> None:
        """设置页面加载策略为none"""
        ...


class PageScrollSetter(object):
    _scroll: PageScroller = ...

    def __init__(self, scroll: PageScroller):
        """
        :param scroll: PageScroller对象
        """
        ...

    def wait_complete(self, on_off: bool = True):
        """设置滚动命令后是否等待完成
        :param on_off: 开或关
        :return: None
        """
        ...

    def smooth(self, on_off: bool = True):
        """设置页面滚动是否平滑滚动
        :param on_off: 开或关
        :return: None
        """
        ...


class WindowSetter(object):
    """用于设置窗口大小的类"""
    _owner: ChromiumBase = ...
    _window_id: str = ...

    def __init__(self, owner: Union[ChromiumTab, ChromiumPage]):
        """
        :param owner: Tab或Page对象
        """
        ...

    def max(self) -> None:
        """窗口最大化"""
        ...

    def mini(self) -> None:
        """窗口最小化"""
        ...

    def full(self) -> None:
        """设置窗口为全屏"""
        ...

    def normal(self) -> None:
        """设置窗口为常规模式"""
        ...

    def size(self, width: int = None, height: int = None) -> None:
        """设置窗口大小
        :param width: 窗口宽度
        :param height: 窗口高度
        :return: None
        """
        ...

    def location(self, x: int = None, y: int = None) -> None:
        """设置窗口在屏幕中的位置，相对左上角坐标
        :param x: 距离顶部距离
        :param y: 距离左边距离
        :return: None
        """
        ...

    def hide(self) -> None:
        """隐藏浏览器窗口，只在Windows系统可用"""
        ...

    def show(self) -> None:
        """显示浏览器窗口，只在Windows系统可用"""
        ...

    def _get_info(self) -> dict:
        """获取窗口位置及大小信息"""
        ...

    def _perform(self, bounds: dict) -> None:
        """执行改变窗口大小操作
        :param bounds: 控制数据
        :return: None
        """
        ...
