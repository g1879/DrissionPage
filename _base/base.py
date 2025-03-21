# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from abc import abstractmethod
from copy import copy
from pathlib import Path
from re import sub
from urllib.parse import quote

from DownloadKit import DownloadKit
from requests import Session

from .._configs.session_options import SessionOptions
from .._elements.none_element import NoneElement
from .._functions.elements import get_frame, get_eles
from .._functions.locator import get_loc
from .._functions.settings import Settings as _S
from .._functions.web import format_html
from ..errors import ElementNotFoundError, LocatorError


class BaseParser(object):
    def __call__(self, locator):
        return self.ele(locator)

    def ele(self, locator, index=1, timeout=None):
        return self._ele(locator, timeout, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        return self._ele(locator, timeout, index=None)

    def find(self, locators, any_one=True, first_ele=True, timeout=None):
        if 'Session' in self._type:
            timeout = 0
        if timeout is None:
            timeout = self.timeout
        r = get_eles(locators, self, any_one, first_ele, timeout)
        if any_one:
            for ele in r:
                if r[ele]:
                    return ele, r[ele]
            return None, None
        return r

    # ----------------以下属性或方法待后代实现----------------
    @property
    def html(self):
        return ''

    def s_ele(self, locator=None):
        pass

    def s_eles(self, locator):
        pass

    def _ele(self, locator, timeout=None, index=1, raise_err=None, method=None):
        pass

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        pass


class BaseElement(BaseParser):
    def __init__(self, owner=None):
        self.owner = owner
        self._type = 'BaseElement'

    def get_frame(self, loc_or_ind, timeout=None):
        if not isinstance(loc_or_ind, (int, str, tuple)):
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'loc_or_ind',
                                           ALLOW_TYPE=_S._lang.LOC_OR_IND, CURR_VAL=loc_or_ind))
        return get_frame(self, loc_ind_ele=loc_or_ind, timeout=timeout)

    def _ele(self, locator, timeout=None, index=1, relative=False, raise_err=None, method=None):
        if hasattr(locator, '_type'):
            return locator
        if timeout is None:
            timeout = self.timeout
        r = self._find_elements(locator, timeout=timeout, index=index, relative=relative, raise_err=raise_err)
        if r or isinstance(r, list):
            return r
        if raise_err is True or (_S.raise_when_ele_not_found and raise_err is None):
            raise ElementNotFoundError(METHOD=method, ARGS={'locator': locator, 'index': index, 'timeout': timeout})

        r.method = method
        r.args = {'locator': locator, 'index': index, 'timeout': timeout}
        return r

    @property
    def timeout(self):
        return self.owner.timeout if self.owner else 10

    @property
    def child_count(self):
        return int(self._ele('xpath:count(./*)'))

    # ----------------以下属性或方法由后代实现----------------
    @property
    def tag(self):
        return

    def parent(self, level_or_loc=1):
        pass

    def next(self, index=1):
        pass

    def nexts(self):
        pass


