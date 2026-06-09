# -*- coding:utf-8 -*-
from typing import Optional, Union

from .._browsers.chromium import Chromium
from .._browsers.chromium_context import ChromiumContext


class BrowserPermSetter(object):
    _owner: Union[Chromium, ChromiumContext] = ...
    _context_id: Optional[str] = ...

    def __init__(self, owner: Union[Chromium, ChromiumContext], context_id: Optional[str] = None):
        ...

    def _set_perm(self, data: dict, allow: bool = True) -> None:
        ...

    def geolocation(self, allow: bool = True) -> None:
        """地理位置权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def notifications(self, allow: bool = True) -> None:
        """通知权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def push(self, allow: bool = True) -> None:
        """推送消息权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def midi(self, allow: bool = True, sysex: bool = None) -> None:
        """MIDI设备访问权限
        :param allow: 允许或禁止
        :param sysex: 是否允许系统独占消息发送
        :return: None
        """
        ...

    def camera(self, allow: bool = True, panTiltZoom: bool = None) -> None:
        """摄像头权限
        :param allow: 允许或禁止
        :param panTiltZoom: 是否允许变焦
        :return: None
        """
        ...

    def microphone(self, allow: bool = True) -> None:
        """麦克风权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def background_fetch(self, allow: bool = True) -> None:
        """后台获取权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def background_sync(self, allow: bool = True) -> None:
        """后台同步权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def persistent_storage(self, allow: bool = True) -> None:
        """持久化存储权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def ambient_light_sensor(self, allow: bool = True) -> None:
        """环境光传感器权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def accelerometer(self, allow: bool = True) -> None:
        """加速度计权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def gyroscope(self, allow: bool = True) -> None:
        """陀螺仪权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def magnetometer(self, allow: bool = True) -> None:
        """磁力计权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def screen_wake_lock(self, allow: bool = True) -> None:
        """屏幕唤醒锁权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def nfc(self, allow: bool = True) -> None:
        """NFC近场通信权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def display_capture(self, allow: bool = True) -> None:
        """屏幕捕获权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def clipboard_read(self, allow: bool = True, allowWithoutSanitization: bool = None) -> None:
        """剪贴板读取权限
        :param allow: 允许或禁止
        :param allowWithoutSanitization: 是否允许不进行清理操作
        :return: None
        """
        ...

    def clipboard_write(self, allow: bool = True, allowWithoutSanitization: bool = None) -> None:
        """剪贴板写入权限
        :param allow: 允许或禁止
        :param allowWithoutSanitization: 是否允许不进行清理操作
        :return: None
        """
        ...

    def payment_handler(self, allow: bool = True) -> None:
        """支付处理器权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def idle_detection(self, allow: bool = True) -> None:
        """空闲检测权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def periodic_background_sync(self, allow: bool = True) -> None:
        """周期性后台同步权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def system_wake_lock(self, allow: bool = True) -> None:
        """系统唤醒锁权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def storage_access(self, allow: bool = True) -> None:
        """存储访问权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def window_management(self, allow: bool = True) -> None:
        """窗口管理权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def local_fonts(self, allow: bool = True) -> None:
        """本地字体访问权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def top_level_storage_access(self, allow: bool = True) -> None:
        """顶级存储访问权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def captured_surface_control(self, allow: bool = True) -> None:
        """捕获表面控制权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def speaker_selection(self, allow: bool = True) -> None:
        """扬声器选择权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def keyboard_lock(self, allow: bool = True) -> None:
        """键盘锁定权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def pointer_lock(self, allow: bool = True) -> None:
        """指针锁定权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def fullscreen(self, allow: bool = True) -> None:
        """全屏权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def web_app_installation(self, allow: bool = True) -> None:
        """Web应用安装权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def local_network_access(self, allow: bool = True) -> None:
        """本地网络访问权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def local_network(self, allow: bool = True) -> None:
        """本地网络权限
        :param allow: 允许或禁止
        :return: None
        """
        ...

    def loopback_network(self, allow: bool = True) -> None:
        """回环网络权限
        :param allow: 允许或禁止
        :return: None
        """
        ...
