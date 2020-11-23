# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_page.py
"""
from os import popen
from pathlib import Path
from pprint import pprint
from re import search as RE_SEARCH
from typing import Union

from selenium import webdriver

from DrissionPage.config import OptionsManager, DriverOptions
from DrissionPage.drission import Drission
from DrissionPage.session_page import SessionPage
from .common import unzip


def show_settings(ini_path: str = None) -> None:
    """打印ini文件内容"""
    om = OptionsManager(ini_path)
    print('paths:')
    pprint(om.get_option('paths'))
    print('\nchrome options:')
    pprint(om.get_option('chrome_options'))
    print('\nsession options:')
    pprint(om.get_option('session_options'))


def set_paths(driver_path: str = None,
              chrome_path: str = None,
              debugger_address: str = None,
              tmp_path: str = None,
              download_path: str = None,
              user_data_path: str = None,
              cache_path: str = None,
              ini_path: str = None,
              check_version: bool = True) -> None:
    """快捷的路径设置函数                                          \n
    :param driver_path: chromedriver.exe路径
    :param chrome_path: chrome.exe路径
    :param debugger_address: 调试浏览器地址，例：127.0.0.1:9222
    :param download_path: 下载文件路径
    :param tmp_path: 临时文件夹路径
    :param user_data_path: 用户数据路径
    :param cache_path: 缓存路径
    :param ini_path: 要修改的ini文件路径
    :param check_version: 是否检查chromedriver和chrome是否匹配
    :return: None
    """
    om = OptionsManager(ini_path)

    def format_path(path: str) -> str:
        return str(path).replace('/', '\\')

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
        set_argument('--user-data-dir', format_path(user_data_path), ini_path)

    if cache_path is not None:
        set_argument('--disk-cache-dir', format_path(cache_path), ini_path)

    if check_version:
        check_driver_version(format_path(driver_path), format_path(chrome_path))


def set_argument(arg: str, value: Union[bool, str], ini_path: str = None) -> None:
    """设置浏览器配置argument属性                            \n
    :param arg: 属性名
    :param value: 属性值，有值的属性传入值，没有的传入bool
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    do = DriverOptions(ini_path=ini_path)
    do.remove_argument(arg)

    if value:
        arg_str = arg if isinstance(value, bool) else f'{arg}={value}'
        do.add_argument(arg_str)

    do.save()


def set_headless(on_off: bool = True, ini_path: str = None) -> None:
    """设置是否隐藏浏览器界面               \n
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    on_off = True if on_off else False
    set_argument('--headless', on_off, ini_path)


def set_no_imgs(on_off: bool = True, ini_path: str = None) -> None:
    """设置是否禁止加载图片                    \n
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    on_off = True if on_off else False
    set_argument('--blink-settings=imagesEnabled=false', on_off, ini_path)


def set_no_js(on_off: bool = True, ini_path: str = None) -> None:
    """设置是否禁用js                              \n
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    on_off = True if on_off else False
    set_argument('--disable-javascript', on_off, ini_path)


def set_mute(on_off: bool = True, ini_path: str = None) -> None:
    """设置是否静音                              \n
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    on_off = True if on_off else False
    set_argument('--mute-audio', on_off, ini_path)


def set_user_agent(user_agent: str, ini_path: str = None) -> None:
    """设置user agent                           \n
    :param user_agent: user agent文本
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    set_argument('user-agent', user_agent, ini_path)


def set_proxy(proxy: str, ini_path: str = None) -> None:
    """设置代理                                  \n
    :param proxy: 代理网址和端口
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    set_argument('--proxy-server', proxy, ini_path)


def check_driver_version(driver_path: str = None, chrome_path: str = None) -> bool:
    """检查传入的chrome和chromedriver是否匹配  \n
    :param driver_path: chromedriver.exe路径
    :param chrome_path: chrome.exe路径
    :return: 是否匹配
    """
    print('正在检测可用性...')
    om = OptionsManager()
    driver_path = driver_path or om.get_value('paths', 'chromedriver_path') or 'chromedriver'
    chrome_path = str(chrome_path or om.get_value('chrome_options', 'binary_location'))
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
        print(f'出现异常：\n{e}\n可执行easy_set.get_match_driver()自动下载匹配的版本。\n'
              f'或自行从以下网址下载：https://chromedriver.chromium.org/downloads')

        return False


