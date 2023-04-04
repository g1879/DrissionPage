# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from os import popen
from pathlib import Path
from re import search
from typing import Union

from .commons.constants import Settings
from .commons.tools import unzip
from .configs.chromium_options import ChromiumOptions
from .configs.options_manage import OptionsManager
from .session_page import SessionPage

try:
    from selenium import webdriver
    from DrissionPage.mixpage.drission import Drission
    from .configs.driver_options import DriverOptions
except ModuleNotFoundError:
    pass


def raise_when_ele_not_found(on_off=True):
    """设置全局变量，找不到元素时是否抛出异常
    :param on_off: True 或 False
    :return: None
    """
    Settings.raise_ele_not_found = on_off


def configs_to_here(save_name=None):
    """把默认ini文件复制到当前目录
    :param save_name: 指定文件名，为None则命名为'dp_configs.ini'
    :return: None
    """
    om = OptionsManager('default')
    save_name = f'{save_name}.ini' if save_name is not None else 'dp_configs.ini'
    om.save(save_name)


def show_settings(ini_path=None):
    """打印ini文件内容
    :param ini_path: ini文件路径
    :return: None
    """
    OptionsManager(ini_path).show()


def set_paths(driver_path=None,
              chrome_path=None,
              browser_path=None,
              local_port=None,
              debugger_address=None,
              download_path=None,
              user_data_path=None,
              cache_path=None,
              ini_path=None,
              check_version=False):
    """快捷的路径设置函数
    :param driver_path: chromedriver.exe路径
    :param chrome_path: 浏览器可执行文件路径
    :param browser_path: 浏览器可执行文件路径
    :param local_port: 本地端口号
    :param debugger_address: 调试浏览器地址，例：127.0.0.1:9222
    :param download_path: 下载文件路径
    :param user_data_path: 用户数据路径
    :param cache_path: 缓存路径
    :param ini_path: 要修改的ini文件路径
    :param check_version: 是否检查chromedriver和chrome是否匹配
    :return: None
    """
    om = OptionsManager(ini_path)

    def format_path(path: str) -> str:
        return str(path) if path else ''

    if driver_path is not None:
        om.set_item('paths', 'chromedriver_path', format_path(driver_path))

    if chrome_path is not None:
        om.set_item('chrome_options', 'binary_location', format_path(chrome_path))

    if browser_path is not None:
        om.set_item('chrome_options', 'binary_location', format_path(browser_path))

    if local_port is not None:
        om.set_item('chrome_options', 'debugger_address', f'127.0.0.1:{local_port}')

    if debugger_address is not None:
        address = debugger_address.replace('localhost', '127.0.0.1').lstrip('http://').lstrip('https://')
        om.set_item('chrome_options', 'debugger_address', address)

    if download_path is not None:
        om.set_item('paths', 'download_path', format_path(download_path))

    om.save()

    if user_data_path is not None:
        set_argument('--user-data-dir', format_path(user_data_path), ini_path)

    if cache_path is not None:
        set_argument('--disk-cache-dir', format_path(cache_path), ini_path)

    if check_version:
        check_driver_version(format_path(driver_path), format_path(browser_path))


def use_auto_port(on_off=True, ini_path=None):
    """设置启动浏览器时使用自动分配的端口和临时文件夹
    :param on_off: 是否开启自动端口
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    if not isinstance(on_off, bool):
        raise TypeError('on_off参数只能输入bool值。')
    om = OptionsManager(ini_path)
    om.set_item('chrome_options', 'auto_port', on_off)
    om.save()


def use_system_user_path(on_off=True, ini_path=None):
    """设置是否使用系统安装的浏览器默认用户文件夹
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: 当前对象
    """
    if not isinstance(on_off, bool):
        raise TypeError('on_off参数只能输入bool值。')
    om = OptionsManager(ini_path)
    om.set_item('chrome_options', 'system_user_path', on_off)
    om.save()


def set_argument(arg, value=None, ini_path=None):
    """设置浏览器配置argument属性
    :param arg: 属性名
    :param value: 属性值，有值的属性传入值，没有的传入None
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    co = ChromiumOptions(ini_path=ini_path)
    co.set_argument(arg, value)
    co.save()