class DrissionElement(BaseElement):

    @property
    def link(self):
        return self.attr('href') or self.attr('src')

    @property
    def css_path(self):
        return self._get_ele_path(xpath=False)

    @property
    def xpath(self):
        return self._get_ele_path()

    @property
    def comments(self):
        return self.eles('xpath:.//comment()')

    def texts(self, text_node_only=False):
        texts = self.eles('xpath:/text()') if text_node_only else [x if isinstance(x, str) else x.text
                                                                   for x in self.eles('xpath:./text() | *')]
        return [format_html(x.strip(' ').rstrip('\n')) for x in texts if x and sub('[\r\n\t ]', '', x) != '']

    def parent(self, level_or_loc=1, index=1, timeout=None):
        if isinstance(level_or_loc, int):
            loc = f'xpath:./ancestor::*[{level_or_loc}]'

        elif isinstance(level_or_loc, (tuple, str)):
            loc = get_loc(level_or_loc, True)
            if loc[0] == 'css selector':
                raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)
            loc = f'xpath:./ancestor::{loc[1].lstrip(". / ")}[{index}]'

        else:
            raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'level_or_loc', ALLOW_TYPE='tuple, int, str',
                                           CURR_VAL=level_or_loc))

        return self._ele(loc, timeout=timeout, relative=True, raise_err=False, method='parent()')

    def child(self, locator='', index=1, timeout=None, ele_only=True):
        if isinstance(locator, int):
            index = locator
            locator = ''
        if not locator:
            loc = '*' if ele_only else 'node()'
        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)
            loc = loc[1].lstrip('./')

        node = self._ele(f'xpath:./{loc}', timeout=timeout, index=index, relative=True, raise_err=False)
        return node if node else NoneElement(self.owner, 'child()',
                                             {'locator': locator, 'index': index, 'ele_only': ele_only})

    def prev(self, locator='', index=1, timeout=None, ele_only=True):
        return self._get_relative('prev()', 'preceding', True, locator, index, timeout, ele_only)

    def next(self, locator='', index=1, timeout=None, ele_only=True):
        return self._get_relative('next()', 'following', True, locator, index, timeout, ele_only)

    def before(self, locator='', index=1, timeout=None, ele_only=True):
        return self._get_relative('before()', 'preceding', False, locator, index, timeout, ele_only)

    def after(self, locator='', index=1, timeout=None, ele_only=True):
        return self._get_relative('after()', 'following', False, locator, index, timeout, ele_only)

    def children(self, locator='', timeout=None, ele_only=True):
        if not locator:
            loc = '*' if ele_only else 'node()'
        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        nodes = self._ele(loc, timeout=timeout, index=None, relative=True)
        return [e for e in nodes if not (isinstance(e, str) and sub('[ \n\t\r]', '', e) == '')]

    def prevs(self, locator='', timeout=None, ele_only=True):
        return self._get_relatives(locator=locator, direction='preceding', timeout=timeout, ele_only=ele_only)

    def nexts(self, locator='', timeout=None, ele_only=True):
        return self._get_relatives(locator=locator, direction='following', timeout=timeout, ele_only=ele_only)

    def befores(self, locator='', timeout=None, ele_only=True):
        return self._get_relatives(locator=locator, direction='preceding',
                                   brother=False, timeout=timeout, ele_only=ele_only)

    def afters(self, locator='', timeout=None, ele_only=True):
        return self._get_relatives(locator=locator, direction='following',
                                   brother=False, timeout=timeout, ele_only=ele_only)

    def _get_relative(self, func, direction, brother, locator='', index=1, timeout=None, ele_only=True):
        if isinstance(locator, int):
            index = locator
            locator = ''
        node = self._get_relatives(index, locator, direction, brother, timeout, ele_only)
        return node if node else NoneElement(self.owner, func,
                                             {'locator': locator, 'index': index, 'ele_only': ele_only})

    def _get_relatives(self, index=None, locator='', direction='following', brother=True, timeout=.5, ele_only=True):
        brother = '-sibling' if brother else ''

        if not locator:
            loc = '*' if ele_only else 'node()'

        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise LocatorError(_S._lang.UNSUPPORTED_CSS_SYNTAX)
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{direction}{brother}::{loc}'

        if index is not None:
            index = index if direction == 'following' else -index
        nodes = self._ele(loc, timeout=timeout, index=index, relative=True, raise_err=False)
        if isinstance(nodes, list):
            nodes = [e for e in nodes if not (isinstance(e, str) and sub('[ \n\t\r]', '', e) == '')]
        return nodes

    # ----------------以下属性或方法由后代实现----------------
    @property
    def attrs(self):
        return

    @property
    def text(self):
        return

    @property
    def raw_text(self):
        return

    @abstractmethod
    def attr(self, name):
        return ''

    def _get_ele_path(self, xpath=True):
        return ''

    def _find_elements(self, locator, timeout, index=1, relative=False, raise_err=None):
        pass


class BasePage(BaseParser):

    def __init__(self):
        self._url = None
        self._url_available = None
        self.retry_times = 3
        self.retry_interval = 2
        self._DownloadKit = None
        self._download_path = None
        self._none_ele_return_value = False
        self._none_ele_value = None
        self._session = None
        self._headers = None
        self._session_options = None
        self._type = 'BasePage'

    @property
    def title(self):
        ele = self._ele('xpath://title', raise_err=False, method='title')
        return ele.text if ele else None

    @property
    def url_available(self):
        return self._url_available

    @property
    def download_path(self):
        return self._download_path

    @property
    def download(self):
        if self._DownloadKit is None:
            if not self._session:
                self._create_session()
            self._DownloadKit = DownloadKit(driver=self, save_path=self.download_path)
        return self._DownloadKit

    def _before_connect(self, url, retry, interval):
        is_file = False
        if isinstance(url, Path) or ('://' not in url and ':\\\\' not in url):
            p = Path(url)
            if p.exists():
                url = str(p.absolute())
                is_file = True

        self._url = url if is_file else quote(url, safe='-_.~!*\'"();:@&=+$,/\\?#[]%')
        retry = retry if retry is not None else self.retry_times
        interval = interval if interval is not None else self.retry_interval
        return retry, interval, is_file

    def _set_session_options(self, session_or_options=None):
        if not session_or_options:
            self._session_options = SessionOptions(session_or_options)

        elif isinstance(session_or_options, SessionOptions):
            self._session_options = session_or_options

        elif isinstance(session_or_options, Session):
            self._session_options = SessionOptions()
            self._session = copy(session_or_options)
            self._headers = self._session.headers
            self._session.headers = None

    def _create_session(self):
        if not self._session_options:
            self._set_session_options()
        self._session, self._headers = self._session_options.make_session()

    # ----------------以下属性或方法由后代实现----------------
    @property
    def url(self):
        return

    @property
    def json(self):
        return

    @property
    def user_agent(self):
        return

    @abstractmethod
    def get(self, url, show_errmsg=False, retry=None, interval=None):
        pass

    def _ele(self, locator, timeout=None, index=1, raise_err=None, method=None):
        if not locator:
            raise ElementNotFoundError(METHOD=method, ARGS={'locator': locator, 'index': index, 'timeout': timeout})
        if timeout is None:
            timeout = self.timeout

        r = self._find_elements(locator, timeout=timeout, index=index, raise_err=raise_err)
        if r or isinstance(r, list):
            return r
        if raise_err is True or (_S.raise_when_ele_not_found and raise_err is None):
            raise ElementNotFoundError(METHOD=method, ARGS={'locator': locator, 'index': index, 'timeout': timeout})

        r.method = method
        r.args = {'locator': locator, 'index': index, 'timeout': timeout}
        return r
