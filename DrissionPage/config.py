# -*- coding:utf-8 -*-
"""
配置文件
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   config.py
"""
from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path
from typing import Any, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class OptionsManager(object):
    """管理配置文件内容的类"""

    def __init__(self, path: str = None):
        """初始化，读取配置文件，如没有设置临时文件夹，则设置并新建
        :param path: ini文件的路径，默认读取模块文件夹下的
        """
        self.path = path or Path(__file__).parent / 'configs.ini'
        self._conf = ConfigParser()
        self._conf.read(self.path, encoding='utf-8')
        if 'global_tmp_path' not in self.get_option('paths') or not self.get_value('paths', 'global_tmp_path'):
            global_tmp_path = str((Path(__file__).parent / 'tmp').absolute())
            Path(global_tmp_path).mkdir(parents=True, exist_ok=True)
            self.set_item('paths', 'global_tmp_path', global_tmp_path)
            self.save()

    def get_value(self, section: str, item: str) -> Any:
        """获取配置的值"""
        try:
            return eval(self._conf.get(section, item))
        except SyntaxError:
            return self._conf.get(section, item)
        except NoSectionError and NoOptionError:
            return None

    def get_option(self, section: str) -> dict:
        """把section内容以字典方式返回"""
        items = self._conf.items(section)
        option = dict()
        for j in items:
            try:
                option[j[0]] = eval(self._conf.get(section, j[0]).replace('\\', '\\\\'))
            except:
                option[j[0]] = self._conf.get(section, j[0])
        return option

    def set_item(self, section: str, item: str, value: Any) -> None:
        """设置配置值"""
        self._conf.set(section, item, str(value))

    def save(self, path: str = None) -> None:
        """保存配置文件
        :param path: ini文件的路径，默认保存到模块文件夹下的
        :return: None
        """
        path = path or Path(__file__).parent / 'configs.ini'
        self._conf.write(open(path, 'w', encoding='utf-8'))


class DriverOptions(Options):
    def __init__(self, read_file=True):
        """初始化，默认从文件读取设置"""
        super().__init__()
        self._driver_path = None
        if read_file:
            options_dict = OptionsManager().get_option('chrome_options')
            paths_dict = OptionsManager().get_option('paths')
            self._binary_location = options_dict['binary_location'] if 'binary_location' in options_dict else ''
            self._arguments = options_dict['arguments'] if 'arguments' in options_dict else []
            self._extensions = options_dict['extensions'] if 'extensions' in options_dict else []
            self._experimental_options = options_dict[
                'experimental_options'] if 'experimental_options' in options_dict else {}
            self._debugger_address = options_dict['debugger_address'] if 'debugger_address' in options_dict else None
            self._driver_path = paths_dict['chromedriver_path'] if 'chromedriver_path' in paths_dict else None

    @property
    def driver_path(self):
        return self._driver_path

    def save(self, path: str = None) -> None:
        """保存设置到文件
        :param path: ini文件的路径，默认保存到模块文件夹下的
        :return: None
        """
        om = OptionsManager()
        options = _chrome_options_to_dict(self)
        for i in options:
            if i == 'driver_path':
                om.set_item('paths', 'chromedriver_path', options[i])
            else:
                om.set_item('chrome_options', i, options[i])
        om.save(path)

    def remove_argument(self, value: str) -> None:
        """移除一个设置
        :param value: 设置项名，有值的设置项传入设置名称即可
        :return: None
        """
        del_list = []
        for argument in self._arguments:
            if argument.startswith(value):
                del_list.append(argument)
        for del_arg in del_list:
            self._arguments.remove(del_arg)

    def remove_experimental_option(self, key: str) -> None:
        """移除一个实验设置，传入key值删除"""
        if key in self._experimental_options:
            self._experimental_options.pop(key)

    def remove_all_extensions(self) -> None:
        """移除所有插件
        因插件是以整个文件储存，难以移除其中一个，故如须设置则全部移除再重设"""
        self._extensions = []

    def set_argument(self, arg: str, value: Union[bool, str]) -> None:
        """设置浏览器配置argument属性
        :param arg: 属性名
        :param value: 属性值，有值的属性传入值，没有的传入bool
        :return: None
        """
        self.remove_argument(arg)
        if value:
            arg_str = arg if isinstance(value, bool) else f'{arg}={value}'
            self.add_argument(arg_str)

    def set_headless(self, on_off: bool = True) -> None:
        """设置headless"""
        self.set_argument('--headless', on_off)

    def set_no_imgs(self, on_off: bool = True) -> None:
        """设置是否加载图片"""
        self.set_argument('--blink-settings=imagesEnabled=false', on_off)

    def set_no_js(self, on_off: bool = True) -> None:
        """设置禁用js"""
        self.set_argument('--disable-javascript', on_off)

    def set_mute(self, on_off: bool = True) -> None:
        """设置静音"""
        self.set_argument('--mute-audio', on_off)

    def set_user_agent(self, user_agent: str) -> None:
        """设置user agent"""
        self.set_argument('user-agent', user_agent)

    def set_proxy(self, proxy: str) -> None:
        """设置代理"""
        self.set_argument('--proxy-server', proxy)

    def set_paths(self,
                  driver_path: str = None,
                  chrome_path: str = None,
                  debugger_address: str = None,
                  download_path: str = None,
                  user_data_path: str = None,
                  cache_path: str = None) -> None:
        """简易设置路径函数
        :param driver_path: chromedriver.exe路径
        :param chrome_path: chrome.exe路径
        :param debugger_address: 调试浏览器地址，例：127.0.0.1:9222
        :param download_path: 下载文件路径
        :param user_data_path: 用户数据路径
        :param cache_path: 缓存路径
        :return: None
        """

        def format_path(path: str) -> str:
            return path.replace('/', '\\')

        if driver_path is not None:
            self._driver_path = format_path(driver_path)
        if chrome_path is not None:
            self.binary_location = format_path(chrome_path)
        if debugger_address is not None:
            self.debugger_address = debugger_address
        if download_path is not None:
            self.experimental_options['prefs']['download.default_directory'] = format_path(download_path)
        if user_data_path is not None:
            self.set_argument('--user-data-dir', format_path(user_data_path))
        if cache_path is not None:
            self.set_argument('--disk-cache-dir', format_path(cache_path))


