# -*- encoding: utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   drission.py
"""
from typing import Union
from urllib.parse import urlparse

import tldextract
from requests import Session
from requests_html import HTMLSession
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from .config import _dict_to_chrome_options, OptionsManager, _chrome_options_to_dict


class Drission(object):
    """Drission类整合了WebDriver对象和HTLSession对象，可按要求创建、关闭及同步cookies"""

    def __init__(self,
                 driver_options: Union[dict, Options] = None,
                 session_options: dict = None,
                 ini_path: str = None,
                 proxy: dict = None):
        """初始化配置信息，但不生成session和driver实例              \n
        :param driver_options: chrome设置，Options类或设置字典
        :param session_options: session设置
        :param ini_path: ini文件路径'
        :param proxy: 代理设置
        """
        self._session = None
        self._driver = None
        self._driver_path = 'chromedriver'
        self._proxy = proxy
        if session_options is None:
            self._session_options = OptionsManager(ini_path).get_option('session_options')
        else:
            self._session_options = session_options
        if driver_options is None:
            om = OptionsManager(ini_path)
            self._driver_options = om.get_option('chrome_options')
            if 'chromedriver_path' in om.get_option('paths') and om.get_option('paths')['chromedriver_path']:
                self._driver_path = om.get_option('paths')['chromedriver_path']
        else:
            self._driver_options = _chrome_options_to_dict(driver_options)
            if 'driver_path' in self._driver_options and self._driver_options['driver_path']:
                self._driver_path = self._driver_options['driver_path']

    @property
    def session(self) -> HTMLSession:
        """返回HTMLSession对象，如为None则按配置信息创建"""
        if self._session is None:
            self._session = HTMLSession()
            attrs = ['headers', 'cookies', 'auth', 'proxies', 'hooks', 'params', 'verify',
                     'cert', 'adapters', 'stream', 'trust_env', 'max_redirects']
            for i in attrs:
                if i in self._session_options:
                    exec(f'self._session.{i} = self._session_options["{i}"]')
            if self._proxy:
                self._session.proxies = self._proxy

        return self._session

    @property
    def driver(self) -> WebDriver:
        """返回WebDriver对象，如为None则按配置信息创建"""
        if self._driver is None:
            if isinstance(self._driver_options, dict):
                options = _dict_to_chrome_options(self._driver_options)
            else:
                raise TypeError('Driver options invalid')

            if self._proxy:
                options.add_argument(f'--proxy-server={self._proxy["http"]}')

            self._driver = webdriver.Chrome(self._driver_path, options=options)

            # 反爬设置，似乎没用
            self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => Chrome
                })
              """
            })

        return self._driver

    @property
    def driver_options(self) -> dict:
        """返回driver配置信息"""
        return self._driver_options

    @property
    def session_options(self) -> dict:
        """返回session配置信息"""
        return self._session_options

    @session_options.setter
    def session_options(self, value: dict):
        """设置session配置"""
        self._session_options = value

    @property
    def proxy(self) -> Union[None, dict]:
        """返回代理信息"""
        return self._proxy

    @proxy.setter
    def proxy(self, proxies: dict = None):
        """设置代理信息"""
        self._proxy = proxies
        if self._session:
            self._session.proxies = proxies
        if self._driver:
            cookies = self._driver.get_cookies()
            url = self._driver.current_url
            self._driver.quit()
            self._driver = None
            self._driver = self.driver
            self._driver.get(url)
            for cookie in cookies:
                self._ensure_add_cookie(cookie)

    def cookies_to_session(self, copy_user_agent: bool = False,
                           driver: WebDriver = None,
                           session: Session = None) -> None:
        """把driver对象的cookies复制到session对象  \n
        :param copy_user_agent: 是否复制ua信息
        :param driver: 来源driver对象
        :param session: 目标session对象
        :return: None
        """
        driver = driver or self.driver
        session = session or self.session
        if copy_user_agent:
            self.user_agent_to_session(driver, session)
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    def cookies_to_driver(self, url: str,
                          driver: WebDriver = None,
                          session: Session = None) -> None:
        """把session对象的cookies复制到driver对象  \n
        :param url: 作用域
        :param driver: 目标driver对象
        :param session: 来源session对象
        :return: None
        """
        driver = driver or self.driver
        session = session or self.session
        domain = urlparse(url).netloc
        if not domain:
            raise Exception('Without specifying a domain')
        # 翻译cookies
        for i in [x for x in session.cookies if domain in x.domain]:
            cookie_data = {'name': i.name, 'value': str(i.value), 'path': i.path, 'domain': i.domain}
            if i.expires:
                cookie_data['expiry'] = i.expires
            self._ensure_add_cookie(cookie_data, driver=driver)

    def _ensure_add_cookie(self, cookie, override_domain=None, driver=None) -> None:
        """添加cookie到driver                  \n
        :param cookie: 要添加的cookie
        :param override_domain: 覆盖作用域
        :param driver: 操作的driver对象
        :return: None
        """
        driver = driver or self.driver
        if override_domain:
            cookie['domain'] = override_domain

        cookie_domain = cookie['domain'] if cookie['domain'][0] != '.' else cookie['domain'][1:]
        try:
            browser_domain = tldextract.extract(driver.current_url).fqdn
        except AttributeError:
            browser_domain = ''
        if cookie_domain not in browser_domain:
            driver.get(f'http://{cookie_domain.lstrip("http://")}')
        if 'expiry' in cookie:
            cookie['expiry'] = int(cookie['expiry'])

        driver.add_cookie(cookie)

        # 如果添加失败，尝试更宽的域名
        if not self._is_cookie_in_driver(cookie, driver):
            cookie['domain'] = tldextract.extract(cookie['domain']).registered_domain
            driver.add_cookie(cookie)
            if not self._is_cookie_in_driver(cookie):
                raise WebDriverException(f"Couldn't add the following cookie to the webdriver\n{cookie}\n")

    def _is_cookie_in_driver(self, cookie, driver=None) -> bool:
        """检查cookie是否已经在driver里                   \n
        只检查name、value、domain，检查domain时比较宽      \n
        :param cookie: 要检查的cookie
        :param driver: 被检查的driver
        :return: 返回布尔值
        """
        driver = driver or self.driver
        for driver_cookie in driver.get_cookies():
            if (cookie['name'] == driver_cookie['name'] and
                    cookie['value'] == driver_cookie['value'] and
                    (cookie['domain'] == driver_cookie['domain'] or
                     f'.{cookie["domain"]}' == driver_cookie['domain'])):
                return True
        return False

    def user_agent_to_session(self, driver: WebDriver = None, session: Session = None) -> None:
        """把driver的user-agent复制到session  \n
        :param driver: 来源driver对象
        :param session: 目标session对象
        :return: None
        """
        driver = driver or self.driver
        session = session or self.session
        selenium_user_agent = driver.execute_script("return navigator.userAgent;")
        session.headers.update({"User-Agent": selenium_user_agent})

    def close_driver(self) -> None:
        """关闭driver和浏览器"""
        self._driver.quit()
        self._driver = None

    def close_session(self) -> None:
        """关闭session"""
        self._session.close()
        self._session = None

    def close(self) -> None:
        """关闭session、driver和浏览器"""
        if self._driver:
            self.close_driver()
        if self._session:
            self.close_session()

    def __del__(self):
        try:
            self.close()
        except ImportError:
            pass
