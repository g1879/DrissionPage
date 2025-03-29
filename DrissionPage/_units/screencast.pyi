# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Optional

from .._pages.chromium_base import ChromiumBase


class Screencast(object):
    _owner: ChromiumBase = ...
    _path: Optional[Path] = ...
    _tmp_path: Optional[Path] = ...
    _running: bool = ...
    _enable: bool = ...
    _mode: str = ...

    def __init__(self, owner: ChromiumBase):
        """
        :param owner: 页面对象
        """

    @property
    def set_mode(self) -> ScreencastMode:
        """返回用于设置录屏幕式的对象"""
        ...

    def start(self, save_path: Union[str, Path] = None) -> None:
        """开始录屏
        :param save_path: 录屏保存位置
        :return: None
        """
        ...

    def stop(self, video_name: str = None, suffix: str='mp4', coding:str='mp4v') -> str:
        """停止录屏
        :param video_name: 视频文件名，为None时以当前时间名命
        :param suffix: 文件后缀名
        :param coding: 视频编码格式，仅video_mode模式有效，根据cv2.VideoWriter_fourcc()定义
        :return: 文件路径
        """
        ...

    def set_save_path(self, save_path: Union[str, Path] = None) -> None:
        """设置保存路径
        :param save_path: 保存路径
        :return: None
        """
        ...

    def _run(self) -> None:
        """非节俭模式运行方法"""
        ...

    def _onScreencastFrame(self, **kwargs) -> None:
        """节俭模式运行方法"""
        ...


class ScreencastMode(object):
    _screencast: Screencast = ...

    def __init__(self, screencast: Screencast):
        """
        :param screencast: Screencast对象
        """
        ...

    def video_mode(self) -> None:
        """持续视频模式，生成的视频没有声音"""
        ...

    def frugal_video_mode(self) -> None:
        """设置节俭视频模式，页面有变化时才录制，生成的视频没有声音"""
        ...

    def js_video_mode(self) -> None:
        """设置使用js录制视频模式，可生成有声音的视频，但需要手动启动"""
        ...

    def frugal_imgs_mode(self) -> None:
        """设置节俭视频模式，页面有变化时才截图"""
        ...

    def imgs_mode(self) -> None:
        """设置图片模式，持续对页面进行截图"""
        ...
