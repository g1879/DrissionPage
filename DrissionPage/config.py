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
            except SyntaxError:
                option[j[0]] = self._conf.get(section, j[0])
        return option

    def set_item(self, section: str, item: str, value: str) -> None:
        """设置配置值"""
        self._conf.set(section, item, str(value))

    def save(self, path: str = None) -> None:
        """保存配置文件
        :param path: ini文件的路径，默认保存到模块文件夹下的
        :return: None
        """
        path = path or Path(__file__).parent / 'configs.ini'
        self._conf.write(open(path, 'w'))


class DriverOptions(Options):
    def __init__(self, read_file=True):
        """初始化，默认从文件读取设置"""
        super().__init__()
        if read_file:
            options_dict = OptionsManager().get_option('chrome_options')
            self._binary_location = options_dict['binary_location'] if 'binary_location' in options_dict else ''
            self._arguments = options_dict['arguments'] if 'arguments' in options_dict else []
            self._extensions = options_dict['extensions'] if 'extensions' in options_dict else []
            self._experimental_options = options_dict[
                'experimental_options'] if 'experimental_options' in options_dict else {}
            self._debugger_address = options_dict['debugger_address'] if 'debugger_address' in options_dict else None

    def save(self, path: str = None) -> None:
        """保存设置到文件
        :param path: ini文件的路径，默认保存到模块文件夹下的
        :return: None
        """
        om = OptionsManager()
        options = _chrome_options_to_dict(self)
        for i in options:
            om.set_item('chrome_options', i, options[i])
        om.save(path)

    def remove_argument(self, value: str) -> None:
        """移除一个设置"""
        if value in self._arguments:
            self._arguments.remove(value)

    def remove_experimental_option(self, key: str) -> None:
        """移除一个实验设置，传入key值删除"""
        if key in self._experimental_options:
            self._experimental_options.pop(key)

    def remove_all_extensions(self) -> None:
        """移除所有插件
        因插件是以整个文件储存，难以移除其中一个，故如须设置则全部移除再重设"""
        self._extensions = []


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


def _chrome_options_to_dict(options: Union[dict, Options, None]) -> Union[dict, None]:
    if options is None or isinstance(options, dict):
        return options

    re_dict = dict()
    if options.debugger_address:
        re_dict['debugger_address'] = options.debugger_address
    else:
        re_dict['binary_location'] = options.binary_location
        re_dict['debugger_address'] = options.debugger_address
        re_dict['arguments'] = options.arguments
        re_dict['extensions'] = options.extensions
        re_dict['experimental_options'] = options.experimental_options
        # re_dict['capabilities'] = options.capabilities
    return re_dict
