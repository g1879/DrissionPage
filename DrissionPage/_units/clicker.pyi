# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union

from .downloader import DownloadMission
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_tab import ChromiumTab
from .._pages.mix_tab import MixTab


class Clicker(object):
    _ele: ChromiumElement = ...

    def __init__(self, ele: ChromiumElement):
        """
        :param ele: ChromiumElement
        """
        ...

    def __call__(self, by_js: Union[bool, str, None] = False,
                 timeout: float = 1.5, wait_stop: bool = True) -> Union[ChromiumElement, False]:
        """点击元素
        如果遇到遮挡，可选择是否用js点击
        :param by_js: 是否用js点击，为None时先用模拟点击，遇到遮挡改用js，为True时直接用js点击，为False时只用模拟点击
        :param timeout: 模拟点击的超时时间（秒），等待元素可见、可用、进入视口
        :param wait_stop: 是否等待元素运动结束再执行点击
        :return: 是否点击成功
        """
        ...

    def left(self, by_js: Union[bool, str, None] = False,
             timeout: float = 1.5, wait_stop: bool = True) -> Union[ChromiumElement, False]:
        """点击元素，可选择是否用js点击
        :param by_js: 是否用js点击，为None时先用模拟点击，遇到遮挡改用js，为True时直接用js点击，为False时只用模拟点击
        :param timeout: 模拟点击的超时时间（秒），等待元素可见、可用、进入视口
        :param wait_stop: 是否等待元素运动结束再执行点击
        :return: 是否点击成功
        """
        ...

    def right(self) -> ChromiumElement:
        """右键单击"""
        ...

    def middle(self, get_tab: bool = True) -> Union[ChromiumTab, MixTab, None]:
        """中键单击，默认返回新出现的tab对象
        :param get_tab: 是否返回新tab对象，为False则返回None
        :return: Tab对象或None
        """
        ...

    def at(self,
           offset_x: float = None,
           offset_y: float = None,
           button: str = 'left',
           count: int = 1) -> ChromiumElement:
        """带偏移量点击本元素，相对于左上角坐标。不传入x或y值时点击元素中间点
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :param button: 点击哪个键，可选 left, middle, right, back, forward
        :param count: 点击次数
        :return: None
        """
        ...

    def multi(self, times: int = 2) -> ChromiumElement:
        """多次点击
        :param times: 默认双击
        :return: None
        """
        ...

    def to_download(self,
                    save_path: Union[str, Path] = None,
                    rename: str = None,
                    suffix: str = None,
                    new_tab: bool = None,
                    by_js: bool = False,
                    timeout: float = None) -> DownloadMission:
        """点击触发下载
        :param save_path: 保存路径，为None保存在原来设置的，如未设置保存到当前路径
        :param rename: 重命名文件名
        :param suffix: 指定文件后缀
        :param new_tab: 下载任务是否从新标签页触发，为None会自动获取，如获取不到，设为True
        :param by_js: 是否用js方式点击，逻辑与click()一致
        :param timeout: 等待下载触发的超时时间，为None则使用页面对象设置
        :return: DownloadMission对象
        """
        ...

    def to_upload(self, file_paths: Union[str, Path, list, tuple], by_js: bool = False) -> None:
        """触发上传文件选择框并自动填入指定路径
        :param file_paths: 文件路径，如果上传框支持多文件，可传入列表或字符串，字符串时多个文件用回车分隔
        :param by_js: 是否用js方式点击，逻辑与click()一致
        :return: None
        """
        ...

    def for_new_tab(self, by_js: bool = False, timeout: float = 3) -> Union[ChromiumTab, MixTab]:
        """点击后等待新tab出现并返回其对象
        :param by_js: 是否使用js点击，逻辑与click()一致
        :param timeout: 等待超时时间
        :return: 新标签页对象，如果没有等到新标签页出现则抛出异常
        """
        ...

    def for_url_change(self, text: str = None, exclude: bool = False,
                       by_js: bool = False, timeout: float = None) -> bool:
        """点击并等待tab的url变成包含或不包含指定文本
        :param text: 用于识别的文本，为None等待当前url变化
        :param exclude: 是否排除，为True时当url不包含text指定文本时返回True，text为None时自动设为True
        :param by_js: 是否用js点击
        :param timeout: 超时时间（秒），为None使用页面设置
        :return: 是否等待成功
        """
        ...

    def for_title_change(self, text: str = None, exclude: bool = False,
                         by_js: bool = False, timeout: float = None) -> bool:
        """点击并等待tab的title变成包含或不包含指定文本
        :param text: 用于识别的文本，为None等待当前title变化
        :param exclude: 是否排除，为True时当title不包含text指定文本时返回True，text为None时自动设为True
        :param by_js: 是否用js点击
        :param timeout: 超时时间（秒），为None使用页面设置
        :return: 是否等待成功
        """
        ...

    def _click(self,
               view_x: float,
               view_y: float,
               button: str = 'left',
               count: int = 1) -> ChromiumElement:
        """实施点击
        :param view_x: 视口x坐标
        :param view_y: 视口y坐标
        :param button: 'left' 'right' 'middle'  'back' 'forward'
        :param count: 点击次数
        :return: None
        """
        ...
