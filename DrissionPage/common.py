# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from ._elements.session_element import make_session_ele
from ._functions.by import By
from ._functions.elements import get_eles
from ._functions.keys import Keys
from ._functions.settings import Settings
from ._functions.tools import wait_until, configs_to_here
from ._functions.web import get_blob, tree
from ._pages.chromium_page import ChromiumPage
from ._units.actions import Actions

__all__ = ['make_session_ele', 'Actions', 'Keys', 'By', 'Settings', 'wait_until', 'configs_to_here', 'get_blob',
           'tree', 'from_selenium', 'from_playwright', 'get_eles']


def from_selenium(driver):
    """从selenium的WebDriver对象生成ChromiumPage对象"""
    address, port = driver.caps.get('goog:chromeOptions', {}).get('debuggerAddress', ':').split(':')
    if not address:
        raise RuntimeError('获取失败。')
    return ChromiumPage(f'{address}:{port}')


def from_playwright(page_or_browser):
    """从playwright的Page或Browser对象生成ChromiumPage对象"""
    if hasattr(page_or_browser, 'context'):
        page_or_browser = page_or_browser.context.browser
    try:
        processes = page_or_browser.new_browser_cdp_session().send('SystemInfo.getProcessInfo')['processInfo']
        for process in processes:
            if process['type'] == 'browser':
                pid = process['id']
                break
        else:
            raise RuntimeError('获取失败。')
    except:
        raise RuntimeError('获取失败。')

    from psutil import net_connections
    for con_info in net_connections():
        if con_info.pid == pid:
            port = con_info.laddr.port
            break
    else:
        raise RuntimeError('获取失败。')
    return ChromiumPage(f'127.0.0.1:{port}')
