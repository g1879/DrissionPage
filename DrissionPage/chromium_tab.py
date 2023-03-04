# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from copy import copy

from tldextract import extract

from .chromium_base import ChromiumBase, ChromiumBaseSetter
from .commons.web import set_session_cookies
from .session_page import SessionPage, SessionPageSetter, DownloadSetter


class ChromiumTab(ChromiumBase):
    """实现浏览器标签页的类"""

    def __init__(self, page, tab_id=None):
        """
        :param page: ChromiumPage对象
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        """
        self.page = page
        super().__init__(page.address, tab_id, page.timeout)

    def _set_runtime_settings(self):
        """重写设置浏览器运行参数方法"""
        self._timeouts = self.page.timeouts
        self.retry_times = self.page.retry_times
        self.retry_interval = self.page.retry_interval
        self._page_load_strategy = self.page.page_load_strategy


class WebPageTab(SessionPage, ChromiumTab):
    def __init__(self, page, tab_id):
        """
        :param page: WebPage对象
        :param tab_id: 要控制的标签页id
        """
        self.page = page
        self.address = page.address
        self._debug = page._debug
        self._debug_recorder = page._debug_recorder
        self._mode = 'd'
        self._has_driver = True
        self._has_session = True
        self._session = copy(page.session)

        self._response = None
        self._download_set = None
        self._download_path = None
        self._set = None
        super(SessionPage, self)._set_runtime_settings()
        self._connect_browser(tab_id)

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele = page('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: 子元素对象
        """
        if self._mode == 'd':
            return super(SessionPage, self).__call__(loc_or_str, timeout)
        elif self._mode == 's':
            return super().__call__(loc_or_str)

    @property
    def url(self):
        """返回当前url"""
        if self._mode == 'd':
            return super(SessionPage, self).url if self._tab_obj else None
        elif self._mode == 's':
            return self._session_url

    @property
    def title(self):
        """返回当前页面title"""
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
            return super(SessionPage, self).html if self._has_driver else ''

    @property
    def json(self):
        """当返回内容是json格式时，返回对应的字典"""
        if self._mode == 's':
            return super().json
        elif self._mode == 'd':
            return super(SessionPage, self).json

    @property
    def response(self):
        """返回 s 模式获取到的 Response 对象，切换到 s 模式"""
        return self._response

    @property
    def mode(self):
        """返回当前模式，'s'或'd' """
        return self._mode

    @property
    def cookies(self):
        if self._mode == 's':
            return super().get_cookies()
        elif self._mode == 'd':
            return super(SessionPage, self).get_cookies()

    @property
    def session(self):
        """返回Session对象，如未初始化则按配置信息创建"""
        if self._session is None:
            self._create_session()
        return self._session

    @property
    def _session_url(self):
        """返回 session 保存的url"""
        return self._response.url if self._response else None

    @property
    def timeout(self):
        """返回通用timeout设置"""
        return self.timeouts.implicit

    @timeout.setter
    def timeout(self, second):
        """设置通用超时时间
        :param second: 秒数
        :return: None
        """
        self.set.timeouts(implicit=second)

    @property
    def set(self):
        """返回用于等待的对象"""
        if self._set is None:
            self._set = WebPageTabSetter(self)
        return self._set

    @property
    def download_set(self):
        """返回下载设置对象"""
        if self._download_set is None:
            self._download_set = WebPageTabDownloadSetter(self)
        return self._download_set

    @property
    def download(self):
        """返回下载器对象"""
        return self.download_set._switched_DownloadKit

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        """跳转到一个url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param timeout: 连接超时时间（秒）
        :param kwargs: 连接参数，s模式专用
        :return: url是否可用，d模式返回None时表示不确定
        """
        if self._mode == 'd':
            return super(SessionPage, self).get(url, show_errmsg, retry, interval, timeout)
        elif self._mode == 's':
            if timeout is None:
                timeout = self.timeouts.page_load if self._has_driver else self.timeout
            return super().get(url, show_errmsg, retry, interval, timeout, **kwargs)

    def post(self, url: str, data=None, show_errmsg=False, retry=None, interval=None, **kwargs):
        """用post方式跳转到url，会切换到s模式
        :param url: 目标url
        :param data: post方式时提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        if self.mode == 'd':
            self.cookies_to_session()
        return super().post(url, data, show_errmsg, retry, interval, **kwargs)

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

    def change_mode(self, mode=None, go=True, copy_cookies=True):
        """切换模式，接收's'或'd'，除此以外的字符串会切换为 d 模式
        如copy_cookies为True，切换时会把当前模式的cookies复制到目标模式
        切换后，如果go是True，调用相应的get函数使访问的页面同步
        :param mode: 模式字符串
        :param go: 是否跳转到原模式的url
        :param copy_cookies: 是否复制cookies到目标模式
        :return: None
        """
        if mode is not None and mode.lower() == self._mode:
            return

        self._mode = 's' if self._mode == 'd' else 'd'

        # s模式转d模式
        if self._mode == 'd':
            if self._tab_obj is None:
                self._connect_browser(self.page._driver_options)

            self._url = None if not self._has_driver else super(SessionPage, self).url
            self._has_driver = True

            if self._session_url:
                if copy_cookies:
                    self.cookies_to_browser()

                if go:
                    self.get(self._session_url)

        # d模式转s模式
        elif self._mode == 's':
            self._has_session = True
            self._url = self._session_url

            if self._has_driver:
                if copy_cookies:
                    self.cookies_to_session()

                if go:
                    url = super(SessionPage, self).url
                    if url.startswith('http'):
                        self.get(url)

    def cookies_to_session(self, copy_user_agent=True):
        """把driver对象的cookies复制到session对象
        :param copy_user_agent: 是否复制ua信息
        :return: None
        """
        if copy_user_agent:
            selenium_user_agent = self.run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']
            self.session.headers.update({"User-Agent": selenium_user_agent})

        self.set.cookies(self._get_driver_cookies(as_dict=True), set_session=True)

    def cookies_to_browser(self):
        """把session对象的cookies复制到浏览器"""
        ex_url = extract(self._session_url)
        domain = f'{ex_url.domain}.{ex_url.suffix}'
        cookies = []
        for cookie in super().get_cookies():
            if cookie.get('domain', '') == '':
                cookie['domain'] = domain

            if domain in cookie['domain']:
                cookies.append(cookie)
        self.set.cookies(cookies, set_driver=True)

    def get_cookies(self, as_dict=False, all_domains=False):
        """返回cookies
        :param as_dict: 是否以字典方式返回
        :param all_domains: 是否返回所有域的cookies
        :return: cookies信息
        """
        if self._mode == 's':
            return super().get_cookies(as_dict, all_domains)
        elif self._mode == 'd':
            return self._get_driver_cookies(as_dict)

    def _get_driver_cookies(self, as_dict=False):
        """获取浏览器cookies
        :param as_dict: 以dict形式返回
        :return: cookies信息
        """
        cookies = self.run_cdp('Network.getCookies')['cookies']
        if as_dict:
            return {cookie['name']: cookie['value'] for cookie in cookies}
        else:
            return cookies

    def _find_elements(self, loc_or_ele, timeout=None, single=True, relative=False, raise_err=None):
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间，d模式专用
        :param single: True则返回第一个，False则返回全部
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super()._find_elements(loc_or_ele, single=single)
        elif self._mode == 'd':
            return super(SessionPage, self)._find_elements(loc_or_ele, timeout=timeout, single=single,
                                                           relative=relative)


class WebPageTabSetter(ChromiumBaseSetter):
    def __init__(self, page):
        super().__init__(page)
        self._session_setter = SessionPageSetter(self._page)
        self._chromium_setter = ChromiumBaseSetter(self._page)

    def cookies(self, cookies, set_session=False, set_driver=False):
        """添加cookies信息到浏览器或session对象
        :param cookies: 可以接收`CookieJar`、`list`、`tuple`、`str`、`dict`格式的`cookies`
        :param set_session: 是否设置到Session对象
        :param set_driver: 是否设置到浏览器
        :return: None
        """
        if set_driver and self._page._has_driver:
            self._chromium_setter.cookies(cookies)
        if set_session and self._page._has_session:
            self._session_setter.cookies(cookies)

    def headers(self, headers) -> None:
        """设置固定发送的headers
        :param headers: dict格式的headers数据
        :return: None
        """
        if self._page._has_session:
            self._session_setter.headers(headers)
        if self._page._has_driver:
            self._chromium_setter.headers(headers)

    def user_agent(self, ua, platform=None):
        """设置user agent，d模式下只有当前tab有效"""
        if self._page._has_session:
            self._session_setter.user_agent(ua)
        if self._page._has_driver:
            self._chromium_setter.user_agent(ua, platform)


class WebPageTabDownloadSetter(DownloadSetter):
    """用于设置下载参数的类"""

    def __init__(self, page):
        super().__init__(page)
        self._session = page.session

    @property
    def _switched_DownloadKit(self):
        """返回从浏览器同步cookies后的Session对象"""
        if self._page.mode == 'd':
            ua = self._page.run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']
            self._page.session.headers.update({"User-Agent": ua})
            set_session_cookies(self._page.session, self._page.get_cookies(as_dict=True))
        return self.DownloadKit
