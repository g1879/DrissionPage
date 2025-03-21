# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from http.cookiejar import CookieJar, Cookie
from pathlib import Path
from typing import Any, Union, Tuple, Optional

from requests import Session
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict


class SessionOptions(object):
    """requests的Session对象配置类"""

    ini_path: Optional[str] = ...
    _download_path: str = ...
    _headers: Union[dict, CaseInsensitiveDict, None] = ...
    _cookies: Union[list, RequestsCookieJar, None] = ...
    _auth: Optional[tuple] = ...
    _proxies: Optional[dict] = ...
    _hooks: Optional[dict] = ...
    _params: Union[dict, None] = ...
    _verify: Optional[bool] = ...
    _cert: Union[str, tuple, None] = ...
    _adapters: Optional[list] = ...
    _stream: Optional[bool] = ...
    _trust_env: Optional[bool] = ...
    _max_redirects: Optional[int] = ...
    _timeout: float = ...
    _del_set: set = ...
    _retry_times: int = ...
    _retry_interval: float = ...

    def __init__(self,
                 read_file: [bool, None] = True,
                 ini_path: Union[str, Path] = None):
        """
        :param read_file: 是否从文件读取配置
        :param ini_path: ini文件路径
        """
        ...

    @property
    def download_path(self) -> str:
        """返回默认下载路径属性信息"""
        ...

    def set_download_path(self, path: Union[str, Path]) -> SessionOptions:
        """设置默认下载路径
        :param path: 下载路径
        :return: 返回当前对象
        """
        ...

    @property
    def timeout(self) -> float:
        """返回timeout属性信息"""
        ...

    def set_timeout(self, second: float) -> SessionOptions:
        """设置超时信息
        :param second: 秒数
        :return: 返回当前对象
        """
        ...

    @property
    def proxies(self) -> dict:
        """返回proxies设置信息"""
        ...

    def set_proxies(self, http: Union[str, None], https: Union[str, None] = None) -> SessionOptions:
        """设置proxies参数
        :param http: http代理地址
        :param https: https代理地址
        :return: 返回当前对象
        """
        ...

    @property
    def retry_times(self) -> int:
        """返回连接失败时的重试次数"""
        ...

    @property
    def retry_interval(self) -> float:
        """返回连接失败时的重试间隔（秒）"""
        ...

    def set_retry(self, times: int = None, interval: float = None) -> SessionOptions:
        """设置连接失败时的重试操作
        :param times: 重试次数
        :param interval: 重试间隔
        :return: 当前对象
        """
        ...

    @property
    def headers(self) -> dict:
        """返回headers设置信息"""
        ...

    def set_headers(self, headers: Union[dict, str, None]) -> SessionOptions:
        """设置headers参数
        :param headers: 参数值，传入None可在ini文件标记删除
        :return: 返回当前对象
        """
        ...

    def set_a_header(self, name: str, value: str) -> SessionOptions:
        """设置headers中一个项
        :param name: 设置名称
        :param value: 设置值
        :return: 返回当前对象
        """
        ...

    def remove_a_header(self, name: str) -> SessionOptions:
        """从headers中删除一个设置
        :param name: 要删除的设置
        :return: 返回当前对象
        """
        ...

    def clear_headers(self) -> SessionOptions:
        """清空已设置的header参数"""
        ...

    @property
    def cookies(self) -> list:
        """以list形式返回cookies"""
        ...

    def set_cookies(self, cookies: Union[Cookie, CookieJar, list, tuple, str, dict, None]) -> SessionOptions:
        """设置一个或多个cookies信息
        :param cookies: cookies，可为Cookie, CookieJar, list, tuple, str, dict，传入None可在ini文件标记删除
        :return: 返回当前对象
        """
        ...

    @property
    def auth(self) -> Union[Tuple[str, str], HTTPBasicAuth]:
        """返回认证设置信息"""
        ...

    def set_auth(self, auth: Union[Tuple[str, str], HTTPBasicAuth, None]) -> SessionOptions:
        """设置认证元组或对象
        :param auth: 认证元组或对象
        :return: 返回当前对象
        """
        ...

    @property
    def hooks(self) -> dict:
        """返回回调方法"""
        ...

    def set_hooks(self, hooks: Union[dict, None]) -> SessionOptions:
        """设置回调方法
        :param hooks: 回调方法
        :return: 返回当前对象
        """
        ...

    @property
    def params(self) -> dict:
        """返回连接参数设置信息"""
        ...

    def set_params(self, params: Union[dict, None]) -> SessionOptions:
        """设置查询参数字典
        :param params: 查询参数字典
        :return: 返回当前对象
        """
        ...

    @property
    def verify(self) -> bool:
        """返回是否验证SSL证书设置"""
        ...

    def set_verify(self, on_off: Union[bool, None]) -> SessionOptions:
        """设置是否验证SSL证书
        :param on_off: 是否验证 SSL 证书
        :return: 返回当前对象
        """
        ...

    @property
    def cert(self) -> Union[str, tuple]:
        """返回SSL证书设置信息"""
        ...

    def set_cert(self, cert: Union[str, Tuple[str, str], None]) -> SessionOptions:
        """SSL客户端证书文件的路径(.pem格式)，或('cert', 'key')元组
        :param cert: 证书路径或元组
        :return: 返回当前对象
        """
        ...

    @property
    def adapters(self) -> list:
        """返回适配器设置信息"""
        ...

    def add_adapter(self, url: str, adapter: HTTPAdapter) -> SessionOptions:
        """添加适配器
        :param url: 适配器对应url
        :param adapter: 适配器对象
        :return: 返回当前对象
        """
        ...

    @property
    def stream(self) -> bool:
        """返回是否使用流式响应内容设置信息"""
        ...

    def set_stream(self, on_off: Union[bool, None]) -> SessionOptions:
        """设置是否使用流式响应内容
        :param on_off: 是否使用流式响应内容
        :return: 返回当前对象
        """
        ...

    @property
    def trust_env(self) -> bool:
        """返回是否信任环境设置信息"""
        ...

    def set_trust_env(self, on_off: Union[bool, None]) -> SessionOptions:
        """设置是否信任环境
        :param on_off: 是否信任环境
        :return: 返回当前对象
        """
        ...

    @property
    def max_redirects(self) -> int:
        """返回最大重定向次数"""
        ...

    def set_max_redirects(self, times: Union[int, None]) -> SessionOptions:
        """设置最大重定向次数
        :param times: 最大重定向次数
        :return: 返回当前对象
        """
        ...

    def _sets(self, arg: str, val: Any) -> None:
        """给属性赋值或标记删除
        :param arg: 属性名称
        :param val: 参数值
        :return: None
        """
        ...

    def save(self, path: str = None) -> str:
        """保存设置到文件
        :param path: ini文件的路径，传入 'default' 保存到默认ini文件
        :return: 保存文件的绝对路径
        """
        ...

    def save_to_default(self) -> str:
        """保存当前配置到默认ini文件"""
        ...

    def as_dict(self) -> dict:
        """以字典形式返回本对象"""
        ...

    def make_session(self) -> Tuple[Session, Optional[CaseInsensitiveDict]]:
        """根据内在的配置生成Session对象，headers从对象中分离"""
        ...

    def from_session(self, session: Session, headers: CaseInsensitiveDict = None) -> SessionOptions:
        """从Session对象中读取配置
        :param session: Session对象
        :param headers: headers
        :return: 当前对象
        """
        ...


def session_options_to_dict(options: Union[dict, SessionOptions, None]) -> Union[dict, None]:
    """把session配置对象转换为字典
    :param options: session配置对象或字典
    :return: 配置字典
    """
    ...
