# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Any, Union, Tuple, Optional

from requests import Session, Response
from requests.structures import CaseInsensitiveDict

from .._base.base import BasePage
from .._configs.session_options import SessionOptions
from .._elements.session_element import SessionElement
from .._functions.cookies import CookiesList
from .._functions.elements import SessionElementsList
from .._units.setter import SessionPageSetter


class SessionPage(BasePage):
    """SessionPage封装了页面操作的常用功能，使用requests来获取、解析网页"""
    _session_options: Optional[SessionOptions] = ...
    _url: str = ...
    _response: Optional[Response] = ...
    _url_available: bool = ...
    _timeout: float = ...
    retry_times: int = ...
    retry_interval: float = ...
    _set: Optional[SessionPageSetter] = ...
    _encoding: Optional[str] = ...
    _page: SessionPage = ...

    def __init__(self, session_or_options: Union[Session, SessionOptions] = None):
        """
        :param session_or_options: Session对象或SessionOptions对象
        """
        ...

    def _s_set_runtime_settings(self) -> None:
        """设置运行时用到的属性"""
        ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str, SessionElement],
                 index: int = 1,
                 timeout: float = None) -> SessionElement:
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性文本
        """
        ...

    @property
    def title(self) -> str:
        """返回网页title"""
        ...

    @property
    def url(self) -> str:
        """返回当前访问url"""
        ...

    @property
    def _session_url(self) -> str:
        """返回当前访问url"""
        ...

    @property
    def raw_data(self) -> Union[str, bytes]:
        """返回页面原始数据"""
        ...

    @property
    def html(self) -> str:
        """返回页面的html文本"""
        ...

    @property
    def json(self) -> Union[dict, None]:
        """当返回内容是json格式时，返回对应的字典，非json格式时返回None"""
        ...

    @property
    def user_agent(self) -> str:
        """返回user agent"""
        ...

    @property
    def session(self) -> Session:
        """返回Session对象"""
        ...

    @property
    def response(self) -> Response:
        """返回访问url得到的Response对象"""
        ...

    @property
    def encoding(self) -> str:
        """返回设置的编码，s模式专用"""
        ...

    @property
    def set(self) -> SessionPageSetter:
        """返回用于设置的对象"""
        ...

    @property
    def timeout(self) -> float:
        """返回超时设置"""
        ...

    def get(self,
            url: Union[Path, str],
            show_errmsg: bool | None = False,
            retry: int | None = None,
            interval: float | None = None,
            timeout: float | None = None,
            params: dict | None = ...,
            data: Union[dict, str, None] = ...,
            json: Union[dict, str, None] = ...,
            headers: Union[dict, str, None] = ...,
            cookies: Any | None = ...,
            files: Any | None = ...,
            auth: Any | None = ...,
            allow_redirects: bool = ...,
            proxies: dict | None = ...,
            hooks: Any | None = ...,
            stream: Any | None = ...,
            verify: Any | None = ...,
            cert: Any | None = ...) -> bool:
        """用get方式跳转到url
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
             retry: int | None = None,
             interval: float | None = None,
             timeout: float | None = ...,
             params: dict | None = ...,
             data: Union[dict, str, None] = ...,
             json: Union[dict, str, None] = ...,
             headers: Union[dict, str, None] = ...,
             cookies: Any | None = ...,
             files: Any | None = ...,
             auth: Any | None = ...,
             allow_redirects: bool = ...,
             proxies: dict | None = ...,
             hooks: Any | None = ...,
             stream: Any | None = ...,
             verify: Any | None = ...,
             cert: Any | None = ...) -> bool:
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
        :return: s模式时返回url是否可用，d模式时返回获取到的Response对象
        """
        ...

    def ele(self,
            locator: Union[Tuple[str, str], str, SessionElement],
            index: int = 1,
            timeout: float = None) -> SessionElement:
        """返回页面中符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本
        """
        ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> SessionElementsList:
        """返回页面中所有符合条件的元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本组成的列表
        """
        ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str, SessionElement] = None,
              index: int = 1) -> SessionElement:
        """返回页面中符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :return: SessionElement对象或属性、文本
        """
        ...

    def s_eles(self, locator: Union[Tuple[str, str], str]) -> SessionElementsList:
        """返回页面中符合条件的所有元素、属性或节点文本
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str, SessionElement],
                       timeout: float,
                       index: Optional[int] = 1,
                       relative: bool = True,
                       raise_err: bool = None) -> Union[SessionElement, SessionElementsList]:
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和父类对应
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: SessionElement对象
        """
        ...

    def cookies(self,
                all_domains: bool = False,
                all_info: bool = False) -> CookiesList:
        """返回cookies
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，False则只返回name、value、domain
        :return: cookies组成的列表
        """
        ...

    def close(self) -> None:
        """关闭Session对象"""
        ...

    def _s_connect(self,
                   url: str,
                   mode: str,
                   show_errmsg: bool = False,
                   retry: int = None,
                   interval: float = None,
                   **kwargs) -> bool:
        """执行get或post连接
        :param url: 目标url
        :param mode: 'get' 或 'post'
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        ...

    def _make_response(self,
                       url: str,
                       mode: str = 'get',
                       retry: int = None,
                       interval: float = None,
                       show_errmsg: bool = False,
                       **kwargs) -> Response:
        """生成Response对象
        :param url: 目标url
        :param mode: 'get' 或 'post'
        :param show_errmsg: 是否显示和抛出异常
        :param kwargs: 其它参数
        :return: Response对象
        """
        ...


def check_headers(kwargs: Union[dict, CaseInsensitiveDict],
                  headers: Union[dict, CaseInsensitiveDict],
                  arg: str) -> bool:
    """检查kwargs或headers中是否有arg所示属性
    :param kwargs: 要检查的参数dict
    :param headers: 要检查的headers
    :param arg: 属性名称
    :return: 检查结果
    """
    ...


def set_charset(response: Response) -> Response:
    """设置Response对象的编码
    :param response: Response对象
    :return: Response对象
    """
    ...
