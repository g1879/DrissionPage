# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_page.py
"""
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
    """简易设置路径函数
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
    if driver_path is not None:
        om.set_item('paths', 'chromedriver_path', driver_path)
    if chrome_path is not None:
        om.set_item('chrome_options', 'binary_location', chrome_path)
    if debugger_address is not None:
        om.set_item('chrome_options', 'debugger_address', debugger_address)
    if tmp_path is not None:
        om.set_item('paths', 'global_tmp_path', tmp_path)
    if download_path is not None:
        experimental_options = om.get_value('chrome_options', 'experimental_options')
        experimental_options['prefs']['download.default_directory'] = download_path
        om.set_item('chrome_options', 'experimental_options', experimental_options)
    om.save()
    if user_data_path is not None:
        set_value_argument('--user-data-dir', user_data_path)
    if cache_path is not None:
        set_value_argument('--disk-cache-dir', cache_path)
    if check_version:
        check_driver_version(driver_path, chrome_path)


def set_value_argument(arg: str, value: str) -> None:
    """设置有值的属性"""
    do = DriverOptions()
    pr_ok = False
    for key, argument in enumerate(do.arguments):
        print(argument)
        if arg in argument:
            do.remove_argument(do.arguments[key])
            print(value)
            if value:
                do.add_argument(f'{arg}={value}')
            pr_ok = True
            break
    if not pr_ok:
        do.add_argument(f'{arg}={value}')
        print(do.arguments)
    do.save()


def set_argument(arg: str, on_off: bool) -> None:
    """设置没有值的属性"""
    do = DriverOptions()
    if on_off:
        if arg not in do.arguments:
            do.add_argument(arg)
    else:
        do.remove_argument(arg)
    do.save()


def set_headless(on_off: bool = True) -> None:
    """设置headless"""
    set_argument('--headless', on_off)


def set_no_imgs(on_off: bool = True) -> None:
    """设置是否加载图片"""
    set_argument('--blink-settings=imagesEnabled=false', on_off)


def set_no_js(on_off: bool = True) -> None:
    """设置禁用js"""
    set_argument('--disable-javascript', on_off)


def set_mute(on_off: bool = True) -> None:
    """设置静音"""
    set_argument('--mute-audio', on_off)


def set_user_agent(user_agent: str) -> None:
    """设置user agent"""
    set_value_argument('user-agent', user_agent)


def set_proxy(proxy: str) -> None:
    """设置代理"""
    set_value_argument('--proxy-server', proxy)


def check_driver_version(driver_path: str = None, chrome_path: str = None) -> bool:
    """检查传入的chrome和chromedriver是否匹配"""
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
