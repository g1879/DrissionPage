# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from copy import copy
from time import sleep

from .._base.base import BasePage
from .._configs.session_options import SessionOptions
from .._functions.settings import Settings
from .._functions.web import set_session_cookies, set_browser_cookies, save_page
from .._pages.chromium_base import ChromiumBase
from .._pages.session_page import SessionPage
from .._units.setter import TabSetter, WebPageTabSetter
from .._units.waiter import TabWaiter


class ChromiumTab(ChromiumBase):
    """实现浏览器标签页的类"""
    _TABS = {}

    def __new__(cls, page, tab_id):
        """
        :param page: ChromiumPage对象
        :param tab_id: 要控制的标签页id
        """
        if Settings.singleton_tab_obj and tab_id in cls._TABS:
            r = cls._TABS[tab_id]
            while not hasattr(r, '_frame_id'):
                sleep(.1)
            return r
        r = object.__new__(cls)
        cls._TABS[tab_id] = r
        return r

    def __init__(self, page, tab_id):
        """
        :param page: ChromiumPage对象
        :param tab_id: 要控制的标签页id
        """
        if Settings.singleton_tab_obj and hasattr(self, '_created'):
            return
        self._created = True

        self._page = page
        self.tab = self
        self._browser = page.browser
        super().__init__(page.address, tab_id, page.timeout)
        self._rect = None
        self._type = 'ChromiumTab'

    def _d_set_runtime_settings(self):
        """重写设置浏览器运行参数方法"""
        self._timeouts = copy(self.page.timeouts)
        self.retry_times = self.page.retry_times
        self.retry_interval = self.page.retry_interval
        self._load_mode = self.page._load_mode
        self._download_path = self.page.download_path

    def close(self):
        """关闭当前标签页"""
        self.page.close_tabs(self.tab_id)

    @property
    def page(self):
        """返回总体page对象"""
        return self._page

    @property
    def set(self):
        """返回用于设置的对象"""
        if self._set is None:
            self._set = TabSetter(self)
        return self._set

    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = TabWaiter(self)
        return self._wait

    def save(self, path=None, name=None, as_pdf=False, **kwargs):
        """把当前页面保存为文件，如果path和name参数都为None，只返回文本
        :param path: 保存路径，为None且name不为None时保存在当前路径
        :param name: 文件名，为None且path不为None时用title属性值
        :param as_pdf: 为Ture保存为pdf，否则为mhtml且忽略kwargs参数
        :param kwargs: pdf生成参数
        :return: as_pdf为True时返回bytes，否则返回文件文本
        """
        return save_page(self, path, name, as_pdf, kwargs)

    def __repr__(self):
        return f'<ChromiumTab browser_id={self.browser.id} tab_id={self.tab_id}>'

    def _on_disconnect(self):
        ChromiumTab._TABS.pop(self.tab_id, None)


