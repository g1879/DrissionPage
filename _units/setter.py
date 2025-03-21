# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from time import sleep

from requests.structures import CaseInsensitiveDict

from .cookies_setter import (SessionCookiesSetter, CookiesSetter, WebPageCookiesSetter, BrowserCookiesSetter,
                             MixTabCookiesSetter)
from .._functions.settings import Settings as _S
from .._functions.tools import show_or_hide_browser
from .._functions.web import format_headers
from ..errors import ElementLostError, JavaScriptError


class BaseSetter(object):
    def __init__(self, owner):
        self._owner = owner

    def NoneElement_value(self, value=None, on_off=True):
        self._owner._none_ele_return_value = on_off
        self._owner._none_ele_value = value

    def retry_times(self, times):
        self._owner.retry_times = times

    def retry_interval(self, interval):
        self._owner.retry_interval = interval

    def download_path(self, path):
        if path is None:
            path = '.'
        self._owner._download_path = str(Path(path).absolute())


class SessionPageSetter(BaseSetter):
    def __init__(self, owner):
        super().__init__(owner)
        self._cookies_setter = None

    @property
    def cookies(self):
        if self._cookies_setter is None:
            self._cookies_setter = SessionCookiesSetter(self._owner)
        return self._cookies_setter

    def download_path(self, path):
        super().download_path(path)
        if self._owner._DownloadKit:
            self._owner._DownloadKit.set.save_path(self._owner._download_path)

    def timeout(self, second):
        self._owner._timeout = second

    def encoding(self, encoding, set_all=True):
        if set_all:
            self._owner._encoding = encoding if encoding else None
        if self._owner.response:
            self._owner.response.encoding = encoding

    def headers(self, headers):
        self._owner._headers = CaseInsensitiveDict(format_headers(headers))

    def header(self, name, value):
        self._owner._headers[name] = value

    def user_agent(self, ua):
        self._owner._headers['user-agent'] = ua

    def proxies(self, http=None, https=None):
        self._owner.session.proxies = {'http': http, 'https': https}

    def auth(self, auth):
        self._owner.session.auth = auth

    def hooks(self, hooks):
        self._owner.session.hooks = hooks

    def params(self, params):
        self._owner.session.params = params

    def verify(self, on_off):
        self._owner.session.verify = on_off

    def cert(self, cert):
        self._owner.session.cert = cert

    def stream(self, on_off):
        self._owner.session.stream = on_off

    def trust_env(self, on_off):
        self._owner.session.trust_env = on_off

    def max_redirects(self, times):
        self._owner.session.max_redirects = times

    def add_adapter(self, url, adapter):
        self._owner.session.mount(url, adapter)


class BrowserBaseSetter(BaseSetter):
    def __init__(self, owner):
        super().__init__(owner)
        self._cookies_setter = None

    @property
    def load_mode(self):
        return LoadMode(self._owner)

    def timeouts(self, base=None, page_load=None, script=None):
        if base is not None:
            self._owner.timeouts.base = base

        if page_load is not None:
            self._owner.timeouts.page_load = page_load

        if script is not None:
            self._owner.timeouts.script = script


class BrowserSetter(BrowserBaseSetter):

    @property
    def cookies(self):
        if self._cookies_setter is None:
            self._cookies_setter = BrowserCookiesSetter(self._owner)
        return self._cookies_setter

    def auto_handle_alert(self, on_off=True, accept=True):
        self._owner._auto_handle_alert = None if on_off is None else accept if on_off else 'close'

    def download_path(self, path):
        super().download_path(path)
        self._owner._dl_mgr.set_path('browser', self._owner._download_path)

    def download_file_name(self, name=None, suffix=None):
        self._owner._dl_mgr.set_rename('browser', name, suffix)

    def when_download_file_exists(self, mode):
        types = {'rename': 'rename', 'overwrite': 'overwrite', 'skip': 'skip', 'r': 'rename', 'o': 'overwrite',
                 's': 'skip'}
        mode = types.get(mode, mode)
        if mode not in types:
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_VAL_, 'mode',
                                           ALLOW_VAL="', '".join(types.keys()), CURR_VAL=mode))
        self._owner._dl_mgr.set_file_exists('browser', mode)


