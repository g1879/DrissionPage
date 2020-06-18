# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   mix_page.py
"""
from typing import Union, List

from requests import Response
from requests_html import HTMLSession
from selenium.webdriver.chrome.webdriver import WebDriver

from .drission import Drission
from .driver_element import DriverElement
from .driver_page import DriverPage
from .session_element import SessionElement
from .session_page import SessionPage


class Null(object):
    """避免IDE警告未调用超类初始化函数而引入的无用类"""

    def __init__(self):
        pass


class MixPage(Null, SessionPage, DriverPage):
    """MixPage封装了页面操作的常用功能，可在selenium（d模式）和requests（s模式）间无缝切换。
    切换的时候会自动同步cookies，兼顾selenium的易用性和requests的高性能。
    获取信息功能为两种模式共有，操作页面元素功能只有d模式有。调用某种模式独有的功能，会自动切换到该模式。
    这些功能由DriverPage和SessionPage类实现。
    """

    def __init__(self, drission: Union[Drission, str] = None, mode: str = 'd', timeout: float = 10):
        """初始化函数
        :param drission: 整合了driver和session的类，传入's'或'd'时快速配置相应模式
        :param mode: 默认使用selenium的d模式
        """
        super().__init__()
        if drission in ['s', 'd']:
            mode = drission
            drission = None
        self._drission = drission or Drission()
        self._session = None
        self._driver = None
        self._url = None
        self._response = None
        self.timeout = timeout
        self._url_available = None
        self._mode = mode
        if mode == 's':
            self._session = True
        elif mode == 'd':
            self._driver = True
        else:
            raise KeyError("mode must be 'd' or 's'.")

    @property
    def url(self) -> str:
        """根据模式获取当前活动的url"""
        if self._mode == 'd':
            return super(SessionPage, self).url
        elif self._mode == 's':
            return self.session_url

    @property
    def session_url(self) -> str:
        return self._response.url if self._response else None

    @property
    def mode(self) -> str:
        """返回当前模式
        :return: 's'或'd'
        """
        return self._mode

    def change_mode(self, mode: str = None, go: bool = True) -> None:
        """切换模式，接收字符串s或d，除此以外的字符串会切换为d模式
        切换时会把当前模式的cookies复制到目标模式
        切换后，如果go是True，调用相应的get函数使访问的页面同步
        :param mode: 模式字符串
        :param go: 是否跳转到原模式的url
        """
        if mode == self._mode:
            return
        self._mode = 's' if self._mode == 'd' else 'd'
        if self._mode == 'd':  # s转d
            self._url = super(SessionPage, self).url
            if self.session_url:
                self.cookies_to_driver(self.session_url)
            if go:
                self.get(self.session_url)
        elif self._mode == 's':  # d转s
            self._url = self.session_url
            if self._session is None:
                self._session = True
            if self._driver:
                self.cookies_to_session()
            if go:
                self.get(super(SessionPage, self).url)

    @property
    def drission(self) -> Drission:
        """返回当前使用的Dirssion对象"""
        return self._drission

    @property
    def driver(self) -> WebDriver:
        """返回driver对象，如没有则创建
        每次访问时切换到d模式，用于独有函数及外部调用
        :return:selenium的WebDriver对象
        """
        self.change_mode('d')
        return self._drission.driver

    @property
    def session(self) -> HTMLSession:
        """返回session对象，如没有则创建
        :return:requests-html的HTMLSession对象
        """
        return self._drission.session

    @property
    def response(self) -> Response:
        """返回response对象，切换到s模式"""
        self.change_mode('s')
        return self._response

    @property
    def cookies(self) -> Union[dict, list]:
        """返回cookies，根据模式获取"""
        if self._mode == 's':
            return super().cookies
        elif self._mode == 'd':
            return super(SessionPage, self).cookies

    def cookies_to_session(self, copy_user_agent: bool = False) -> None:
        """从driver复制cookies到session
        :param copy_user_agent : 是否复制user agent信息
        """
        self._drission.cookies_to_session(copy_user_agent)

    def cookies_to_driver(self, url=None) -> None:
        """从session复制cookies到driver，chrome需要指定域才能接收cookies"""
        u = url or self.session_url
        self._drission.cookies_to_driver(u)

    # ----------------重写SessionPage的函数-----------------------

    def post(self, url: str, data: dict = None, go_anyway: bool = False, **kwargs) -> Union[bool, None]:
        """post前先转换模式，但不跳转"""
        self.change_mode('s', go=False)
        return super().post(url, data, go_anyway, **kwargs)

    # ----------------重写DriverPage的函数-----------------------

    def chrome_downloading(self, download_path: str = None) -> list:
        """检查浏览器下载情况，返回正在下载的文件列表
        :param download_path: 下载文件夹路径，默认读取配置信息
        :return: 正在下载的文件列表
        """
        try:
            path = download_path or self._drission.driver_options['experimental_options']['prefs'][
                'download.default_directory']
            if not path:
                raise KeyError
        except KeyError:
            raise KeyError('Download path not found.')

        return super().chrome_downloading(path)

    # ----------------以下为共用函数-----------------------

    def get(self, url: str, go_anyway=False, **kwargs) -> Union[bool, None]:
        """跳转到一个url，跳转前先同步cookies，跳转后判断目标url是否可用"""
        if self._mode == 'd':
            if super(SessionPage, self).get(url=url, go_anyway=go_anyway) is None:
                return
            if self.session_url == self.url:
                self._url_available = True if self._response and self._response.ok else False
            else:
                self._url_available = self.check_page()
            return self._url_available
        elif self._mode == 's':
            return None if super().get(url=url, go_anyway=go_anyway, **kwargs) is None else self._url_available

    def ele(self, loc_or_ele: Union[tuple, str, DriverElement, SessionElement], mode: str = None, timeout: float = None,
            show_errmsg: bool = False) -> Union[DriverElement, SessionElement]:
        """查找一个元素，根据模式调用对应的查找函数
        :param loc_or_ele: 页面元素地址
        :param mode: 以某种方式查找元素，可选'single','all','visible'(d模式独有)
        :param timeout: 超时时间
        :param show_errmsg: 是否显示错误信息
        :return: 页面元素对象，s模式下返回Element，d模式下返回WebElement
        """
        if self._mode == 's':
            return super().ele(loc_or_ele, mode=mode, show_errmsg=show_errmsg)
        elif self._mode == 'd':
            timeout = timeout or self.timeout
            # return super(SessionPage, self).ele(loc_or_ele, mode=mode, timeout=timeout, show_errmsg=show_errmsg)
            return DriverPage.ele(self, loc_or_ele, mode=mode, timeout=timeout, show_errmsg=show_errmsg)

    def eles(self, loc_or_str: Union[tuple, str], timeout: float = None, show_errmsg: bool = False) \
            -> List[DriverElement]:
        """查找符合条件的所有元素"""
        if self._mode == 's':
            return super().eles(loc_or_str, show_errmsg)
        elif self._mode == 'd':
            return super(SessionPage, self).eles(loc_or_str, timeout=timeout, show_errmsg=show_errmsg)

    @property
    def html(self) -> str:
        """获取页面HTML"""
        if self._mode == 's':
            return super().html
        elif self._mode == 'd':
            return super(SessionPage, self).html

    @property
    def title(self) -> str:
        """获取页面title"""
        if self._mode == 's':
            return super().title
        elif self._mode == 'd':
            return super(SessionPage, self).title

    def close_driver(self) -> None:
        """关闭driver及浏览器，切换到s模式"""
        self.change_mode('s')
        self._driver = None
        self.drission.close_driver()

    def close_session(self) -> None:
        """关闭session，切换到d模式"""
        self.change_mode('d')
        self._session = None
        self.drission.close_session()
