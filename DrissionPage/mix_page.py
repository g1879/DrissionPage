# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   mix_page.py
"""
from typing import Union, List

from requests import Response
from requests_html import HTMLSession, Element
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

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
        """初始化函数                                                              \n
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
            raise ValueError("Argument mode can only be 'd' or 's'.")

    @property
    def url(self) -> Union[str, None]:
        """返回当前url"""
        if self._mode == 'd':
            if not self._driver or not self._drission.driver.current_url.startswith('http'):
                return None
            else:
                return self._drission.driver.current_url
        elif self._mode == 's':
            return self.session_url

    @property
    def session_url(self) -> str:
        """返回session访问的url"""
        return self._response.url if self._response else None

    @property
    def mode(self) -> str:
        """返回当前模式                \n
        :return: 's' 或 'd'
        """
        return self._mode

    def change_mode(self, mode: str = None, go: bool = True) -> None:
        """切换模式，接收字符串s或d，除此以外的字符串会切换为d模式  \n
        切换时会把当前模式的cookies复制到目标模式                 \n
        切换后，如果go是True，调用相应的get函数使访问的页面同步    \n
        :param mode: 模式字符串
        :param go: 是否跳转到原模式的url
        """
        if mode == self._mode:
            return
        self._mode = 's' if self._mode == 'd' else 'd'
        if self._mode == 'd':  # s转d
            self._driver = True
            self._url = None if not self._driver else self._drission.driver.current_url
            if self.session_url:
                self.cookies_to_driver(self.session_url)
                if go:
                    self.get(self.session_url)
        elif self._mode == 's':  # d转s
            self._session = True
            self._url = self.session_url
            if self._driver:
                self.cookies_to_session()
                if go and self._drission.driver.current_url.startswith('http'):
                    self.get(self._drission.driver.current_url)

    @property
    def drission(self) -> Drission:
        """返回当前使用的Dirssion对象"""
        return self._drission

    @property
    def driver(self) -> WebDriver:
        """返回driver对象，如没有则创建              \n
        每次访问时切换到d模式，用于独有函数及外部调用
        :return: WebDriver对象
        """
        self.change_mode('d')
        return self._drission.driver

    @property
    def session(self) -> HTMLSession:
        """返回session对象，如没有则创建            \n
        :return: HTMLSession对象
        """
        return self._drission.session

    @property
    def response(self) -> Response:
        """返回response对象，切换到s模式"""
        self.change_mode('s')
        return self._response

    @property
    def cookies(self) -> Union[dict, list]:
        """返回cookies"""
        if self._mode == 's':
            return super().cookies
        elif self._mode == 'd':
            return super(SessionPage, self).cookies

    def cookies_to_session(self, copy_user_agent: bool = False) -> None:
        """从driver复制cookies到session                  \n
        :param copy_user_agent : 是否复制user agent信息
        """
        self._drission.cookies_to_session(copy_user_agent)

    def cookies_to_driver(self, url=None) -> None:
        """从session复制cookies到driver  \n
        chrome需要指定域才能接收cookies   \n
        :param url: 目标域
        :return: None
        """
        u = url or self.session_url
        self._drission.cookies_to_driver(u)

    # ----------------重写SessionPage的函数-----------------------

    def post(self, url: str, data: dict = None, go_anyway: bool = False, **kwargs) -> Union[bool, None]:
        """用post方式跳转到url                                 \n
        post前先转换模式，但不跳转
        :param url: 目标url
        :param data: 提交的数据
        :param go_anyway: 若目标url与当前url一致，是否强制跳转
        :param kwargs: 连接参数
        :return: url是否可用
        """
        self.change_mode('s', go=False)
        return super().post(url, data, go_anyway, **kwargs)

    def download(self,
                 file_url: str,
                 goal_path: str = None,
                 rename: str = None,
                 file_exists: str = 'rename',
                 show_msg: bool = False,
                 **kwargs) -> tuple:
        """下载一个文件                                                                      \n
        d模式下下载前先同步cookies                                                            \n
        :param file_url: 文件url
        :param goal_path: 存放路径
        :param rename: 重命名文件，可不写扩展名
        :param file_exists: 若存在同名文件，可选择 'rename', 'overwrite', 'skip' 方式处理
        :param show_msg: 是否显示下载信息
        :param kwargs: 连接参数
        :return: 下载是否成功（bool）和状态信息（成功时信息为文件路径）的元组
        """
        if self.mode == 'd':
            self.cookies_to_session()
        return super().download(file_url, goal_path, rename, file_exists, show_msg, **kwargs)

    # ----------------重写DriverPage的函数-----------------------

    def chrome_downloading(self, download_path: str = None) -> list:
        """返回浏览器下载中的文件列表                             \n
        :param download_path: 下载文件夹路径，默认读取配置信息
        :return: 正在下载的文件列表
        """
        try:
            path = download_path or self._drission.driver_options['experimental_options']['prefs'][
                'download.default_directory']
            if not path:
                raise
        except:
            raise IOError('Download path not found.')
        return super().chrome_downloading(path)

    # ----------------以下为共用函数-----------------------

    def get(self, url: str, go_anyway=False, **kwargs) -> Union[bool, None]:
        """跳转到一个url                                         \n
        跳转前先同步cookies，跳转后判断目标url是否可用
        :param url: 目标url
        :param go_anyway: 若目标url与当前url一致，是否强制跳转
        :param kwargs: 连接参数，s模式专用
        :return: url是否可用
        """
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

    def ele(self,
            loc_or_ele: Union[tuple, str, DriverElement, SessionElement, Element, WebElement],
            mode: str = None,
            timeout: float = None,
            show_errmsg: bool = False) -> Union[DriverElement, SessionElement]:
        """返回页面中符合条件的元素，默认返回第一个                                                          \n
        示例：                                                                                           \n
        - 接收到元素对象时：                                                                              \n
            返回元素对象对象                                                                              \n
        - 用loc元组查找：                                                                                 \n
            ele.ele((By.CLASS_NAME, 'ele_class')) - 返回第一个class为ele_class的子元素                       \n
        - 用查询字符串查找：                                                                               \n
            查找方式：属性、tag name和属性、文本、xpath、css selector                                        \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                          \n
            page.ele('@class:ele_class')                 - 返回第一个class含有ele_class的元素              \n
            page.ele('@name=ele_name')                   - 返回第一个name等于ele_name的元素                \n
            page.ele('@placeholder')                     - 返回第一个带placeholder属性的元素               \n
            page.ele('tag:p')                            - 返回第一个<p>元素                              \n
            page.ele('tag:div@class:ele_class')          - 返回第一个class含有ele_class的div元素           \n
            page.ele('tag:div@class=ele_class')          - 返回第一个class等于ele_class的div元素           \n
            page.ele('tag:div@text():some_text')         - 返回第一个文本含有some_text的div元素             \n
            page.ele('tag:div@text()=some_text')         - 返回第一个文本等于some_text的div元素             \n
            page.ele('text:some_text')                   - 返回第一个文本含有some_text的元素                \n
            page.ele('some_text')                        - 返回第一个文本含有some_text的元素（等价于上一行）  \n
            page.ele('text=some_text')                   - 返回第一个文本等于some_text的元素                \n
            page.ele('xpath://div[@class="ele_class"]')  - 返回第一个符合xpath的元素                        \n
            page.ele('css:div.ele_class')                - 返回第一个符合css selector的元素                 \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param mode: 'single' 或 'all‘，对应查找一个或全部
        :param timeout: 查找元素超时时间，d模式专用
        :param show_errmsg: 出现异常时是否打印信息
        :return: 元素对象，d模式为DriverElement，s模式为SessionElement
        """
        if self._mode == 's':
            return super().ele(loc_or_ele, mode=mode, show_errmsg=show_errmsg)
        elif self._mode == 'd':
            timeout = timeout or self.timeout
            return super(SessionPage, self).ele(loc_or_ele, mode=mode, timeout=timeout, show_errmsg=show_errmsg)

    def eles(self,
             loc_or_str: Union[tuple, str],
             timeout: float = None,
             show_errmsg: bool = False) -> Union[List[DriverElement], List[SessionElement]]:
        """返回页面中所有符合条件的元素                                                                   \n
        示例：                                                                                          \n
        - 用loc元组查找：                                                                                \n
            page.eles((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的元素                     \n
        - 用查询字符串查找：                                                                              \n
            查找方式：属性、tag name和属性、文本、xpath、css selector                                       \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                         \n
            page.eles('@class:ele_class')                 - 返回所有class含有ele_class的元素              \n
            page.eles('@name=ele_name')                   - 返回所有name等于ele_name的元素                \n
            page.eles('@placeholder')                     - 返回所有带placeholder属性的元素               \n
            page.eles('tag:p')                            - 返回所有<p>元素                              \n
            page.eles('tag:div@class:ele_class')          - 返回所有class含有ele_class的div元素           \n
            page.eles('tag:div@class=ele_class')          - 返回所有class等于ele_class的div元素           \n
            page.eles('tag:div@text():some_text')         - 返回所有文本含有some_text的div元素             \n
            page.eles('tag:div@text()=some_text')         - 返回所有文本等于some_text的div元素             \n
            page.eles('text:some_text')                   - 返回所有文本含有some_text的元素                \n
            page.eles('some_text')                        - 返回所有文本含有some_text的元素（等价于上一行）  \n
            page.eles('text=some_text')                   - 返回所有文本等于some_text的元素                \n
            page.eles('xpath://div[@class="ele_class"]')  - 返回所有符合xpath的元素                        \n
            page.eles('css:div.ele_class')                - 返回所有符合css selector的元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，d模式专用
        :param show_errmsg: 出现异常时是否打印信息
        :return: 元素对象组成的列表，d模式下由DriverElement组成，s模式下由SessionElement组成
        """
        if self._mode == 's':
            return super().eles(loc_or_str, show_errmsg)
        elif self._mode == 'd':
            return super(SessionPage, self).eles(loc_or_str, timeout=timeout, show_errmsg=show_errmsg)

    @property
    def html(self) -> str:
        """返回页面html文本"""
        if self._mode == 's':
            return super().html
        elif self._mode == 'd':
            return super(SessionPage, self).html

    @property
    def title(self) -> str:
        """返回网页title"""
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
