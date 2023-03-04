# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path

from selenium.webdriver.chrome.options import Options

from .options_manage import OptionsManager


class DriverOptions(Options):
    """chrome浏览器配置类，继承自selenium.webdriver.chrome.options的Options类，
    增加了删除配置和保存到文件方法。
    """

    def __init__(self, read_file=True, ini_path=None):
        """初始化，默认从文件读取设置
        :param read_file: 是否从默认ini文件中读取配置信息
        :param ini_path: ini文件路径，为None则读取默认ini文件
        """
        super().__init__()
        self._user_data_path = None

        if read_file:
            self.ini_path = str(ini_path) if ini_path else str(Path(__file__).parent / 'configs.ini')
            om = OptionsManager(self.ini_path)
            options_dict = om.chrome_options

            self._driver_path = om.paths.get('chromedriver_path', None)
            self._download_path = om.paths.get('download_path', None)
            self._binary_location = options_dict.get('binary_location', '')
            self._arguments = options_dict.get('arguments', [])
            self._extensions = options_dict.get('extensions', [])
            self._experimental_options = options_dict.get('experimental_options', {})
            self._debugger_address = options_dict.get('debugger_address', None)
            self.page_load_strategy = options_dict.get('page_load_strategy', 'normal')

            for arg in self._arguments:
                if arg.startswith('--user-data-dir='):
                    self.set_paths(user_data_path=arg[16:])
                    break

            self.timeouts = options_dict.get('timeouts', {'implicit': 10, 'pageLoad': 30, 'script': 30})
            return

        self._driver_path = None
        self._download_path = None
        self.ini_path = None
        self.timeouts = {'implicit': 10, 'pageLoad': 30, 'script': 30}
        self._debugger_address = '127.0.0.1:9222'

    @property
    def driver_path(self):
        """chromedriver文件路径"""
        return self._driver_path

    @property
    def download_path(self):
        """默认下载路径文件路径"""
        return self._download_path

    @property
    def chrome_path(self):
        """浏览器启动文件路径"""
        return self.browser_path

    @property
    def browser_path(self):
        """浏览器启动文件路径"""
        return self.binary_location or 'chrome'

    @property
    def user_data_path(self):
        """返回用户文件夹路径"""
        return self._user_data_path

    # -------------重写父类方法，实现链式操作-------------
    def add_argument(self, argument):
        """添加一个配置项
        :param argument: 配置项内容
        :return: 当前对象
        """
        super().add_argument(argument)
        return self

    def set_capability(self, name, value):
        """设置一个capability
        :param name: capability名称
        :param value: capability值
        :return: 当前对象
        """
        super().set_capability(name, value)
        return self

    def add_extension(self, extension):
        """添加插件
        :param extension: crx文件路径
        :return: 当前对象
        """
        super().add_extension(extension)
        return self

    def add_encoded_extension(self, extension):
        """将带有扩展数据的 Base64 编码字符串添加到将用于将其提取到 ChromeDriver 的列表中
        :param extension: 带有扩展数据的 Base64 编码字符串
        :return: 当前对象
        """
        super().add_encoded_extension(extension)
        return self

    def add_experimental_option(self, name, value):
        """添加一个实验选项到浏览器
        :param name: 选项名称
        :param value: 选项值
        :return: 当前对象
        """
        super().add_experimental_option(name, value)
        return self

    # -------------重写父类方法结束-------------

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

        options = self.as_dict()

        for i in options:
            if i == 'driver_path':
                om.set_item('paths', 'chromedriver_path', options[i])
            elif i == 'download_path':
                om.set_item('paths', 'download_path', options[i])
            else:
                om.set_item('chrome_options', i, options[i])

        path = str(path)
        om.save(path)

        return path

    def save_to_default(self):
        """保存当前配置到默认ini文件"""
        return self.save('default')

    def remove_argument(self, value):
        """移除一个argument项
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

    def remove_experimental_option(self, key):
        """移除一个实验设置，传入key值删除
        :param key: 实验设置的名称
        :return: 当前对象
        """
        if key in self._experimental_options:
            self._experimental_options.pop(key)

        return self

    def remove_all_extensions(self):
        """移除所有插件
        :return: 当前对象
        """
        # 因插件是以整个文件储存，难以移除其中一个，故如须设置则全部移除再重设
        self._extensions = []
        return self

    def set_argument(self, arg, value):
        """设置浏览器配置的argument属性
        :param arg: 属性名
        :param value: 属性值，有值的属性传入值，没有的传入bool
        :return: 当前对象
        """
        self.remove_argument(arg)

        if value:
            arg_str = arg if isinstance(value, bool) else f'{arg}={value}'
            self.add_argument(arg_str)

        return self

    def set_timeouts(self, implicit=None, pageLoad=None, script=None):
        """设置超时时间，设置单位为秒，selenium4以上版本有效
        :param implicit: 查找元素超时时间
        :param pageLoad: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: 当前对象
        """
        if implicit is not None:
            self.timeouts['implicit'] = implicit
        if pageLoad is not None:
            self.timeouts['pageLoad'] = pageLoad
        if script is not None:
            self.timeouts['script'] = script

        return self

    def set_headless(self, on_off=True):
        """设置是否隐藏浏览器界面
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = True if on_off else False
        return self.set_argument('--headless', on_off)

    def set_no_imgs(self, on_off=True):
        """设置是否加载图片
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = True if on_off else False
        return self.set_argument('--blink-settings=imagesEnabled=false', on_off)

    def set_no_js(self, on_off=True):
        """设置是否禁用js
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = True if on_off else False
        return self.set_argument('--disable-javascript', on_off)

    def set_mute(self, on_off=True):
        """设置是否静音
        :param on_off: 开或关
        :return: 当前对象
        """
        on_off = True if on_off else False
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
        return self.set_argument('--proxy-server', proxy)

    def set_page_load_strategy(self, value):
        """设置page_load_strategy，可接收 'normal', 'eager', 'none'
        selenium4以上版本才支持此功能
        normal：默认情况下使用, 等待所有资源下载完成
        eager：DOM访问已准备就绪, 但其他资源 (如图像) 可能仍在加载中
        none：完全不阻塞WebDriver
        :param value: 可接收 'normal', 'eager', 'none'
        :return: 当前对象
        """
        if value not in ('normal', 'eager', 'none'):
            raise ValueError("只能选择'normal', 'eager', 'none'。")
        self.page_load_strategy = value.lower()
        return self

    def set_paths(self, driver_path=None, chrome_path=None, browser_path=None, local_port=None,
                  debugger_address=None, download_path=None, user_data_path=None, cache_path=None):
        """快捷的路径设置函数
        :param driver_path: chromedriver.exe路径
        :param chrome_path: chrome.exe路径
        :param browser_path: 浏览器可执行文件路径
        :param local_port: 本地端口号
        :param debugger_address: 调试浏览器地址，例：127.0.0.1:9222
        :param download_path: 下载文件路径
        :param user_data_path: 用户数据路径
        :param cache_path: 缓存路径
        :return: 当前对象
        """
        if driver_path is not None:
            self._driver_path = str(driver_path)

        if chrome_path is not None:
            self.binary_location = str(chrome_path)

        if browser_path is not None:
            self.binary_location = str(browser_path)

        if local_port is not None:
            self.debugger_address = '' if local_port == '' else f'127.0.0.1:{local_port}'

        if debugger_address is not None:
            self.debugger_address = debugger_address

        if download_path is not None:
            self._download_path = str(download_path)

        if user_data_path is not None:
            self.set_argument('--user-data-dir', str(user_data_path))
            self._user_data_path = user_data_path

        if cache_path is not None:
            self.set_argument('--disk-cache-dir', str(cache_path))

        return self

    def as_dict(self):
        """已dict方式返回所有配置信息"""
        return chrome_options_to_dict(self)


def chrome_options_to_dict(options):
    """把chrome配置对象转换为字典
    :param options: chrome配置对象，字典或DriverOptions对象
    :return: 配置字典
    """
    if options in (False, None):
        return DriverOptions(read_file=False).as_dict()

    if isinstance(options, dict):
        return options

    re_dict = dict()
    attrs = ['debugger_address', 'binary_location', 'arguments', 'extensions', 'experimental_options', 'driver_path',
             'page_load_strategy', 'download_path']

    options_dir = options.__dir__()
    for attr in attrs:
        try:
            re_dict[attr] = options.__getattribute__(attr) if attr in options_dir else None
        except Exception:
            pass

    if 'timeouts' in options_dir and 'timeouts' in options._caps:
        timeouts = options.__getattribute__('timeouts')
        re_dict['timeouts'] = timeouts

    return re_dict
