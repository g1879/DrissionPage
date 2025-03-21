# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from abc import abstractmethod
from typing import Union, Tuple, List, Any, Optional, Dict

from DownloadKit import DownloadKit
from requests import Session
from requests.structures import CaseInsensitiveDict

from .._configs.session_options import SessionOptions
from .._elements.chromium_element import ChromiumElement
from .._elements.none_element import NoneElement
from .._elements.session_element import SessionElement
from .._functions.elements import SessionElementsList
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._pages.session_page import SessionPage
from .._pages.web_page import WebPage


class BaseParser(object):
    """所有页面、元素类的基类"""
    _type: str
    timeout: float

    def __call__(self, locator: Union[Tuple[str, str], str], index: int = 1): ...

    def ele(self,
            locator: Union[Tuple[str, str], str, BaseElement],
            index: int = 1,
            timeout: float = None): ...

    def eles(self, locator: Union[Tuple[str, str], str], timeout=None): ...

    def find(self,
             locators: Union[str, List[str], tuple],
             any_one: bool = True,
             first_ele: bool = True,
             timeout: float = None) -> Union[Dict[str, ChromiumElement], Dict[str, SessionElement],
    Dict[str, List[ChromiumElement]], Dict[str, List[SessionElement]], Tuple[str, SessionElement],
    Tuple[str, ChromiumElement]]:
        """传入多个定位符，获取多个ele
        :param locators: 定位符组成的列表
        :param any_one: 是否任何一个定位符找到结果即返回
        :param first_ele: 每个定位符是否只获取第一个元素
        :param timeout: 超时时间（秒）
        :return: any_one为True时，返回一个找到的元素定位符和对象组成的元组，格式：(loc, ele)，全都没找到返回(None, None)
                 any_one为False时，返回dict格式，key为定位符，value为找到的元素或列表
        """
        ...

    # ----------------以下属性或方法待后代实现----------------
    @property
    def html(self) -> str: ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str, BaseElement, None] = None,
              index: int = 1) -> SessionElement: ...

    def s_eles(self, locator: Union[Tuple[str, str], str]) -> SessionElementsList: ...

    def _ele(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None,
             index: Optional[int] = 1,
             raise_err: bool = None,
             method: str = None): ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str],
                       timeout: float,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = None): ...


class BaseElement(BaseParser):
    """各元素类的基类"""
    owner: BasePage = ...

    def __init__(self, owner: BasePage = None): ...

    @property
    def timeout(self) -> float:
        """返回其查找元素时超时时间"""
        ...

    @property
    def child_count(self) -> int:
        """返回直接子元素的个数"""
        ...

    # ----------------以下属性或方法由后代实现----------------
    @property
    def tag(self) -> str: ...

    def parent(self, level_or_loc: Union[tuple, str, int] = 1): ...

    def prev(self, index: int = 1) -> None: ...

    def prevs(self) -> None: ...

    def next(self, index: int = 1): ...

    def nexts(self): ...

    def get_frame(self, loc_or_ind, timeout=None) -> ChromiumFrame:
        """获取元素中一个frame对象
        :param loc_or_ind: 定位符、iframe序号，序号从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒）
        :return: ChromiumFrame对象
        """
        ...

    def _ele(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None,
             index: Optional[int] = 1,
             relative: bool = False,
             raise_err: bool = None,
             method: str = None):
        """调用获取元素的方法
        :param locator: 定位符
        :param timeout: 超时时间（秒）
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param relative: 是否相对定位
        :param raise_err: 找不到时是否抛出异常
        :param method: 调用的方法名
        :return: 元素对象或它们组成的列表
        """
        ...


