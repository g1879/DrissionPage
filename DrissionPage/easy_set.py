# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_page.py
"""
from os import popen
from pathlib import Path
from pprint import pprint
from re import search as RE_SEARCH, sub
from typing import Union

from selenium import webdriver

from .common import unzip
from .config import OptionsManager, DriverOptions
from .drission import Drission
from .session_page import SessionPage


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
              local_port: Union[int, str] = None,
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
    :param local_port: 本地端口号
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
        return path or ''

    if driver_path is not None:
        om.set_item('paths', 'chromedriver_path', format_path(driver_path))

    if chrome_path is not None:
        om.set_item('chrome_options', 'binary_location', format_path(chrome_path))

    if local_port is not None:
        om.set_item('chrome_options', 'debugger_address', format_path(f'127.0.0.1:{local_port}'))

    if debugger_address is not None:
        om.set_item('chrome_options', 'debugger_address', format_path(debugger_address))

    if tmp_path is not None:
        om.set_item('paths', 'tmp_path', format_path(tmp_path))

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
def get_match_driver(ini_path: Union[str, None] = 'default',
                     save_path: str = None,
                     chrome_path: str = None,
                     show_msg: bool = True,
                     check_version: bool = True) -> Union[str, None]:
    """自动识别chrome版本并下载匹配的driver             \n
    :param ini_path: 要读取和修改的ini文件路径
    :param save_path: chromedriver保存路径
    :param chrome_path: 指定chrome.exe位置
    :param show_msg: 是否打印信息
    :param check_version: 是否检查版本匹配
    :return: None
    """
    save_path = save_path or str(Path(__file__).parent)

    chrome_path = chrome_path or _get_chrome_path(ini_path, show_msg)
    chrome_path = Path(chrome_path).absolute() if chrome_path else None
    if show_msg:
        print('chrome.exe路径', chrome_path)

    ver = _get_chrome_version(str(chrome_path))
    if show_msg:
        print('version', ver)

    zip_path = _download_driver(ver, save_path, show_msg=show_msg)

    if not zip_path and show_msg:
        print('没有找到对应版本的driver。')

    try:
        driver_path = unzip(zip_path, save_path)[0]
    except TypeError:
        driver_path = None

    if show_msg:
        print('解压路径', driver_path)

    if driver_path:
        Path(zip_path).unlink()
        if ini_path:
            set_paths(driver_path=driver_path, chrome_path=str(chrome_path), ini_path=ini_path, check_version=False)

        if check_version:
            if not check_driver_version(driver_path, chrome_path) and show_msg:
                print('获取失败，请手动配置。')
    else:
        if show_msg:
            print('获取失败，请手动配置。')

    return driver_path


def _get_chrome_path(ini_path: str = None,
                     show_msg: bool = True,
                     from_ini: bool = True,
                     from_regedit: bool = True,
                     from_system_path: bool = True, ) -> Union[str, None]:
    """从ini文件或系统变量中获取chrome.exe的路径    \n
    :param ini_path: ini文件路径
    :return: chrome.exe路径
    """
    # -----------从ini文件中获取--------------
    if ini_path and from_ini:
        try:
            path = OptionsManager(ini_path).chrome_options['binary_location']
        except KeyError:
            path = None
    else:
        path = None

    if path and Path(path).is_file():
        if show_msg:
            print('ini文件中', end='')
        return str(path)

    # -----------从注册表中获取--------------
    if from_regedit:
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe',
                                 reserved=0, access=winreg.KEY_READ)
            k = winreg.EnumValue(key, 0)
            winreg.CloseKey(key)

            if show_msg:
                print('注册表中', end='')

            return k[1]

        except FileNotFoundError:
            pass

    # -----------从系统变量中获取--------------
    if from_system_path:
        paths = popen('set path').read().lower()
        r = RE_SEARCH(r'[^;]*chrome[^;]*', paths)

        if r:
            path = Path(r.group(0)) if 'chrome.exe' in r.group(0) else Path(r.group(0)) / 'chrome.exe'

            if path.exists():
                if show_msg:
                    print('系统变量中', end='')
                return str(path)

        paths = paths.split(';')

        for path in paths:
            path = Path(path) / 'chrome.exe'

            try:
                if path.exists():
                    if show_msg:
                        print('系统变量中', end='')
                    return str(path)
            except OSError:
                pass


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
    except Exception:
        return None


def _download_driver(version: str, save_path: str = None, show_msg: bool = True) -> Union[str, None]:
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

    remote_versions = page.eles(f'xpath://pre/a[starts-with(text(),"{loc_main}.")]')
    remote_versions = [v for v in remote_versions if v.text and v.text[-1] == '/']
    remote_versions.sort(key=lambda x: x.text)

    for i in remote_versions:
        try:
            remote_num = int(sub(r'[./]', '', i.text))
        except ValueError:
            continue

        if remote_num >= loc_num:
            remote_ver = i.text
            break

    # 没有匹配到，则取大版本的最后一个号
    if remote_versions and not remote_ver:
        remote_ver = remote_versions[-1].text

    if remote_ver:
        url = f'https://cdn.npm.taobao.org/dist/chromedriver/{remote_ver}chromedriver_win32.zip'
        save_path = save_path or Path(__file__).parent
        result = page.download(url, save_path, file_exists='overwrite', show_msg=show_msg)

        if result[0]:
            return result[1]

    return None
