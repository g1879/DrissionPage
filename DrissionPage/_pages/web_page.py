# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from .chromium_page import ChromiumPage
from .chromium_tab import WebPageTab
from .session_page import SessionPage
from .._base.base import BasePage
from .._configs.chromium_options import ChromiumOptions
from .._functions.web import set_session_cookies, set_browser_cookies
from .._units.setter import WebPageSetter


class WebPage(SessionPage, ChromiumPage, BasePage):
    """整合浏览器和request的页面类"""

    def __new__(cls, mode='d', timeout=None, chromium_options=None, session_or_options=None):
        """初始化函数
        :param mode: 'd' 或 's'，即driver模式和session模式
        :param timeout: 超时时间（秒），d模式时为寻找元素时间，s模式时为连接时间，默认10秒
        :param chromium_options: Driver对象，只使用s模式时应传入False
        :param session_or_options: Session对象或SessionOptions对象，只使用d模式时应传入False
        """
        return super().__new__(cls, chromium_options)

    def __init__(self, mode='d', timeout=None, chromium_options=None, session_or_options=None, driver_or_options=None):
        """初始化函数
        :param mode: 'd' 或 's'，即driver模式和session模式
        :param timeout: 超时时间（秒），d模式时为寻找元素时间，s模式时为连接时间，默认10秒
        :param chromium_options: ChromiumOptions对象，只使用s模式时应传入False
        :param session_or_options: Session对象或SessionOptions对象，只使用d模式时应传入False
        """
        if hasattr(self, '_created'):
            return

        self._mode = mode.lower()
        if self._mode not in ('s', 'd'):
            raise ValueError('mode参数只能是s或d。')
        self._has_driver = True
        self._has_session = True

        super().__init__(session_or_options=session_or_options)
        if not chromium_options:
            chromium_options = ChromiumOptions(read_file=chromium_options)
            chromium_options.set_timeouts(base=self._timeout).set_paths(download_path=self.download_path)
        super(SessionPage, self).__init__(addr_or_opts=chromium_options, timeout=timeout)
        self._type = 'WebPage'
        self.change_mode(self._mode, go=False, copy_cookies=False)

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
            self._set = WebPageSetter(self)
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
                self._connect_browser(self._chromium_options)

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

                if go and not self.get(super(SessionPage, self).url):
                    raise ConnectionError('s模式访问失败，请设置go=False，自行构造连接参数进行访问。')

    def cookies_to_session(self, copy_user_agent=True):
        """把driver对象的cookies复制到session对象
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

    def get_tab(self, id_or_num=None, title=None, url=None, tab_type='page', as_id=False):
        """获取一个标签页对象，id_or_num不为None时，后面几个参数无效
        :param id_or_num: 要获取的标签页id或序号，序号从1开始，可传入负数获取倒数第几个，不是视觉排列顺序，而是激活顺序
        :param title: 要匹配title的文本，模糊匹配，为None则匹配所有
        :param url: 要匹配url的文本，模糊匹配，为None则匹配所有
        :param tab_type: tab类型，可用列表输入多个，如 'page', 'iframe' 等，为None则匹配所有
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: WebPageTab对象
        """
        if id_or_num is not None:
            if isinstance(id_or_num, str):
                id_or_num = id_or_num
            elif isinstance(id_or_num, int):
                id_or_num = self.tab_ids[id_or_num - 1 if id_or_num > 0 else id_or_num]
            elif isinstance(id_or_num, WebPageTab):
                return id_or_num.tab_id if as_id else id_or_num

        elif title == url == tab_type is None:
            id_or_num = self.tab_id

        else:
            id_or_num = self._browser.find_tabs(title, url, tab_type)
            if id_or_num:
                id_or_num = id_or_num[0]['id']
            else:
                return None

        if as_id:
            return id_or_num

        with self._lock:
            return WebPageTab(self, id_or_num)

    def get_tabs(self, title=None, url=None, tab_type='page', as_id=False):
        """查找符合条件的tab，返回它们组成的列表
        :param title: 要匹配title的文本，模糊匹配，为None则匹配所有
        :param url: 要匹配url的文本，模糊匹配，为None则匹配所有
        :param tab_type: tab类型，可用列表输入多个，如 'page', 'iframe' 等，为None则匹配所有
        :param as_id: 是否返回标签页id而不是标签页对象
        :return: ChromiumTab对象组成的列表
        """
        if as_id:
            return [tab['id'] for tab in self._browser.find_tabs(title, url, tab_type)]
        with self._lock:
            return [WebPageTab(self, tab['id']) for tab in self._browser.find_tabs(title, url, tab_type)]

    def new_tab(self, url=None, new_window=False, background=False, new_context=False):
        """新建一个标签页
        :param url: 新标签页跳转到的网址
        :param new_window: 是否在新窗口打开标签页
        :param background: 是否不激活新标签页，如new_window为True则无效
        :param new_context: 是否创建新的上下文
        :return: 新标签页对象
        """
        tab = WebPageTab(self, tab_id=self.browser.new_tab(new_window, background, new_context))
        if url:
            tab.get(url)
        return tab

    def close_driver(self):
        """关闭driver及浏览器"""
        if self._has_driver:
            self.change_mode('s')
            try:
                self.driver.run('Browser.close')
            except Exception:
                pass
            self._driver.stop()
            self._driver = None
            self._has_driver = None

    def close_session(self):
        """关闭session"""
        if self._has_session:
            self.change_mode('d')
            self._session.close()
            if self._response is not None:
                self._response.close()
            self._session = None
            self._response = None
            self._has_session = None

    def close(self):
        """关闭标签页和Session"""
        if self._has_driver:
            self.close_tabs(self.tab_id)
        if self._session:
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

    def quit(self, timeout=5, force=True):
        """关闭浏览器和Session
        :param timeout: 等待浏览器关闭超时时间（秒）
        :param force: 关闭超时是否强制终止进程
        :return: None
        """
        if self._has_session:
            self._session.close()
            self._session = None
            self._response = None
            self._has_session = None
        if self._has_driver:
            super(SessionPage, self).quit(timeout, force)
            self._driver = None
            self._has_driver = None

    def __repr__(self):
        return f'<WebPage browser_id={self.browser.id} tab_id={self.tab_id}>'
