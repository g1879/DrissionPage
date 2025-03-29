# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from http.cookiejar import CookieJar
from typing import Union, Tuple, List, Any, Optional, Literal

from requests import Session, Response

from .chromium_frame import ChromiumFrame
from .chromium_page import ChromiumPage
from .mix_tab import MixTab
from .session_page import SessionPage
from .._base.base import BasePage
from .._configs.chromium_options import ChromiumOptions
from .._configs.session_options import SessionOptions
from .._elements.chromium_element import ChromiumElement
from .._elements.session_element import SessionElement
from .._functions.cookies import CookiesList
from .._functions.elements import SessionElementsList, ChromiumElementsList
from .._units.setter import WebPageSetter
from .._units.waiter import WebPageWaiter


class WebPage(SessionPage, ChromiumPage, BasePage):
    """整合浏览器和request的页面类"""
    _d_mode: bool = ...
    _set: WebPageSetter = ...
    _has_driver: Optional[bool] = ...
    _has_session: Optional[bool] = ...
    _session_options: Union[SessionOptions, None] = ...
    _chromium_options: Union[ChromiumOptions, None] = ...

    def __init__(self,
                 mode: str = 'd',
                 chromium_options: Union[ChromiumOptions, bool] = None,
                 session_or_options: Union[Session, SessionOptions, bool] = None) -> None:
        """初始化函数
        :param mode: 'd' 或 's'，即driver模式和session模式
        :param chromium_options: ChromiumOptions对象，传入None时从默认ini文件读取，传入False时不读取ini文件，使用默认配置
        :param session_or_options: Session对象或SessionOptions对象，传入None时从默认ini文件读取，传入False时不读取ini文件，使用默认配置
        """
        ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
                 index: int = 1,
                 timeout: float = None) -> Union[ChromiumElement, SessionElement]:
        """在内部查找元素
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 超时时间（秒）
        :return: 子元素对象
        """
        ...

    @property
    def latest_tab(self) -> Union[MixTab, WebPage, str]:
        """返回最新的标签页，最新标签页指最后创建或最后被激活的
        当Settings.singleton_tab_obj==True时返回Tab对象，否则返回tab id"""
        ...

    @property
    def set(self) -> WebPageSetter:
        """返回用于设置的对象"""
        ...

    @property
    def wait(self) -> WebPageWaiter:
        """返回用于等待的对象"""
        ...

    @property
    def url(self) -> Union[str, None]:
        """返回浏览器当前url"""
        ...

    @property
    def _browser_url(self) -> Union[str, None]:
        """返回浏览器当前url"""
        ...

    @property
    def title(self) -> str:
        """返回当前页面title"""
        ...

    @property
    def raw_data(self) -> Union[str, bytes]:
        """返回页码原始数据数据"""
        ...

    @property
    def html(self) -> str:
        """返回页面html文本"""
        ...

    @property
    def json(self) -> dict:
        """当返回内容是json格式时，返回对应的字典"""
        ...

    @property
    def response(self) -> Response:
        """返回 s 模式获取到的 Response 对象，切换到 s 模式"""
        ...

    @property
    def mode(self) -> Literal['s', 'd']:
        """返回当前模式，'s'或'd' """
        ...

    @property
    def user_agent(self) -> str:
        """返回user agent"""
        ...

    @property
    def session(self) -> Session:
        """返回Session对象，如未初始化则按配置信息创建"""
        ...

    @property
    def _session_url(self) -> str:
        """返回 session 保存的url"""
        ...

    @property
    def timeout(self) -> float:
        """返回通用timeout设置"""
        ...

    def get(self,
            url: str,
            show_errmsg: bool = False,
            retry: Optional[int] = None,
            interval: Optional[float] = None,
            timeout: Optional[float] = None,
            params: Optional[dict] = None,
            data: Union[dict, str, None] = None,
            json: Union[dict, str, None] = None,
            headers: Optional[dict] = None,
            cookies: Union[CookieJar, dict] = None,
            files: Optional[Any] = None,
            auth: Optional[Any] = None,
            allow_redirects: bool = True,
            proxies: Optional[dict] = None,
            hooks: Optional[Any] = None,
            stream: bool = None,
            verify: Union[bool, str] = None,
            cert: [str, Tuple[str, str]] = None) -> Union[bool, None]:
        """跳转到一个url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param timeout: 连接超时时间
        :param params: url中的参数
        :param data: 携带的数据
        :param json: 要发送的 JSON 数据，会自动设置 Content-Type 为 application/json
        :param headers: 请求头
        :param cookies: cookies信息
        :param files: 要上传的文件，可以是一个字典，其中键是文件名，值是文件对象或文件路径
        :param auth: 身份认证信息
        :param allow_redirects: 是否允许重定向
        :param proxies: 代理信息
        :param hooks: 回调方法
        :param stream: 是否使用流式传输
        :param verify: 是否验证 SSL 证书
        :param cert: SSL客户端证书文件的路径(.pem格式)，或('cert', 'key')元组
        :return: s模式时返回url是否可用，d模式时返回获取到的Response对象
        """
        ...

    def post(self,
             url: str,
             show_errmsg: bool = False,
             retry: Optional[int] = None,
             interval: Optional[float] = None,
             timeout: Optional[float] = None,
             params: Optional[dict] = None,
             data: Union[dict, str, None] = None,
             json: Union[dict, str, None] = None,
             headers: Optional[dict] = None,
             cookies: Union[CookieJar, dict] = None,
             files: Optional[Any] = None,
             auth: Optional[Any] = None,
             allow_redirects: bool = True,
             proxies: Optional[dict] = None,
             hooks: Optional[Any] = None,
             stream: bool = None,
             verify: Union[bool, str] = None,
             cert: [str, Tuple[str, str]] = None) -> Response:
        """用post方式跳转到url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param timeout: 连接超时时间
        :param params: url中的参数
        :param data: 携带的数据
        :param json: 要发送的 JSON 数据，会自动设置 Content-Type 为 application/json
        :param headers: 请求头
        :param cookies: cookies信息
        :param files: 要上传的文件，可以是一个字典，其中键是文件名，值是文件对象或文件路径
        :param auth: 身份认证信息
        :param allow_redirects: 是否允许重定向
        :param proxies: 代理信息
        :param hooks: 回调方法
        :param stream: 是否使用流式传输
        :param verify: 是否验证 SSL 证书
        :param cert: SSL客户端证书文件的路径(.pem格式)，或('cert', 'key')元组
        :return: 获取到的Response对象
        """
        ...

    def ele(self,
            locator: Union[Tuple[str, str], str, ChromiumElement, SessionElement],
            index: int = 1,
            timeout: float = None) -> Union[ChromiumElement, SessionElement]:
        """返回第一个符合条件的元素、属性或节点文本
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与页面等待时间一致
        :return: 元素对象或属性、文本节点文本
        """
        ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> Union[ChromiumElementsList, SessionElementsList]:
        """返回页面中所有符合条件的元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与页面等待时间一致
        :return: 元素对象或属性、文本组成的列表
        """
        ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str] = None,
              index: int = 1,
              timeout: float = None) -> SessionElement:
        """查找第一个符合条件的元素以SessionElement形式返回，d模式处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与页面等待时间一致
        :return: SessionElement对象或属性、文本
        """
        ...

    def s_eles(self, locator: Union[Tuple[str, str], str], timeout: float = None) -> SessionElementsList:
        """查找所有符合条件的元素以SessionElement形式返回，d模式处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与页面等待时间一致
        :return: SessionElement对象或属性、文本组成的列表
        """
        ...

    def change_mode(self,
                    mode: str = None,
                    go: bool = True,
                    copy_cookies: bool = True) -> None:
        """切换模式，接收's'或'd'，除此以外的字符串会切换为 d 模式
        如copy_cookies为True，切换时会把当前模式的cookies复制到目标模式
        切换后，如果go是True，调用相应的get函数使访问的页面同步
        :param mode: 模式字符串
        :param go: 是否跳转到原模式的url
        :param copy_cookies: 是否复制cookies到目标模式
        :return: None
        """
        ...

    def cookies_to_session(self, copy_user_agent: bool = True) -> None:
        """把driver对象的cookies复制到session对象
        :param copy_user_agent: 是否复制ua信息
        :return: None
        """
        ...

    def cookies_to_browser(self) -> None:
        """把session对象的cookies复制到浏览器"""
        ...

    def cookies(self,
                all_domains: bool = False,
                all_info: bool = False) -> CookiesList:
        """返回cookies
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，False则只返回name、value、domain
        :return: cookies信息
        """
        ...

    def get_tab(self,
                id_or_num: Union[str, MixTab, int] = None,
                title: str = None,
                url: str = None,
                tab_type: Union[str, list, tuple] = 'page',
                as_id: bool = False) -> Union[MixTab, str, None]:
        """获取一个标签页对象，id_or_num不为None时，后面几个参数无效
        :param id_or_num: 要获取的标签页id或序号，序号从1开始，可传入负数获取倒数第几个，不是视觉排列顺序，而是激活顺序
        :param title: 要匹配title的文本，模糊匹配，为None则匹配所有
        :param url: 要匹配url的文本，模糊匹配，为None则匹配所有
        :param tab_type: tab类型，可用列表输入多个，如 'page', 'iframe' 等，为None则匹配所有
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: MixTab对象
        """
        ...

    def get_tabs(self,
                 title: str = None,
                 url: str = None,
                 tab_type: Union[str, list, tuple] = 'page',
                 as_id: bool = False) -> Union[List[MixTab], List[str]]:
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
                new_context: bool = False) -> MixTab:
        """新建一个标签页
        :param url: 新标签页跳转到的网址
        :param new_window: 是否在新窗口打开标签页
        :param background: 是否不激活新标签页，如new_window为True则无效
        :param new_context: 是否创建新的上下文
        :return: 新标签页对象
        """
        ...

    def close_driver(self) -> None:
        """关闭driver及浏览器"""
        ...

    def close_session(self) -> None:
        """关闭session"""
        ...

    def close(self) -> None:
        """关闭标签页和Session"""
        ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str, ChromiumElement, SessionElement, ChromiumFrame],
                       timeout: float,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = None) -> Union[
        ChromiumElement, SessionElement, ChromiumFrame, SessionElementsList, ChromiumElementsList]:
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），d模式专用
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: MixTab用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: 元素对象或属性、文本节点文本
        """
        ...

    def quit(self,
             timeout: float = 5,
             force: bool = True,
             del_data: bool = False) -> None:
        """关闭浏览器和Session
        :param timeout: 等待浏览器关闭超时时间（秒）
        :param force: 关闭超时是否强制终止进程
        :param del_data: 是否删除用户文件夹
        :return: None
        """
        ...