def set_headless(on_off=True, ini_path=None):
    """设置是否隐藏浏览器界面
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    on_off = 'new' if on_off else False
    set_argument('--headless', on_off, ini_path)


def set_no_imgs(on_off=True, ini_path=None):
    """设置是否禁止加载图片
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    on_off = None if on_off else False
    set_argument('--blink-settings=imagesEnabled=false', on_off, ini_path)


def set_no_js(on_off=True, ini_path=None):
    """设置是否禁用js
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    on_off = None if on_off else False
    set_argument('--disable-javascript', on_off, ini_path)


def set_mute(on_off=True, ini_path=None):
    """设置是否静音
    :param on_off: 开或关
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    on_off = None if on_off else False
    set_argument('--mute-audio', on_off, ini_path)


def set_user_agent(user_agent, ini_path=None):
    """设置user agent
    :param user_agent: user agent文本
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    set_argument('--user-agent', user_agent, ini_path)


def set_proxy(proxy, ini_path=None):
    """设置代理
    :param proxy: 代理网址和端口
    :param ini_path: 要修改的ini文件路径
    :return: None
    """
    set_argument('--proxy-server', proxy, ini_path)


def check_driver_version(driver_path=None, chrome_path=None):
    """检查传入的chrome和chromedriver是否匹配
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
              f'或自行从以下网址下载：http://npm.taobao.org/mirrors/chromedriver/')

        return False


# -------------------------自动识别chrome版本号并下载对应driver------------------------
def get_match_driver(ini_path='default',
                     save_path=None,
                     chrome_path=None,
                     show_msg=True,
                     check_version=True):
    """自动识别chrome版本并下载匹配的driver
    :param ini_path: 要读取和修改的ini文件路径
    :param save_path: chromedriver保存路径
    :param chrome_path: 指定chrome.exe位置
    :param show_msg: 是否打印信息
    :param check_version: 是否检查版本匹配
    :return: None
    """
    save_path = save_path or str(Path(__file__).parent)

    chrome_path = chrome_path or get_chrome_path(ini_path, show_msg)
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


def get_chrome_path(ini_path=None,
                    show_msg=True,
                    from_ini=True,
                    from_regedit=True,
                    from_system_path=True):
    """从ini文件或系统变量中获取chrome.exe的路径
    :param ini_path: ini文件路径
    :param show_msg: 是否打印信息
    :param from_ini: 是否从ini文件获取
    :param from_regedit: 是否从注册表获取
    :param from_system_path: 是否从系统路径获取
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

    from platform import system
    if system().lower() != 'windows':
        return None

    # -----------从注册表中获取--------------
    if from_regedit:
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe',
                                 reserved=0, access=winreg.KEY_READ)
            # key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon\version',
            #                      reserved=0, access=winreg.KEY_READ)
            k = winreg.EnumValue(key, 0)
            winreg.CloseKey(key)

            if show_msg:
                print('注册表中', end='')

            return k[1]

        except FileNotFoundError:
            pass

    # -----------从系统变量中获取--------------
    if from_system_path:
        try:
            paths = popen('set path').read().lower()
        except:
            return None
        r = search(r'[^;]*chrome[^;]*', paths)

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
    """根据文件路径获取版本号
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
    """根据传入的版本号到镜像网站查找，下载最相近的
    :param version: 本地版本号
    :return: 保存地址
    """
    if not version:
        return

    main_ver = version.split('.')[0]
    remote_ver = None

    page = SessionPage(Drission().session)
    page.get('https://registry.npmmirror.com/-/binary/chromedriver/')

    for version in page.json:
        # 遍历所有版本，跳过大版本不一致的，如果有完全匹配的，获取url，如果没有，获取最后一个版本的url
        if not version['name'].startswith(f'{main_ver}.'):
            continue

        remote_ver = version['name']
        if version['name'] == f'{version}/':
            break

    if remote_ver:
        url = f'https://cdn.npmmirror.com/binaries/chromedriver/{remote_ver}chromedriver_win32.zip'
        save_path = save_path or str(Path(__file__).parent)
        result = page.download(url, save_path, file_exists='overwrite', show_msg=show_msg)

        if result[0]:
            return result[1]

    return None
