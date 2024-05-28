# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from configparser import RawConfigParser, NoSectionError, NoOptionError
from pathlib import Path
from pprint import pprint


class OptionsManager(object):
    """管理配置文件内容的类"""

    def __init__(self, path=None):
        """初始化，读取配置文件，如没有设置临时文件夹，则设置并新建
        :param path: ini文件的路径，为None则找项目文件夹下的，找不到则读取模块文件夹下的
        """
        if path is False:
            self.ini_path = None
        else:
            default_configs = Path(__file__).parent / 'configs.ini'
            if path is None:
                dp_configs = Path('dp_configs.ini')
                if dp_configs.exists():
                    self.ini_path = dp_configs
                else:
                    self.ini_path = default_configs
            elif path == 'default':
                self.ini_path = default_configs
            elif isinstance(path, Path):
                self.ini_path = path
            else:
                self.ini_path = Path(path)

        self._conf = RawConfigParser()
        if path is not False and self.ini_path.exists():
            self.file_exists = True
            self._conf.read(self.ini_path, encoding='utf-8')
        else:
            self.file_exists = False
            self._conf.add_section('paths')
            self._conf.add_section('chromium_options')
            self._conf.add_section('session_options')
            self._conf.add_section('timeouts')
            self._conf.add_section('proxies')
            self._conf.add_section('others')
            self.set_item('paths', 'download_path', '')
            self.set_item('paths', 'tmp_path', '')
            self.set_item('chromium_options', 'address', '127.0.0.1:9222')
            self.set_item('chromium_options', 'browser_path', 'chrome')
            self.set_item('chromium_options', 'arguments', "['--no-default-browser-check', '--disable-suggestions-ui', "
                                                           "'--no-first-run', '--disable-infobars', "
                                                           "'--disable-popup-blocking', '--hide-crash-restore-bubble', "
                                                           "'--disable-features=PrivacySandboxSettings4']")
            self.set_item('chromium_options', 'extensions', '[]')
            self.set_item('chromium_options', 'prefs', "{'profile.default_content_settings.popups': 0, "
                                                       "'profile.default_content_setting_values': "
                                                       "{'notifications': 2}}")
            self.set_item('chromium_options', 'flags', '{}')
            self.set_item('chromium_options', 'load_mode', 'normal')
            self.set_item('chromium_options', 'user', 'Default')
            self.set_item('chromium_options', 'auto_port', 'False')
            self.set_item('chromium_options', 'system_user_path', 'False')
            self.set_item('chromium_options', 'existing_only', 'False')
            self.set_item('session_options', 'headers', "{'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X "
                                                        "10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10."
                                                        "1.2 Safari/603.3.8', 'accept': 'text/html,application/xhtml"
                                                        "+xml,application/xml;q=0.9,*/*;q=0.8', 'connection': "
                                                        "'keep-alive', 'accept-charset': 'GB2312,utf-8;q=0.7,*;q=0.7'}")
            self.set_item('timeouts', 'base', '10')
            self.set_item('timeouts', 'page_load', '30')
            self.set_item('timeouts', 'script', '30')
            self.set_item('proxies', 'http', '')
            self.set_item('proxies', 'https', '')
            self.set_item('others', 'retry_times', '3')
            self.set_item('others', 'retry_interval', '2')

    def __getattr__(self, item):
        """以dict形似返回获取大项信息
        :param item: 项名
        :return: None
        """
        return self.get_option(item)

    def get_value(self, section, item):
        """获取配置的值
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

    def get_option(self, section):
        """把section内容以字典方式返回
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

    def set_item(self, section, item, value):
        """设置配置值
        :param section: 段名
        :param item: 项名
        :param value: 项值
        :return: None
        """
        self._conf.set(section, item, str(value))
        self.__setattr__(f'_{section}', None)
        return self

    def remove_item(self, section, item):
        """删除配置值
        :param section: 段名
        :param item: 项名
        :return: None
        """
        self._conf.remove_option(section, item)
        return self

    def save(self, path=None):
        """保存配置文件
        :param path: ini文件的路径，传入 'default' 保存到默认ini文件
        :return: 保存路径
        """
        default_path = (Path(__file__).parent / 'configs.ini').absolute()
        if path == 'default':
            path = default_path
        elif path is None:
            if self.ini_path is None:
                raise ValueError('ini_path未设置。')
            path = self.ini_path.absolute()
        else:
            path = Path(path).absolute()

        path = path / 'config.ini' if path.is_dir() else path
        path.parent.mkdir(exist_ok=True, parents=True)

        path = str(path)
        self._conf.write(open(path, 'w', encoding='utf-8'))

        print(f'配置已保存到文件：{path}')
        if path == str(default_path):
            print('以后程序可自动从文件加载配置。')

        self.file_exists = True
        return path

    def save_to_default(self):
        """保存当前配置到默认ini文件"""
        return self.save('default')

    def show(self):
        """打印所有设置信息"""
        for i in self._conf.sections():
            print(f'[{i}]')
            pprint(self.get_option(i))
            print()
