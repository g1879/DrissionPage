# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from ._base.chromium import Chromium
from ._configs.chromium_options import ChromiumOptions
from ._elements.session_element import make_session_ele
from ._functions.by import By
from ._functions.keys import Keys
from ._functions.settings import Settings
from ._functions.tools import wait_until, configs_to_here
from ._functions.web import get_blob, tree
from ._units.actions import Actions

__all__ = ['make_session_ele', 'Actions', 'Keys', 'By', 'Settings', 'wait_until', 'configs_to_here', 'get_blob',
           'tree', 'from_selenium', 'from_playwright']


def from_selenium(driver):
    """从selenium的WebDriver对象生成Chromium对象"""
    address, port = driver.caps.get('goog:chromeOptions', {}).get('debuggerAddress', ':').split(':')
    if not address:
        raise RuntimeError(Settings._lang.join(Settings._lang.GET_OBJ_FAILED))
    co = ChromiumOptions().set_local_port(port)
    co._ua_set = True
    return Chromium(co)


def from_playwright(page_or_browser):
    """从playwright的Page或Browser对象生成Chromium对象"""
    if hasattr(page_or_browser, 'context'):
        page_or_browser = page_or_browser.context.browser
    try:
        processes = page_or_browser.new_browser_cdp_session().send('SystemInfo.getProcessInfo')['processInfo']
        for process in processes:
            if process['type'] == 'browser':
                pid = process['id']
                break
        else:
            raise RuntimeError(Settings._lang.join(Settings._lang.GET_OBJ_FAILED))
    except:
        raise RuntimeError(Settings._lang.join(Settings._lang.GET_OBJ_FAILED))

    from psutil import net_connections
    for con_info in net_connections():
        if con_info.pid == pid:
            port = con_info.laddr.port
            break
    else:
        raise RuntimeError(Settings._lang.join(Settings._lang.GET_OBJ_FAILED, TIP=Settings._lang.RUN_BY_ADMIN))
    co = ChromiumOptions().set_local_port(f'127.0.0.1:{port}')
    co._ua_set = True
    return Chromium(co)