# -------------------------自动识别chrome版本号并下载对应driver------------------------
def get_match_driver(ini_path: str = None,
                     save_path: str = None,
                     chrome_path: str = None) -> None:
    """自动识别chrome版本并下载匹配的driver             \n
    :param ini_path: 要读取和修改的ini文件路径
    :param save_path: chromedriver保存路径
    :param chrome_path: 指定chrome.exe位置
    :return: None
    """
    save_path = save_path or str(Path(__file__).parent)

    chrome_path = chrome_path or _get_chrome_path(ini_path)
    chrome_path = Path(chrome_path).absolute() if chrome_path else None
    print('chrome.exe路径', chrome_path, '\n')

    ver = _get_chrome_version(chrome_path)
    print('version', ver, '\n')

    zip_path = _download_driver(ver, save_path)

    if not zip_path:
        print('没有找到对应版本的driver。')

    try:
        driver_path = unzip(zip_path, save_path)[0]
    except TypeError:
        driver_path = None

    print('\n解压路径', driver_path, '\n')

    if driver_path:
        Path(zip_path).unlink()
        set_paths(driver_path=driver_path, chrome_path=str(chrome_path), ini_path=ini_path, check_version=False)

        if not check_driver_version(driver_path, chrome_path):
            print('获取失败，请手动配置。')
    else:
        print('获取失败，请手动配置。')


def _get_chrome_path(ini_path: str = None) -> Union[str, None]:
    """从ini文件或系统变量中获取chrome.exe的路径    \n
    :param ini_path: ini文件路径
    :return: chrome.exe路径
    """
    # -----------从ini文件中获取--------------
    try:
        path = OptionsManager(ini_path).chrome_options['binary_location']
    except KeyError:
        return None

    if path and Path(path).is_file():
        print('ini文件中', end='')
        return str(path)

    # -----------从系统路径中获取--------------
    paths = popen('set path').read().lower()
    r = RE_SEARCH(r'[^;]*chrome[^;]*', paths)

    if r:
        path = Path(r.group(0)) if 'chrome.exe' in r.group(0) else Path(r.group(0)) / 'chrome.exe'

        if path.exists():
            print('系统中', end='')
            return str(path)

    paths = paths.split(';')

    for path in paths:
        path = Path(path) / 'chrome.exe'

        if path.exists():
            print('系统中', end='')
            return str(path)


def _get_chrome_version(path: str) -> Union[str, None]:
    """根据文件路径获取版本号              \n
    :param path: chrome.exe文件路径
    :return: 版本号
    """
    if not path:
        return

    path = str(path).replace('\\', '\\\\')

    try:
        return (popen(f'wmic datafile where "name=\'{path}\'" get version').read()
                .lower().split('\n')[2].replace(' ', ''))
    except:
        return None


def _download_driver(version: str, save_path: str = None) -> Union[str, None]:
    """根据传入的版本号到镜像网站查找，下载最相近的          \n
    :param version: 本地版本号
    :return: 保存地址
    """
    if not version:
        return

    page = SessionPage(Drission().session)
    page.get('http://npm.taobao.org/mirrors/chromedriver')

    remote_ver = None
    loc_main = version.split('.')[0]

    try:
        loc_num = int(version.replace('.', ''))
    except ValueError:
        return None

    for i in page.eles('xpath://pre/a'):
        remote_main = i.text.split('.')[0]

        try:
            remote_num = int(i.text.replace('.', '').replace('/', ''))
        except ValueError:
            continue

        if remote_main == loc_main and remote_num >= loc_num:
            remote_ver = i.text
            break

    if remote_ver:
        url = f'https://cdn.npm.taobao.org/dist/chromedriver/{remote_ver}chromedriver_win32.zip'
        save_path = save_path or Path(__file__).parent
        result = page.download(url, save_path, file_exists='overwrite', show_msg=True)

        if result[0]:
            return result[1]

    return None
