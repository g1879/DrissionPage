# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from re import search

from .options_manage import OptionsManager
from .._functions.settings import Settings as _S


class ChromiumOptions(object):
    def __init__(self, read_file=True, ini_path=None):
        self._user_data_path = None
        self._user = 'Default'
        self._prefs_to_del = []
        self.clear_file_flags = False
        self._is_headless = False
        self._ua_set = False

        if read_file is False:
            ini_path = False
            self.ini_path = None
        elif ini_path:
            ini_path = Path(ini_path).absolute()
            if not ini_path.exists():
                raise FileNotFoundError(_S._lang.join(_S._lang.INI_NOT_FOUND, PATH=ini_path))
            self.ini_path = str(ini_path)
        else:
            self.ini_path = str(Path(__file__).parent / 'configs.ini')

        om = OptionsManager(ini_path)
        options = om.chromium_options
        self._download_path = om.paths.get('download_path', '.') or '.'
        self._tmp_path = om.paths.get('tmp_path', None) or None
        self._arguments = options.get('arguments', [])
        self._browser_path = options.get('browser_path', '')
        self._extensions = options.get('extensions', [])
        self._prefs = options.get('prefs', {})
        self._flags = options.get('flags', {})
        self._address = options.get('address', None)
        self._load_mode = options.get('load_mode', 'normal')
        self._system_user_path = options.get('system_user_path', False)
        self._existing_only = options.get('existing_only', False)
        self._new_env = options.get('new_env', False)
        for i in self._arguments:
            if i.startswith('--headless'):
                self._is_headless = True
                break

        self._proxy = om.proxies.get('http', None) or om.proxies.get('https', None)

        user_path = user = False
        for arg in self._arguments:
            if arg.startswith('--user-data-dir='):
                self.set_paths(user_data_path=arg[16:])
                user_path = True
            if arg.startswith('--profile-directory='):
                self.set_user(arg[20:])
                user = True
            if user and user_path:
                break

        timeouts = om.timeouts
        self._timeouts = {'base': timeouts['base'],
                          'page_load': timeouts['page_load'],
                          'script': timeouts['script']}

        self._auto_port = options.get('auto_port', False)

        others = om.others
        self._retry_times = others.get('retry_times', 3)
        self._retry_interval = others.get('retry_interval', 2)

        return

    def __repr__(self):
        return f'<ChromiumOptions at {id(self)}>'

    @property
    def download_path(self):
        return self._download_path

    @property
    def browser_path(self):
        return self._browser_path

    @property
    def user_data_path(self):
        return self._user_data_path

    @property
    def tmp_path(self):
        return self._tmp_path

    @property
    def user(self):
        return self._user

    @property
    def load_mode(self):
        return self._load_mode

    @property
    def timeouts(self):
        return self._timeouts

    @property
    def proxy(self):
        return self._proxy

    @property
    def address(self):
        return self._address

    @property
    def arguments(self):
        return self._arguments

    @property
    def extensions(self):
        return self._extensions

    @property
    def preferences(self):
        return self._prefs

    @property
    def flags(self):
        return self._flags

    @property
    def system_user_path(self):
        return self._system_user_path

    @property
    def is_existing_only(self):
        return self._existing_only

    @property
    def is_auto_port(self):
        return self._auto_port

    @property
    def retry_times(self):
        return self._retry_times

    @property
    def retry_interval(self):
        return self._retry_interval

    @property
    def is_headless(self):
        return self._is_headless

    def set_retry(self, times=None, interval=None):
        if times is not None:
            self._retry_times = times
        if interval is not None:
            self._retry_interval = interval
        return self

    def set_argument(self, arg, value=None):
        self.remove_argument(arg)
        if value is not False:
            if arg == '--headless':
                if value == 'false':
                    self._is_headless = False
                else:
                    if value is None:
                        value = 'new'
                    self._arguments.append(f'--headless={value}')
                    self._is_headless = True
            else:
                arg_str = arg if value is None else f'{arg}={value}'
                self._arguments.append(arg_str)
        elif arg == '--headless':
            self._is_headless = False
        return self

    def remove_argument(self, value):
        elements_to_delete = [arg for arg in self._arguments if arg == value or arg.startswith(f'{value}=')]
        if not elements_to_delete:
            return self

        if len(elements_to_delete) == 1:
            self._arguments.remove(elements_to_delete[0])
        else:
            self._arguments = [arg for arg in self._arguments if arg not in elements_to_delete]

        return self

    def add_extension(self, path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(_S._lang.join(_S._lang.EXT_NOT_FOUND, PATH=path))
        self._extensions.append(str(path))
        return self

    def remove_extensions(self):
        self._extensions = []
        return self

    def set_pref(self, arg, value):
        self._prefs[arg] = value
        return self

    def remove_pref(self, arg):
        self._prefs.pop(arg, None)
        return self

    def remove_pref_from_file(self, arg):
        self._prefs_to_del.append(arg)
        return self

    def set_flag(self, flag, value=None):
        if value is False:
            self._flags.pop(flag, None)
        else:
            self._flags[flag] = value
        return self

    def clear_flags_in_file(self):
        self.clear_file_flags = True
        return self

    def clear_flags(self):
        self._flags = {}
        return self

    def clear_arguments(self):
        self._arguments = []
        return self

    def clear_prefs(self):
        self._prefs = {}
        return self

    def set_timeouts(self, base=None, page_load=None, script=None):
        if base is not None:
            self._timeouts['base'] = base
        if page_load is not None:
            self._timeouts['page_load'] = page_load
        if script is not None:
            self._timeouts['script'] = script

        return self

    def set_user(self, user='Default'):
        self.set_argument('--profile-directory', user)
        self._user = user
        return self

    def headless(self, on_off=True):
        on_off = 'new' if on_off else on_off
        return self.set_argument('--headless', on_off)

    def no_imgs(self, on_off=True):
        on_off = None if on_off else False
        return self.set_argument('--blink-settings=imagesEnabled=false', on_off)

    def no_js(self, on_off=True):
        on_off = None if on_off else False
        return self.set_argument('--disable-javascript', on_off)

    def mute(self, on_off=True):
        on_off = None if on_off else False
        return self.set_argument('--mute-audio', on_off)

    def incognito(self, on_off=True):
        on_off = None if on_off else False
        self.set_argument('--incognito', on_off)
        return self.set_argument('--inprivate', on_off)  # edge

    def new_env(self, on_off=True):
        self._new_env = on_off
        return self

    def ignore_certificate_errors(self, on_off=True):
        on_off = None if on_off else False
        return self.set_argument('--ignore-certificate-errors', on_off)

    def set_user_agent(self, user_agent):
        return self.set_argument('--user-agent', user_agent)

    def set_proxy(self, proxy):
        if search(r'.*?:.*?@.*?\..*', proxy):
            print(_S._lang.UNSUPPORTED_USER_PROXY)
        if proxy.lower().startswith('socks'):
            print(_S._lang.UNSUPPORTED_SOCKS_PROXY)
        self._proxy = proxy
        return self.set_argument('--proxy-server', proxy)

    def set_load_mode(self, value):
        if value not in ('normal', 'eager', 'none'):
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_VAL_, 'value',
                                           ALLOW_VAL="'normal', 'eager', 'none'", CURR_VAL=value))
        self._load_mode = value.lower()
        return self

    def set_paths(self, browser_path=None, local_port=None, address=None, download_path=None,
                  user_data_path=None, cache_path=None):
        """快捷的路径设置函数
        :param browser_path: 浏览器可执行文件路径
        :param local_port: 本地端口号
        :param address: 调试浏览器地址，例：127.0.0.1:9222
        :param download_path: 下载文件路径
        :param user_data_path: 用户数据路径
        :param cache_path: 缓存路径
        :return: 当前对象
        """
        if browser_path is not None:
            self.set_browser_path(browser_path)

        if local_port is not None:
            self.set_local_port(local_port)

        if address is not None:
            self.set_address(address)

        if download_path is not None:
            self.set_download_path(download_path)

        if user_data_path is not None:
            self.set_user_data_path(user_data_path)

        if cache_path is not None:
            self.set_cache_path(cache_path)

        return self

    def set_local_port(self, port):
        self._address = f'127.0.0.1:{port}'
        self._auto_port = False
        return self

    def set_address(self, address):
        address = address.replace('localhost', '127.0.0.1').lstrip('htps:/')
        self._address = address
        return self

    def set_browser_path(self, path):
        self._browser_path = str(path)
        return self

    def set_download_path(self, path):
        self._download_path = '.' if path is None else str(path)
        return self

    def set_tmp_path(self, path):
        self._tmp_path = str(path)
        return self

    def set_user_data_path(self, path):
        u = str(path)
        self.set_argument('--user-data-dir', u)
        self._user_data_path = u
        self._auto_port = False
        return self

    def set_cache_path(self, path):
        self.set_argument('--disk-cache-dir', str(path))
        return self

    def use_system_user_path(self, on_off=True):
        self._system_user_path = on_off
        return self

    def auto_port(self, on_off=True, scope=None):
        if on_off:
            self._auto_port = scope if scope else (9600, 59600)
        else:
            self._auto_port = False
        return self

    def existing_only(self, on_off=True):
        self._existing_only = on_off
        return self

    def save(self, path=None):
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
            om = OptionsManager(path)
        else:
            om = OptionsManager(self.ini_path or (Path(__file__).parent / 'configs.ini'))

        # 设置chromium_options
        attrs = ('address', 'browser_path', 'arguments', 'extensions', 'user', 'load_mode',
                 'auto_port', 'system_user_path', 'existing_only', 'flags', 'new_env')
        for i in attrs:
            om.set_item('chromium_options', i, self.__getattribute__(f'_{i}'))
        # 设置代理
        om.set_item('proxies', 'http', self._proxy or '')
        om.set_item('proxies', 'https', self._proxy or '')
        # 设置路径
        om.set_item('paths', 'download_path', self._download_path or '')
        om.set_item('paths', 'tmp_path', self._tmp_path or '')
        # 设置timeout
        om.set_item('timeouts', 'base', self._timeouts['base'])
        om.set_item('timeouts', 'page_load', self._timeouts['page_load'])
        om.set_item('timeouts', 'script', self._timeouts['script'])
        # 设置重试
        om.set_item('others', 'retry_times', self.retry_times)
        om.set_item('others', 'retry_interval', self.retry_interval)
        # 设置prefs
        om.set_item('chromium_options', 'prefs', self._prefs)

        path = str(path)
        om.save(path)

        return path

    def save_to_default(self):
        return self.save('default')
