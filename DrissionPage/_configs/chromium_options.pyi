# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Any, Literal, Optional, Tuple


class ChromiumOptions(object):
    ini_path: Optional[str] = ...
    _driver_path: str = ...
    _user_data_path: Optional[str] = ...
    _download_path: str = ...
    _tmp_path: str = ...
    _arguments: list = ...
    _browser_path: str = ...
    _user: str = ...
    _load_mode: str = ...
    _timeouts: dict = ...
    _proxy: str = ...
    _address: str = ...
    _extensions: list = ...
    _prefs: dict = ...
    _flags: dict = ...
    _prefs_to_del: list = ...
    _new_env: bool = ...
    clear_file_flags: bool = ...
    _auto_port: Union[Tuple[int, int], False] = ...
    _system_user_path: bool = ...
    _existing_only: bool = ...
    _retry_times: int = ...
    _retry_interval: float = ...
    _is_headless: bool = ...
    _ua_set: bool = ...

    def __init__(self,
                 read_file: [bool, None] = True,
                 ini_path: Union[str, Path] = None):
        """
        :param read_file: 是否从默认ini文件中读取配置信息
        :param ini_path: ini文件路径，为None则读取默认ini文件
        """
        ...

    @property
    def download_path(self) -> str:
        """默认下载路径文件路径"""
        ...

    @property
    def browser_path(self) -> str:
        """浏览器启动文件路径"""
        ...

    @property
    def user_data_path(self) -> str:
        """返回用户数据文件夹路径"""
        ...

    @property
    def tmp_path(self) -> Optional[str]:
        """返回临时文件夹路径"""
        ...

    @property
    def user(self) -> str:
        """返回用户配置文件夹名称"""
        ...

    @property
    def load_mode(self) -> str:
        """返回页面加载策略，'normal', 'eager', 'none'"""
        ...

    @property
    def timeouts(self) -> dict:
        """返回timeouts设置"""
        ...

    @property
    def proxy(self) -> str:
        """返回代理设置"""
        ...

    @property
    def address(self) -> str:
        """返回浏览器地址，ip:port"""
        ...

    @property
    def arguments(self) -> list:
        """返回浏览器命令行设置列表"""
        ...

    @property
    def extensions(self) -> list:
        """以list形式返回要加载的插件路径"""
        ...

    @property
    def preferences(self) -> dict:
        """返回用户首选项配置"""
        ...

    @property
    def flags(self) -> dict:
        """返回实验项配置"""
        ...

    @property
    def system_user_path(self) -> bool:
        """返回是否使用系统安装的浏览器所使用的用户数据文件夹"""
        ...

    @property
    def is_existing_only(self) -> bool:
        """返回是否只接管现有浏览器方式"""
        ...

    @property
    def is_auto_port(self) -> Union[bool, Tuple[int, int]]:
        """返回是否使用自动端口和用户文件，如指定范围则返回范围tuple"""
        ...

    @property
    def retry_times(self) -> int:
        """返回连接失败时的重试次数"""
        ...

    @property
    def retry_interval(self) -> float:
        """返回连接失败时的重试间隔（秒）"""
        ...

    @property
    def is_headless(self) -> bool:
        """返回是否无头模式"""
        ...

    def set_retry(self, times: int = None, interval: float = None) -> ChromiumOptions:
        """设置连接失败时的重试操作
        :param times: 重试次数
        :param interval: 重试间隔
        :return: 当前对象
        """
        ...

    def set_argument(self, arg: str, value: Union[str, None, bool] = None) -> ChromiumOptions:
        """设置浏览器配置的argument属性
        :param arg: 属性名
        :param value: 属性值，有值的属性传入值，没有的传入None，如传入False，删除该项
        :return: 当前对象
        """
        ...

    def remove_argument(self, value: str) -> ChromiumOptions:
        """移除一个argument项
        :param value: 设置项名，有值的设置项传入设置名称即可
        :return: 当前对象
        """
        ...

    def add_extension(self, path: Union[str, Path]) -> ChromiumOptions:
        """添加插件
        :param path: 插件路径，可指向文件夹
        :return: 当前对象
        """
        ...

    def remove_extensions(self) -> ChromiumOptions:
        """移除所有插件
        :return: 当前对象
        """
        ...

    def set_pref(self, arg: str, value: Any) -> ChromiumOptions:
        """设置Preferences文件中的用户设置项
        :param arg: 设置项名称
        :param value: 设置项值
        :return: 当前对象
        """
        ...

    def remove_pref(self, arg: str) -> ChromiumOptions:
        """删除用户首选项设置，不能删除已设置到文件中的项
        :param arg: 设置项名称
        :return: 当前对象
        """
        ...

    def remove_pref_from_file(self, arg: str) -> ChromiumOptions:
        """删除用户配置文件中已设置的项
        :param arg: 设置项名称
        :return: 当前对象
        """
        ...

    def set_flag(self, flag: str, value: Union[int, str, bool] = None) -> ChromiumOptions:
        """设置实验项
        :param flag: 设置项名称
        :param value: 设置项的值，为False则删除该项
        :return: 当前对象
        """
        ...

    def clear_flags_in_file(self) -> ChromiumOptions:
        """删除浏览器配置文件中已设置的实验项"""
        ...

    def clear_flags(self) -> ChromiumOptions:
        """清空本对象已设置的flag参数"""
        ...

    def clear_arguments(self) -> ChromiumOptions:
        """清空本对象已设置的argument参数"""
        ...

    def clear_prefs(self) -> ChromiumOptions:
        """清空本对象已设置的pref参数"""
        ...

    def set_timeouts(self,
                     base: float = None,
                     page_load: float = None,
                     script: float = None) -> ChromiumOptions:
        """设置超时时间，单位为秒
        :param base: 默认超时时间
        :param page_load: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: 当前对象
        """
        ...

    def set_user(self, user: str = 'Default') -> ChromiumOptions:
        """设置使用哪个用户配置文件夹
        :param user: 用户文件夹名称
        :return: 当前对象
        """
        ...

    def headless(self, on_off: bool = True) -> ChromiumOptions:
        """设置是否隐藏浏览器界面
        :param on_off: 开或关
        :return: 当前对象
        """
        ...

    def no_imgs(self, on_off: bool = True) -> ChromiumOptions:
        """设置是否加载图片
        :param on_off: 开或关
        :return: 当前对象
        """
        ...

    def no_js(self, on_off: bool = True) -> ChromiumOptions:
        """设置是否禁用js
        :param on_off: 开或关
        :return: 当前对象
        """
        ...

    def mute(self, on_off: bool = True) -> ChromiumOptions:
        """设置是否静音
        :param on_off: 开或关
        :return: 当前对象
        """
        ...

    def incognito(self, on_off: bool = True) -> ChromiumOptions:
        """设置是否使用无痕模式启动
        :param on_off: 开或关
        :return: 当前对象
        """
        ...

    def new_env(self, on_off: bool = True) -> ChromiumOptions:
        """设置是否使用全新浏览器环境
        :param on_off: 开或关
        :return: 当前对象
        """
        ...

    def ignore_certificate_errors(self, on_off=True) -> ChromiumOptions:
        """设置是否忽略证书错误
        :param on_off: 开或关
        :return: 当前对象
        """
        ...

    def set_user_agent(self, user_agent: str) -> ChromiumOptions:
        """设置user agent
        :param user_agent: user agent文本
        :return: 当前对象
        """
        ...

    def set_proxy(self, proxy: str) -> ChromiumOptions:
        """设置代理
        :param proxy: 代理url和端口
        :return: 当前对象
        """
        ...

    def set_load_mode(self, value: Literal['normal', 'eager', 'none']) -> ChromiumOptions:
        """设置load_mode，可接收 'normal', 'eager', 'none'
        normal：默认情况下使用, 等待所有资源下载完成
        eager：DOM访问已准备就绪, 但其他资源 (如图像) 可能仍在加载中
        none：完全不阻塞
        :param value: 可接收 'normal', 'eager', 'none'
        :return: 当前对象
        """
        ...

    def set_local_port(self, port: Union[str, int]) -> ChromiumOptions:
        """设置本地启动端口
        :param port: 端口号
        :return: 当前对象
        """
        ...

    def set_address(self, address: str) -> ChromiumOptions:
        """设置浏览器地址，格式'ip:port'
        :param address: 浏览器地址
        :return: 当前对象
        """
        ...

    def set_browser_path(self, path: Union[str, Path]) -> ChromiumOptions:
        """设置浏览器可执行文件路径
        :param path: 浏览器路径
        :return: 当前对象
        """
        ...

    def set_download_path(self, path: Union[str, Path]) -> ChromiumOptions:
        """设置下载文件保存路径
        :param path: 下载路径
        :return: 当前对象
        """
        ...

    def set_tmp_path(self, path: Union[str, Path]) -> ChromiumOptions:
        """设置临时文件文件保存路径
        :param path: 下载路径
        :return: 当前对象
        """
        ...

    def set_user_data_path(self, path: Union[str, Path]) -> ChromiumOptions:
        """设置用户文件夹路径
        :param path: 用户文件夹路径
        :return: 当前对象
        """
        ...

    def set_cache_path(self, path: Union[str, Path]) -> ChromiumOptions:
        """设置缓存路径
        :param path: 缓存路径
        :return: 当前对象
        """
        ...

    def set_paths(self, browser_path: Union[str, Path] = None, local_port: Union[int, str] = None,
                  address: str = None, download_path: Union[str, Path] = None, user_data_path: Union[str, Path] = None,
                  cache_path: Union[str, Path] = None) -> ChromiumOptions: ...

    def use_system_user_path(self, on_off: bool = True) -> ChromiumOptions:
        """设置是否使用系统安装的浏览器默认用户文件夹
        :param on_off: 开或关
        :return: 当前对象
        """
        ...

    def auto_port(self,
                  on_off: bool = True,
                  scope: Tuple[int, int] = None) -> ChromiumOptions:
        """自动获取可用端口
        :param on_off: 是否开启自动获取端口号
        :param scope: 指定端口范围，不含最后的数字，为None则使用[9600-59600)
        :return: 当前对象
        """
        ...

    def existing_only(self, on_off: bool = True) -> ChromiumOptions:
        """设置只接管已有浏览器，不自动启动新的
        :param on_off: 是否开启自动获取端口号
        :return: 当前对象
        """
        ...

    def save(self, path: Union[str, Path] = None) -> str:
        """保存设置到文件
        :param path: ini文件的路径， None 保存到当前读取的配置文件，传入 'default' 保存到默认ini文件
        :return: 保存文件的绝对路径
        """
        ...

    def save_to_default(self) -> str:
        """保存当前配置到默认ini文件"""
        ...
