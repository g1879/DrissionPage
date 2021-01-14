# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   mix_page.py
"""
from typing import Union, List, Tuple

from requests import Response, Session
from requests.cookies import RequestsCookieJar
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .config import DriverOptions, SessionOptions
from .drission import Drission
from .driver_element import DriverElement
from .driver_page import DriverPage
from .session_element import SessionElement
from .session_page import SessionPage


class Null(object):
    """避免IDE发出未调用超类初始化函数的警告，无实际作用"""

    def __init__(self):
        pass


class MixPage(Null, SessionPage, DriverPage):
    """MixPage整合了DriverPage和SessionPage，封装了对页面的操作，
    可在selenium（d模式）和requests（s模式）间无缝切换。
    切换的时候会自动同步cookies。
    获取信息功能为两种模式共有，操作页面元素功能只有d模式有。
    调用某种模式独有的功能，会自动切换到该模式。
    """

    def __init__(self,
                 drission: Union[Drission, str] = None,
                 mode: str = 'd',
                 timeout: float = 10,
                 driver_options: Union[dict, DriverOptions] = None,
                 session_options: Union[dict, SessionOptions] = None):
        """初始化函数                                                                         \n
        :param drission: Drission对象，传入's'或'd'可自动创建Drission对象
        :param mode: 'd' 或 's'，即driver模式和session模式
        :param driver_options: 浏览器设置，没有传入drission参数时会用这个设置新建Drission对象
        :param session_options: requests设置，没有传入drission参数时会用这个设置新建Drission对象
        """
        super().__init__()
        if drission in ('s', 'd', 'S', 'D'):
            mode = drission.lower()
            drission = None

        self._drission = drission or Drission(driver_options, session_options)
        self._url = None
        self._response = None
        self.timeout = timeout
        self._url_available = None
        self._mode = mode

        self.retry_times = 3
        self.retry_interval = 2

        if mode == 's':
            self._driver = None
            self._session = True
        elif mode == 'd':
            self._driver = True
            self._session = None
        else:
            raise ValueError("Argument mode can only be 'd' or 's'.")

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, DriverElement, SessionElement, WebElement],
                 mode: str = 'single',
                 timeout: float = None):
        return self.ele(loc_or_str, mode, timeout)

    @property
    def url(self) -> Union[str, None]:
        """返回当前url"""
        if self._mode == 'd':
            return self._drission.driver.current_url if self._driver else None
        elif self._mode == 's':
            return self._session_url

    @property
    def _session_url(self) -> str:
        """返回session保存的url"""
        return self._response.url if self._response else None

    @property
    def mode(self) -> str:
        """返回当前模式，'s'或'd' """
        return self._mode

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
    def session(self) -> Session:
        """返回Session对象，如没有则创建"""
        return self._drission.session

    @property
    def response(self) -> Response:
        """返回s模式获取到的Response对象，切换到s模式"""
        self.change_mode('s')
        return self._response

    @property
    def cookies(self) -> Union[dict, list]:
        """返回cookies"""
        if self._mode == 's':
            return super().cookies
        elif self._mode == 'd':
            return super(SessionPage, self).cookies

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

    def set_cookies(self, cookies: Union[RequestsCookieJar, list, tuple, str, dict], refresh: bool = True) -> None:
        """设置cookies                                                          \n
        :param cookies: cookies信息，可为CookieJar, list, tuple, str, dict
        :param refresh: 设置cookies后是否刷新页面
        :return: None
        """
        if self._mode == 's':
            self.drission.set_cookies(cookies, set_session=True)
        elif self._mode == 'd':
            self.drission.set_cookies(cookies, set_driver=True)

            if refresh:
                self.refresh()

    def get_cookies(self, as_dict: bool = False, all_domains: bool = False) -> Union[dict, list]:
        """返回cookies                               \n
        :param as_dict: 是否以字典方式返回
        :param all_domains: 是否返回所有域的cookies
        :return: cookies信息
        """
        if self._mode == 's':
            return super().get_cookies(as_dict, all_domains)
        elif self._mode == 'd':
            return super(SessionPage, self).get_cookies(as_dict)

    def change_mode(self, mode: str = None, go: bool = True) -> None:
        """切换模式，接收's'或'd'，除此以外的字符串会切换为d模式   \n
        切换时会把当前模式的cookies复制到目标模式                 \n
        切换后，如果go是True，调用相应的get函数使访问的页面同步    \n
        :param mode: 模式字符串
        :param go: 是否跳转到原模式的url
        """
        if mode is not None and mode.lower() == self._mode:
            return

        self._mode = 's' if self._mode == 'd' else 'd'

        # s模式转d模式
        if self._mode == 'd':
            self._driver = True
            self._url = None if not self._driver else self._drission.driver.current_url

            if self._session_url:
                self.cookies_to_driver(self._session_url)

                if go:
                    self.get(self._session_url)

        # d模式转s模式
        elif self._mode == 's':
            self._session = True
            self._url = self._session_url

            if self._driver:
                self.cookies_to_session()

                if go and self._drission.driver.current_url.startswith('http'):
                    self.get(self._drission.driver.current_url)

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
        url = url or self._session_url
        self._drission.cookies_to_driver(url)

    def check_page(self, by_requests: bool = False) -> Union[bool, None]:
        """d模式时检查网页是否符合预期                \n
        默认由response状态检查，可重载实现针对性检查   \n
        :param by_requests: 是否用内置response检查
        :return: bool或None，None代表不知道结果
        """
        if self._session_url and self._session_url == self.url:
            return self._response.ok

        # 使用requests访问url并判断可用性
        if by_requests:
            self.cookies_to_session()
            r = self._make_response(self.url, **{'timeout': 3})[0]
            return r.ok if r else False

    # ----------------重写SessionPage的函数-----------------------

    def post(self,
             url: str,
             data: dict = None,
             go_anyway: bool = False,
             show_errmsg: bool = False,
             retry: int = None,
             interval: float = None,
             **kwargs) -> Union[bool, None]:
        """用post方式跳转到url，会切换到s模式                        \n
        :param url: 目标url
        :param data: post方式时提交的数据
        :param go_anyway: 若目标url与当前url一致，是否强制跳转
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        self.change_mode('s', go=False)
        return super().post(url, data, go_anyway, show_errmsg, retry, interval, **kwargs)

    def download(self,
                 file_url: str,
                 goal_path: str = None,
                 rename: str = None,
                 file_exists: str = 'rename',
                 post_data: dict = None,
                 show_msg: bool = False,
                 show_errmsg: bool = False,
                 **kwargs) -> Tuple[bool, str]:
        """下载一个文件                                                                      \n
        d模式下下载前先同步cookies                                                            \n
        :param file_url: 文件url
        :param goal_path: 存放路径，默认为ini文件中指定的临时文件夹
        :param rename: 重命名文件，可不写扩展名
        :param file_exists: 若存在同名文件，可选择 'rename', 'overwrite', 'skip' 方式处理
        :param post_data: post方式的数据
        :param show_msg: 是否显示下载信息
        :param show_errmsg: 是否显示和抛出异常
        :param kwargs: 连接参数
        :return: 下载是否成功（bool）和状态信息（成功时信息为文件路径）的元组
        """
        if self.mode == 'd':
            self.cookies_to_session()
        return super().download(file_url, goal_path, rename, file_exists, post_data, show_msg, show_errmsg, **kwargs)

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
    def _try_to_connect(self,
                        to_url: str,
                        times: int = 0,
                        interval: float = 1,
                        mode: str = 'get',
                        data: dict = None,
                        show_errmsg: bool = False,
                        **kwargs):
        """尝试连接，重试若干次                            \n
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :param kwargs: 连接参数
        :return: s模式为Response对象，d模式为bool
        """
        if self._mode == 'd':
            return super(SessionPage, self)._try_to_connect(to_url, times, interval, show_errmsg)
        elif self._mode == 's':
            return super()._try_to_connect(to_url, times, interval, mode, data, show_errmsg, **kwargs)

    def get(self,
            url: str,
            go_anyway=False,
            show_errmsg: bool = False,
            retry: int = None,
            interval: float = None,
            **kwargs) -> Union[bool, None]:
        """跳转到一个url                                         \n
        跳转前先同步cookies，跳转后判断目标url是否可用
        :param url: 目标url
        :param go_anyway: 若目标url与当前url一致，是否强制跳转
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数，s模式专用
        :return: url是否可用
        """
        if self._mode == 'd':
            return super(SessionPage, self).get(url, go_anyway, show_errmsg, retry, interval)
        elif self._mode == 's':
            return super().get(url, go_anyway, show_errmsg, retry, interval, **kwargs)

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, DriverElement, SessionElement, WebElement],
            mode: str = None,
            timeout: float = None) \
            -> Union[DriverElement, SessionElement, str, List[SessionElement], List[DriverElement]]:
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个                                               \n
        示例：                                                                                             \n
        - 接收到元素对象时：                                                                                 \n
            返回元素对象对象                                                                                 \n
        - 用loc元组查找：                                                                                    \n
            ele.ele((By.CLASS_NAME, 'ele_class'))        - 返回第一个class为ele_class的子元素                 \n
        - 用查询字符串查找：                                                                                  \n
            查找方式：属性、tag name和属性、文本、xpath、css selector、id、class                                \n
            @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串              \n
            page.ele('.ele_class')                       - 返回第一个 class 为 ele_class 的元素               \n
            page.ele('.:ele_class')                      - 返回第一个 class 中含有 ele_class 的元素            \n
            page.ele('#ele_id')                          - 返回第一个 id 为 ele_id 的元素                     \n
            page.ele('#:ele_id')                         - 返回第一个 id 中含有 ele_id 的元素                  \n
            page.ele('@class:ele_class')                 - 返回第一个class含有ele_class的元素                  \n
            page.ele('@name=ele_name')                   - 返回第一个name等于ele_name的元素                    \n
            page.ele('@placeholder')                     - 返回第一个带placeholder属性的元素                   \n
            page.ele('tag:p')                            - 返回第一个<p>元素                                  \n
            page.ele('tag:div@class:ele_class')          - 返回第一个class含有ele_class的div元素               \n
            page.ele('tag:div@class=ele_class')          - 返回第一个class等于ele_class的div元素               \n
            page.ele('tag:div@text():some_text')         - 返回第一个文本含有some_text的div元素                 \n
            page.ele('tag:div@text()=some_text')         - 返回第一个文本等于some_text的div元素                 \n
            page.ele('text:some_text')                   - 返回第一个文本含有some_text的元素                    \n
            page.ele('some_text')                        - 返回第一个文本含有some_text的元素（等价于上一行）      \n
            page.ele('text=some_text')                   - 返回第一个文本等于some_text的元素                    \n
            page.ele('xpath://div[@class="ele_class"]')  - 返回第一个符合xpath的元素                           \n
            page.ele('css:div.ele_class')                - 返回第一个符合css selector的元素                    \n
        - 查询字符串还有最精简模式，用x代替xpath、c代替css、t代替tag、tx代替text：                                  \n
            page.ele('x://div[@class="ele_class"]')      - 等同于 page.ele('xpath://div[@class="ele_class"]') \n
            page.ele('c:div.ele_class')                  - 等同于 page.ele('css:div.ele_class')               \n
            page.ele('t:div')                            - 等同于 page.ele('tag:div')                         \n
            page.ele('t:div@tx()=some_text')             - 等同于 page.ele('tag:div@text()=some_text')        \n
            page.ele('tx:some_text')                     - 等同于 page.ele('text:some_text')                  \n
            page.ele('tx=some_text')                     - 等同于 page.ele('text=some_text')
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param mode: 'single' 或 'all‘，对应查找一个或全部
        :param timeout: 查找元素超时时间，d模式专用
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super().ele(loc_or_ele, mode=mode)
        elif self._mode == 'd':
            return super(SessionPage, self).ele(loc_or_ele, mode=mode, timeout=timeout)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> Union[List[DriverElement], List[SessionElement]]:
        """返回页面中所有符合条件的元素、属性或节点文本                                                           \n
        示例：                                                                                                \n
        - 用loc元组查找：                                                                                      \n
            page.eles((By.CLASS_NAME, 'ele_class'))       - 返回所有class为ele_class的元素                      \n
        - 用查询字符串查找：                                                                                    \n
            查找方式：属性、tag name和属性、文本、xpath、css selector、id、class                                  \n
            @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                \n
            page.eles('.ele_class')                       - 返回所有 class 为 ele_class 的元素                  \n
            page.eles('.:ele_class')                      - 返回所有 class 中含有 ele_class 的元素              \n
            page.eles('#ele_id')                          - 返回所有 id 为 ele_id 的元素                        \n
            page.eles('#:ele_id')                         - 返回所有 id 中含有 ele_id 的元素                    \n
            page.eles('@class:ele_class')                 - 返回所有class含有ele_class的元素                    \n
            page.eles('@name=ele_name')                   - 返回所有name等于ele_name的元素                      \n
            page.eles('@placeholder')                     - 返回所有带placeholder属性的元素                     \n
            page.eles('tag:p')                            - 返回所有<p>元素                                    \n
            page.eles('tag:div@class:ele_class')          - 返回所有class含有ele_class的div元素                 \n
            page.eles('tag:div@class=ele_class')          - 返回所有class等于ele_class的div元素                 \n
            page.eles('tag:div@text():some_text')         - 返回所有文本含有some_text的div元素                   \n
            page.eles('tag:div@text()=some_text')         - 返回所有文本等于some_text的div元素                   \n
            page.eles('text:some_text')                   - 返回所有文本含有some_text的元素                      \n
            page.eles('some_text')                        - 返回所有文本含有some_text的元素（等价于上一行）        \n
            page.eles('text=some_text')                   - 返回所有文本等于some_text的元素                      \n
            page.eles('xpath://div[@class="ele_class"]')  - 返回所有符合xpath的元素                              \n
            page.eles('css:div.ele_class')                - 返回所有符合css selector的元素                       \n
        - 查询字符串还有最精简模式，用x代替xpath、c代替css、t代替tag、tx代替text：                                    \n
            page.eles('x://div[@class="ele_class"]')      - 等同于 page.eles('xpath://div[@class="ele_class"]') \n
            page.eles('c:div.ele_class')                  - 等同于 page.eles('css:div.ele_class')               \n
            page.eles('t:div')                            - 等同于 page.eles('tag:div')                         \n
            page.eles('t:div@tx()=some_text')             - 等同于 page.eles('tag:div@text()=some_text')        \n
            page.eles('tx:some_text')                     - 等同于 page.eles('text:some_text')                  \n
            page.eles('tx=some_text')                     - 等同于 page.eles('text=some_text')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，d模式专用
        :return: 元素对象或属性、文本节点文本组成的列表
        """
        if self._mode == 's':
            return super().eles(loc_or_str)
        elif self._mode == 'd':
            return super(SessionPage, self).eles(loc_or_str, timeout=timeout)

    def close_driver(self) -> None:
        """关闭driver及浏览器"""
        self._driver = None
        self.drission.close_driver()

    def close_session(self) -> None:
        """关闭session"""
        self._session = None
        self._response = None
        self.drission.close_session()
