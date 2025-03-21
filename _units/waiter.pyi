# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union, Tuple, Any

from .downloader import DownloadMission
from .._base.chromium import Chromium
from .._elements.chromium_element import ChromiumElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._pages.chromium_tab import ChromiumTab
from .._pages.mix_tab import MixTab
from .._pages.web_page import WebPage


class OriginWaiter(object):
    _owner: Any = ...

    def __init__(self, owner: Any): ...

    def __call__(self, second: float, scope: float = None):
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: 调用等待的对象
        """
        ...


class BrowserWaiter(OriginWaiter):
    _owner: Chromium = ...

    def __init__(self, owner: Chromium):
        """
        :param owner: Chromium对象
        """
        ...

    def __call__(self, second: float, scope: float = None) -> Chromium:
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: Chromium对象
        """
        ...

    def new_tab(self,
                timeout: float = None,
                curr_tab: Union[str, ChromiumTab, MixTab] = None,
                raise_err: bool = None) -> Union[str, bool]:
        """等待新标签页出现
        :param timeout: 超时时间（秒），为None则使用对象timeout属性
        :param curr_tab: 指定当前最新的tab对象或tab id，用于判断新tab出现，为None自动获取
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等到新标签页返回其id，否则返回False
        """
        ...

    def download_begin(self, timeout: float = None, cancel_it: bool = False) -> Union[DownloadMission, False]:
        """等待浏览器下载开始，可将其拦截
        :param timeout: 超时时间（秒），None使用页面对象超时时间
        :param cancel_it: 是否取消该任务
        :return: 成功返回任务对象，失败返回False
        """
        ...

    def downloads_done(self, timeout: float = None, cancel_if_timeout: bool = True) -> bool:
        """等待所有浏览器下载任务结束
        :param timeout: 超时时间（秒），为None时无限等待
        :param cancel_if_timeout: 超时时是否取消剩余任务
        :return: 是否等待成功
        """
        ...


class BaseWaiter(OriginWaiter):
    _owner: ChromiumBase = ...

    def ele_deleted(self,
                    loc_or_ele: Union[str, tuple, ChromiumElement],
                    timeout: float = None,
                    raise_err: bool = None) -> bool:
        """等待元素从DOM中删除
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间（秒），默认读取页面超时时间
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ...

    def ele_displayed(self,
                      loc_or_ele: Union[str, tuple, ChromiumElement],
                      timeout: float = None,
                      raise_err: bool = None) -> bool:
        """等待元素变成显示状态
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间（秒），默认读取页面超时时间
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ...

    def ele_hidden(self,
                   loc_or_ele: Union[str, tuple, ChromiumElement],
                   timeout: float = None,
                   raise_err: bool = None) -> bool:
        """等待元素变成隐藏状态
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间（秒），默认读取页面超时时间
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ...

    def eles_loaded(self,
                    locators: Union[Tuple[str, str], str, list, tuple],
                    timeout: float = None,
                    any_one: bool = False,
                    raise_err: bool = None) -> bool:
        """等待元素加载到DOM，可等待全部或任意一个
        :param locators: 要等待的元素，输入定位符，用list输入多个
        :param timeout: 超时时间（秒），默认读取页面超时时间
        :param any_one: 是否等待到一个就返回
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回True，失败返回False
        """
        ...

    def load_start(self, timeout: float = None, raise_err: bool = None) -> bool:
        """等待页面开始加载
        :param timeout: 超时时间（秒），为None时使用页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ...

    def doc_loaded(self, timeout: float = None, raise_err: bool = None) -> bool:
        """等待页面加载完成
        :param timeout: 超时时间（秒），为None时使用页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ...

    def upload_paths_inputted(self) -> bool:
        """等待自动填写上传文件路径"""
        ...

    def download_begin(self, timeout: float = None, cancel_it: bool = False) -> Union[DownloadMission, bool, dict]:
        """等待浏览器下载开始，可将其拦截
        :param timeout: 超时时间（秒），None使用页面对象超时时间
        :param cancel_it: 是否取消该任务
        :return: 成功返回任务对象（cancel_it为True时返回dict格式的下载信息），失败返回False
        """
        ...

    def url_change(self,
                   text: str,
                   exclude: bool = False,
                   timeout: float = None,
                   raise_err: bool = None) -> ChromiumBase:
        """等待url变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当url不包含text指定文本时返回True
        :param timeout: 超时时间（秒）
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...

    def title_change(self,
                     text: str,
                     exclude: bool = False,
                     timeout: float = None,
                     raise_err: bool = None) -> ChromiumBase:
        """等待title变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当title不包含text指定文本时返回True
        :param timeout: 超时时间（秒），为None使用页面设置
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...

    def _change(self,
                arg: str,
                text: str,
                exclude: bool = False,
                timeout: float = None,
                raise_err: bool = None) -> bool:
        """等待指定属性变成包含或不包含指定文本
        :param arg: 要被匹配的属性
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当属性不包含text指定文本时返回True
        :param timeout: 超时时间（秒）
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ...

    def _loading(self,
                 timeout: float = None,
                 start: bool = True,
                 gap: float = .01,
                 raise_err: bool = None) -> bool:
        """等待页面开始加载或加载完成
        :param timeout: 超时时间（秒），为None时使用页面timeout属性
        :param start: 等待开始还是结束
        :param gap: 间隔秒数
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 是否等待成功
        """
        ...


