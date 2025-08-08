# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from typing import Union, Tuple, Any, Optional, Literal

from requests import Session

from .chromium_page import ChromiumPage
from .chromium_tab import ChromiumTab
from .mix_tab import MixTab
from .web_page import WebPage
from .._base.base import BasePage
from .._base.chromium import Chromium
from .._base.driver import Driver
from .._elements.chromium_element import ChromiumElement
from .._elements.session_element import SessionElement
from .._functions.cookies import CookiesList
from .._functions.elements import SessionElementsList, ChromiumElementsList
from .._pages.chromium_frame import ChromiumFrame
from .._units.actions import Actions
from .._units.console import Console
from .._units.listener import Listener
from .._units.rect import TabRect, FrameRect
from .._units.screencast import Screencast
from .._units.scroller import Scroller, PageScroller
from .._units.setter import ChromiumBaseSetter
from .._units.states import PageStates
from .._units.waiter import BaseWaiter

PIC_TYPE = Literal['jpg', 'jpeg', 'png', 'webp', True]


class ChromiumBase(BasePage):
    """标签页、Frame、Page基类"""
    _tab: Union[ChromiumTab, MixTab, ChromiumFrame, ChromiumPage, WebPage] = ...
    _browser: Chromium = ...
    _driver: Optional[Driver] = ...
    _frame_id: str = ...
    _is_reading: bool = ...
    _is_timeout: bool = ...
    _timeouts: Timeout = ...
    _first_run: bool = ...
    _is_loading: Optional[bool] = ...
    _load_mode: str = ...
    _scroll: Optional[Scroller] = ...
    _url: str = ...
    _root_id: Optional[str] = ...
    _upload_list: Optional[list] = ...
    _wait: Optional[BaseWaiter] = ...
    _set: Optional[ChromiumBaseSetter] = ...
    _screencast: Optional[Screencast] = ...
    _actions: Optional[Actions] = ...
    _listener: Optional[Listener] = ...
    _states: Optional[PageStates] = ...
    _alert: Alert = ...
    _has_alert: bool = ...
    _auto_handle_alert: Optional[bool] = ...
    _doc_got: bool = ...
    _load_end_time: float = ...
    _init_jss: list = ...
    _ready_state: Optional[str] = ...
    _rect: Optional[TabRect] = ...
    _console: Optional[Console] = ...
    _disconnect_flag: bool = ...
    _type: str = ...

    def __init__(self,
                 browser: Chromium,
                 tab_id: str = None):
        """
        :param browser: Chromium
        :param tab_id: 要控制的tab id，不指定默认为激活的标签页
        """
        ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str, ChromiumElement],
                 index: int = 1,
                 timeout: float = None) -> ChromiumElement:
        """在内部查找元素
        例：ele = page('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 超时时间（秒）
        :return: ChromiumElement对象
        """
        ...

    def _d_set_runtime_settings(self) -> None: ...

    def _connect_browser(self, target_id: str = None) -> None:
        """连接浏览器，在第一次时运行
        :param target_id: 要控制的target id，不指定默认为激活的标签页
        :return: None
        """
        ...

    def _driver_init(self, target_id: str) -> None:
        """新建页面、页面刷新后要进行的cdp参数初始化
        :param target_id: 要跳转到的target id
        :return: None
        """
        ...

    def _get_document(self, timeout: float = 10) -> bool:
        """获取页面文档
        :param timeout: 超时时间（秒）
        :return: 是否获取成功
        """
        ...

    def _onFrameDetached(self, **kwargs) -> None: ...

    def _onFrameAttached(self, **kwargs) -> None: ...

    def _onFrameStartedLoading(self, **kwargs):
        """页面开始加载时执行"""
        ...

    def _onFrameNavigated(self, **kwargs):
        """页面跳转时执行"""
        ...

    def _onDomContentEventFired(self, **kwargs):
        """在页面刷新、变化后重新读取页面内容"""
        ...

    def _onLoadEventFired(self, **kwargs):
        """在页面刷新、变化后重新读取页面内容"""
        ...

    def _onFrameStoppedLoading(self, **kwargs):
        """页面加载完成后执行"""
        ...

    def _onFileChooserOpened(self, **kwargs):
        """文件选择框打开时执行"""
        ...

    def _wait_to_stop(self):
        """eager策略超时时使页面停止加载"""
        ...

    @property
    def wait(self) -> BaseWaiter:
        """返回用于等待的对象"""
        ...

    @property
    def set(self) -> ChromiumBaseSetter:
        """返回用于设置的对象"""
        ...

    @property
    def screencast(self) -> Screencast:
        """返回用于录屏的对象"""
        ...

    @property
    def actions(self) -> Actions:
        """返回用于执行动作链的对象"""
        ...

    @property
    def listen(self) -> Listener:
        """返回用于聆听数据包的对象"""
        ...

    @property
    def states(self) -> PageStates:
        """返回用于获取状态信息的对象"""
        ...

    @property
    def scroll(self) -> PageScroller:
        """返回用于滚动滚动条的对象"""
        ...

    @property
    def rect(self) -> Union[TabRect, FrameRect]:
        """返回获取窗口坐标和大小的对象"""
        ...

    @property
    def console(self) -> Console:
        """返回获取控制台信息的对象"""
        ...

    @property
    def timeout(self) -> float:
        """返回timeout设置"""
        ...

    @property
    def timeouts(self) -> Timeout:
        """返回timeouts设置"""
        ...

    @property
    def browser(self) -> Chromium:
        """返回浏览器对象"""
        ...

    @property
    def driver(self) -> Driver:
        """返回用于控制浏览器的Driver对象"""
        ...

    @property
    def title(self) -> str:
        """返回当前页面title"""
        ...

    @property
    def url(self) -> str:
        """返回当前页面url"""
        ...

    @property
    def _browser_url(self) -> str:
        """用于被MixTab覆盖"""
        ...

    @property
    def html(self) -> str:
        """返回当前页面html文本"""
        ...

    @property
    def json(self) -> Union[dict, None]:
        """当返回内容是json格式时，返回对应的字典，非json格式时返回None"""
        ...

    @property
    def tab_id(self) -> str:
        """返回当前标签页id"""
        ...

    @property
    def _target_id(self) -> str:
        """返回当前标签页id"""
        ...

    @property
    def active_ele(self) -> ChromiumElement:
        """返回当前焦点所在元素"""
        ...

    @property
    def load_mode(self) -> Literal['none', 'normal', 'eager']:
        """返回页面加载策略，有3种：'none'、'normal'、'eager'"""
        ...

    @property
    def user_agent(self) -> str:
        """返回user agent"""
        ...

    @property
    def upload_list(self) -> list:
        """返回等待上传文件列表"""
        ...

    @property
    def session(self) -> Session:
        """返回用于转换模式或download的Session对象"""
        ...

    @property
    def _js_ready_state(self) -> str:
        """返回js获取的ready state信息"""
        ...

    def run_cdp(self, cmd: str, **cmd_args) -> dict:
        """执行Chrome DevTools Protocol语句
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        ...

    def run_cdp_loaded(self, cmd: str, **cmd_args) -> dict:
        """执行Chrome DevTools Protocol语句，执行前等待页面加载完毕
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        ...

    def _run_cdp(self, cmd: str, **cmd_args) -> dict:
        """执行Chrome DevTools Protocol语句
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        ...

    def _run_cdp_loaded(self, cmd: str, **cmd_args) -> dict:
        """执行Chrome DevTools Protocol语句，执行前等待页面加载完毕
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        ...

    def run_js(self, script: Union[str, Path], *args, as_expr: bool = False, timeout: float = None) -> Any:
        """运行javascript代码
        :param script: js文本或js文件路径
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        ...

    def run_js_loaded(self, script: Union[str, Path], *args, as_expr: bool = False, timeout: float = None) -> Any:
        """运行javascript代码，执行前等待页面加载完毕
        :param script: js文本或js文件路径
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script属性值
        :return: 运行的结果
        """
        ...

    def _run_js(self, script: Union[str, Path], *args, as_expr: bool = False, timeout: float = None) -> Any:
        """运行javascript代码
        :param script: js文本或js文件路径
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script设置
        :return: 运行的结果
        """
        ...

    def _run_js_loaded(self, script: Union[str, Path], *args, as_expr: bool = False, timeout: float = None) -> Any:
        """运行javascript代码，执行前等待页面加载完毕
        :param script: js文本或js文件路径
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :param timeout: js超时时间（秒），为None则使用页面timeouts.script属性值
        :return: 运行的结果
        """
        ...

    def run_async_js(self, script: Union[str, Path], *args, as_expr: bool = False) -> None:
        """以异步方式执行js代码或js文件路径
        :param script: js文本
        :param args: 参数，按顺序在js文本中对应arguments[0]、arguments[1]...
        :param as_expr: 是否作为表达式运行，为True时args无效
        :return: None
        """
        ...

    def get(self, url: str, show_errmsg: bool = False, retry: int = None,
            interval: float = None, timeout: float = None) -> Union[None, bool]:
        """访问url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param timeout: 连接超时时间（秒），为None时使用页面对象timeouts.page_load属性值
        :return: 目标url是否可用
        """
        ...

    def cookies(self, all_domains: bool = False, all_info: bool = False) -> CookiesList:
        """返回cookies信息
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，为False时只返回name、value、domain
        :return: cookies信息
        """
        ...

    def ele(self,
            locator: Union[Tuple[str, str], str, ChromiumElement, ChromiumFrame],
            index: int = 1,
            timeout: float = None) -> ChromiumElement:
        """获取一个符合条件的元素对象
        :param locator: 定位符或元素对象
        :param index: 获取第几个元素，从1开始，可传入负数获取倒数第几个
        :param timeout: 查找超时时间（秒），默认与页面等待时间一致
        :return: ChromiumElement对象
        """
        ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> ChromiumElementsList:
        """获取所有符合条件的元素对象
        :param locator: 定位符或元素对象
        :param timeout: 查找超时时间（秒），默认与页面等待时间一致
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
        :param timeout: 查找元素超时时间（秒），默认与页面等待时间一致
        :return: SessionElement对象或属性、文本
        """
        ...

    def s_eles(self,
               locator: Union[Tuple[str, str], str],
               timeout: float = None) -> SessionElementsList:
        """查找所有符合条件的元素以SessionElement列表形式返回
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间（秒），默认与页面等待时间一致
        :return: SessionElement对象组成的列表
        """
        ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str, ChromiumElement, ChromiumFrame],
                       timeout: float,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = None) -> Union[ChromiumElement, ChromiumFrame, ChromiumElementsList]:
        """执行元素查找
        :param locator: 定位符或元素对象
        :param timeout: 查找超时时间（秒）
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param relative: MixTab用的表示是否相对定位的参数
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: ChromiumElement对象或元素对象组成的列表
        """
        ...

    def refresh(self, ignore_cache: bool = False) -> None:
        """刷新当前页面
        :param ignore_cache: 是否忽略缓存
        :return: None
        """
        ...

    def forward(self, steps: int = 1) -> None:
        """在浏览历史中前进若干步
        :param steps: 前进步数
        :return: None
        """
        ...

    def back(self, steps: int = 1) -> None:
        """在浏览历史中后退若干步
        :param steps: 后退步数
        :return: None
        """
        ...

    def _forward_or_back(self, steps: int) -> None:
        """执行浏览器前进或后退，会跳过url相同的历史记录
        :param steps: 步数
        :return: None
        """
        ...

    def stop_loading(self) -> None:
        """页面停止加载"""
        ...

    def remove_ele(self, loc_or_ele: Union[ChromiumElement, ChromiumFrame, str, Tuple[str, str]]) -> None:
        """从页面上删除一个元素
        :param loc_or_ele: 元素对象或定位符
        :return: None
        """
        ...

    def add_ele(self,
                html_or_info: Union[str, Tuple[str, dict]],
                insert_to: Union[ChromiumElement, str, Tuple[str, str], None] = None,
                before: Union[ChromiumElement, str, Tuple[str, str], None] = None) -> Union[
        ChromiumElement, ChromiumFrame]:
        """新建一个元素
        :param html_or_info: 新元素的html文本或信息。信息格式为：(tag, {attr1: value, ...})
        :param insert_to: 插入到哪个元素中，可接收元素对象和定位符，为None且为html添加到body，不为html不插入
        :param before: 在哪个子节点前面插入，可接收对象和定位符，为None插入到父元素末尾
        :return: 元素对象
        """
        ...

    def get_frame(self,
                  loc_ind_ele: Union[str, int, tuple, ChromiumFrame, ChromiumElement],
                  timeout: float = None) -> ChromiumFrame:
        """获取页面中一个frame对象
        :param loc_ind_ele: 定位符、iframe序号、ChromiumFrame对象，序号从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒）
        :return: ChromiumFrame对象
        """
        ...

    def get_frames(self,
                   locator: Union[str, tuple] = None,
                   timeout: float = None) -> ChromiumElementsList:
        """获取所有符合条件的frame对象
        :param locator: 定位符，为None时返回所有
        :param timeout: 查找超时时间（秒）
        :return: ChromiumFrame对象组成的列表
        """
        ...

    def session_storage(self, item: str = None) -> Union[str, dict, None]:
        """返回sessionStorage信息，不设置item则获取全部
        :param item: 要获取的项，不设置则返回全部
        :return: sessionStorage一个或所有项内容
        """
        ...

    def local_storage(self, item: str = None) -> Union[str, dict, None]:
        """返回localStorage信息，不设置item则获取全部
        :param item: 要获取的项目，不设置则返回全部
        :return: localStorage一个或所有项内容
        """
        ...

    def get_screenshot(self, path: [str, Path] = None, name: str = None, as_bytes: PIC_TYPE = None,
                       as_base64: PIC_TYPE = None, full_page: bool = False, left_top: Tuple[int, int] = None,
                       right_bottom: Tuple[int, int] = None) -> Union[str, bytes]:
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :return: 图片完整路径或字节文本
        """
        ...

    def add_init_js(self, script: str) -> str:
        """添加初始化脚本，在页面加载任何脚本前执行
        :param script: js文本
        :return: 添加的脚本的id
        """
        ...

    def remove_init_js(self, script_id: str = None) -> None:
        """删除初始化脚本，js_id传入None时删除所有
        :param script_id: 脚本的id
        :return: None
        """
        ...

    def clear_cache(self, session_storage: bool = True, local_storage: bool = True, cache: bool = True,
                    cookies: bool = True) -> None:
        """清除缓存，可选要清除的项
        :param session_storage: 是否清除sessionStorage
        :param local_storage: 是否清除localStorage
        :param cache: 是否清除cache
        :param cookies: 是否清除cookies
        :return: None
        """
        ...

    def disconnect(self) -> None:
        """断开与页面的连接，不关闭页面"""
        ...

    def reconnect(self, wait: float = 0) -> None:
        """断开与页面原来的页面，重新建立连接
        :param wait: 断开后等待若干秒再连接
        :return: None
        """
        ...

    def handle_alert(self,
                     accept: Optional[bool] = True,
                     send: str = None,
                     timeout: float = None,
                     next_one: bool = False) -> Union[str, False]:
        """处理提示框，可以自动等待提示框出现
        :param accept: True表示确认，False表示取消，为None不会按按钮但依然返回文本值
        :param send: 处理prompt提示框时可输入文本
        :param timeout: 等待提示框出现的超时时间（秒），为None则使用self.timeout属性的值
        :param next_one: 是否处理下一个出现的提示框，为True时timeout参数无效
        :return: 提示框内容文本，未等到提示框则返回False
        """
        ...

    def _handle_alert(self,
                      accept: Optional[bool] = True,
                      send: str = None,
                      timeout: float = None,
                      next_one: bool = False) -> Union[str, False]:
        """处理提示框，可以自动等待提示框出现
        :param accept: True表示确认，False表示取消，其它值不会按按钮但依然返回文本值
        :param send: 处理prompt提示框时可输入文本
        :param timeout: 等待提示框出现的超时时间（秒），为None则使用self.timeout属性的值
        :param next_one: 是否处理下一个出现的提示框，为True时timeout参数无效
        :return: 提示框内容文本，未等到提示框则返回False
        """
        ...

    def _on_alert_open(self, **kwargs):
        """alert出现时触发的方法"""
        ...

    def _on_alert_close(self, **kwargs):
        """alert关闭时触发的方法"""
        ...

    def _wait_loaded(self, timeout: float = None) -> bool:
        """等待页面加载完成，超时触发停止加载
        :param timeout: 超时时间（秒）
        :return: 是否成功，超时返回False
        """
        ...

    def _d_connect(self, to_url: str, times: int = 0, interval: float = 1, show_errmsg: bool = False,
                   timeout: float = None) -> Union[bool, None]:
        """尝试连接，重试若干次
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :param timeout: 连接超时时间（秒）
        :return: 是否成功，返回None表示不确定
        """
        ...

    def _get_screenshot(self, path: [str, Path] = None, name: str = None, as_bytes: PIC_TYPE = None,
                        as_base64: PIC_TYPE = None, full_page: bool = False, left_top: Tuple[float, float] = None,
                        right_bottom: Tuple[float, float] = None, ele: ChromiumElement = None) -> Union[str, bytes]:
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 保存路径
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


class Timeout(object):
    """用于保存d模式timeout信息的类"""
    base: float = ...
    page_load: float = ...
    script: float = ...

    def __init__(self, base=None, page_load=None, script=None):
        """
        :param base: 默认超时时间
        :param page_load: 页面加载超时时间
        :param script: js超时时间
        """
        ...

    @property
    def as_dict(self) -> dict:
        """以dict格式返回timeout设置"""
        ...


class Alert(object):
    """用于保存alert信息的类"""
    activated: Optional[bool] = ...
    text: Optional[str] = ...
    type: Optional[str] = ...
    defaultPrompt: Optional[str] = ...
    response_accept: Optional[str] = ...
    response_text: Optional[str] = ...
    handle_next: Optional[bool] = ...
    next_text: Optional[str] = ...
    auto: Optional[bool] = ...

    def __init__(self, auto: bool = None): ...
