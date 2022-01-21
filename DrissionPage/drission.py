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

from .config import _session_options_to_dict, SessionOptions, DriverOptions, _cookies_to_tuple


class Drission(object):
    """Drission类用于管理WebDriver对象和Session对象，是驱动器的角色"""

    def __init__(self,
                 driver_or_options: Union[WebDriver, Options, DriverOptions, bool] = None,
                 session_or_options: Union[Session, dict, SessionOptions, bool] = None,
                 ini_path: str = None,
                 proxy: dict = None):
        """初始化，可接收现成的WebDriver和Session对象，或接收它们的配置信息生成对象                     \n
        :param driver_or_options: driver对象或DriverOptions、Options类，传入False则创建空配置对象
        :param session_or_options: Session对象或设置字典，传入False则创建空配置对象
        :param ini_path: ini文件路径
        :param proxy: 代理设置
        """
        self._session = None
        self._driver = None
        self._session_options = None
        self._driver_options = None
        self._debugger = None
        self._proxy = proxy

        # ------------------处理session options----------------------
        if session_or_options is None:
            self._session_options = SessionOptions(ini_path=ini_path).as_dict()

        elif session_or_options is False:
            self._driver_options = SessionOptions(read_file=False).as_dict()

        elif isinstance(session_or_options, Session):
            self._session = session_or_options

        elif isinstance(session_or_options, SessionOptions):
            self._session_options = session_or_options.as_dict()

        elif isinstance(session_or_options, dict):
            self._session_options = session_or_options

        else:
            raise TypeError('session_or_options参数只能接收Session, dict, SessionOptions或False。')

        # ------------------处理driver options----------------------
        if driver_or_options is None:
            self._driver_options = DriverOptions(ini_path=ini_path)

        elif driver_or_options is False:
            self._driver_options = DriverOptions(read_file=False)

        elif isinstance(driver_or_options, WebDriver):
            self._driver = driver_or_options

        elif isinstance(driver_or_options, (Options, DriverOptions)):
            self._driver_options = driver_or_options

        else:
            raise TypeError('driver_or_options参数只能接收WebDriver, Options, DriverOptions或False。')

    def __del__(self):
        """关闭对象时关闭浏览器和Session"""
        try:
            self.close()
        except ImportError:
            pass

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
            if not self.driver_options.debugger_address and self._proxy:
                self.driver_options.add_argument(f'--proxy-server={self._proxy["http"]}')

            driver_path = self.driver_options.driver_path or 'chromedriver'
            chrome_path = self.driver_options.binary_location or 'chrome.exe'

            # -----------若指定debug端口且该端口未在使用中，则先启动浏览器进程-----------
            if self.driver_options.debugger_address and _check_port(self.driver_options.debugger_address) is False:
                from subprocess import Popen
                port = self.driver_options.debugger_address.split(':')[-1]

                # 启动浏览器进程，同时返回该进程使用的 chrome.exe 路径
                chrome_path, self._debugger = _create_chrome(chrome_path, port,
                                                             self.driver_options.arguments, self._proxy)

            # -----------创建WebDriver对象-----------
            self._driver = _create_driver(chrome_path, driver_path, self.driver_options)

            # 反反爬设置
            try:
                self._driver.execute_script('Object.defineProperty(navigator,"webdriver",{get:() => undefined,});')
            except Exception:
                pass

            # self._driver.execute_cdp_cmd(
            #     'Page.addScriptToEvaluateOnNewDocument',
            #     {'source': 'Object.defineProperty(navigator,"webdriver",{get:() => Chrome,});'})

        return self._driver

    @property
    def driver_options(self) -> Union[DriverOptions, Options]:
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

    @property
    def debugger_progress(self):
        """调试浏览器进程"""
        return self._debugger

    def kill_browser(self) -> None:
        """关闭浏览器进程（如果可以）"""
        if self.debugger_progress:
            self.debugger_progress.kill()
            return

        pid = self.get_browser_progress_id()
        from os import popen
        from platform import system

        if pid and system().lower() == 'windows' \
                and popen(f'tasklist | findstr {pid}').read().lower().startswith('chrome.exe'):
            popen(f'taskkill /pid {pid} /F')

        else:
            self._driver.quit()

    def get_browser_progress_id(self) -> Union[str, None]:
        """获取浏览器进程id"""
        if self.debugger_progress:
            return self.debugger_progress.pid

        address = str(self.driver_options.debugger_address).split(':')
        if len(address) == 2:
            ip, port = address
            if ip not in ('127.0.0.1', 'localhost') or not port.isdigit():
                return None

            from os import popen
            txt = ''
            progresses = popen(f'netstat -nao | findstr :{port}').read().split('\n')
            for progress in progresses:
                if 'LISTENING' in progress:
                    txt = progress
                    break
            if not txt:
                return None

            return txt.split(' ')[-1]

    def hide_browser(self) -> None:
        """隐藏浏览器界面"""
        self._show_or_hide_browser()

    def show_browser(self) -> None:
        """显示浏览器界面"""
        self._show_or_hide_browser(False)

    def _show_or_hide_browser(self, hide: bool = True) -> None:
        from platform import system
        if system().lower() != 'windows':
            raise OSError('该方法只能在Windows系统使用。')

        try:
            from win32gui import ShowWindow
            from win32con import SW_HIDE, SW_SHOW
        except ImportError:
            raise ImportError('请先安装：pip install pypiwin32')

        pid = self.get_browser_progress_id()
        if not pid:
            print('只有设置了debugger_address参数才能使用 show_browser() 和 hide_browser()')
            return
        hds = _get_chrome_hwnds_from_pid(pid)
        sw = SW_HIDE if hide else SW_SHOW
        for hd in hds:
            ShowWindow(hd, sw)

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
                kwargs = {x: cookie[x] for x in cookie
                          if x.lower() not in ('name', 'value', 'httponly', 'expiry', 'samesite')}

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
                        raise ValueError('cookie中没有域名或浏览器未访问过URL。')

                    cookie['domain'] = cookie_domain

                else:
                    cookie_domain = cookie['domain'] if cookie['domain'][0] != '.' else cookie['domain'][1:]

                if cookie_domain not in browser_domain:
                    self.driver.get(cookie_domain if cookie_domain.startswith('http://')
                                    else f'http://{cookie_domain}')

                # 避免selenium自动添加.后无法正确覆盖已有cookie
                if cookie['domain'][0] != '.':
                    c = self.driver.get_cookie(cookie['name'])
                    if c and c['domain'] == cookie['domain']:
                        self.driver.delete_cookie(cookie['name'])

                self.driver.add_cookie(cookie)

    def _set_session(self, data: dict) -> None:
        """根据传入字典对session进行设置    \n
        :param data: session配置字典
        :return: None
        """
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
            user_agent_to_session(self.driver, self.session)

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

    def close_driver(self, kill: bool = False) -> None:
        """关闭driver和浏览器"""
        if self._driver:
            if kill:
                self.kill_browser()
            else:
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


