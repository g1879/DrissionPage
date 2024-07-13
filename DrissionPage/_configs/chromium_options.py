# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path
from re import search

from .options_manage import OptionsManager


class ChromiumOptions(object):
    def __init__(self, read_file=True, ini_path=None):
        """
        :param read_file: 是否从默认ini文件中读取配置信息
        :param ini_path: ini文件路径，为None则读取默认ini文件
        """
        self._user_data_path = None
        self._user = 'Default'
        self._prefs_to_del = []
        self.clear_file_flags = False
        self._headless = None

        if read_file is False:
            ini_path = False
            self.ini_path = None
        elif ini_path:
            ini_path = Path(ini_path).absolute()
            if not ini_path.exists():
                raise ValueError(f'文件不存在：{ini_path}')
            self.ini_path = str(ini_path)
        else:
            self.ini_path = str(Path(__file__).parent / 'configs.ini')
        om = OptionsManager(ini_path)

        options = om.chromium_options
        self._download_path = om.paths.get('download_path', None) or None
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

    @property
    def download_path(self):
        """默认下载路径文件路径"""
        return self._download_path

    @property
    def browser_path(self):
        """浏览器启动文件路径"""
        return self._browser_path

    @property
    def user_data_path(self):
        """返回用户数据文件夹路径"""
        return self._user_data_path

    @property
    def tmp_path(self):
        """返回临时文件夹路径"""
        return self._tmp_path

    @property
    def user(self):
        """返回用户配置文件夹名称"""
        return self._user

    @property
    def load_mode(self):
        """返回页面加载策略，'normal', 'eager', 'none'"""
        return self._load_mode

    @property
    def timeouts(self):
        """返回timeouts设置"""
        return self._timeouts

    @property
    def proxy(self):
        """返回代理设置"""
        return self._proxy

    @property
    def address(self):
        """返回浏览器地址，ip:port"""
        return self._address

    @property
    def arguments(self):
        """返回浏览器命令行设置列表"""
        return self._arguments

    @property
    def extensions(self):
        """以list形式返回要加载的插件路径"""
        return self._extensions

    @property
    def preferences(self):
        """返回用户首选项配置"""
        return self._prefs

    @property
    def flags(self):
        """返回实验项配置"""
        return self._flags

    @property
    def system_user_path(self):
        """返回是否使用系统安装的浏览器所使用的用户数据文件夹"""
        return self._system_user_path

    @property
    def is_existing_only(self):
        """返回是否只接管现有浏览器方式"""
        return self._existing_only

    @property
    def is_auto_port(self):
        """返回是否使用自动端口和用户文件，如指定范围则返回范围tuple"""
        return self._auto_port

    @property
    def retry_times(self):
        """返回连接失败时的重试次数"""
        return self._retry_times

    @property
    def retry_interval(self):
        """返回连接失败时的重试间隔（秒）"""
        return self._retry_interval

    def set_retry(self, times=None, interval=None):
        """设置连接失败时的重试操作
        :param times: 重试次数
        :param interval: 重试间隔
        :return: 当前对象
        """
        if times is not None:
            self._retry_times = times
        if interval is not None:
            self._retry_interval = interval
        return self

    def set_argument(self, arg, value=None):
        """设置浏览器配置的argument属性
        :param arg: 属性名
        :param value: 属性值，有值的属性传入值，没有的传入None，如传入False，删除该项
        :return: 当前对象
        """
        self.remove_argument(arg)
        if value is not False:
            if arg == '--headless' and value is None:
                self._arguments.append('--headless=new')
            else:
                arg_str = arg if value is None else f'{arg}={value}'
                self._arguments.append(arg_str)
        return self

    def remove_argument(self, value):
        """移除一个argument项
        :param value: 设置项名，有值的设置项传入设置名称即可
        :return: 当前对象
        """
        elements_to_delete = tuple(
            arg for arg in self._arguments 
            if arg == value or arg.startswith(f'{value}=')
        )
        if len(elements_to_delete) == 0:
            return self

        if len(elements_to_delete) == 1:
            self._arguments.remove(elements_to_delete[0])
        else:
            self._arguments = [
                arg for arg in self._arguments 
                if arg not in elements_to_delete
            ]
        return self

    def add_extension(self, path):
        """添加插件
        :param path: 插件路径，可指向文件夹
        :return: 当前对象
        """
        path = Path(path)
        if not path.exists():
            raise OSError('插件路径不存在。')
        self._extensions.append(str(path))
        return self

    def remove_extensions(self):
        """移除所有插件
        :return: 当前对象
        """
        self._extensions = []
        return self

    def set_pref(self, arg, value):
        """设置Preferences文件中的用户设置项
        :param arg: 设置项名称
        :param value: 设置项值
        :return: 当前对象
        """
        self._prefs[arg] = value
        return self

    def remove_pref(self, arg):
        """删除用户首选项设置，不能删除已设置到文件中的项
        :param arg: 设置项名称
        :return: 当前对象
        """
        self._prefs.pop(arg, None)
        return self

    def remove_pref_from_file(self, arg):
        """删除用户配置文件中已设置的项
        :param arg: 设置项名称
        :return: 当前对象
        """
        self._prefs_to_del.append(arg)
        return self

    def set_flag(self, flag, value=None):
        """设置实验项
        :param flag: 设置项名称
        :param value: 设置项的值，为False则删除该项
        :return: 当前对象
        """
        if value is False:
            self._flags.pop(flag, None)
        else:
            self._flags[flag] = value
        return self

    def clear_flags_in_file(self):
        """删除浏览器配置文件中已设置的实验项"""
        self.clear_file_flags = True
        return self

    def clear_flags(self):
        """清空本对象已设置的flag参数"""
        self._flags = {}
        return self

    def clear_arguments(self):
        """清空本对象已设置的argument参数"""
        self._arguments = []
        return self

    def clear_prefs(self):
        """清空本对象已设置的pref参数"""
        self._prefs = {}
        return self

    def set_timeouts(self, base=None, page_load=None, script=None, implicit=None):
        """设置超时时间，单位为秒
        :param base: 默认超时时间
        :param page_load: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: 当前对象
        """
        base = base if base is not None else implicit
        if base is not None:
            self._timeouts['base'] = base
        if page_load is not None:
            self._timeouts['page_load'] = page_load
        if script is not None:
            self._timeouts['script'] = script

        return self

    def set_user(self, user='Default'):
        """设置使用哪个用户配置文件夹
        :param user: 用户文件夹名称
        :return: 当前对象
        """
        self.set_argument('--profile-directory', user)
        self._user = user
        return self

    def headless(self, on_off=True):
        """设置是否隐藏浏览器界面
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = 'new' if on_off else 'false'
        return self.set_argument('--headless', on_off)

    def no_imgs(self, on_off=True):
        """设置是否加载图片
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = None if on_off else False
        return self.set_argument('--blink-settings=imagesEnabled=false', on_off)

    def no_js(self, on_off=True):
        """设置是否禁用js
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = None if on_off else False
        return self.set_argument('--disable-javascript', on_off)

    def mute(self, on_off=True):
        """设置是否静音
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = None if on_off else False
        return self.set_argument('--mute-audio', on_off)

    def incognito(self, on_off=True):
        """设置是否使用无痕模式启动
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = None if on_off else False
        return self.set_argument('--incognito', on_off)

    def ignore_certificate_errors(self, on_off=True):
        """设置是否忽略证书错误
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = None if on_off else False
        return self.set_argument('--ignore-certificate-errors', on_off)

    def set_user_agent(self, user_agent):
        """设置user agent
        :param user_agent: user agent文本
        :return: 当前对象
        """
        return self.set_argument('--user-agent', user_agent)

    def set_proxy(self, proxy):
        """设置代理
        :param proxy: 代理url和端口
        :return: 当前对象
        """
        if search(r'.*?:.*?@.*?\..*', proxy):
            print('你似乎在设置使用账号密码的代理，暂时不支持这种代理，可自行用插件实现需求。')
        if proxy.lower().startswith('socks'):
            print('你似乎在设置使用socks代理，暂时不支持这种代理，可自行用插件实现需求。')
        self._proxy = proxy
        return self.set_argument('--proxy-server', proxy)

    def set_load_mode(self, value):
        """设置load_mode，可接收 'normal', 'eager', 'none'
        normal：默认情况下使用, 等待所有资源下载完成
        eager：DOM访问已准备就绪, 但其他资源 (如图像) 可能仍在加载中
        none：完全不阻塞
        :param value: 可接收 'normal', 'eager', 'none'
        :return: 当前对象
        """
        if value not in ('normal', 'eager', 'none'):
            raise ValueError("只能选择 'normal', 'eager', 'none'。")
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
        """设置本地启动端口
        :param port: 端口号
        :return: 当前对象
        """
        self._address = f'127.0.0.1:{port}'
        self._auto_port = False
        return self

    def set_address(self, address):
        """设置浏览器地址，格式'ip:port'
        :param address: 浏览器地址
        :return: 当前对象
        """
        address = address.replace('localhost', '127.0.0.1').lstrip('http://').lstrip('https://')
        self._address = address
        return self

    def set_browser_path(self, path):
        """设置浏览器可执行文件路径
        :param path: 浏览器路径
        :return: 当前对象
        """
        self._browser_path = str(path)
        return self

    def set_download_path(self, path):
        """设置下载文件保存路径
        :param path: 下载路径
        :return: 当前对象
        """
        self._download_path = str(path)
        return self

    def set_tmp_path(self, path):
        """设置临时文件文件保存路径
        :param path: 下载路径
        :return: 当前对象
        """
        self._tmp_path = str(path)
        return self

    def set_user_data_path(self, path):
        """设置用户文件夹路径
        :param path: 用户文件夹路径
        :return: 当前对象
        """
        u = str(path)
        self.set_argument('--user-data-dir', u)
        self._user_data_path = u
        self._auto_port = False
        return self

    def set_cache_path(self, path):
        """设置缓存路径
        :param path: 缓存路径
        :return: 当前对象
        """
        self.set_argument('--disk-cache-dir', str(path))
        return self

    def use_system_user_path(self, on_off=True):
        """设置是否使用系统安装的浏览器默认用户文件夹
        :param on_off: 开或关
        :return: 当前对象
        """
        self._system_user_path = on_off
        return self

    def auto_port(self, on_off=True, tmp_path=None, scope=None):
        """自动获取可用端口
        :param on_off: 是否开启自动获取端口号
        :param tmp_path: 临时文件保存路径，为None时保存到系统临时文件夹，on_off为False时此参数无效
        :param scope: 指定端口范围，不含最后的数字，为None则使用[9600-19600)
        :return: 当前对象
        """
        if on_off:
            self._auto_port = scope if scope else True
            if tmp_path:
                self._tmp_path = str(tmp_path)
        else:
            self._auto_port = False
        return self

    def existing_only(self, on_off=True):
        """设置只接管已有浏览器，不自动启动新的
        :param on_off: 是否开启自动获取端口号
        :return: 当前对象
        """
        self._existing_only = on_off
        return self

    def save(self, path=None):
        """保存设置到文件
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
            om = OptionsManager(path)
        else:
            om = OptionsManager(self.ini_path or (Path(__file__).parent / 'configs.ini'))

        # 设置chromium_options
        attrs = ('address', 'browser_path', 'arguments', 'extensions', 'user', 'load_mode',
                 'auto_port', 'system_user_path', 'existing_only', 'flags')
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
        """保存当前配置到默认ini文件"""
        return self.save('default')

    def __repr__(self):
        return f'<ChromiumOptions at {id(self)}>'