class ChromiumBaseSetter(BrowserBaseSetter):

    @property
    def scroll(self):
        return PageScrollSetter(self._owner.scroll)

    @property
    def cookies(self):
        if self._cookies_setter is None:
            self._cookies_setter = CookiesSetter(self._owner)
        return self._cookies_setter

    def headers(self, headers):
        self._owner._run_cdp('Network.enable')
        self._owner._run_cdp('Network.setExtraHTTPHeaders', headers=format_headers(headers))

    def user_agent(self, ua, platform=None):
        keys = {'userAgent': ua}
        if platform:
            keys['platform'] = platform
        self._owner._run_cdp('Emulation.setUserAgentOverride', **keys)

    def session_storage(self, item, value):
        self._owner._run_cdp_loaded('DOMStorage.enable')
        i = self._owner._run_cdp('Storage.getStorageKeyForFrame', frameId=self._owner._frame_id)['storageKey']
        if value is False:
            self._owner._run_cdp('DOMStorage.removeDOMStorageItem',
                                 storageId={'storageKey': i, 'isLocalStorage': False}, key=item)
        else:
            self._owner._run_cdp('DOMStorage.setDOMStorageItem', storageId={'storageKey': i, 'isLocalStorage': False},
                                 key=item, value=value)
        self._owner._run_cdp_loaded('DOMStorage.disable')

    def local_storage(self, item, value):
        self._owner._run_cdp_loaded('DOMStorage.enable')
        i = self._owner._run_cdp('Storage.getStorageKeyForFrame', frameId=self._owner._frame_id)['storageKey']
        if value is False:
            self._owner._run_cdp('DOMStorage.removeDOMStorageItem',
                                 storageId={'storageKey': i, 'isLocalStorage': True}, key=item)
        else:
            self._owner._run_cdp('DOMStorage.setDOMStorageItem', storageId={'storageKey': i, 'isLocalStorage': True},
                                 key=item, value=value)
        self._owner._run_cdp_loaded('DOMStorage.disable')

    def upload_files(self, files):
        if not self._owner._upload_list:
            self._owner.driver.set_callback('Page.fileChooserOpened', self._owner._onFileChooserOpened)
            self._owner._run_cdp('Page.setInterceptFileChooserDialog', enabled=True)

        if isinstance(files, str):
            files = files.split('\n')
        elif isinstance(files, Path):
            files = (files,)
        self._owner._upload_list = [str(Path(i).absolute()) for i in files]

    def auto_handle_alert(self, on_off=True, accept=True):
        self._owner._alert.auto = None if on_off is None else accept if on_off else 'close'

    def blocked_urls(self, urls):
        if not urls:
            urls = []
        elif isinstance(urls, str):
            urls = (urls,)
        if not isinstance(urls, (list, tuple)):
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'urls',
                                           ALLOW_TYPE='str, list, tuple', CURR_VAL=urls))
        self._owner._run_cdp('Network.enable')
        self._owner._run_cdp('Network.setBlockedURLs', urls=urls)


class TabSetter(ChromiumBaseSetter):
    def __init__(self, owner):
        super().__init__(owner)

    @property
    def window(self):
        return WindowSetter(self._owner)

    def download_path(self, path):
        super().download_path(path)
        self._owner.browser._dl_mgr.set_path(self._owner, self._owner._download_path)
        if self._owner._DownloadKit:
            self._owner._DownloadKit.set.save_path(self._owner._download_path)

    def download_file_name(self, name=None, suffix=None):
        self._owner.browser._dl_mgr.set_rename(self._owner.tab_id, name, suffix)

    def when_download_file_exists(self, mode):
        types = {'rename': 'rename', 'overwrite': 'overwrite', 'skip': 'skip',
                 'r': 'rename', 'o': 'overwrite', 's': 'skip'}
        mode = types.get(mode, mode)
        if mode not in types:
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_VAL_, 'mode',
                                           ALLOW_VAL="', '".join(types.keys()), CURR_VAL=mode))
        self._owner.browser._dl_mgr.set_file_exists(self._owner.tab_id, mode)

    def activate(self):
        self._owner.browser.activate_tab(self._owner.tab_id)


