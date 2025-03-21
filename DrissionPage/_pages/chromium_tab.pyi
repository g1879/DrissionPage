# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Optional

from .chromium_base import ChromiumBase
from .._base.chromium import Chromium
from .._units.rect import TabRect
from .._units.setter import TabSetter
from .._units.waiter import TabWaiter


class ChromiumTab(ChromiumBase):
    """实现浏览器标签页的类"""
    _TABS: dict = ...
    _tab: ChromiumTab = ...
    _rect: Optional[TabRect] = ...

    def __new__(cls, browser: Chromium, tab_id: str):
        """
        :param browser: Browser对象
        :param tab_id: 标签页id
        """
        ...

    def __init__(self, browser: Chromium, tab_id: str):
        """
        :param browser: Browser对象
        :param tab_id: 标签页id
        """
        ...

    def _d_set_runtime_settings(self) -> None:
        """重写设置浏览器运行参数方法"""
        ...

    def close(self, others: bool = False) -> None:
        """关闭标签页
        :param others: 是否关闭其它，保留自己
        :return: None
        """
        ...

    @property
    def set(self) -> TabSetter:
        """返回用于设置的对象"""
        ...

    @property
    def wait(self) -> TabWaiter:
        """返回用于等待的对象"""
        ...

    def save(self,
             path: Union[str, Path] = None,
             name: str = None,
             as_pdf: bool = False,
             landscape: bool = False,
             displayHeaderFooter: bool = False,
             printBackground: bool = False,
             scale: float = 1,
             paperWidth: float = 8.5,
             paperHeight: float = 11,
             marginTop: float = 11,
             marginBottom: float = 1,
             marginLeft: float = 1,
             marginRight: float = 1,
             pageRanges: str = '',
             headerTemplate: str = '',
             footerTemplate: str = '',
             preferCSSPageSize: bool = False,
             generateTaggedPDF: bool = ...,
             generateDocumentOutline: bool = ...) -> Union[bytes, str]:
        """把当前页面保存为文件，如果path和name参数都为None，只返回文本
        :param path: 保存路径，为None且name不为None时保存在当前路径
        :param name: 文件名，为None且path不为None时用title属性值
        :param as_pdf: 为Ture保存为pdf，否则为mhtml且忽略kwargs参数
        :param landscape: 纸张方向，as_pdf为True时才生效
        :param displayHeaderFooter: 是否显示页头页脚，as_pdf为True时才生效
        :param printBackground: 是否打印背景图片，as_pdf为True时才生效
        :param scale: 缩放比例，as_pdf为True时才生效
        :param paperWidth: 页面宽度（英寸），as_pdf为True时才生效
        :param paperHeight: 页面高度（英寸），as_pdf为True时才生效
        :param marginTop: 上边距（英寸），as_pdf为True时才生效
        :param marginBottom: 下边距（英寸），as_pdf为True时才生效
        :param marginLeft: 左边距（英寸），as_pdf为True时才生效
        :param marginRight: 右边距（英寸），as_pdf为True时才生效
        :param pageRanges: 页面范围，格式'1-5, 8, 11-13'，as_pdf为True时才生效
        :param headerTemplate: 页头HTML模板，as_pdf为True时才生效
                模板可包含以下class：
                - date：日期
                - title：文档标题
                - url：文档url
                - pageNumber：当前页码
                - totalPages：总页数
                示例：<span class=title></span>
        :param footerTemplate: 页脚HTML模板，格式与页头的一样，as_pdf为True时才生效
        :param preferCSSPageSize: 是否使用css定义的页面大小，as_pdf为True时才生效
        :param generateTaggedPDF: 是否生成带标签的(可访问的)PDF。默认为嵌入器选择，as_pdf为True时才生效
        :param generateDocumentOutline: 是否将文档大纲嵌入到PDF中。，as_pdf为True时才生效
        :return: as_pdf为True时返回bytes，否则返回文件文本
        """
        ...

    def _on_disconnect(self): ...
