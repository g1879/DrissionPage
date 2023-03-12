# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from .base import BasePage
from .drission import Drission
from .driver_page import DriverPage
from .session_page import SessionPage


class MixPage(SessionPage, DriverPage, BasePage):
    """MixPage整合了DriverPage和SessionPage，封装了对页面的操作，
    可在selenium（d模式）和requests（s模式）间无缝切换。
    切换的时候会自动同步cookies。
    获取信息功能为两种模式共有，操作页面元素功能只有d模式有。
    调用某种模式独有的功能，会自动切换到该模式。
    """

    def __init__(self, mode='d', drission=None, timeout=None, driver_options=None, session_options=None):
        """初始化函数
        :param mode: 'd' 或 's'，即driver模式和session模式
        :param drission: Drission对象，不传入时会自动创建，有传入时driver_options和session_options参数无效
        :param timeout: 超时时间，d模式时为寻找元素时间，s模式时为连接时间，默认10秒
        :param driver_options: 浏览器设置，没传入drission参数时会用这个设置新建Drission对象中的WebDriver对象，传入False则不创建
        :param session_options: requests设置，没传入drission参数时会用这个设置新建Drission对象中的Session对象，传入False则不创建
        """
        self._mode = mode.lower()
        if self._mode not in ('s', 'd'):
            raise ValueError('mode参数只能是s或d。')

        super(DriverPage, self).__init__(timeout)
        self._driver, self._session = (None, True) if self._mode == 's' else (True, None)
        self._drission = drission or Drission(driver_options, session_options)
        self._wait_object = None
        self._response = None
        self._scroll = None
        self._download_set = None
        self._download_path = None

        if self._mode == 'd':
            try:
                timeouts = self.drission.driver_options.timeouts
                t = timeout if isinstance(timeout, (int, float)) else timeouts['implicit']
                self.set_timeouts(t, timeouts['pageLoad'], timeouts['script'])

            except Exception:
                self.timeout = timeout if timeout is not None else 10

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele = page('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: 子元素对象或属性文本
        """
        if self._mode == 's':
            return super().__call__(loc_or_str)
        elif self._mode == 'd':
            return super(SessionPage, self).__call__(loc_or_str, timeout)

    # -----------------共有属性和方法-------------------
    @property
    def url(self):
        """返回当前url"""
        if self._mode == 'd':
            return self._drission.driver.current_url if self._driver else None
        elif self._mode == 's':
            return self._session_url

    @property
    def title(self):
        """返回网页title"""
        if self._mode == 's':
            return super().title
        elif self._mode == 'd':
            return super(SessionPage, self).title

    @property
    def html(self):
        """返回页面html文本"""
        if self._mode == 's':
            return super().html
        elif self._mode == 'd':
            return super(SessionPage, self).html

    @property
    def json(self):
        """当返回内容是json格式时，返回对应的字典"""
        if self._mode == 's':
            return super().json
        elif self._mode == 'd':
            return super(SessionPage, self).json

    def get(self, url, show_errmsg=False, retry=None, interval=None, **kwargs):
        """跳转到一个url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数，s模式专用
        :return: url是否可用，d模式返回None时表示不确定
        """
        if self._mode == 'd':
            return super(SessionPage, self).get(url, show_errmsg, retry, interval)
        elif self._mode == 's':
            return super().get(url, show_errmsg, retry, interval, **kwargs)

    def ele(self, loc_or_ele, timeout=None):
        """返回第一个符合条件的元素、属性或节点文本
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与页面等待时间一致
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super().ele(loc_or_ele)
        elif self._mode == 'd':
            return super(SessionPage, self).ele(loc_or_ele, timeout=timeout)

    def eles(self, loc_or_str, timeout=None):
        """返回页面中所有符合条件的元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与页面等待时间一致
        :return: 元素对象或属性、文本组成的列表
        """
        if self._mode == 's':
            return super().eles(loc_or_str)
        elif self._mode == 'd':
            return super(SessionPage, self).eles(loc_or_str, timeout=timeout)

    def s_ele(self, loc_or_ele=None):
        """查找第一个符合条件的元素以SessionElement形式返回，d模式处理复杂页面时效率很高
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        if self._mode == 's':
            return super().s_ele(loc_or_ele)
        elif self._mode == 'd':
            return super(SessionPage, self).s_ele(loc_or_ele)

    def s_eles(self, loc_or_str):
        """查找所有符合条件的元素以SessionElement形式返回，d模式处理复杂页面时效率很高
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本组成的列表
        """
        if self._mode == 's':
            return super().s_eles(loc_or_str)
        elif self._mode == 'd':
            return super(SessionPage, self).s_eles(loc_or_str)

    def _ele(self, loc_or_ele, timeout=None, single=True):
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间，d模式专用
        :param single: True则返回第一个，False则返回全部
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super()._ele(loc_or_ele, single=single)
        elif self._mode == 'd':
            return super(SessionPage, self)._ele(loc_or_ele, timeout=timeout, single=single)

    def get_cookies(self, as_dict=False, all_domains=False):
        """返回cookies
        :param as_dict: 是否以字典方式返回
        :param all_domains: 是否返回所有域的cookies
        :return: cookies信息
        """
        if self._mode == 's':
            return super().get_cookies(as_dict, all_domains)
        elif self._mode == 'd':
            return super(SessionPage, self).get_cookies(as_dict)

    # ----------------MixPage独有属性和方法-----------------------
    @property
    def drission(self):
        """返回当前使用的 Dirssion 对象"""
        return self._drission

    @property
    def driver(self):
        """返回 driver 对象，如没有则创建
        每次访问时切换到 d 模式，用于独有函数及外部调用
        :return: WebDriver对象
        """
        self.change_mode('d')
        return self._drission.driver

    @property
    def session(self):
        """返回 Session 对象，如没有则创建"""
        return self._drission.session

    @property
    def response(self):
        """返回 s 模式获取到的 Response 对象，切换到 s 模式"""
        self.change_mode('s')
        return self._response

    @property
    def mode(self):
        """返回当前模式，'s'或'd' """
        return self._mode

    @property
    def _session_url(self):
        """返回 session 保存的url"""
        return self._response.url if self._response else None

    def change_mode(self, mode=None, go=True, copy_cookies=True):
        """切换模式，接收's'或'd'，除此以外的字符串会切换为 d 模式
        切换时会把当前模式的cookies复制到目标模式
        切换后，如果go是True，调用相应的get函数使访问的页面同步
        注意：s转d时，若浏览器当前网址域名和s模式不一样，必须会跳转
        :param mode: 模式字符串
        :param go: 是否跳转到原模式的url
        :param copy_cookies: 是否复制cookies到目标模式
        """
        if mode is not None and mode.lower() == self._mode:
            return

        self._mode = 's' if self._mode == 'd' else 'd'

        # s模式转d模式
        if self._mode == 'd':
            self._driver = True
            self._url = None if not self._driver else self._drission.driver.current_url

            if self._session_url:
                if copy_cookies:
                    self.cookies_to_driver(self._session_url)

                if go:
                    self.get(self._session_url)

        # d模式转s模式
        elif self._mode == 's':
            self._session = True
            self._url = self._session_url

            if self._driver:
                if copy_cookies:
                    self.cookies_to_session()

                if go and self._drission.driver.current_url.startswith('http'):
                    self.get(self._drission.driver.current_url)

    def set_cookies(self, cookies, refresh=True):
        """设置cookies
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

    def cookies_to_session(self, copy_user_agent=False):
        """从driver复制cookies到session
        :param copy_user_agent : 是否复制user agent信息
        """
        self._drission.cookies_to_session(copy_user_agent)

    def cookies_to_driver(self, url=None):
        """从session复制cookies到driver
        chrome需要指定域才能接收cookies
        :param url: 目标域
        :return: None
        """
        url = url or self._session_url
        self._drission.cookies_to_driver(url)

    def check_page(self, by_requests=False):
        """d模式时检查网页是否符合预期
        默认由response状态检查，可重载实现针对性检查
        :param by_requests: 是否用内置response检查
        :return: bool或None，None代表不知道结果
        """
        if self._session_url and self._session_url == self.url:
            return self._response.ok

        # 使用requests访问url并判断可用性
        if by_requests:
            self.cookies_to_session()
            r = self._make_response(self.url, retry=0)[0]
            return r.ok if r else False

    def close_driver(self):
        """关闭driver及浏览器"""
        self._driver = None
        self.drission.close_driver(True)

    def close_session(self):
        """关闭session"""
        self._session = None
        self._response = None
        self.drission.close_session()

    # ----------------重写SessionPage的函数-----------------------
    def post(self, url, data=None, show_errmsg=False, retry=None, interval=None, **kwargs):
        """用post方式跳转到url，会切换到s模式
        :param url: 目标url
        :param data: post方式时提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        self.change_mode('s', go=False)
        return super().post(url, data, show_errmsg, retry, interval, **kwargs)

    @property
    def download(self):
        """返回下载器对象"""
        if self.mode == 'd':
            self.cookies_to_session()
        return super().download

    def chrome_downloading(self, path=None):
        """返回浏览器下载中的文件列表
        :param path: 下载文件夹路径，默认读取配置信息
        :return: 正在下载的文件列表
        """
        try:
            path = path or self._drission.driver_options.experimental_options['prefs']['download.default_directory']
            if not path:
                raise ValueError('未指定下载路径。')
        except Exception:
            raise IOError('无法找到下载路径。')

        return super().chrome_downloading(path)

    # ----------------MixPage独有函数-----------------------
    def hide_browser(self):
        """隐藏浏览器窗口"""
        self.drission.hide_browser()

    def show_browser(self):
        """显示浏览器窗口"""
        self.drission.show_browser()
