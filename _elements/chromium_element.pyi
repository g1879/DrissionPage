# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Tuple, List, Any, Literal, Optional

from .._base.base import DrissionElement, BaseElement
from .._elements.session_element import SessionElement
from .._functions.elements import SessionElementsList, ChromiumElementsList
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._pages.chromium_tab import ChromiumTab
from .._pages.web_page import WebPage
from .._units.clicker import Clicker
from .._units.rect import ElementRect
from .._units.scroller import ElementScroller
from .._units.selector import SelectElement
from .._units.setter import ChromiumElementSetter
from .._units.states import ShadowRootStates, ElementStates
from .._units.waiter import ElementWaiter

PIC_TYPE = Literal['jpg', 'jpeg', 'png', 'webp', True]


class ChromiumElement(DrissionElement):
    _tag: Optional[str] = ...
    owner: ChromiumBase = ...
    page: Union[ChromiumPage, WebPage] = ...
    tab: Union[ChromiumPage, ChromiumTab] = ...
    _node_id: int = ...
    _obj_id: str = ...
    _backend_id: int = ...
    _doc_id: Optional[str] = ...
    _scroll: Optional[ElementScroller] = ...
    _clicker: Optional[Clicker] = ...
    _select: Union[SelectElement, None, False] = ...
    _wait: Optional[ElementWaiter] = ...
    _rect: Optional[ElementRect] = ...
    _set: Optional[ChromiumElementSetter] = ...
    _states: Optional[ElementStates] = ...
    _pseudo: Optional[Pseudo] = ...

    def __init__(self,
                 owner: ChromiumBase,
                 node_id: int = None,
                 obj_id: str = None,
                 backend_id: int = None):
        """node_id、obj_id和backend_id必须至少传入一个
        :param owner: 元素所在页面对象
        :param node_id: cdp中的node id
        :param obj_id: js中的object id
        :param backend_id: backend id
        """
        ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str],
                 index: int = 1,
                 timeout: float = None) -> ChromiumElement:
        """在内部查找元素
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间（秒）
        :return: ChromiumElement对象或属性、文本
        """
        ...

    def __repr__(self) -> str: ...

    def __eq__(self, other: ChromiumElement) -> bool: ...

    @property
    def tag(self) -> str:
        """返回元素tag"""
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
    def attrs(self) -> dict:
        """返回元素所有attribute属性"""
        ...

    @property
    def text(self) -> str:
        """返回元素内所有文本，文本已格式化"""
        ...

    @property
    def raw_text(self) -> str:
        """返回未格式化处理的元素内文本"""
        ...

    @property
    def set(self) -> ChromiumElementSetter:
        """返回用于设置元素属性的对象"""
        ...

    @property
    def states(self) -> ElementStates:
        """返回用于获取元素状态的对象"""
        ...

    @property
    def pseudo(self) -> Pseudo:
        """返回用于获取伪元素内容的对象"""
        ...

    @property
    def rect(self) -> ElementRect:
        """返回用于获取元素位置的对象"""
        ...

    @property
    def shadow_root(self) -> Union[None, ShadowRoot]:
        """返回当前元素的shadow_root元素对象"""
        ...

    @property
    def sr(self) -> Union[None, ShadowRoot]:
        """返回当前元素的shadow_root元素对象"""
        ...

    @property
    def scroll(self) -> ElementScroller:
        """用于滚动滚动条的对象"""
        ...

    @property
    def click(self) -> Clicker:
        """返回用于点击的对象"""
        ...

    @property
    def wait(self) -> ElementWaiter:
        """返回用于等待的对象"""
        ...

    @property
    def select(self) -> Union[SelectElement, False]:
        """返回专门处理下拉列表的Select类，非<select>元素返回False"""
        ...

    @property
    def value(self) -> str:
        """返回元素property属性的value值"""
        ...

    def parent(self,
               level_or_loc: Union[tuple, str, int] = 1,
               index: int = 1,
               timeout: float = 0) -> ChromiumElement:
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，1开始，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果，1开始
        :param timeout: 查找超时时间（秒）
        :return: 上级元素对象
        """
        ...

    def child(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[ChromiumElement, str]:
        """返回当前元素的一个符合条件的直接子元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本
        """
        ...

    def prev(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[ChromiumElement, str]:
        """返回当前元素前面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本
        """
        ...

    def next(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[ChromiumElement, str]:
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本
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
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        ...

    def children(self,
                 locator: Union[Tuple[str, str], str] = '',
                 timeout: float = None,
                 ele_only: bool = True) -> Union[ChromiumElementsList, List[Union[ChromiumElement, str]]]:
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        ...

    def prevs(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> Union[ChromiumElementsList, List[Union[ChromiumElement, str]]]:
        """返回当前元素前面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        ...

    def nexts(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> Union[ChromiumElementsList, List[Union[ChromiumElement, str]]]:
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        ...

    def befores(self,
                locator: Union[Tuple[str, str], str] = '',
                timeout: float = None,
                ele_only: bool = True) -> Union[ChromiumElementsList, List[Union[ChromiumElement, str]]]:
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
               ele_only: bool = True) -> Union[ChromiumElementsList, List[Union[ChromiumElement, str]]]:
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        ...

    def over(self, timeout: float = None) -> ChromiumElement:
        """获取覆盖在本元素上最上层的元素
        :param timeout: 等待元素出现的超时时间（秒）
        :return: 元素对象
        """
        ...

    def offset(self,
               locator: Optional[str] = None,
               x: int = None,
               y: int = None,
               timeout: float = None) -> ChromiumElement:
        """获取相对本元素左上角左边指定偏移量位置的元素，如果offset_x和offset_y都是None，定位到元素中间点
        :param locator: 定位符，只支持str，且不支持xpath和css方式
        :param x: 横坐标偏移量，向右为正
        :param y: 纵坐标偏移量，向下为正
        :param timeout: 超时时间（秒），为None使用所在页面设置
        :return: 元素对象
        """
        ...

    def east(self, loc_or_pixel: Union[str, int, None] = None, index: int = 1) -> ChromiumElement:
        """获取元素右边某个指定元素
        :param loc_or_pixel: 定位符，只支持str或int，且不支持xpath和css方式，传入int按像素距离获取
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        ...

    def south(self, loc_or_pixel: Union[str, int, None] = None, index: int = 1) -> ChromiumElement:
        """获取元素下方某个指定元素
        :param loc_or_pixel: 定位符，只支持str或int，且不支持xpath和css方式，传入int按像素距离获取
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        ...

    def west(self, loc_or_pixel: Union[str, int, None] = None, index: int = 1) -> ChromiumElement:
        """获取元素左边某个指定元素
        :param loc_or_pixel: 定位符，只支持str或int，且不支持xpath和css方式，传入int按像素距离获取
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        ...

    def north(self, loc_or_pixel: Union[str, int, None] = None, index: int = 1) -> ChromiumElement:
        """获取元素上方某个指定元素
        :param loc_or_pixel: 定位符，只支持str或int，且不支持xpath和css方式，传入int按像素距离获取
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        ...

    def _get_relative_eles(self,
                           mode: str = 'north',
                           locator: Union[int, str] = None,
                           index: int = 1) -> ChromiumElement:
        """获取元素下方某个指定元素
        :param locator: 定位符，只支持str或int，且不支持xpath和css方式
        :param index: 第几个，从1开始
        :return: 获取到的元素对象
        """
        ...

    def check(self, uncheck: bool = False, by_js: bool = False) -> None:
        """选中或取消选中当前元素
        :param uncheck: 是否取消选中
        :param by_js: 是否用js执行
        :return: None
        """
        ...

    def attr(self, name: str) -> Union[str, None]:
        """返回一个attribute属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        ...

    def remove_attr(self, name: str) -> ChromiumElement:
        """删除元素一个attribute属性
        :param name: 属性名
        :return: None
        """
        ...

    def property(self, name: str) -> Union[str, int, None]:
        """获取一个property属性值
        :param name: 属性名
        :return: 属性值文本
        """
        ...

    def run_js(self, script: str, *args, as_expr: bool = False, timeout: float = None) -> Any:
        """对本元素执行javascript代码
        :param script: js文本，文本中用this表示本元素
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        ...

    def _run_js(self, script: str, *args, as_expr: bool = False, timeout: float = None) -> Any:
        """对本元素执行javascript代码
        :param script: js文本，文本中用this表示本元素
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        ...

    def run_async_js(self, script: str, *args, as_expr: bool = False) -> None:
        """以异步方式对本元素执行javascript代码
        :param script: js文本，文本中用this表示本元素
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: None
        """
        ...

    def ele(self,
            locator: Union[Tuple[str, str], str],
            index: int = 1,
            timeout: float = None) -> ChromiumElement:
        """返回当前元素下级符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本
        """
        ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> ChromiumElementsList:
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: ChromiumElement对象或属性、文本组成的列表
        """
        ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str] = None,
              index: int = 1,
              timeout: float = None) -> SessionElement:
        """查找一个符合条件的元素，以SessionElement形式返回
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: SessionElement对象或属性、文本
        """
        ...

    def s_eles(self,
               locator: Union[Tuple[str, str], str] = None,
               timeout: float = None) -> SessionElementsList:
        """查找所有符合条件的元素，以SessionElement列表形式返回
        :param locator: 定位符
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: SessionElement或属性、文本组成的列表
        """
        ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str],
                       timeout: float,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = False) -> Union[ChromiumElement, ChromiumFrame, ChromiumElementsList]:
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒）
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: MixTab用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或文本、属性或其组成的列表
        """
        ...

    def style(self, style: str, pseudo_ele: str = '') -> str:
        """返回元素样式属性值，可获取伪元素属性值
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        ...

    def src(self, timeout: float = None, base64_to_bytes: bool = True) -> Union[bytes, str, None]:
        """返回元素src资源，base64的可转为bytes返回，其它返回str
        :param timeout: 等待资源加载的超时时间（秒）
        :param base64_to_bytes: 为True时，如果是base64数据，转换为bytes格式
        :return: 资源内容
        """
        ...

    def save(self,
             path: [str, bool] = None,
             name: str = None,
             timeout: float = None,
             rename: bool = True) -> str:
        """保存图片或其它有src属性的元素的资源
        :param path: 文件保存路径，为None时保存到当前文件夹
        :param name: 文件名称，为None时从资源url获取
        :param timeout: 等待资源加载的超时时间（秒）
        :param rename: 遇到重名文件时是否自动重命名
        :return: 返回保存路径
        """
        ...

    def get_screenshot(self,
                       path: [str, Path] = None,
                       name: str = None,
                       as_bytes: PIC_TYPE = None,
                       as_base64: PIC_TYPE = None,
                       scroll_to_center: bool = True) -> Union[str, bytes]:
        """对当前元素截图，可保存到文件，或以字节方式返回
        :param path: 文件保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param scroll_to_center: 截图前是否滚动到视口中央
        :return: 图片完整路径或字节文本
        """
        ...

    def input(self, vals: Any, clear: bool = False, by_js: bool = False) -> ChromiumElement:
        """输入文本或组合键，也可用于输入文件路径到input元素（路径间用\n间隔）
        :param vals: 文本值或按键组合
        :param clear: 输入前是否清空文本框
        :param by_js: 是否用js方式输入，不能输入组合键
        :return: None
        """
        ...

    def clear(self, by_js: bool = False) -> ChromiumElement:
        """清空元素文本
        :param by_js: 是否用js方式清空，为False则用全选+del模拟输入删除
        :return: None
        """
        ...

    def _input_focus(self) -> None:
        """输入前使元素获取焦点"""
        ...

    def focus(self) -> ChromiumElement:
        """使元素获取焦点"""
        ...

    def hover(self, offset_x: int = None, offset_y: int = None) -> ChromiumElement:
        """鼠标悬停，可接受偏移量，偏移量相对于元素左上角坐标。不传入offset_x和offset_y值时悬停在元素中点
        :param offset_x: 相对元素左上角坐标的x轴偏移量
        :param offset_y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        ...

    def drag(self, offset_x: int = 0, offset_y: int = 0, duration: float = 0.5) -> ChromiumElement:
        """拖拽当前元素到相对位置
        :param offset_x: x变化值
        :param offset_y: y变化值
        :param duration: 拖动用时，传入0即瞬间到达
        :return: None
        """
        ...

    def drag_to(self,
                ele_or_loc: Union[Tuple[int, int], str, ChromiumElement],
                duration: float = 0.5) -> ChromiumElement:
        """拖拽当前元素，目标为另一个元素或坐标元组(x, y)
        :param ele_or_loc: 另一个元素或坐标元组，坐标为元素中点的坐标
        :param duration: 拖动用时，传入0即瞬间到达
        :return: None
        """
        ...

    def _get_obj_id(self, node_id: int = None, backend_id: int = None) -> str: ...

    def _get_node_id(self, obj_id: str = None, backend_id: int = None) -> int: ...

    def _get_backend_id(self, node_id: int) -> int: ...

    def _refresh_id(self) -> None:
        """根据backend id刷新其它id"""
        ...

    def _get_ele_path(self, xpath: bool = True) -> str:
        """返获取绝对的css路径或xpath路径"""
        ...

    def _set_file_input(self, files: Union[str, list, tuple]) -> None:
        """对上传控件写入路径
        :param files: 文件路径列表或字符串，字符串时多个文件用回车分隔
        :return: None
        """
        ...


class ShadowRoot(BaseElement):
    owner: ChromiumBase = ...
    tab: Union[ChromiumPage, ChromiumTab] = ...
    _obj_id: str = ...
    _node_id: int = ...
    _backend_id: int = ...
    parent_ele: ChromiumElement = ...
    _states: Optional[ShadowRootStates] = ...

    def __init__(self, parent_ele: ChromiumElement, obj_id: str = None, backend_id: int = None):
        """
        :param parent_ele: shadow root 所在父元素
        :param obj_id: js中的object id
        :param backend_id: cdp中的backend id
        """
        ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str],
                 index: int = 1,
                 timeout: float = None) -> ChromiumElement:
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 超时时间（秒）
        :return: 元素对象或属性、文本
        """
        ...

    def __repr__(self) -> str: ...

    def __eq__(self, other: ShadowRoot) -> bool: ...

    @property
    def tag(self) -> str:
        """返回元素标签名"""
        ...

    @property
    def html(self) -> str:
        """返回outerHTML文本"""
        ...

    @property
    def inner_html(self) -> str:
        """返回内部的html文本"""
        ...

    @property
    def states(self) -> ShadowRootStates:
        """返回用于获取元素状态的对象"""
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

    def run_async_js(self,
                     script: str,
                     *args,
                     as_expr: bool = False,
                     timeout: float = None) -> None:
        """以异步方式执行js代码
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: None
        """
        ...

    def parent(self,
               level_or_loc: Union[str, int] = 1,
               index: int = 1,
               timeout: float = 0) -> ChromiumElement:
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果
        :param timeout: 查找超时时间（秒）
        :return: ChromiumElement对象
        """
        ...

    def child(self,
              locator: Union[Tuple[str, str], str] = '',
              index: int = 1, timeout: float = None) -> ChromiumElement:
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找超时时间（秒）
        :return: 直接子元素或节点文本组成的列表
        """
        ...

    def next(self,
             locator: Union[Tuple[str, str], str] = '',
             index: int = 1, timeout: float = None) -> ChromiumElement:
        """返回当前元素后面一个符合条件的同级元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找超时时间（秒）
        :return: ChromiumElement对象
        """
        ...

    def before(self,
               locator: Union[Tuple[str, str], str] = '',
               index: int = 1, timeout: float = None) -> ChromiumElement:
        """返回文档中当前元素前面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找超时时间（秒）
        :return: 本元素前面的某个元素或节点
        """
        ...

    def after(self,
              locator: Union[Tuple[str, str], str] = '',
              index: int = 1, timeout: float = None) -> ChromiumElement:
        """返回文档中此当前元素后面符合条件的一个元素，可用查询语法筛选，可指定返回筛选结果的第几个
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找超时时间（秒）
        :return: 本元素后面的某个元素或节点
        """
        ...

    def children(self, locator: Union[Tuple[str, str], str] = '', timeout: float = None) -> List[ChromiumElement]:
        """返回当前元素符合条件的直接子元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找超时时间（秒）
        :return: 直接子元素或节点文本组成的列表
        """
        ...

    def nexts(self, locator: Union[Tuple[str, str], str] = '', timeout: float = None) -> List[ChromiumElement]:
        """返回当前元素后面符合条件的同级元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找超时时间（秒）
        :return: ChromiumElement对象组成的列表
        """
        ...

    def befores(self, locator: Union[Tuple[str, str], str] = '', timeout: float = None) -> List[ChromiumElement]:
        """返回文档中当前元素前面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找超时时间（秒）
        :return: 本元素前面的元素或节点组成的列表
        """
        ...

    def afters(self, locator: Union[Tuple[str, str], str] = '', timeout: float = None) -> List[ChromiumElement]:
        """返回文档中当前元素后面符合条件的元素或节点组成的列表，可用查询语法筛选
        查找范围不限同级元素，而是整个DOM文档
        :param locator: 用于筛选的查询语法
        :param timeout: 查找超时时间（秒）
        :return: 本元素后面的元素或节点组成的列表
        """
        ...

    def ele(self,
            locator: Union[Tuple[str, str], str],
            index: int = 1,
            timeout: float = None) -> ChromiumElement:
        """返回当前元素下级符合条件的一个元素
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: ChromiumElement对象
        """
        ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> ChromiumElementsList:
        """返回当前元素下级所有符合条件的子元素
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: ChromiumElement对象组成的列表
        """
        ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str] = None,
              index: int = 1,
              timeout: float = None) -> SessionElement:
        """查找一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: SessionElement对象或属性、文本
        """
        ...

    def s_eles(self, locator: Union[Tuple[str, str], str], timeout: float = None) -> SessionElementsList:
        """查找所有符合条件的元素以SessionElement列表形式返回，处理复杂页面时效率很高
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与元素所在页面等待时间一致
        :return: SessionElement对象
        """
        ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str],
                       timeout: float,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = None) -> Union[ChromiumElement, ChromiumFrame, str, ChromiumElementsList]:
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒）
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: MixTab用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或其组成的列表
        """
        ...

    def _get_node_id(self, obj_id: str) -> int: ...

    def _get_obj_id(self, back_id: int) -> str: ...

    def _get_backend_id(self, node_id: int) -> int: ...


def find_in_chromium_ele(ele: ChromiumElement,
                         locator: Union[str, Tuple[str, str]],
                         index: Optional[int] = 1,
                         timeout: float = None,
                         relative: bool = True) -> Union[ChromiumElement, List[ChromiumElement]]:
    """在chromium元素中查找
    :param ele: ChromiumElement对象
    :param locator: 元素定位元组
    :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
    :param timeout: 查找元素超时时间（秒）
    :param relative: MixTab用于标记是否相对定位使用
    :return: 返回ChromiumElement元素或它们组成的列表
    """
    ...


def find_by_xpath(ele: ChromiumElement,
                  xpath: str,
                  index: Optional[int],
                  timeout: float,
                  relative: bool = True) -> Union[ChromiumElement, List[ChromiumElement]]:
    """执行用xpath在元素中查找元素
    :param ele: 在此元素中查找
    :param xpath: 查找语句
    :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
    :param timeout: 超时时间（秒）
    :param relative: 是否相对定位
    :return: ChromiumElement或其组成的列表
    """
    ...


def find_by_css(ele: ChromiumElement,
                selector: str,
                index: Optional[int],
                timeout: float) -> Union[ChromiumElement, List[ChromiumElement],]:
    """执行用css selector在元素中查找元素
    :param ele: 在此元素中查找
    :param selector: 查找语句
    :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
    :param timeout: 超时时间（秒）
    :return: ChromiumElement或其组成的列表
    """
    ...


def make_chromium_eles(page: Union[ChromiumBase, ChromiumPage, WebPage, ChromiumTab, ChromiumFrame],
                       _ids: Union[tuple, list, str, int],
                       index: Optional[int] = 1,
                       is_obj_id: bool = True,
                       ele_only: bool = False
                       ) -> Union[ChromiumElement, ChromiumFrame, ChromiumElementsList]:
    """根据node id或object id生成相应元素对象
    :param page: ChromiumPage对象
    :param _ids: 元素的id列表
    :param index: 获取第几个，为None返回全部
    :param is_obj_id: 传入的id是obj id还是node id
    :param ele_only: 是否只返回ele，在页面查找元素时生效
    :return: 浏览器元素对象或它们组成的列表，生成失败返回False
    """
    ...


def make_js_for_find_ele_by_xpath(xpath: str, type_txt: str, node_txt: str) -> str:
    """生成用xpath在元素中查找元素的js文本
    :param xpath: xpath文本
    :param type_txt: 查找类型
    :param node_txt: 节点类型
    :return: js文本
    """
    ...


def run_js(page_or_ele: Union[ChromiumBase, ChromiumElement, ShadowRoot],
           script: str,
           as_expr: bool,
           timeout: float,
           args: tuple = ...) -> Any:
    """运行javascript代码
    :param page_or_ele: 页面对象或元素对象
    :param script: js文本
    :param as_expr: 是否作为表达式运行，为True时args无效
    :param timeout: 超时时间（秒）
    :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
    :return: js执行结果
    """
    ...


def parse_js_result(page: ChromiumBase,
                    ele: ChromiumElement,
                    result: dict,
                    end_time: float):
    """解析js返回的结果"""
    ...


def convert_argument(arg: Any) -> dict:
    """把参数转换成js能够接收的形式"""
    ...


class Pseudo(object):
    _ele: ChromiumElement = ...

    def __init__(self, ele: ChromiumElement):
        """
        :param ele: ChromiumElement
        """
        ...

    @property
    def before(self) -> str:
        """返回当前元素的::before伪元素文本内容"""
        ...

    @property
    def after(self) -> str:
        """返回当前元素的::after伪元素文本内容"""
        ...
