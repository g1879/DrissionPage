# -*- encoding: utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   drission.py
"""
from sys import exit
from typing import Union

from requests import Session
from requests.cookies import RequestsCookieJar
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from tldextract import extract

from .config import (_dict_to_chrome_options, _session_options_to_dict,
                     SessionOptions, DriverOptions, _chrome_options_to_dict, OptionsManager, _cookies_to_tuple)


class Drission(object):
    """Drission类用于管理WebDriver对象和Session对象，是驱动器的角色"""

    def __init__(self,
                 driver_or_options: Union[WebDriver, dict, Options, DriverOptions] = None,
                 session_or_options: Union[Session, dict, SessionOptions] = None,
                 ini_path: str = None,
                 proxy: dict = None):
        """初始化，可接收现成的WebDriver和Session对象，或接收它们的配置信息生成对象       \n
        :param driver_or_options: driver对象或chrome设置，Options类或设置字典
        :param session_or_options: Session对象或设置
        :param ini_path: ini文件路径
        :param proxy: 代理设置
        """
        self._session = None
        self._driver = None
        self._proxy = proxy

        om = OptionsManager(ini_path) if session_or_options is None or driver_or_options is None else None

        # ------------------处理session options----------------------
        if session_or_options is None:
            self._session_options = om.session_options

        else:
            # 若接收到Session对象，直接记录
            if isinstance(session_or_options, Session):
                self._session = session_or_options

            # 否则记录其配置信息
            else:
                self._session_options = _session_options_to_dict(session_or_options)

        # ------------------处理driver options----------------------
        if driver_or_options is None:
            self._driver_options = om.chrome_options
            self._driver_options['driver_path'] = om.get_value('paths', 'chromedriver_path')

        else:
            # 若接收到WebDriver对象，直接记录
            if isinstance(driver_or_options, WebDriver):
                self._driver = driver_or_options

            # 否则记录其配置信息
            else:
                self._driver_options = _chrome_options_to_dict(driver_or_options)

    @property
    def session(self) -> Session:
        """返回Session对象，如未初始化则按配置信息创建"""
        if self._session is None:
            self._set_session(self._session_options)

            if self._proxy:
                self._session.proxies = self._proxy

        return self._session

    @property
    def driver(self) -> WebDriver:
        """返回WebDriver对象，如未初始化则按配置信息创建。         \n
        如设置了本地调试浏览器，可自动接入或打开浏览器进程。
        """
        if self._driver is None:
            if isinstance(self._driver_options, dict):
                options = _dict_to_chrome_options(self._driver_options)
            else:
                raise TypeError('Driver options invalid')

            if self._proxy:
                options.add_argument(f'--proxy-server={self._proxy["http"]}')

            driver_path = self._driver_options.get('driver_path', None) or 'chromedriver'
            chrome_path = self._driver_options.get('binary_location', None) or 'chrome.exe'

            if options.debugger_address and _check_port(options.debugger_address) is False:
                from subprocess import Popen
                port = options.debugger_address.split(':')[-1]

                Popen(f'{chrome_path} --remote-debugging-port={port}', shell=False)

            try:
                self._driver = webdriver.Chrome(driver_path, options=options)

            except (WebDriverException, SessionNotCreatedException):
                from .easy_set import get_match_driver

                chrome_path = self._driver_options.get('binary_location', None) or None
                driver_path = get_match_driver(chrome_path=chrome_path, check_version=False, show_msg=False)

                if driver_path:
                    try:
                        self._driver = webdriver.Chrome(driver_path, options=options)
                    except:
                        print('无法启动，请检查chromedriver版本与Chrome是否匹配，并手动设置。')
                        exit(0)
                else:
                    print('无法启动，请检查chromedriver版本与Chrome是否匹配，并手动设置。')
                    exit(0)

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
    def session_options(self, options: Union[dict, SessionOptions]) -> None:
        """设置session配置                  \n
        :param options: session配置字典
        :return: None
        """
        self._session_options = _session_options_to_dict(options)
        self._set_session(self._session_options)

    @property
    def proxy(self) -> Union[None, dict]:
        """返回代理信息"""
        return self._proxy

    @proxy.setter
    def proxy(self, proxies: dict = None) -> None:
        """设置代理信息                \n
        :param proxies: 代理信息字典
        :return: None
        """
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
                self.set_cookies(cookie, set_driver=True)

    def set_cookies(self,
                    cookies: Union[RequestsCookieJar, list, tuple, str, dict],
                    set_session: bool = False,
                    set_driver: bool = False) -> None:
        """设置cookies                                                      \n
        :param cookies: cookies信息，可为CookieJar, list, tuple, str, dict
        :param set_session: 是否设置session的cookies
        :param set_driver: 是否设置driver的cookies
        :return: None
        """
        cookies = _cookies_to_tuple(cookies)

        for cookie in cookies:
            if cookie['value'] is None:
                cookie['value'] = ''

            # 添加cookie到session
            if set_session:
                kwargs = {x: cookie[x] for x in cookie if x not in ('name', 'value', 'httpOnly', 'expiry')}

                if 'expiry' in cookie:
                    kwargs['expires'] = cookie['expiry']

                self.session.cookies.set(cookie['name'], cookie['value'], **kwargs)

            # 添加cookie到driver
            if set_driver:
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])

                try:
                    browser_domain = extract(self.driver.current_url).fqdn
                except AttributeError:
                    browser_domain = ''

                if not cookie.get('domain', None):
                    if browser_domain:
                        url = extract(browser_domain)
                        cookie_domain = f'{url.domain}.{url.suffix}'
                    else:
                        raise ValueError('There is no domain name in the cookie or the browser has not visited a URL.')

                    cookie['domain'] = cookie_domain

                else:
                    cookie_domain = cookie['domain'] if cookie['domain'][0] != '.' else cookie['domain'][1:]

                if cookie_domain not in browser_domain:
                    self.driver.get(cookie_domain if cookie_domain.startswith('http://')
                                    else f'http://{cookie_domain}')

                self.driver.add_cookie(cookie)

    def _set_session(self, data: dict) -> None:
        if self._session is None:
            self._session = Session()

        attrs = ['headers', 'auth', 'proxies', 'hooks', 'params', 'verify',
                 'cert', 'stream', 'trust_env', 'max_redirects']  # , 'adapters'

        if 'cookies' in data:
            self.set_cookies(data['cookies'], set_session=True)

        for i in attrs:
            if i in data:
                self._session.__setattr__(i, data[i])

    def cookies_to_session(self, copy_user_agent: bool = False) -> None:
        """把driver对象的cookies复制到session对象    \n
        :param copy_user_agent: 是否复制ua信息
        :return: None
        """
        if copy_user_agent:
            self.user_agent_to_session(self.driver, self.session)

        self.set_cookies(self.driver.get_cookies(), set_session=True)

    def cookies_to_driver(self, url: str) -> None:
        """把session对象的cookies复制到driver对象  \n
        :param url: 作用域
        :return: None
        """
        browser_domain = extract(self.driver.current_url).fqdn
        ex_url = extract(url)

        if ex_url.fqdn not in browser_domain:
            self.driver.get(url)

        domain = f'{ex_url.domain}.{ex_url.suffix}'

        cookies = []
        for cookie in self.session.cookies:
            if cookie.domain == '':
                cookie.domain = domain

            if domain in cookie.domain:
                cookies.append(cookie)

        self.set_cookies(cookies, set_driver=True)

    def user_agent_to_session(self, driver: WebDriver = None, session: Session = None) -> None:
        """把driver的user-agent复制到session    \n
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
        if self._driver:
            self._driver.quit()
            self._driver = None

    def close_session(self) -> None:
        """关闭session"""
        if self._session:
            self._session.close()
            self._session = None

    def close(self) -> None:
        """关闭session、driver和浏览器"""
        if self._driver:
            self.close_driver()

        if self._session:
            self.close_session()

    def __del__(self):
        """关闭对象时关闭浏览器和Session"""
        try:
            self.close()
        except ImportError:
            pass


def _check_port(debugger_address: str) -> Union[bool, None]:
    """检查端口是否可用                               \n
    :param debugger_address: 浏览器地址及端口
    :return: bool
    """
    import socket

    ip, port = debugger_address.split(':')

    if ip not in ('127.0.0.1', 'localhost'):
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except socket.error:
        return False