class ChromiumPageSetter(TabSetter):

    def NoneElement_value(self, value=None, on_off=True):
        super().NoneElement_value(value, on_off)
        self._owner.browser._none_ele_return_value = on_off
        self._owner.browser._none_ele_value = value

    def retry_times(self, times):
        super().retry_times(times)
        self._owner.browser.retry_times = times

    def retry_interval(self, interval):
        super().retry_interval(interval)
        self._owner.browser.retry_interval = interval

    def download_path(self, path):
        if path is None:
            path = '.'
        self._owner._download_path = str(Path(path).absolute())
        self._owner.browser.set.download_path(path)
        if self._owner._DownloadKit:
            self._owner._DownloadKit.set.save_path(path)

    def download_file_name(self, name=None, suffix=None):
        self._owner.browser.set.download_file_name(name, suffix)

    def when_download_file_exists(self, mode):
        self._owner.browser.set.when_download_file_exists(mode)


class WebPageSetter(ChromiumPageSetter):
    def __init__(self, owner):
        super().__init__(owner)
        self._session_setter = SessionPageSetter(self._owner)
        self._chromium_setter = ChromiumPageSetter(self._owner)

    @property
    def cookies(self):
        if self._cookies_setter is None:
            self._cookies_setter = WebPageCookiesSetter(self._owner)
        return self._cookies_setter

    def headers(self, headers):
        if self._owner.mode == 's':
            self._session_setter.headers(headers)
        else:
            self._chromium_setter.headers(headers)

    def user_agent(self, ua, platform=None):
        if self._owner.mode == 's':
            self._session_setter.user_agent(ua)
        else:
            self._chromium_setter.user_agent(ua, platform)


class MixTabSetter(TabSetter):
    def __init__(self, owner):
        super().__init__(owner)
        self._session_setter = SessionPageSetter(self._owner)
        self._chromium_setter = ChromiumBaseSetter(self._owner)

    @property
    def cookies(self):
        if self._cookies_setter is None:
            self._cookies_setter = MixTabCookiesSetter(self._owner)
        return self._cookies_setter

    def headers(self, headers):
        if self._owner._session:
            self._session_setter.headers(headers)
        if self._owner._driver and self._owner._driver.is_running:
            self._chromium_setter.headers(headers)

    def user_agent(self, ua, platform=None):
        if self._owner._session:
            self._session_setter.user_agent(ua)
        if self._owner._driver and self._owner._driver.is_running:
            self._chromium_setter.user_agent(ua, platform)

    def timeouts(self, base=None, page_load=None, script=None):
        super().timeouts(base=base, page_load=page_load, script=script)
        if base is not None:
            self._owner._timeout = base


class ChromiumElementSetter(object):
    def __init__(self, ele):
        self._ele = ele

    def attr(self, name, value=''):
        try:
            self._ele.owner._run_cdp('DOM.setAttributeValue',
                                     nodeId=self._ele._node_id, name=name, value=str(value))
        except ElementLostError:
            self._ele._refresh_id()
            self._ele.owner._run_cdp('DOM.setAttributeValue',
                                     nodeId=self._ele._node_id, name=name, value=str(value))

    def property(self, name, value):
        value = value.replace('"', r'\"')
        self._ele._run_js(f'this.{name}="{value}";')

    def style(self, name, value):
        try:
            self._ele._run_js(f'this.style.{name}="{value}";')
        except JavaScriptError:
            raise RuntimeError(_S._lang.join(_S._lang.SET_FAILED_, name, VALUE=value))

    def innerHTML(self, html):
        self.property('innerHTML', html)

    def value(self, value):
        self.property('value', value)


