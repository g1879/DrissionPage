# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from pathlib import Path
from platform import system
from re import search
from time import perf_counter, sleep

from requests import Session

from .chromium_base import Timeout, ChromiumBase
from .chromium_tab import ChromiumTab
from .common import connect_chrome
from .config import DriverOptions
from .chromium_driver import ChromiumDriver


class ChromiumPage(ChromiumBase):
    """用于管理浏览器的类"""

    def __init__(self, addr_driver_opts=None, tab_id=None, timeout=None):
        """初始化                                                                       \n
        :param addr_driver_opts: 浏览器地址:端口、ChromiumDriver对象或DriverOptions对象
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :param timeout: 超时时间
        """
        super().__init__(addr_driver_opts, tab_id, timeout)

    def _connect_browser(self, addr_driver_opts=None, tab_id=None):
        """连接浏览器，在第一次时运行                                    \n
        :param addr_driver_opts: 浏览器地址、ChromiumDriver对象或DriverOptions对象
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :return: None
        """
        self._is_loading = False
        self._is_reading = False
        self._root_id = None
        self.timeouts = Timeout(self)
        self._control_session = Session()
        self._control_session.keep_alive = False
        self._alert = Alert()
        self._first_run = True

        # 接管或启动浏览器
        if addr_driver_opts is None or isinstance(addr_driver_opts, DriverOptions):
            self.options = addr_driver_opts or DriverOptions()  # 从ini文件读取
            self.address = self.options.debugger_address
            self.process = connect_chrome(self.options)[1]
            json = self._control_session.get(f'http://{self.address}/json').json()
            tab_id = [i['id'] for i in json if i['type'] == 'page'][0]

        # 接收浏览器地址和端口
        elif isinstance(addr_driver_opts, str):
            self.address = addr_driver_opts
            self.options = DriverOptions(read_file=False)
            self.options.debugger_address = addr_driver_opts
            self.process = connect_chrome(self.options)[1]
            if not tab_id:
                json = self._control_session.get(f'http://{self.address}/json').json()
                tab_id = [i['id'] for i in json if i['type'] == 'page'][0]

        # 接收传递过来的ChromiumDriver，浏览器
        elif isinstance(addr_driver_opts, ChromiumDriver):
            self._tab_obj = addr_driver_opts
            self.address = search(r'ws://(.*?)/dev', addr_driver_opts._websocket_url).group(1)
            self.process = None
            self.options = DriverOptions(read_file=False)

        else:
            raise TypeError('只能接收ChromiumDriver或DriverOptions类型参数。')

        self._set_options()
        self._init_page(tab_id)
        self._get_document()
        self._first_run = False
        self._main_tab = self.tab_id

    def _init_page(self, tab_id=None):
        """新建页面、页面刷新、切换标签页后要进行的cdp参数初始化
        :param tab_id: 要跳转到的标签页id
        :return: None
        """
        super()._init_page(tab_id)

        self._tab_obj.Page.javascriptDialogOpening = self._on_alert_open
        self._tab_obj.Page.javascriptDialogClosed = self._on_alert_close

    def _set_options(self):
        self.set_timeouts(page_load=self.options.timeouts['pageLoad'] / 1000,
                          script=self.options.timeouts['script'] / 1000,
                          implicit=self.options.timeouts['implicit'] / 1000 if self.timeout is None else self.timeout)
        self._page_load_strategy = self.options.page_load_strategy

    @property
    def tabs_count(self):
        """返回标签页数量"""
        return len(self.tabs)

    @property
    def tabs(self):
        """返回所有标签页id组成的列表"""
        tabs = self.run_cdp('Target.getTargets', filter=[{'type': "page"}])['targetInfos']
        return [i['targetId'] for i in tabs]

    @property
    def main_tab(self):
        return self._main_tab

    @property
    def process_id(self):
        """返回浏览器进程id"""
        try:
            return self._driver.SystemInfo.getProcessInfo()['id']
        except Exception:
            return None

    @property
    def set_window(self):
        """返回用于设置窗口大小的对象"""
        if not hasattr(self, '_window_setter'):
            self._window_setter = WindowSetter(self)
        return self._window_setter

    def get_tab(self, tab_id=None):
        """获取一个标签页对象                                    \n
        :param tab_id: 要获取的标签页id，为None时获取当前tab
        :return: 标签页对象
        """
        tab_id = tab_id or self.tab_id
        return ChromiumTab(self, tab_id)

    def get_screenshot(self, path=None, as_bytes=None, full_page=False, left_top=None, right_bottom=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持             \n
        :param path: 完整路径，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否已字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :return: 图片完整路径或字节文本
        """
        if as_bytes:
            if as_bytes is True:
                pic_type = 'png'
            else:
                if as_bytes not in ('jpg', 'jpeg', 'png', 'webp'):
                    raise ValueError("只能接收'jpg', 'jpeg', 'png', 'webp'四种格式。")
                pic_type = 'jpeg' if as_bytes == 'jpg' else as_bytes

        else:
            if not path:
                raise ValueError('保存为文件时必须传入路径。')
            path = Path(path)
            pic_type = path.suffix.lower()
            if pic_type not in ('.jpg', '.jpeg', '.png', '.webp'):
                raise TypeError(f'不支持的文件格式：{pic_type}。')
            pic_type = 'jpeg' if pic_type == '.jpg' else pic_type[1:]

        width, height = self.size
        if full_page:
            vp = {'x': 0, 'y': 0, 'width': width, 'height': height, 'scale': 1}
            png = self._wait_driver.Page.captureScreenshot(format=pic_type, captureBeyondViewport=True, clip=vp)['data']
        else:
            if left_top and right_bottom:
                x, y = left_top
                w = right_bottom[0] - x
                h = right_bottom[1] - y
                vp = {'x': x, 'y': y, 'width': w, 'height': h, 'scale': 1}
                png = self._wait_driver.Page.captureScreenshot(format=pic_type, captureBeyondViewport=True, clip=vp)[
                    'data']
            else:
                png = self._wait_driver.Page.captureScreenshot(format=pic_type)['data']

        from base64 import b64decode
        png = b64decode(png)

        if as_bytes:
            return png

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(png)
        return str(path.absolute())

    def to_front(self):
        """激活当前标签页使其处于最前面"""
        self._control_session.get(f'http://{self.address}/json/activate/{self.tab_id}')

    def new_tab(self, url=None, switch_to=True):
        """新建一个标签页,该标签页在最后面                \n
        :param url: 新标签页跳转到的网址
        :param switch_to: 新建标签页后是否把焦点移过去
        :return: None
        """
        if switch_to:
            begin_len = len(self.tabs)
            self._control_session.get(f'http://{self.address}/json/new')

            tabs = self.tabs
            while len(tabs) <= begin_len:
                tabs = self.tabs

            self._to_tab(tabs[0], read_doc=False)
            if url:
                self.get(url)

        elif url:
            self._control_session.get(f'http://{self.address}/json/new?{url}')

        else:
            self._control_session.get(f'http://{self.address}/json/new')

    def set_main_tab(self, tab_id=None):
        """设置主tab                               \n
        :param tab_id: 标签页id，不传入则设置当前tab
        :return: None
        """
        self._main_tab = tab_id or self.tab_id

    def to_main_tab(self):
        """跳转到主标签页"""
        self.to_tab(self._main_tab)

    def to_tab(self, tab_id=None, activate=True):
        """跳转到标签页                                           \n
        :param tab_id: 标签页id字符串，默认跳转到main_tab
        :param activate: 切换后是否变为活动状态
        :return: None
        """
        self._to_tab(tab_id, activate)

    def _to_tab(self, tab_id=None, activate=True, read_doc=True):
        """跳转到标签页                                           \n
        :param tab_id: 标签页id字符串，默认跳转到main_tab
        :param activate: 切换后是否变为活动状态
        :param read_doc: 切换后是否读取文档
        :return: None
        """
        tabs = self.tabs
        if not tab_id:
            tab_id = self._main_tab
        if tab_id not in tabs:
            tab_id = tabs[0]

        if activate:
            self._control_session.get(f'http://{self.address}/json/activate/{tab_id}')

        if tab_id == self.tab_id:
            return

        self._driver.stop()
        self._init_page(tab_id)
        if read_doc and self.ready_state == 'complete':
            self._get_document()

    def close_tabs(self, tab_ids=None, others=False):
        """关闭传入的标签页，默认关闭当前页。可传入多个                                                        \n
        :param tab_ids: 要关闭的标签页id，可传入id组成的列表或元组，为None时关闭当前页
        :param others: 是否关闭指定标签页之外的
        :return: None
        """
        all_tabs = set(self.tabs)
        if isinstance(tab_ids, str):
            tabs = {tab_ids}
        elif tab_ids is None:
            tabs = {self.tab_id}
        else:
            tabs = set(tab_ids)

        if others:
            tabs = all_tabs - tabs

        end_len = len(all_tabs) - len(tabs)
        if end_len <= 0:
            self.quit()
            return

        if self.tab_id in tabs:
            self._driver.stop()

        for tab in tabs:
            self._control_session.get(f'http://{self.address}/json/close/{tab}')
        while len(self.tabs) != end_len:
            sleep(.1)

        if self._main_tab in tabs:
            self._main_tab = self.tabs[0]

        self.to_tab()

    def close_other_tabs(self, tab_ids=None):
        """关闭传入的标签页以外标签页，默认保留当前页。可传入多个                                              \n
        :param tab_ids: 要保留的标签页id，可传入id组成的列表或元组，为None时保存当前页
        :return: None
        """
        self.close_tabs(tab_ids, True)

    def handle_alert(self, accept=True, send=None, timeout=None):
        """处理提示框，可以自动等待提示框出现                                                       \n
        :param accept: True表示确认，False表示取消，其它值不会按按钮但依然返回文本值
        :param send: 处理prompt提示框时可输入文本
        :param timeout: 等待提示框出现的超时时间，为None则使用self.timeout属性的值
        :return: 提示框内容文本，未等到提示框则返回None
        """
        timeout = timeout or self.timeout
        end_time = perf_counter() + timeout
        while not self._alert.activated and perf_counter() < end_time:
            sleep(.1)
        if not self._alert.activated:
            return None

        res_text = self._alert.text
        if self._alert.type == 'prompt':
            self._driver.Page.handleJavaScriptDialog(accept=accept, promptText=send)
        else:
            self._driver.Page.handleJavaScriptDialog(accept=accept)
        return res_text

    def hide_browser(self):
        """隐藏浏览器窗口，只在Windows系统可用"""
        show_or_hide_browser(self, hide=True)

    def show_browser(self):
        """显示浏览器窗口，只在Windows系统可用"""
        show_or_hide_browser(self, hide=False)

    def quit(self):
        """关闭浏览器"""
        self._tab_obj.Browser.close()
        self._tab_obj.stop()

    def _on_alert_close(self, **kwargs):
        """alert关闭时触发的方法"""
        self._alert.activated = False
        self._alert.text = None
        self._alert.type = None
        self._alert.defaultPrompt = None
        self._alert.response_accept = kwargs.get('result')
        self._alert.response_text = kwargs['userInput']

    def _on_alert_open(self, **kwargs):
        """alert出现时触发的方法"""
        self._alert.activated = True
        self._alert.text = kwargs['message']
        self._alert.type = kwargs['message']
        self._alert.defaultPrompt = kwargs.get('defaultPrompt', None)
        self._alert.response_accept = None
        self._alert.response_text = None


class Alert(object):
    """用于保存alert信息的类"""

    def __init__(self):
        self.activated = False
        self.text = None
        self.type = None
        self.defaultPrompt = None
        self.response_accept = None
        self.response_text = None


class WindowSetter(object):
    """用于设置窗口大小的类"""

    def __init__(self, page):
        self.driver = page._driver
        self.window_id = self._get_info()['windowId']

    def maximized(self):
        """窗口最大化"""
        self._perform({'windowState': 'maximized'})

    def minimized(self):
        """窗口最小化"""
        self._perform({'windowState': 'minimized'})

    def fullscreen(self):
        """设置窗口为全屏"""
        self._perform({'windowState': 'fullscreen'})

    def normal(self):
        """设置窗口为常规模式"""
        self._perform({'windowState': 'normal'})

    def size(self, width=None, height=None):
        """设置窗口大小             \n
        :param width: 窗口宽度
        :param height: 窗口高度
        :return: None
        """
        if width or height:
            info = self._get_info()['bounds']
            width = width or info['width']
            height = height or info['height']
            self._perform({'width': width, 'height': height})

    def location(self, x=None, y=None):
        """设置窗口在屏幕中的位置，相对左上角坐标  \n
        :param x: 距离顶部距离
        :param y: 距离左边距离
        :return: None
        """
        if x or y:
            self.normal()
            info = self._get_info()['bounds']
            x = x or info['left']
            y = y or info['top']
            self._perform({'left': x, 'top': y})

    def _get_info(self):
        """获取窗口位置及大小信息"""
        return self.driver.Browser.getWindowBounds()

    def _perform(self, bounds):
        """执行改变窗口大小操作
        :param bounds: 控制数据
        :return: None
        """
        self.driver.Browser.setWindowBounds(windowId=self.window_id, bounds=bounds)


def show_or_hide_browser(page, hide=True):
    """执行显示或隐藏浏览器窗口
    :param page: ChromePage对象
    :param hide: 是否隐藏
    :return: None
    """
    if not page.address.startswith(('localhost', '127.0.0.1')):
        return

    if system().lower() != 'windows':
        raise OSError('该方法只能在Windows系统使用。')

    try:
        from win32gui import ShowWindow
        from win32con import SW_HIDE, SW_SHOW
    except ImportError:
        raise ImportError('请先安装：pip install pypiwin32')

    pid = page.process_id or get_browser_progress_id(page.process, page.address)
    if not pid:
        return None
    hds = get_chrome_hwnds_from_pid(pid, page.title)
    sw = SW_HIDE if hide else SW_SHOW
    for hd in hds:
        ShowWindow(hd, sw)


def get_browser_progress_id(progress, address):
    """获取浏览器进程id
    :param progress: 已知的进程对象，没有时传入None
    :param address: 浏览器管理地址，含端口
    :return: 进程id或None
    """
    if progress:
        return progress.pid

    from os import popen
    port = address.split(':')[-1]
    txt = ''
    progresses = popen(f'netstat -nao | findstr :{port}').read().split('\n')
    for progress in progresses:
        if 'LISTENING' in progress:
            txt = progress
            break
    if not txt:
        return None

    return txt.split(' ')[-1]


def get_chrome_hwnds_from_pid(pid, title):
    """通过PID查询句柄ID
    :param pid: 进程id
    :param title: 窗口标题
    :return: 进程句柄组成的列表
    """
    try:
        from win32gui import IsWindow, GetWindowText, EnumWindows
        from win32process import GetWindowThreadProcessId
    except ImportError:
        raise ImportError('请先安装win32gui，pip install pypiwin32')

    def callback(hwnd, hds):
        if IsWindow(hwnd) and title in GetWindowText(hwnd):
            _, found_pid = GetWindowThreadProcessId(hwnd)
            if str(found_pid) == str(pid):
                hds.append(hwnd)
            return True

    hwnds = []
    EnumWindows(callback, hwnds)
    return hwnds