class WebPageTab(SessionPage, ChromiumTab, BasePage):
    def __init__(self, page, tab_id):
        """
        :param page: WebPage对象
        :param tab_id: 要控制的标签页id
        """
        if Settings.singleton_tab_obj and hasattr(self, '_created'):
            return

        self._mode = 'd'
        self._has_driver = True
        self._has_session = True
        super().__init__(session_or_options=SessionOptions(read_file=False).from_session(copy(page.session),
                                                                                         page._headers))
        super(SessionPage, self).__init__(page=page, tab_id=tab_id)
        self._type = 'WebPageTab'

    def __call__(self, locator, index=1, timeout=None):
        """在内部查找元素
        例：ele = page('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 超时时间（秒）
        :return: 子元素对象
        """
        if self._mode == 'd':
            return super(SessionPage, self).__call__(locator, index=index, timeout=timeout)
        elif self._mode == 's':
            return super().__call__(locator, index=index)

    @property
    def set(self):
        """返回用于设置的对象"""
        if self._set is None:
            self._set = WebPageTabSetter(self)
        return self._set

    @property
    def url(self):
        """返回当前url"""
        if self._mode == 'd':
            return self._browser_url
        elif self._mode == 's':
            return self._session_url

    @property
    def _browser_url(self):
        """返回浏览器当前url"""
        return super(SessionPage, self).url if self._driver else None

    @property
    def title(self):
        """返回当前页面title"""
        if self._mode == 's':
            return super().title
        elif self._mode == 'd':
            return super(SessionPage, self).title

    @property
    def raw_data(self):
        """返回页码原始数据数据"""
        if self._mode == 's':
            return super().raw_data
        elif self._mode == 'd':
            return super(SessionPage, self).html if self._has_driver else ''

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
    def user_agent(self):
        """返回user agent"""
        if self._mode == 's':
            return super().user_agent
        elif self._mode == 'd':
            return super(SessionPage, self).user_agent

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
        return self.timeouts.base

    @timeout.setter
    def timeout(self, second):
        """设置通用超时时间
        :param second: 秒数
        :return: None
        """
        self.set.timeouts(base=second)

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        """跳转到一个url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param timeout: 连接超时时间（秒），为None时使用页面对象timeouts.page_load属性值
        :param kwargs: 连接参数，s模式专用
        :return: url是否可用，d模式返回None时表示不确定
        """
        if self._mode == 'd':
            return super(SessionPage, self).get(url, show_errmsg, retry, interval, timeout)
        elif self._mode == 's':
            if timeout is None:
                timeout = self.timeouts.page_load if self._has_driver else self.timeout
            return super().get(url, show_errmsg, retry, interval, timeout, **kwargs)

    def post(self, url, show_errmsg=False, retry=None, interval=None, **kwargs):
        """用post方式跳转到url，会切换到s模式
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param kwargs: 连接参数
        :return: s模式时返回url是否可用，d模式时返回获取到的Response对象
        """
        if self.mode == 'd':
            self.cookies_to_session()
            super().post(url, show_errmsg, retry, interval, **kwargs)
            return self.response
        return super().post(url, show_errmsg, retry, interval, **kwargs)

    def ele(self, locator, index=1, timeout=None):
        """返回第一个符合条件的元素、属性或节点文本
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与页面等待时间一致
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super().ele(locator, index=index)
        elif self._mode == 'd':
            return super(SessionPage, self).ele(locator, index=index, timeout=timeout)

    def eles(self, locator, timeout=None):
        """返回页面中所有符合条件的元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与页面等待时间一致
        :return: 元素对象或属性、文本组成的列表
        """
        if self._mode == 's':
            return super().eles(locator)
        elif self._mode == 'd':
            return super(SessionPage, self).eles(locator, timeout=timeout)

    def s_ele(self, locator=None, index=1):
        """查找第一个符合条件的元素以SessionElement形式返回，d模式处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :return: SessionElement对象或属性、文本
        """
        if self._mode == 's':
            return super().s_ele(locator, index=index)
        elif self._mode == 'd':
            return super(SessionPage, self).s_ele(locator, index=index)

    def s_eles(self, locator):
        """查找所有符合条件的元素以SessionElement形式返回，d模式处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本组成的列表
        """
        if self._mode == 's':
            return super().s_eles(locator)
        elif self._mode == 'd':
            return super(SessionPage, self).s_eles(locator)

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
            if self._driver is None:
                self._connect_browser(self.page._chromium_options)

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
        """把浏览器的cookies复制到session对象
        :param copy_user_agent: 是否复制ua信息
        :return: None
        """
        if not self._has_session:
            return

        if copy_user_agent:
            user_agent = self.run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value']
            self._headers.update({"User-Agent": user_agent})

        set_session_cookies(self.session, super(SessionPage, self).cookies())

    def cookies_to_browser(self):
        """把session对象的cookies复制到浏览器"""
        if not self._has_driver:
            return
        set_browser_cookies(self, super().cookies())

    def cookies(self, as_dict=False, all_domains=False, all_info=False):
        """返回cookies
        :param as_dict: 为True时以dict格式返回，为False时返回list且all_info无效
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，False则只返回name、value、domain
        :return: cookies信息
        """
        if self._mode == 's':
            return super().cookies(as_dict, all_domains, all_info)
        elif self._mode == 'd':
            return super(SessionPage, self).cookies(as_dict, all_domains, all_info)

    def close(self):
        """关闭当前标签页"""
        self.page.close_tabs(self.tab_id)
        self._session.close()
        if self._response is not None:
            self._response.close()

    def _find_elements(self, locator, timeout=None, index=1, relative=False, raise_err=None):
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），d模式专用
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: WebPage用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super()._find_elements(locator, index=index)
        elif self._mode == 'd':
            return super(SessionPage, self)._find_elements(locator, timeout=timeout, index=index, relative=relative)

    def __repr__(self):
        return f'<WebPageTab browser_id={self.browser.id} tab_id={self.tab_id}>'
