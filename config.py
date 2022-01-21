# -*- coding:utf-8 -*-
"""
管理配置的类
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   config.py
"""
from configparser import RawConfigParser, NoSectionError, NoOptionError
from http.cookiejar import Cookie
from pathlib import Path
from typing import Any, Union

from requests.cookies import RequestsCookieJar
from selenium.webdriver.chrome.options import Options


class OptionsManager(object):
    """管理配置文件内容的类"""

    def __init__(self, path: str = None):
        """初始化，读取配置文件，如没有设置临时文件夹，则设置并新建  \n
        :param path: ini文件的路径，默认读取模块文件夹下的
        """
        self.ini_path = str(Path(__file__).parent / 'configs.ini') if path == 'default' or path is None else path
        if not Path(self.ini_path).exists():
            raise FileNotFoundError('ini文件不存在。')
        self._conf = RawConfigParser()
        self._conf.read(self.ini_path, encoding='utf-8')

        self._paths = None
        self._chrome_options = None
        self._session_options = None

    def __text__(self) -> str:
        """打印ini文件内容"""
        return (f"paths:\n"
                f"{self.get_option('paths')}\n\n"
                "chrome options:\n"
                f"{self.get_option('chrome_options')}\n\n"
                "session options:\n"
                f"{self.get_option('session_options')}")

    @property
    def paths(self) -> dict:
        """返回paths设置"""
        if self._paths is None:
            self._paths = self.get_option('paths')

        return self._paths

    @property
    def chrome_options(self) -> dict:
        """返回chrome设置"""
        if self._chrome_options is None:
            self._chrome_options = self.get_option('chrome_options')

        return self._chrome_options

    @property
    def session_options(self) -> dict:
        """返回session设置"""
        if self._session_options is None:
            self._session_options = self.get_option('session_options')

        return self._session_options

    def get_value(self, section: str, item: str) -> Any:
        """获取配置的值         \n
        :param section: 段名
        :param item: 项名
        :return: 项值
        """
        try:
            return eval(self._conf.get(section, item))
        except (SyntaxError, NameError):
            return self._conf.get(section, item)
        except NoSectionError and NoOptionError:
            return None

    def get_option(self, section: str) -> dict:
        """把section内容以字典方式返回   \n
        :param section: 段名
        :return: 段内容生成的字典
        """
        items = self._conf.items(section)
        option = dict()

        for j in items:
            try:
                option[j[0]] = eval(self._conf.get(section, j[0]))
            except Exception:
                option[j[0]] = self._conf.get(section, j[0])

        return option

    def set_item(self, section: str, item: str, value: Any):
        """设置配置值            \n
        :param section: 段名
        :param item: 项名
        :param value: 项值
        :return: 当前对象
        """
        self._conf.set(section, item, str(value))
        self.__setattr__(f'_{section}', None)
        return self

    def save(self, path: str = None) -> str:
        """保存配置文件                                               \n
        :param path: ini文件的路径，传入 'default' 保存到默认ini文件
        :return: 保存路径
        """
        default_path = (Path(__file__).parent / 'configs.ini').absolute()
        if path == 'default':
            path = default_path
        elif path is None:
            path = Path(self.ini_path).absolute()
        else:
            path = Path(path).absolute()

        path = path / 'config.ini' if path.is_dir() else path

        path = str(path)
        self._conf.write(open(path, 'w', encoding='utf-8'))

        print(f'配置已保存到文件：{path}')
        if path == str(default_path):
            print('以后程序可自动从文件加载配置。')

        return path

    def save_to_default(self) -> str:
        """保存当前配置到默认ini文件"""
        return self.save('default')


