# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from click import command, option

from .._functions.tools import configs_to_here as ch
from .._configs.chromium_options import ChromiumOptions
from .._pages.chromium_page import ChromiumPage


@command()
@option("-p", "--set-browser-path", help="设置浏览器路径")
@option("-u", "--set-user-path", help="设置用户数据路径")
@option("-c", "--configs-to-here", is_flag=True, help="复制默认配置文件到当前路径")
@option("-l", "--launch-browser", default=-1, help="启动浏览器，传入端口号，0表示用配置文件中的值")
def main(set_browser_path, set_user_path, configs_to_here, launch_browser):
    if set_browser_path:
        set_paths(browser_path=set_browser_path)

    if set_user_path:
        set_paths(user_data_path=set_user_path)

    if configs_to_here:
        ch()

    if launch_browser >= 0:
        port = f'127.0.0.1:{launch_browser}' if launch_browser else None
        ChromiumPage(port)


def set_paths(browser_path=None, user_data_path=None):
    """快捷的路径设置函数
    :param browser_path: 浏览器可执行文件路径
    :param user_data_path: 用户数据路径
    :return: None
    """
    co = ChromiumOptions()

    if browser_path is not None:
        co.set_browser_path(browser_path)

    if user_data_path is not None:
        co.set_user_data_path(user_data_path)

    co.save()


if __name__ == '__main__':
    main()
