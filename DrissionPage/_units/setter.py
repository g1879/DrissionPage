# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path
from time import sleep

from requests.structures import CaseInsensitiveDict

from .cookies_setter import SessionCookiesSetter, CookiesSetter, WebPageCookiesSetter
from .._functions.tools import show_or_hide_browser


class BasePageSetter(object):
    def __init__(self, page):
        self._page = page

    def NoneElement_value(self, value=None, on_off=True):
        """设置空元素是否返回设定值
        :param value: 返回的设定值
        :param on_off: 是否启用
        :return: None
        """
        self._page._none_ele_return_value = on_off
        self._page._none_ele_value = value


class ChromiumBaseSetter(BasePageSetter):
    def __init__(self, page):
        super().__init__(page)
        self._cookies_setter = None

    @property
    def load_mode(self):
        """返回用于设置页面加载策略的对象"""
        return LoadMode(self._page)

    @property
    def scroll(self):
        """返回用于设置页面滚动设置的对象"""
        return PageScrollSetter(self._page.scroll)

    @property
    def cookies(self):
        """返回用于设置cookies的对象"""
        if self._cookies_setter is None:
            self._cookies_setter = CookiesSetter(self._page)
        return self._cookies_setter

    def retry_times(self, times):
        """设置连接失败重连次数"""
        self._page.retry_times = times

    def retry_interval(self, interval):
        """设置连接失败重连间隔"""
        self._page.retry_interval = interval

    def timeouts(self, base=None, page_load=None, script=None, implicit=None):
        """设置超时时间，单位为秒
        :param base: 基本等待时间，除页面加载和脚本超时，其它等待默认使用
        :param page_load: 页面加载超时时间
        :param script: 脚本运行超时时间
        :return: None
        """
        base = base if base is not None else implicit
        if base is not None:
            self._page.timeouts.base = base
            self._page._timeout = base

        if page_load is not None:
            self._page.timeouts.page_load = page_load

        if script is not None:
            self._page.timeouts.script = script

    def user_agent(self, ua, platform=None):
        """为当前tab设置user agent，只在当前tab有效
        :param ua: user agent字符串
        :param platform: platform字符串
        :return: None
        """
        keys = {'userAgent': ua}
        if platform:
            keys['platform'] = platform
        self._page.run_cdp('Emulation.setUserAgentOverride', **keys)

    def session_storage(self, item, value):
        """设置或删除某项sessionStorage信息
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        self._page.run_cdp_loaded('DOMStorage.enable')
        i = self._page.run_cdp('Storage.getStorageKeyForFrame', frameId=self._page._frame_id)['storageKey']
        if value is False:
            self._page.run_cdp('DOMStorage.removeDOMStorageItem',
                               storageId={'storageKey': i, 'isLocalStorage': False}, key=item)
        else:
            self._page.run_cdp('DOMStorage.setDOMStorageItem', storageId={'storageKey': i, 'isLocalStorage': False},
                               key=item, value=value)
        self._page.run_cdp_loaded('DOMStorage.disable')

    def local_storage(self, item, value):
        """设置或删除某项localStorage信息
        :param item: 要设置的项
        :param value: 项的值，设置为False时，删除该项
        :return: None
        """
        self._page.run_cdp_loaded('DOMStorage.enable')
        i = self._page.run_cdp('Storage.getStorageKeyForFrame', frameId=self._page._frame_id)['storageKey']
        if value is False:
            self._page.run_cdp('DOMStorage.removeDOMStorageItem',
                               storageId={'storageKey': i, 'isLocalStorage': True}, key=item)
        else:
            self._page.run_cdp('DOMStorage.setDOMStorageItem', storageId={'storageKey': i, 'isLocalStorage': True},
                               key=item, value=value)
        self._page.run_cdp_loaded('DOMStorage.disable')

    def upload_files(self, files):
        """等待上传的文件路径
        :param files: 文件路径列表或字符串，字符串时多个文件用回车分隔
        :return: None
        """
        if not self._page._upload_list:
            self._page.driver.set_callback('Page.fileChooserOpened', self._page._onFileChooserOpened)
            self._page.run_cdp('Page.setInterceptFileChooserDialog', enabled=True)

        if isinstance(files, str):
            files = files.split('\n')
        self._page._upload_list = [str(Path(i).absolute()) for i in files]

    def headers(self, headers: dict) -> None:
        """设置固定发送的headers
        :param headers: dict格式的headers数据
        :return: None
        """
        self._page.run_cdp('Network.enable')
        self._page.run_cdp('Network.setExtraHTTPHeaders', headers=headers)

    def auto_handle_alert(self, on_off=True, accept=True):
        """设置是否启用自动处理弹窗
        :param on_off: bool表示开或关
        :param accept: bool表示确定还是取消
        :return: None
        """
        self._page._alert.auto = accept if on_off else None

    def blocked_urls(self, urls):
        """设置要忽略的url
        :param urls: 要忽略的url，可用*通配符，可输入多个，传入None时清空已设置的内容
        :return: None
        """
        if not urls:
            urls = []
        elif isinstance(urls, str):
            urls = (urls,)
        if not isinstance(urls, (list, tuple)):
            raise TypeError('urls需传入str、list或tuple类型。')
        self._page.run_cdp('Network.enable')
        self._page.run_cdp('Network.setBlockedURLs', urls=urls)

    # --------------即将废弃---------------

    @property
    def load_strategy(self):
        """返回用于设置页面加载策略的对象"""
        return LoadMode(self._page)


class TabSetter(ChromiumBaseSetter):
    def __init__(self, page):
        super().__init__(page)

    @property
    def window(self):
        """返回用于设置浏览器窗口的对象"""
        return WindowSetter(self._page)

    def download_path(self, path):
        """设置下载路径
        :param path: 下载路径
        :return: None
        """
        path = str(Path(path).absolute())
        self._page._download_path = path
        self._page.browser._dl_mgr.set_path(self._page, path)
        if self._page._DownloadKit:
            self._page._DownloadKit.set.goal_path(path)

    def download_file_name(self, name=None, suffix=None):
        """设置下一个被下载文件的名称
        :param name: 文件名，可不含后缀，会自动使用远程文件后缀
        :param suffix: 后缀名，显式设置后缀名，不使用远程文件后缀
        :return: None
        """
        self._page.browser._dl_mgr.set_rename(self._page.tab_id, name, suffix)

    def when_download_file_exists(self, mode):
        """设置当存在同名文件时的处理方式
        :param mode: 可在 'rename', 'overwrite', 'skip', 'r', 'o', 's'中选择
        :return: None
        """
        types = {'rename': 'rename', 'overwrite': 'overwrite', 'skip': 'skip', 'r': 'rename', 'o': 'overwrite',
                 's': 'skip'}
        mode = types.get(mode, mode)
        if mode not in types:
            raise ValueError(f'''mode参数只能是 '{"', '".join(types.keys())}' 之一，现在是：{mode}''')

        self._page.browser._dl_mgr.set_file_exists(self._page.tab_id, mode)

    def activate(self):
        """使标签页处于最前面"""
        self._page.browser.activate_tab(self._page.tab_id)


class ChromiumPageSetter(TabSetter):

    def tab_to_front(self, tab_or_id=None):
        """激活标签页使其处于最前面
        :param tab_or_id: 标签页对象或id，为None表示当前标签页
        :return: None
        """
        if not tab_or_id:
            tab_or_id = self._page.tab_id
        elif not isinstance(tab_or_id, str):  # 传入Tab对象
            tab_or_id = tab_or_id.tab_id
        self._page.browser.activate_tab(tab_or_id)

    @property
    def window(self):
        """返回用于设置浏览器窗口的对象"""
        return PageWindowSetter(self._page)


class SessionPageSetter(BasePageSetter):
    def __init__(self, page):
        """
        :param page: SessionPage对象
        """
        super().__init__(page)
        self._cookies_setter = None

    @property
    def cookies(self):
        """返回用于设置cookies的对象"""
        if self._cookies_setter is None:
            self._cookies_setter = SessionCookiesSetter(self._page)
        return self._cookies_setter

    def retry_times(self, times):
        """设置连接失败时重连次数"""
        self._page.retry_times = times

    def retry_interval(self, interval):
        """设置连接失败时重连间隔"""
        self._page.retry_interval = interval

    def download_path(self, path):
        """设置下载路径
        :param path: 下载路径
        :return: None
        """
        path = str(Path(path).absolute())
        self._page._download_path = path
        if self._page._DownloadKit:
            self._page._DownloadKit.set.goal_path(path)

    def timeout(self, second):
        """设置连接超时时间
        :param second: 秒数
        :return: None
        """
        self._page.timeout = second

    def encoding(self, encoding, set_all=True):
        """设置编码
        :param encoding: 编码名称，如果要取消之前的设置，传入None
        :param set_all: 是否设置对象参数，为False则只设置当前Response
        :return: None
        """
        if set_all:
            self._page._encoding = encoding if encoding else None
        if self._page.response:
            self._page.response.encoding = encoding

    def headers(self, headers):
        """设置通用的headers
        :param headers: dict形式的headers
        :return: None
        """
        self._page._headers = CaseInsensitiveDict(headers)

    def header(self, name, value):
        """设置headers中一个项
        :param name: 设置名称
        :param value: 设置值
        :return: None
        """
        self._page._headers[name] = value

    def user_agent(self, ua):
        """设置user agent
        :param ua: user agent
        :return: None
        """
        self._page._headers['user-agent'] = ua

    def proxies(self, http=None, https=None):
        """设置proxies参数
        :param http: http代理地址
        :param https: https代理地址
        :return: None
        """
        self._page.session.proxies = {'http': http, 'https': https}

    def auth(self, auth):
        """设置认证元组或对象
        :param auth: 认证元组或对象
        :return: None
        """
        self._page.session.auth = auth

    def hooks(self, hooks):
        """设置回调方法
        :param hooks: 回调方法
        :return: None
        """
        self._page.session.hooks = hooks

    def params(self, params):
        """设置查询参数字典
        :param params: 查询参数字典
        :return: None
        """
        self._page.session.params = params

    def verify(self, on_off):
        """设置是否验证SSL证书
        :param on_off: 是否验证 SSL 证书
        :return: None
        """
        self._page.session.verify = on_off

    def cert(self, cert):
        """SSL客户端证书文件的路径(.pem格式)，或(‘cert’, ‘key’)元组
        :param cert: 证书路径或元组
        :return: None
        """
        self._page.session.cert = cert

    def stream(self, on_off):
        """设置是否使用流式响应内容
        :param on_off: 是否使用流式响应内容
        :return: None
        """
        self._page.session.stream = on_off

    def trust_env(self, on_off):
        """设置是否信任环境
        :param on_off: 是否信任环境
        :return: None
        """
        self._page.session.trust_env = on_off

    def max_redirects(self, times):
        """设置最大重定向次数
        :param times: 最大重定向次数
        :return: None
        """
        self._page.session.max_redirects = times

    def add_adapter(self, url, adapter):
        """添加适配器
        :param url: 适配器对应url
        :param adapter: 适配器对象
        :return: None
        """
        self._page.session.mount(url, adapter)


class WebPageSetter(ChromiumPageSetter):
    def __init__(self, page):
        super().__init__(page)
        self._session_setter = SessionPageSetter(self._page)
        self._chromium_setter = ChromiumPageSetter(self._page)

    @property
    def cookies(self):
        """返回用于设置cookies的对象"""
        if self._cookies_setter is None:
            self._cookies_setter = WebPageCookiesSetter(self._page)
        return self._cookies_setter

    def headers(self, headers) -> None:
        """设置固定发送的headers
        :param headers: dict格式的headers数据
        :return: None
        """
        if self._page.mode == 's':
            self._session_setter.headers(headers)
        else:
            self._chromium_setter.headers(headers)

    def user_agent(self, ua, platform=None):
        """设置user agent，d模式下只有当前tab有效"""
        if self._page.mode == 's':
            self._session_setter.user_agent(ua)
        else:
            self._chromium_setter.user_agent(ua, platform)


class WebPageTabSetter(TabSetter):
    def __init__(self, page):
        super().__init__(page)
        self._session_setter = SessionPageSetter(self._page)
        self._chromium_setter = ChromiumBaseSetter(self._page)

    @property
    def cookies(self):
        """返回用于设置cookies的对象"""
        if self._cookies_setter is None:
            self._cookies_setter = WebPageCookiesSetter(self._page)
        return self._cookies_setter

    def headers(self, headers) -> None:
        """设置固定发送的headers
        :param headers: dict格式的headers数据
        :return: None
        """
        if self._page._has_session:
            self._session_setter.headers(headers)
        if self._page._has_driver:
            self._chromium_setter.headers(headers)

    def user_agent(self, ua, platform=None):
        """设置user agent，d模式下只有当前tab有效"""
        if self._page._has_session:
            self._session_setter.user_agent(ua)
        if self._page._has_driver:
            self._chromium_setter.user_agent(ua, platform)


class ChromiumElementSetter(object):
    def __init__(self, ele):
        """
        :param ele: ChromiumElement
        """
        self._ele = ele

    def attr(self, name, value):
        """设置元素attribute属性
        :param name: 属性名
        :param value: 属性值
        :return: None
        """
        self._ele.page.run_cdp('DOM.setAttributeValue', nodeId=self._ele._node_id, name=name, value=str(value))

    def property(self, name, value):
        """设置元素property属性
        :param name: 属性名
        :param value: 属性值
        :return: None
        """
        value = value.replace('"', r'\"')
        self._ele.run_js(f'this.{name}="{value}";')

    def innerHTML(self, html):
        """设置元素innerHTML
        :param html: html文本
        :return: None
        """
        self.property('innerHTML', html)

    def value(self, value):
        """设置元素value值
        :param value: value值
        :return: None
        """
        self.property('value', value)


class ChromiumFrameSetter(ChromiumBaseSetter):
    def attr(self, name, value):
        """设置frame元素attribute属性
        :param name: 属性名
        :param value: 属性值
        :return: None
        """
        self._page.frame_ele.set.attr(name, value)


class LoadMode(object):
    """用于设置页面加载策略的类"""

    def __init__(self, page):
        """
        :param page: ChromiumBase对象
        """
        self._page = page

    def __call__(self, value):
        """设置加载策略
        :param value: 可选 'normal', 'eager', 'none'
        :return: None
        """
        if value.lower() not in ('normal', 'eager', 'none'):
            raise ValueError("只能选择 'normal', 'eager', 'none'。")
        self._page._load_mode = value

    def normal(self):
        """设置页面加载策略为normal"""
        self._page._load_mode = 'normal'

    def eager(self):
        """设置页面加载策略为eager"""
        self._page._load_mode = 'eager'

    def none(self):
        """设置页面加载策略为none"""
        self._page._load_mode = 'none'


class PageScrollSetter(object):
    def __init__(self, scroll):
        self._scroll = scroll

    def wait_complete(self, on_off=True):
        """设置滚动命令后是否等待完成
        :param on_off: 开或关
        :return: None
        """
        if not isinstance(on_off, bool):
            raise TypeError('on_off必须为bool。')
        self._scroll._wait_complete = on_off

    def smooth(self, on_off=True):
        """设置页面滚动是否平滑滚动
        :param on_off: 开或关
        :return: None
        """
        if not isinstance(on_off, bool):
            raise TypeError('on_off必须为bool。')
        b = 'smooth' if on_off else 'auto'
        self._scroll._driver.run_js(f'document.documentElement.style.setProperty("scroll-behavior","{b}");')
        self._scroll._wait_complete = on_off


class WindowSetter(object):
    """用于设置窗口大小的类"""

    def __init__(self, page):
        """
        :param page: 页面对象
        """
        self._page = page
        self._window_id = self._get_info()['windowId']

    def max(self):
        """窗口最大化"""
        s = self._get_info()['bounds']['windowState']
        if s in ('fullscreen', 'minimized'):
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'maximized'})

    def mini(self):
        """窗口最小化"""
        s = self._get_info()['bounds']['windowState']
        if s == 'fullscreen':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'minimized'})

    def full(self):
        """设置窗口为全屏"""
        s = self._get_info()['bounds']['windowState']
        if s == 'minimized':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'fullscreen'})

    def normal(self):
        """设置窗口为常规模式"""
        s = self._get_info()['bounds']['windowState']
        if s == 'fullscreen':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'normal'})

    def size(self, width=None, height=None):
        """设置窗口大小
        :param width: 窗口宽度
        :param height: 窗口高度
        :return: None
        """
        if width or height:
            s = self._get_info()['bounds']['windowState']
            if s != 'normal':
                self._perform({'windowState': 'normal'})
            info = self._get_info()['bounds']
            width = width - 16 if width else info['width']
            height = height + 7 if height else info['height']
            self._perform({'width': width, 'height': height})

    def location(self, x=None, y=None):
        """设置窗口在屏幕中的位置，相对左上角坐标
        :param x: 距离顶部距离
        :param y: 距离左边距离
        :return: None
        """
        if x is not None or y is not None:
            self.normal()
            info = self._get_info()['bounds']
            x = x if x is not None else info['left']
            y = y if y is not None else info['top']
            self._perform({'left': x - 8, 'top': y})

    def _get_info(self):
        """获取窗口位置及大小信息"""
        for _ in range(50):
            try:
                return self._page.run_cdp('Browser.getWindowForTarget')
            except:
                sleep(.1)

    def _perform(self, bounds):
        """执行改变窗口大小操作
        :param bounds: 控制数据
        :return: None
        """
        try:
            self._page.run_cdp('Browser.setWindowBounds', windowId=self._window_id, bounds=bounds)
        except:
            raise RuntimeError('浏览器全屏或最小化状态时请先调用set.window.normal()恢复正常状态。')

    # ------------即将废除----------

    def maximized(self):
        """窗口最大化"""
        self.max()

    def minimized(self):
        """窗口最小化"""
        self.mini()

    def fullscreen(self):
        """设置窗口为全屏"""
        self.full()


class PageWindowSetter(WindowSetter):
    def hide(self):
        """隐藏浏览器窗口，只在Windows系统可用"""
        show_or_hide_browser(self._page, hide=True)

    def show(self):
        """显示浏览器窗口，只在Windows系统可用"""
        show_or_hide_browser(self._page, hide=False)