class TabWaiter(BaseWaiter):
    _owner: ChromiumTab = ...

    def __init__(self, owner: ChromiumTab):
        """
        :param owner: Tab对象
        """
        ...

    def __call__(self,
                 second: float,
                 scope: float = None) -> ChromiumTab:
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: ChromiumTab对象
        """
        ...

    def downloads_done(self,
                       timeout: float = None,
                       cancel_if_timeout: bool = True) -> Union[False, ChromiumTab]:
        """等待所有浏览器下载任务结束
        :param timeout: 超时时间（秒），为None时无限等待
        :param cancel_if_timeout: 超时时是否取消剩余任务
        :return: 是否等待成功
        """
        ...

    def alert_closed(self, timeout: float = None) -> ChromiumTab:
        """等待弹出框关闭
        :param timeout: 超时时间，为None无限等待
        :return: 标签页对象自己
        """
        ...

    def url_change(self,
                   text: str,
                   exclude: bool = False,
                   timeout: float = None,
                   raise_err: bool = None) -> Union[False, ChromiumTab]:
        """等待url变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当url不包含text指定文本时返回True
        :param timeout: 超时时间（秒）
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...

    def title_change(self,
                     text: str,
                     exclude: bool = False,
                     timeout: float = None,
                     raise_err: bool = None) -> Union[False, ChromiumTab]:
        """等待title变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当title不包含text指定文本时返回True
        :param timeout: 超时时间（秒），为None使用页面设置
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...


class MixTabWaiter(BaseWaiter):
    _owner: MixTab = ...

    def __init__(self, owner: MixTab):
        """
        :param owner: Tab对象
        """
        ...

    def __call__(self,
                 second: float,
                 scope: float = None) -> MixTab:
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: MixTab对象
        """
        ...

    def downloads_done(self,
                       timeout: float = None,
                       cancel_if_timeout: bool = True) -> Union[False, MixTab]:
        """等待所有浏览器下载任务结束
        :param timeout: 超时时间（秒），为None时无限等待
        :param cancel_if_timeout: 超时时是否取消剩余任务
        :return: 是否等待成功
        """
        ...

    def alert_closed(self, timeout: float = None) -> MixTab:
        """等待弹出框关闭
        :param timeout: 超时时间，为None无限等待
        :return: 标签页对象自己
        """
        ...

    def url_change(self,
                   text: str,
                   exclude: bool = False,
                   timeout: float = None,
                   raise_err: bool = None) -> Union[False, MixTab]:
        """等待url变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当url不包含text指定文本时返回True
        :param timeout: 超时时间（秒）
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...

    def title_change(self,
                     text: str,
                     exclude: bool = False,
                     timeout: float = None,
                     raise_err: bool = None) -> Union[False, MixTab]:
        """等待title变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当title不包含text指定文本时返回True
        :param timeout: 超时时间（秒），为None使用页面设置
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...