class DrissionElement(BaseElement):
    """ChromiumElement 和 SessionElement的基类，但不是ShadowRoot的基类"""

    def __init__(self, owner: BasePage = None): ...

    @property
    def link(self) -> str:
        """返回href或src绝对url"""
        ...

    @property
    def css_path(self) -> str:
        """返回css path路径"""
        ...

    @property
    def xpath(self) -> str:
        """返回xpath路径"""
        ...

    @property
    def comments(self) -> list:
        """返回元素注释文本组成的列表"""
        ...

    def texts(self, text_node_only: bool = False) -> list:
        """返回元素内所有直接子节点的文本，包括元素和文本节点
        :param text_node_only: 是否只返回文本节点
        :return: 文本列表
        """
        ...

    def parent(self,
               level_or_loc: Union[tuple, str, int] = 1,
               index: int = 1,
               timeout: float = None) -> Union[DrissionElement, None]:
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，1开始，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果，1开始
        :param timeout: 时间（秒）
        :return: 上级元素对象
        """
        ...

    def child(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[DrissionElement, str, NoneElement]:
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        ...

    def prev(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[DrissionElement, str, NoneElement]:
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素
        """
        ...

    def next(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[DrissionElement, str, NoneElement]:
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素
        """
        ...

    def before(self,
               locator: Union[Tuple[str, str], str, int] = '',
               index: int = 1,
               timeout: float = None,
               ele_only: bool = True) -> Union[DrissionElement, str, NoneElement]:
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
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
              ele_only: bool = True) -> Union[DrissionElement, str, NoneElement]:
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        ...

    def children(self,
                 locator: Union[Tuple[str, str], str] = '',
                 timeout: float = None,
                 ele_only: bool = True) -> List[Union[DrissionElement, str]]:
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        ...

    def prevs(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> List[Union[DrissionElement, str]]:
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        ...

    def nexts(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> List[Union[DrissionElement, str]]:
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        ...

    def befores(self,
                locator: Union[Tuple[str, str], str] = '',
                timeout: float = None,
                ele_only: bool = True) -> List[Union[DrissionElement, str]]:
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        ...

    def afters(self,
               locator: Union[Tuple[str, str], str] = '',
               timeout: float = None,
               ele_only: bool = True) -> List[Union[DrissionElement, str]]:
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        ...

    def _get_relative(self,
                      func: str,
                      direction: str,
                      brother: bool,
                      locator: Union[Tuple[str, str], str] = '',
                      index: int = 1,
                      timeout: float = None,
                      ele_only: bool = True) -> DrissionElement:
        """获取一个亲戚元素或节点，可用查询语法筛选，可指定返回筛选结果的第几个
        :param func: 方法名称
        :param direction: 方向，'following' 或 'preceding'
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        ...

    def _get_relatives(self,
                       index: int = None,
                       locator: Union[Tuple[str, str], str] = '',
                       direction: str = 'following',
                       brother: bool = True,
                       timeout: float = 0.5,
                       ele_only: bool = True) -> List[Union[DrissionElement, str]]:
        """按要求返回兄弟元素或节点组成的列表
        :param index: 获取第几个，该参数不为None时只获取该编号的元素
        :param locator: 用于筛选的查询语法
        :param direction: 'following' 或 'preceding'，查找的方向
        :param brother: 查找范围，在同级查找还是整个dom前后查找
        :param timeout: 查找等待时间（秒）
        :return: 元素对象或字符串
        """
        ...

    # ----------------以下属性或方法由后代实现----------------
    @property
    def attrs(self) -> dict: ...

    @property
    def text(self) -> str: ...

    @property
    def raw_text(self) -> str: ...

    @abstractmethod
    def attr(self, name: str) -> str: ...

    def _get_ele_path(self, xpath: bool = True) -> str: ...


class BasePage(BaseParser):
    """页面类的基类"""

    _url_available: Optional[bool] = ...
    retry_times: int = ...
    retry_interval: float = ...
    _download_path: Optional[str] = ...
    _DownloadKit: Optional[DownloadKit] = ...
    _none_ele_return_value: bool = ...
    _none_ele_value: Any = ...
    _page: Union[ChromiumPage, SessionPage, WebPage] = ...
    _session: Optional[Session] = ...
    _headers: Optional[CaseInsensitiveDict] = ...
    _session_options: Optional[SessionOptions] = ...

    def __init__(self): ...

    @property
    def title(self) -> Union[str, None]:
        """返回网页title"""
        ...

    @property
    def url_available(self) -> bool:
        """返回当前访问的url有效性"""
        ...

    @property
    def download_path(self) -> str:
        """返回默认下载路径"""
        ...

    @property
    def download(self) -> DownloadKit:
        """返回下载器对象"""
        ...

    def _before_connect(self, url: str, retry: int, interval: float) -> tuple:
        """连接前的准备
        :param url: 要访问的url
        :param retry: 重试次数
        :param interval: 重试间隔
        :return: 重试次数、间隔、是否文件组成的tuple
        """
        ...

    def _set_session_options(self, session_or_options: Union[Session, SessionOptions] = None) -> None:
        """启动配置
        :param session_or_options: Session、SessionOptions对象
        :return: None
        """
        ...

    def _create_session(self) -> None:
        """创建内建Session对象"""
        ...

    # ----------------以下属性或方法由后代实现----------------
    @property
    def url(self) -> str: ...

    @property
    def json(self) -> dict: ...

    @property
    def user_agent(self) -> str: ...

    @abstractmethod
    def get(self, url: str, show_errmsg: bool = False, retry: int = None, interval: float = None): ...

    def _ele(self,
             locator,
             timeout: float = None,
             index: Optional[int] = 1,
             raise_err: bool = None,
             method: str = None):
        """调用获取元素的方法
        :param locator: 定位符
        :param timeout: 超时时间（秒）
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param raise_err: 找不到时是否抛出异常
        :param method: 调用的方法名
        :return: 元素对象或它们组成的列表
        """
        ...
