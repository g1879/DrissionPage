# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_page.py
"""
from typing import Union

from selenium import webdriver

from DrissionPage.config import OptionsManager, DriverOptions


def set_paths(driver_path: str = None,
              chrome_path: str = None,
              debugger_address: str = None,
              tmp_path: str = None,
              download_path: str = None,
              user_data_path: str = None,
              cache_path: str = None,
              check_version: bool = True) -> None:
    """快捷的路径设置函数                                          \n
    :param driver_path: chromedriver.exe路径
    :param chrome_path: chrome.exe路径
    :param debugger_address: 调试浏览器地址，例：127.0.0.1:9222
    :param download_path: 下载文件路径
    :param tmp_path: 临时文件夹路径
    :param user_data_path: 用户数据路径
    :param cache_path: 缓存路径
    :param check_version: 是否检查chromedriver和chrome是否匹配
    :return: None
    """
    om = OptionsManager()

    def format_path(path: str) -> str:
        if isinstance(path, str):
            return path.replace('/', '\\')

    if driver_path is not None:
        om.set_item('paths', 'chromedriver_path', format_path(driver_path))

    if chrome_path is not None:
        om.set_item('chrome_options', 'binary_location', format_path(chrome_path))

    if debugger_address is not None:
        om.set_item('chrome_options', 'debugger_address', format_path(debugger_address))

    if tmp_path is not None:
        om.set_item('paths', 'global_tmp_path', format_path(tmp_path))

    if download_path is not None:
        experimental_options = om.get_value('chrome_options', 'experimental_options')
        experimental_options['prefs']['download.default_directory'] = format_path(download_path)
        om.set_item('chrome_options', 'experimental_options', experimental_options)

    om.save()

    if user_data_path is not None:
        set_argument('--user-data-dir', format_path(user_data_path))

    if cache_path is not None:
        set_argument('--disk-cache-dir', format_path(cache_path))

    if check_version:
        check_driver_version(format_path(driver_path), format_path(chrome_path))


def set_argument(arg: str, value: Union[bool, str]) -> None:
    """设置浏览器配置argument属性                            \n
    :param arg: 属性名
    :param value: 属性值，有值的属性传入值，没有的传入bool
    :return: None
    """
    do = DriverOptions()
    do.remove_argument(arg)

    if value:
        arg_str = arg if isinstance(value, bool) else f'{arg}={value}'
        do.add_argument(arg_str)

    do.save()


def set_headless(on_off: bool = True) -> None:
    """设置是否隐藏浏览器界面  \n
    :param on_off: 开或关
    :return: None
    """
    set_argument('--headless', on_off)


def set_no_imgs(on_off: bool = True) -> None:
    """设置是否禁止加载图片   \n
    :param on_off: 开或关
    :return: None
    """
    set_argument('--blink-settings=imagesEnabled=false', on_off)


def set_no_js(on_off: bool = True) -> None:
    """设置是否禁用js              \n
    :param on_off: 开或关
    :return: None
    """
    set_argument('--disable-javascript', on_off)


def set_mute(on_off: bool = True) -> None:
    """设置是否静音                \n
    :param on_off: 开或关
    :return: None
    """
    set_argument('--mute-audio', on_off)


def set_user_agent(user_agent: str) -> None:
    """设置user agent                    \n
    :param user_agent: user agent文本
    :return: None
    """
    set_argument('user-agent', user_agent)


def set_proxy(proxy: str) -> None:
    """设置代理                   \n
    :param proxy: 代理网址和端口
    :return: None
    """
    set_argument('--proxy-server', proxy)


def check_driver_version(driver_path: str = None, chrome_path: str = None) -> bool:
    """检查传入的chrome和chromedriver是否匹配  \n
    :param driver_path: chromedriver.exe路径
    :param chrome_path: chrome.exe路径
    :return: 是否匹配
    """
    print('正在检测可用性...')
    om = OptionsManager()
    driver_path = driver_path or om.get_value('paths', 'chromedriver_path') or 'chromedriver'
    chrome_path = chrome_path or om.get_value('chrome_options', 'binary_location')
    do = DriverOptions(read_file=False)
    do.add_argument('--headless')

    if chrome_path:
        do.binary_location = chrome_path

    try:
        driver = webdriver.Chrome(driver_path, options=do)
        driver.quit()
        print('版本匹配，可正常使用。')
        return True
    except Exception as e:
        info = f'''
出现异常：
{e}chromedriver下载网址：https://chromedriver.chromium.org/downloads
'''
        print(info)
        return False