class SessionOptions(object):
    def __init__(self, read_file: bool = True, ini_path: str = None):
        """requests的Session对象配置类             \n
        :param read_file: 是否从文件读取配置
        :param ini_path: ini文件路径
        """
        self.ini_path = None
        self._headers = None
        self._cookies = None
        self._auth = None
        self._proxies = None
        self._hooks = None
        self._params = None
        self._verify = None
        self._cert = None
        self._adapters = None
        self._stream = None
        self._trust_env = None
        self._max_redirects = None

        if read_file:
            self.ini_path = ini_path or str(Path(__file__).parent / 'configs.ini')
            om = OptionsManager(self.ini_path)
            options_dict = om.session_options

            if options_dict.get('headers', None) is not None:
                self._headers = {key.lower(): options_dict['headers'][key] for key in options_dict['headers']}

            if options_dict.get('cookies', None) is not None:
                self._cookies = options_dict['cookies']

            if options_dict.get('auth', None) is not None:
                self._auth = options_dict['auth']

            if options_dict.get('proxies', None) is not None:
                self._proxies = options_dict['proxies']

            if options_dict.get('hooks', None) is not None:
                self._hooks = options_dict['hooks']

            if options_dict.get('params', None) is not None:
                self._params = options_dict['params']

            if options_dict.get('verify', None) is not None:
                self._verify = options_dict['verify']

            if options_dict.get('cert', None) is not None:
                self._cert = options_dict['cert']

            # if options_dict.get('adapters', None) is not None:
            #     self._adapters = options_dict['adapters']

            if options_dict.get('stream', None) is not None:
                self._stream = options_dict['stream']

            if options_dict.get('trust_env', None) is not None:
                self._trust_env = options_dict['trust_env']

            if options_dict.get('max_redirects', None) is not None:
                self._max_redirects = options_dict['max_redirects']

    @property
    def headers(self) -> dict:
        """返回headers设置信息"""
        if self._headers is None:
            self._headers = {}
        return self._headers

    @property
    def cookies(self) -> list:
        """返回cookies设置信息"""
        if self._cookies is None:
            self._cookies = []

        return self._cookies

    @property
    def auth(self) -> tuple:
        """返回auth设置信息"""
        return self._auth

    @property
    def proxies(self) -> dict:
        """返回proxies设置信息"""
        if self._proxies is None:
            self._proxies = {}

        return self._proxies

    @property
    def hooks(self) -> dict:
        """返回hooks设置信息"""
        if self._hooks is None:
            self._hooks = {}

        return self._hooks

    @property
    def params(self) -> dict:
        """返回params设置信息"""
        if self._params is None:
            self._params = {}
        return self._params

    @property
    def verify(self) -> bool:
        """返回verify设置信息"""
        return self._verify

    @property
    def cert(self) -> Union[str, tuple]:
        """返回cert设置信息"""
        return self._cert

    @property
    def adapters(self):
        """返回adapters设置信息"""
        return self._adapters

    @property
    def stream(self) -> bool:
        """返回stream设置信息"""
        return self._stream

    @property
    def trust_env(self) -> bool:
        """返回trust_env设置信息"""
        return self._trust_env

    @property
    def max_redirects(self) -> int:
        """返回max_redirects设置信息"""
        return self._max_redirects

    @headers.setter
    def headers(self, headers: dict) -> None:
        """设置headers参数           \n
        :param headers: 参数值
        :return: None
        """
        self.set_headers(headers)

    @cookies.setter
    def cookies(self, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None:
        """设置cookies参数           \n
        :param cookies: 参数值
        :return: None
        """
        self._cookies = cookies

    @auth.setter
    def auth(self, auth: tuple) -> None:
        """设置auth参数           \n
        :param auth: 参数值
        :return: None
        """
        self._auth = auth

    @proxies.setter
    def proxies(self, proxies: dict) -> None:
        """设置proxies参数           \n
        :param proxies: 参数值
        :return: None
        """
        self.set_proxies(proxies)

    @hooks.setter
    def hooks(self, hooks: dict) -> None:
        """设置hooks参数           \n
        :param hooks: 参数值
        :return: None
        """
        self._hooks = hooks

    @params.setter
    def params(self, params: dict) -> None:
        """设置params参数           \n
        :param params: 参数值
        :return: None
        """
        self._params = params

    @verify.setter
    def verify(self, verify: bool) -> None:
        """设置verify参数           \n
        :param verify: 参数值
        :return: None
        """
        self._verify = verify

    @cert.setter
    def cert(self, cert: Union[str, tuple]) -> None:
        """设置cert参数           \n
        :param cert: 参数值
        :return: None
        """
        self._cert = cert

    @adapters.setter
    def adapters(self, adapters) -> None:
        """设置           \n
        :param adapters: 参数值
        :return: None
        """
        self._adapters = adapters

    @stream.setter
    def stream(self, stream: bool) -> None:
        """设置stream参数           \n
        :param stream: 参数值
        :return: None
        """
        self._stream = stream

    @trust_env.setter
    def trust_env(self, trust_env: bool) -> None:
        """设置trust_env参数           \n
        :param trust_env: 参数值
        :return: None
        """
        self._trust_env = trust_env

    @max_redirects.setter
    def max_redirects(self, max_redirects: int) -> None:
        """设置max_redirects参数          \n
        :param max_redirects: 参数值
        :return: None
        """
        self._max_redirects = max_redirects

    def set_headers(self, headers: dict) -> 'SessionOptions':
        """设置headers参数           \n
        :param headers: 参数值
        :return: 返回当前对象
        """
        self._headers = {key.lower(): headers[key] for key in headers}
        return self

    def set_a_header(self, attr: str, value: str) -> 'SessionOptions':
        """设置headers中一个项          \n
        :param attr: 设置名称
        :param value: 设置值
        :return: 返回当前对象
        """
        if self._headers is None:
            self._headers = {}

        self._headers[attr.lower()] = value
        return self

    def remove_a_header(self, attr: str) -> 'SessionOptions':
        """从headers中删除一个设置     \n
        :param attr: 要删除的设置
        :return: 返回当前对象
        """
        if self._headers is None:
            return self

        attr = attr.lower()
        if attr in self._headers:
            self._headers.pop(attr)

        return self

    def set_proxies(self, proxies: dict) -> 'SessionOptions':
        """设置proxies参数           \n
        {'http': 'http://xx.xx.xx.xx:xxxx',
         'https': 'http://xx.xx.xx.xx:xxxx'}
        :param proxies: 参数值
        :return: None
        """
        self._proxies = proxies
        return self

    def save(self, path: str = None) -> str:
        """保存设置到文件                                              \n
        :param path: ini文件的路径，传入 'default' 保存到默认ini文件
        :return: 保存文件的绝对路径
        """
        if path == 'default':
            path = (Path(__file__).parent / 'configs.ini').absolute()

        elif path is None:
            if self.ini_path:
                path = Path(self.ini_path).absolute()
            else:
                path = (Path(__file__).parent / 'configs.ini').absolute()

        else:
            path = Path(path).absolute()

        path = path / 'config.ini' if path.is_dir() else path

        if path.exists():
            om = OptionsManager(str(path))
        else:
            om = OptionsManager(self.ini_path or str(Path(__file__).parent / 'configs.ini'))

        options = _session_options_to_dict(self)

        for i in options:
            om.set_item('session_options', i, options[i])

        path = str(path)
        om.save(path)

        return path

    def save_to_default(self) -> str:
        """保存当前配置到默认ini文件"""
        return self.save('default')

    def as_dict(self) -> dict:
        """以字典形式返回本对象"""
        return _session_options_to_dict(self)


class DriverOptions(Options):
    """chrome浏览器配置类，继承自selenium.webdriver.chrome.options的Options类，
    增加了删除配置和保存到文件方法。
    """

    def __init__(self, read_file: bool = True, ini_path: str = None):
        """初始化，默认从文件读取设置                      \n
        :param read_file: 是否从默认ini文件中读取配置信息
        :param ini_path: ini文件路径，为None则读取默认ini文件
        """
        super().__init__()
        self._driver_path = None
        self.ini_path = None

        if read_file:
            self.ini_path = ini_path or str(Path(__file__).parent / 'configs.ini')
            om = OptionsManager(self.ini_path)
            options_dict = om.chrome_options

            self._driver_path = om.paths.get('chromedriver_path', None)
            self._binary_location = options_dict.get('binary_location', '')
            self._arguments = options_dict.get('arguments', [])
            self._extensions = options_dict.get('extensions', [])
            self._experimental_options = options_dict.get('experimental_options', {})
            self._debugger_address = options_dict.get('debugger_address', None)
            self.set_window_rect = options_dict.get('set_window_rect', None)
            self.page_load_strategy = options_dict.get('page_load_strategy', 'normal')

            self.timeouts = options_dict.get('timeouts', {'implicit': 10, 'pageLoad': 30, 'script': 30})
            self.timeouts['implicit'] *= 1000
            self.timeouts['pageLoad'] *= 1000
            self.timeouts['script'] *= 1000

    @property
    def driver_path(self) -> str:
        """chromedriver文件路径"""
        return self._driver_path

    @property
    def chrome_path(self) -> str:
        """浏览器启动文件路径"""
        return self.binary_location

    def save(self, path: str = None) -> str:
        """保存设置到文件                                                                        \n
        :param path: ini文件的路径， None 保存到当前读取的配置文件，传入 'default' 保存到默认ini文件
        :return: 保存文件的绝对路径
        """
        if path == 'default':
            path = (Path(__file__).parent / 'configs.ini').absolute()

        elif path is None:
            if self.ini_path:
                path = Path(self.ini_path).absolute()
            else:
                path = (Path(__file__).parent / 'configs.ini').absolute()

        else:
            path = Path(path).absolute()

        path = path / 'config.ini' if path.is_dir() else path

        if path.exists():
            om = OptionsManager(str(path))
        else:
            om = OptionsManager(self.ini_path or str(Path(__file__).parent / 'configs.ini'))

        options = self.as_dict()

        for i in options:
            if i == 'driver_path':
                om.set_item('paths', 'chromedriver_path', options[i])
            else:
                om.set_item('chrome_options', i, options[i])

        path = str(path)
        om.save(path)

        return path

    def save_to_default(self) -> str:
        """保存当前配置到默认ini文件"""
        return self.save('default')

    def remove_argument(self, value: str) -> 'DriverOptions':
        """移除一个argument项                                    \n
        :param value: 设置项名，有值的设置项传入设置名称即可
        :return: 当前对象
        """
        del_list = []

        for argument in self._arguments:
            if argument.startswith(value):
                del_list.append(argument)

        for del_arg in del_list:
            self._arguments.remove(del_arg)

        return self

    def remove_experimental_option(self, key: str) -> 'DriverOptions':
        """移除一个实验设置，传入key值删除  \n
        :param key: 实验设置的名称
        :return: 当前对象
        """
        if key in self._experimental_options:
            self._experimental_options.pop(key)

        return self

    def remove_all_extensions(self) -> 'DriverOptions':
        """移除所有插件             \n
        :return: 当前对象
        """
        # 因插件是以整个文件储存，难以移除其中一个，故如须设置则全部移除再重设
        self._extensions = []
        return self

    def set_argument(self, arg: str, value: Union[bool, str]) -> 'DriverOptions':
        """设置浏览器配置的argument属性                          \n
        :param arg: 属性名
        :param value: 属性值，有值的属性传入值，没有的传入bool
        :return: 当前对象
        """
        self.remove_argument(arg)

        if value:
            arg_str = arg if isinstance(value, bool) else f'{arg}={value}'
            self.add_argument(arg_str)

        return self

    def set_timeouts(self, implicit: float = None, pageLoad: float = None, script: float = None) -> 'DriverOptions':
        """设置超时时间，设置单位为秒，selenium4以上版本有效       \n
        :param implicit: 查找元素超时时间
        :param pageLoad: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: 当前对象
        """
        timeouts = self._caps.get('timeouts', {'implicit': 10, 'pageLoad': 3000, 'script': 3000})
        if implicit is not None:
            timeouts['implicit'] = implicit
        if pageLoad is not None:
            timeouts['pageLoad'] = pageLoad * 1000
        if script is not None:
            timeouts['script'] = script * 1000
        self.timeouts = timeouts

        return self

    def set_headless(self, on_off: bool = True) -> 'DriverOptions':
        """设置是否隐藏浏览器界面   \n
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = True if on_off else False
        return self.set_argument('--headless', on_off)

    def set_no_imgs(self, on_off: bool = True) -> 'DriverOptions':
        """设置是否加载图片           \n
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = True if on_off else False
        return self.set_argument('--blink-settings=imagesEnabled=false', on_off)

    def set_no_js(self, on_off: bool = True) -> 'DriverOptions':
        """设置是否禁用js       \n
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = True if on_off else False
        return self.set_argument('--disable-javascript', on_off)

    def set_mute(self, on_off: bool = True) -> 'DriverOptions':
        """设置是否静音            \n
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = True if on_off else False
        return self.set_argument('--mute-audio', on_off)

    def set_user_agent(self, user_agent: str) -> 'DriverOptions':
        """设置user agent                  \n
        :param user_agent: user agent文本
        :return: 当前对象
        """
        return self.set_argument('user-agent', user_agent)

    def set_proxy(self, proxy: str) -> 'DriverOptions':
        """设置代理                    \n
        :param proxy: 代理url和端口
        :return: 当前对象
        """
        return self.set_argument('--proxy-server', proxy)

    def set_page_load_strategy(self, value: str) -> 'DriverOptions':
        """设置page_load_strategy，可接收 'normal', 'eager', 'none'                    \n
        selenium4以上版本才支持此功能
        normal：默认情况下使用, 等待所有资源下载完成
        eager：DOM访问已准备就绪, 但其他资源 (如图像) 可能仍在加载中
        none：完全不阻塞WebDriver
        :param value: 可接收 'normal', 'eager', 'none'
        :return: 当前对象
        """
        self.page_load_strategy = value.lower()
        return self

    def set_paths(self,
                  driver_path: str = None,
                  chrome_path: str = None,
                  local_port: Union[int, str] = None,
                  debugger_address: str = None,
                  download_path: str = None,
                  user_data_path: str = None,
                  cache_path: str = None) -> 'DriverOptions':
        """快捷的路径设置函数                                             \n
        :param driver_path: chromedriver.exe路径
        :param chrome_path: chrome.exe路径
        :param local_port: 本地端口号
        :param debugger_address: 调试浏览器地址，例：127.0.0.1:9222
        :param download_path: 下载文件路径
        :param user_data_path: 用户数据路径
        :param cache_path: 缓存路径
        :return: 当前对象
        """
        if driver_path is not None:
            self._driver_path = driver_path

        if chrome_path is not None:
            self.binary_location = chrome_path

        if local_port is not None:
            self.debugger_address = f'127.0.0.1:{local_port}'

        if debugger_address is not None:
            self.debugger_address = debugger_address

        if download_path is not None:
            self.experimental_options['prefs']['download.default_directory'] = download_path

        if user_data_path is not None:
            self.set_argument('--user-data-dir', user_data_path)

        if cache_path is not None:
            self.set_argument('--disk-cache-dir', cache_path)

        return self

    def as_dict(self) -> dict:
        """已dict方式返回所有配置信息"""
        return _chrome_options_to_dict(self)


def _chrome_options_to_dict(options: Union[dict, DriverOptions, Options, None, bool]) -> Union[dict, None]:
    """把chrome配置对象转换为字典                             \n
    :param options: chrome配置对象，字典或DriverOptions对象
    :return: 配置字典
    """
    if options in (False, None):
        return DriverOptions(read_file=False).as_dict()

    if isinstance(options, dict):
        return options

    re_dict = dict()
    attrs = ['debugger_address', 'binary_location', 'arguments', 'extensions', 'experimental_options', 'driver_path',
             'set_window_rect', 'page_load_strategy']

    options_dir = options.__dir__()
    for attr in attrs:
        try:
            re_dict[attr] = options.__getattribute__(f'{attr}') if attr in options_dir else None
        except Exception:
            pass

    if 'timeouts' in options_dir and 'timeouts' in options._caps:
        timeouts = options.__getattribute__('timeouts')
        timeouts['implicit'] /= 1000
        timeouts['pageLoad'] /= 1000
        timeouts['script'] /= 1000
        re_dict['timeouts'] = timeouts

    return re_dict


def _session_options_to_dict(options: Union[dict, SessionOptions, None]) -> Union[dict, None]:
    """把session配置对象转换为字典                 \n
    :param options: session配置对象或字典
    :return: 配置字典
    """
    if options in (False, None):
        return SessionOptions(read_file=False).as_dict()

    if isinstance(options, dict):
        return options

    re_dict = dict()
    attrs = ['headers', 'proxies', 'hooks', 'params', 'verify', 'stream', 'trust_env', 'max_redirects']  # 'adapters',

    cookies = options.__getattribute__('_cookies')

    if cookies is not None:
        re_dict['cookies'] = _cookies_to_tuple(cookies)

    for attr in attrs:
        val = options.__getattribute__(f'_{attr}')
        if val is not None:
            re_dict[attr] = val

    # cert属性默认值为None，为免无法区分是否被设置，故主动赋值
    re_dict['cert'] = options.__getattribute__('_cert')
    re_dict['auth'] = options.__getattribute__('_auth')

    return re_dict


def _cookie_to_dict(cookie: Union[Cookie, str, dict]) -> dict:
    """把Cookie对象转为dict格式                \n
    :param cookie: Cookie对象
    :return: cookie字典
    """
    if isinstance(cookie, Cookie):
        cookie_dict = cookie.__dict__.copy()
        cookie_dict.pop('rfc2109')
        cookie_dict.pop('_rest')
        return cookie_dict

    elif isinstance(cookie, dict):
        cookie_dict = cookie

    elif isinstance(cookie, str):
        cookie = cookie.split(',' if ',' in cookie else ';')
        cookie_dict = {}

        for key, attr in enumerate(cookie):
            attr_val = attr.lstrip().split('=')

            if key == 0:
                cookie_dict['name'] = attr_val[0]
                cookie_dict['value'] = attr_val[1] if len(attr_val) == 2 else ''
            else:
                cookie_dict[attr_val[0]] = attr_val[1] if len(attr_val) == 2 else ''

        return cookie_dict

    else:
        raise TypeError('cookie参数必须为Cookie、str或dict类型。')

    return cookie_dict


def _cookies_to_tuple(cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> tuple:
    """把cookies转为tuple格式                                                \n
    :param cookies: cookies信息，可为CookieJar, list, tuple, str, dict
    :return: 返回tuple形式的cookies
    """
    if isinstance(cookies, (list, tuple, RequestsCookieJar)):
        cookies = tuple(_cookie_to_dict(cookie) for cookie in cookies)

    elif isinstance(cookies, str):
        cookies = tuple(_cookie_to_dict(cookie.lstrip()) for cookie in cookies.split(";"))

    elif isinstance(cookies, dict):
        cookies = tuple({'name': cookie, 'value': cookies[cookie]} for cookie in cookies)

    else:
        raise TypeError('cookies参数必须为RequestsCookieJar、list、tuple、str或dict类型。')

    return cookies