class ChromiumPageWaiter(TabWaiter):
    _owner: Union[ChromiumPage, WebPage] = ...

    def __init__(self, owner: ChromiumPage):
        """
        :param owner: Page对象
        """
        ...

    def __call__(self,
                 second: float,
                 scope: float = None) -> ChromiumPage:
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: ChromiumPage对象
        """
        ...

    def new_tab(self,
                timeout: float = None,
                raise_err: bool = None) -> Union[str, bool]:
        """等待新标签页出现
        :param timeout: 超时时间（秒），为None则使用页面对象timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等到新标签页返回其id，否则返回False
        """
        ...

    def all_downloads_done(self,
                           timeout: float = None,
                           cancel_if_timeout: bool = True) -> bool:
        """等待所有浏览器下载任务结束
        :param timeout: 超时时间（秒），为None时无限等待
        :param cancel_if_timeout: 超时时是否取消剩余任务
        :return: 是否等待成功
        """
        ...

    def url_change(self,
                   text: str,
                   exclude: bool = False,
                   timeout: float = None,
                   raise_err: bool = None) -> Union[False, ChromiumPage]:
        """等待url变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当url不包含text指定文本时返回True
        :param timeout: 超时时间（秒）
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...

    def title_change(self,
                     text: str,
                     exclude: bool = False,
                     timeout: float = None,
                     raise_err: bool = None) -> Union[False, ChromiumPage]:
        """等待title变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当title不包含text指定文本时返回True
        :param timeout: 超时时间（秒），为None使用页面设置
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...


class WebPageWaiter(TabWaiter):
    _owner: Union[ChromiumPage, WebPage] = ...

    def __init__(self, owner: WebPage):
        """
        :param owner: Page对象
        """
        ...

    def __call__(self,
                 second: float,
                 scope: float = None) -> WebPage:
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: WebPage对象
        """
        ...

    def new_tab(self,
                timeout: float = None,
                raise_err: bool = None) -> Union[str, bool]:
        """等待新标签页出现
        :param timeout: 超时时间（秒），为None则使用页面对象timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等到新标签页返回其id，否则返回False
        """
        ...

    def all_downloads_done(self,
                           timeout: float = None,
                           cancel_if_timeout: bool = True) -> bool:
        """等待所有浏览器下载任务结束
        :param timeout: 超时时间（秒），为None时无限等待
        :param cancel_if_timeout: 超时时是否取消剩余任务
        :return: 是否等待成功
        """
        ...

    def url_change(self,
                   text: str,
                   exclude: bool = False,
                   timeout: float = None,
                   raise_err: bool = None) -> Union[False, WebPage]:
        """等待url变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当url不包含text指定文本时返回True
        :param timeout: 超时时间（秒）
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...

    def title_change(self,
                     text: str,
                     exclude: bool = False,
                     timeout: float = None,
                     raise_err: bool = None) -> Union[False, WebPage]:
        """等待title变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当title不包含text指定文本时返回True
        :param timeout: 超时时间（秒），为None使用页面设置
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...


