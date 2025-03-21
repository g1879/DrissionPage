# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Tuple, List, Any, Optional, Literal

from .chromium_base import ChromiumBase
from .chromium_tab import ChromiumTab
from .mix_tab import MixTab
from .._elements.chromium_element import ChromiumElement, ShadowRoot
from .._functions.elements import ChromiumElementsList
from .._units.listener import FrameListener
from .._units.rect import FrameRect
from .._units.scroller import FrameScroller
from .._units.setter import ChromiumFrameSetter
from .._units.states import FrameStates
from .._units.waiter import FrameWaiter


class ChromiumFrame(ChromiumBase):
    _Frames: dict = ...
    _target_page: Union[ChromiumTab, ChromiumFrame] = ...
    _tab: Union[MixTab, ChromiumTab] = ...
    _set: ChromiumFrameSetter = ...
    _frame_ele: ChromiumElement = ...
    _backend_id: int = ...
    _doc_ele: ChromiumElement = ...
    _is_diff_domain: bool = ...
    doc_ele: ChromiumElement = ...
    _states: FrameStates = ...
    _reloading: bool = ...
    _rect: Optional[FrameRect] = ...
    _listener: FrameListener = ...

    def __init__(self,
                 owner: Union[ChromiumTab, ChromiumFrame],
                 ele: ChromiumElement,
                 info: dict = None):
        """
        :param owner: frame所在的页面对象
        :param ele: frame所在元素
        :param info: frame所在元素信息
        """
        ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str],
                 index: int = 1,
                 timeout: float = None) -> ChromiumElement:
        """在内部查找元素
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 超时时间（秒）
        :return: ChromiumElement对象或属性、文本
        """
        ...

    def __repr__(self) -> str: ...

    def __eq__(self, other: ChromiumFrame) -> bool: ...

    def _d_set_runtime_settings(self) -> None:
        """重写设置浏览器运行参数方法"""
        ...

    def _driver_init(self, target_id: str, is_init: bool = True) -> None:
        """避免出现服务器500错误
        :param target_id: 要跳转到的target id
        :return: None
        """
        ...

    def _reload(self) -> None:
        """重新获取document"""
        ...

    def _get_document(self, timeout: float = 10) -> bool:
        """刷新cdp使用的document数据
        :param timeout: 超时时间（秒）
        :return: 是否获取成功
        """
        ...

    def _onFrameStoppedLoading(self, **kwargs): ...

    def _onInspectorDetached(self, **kwargs): ...

    @property
    def scroll(self) -> FrameScroller:
        """返回用于滚动的对象"""
        ...

    @property
    def set(self) -> ChromiumFrameSetter:
        """返回用于设置的对象"""
        ...

    @property
    def states(self) -> FrameStates:
        """返回用于获取状态信息的对象"""
        ...

    @property
    def wait(self) -> FrameWaiter:
        """返回用于等待的对象"""
        ...

    @property
    def rect(self) -> FrameRect:
        """返回获取坐标和大小的对象"""
        ...

    @property
    def listen(self) -> FrameListener:
        """返回用于聆听数据包的对象"""
        ...

    @property
    def _obj_id(self) -> str: ...

    @property
    def _node_id(self) -> int: ...

    @property
    def owner(self) -> ChromiumBase:
        """返回所属页面对象"""
        ...

    @property
    def frame_ele(self) -> ChromiumElement:
        """返回总页面上的frame元素"""
        ...

    @property
    def tag(self) -> str:
        """返回元素tag"""
        ...

    @property
    def url(self) -> str:
        """返回frame当前访问的url"""
        ...

    @property
    def html(self) -> str:
        """返回元素outerHTML文本"""
        ...

    @property
    def inner_html(self) -> str:
        """返回元素innerHTML文本"""
        ...

    @property
    def link(self) -> str:
        """返回href或src绝对url"""
        ...

    @property
    def title(self) -> str:
        """返回页面title"""
        ...

    @property
    def attrs(self) -> dict:
        """返回frame元素所有attribute属性"""
        ...

    @property
    def active_ele(self) -> ChromiumElement:
        """返回当前焦点所在元素"""
        ...

    @property
    def xpath(self) -> str:
        """返回frame的xpath绝对路径"""
        ...

    @property
    def css_path(self) -> str:
        """返回frame的css selector绝对路径"""
        ...

    @property
    def tab(self) -> Union[ChromiumTab, MixTab]:
        """返回frame所在的tab对象"""
        ...

    @property
    def tab_id(self) -> str:
        """返回frame所在tab的id"""
        ...

    @property
    def download_path(self) -> str:
        """返回下载文件保存路径"""
        ...

    @property
    def sr(self) -> Union[None, ShadowRoot]:
        """返回iframe的shadow-root元素对象"""
        ...

    @property
    def shadow_root(self) -> Union[None, ShadowRoot]:
        """返回iframe的shadow-root元素对象"""
        ...

    @property
    def child_count(self) -> int:
        """返回直接子元素的个数"""
        ...

    @property
    def _js_ready_state(self) -> Literal['loading', 'interactive', 'complete']:
        """返回当前页面加载状态"""
        ...

    def refresh(self) -> None:
        """刷新frame页面"""
        ...

    def property(self, name: str) -> Union[str, None]:
        """返回frame元素一个property属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        ...

    def attr(self, name: str) -> Union[str, None]:
        """返回frame元素一个attribute属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        ...

    def remove_attr(self, name: str) -> None:
        """删除frame元素attribute属性
        :param name: 属性名
        :return: None
        """
        ...

    def style(self, style: str, pseudo_ele: str = '') -> str:
        """返回frame元素样式属性值，可获取伪元素属性值
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        ...

    def run_js(self,
               script: str,
               *args,
               as_expr: bool = False,
               timeout: float = None) -> Any:
        """运行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        ...

    def _run_js(self,
                script: str,
                *args,
                as_expr: bool = False,
                timeout: float = None) -> Any:
        """运行javascript代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        ...

    def parent(self,
               level_or_loc: Union[Tuple[str, str], str, int] = 1,
               index: int = 1,
               timeout: float = 0) -> ChromiumElement:
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，1开始，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果，1开始
        :param timeout: 查找超时时间（秒）
        :return: 上级元素对象
        """
        ...

    def prev(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = 0,
             ele_only: bool = True) -> Union[ChromiumElement, str]:
        """返回当前元素前面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点
        """
        ...

    def next(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = 0,
             ele_only: bool = True) -> Union[ChromiumElement, str]:
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点
        """
        ...

    def before(self,
               locator: Union[Tuple[str, str], str, int] = '',
               index: int = 1,
               timeout: float = None,
               ele_only: bool = True) -> Union[ChromiumElement, str]:
        """返回文档中当前元素前面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        ...

    def after(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[ChromiumElement, str]:
        """返回文档中此当前元素后面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        ...

    def prevs(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = 0,
              ele_only: bool = True) -> List[Union[ChromiumElement, str]]:
        """返回当前元素前面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点文本组成的列表
        """
        ...

    def nexts(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = 0,
              ele_only: bool = True) -> List[Union[ChromiumElement, str]]:
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 同级元素或节点文本组成的列表
        """
        ...

    def befores(self,
                locator: Union[Tuple[str, str], str] = '',
                timeout: float = None,
                ele_only: bool = True) -> List[Union[ChromiumElement, str]]:
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        ...

    def afters(self,
               locator: Union[Tuple[str, str], str] = '',
               timeout: float = None,
               ele_only: bool = True) -> List[Union[ChromiumElement, str]]:
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        ...

    def get_screenshot(self,
                       path: [str, Path] = None,
                       name: str = None,
                       as_bytes: [bool, str] = None,
                       as_base64: [bool, str] = None) -> Union[str, bytes]:
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 文件保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :return: 图片完整路径或字节文本
        """
        ...

    def _get_screenshot(self,
                        path: [str, Path] = None,
                        name: str = None,
                        as_bytes: [bool, str] = None,
                        as_base64: [bool, str] = None,
                        full_page: bool = False,
                        left_top: Tuple[int, int] = None,
                        right_bottom: Tuple[int, int] = None,
                        ele: ChromiumElement = None) -> Union[str, bytes]:
        """实现截图
        :param path: 文件保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :param ele: 为异域iframe内元素截图设置
        :return: 图片完整路径或字节文本
        """
        ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str, ChromiumElement, ChromiumFrame],
                       timeout: float,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = None) -> Union[ChromiumElement, ChromiumFrame, None, ChromiumElementsList]:
        """在frame内查找单个元素
        :param locator: 定位符或元素对象
        :param timeout: 查找超时时间（秒）
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: MixTab用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象
        """
        ...

    def _is_inner_frame(self) -> bool:
        """返回当前frame是否同域"""
        ...