class ChromiumFrameSetter(ChromiumBaseSetter):
    def attr(self, name, value):
        self._owner.frame_ele.set.attr(name, value)

    def property(self, name, value):
        self._owner.frame_ele.set.property(name=name, value=value)

    def style(self, name, value):
        self._owner.frame_ele.set.style(name=name, value=value)


class LoadMode(object):
    def __init__(self, owner):
        self._owner = owner

    def __call__(self, value):
        if value.lower() not in ('normal', 'eager', 'none'):
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_VAL_, 'value',
                                           ALLOW_VAL="'normal', 'eager', 'none'", CURR_VAL=value))
        self._owner._load_mode = value
        if self._owner._type in ('ChromiumPage', 'WebPage'):
            self._owner.browser._load_mode = value

    def normal(self):
        self.__call__('normal')

    def eager(self):
        self.__call__('eager')

    def none(self):
        self.__call__('none')


class PageScrollSetter(object):
    def __init__(self, scroll):
        self._scroll = scroll

    def wait_complete(self, on_off=True):
        if not isinstance(on_off, bool):
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'on_off',
                                           ALLOW_TYPE='bool', CURR_TYPE=type(on_off)))
        self._scroll._wait_complete = on_off

    def smooth(self, on_off=True):
        if not isinstance(on_off, bool):
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'on_off',
                                           ALLOW_TYPE='bool', CURR_TYPE=type(on_off)))
        b = 'smooth' if on_off else 'auto'
        self._scroll._owner._run_js(f'document.documentElement.style.setProperty("scroll-behavior","{b}");')
        self._scroll._wait_complete = on_off


class WindowSetter(object):
    def __init__(self, owner):
        self._owner = owner
        self._window_id = self._get_info()['windowId']

    def max(self):
        s = self._get_info()['bounds']['windowState']
        if s in ('fullscreen', 'minimized'):
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'maximized'})

    def mini(self):
        s = self._get_info()['bounds']['windowState']
        if s == 'fullscreen':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'minimized'})

    def full(self):
        s = self._get_info()['bounds']['windowState']
        if s == 'minimized':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'fullscreen'})

    def normal(self):
        s = self._get_info()['bounds']['windowState']
        if s == 'fullscreen':
            self._perform({'windowState': 'normal'})
        self._perform({'windowState': 'normal'})

    def size(self, width=None, height=None):
        if width or height:
            s = self._get_info()['bounds']['windowState']
            if s != 'normal':
                self._perform({'windowState': 'normal'})
            info = self._get_info()['bounds']
            width = width - 16 if width else info['width']
            height = height + 7 if height else info['height']
            self._perform({'width': width, 'height': height})

    def location(self, x=None, y=None):
        if x is not None or y is not None:
            self.normal()
            info = self._get_info()['bounds']
            x = x if x is not None else info['left']
            y = y if y is not None else info['top']
            self._perform({'left': x - 8, 'top': y})

    def hide(self):
        show_or_hide_browser(self._owner, hide=True)

    def show(self):
        show_or_hide_browser(self._owner, hide=False)

    def _get_info(self):
        for _ in range(50):
            try:
                return self._owner._run_cdp('Browser.getWindowForTarget')
            except:
                sleep(.02)
        raise RuntimeError(_S._lang.join(_S._lang.GET_WINDOW_SIZE_FAILED))

    def _perform(self, bounds):
        try:
            self._owner._run_cdp('Browser.setWindowBounds', windowId=self._window_id, bounds=bounds)
        except:
            raise RuntimeError(_S._lang.join(TIP=_S._lang.SET_WINDOW_NORMAL))