class ElementWaiter(OriginWaiter):
    _owner: ChromiumElement = ...
    _ele: ChromiumElement = ...

    def __init__(self, owner: ChromiumElement):
        """
        :param owner: ChromiumElement对象
        """
        ...

    def __call__(self,
                 second: float,
                 scope: float = None) -> ChromiumElement:
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: ChromiumElement对象
        """
        ...

    @property
    def _timeout(self) -> float:
        """返回超时设置"""
        ...

    def deleted(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待元素从dom删除
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def displayed(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待元素从dom显示
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def hidden(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待元素从dom隐藏
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def covered(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待当前元素被遮盖
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回覆盖元素id，返回False
        """
        ...

    def not_covered(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待当前元素不被遮盖
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def enabled(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待当前元素变成可用
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def disabled(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待当前元素变成不可用
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def disabled_or_deleted(self, timeout: float = None, raise_err: bool = None) -> bool:
        """等待当前元素变成不可用或从DOM移除
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def clickable(self,
                  wait_moved: bool = True,
                  timeout: float = None,
                  raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待当前元素可被点击
        :param wait_moved: 是否等待元素运动结束
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def has_rect(self,
                 timeout: float = None,
                 raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待当前元素有大小及位置属性
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def stop_moving(self,
                    timeout: float = None,
                    gap: float = .1,
                    raise_err: bool = None) -> Union[ChromiumElement, False]:
        """等待当前元素停止运动
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param gap: 检测间隔时间
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def _wait_state(self,
                    attr: str,
                    mode: bool = False,
                    timeout: float = None,
                    raise_err: bool = None,
                    err_text: str = None) -> Union[ChromiumElement, False]:
        """等待元素某个元素状态到达指定状态
        :param attr: 状态名称
        :param mode: 等待True还是False
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :param err_text: 抛出错误时显示的信息
        :return: 成功返回元素对象，失败返回False
        """
        ...


class FrameWaiter(BaseWaiter, ElementWaiter):
    _owner: ChromiumFrame = ...

    def __init__(self, owner: ChromiumFrame):
        """
        :param owner: ChromiumFrame对象
        """
        ...

    def __call__(self,
                 second: float,
                 scope: float = None) -> ChromiumFrame:
        """等待若干秒，如传入两个参数，等待时间为这两个数间的一个随机数
        :param second: 秒数
        :param scope: 随机数范围
        :return: ChromiumFrame对象
        """
        ...

    def url_change(self,
                   text: str,
                   exclude: bool = False,
                   timeout: float = None,
                   raise_err: bool = None) -> Union[False, ChromiumFrame]:
        """等待url变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当url不包含text指定文本时返回True
        :param timeout: 超时时间（秒）
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...

    def title_change(self,
                     text: str,
                     exclude: bool = False,
                     timeout: float = None,
                     raise_err: bool = None) -> Union[False, ChromiumFrame]:
        """等待title变成包含或不包含指定文本
        :param text: 用于识别的文本
        :param exclude: 是否排除，为True时当title不包含text指定文本时返回True
        :param timeout: 超时时间（秒），为None使用页面设置
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 等待成功返回页面对象，否则返回False
        """
        ...

    def deleted(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待元素从dom删除
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def displayed(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待元素从dom显示
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def hidden(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待元素从dom隐藏
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def has_rect(self,
                 timeout: float = None,
                 raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待当前元素有大小及位置属性
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def covered(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待当前元素被遮盖
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回覆盖元素id，返回False
        """
        ...

    def not_covered(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待当前元素不被遮盖
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def enabled(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待当前元素变成可用
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def disabled(self, timeout: float = None, raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待当前元素变成不可用
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def disabled_or_deleted(self, timeout: float = None, raise_err: bool = None) -> bool:
        """等待当前元素变成不可用或从DOM移除
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def clickable(self,
                  wait_moved: bool = True,
                  timeout: float = None,
                  raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待当前元素可被点击
        :param wait_moved: 是否等待元素运动结束
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...

    def stop_moving(self,
                    timeout: float = None,
                    gap: float = .1,
                    raise_err: bool = None) -> Union[ChromiumFrame, False]:
        """等待当前元素停止运动
        :param timeout: 超时时间（秒），为None使用元素所在页面timeout属性
        :param gap: 检测间隔时间
        :param raise_err: 等待失败时是否报错，为None时根据Settings设置
        :return: 成功返回元素对象，失败返回False
        """
        ...


def wait_mission(browser: Chromium, tid: str, timeout: float = None) -> Union[DownloadMission, False]:
    """等待下载任务
    :param browser: Chromium对象
    :param tid: 标签页id
    :param timeout: 超时时间
    :return:
    """
    ...
