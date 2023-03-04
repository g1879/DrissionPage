# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
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
        if path is None:
            if Path('dp_configs.ini').exists():
                self.ini_path = 'dp_configs.ini'
            else:
                self.ini_path = str(Path(__file__).parent / 'configs.ini')
        elif path == 'default':
            self.ini_path = str(Path(__file__).parent / 'configs.ini')
        else:
            self.ini_path = str(path)

        if not Path(self.ini_path).exists():
            raise FileNotFoundError('ini文件不存在。')
        self._conf = RawConfigParser()
        self._conf.read(self.ini_path, encoding='utf-8')

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

    def save_to_default(self):
        """保存当前配置到默认ini文件"""
        return self.save('default')

    def show(self):
        """打印所有设置信息"""
        for i in self._conf.sections():
            print(f'[{i}]')
            pprint(self.get_option(i))
            print()
