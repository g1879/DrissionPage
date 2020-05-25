# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_page.py
"""
from selenium import webdriver
import re

from DrissionPage.config import OptionsManager, DriverOptions


def set_paths(driver_path: str = None,
              chrome_path: str = None,
              debugger_address: str = None,
              global_tmp_path: str = None,
              download_path: str = None) -> None:
    """简易设置路径函数
    :param driver_path: chromedriver.exe路径
    :param chrome_path: chrome.exe路径
    :param debugger_address: 调试浏览器地址，例：127.0.0.1:9222
    :param download_path: 下载文件路径
    :param global_tmp_path: 临时文件夹路径
    :return: None
    """
    om = OptionsManager()
    if driver_path is not None:
        om.set_item('paths', 'chromedriver_path', driver_path)
    if chrome_path is not None:
        om.set_item('chrome_options', 'binary_location', chrome_path)
    if debugger_address is not None:
        om.set_item('chrome_options', 'debugger_address', debugger_address)
    if global_tmp_path is not None:
        om.set_item('paths', 'global_tmp_path', global_tmp_path)
    if download_path is not None:
        experimental_options = om.get_value('chrome_options', 'experimental_options')
        experimental_options['prefs']['download.default_directory'] = download_path
        om.set_item('chrome_options', 'experimental_options', experimental_options)
    om.save()
    check_driver_version(driver_path, chrome_path)


def check_driver_version(driver_path: str = None, chrome_path: str = None) -> bool:
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
        r = re.search(r'chromedriver=(.+?) ', str(e))
        info = f'''
版本不兼容。
请下载与当前chrome版本匹配的chromedriver。
当前chromedriver版本：{r.group(1)}
查看chrome版本方法：帮助 -> 关于Google Chrome
chromedriver下载网址：https://chromedriver.chromium.org/downloads
'''
        print(info)
        return False
