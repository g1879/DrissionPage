# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from tempfile import gettempdir, TemporaryDirectory

from DrissionPage.commons.tools import port_is_using, clean_folder
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

        if read_file is not False:
            ini_path = str(ini_path) if ini_path else None
            om = OptionsManager(ini_path)
            self.ini_path = om.ini_path
            options = om.chrome_options

            self._download_path = om.paths.get('download_path', None)
            self._arguments = options.get('arguments', [])
            self._binary_location = options.get('binary_location', '')
            self._extensions = options.get('extensions', [])
            self._prefs = options.get('experimental_options', {}).get('prefs', {})
            self._debugger_address = options.get('debugger_address', None)
            self._page_load_strategy = options.get('page_load_strategy', 'normal')
            self._proxy = om.proxies.get('http', None)
            self._system_user_path = options.get('system_user_path', False)

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
            self._timeouts = {'implicit': timeouts['implicit'],
                              'pageLoad': timeouts['page_load'],
                              'script': timeouts['script']}

            self._auto_port = options.get('auto_port', False)
            if self._auto_port:
                port, path = PortFinder().get_port()
                self._debugger_address = f'127.0.0.1:{port}'
                self.set_argument('--user-data-dir', path)
            return

        self.ini_path = None
        self._binary_location = "chrome"
        self._arguments = []
        self._download_path = None
        self._extensions = []
        self._prefs = {}
        self._timeouts = {'implicit': 10, 'pageLoad': 30, 'script': 30}
        self._debugger_address = '127.0.0.1:9222'
        self._page_load_strategy = 'normal'
        self._proxy = None
        self._auto_port = False
        self._system_user_path = False

    @property
    def download_path(self):
        """默认下载路径文件路径"""
        return self._download_path

    @property
    def browser_path(self):
        """浏览器启动文件路径"""
        return self._binary_location

    @property
    def user_data_path(self):
        """返回用户数据文件夹路径"""
        return self._user_data_path

    @property
    def user(self):
        """返回用户配置文件夹名称"""
        return self._user

    @property
    def page_load_strategy(self):
        """返回页面加载策略，'normal', 'eager', 'none'"""
        return self._page_load_strategy

    @property
    def timeouts(self):
        """返回timeouts设置"""
        return self._timeouts

    @property
    def proxy(self):
        """返回代理设置"""
        return self._proxy

    @property
    def debugger_address(self):
        """返回浏览器地址，ip:port"""
        return self._debugger_address

    @debugger_address.setter
    def debugger_address(self, address):
        """设置浏览器地址，格式ip:port"""
        address = address.replace('localhost', '127.0.0.1').lstrip('http://').lstrip('https://')
        self._debugger_address = address

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
    def system_user_path(self):
        """返回是否使用系统安装的浏览器所使用的用户数据文件夹"""
        return self._system_user_path

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
        del_list = []

        for argument in self._arguments:
            if argument == value or argument.startswith(f'{value}='):
                del_list.append(argument)

        for del_arg in del_list:
            self._arguments.remove(del_arg)

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
        self._prefs.pop(arg)
        return self

    def remove_pref_from_file(self, arg):
        """删除用户配置文件中已设置的项
        :param arg: 设置项名称
        :return: 当前对象
        """
        self._prefs_to_del.append(arg)
        return self

    def set_timeouts(self, implicit=None, pageLoad=None, script=None):
        """设置超时时间，单位为秒
        :param implicit: 默认超时时间
        :param pageLoad: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: 当前对象
        """
        if implicit is not None:
            self._timeouts['implicit'] = implicit
        if pageLoad is not None:
            self._timeouts['pageLoad'] = pageLoad
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

    def set_headless(self, on_off=True):
        """设置是否隐藏浏览器界面
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = 'new' if on_off else False
        return self.set_argument('--headless', on_off)

    def set_no_imgs(self, on_off=True):
        """设置是否加载图片
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = None if on_off else False
        return self.set_argument('--blink-settings=imagesEnabled=false', on_off)

    def set_no_js(self, on_off=True):
        """设置是否禁用js
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = None if on_off else False
        return self.set_argument('--disable-javascript', on_off)

    def set_mute(self, on_off=True):
        """设置是否静音
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = None if on_off else False
        return self.set_argument('--mute-audio', on_off)

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
        self._proxy = proxy
        return self.set_argument('--proxy-server', proxy)

    def set_page_load_strategy(self, value):
        """设置page_load_strategy，可接收 'normal', 'eager', 'none'
        normal：默认情况下使用, 等待所有资源下载完成
        eager：DOM访问已准备就绪, 但其他资源 (如图像) 可能仍在加载中
        none：完全不阻塞
        :param value: 可接收 'normal', 'eager', 'none'
        :return: 当前对象
        """
        if value not in ('normal', 'eager', 'none'):
            raise ValueError("只能选择'normal', 'eager', 'none'。")
        self._page_load_strategy = value.lower()
        return self

    def set_paths(self, browser_path=None, local_port=None, debugger_address=None, download_path=None,
                  user_data_path=None, cache_path=None):
        """快捷的路径设置函数
        :param browser_path: 浏览器可执行文件路径
        :param local_port: 本地端口号
        :param debugger_address: 调试浏览器地址，例：127.0.0.1:9222
        :param download_path: 下载文件路径
        :param user_data_path: 用户数据路径
        :param cache_path: 缓存路径
        :return: 当前对象
        """
        if browser_path is not None:
            self._binary_location = str(browser_path)
            self._auto_port = False

        if local_port is not None:
            self._debugger_address = f'127.0.0.1:{local_port}'
            self._auto_port = False

        if debugger_address is not None:
            self.debugger_address = debugger_address

        if download_path is not None:
            self._download_path = str(download_path)

        if user_data_path is not None:
            u = str(user_data_path)
            self.set_argument('--user-data-dir', u)
            self._user_data_path = u
            self._auto_port = False

        if cache_path is not None:
            self.set_argument('--disk-cache-dir', str(cache_path))

        return self

    def use_system_user_path(self, on_off=True):
        """设置是否使用系统安装的浏览器默认用户文件夹
        :param on_off: 开或关
        :return: 当前对象
        """
        self._system_user_path = on_off
        return self

    def auto_port(self, on_off=True):
        """自动获取可用端口
        :param on_off: 是否开启自动获取端口号
        :return: 当前对象
        """
        if on_off:
            port, path = PortFinder().get_port()
            self.set_paths(local_port=port, user_data_path=path)
            self._auto_port = True
        else:
            self._auto_port = False
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
            om = OptionsManager(str(path))
        else:
            om = OptionsManager(self.ini_path or str(Path(__file__).parent / 'configs.ini'))

        # 设置chrome_options
        attrs = ('debugger_address', 'binary_location', 'arguments', 'extensions', 'user', 'page_load_strategy',
                 'auto_port', 'system_user_path')
        for i in attrs:
            om.set_item('chrome_options', i, self.__getattribute__(f'_{i}'))
        # 设置代理
        om.set_item('proxies', 'http', self._proxy)
        om.set_item('proxies', 'https', self._proxy)
        # 设置路径
        om.set_item('paths', 'download_path', self._download_path)
        # 设置timeout
        om.set_item('timeouts', 'implicit', self._timeouts['implicit'])
        om.set_item('timeouts', 'page_load', self._timeouts['pageLoad'])
        om.set_item('timeouts', 'script', self._timeouts['script'])
        # 设置prefs
        eo = om.chrome_options.get('experimental_options', {})
        eo['prefs'] = self._prefs
        om.set_item('chrome_options', 'experimental_options', eo)

        path = str(path)
        om.save(path)

        return path

    def save_to_default(self):
        """保存当前配置到默认ini文件"""
        return self.save('default')


class PortFinder(object):
    used_port = []

    def __init__(self):
        self.tmp_dir = Path(gettempdir()) / 'DrissionPage' / 'TempFolder'
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        if not PortFinder.used_port:
            clean_folder(self.tmp_dir)

    def get_port(self):
        """查找一个可用端口
        :return: 可以使用的端口和用户文件夹路径组成的元组
        """
        for i in range(9600, 19800):
            if i in PortFinder.used_port or port_is_using('127.0.0.1', i):
                continue

            path = TemporaryDirectory(dir=self.tmp_dir)
            PortFinder.used_port.append(i)
            return i, path.name

        raise OSError('未找到可用端口。')