def user_agent_to_session(driver: WebDriver, session: Session) -> None:
    """把driver的user-agent复制到session    \n
    :param driver: 来源driver对象
    :param session: 目标session对象
    :return: None
    """
    driver = driver
    session = session
    selenium_user_agent = driver.execute_script("return navigator.userAgent;")
    session.headers.update({"User-Agent": selenium_user_agent})


def _check_port(debugger_address: str) -> Union[bool, None]:
    """检查端口是否被占用                               \n
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
    finally:
        if s:
            s.close()


def _create_chrome(chrome_path: str, port: str, args: list, proxy: dict) -> tuple:
    """创建 chrome 进程                          \n
    :param chrome_path: chrome.exe 路径
    :param port: 进程运行的端口号
    :param args: chrome 配置参数
    :return: chrome.exe 路径和进程对象组成的元组
    """
    from subprocess import Popen

    # ----------为路径加上双引号，避免路径中的空格产生异常----------
    args1 = []
    for arg in args:
        if arg.startswith(('--user-data-dir', '--disk-cache-dir')):
            index = arg.find('=') + 1
            args1.append(f'{arg[:index]}"{arg[index:].strip()}"')
        else:
            args1.append(arg)

    args = ' '.join(set(args1))

    if proxy:
        args = f'{args} --proxy-server={proxy["http"]}'

    # ----------创建浏览器进程----------
    try:
        debugger = Popen(f'{chrome_path} --remote-debugging-port={port} {args}', shell=False)

        if chrome_path == 'chrome.exe':
            from .common import get_exe_path_from_port
            chrome_path = get_exe_path_from_port(port)

    # 传入的路径找不到，主动在ini文件、注册表、系统变量中找
    except FileNotFoundError:
        from DrissionPage.easy_set import _get_chrome_path
        chrome_path = _get_chrome_path(show_msg=False)

        if not chrome_path:
            raise FileNotFoundError('无法找到chrome.exe路径，请手动配置。')

        debugger = Popen(f'"{chrome_path}" --remote-debugging-port={port} {args}', shell=False)

    return chrome_path, debugger


def _create_driver(chrome_path: str, driver_path: str, options: Options) -> WebDriver:
    """创建 WebDriver 对象                            \n
    :param chrome_path: chrome.exe 路径
    :param driver_path: chromedriver.exe 路径
    :param options: Options 对象
    :return: WebDriver 对象
    """
    try:
        debugger_address = options.debugger_address
        if options.debugger_address:
            options = Options()
            options.debugger_address = debugger_address

        return webdriver.Chrome(driver_path, options=options)

    # 若版本不对，获取对应 chromedriver 再试
    except (WebDriverException, SessionNotCreatedException):
        print('打开失败，尝试获取driver。\n')
        from .easy_set import get_match_driver
        from DrissionPage.easy_set import _get_chrome_path

        if chrome_path == 'chrome.exe':
            chrome_path = _get_chrome_path(show_msg=False, from_ini=False)

        if chrome_path:
            driver_path = get_match_driver(chrome_path=chrome_path, check_version=False, show_msg=True)
            if driver_path:
                try:
                    options.binary_location = chrome_path
                    return webdriver.Chrome(driver_path, options=options)
                except Exception:
                    pass

    print('无法启动，请检查浏览器路径，或手动设置chromedriver。\n下载地址：http://npm.taobao.org/mirrors/chromedriver/')
    exit(0)


def _get_chrome_hwnds_from_pid(pid) -> list:
    # 通过PID查询句柄ID
    try:
        from win32gui import IsWindow, GetWindowText, EnumWindows
        from win32process import GetWindowThreadProcessId
    except ImportError:
        raise ImportError('请先安装win32gui，pip install pypiwin32')

    def callback(hwnd, hds):
        if IsWindow(hwnd) and '- Google Chrome' in GetWindowText(hwnd):
            _, found_pid = GetWindowThreadProcessId(hwnd)
            if str(found_pid) == str(pid):
                hds.append(hwnd)
            return True

    hwnds = []
    EnumWindows(callback, hwnds)
    return hwnds