def _dict_to_chrome_options(options: dict) -> Options:
    """从传入的字典获取浏览器设置，返回ChromeOptions对象"""
    chrome_options = webdriver.ChromeOptions()
    if 'debugger_address' in options and options['debugger_address']:
        # 控制已打开的浏览器
        chrome_options.debugger_address = options['debugger_address']
    else:
        if 'binary_location' in options and options['binary_location']:
            # 手动指定使用的浏览器位置
            chrome_options.binary_location = options['binary_location']
        if 'arguments' in options:
            # 启动参数
            if not isinstance(options['arguments'], list):
                raise Exception(f'Arguments need list，not {type(options["arguments"])}.')
            for arg in options['arguments']:
                chrome_options.add_argument(arg)
        if 'extension_files' in options and options['extension_files']:
            # 加载插件
            if not isinstance(options['extension_files'], list):
                raise Exception(f'Extension files need list，not {type(options["extension_files"])}.')
            for arg in options['extension_files']:
                chrome_options.add_extension(arg)
        if 'extensions' in options and options['extensions']:
            if not isinstance(options['extensions'], list):
                raise Exception(f'Extensions need list，not {type(options["extensions"])}.')
            for arg in options['extensions']:
                chrome_options.add_encoded_extension(arg)
        if 'experimental_options' in options and options['experimental_options']:
            # 实验性质的设置参数
            if not isinstance(options['experimental_options'], dict):
                raise Exception(f'Experimental options need dict，not {type(options["experimental_options"])}.')
            for i in options['experimental_options']:
                chrome_options.add_experimental_option(i, options['experimental_options'][i])
        # if 'capabilities' in options and options['capabilities']:
        #     pass  # 未知怎么用
    return chrome_options


def _chrome_options_to_dict(options: Union[dict, DriverOptions, None]) -> Union[dict, None]:
    if options is None or isinstance(options, dict):
        return options

    re_dict = dict()
    re_dict['debugger_address'] = options.debugger_address
    re_dict['binary_location'] = options.binary_location
    re_dict['debugger_address'] = options.debugger_address
    re_dict['arguments'] = options.arguments
    re_dict['extensions'] = options.extensions
    re_dict['experimental_options'] = options.experimental_options
    try:
        re_dict['driver_path'] = options.driver_path
    except:
        re_dict['driver_path'] = None
    # re_dict['capabilities'] = options.capabilities
    return re_dict
