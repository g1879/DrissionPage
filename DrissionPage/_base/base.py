# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from abc import abstractmethod
from pathlib import Path
from re import sub
from urllib.parse import quote

from DownloadKit import DownloadKit

from .._functions.settings import Settings
from .._functions.locator import get_loc
from .._functions.web import format_html
from .._elements.none_element import NoneElement
from ..errors import ElementNotFoundError


class BaseParser(object):
    """所有页面、元素类的基类"""

    def __call__(self, locator):
        return self.ele(locator)

    def ele(self, locator, index=1, timeout=None):
        return self._ele(locator, timeout, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        return self._ele(locator, timeout, index=None)

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

    def _find_elements(self, locator, timeout=None, index=1, relative=False, raise_err=None):
        pass


class BaseElement(BaseParser):
    """各元素类的基类"""

    def __init__(self, owner=None):
        self.owner = owner
        self.page = owner._page if owner else None
        self._type = 'BaseElement'

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

    def _ele(self, locator, timeout=None, index=1, relative=False, raise_err=None, method=None):
        """调用获取元素的方法
        :param locator: 定位符
        :param timeout: 超时时间（秒）
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param relative: 是否相对定位
        :param raise_err: 找不到时是否抛出异常
        :param method: 调用的方法名
        :return: 元素对象或它们组成的列表
        """
        r = self._find_elements(locator, timeout=timeout, index=index, relative=relative, raise_err=raise_err)
        if r or isinstance(r, list):
            return r
        if Settings.raise_when_ele_not_found or raise_err is True:
            raise ElementNotFoundError(None, method, {'locator': locator, 'index': index})

        r.method = method
        r.args = {'locator': locator, 'index': index}
        return r


class DrissionElement(BaseElement):
    """ChromiumElement 和 SessionElement的基类，但不是ShadowRoot的基类"""

    @property
    def link(self):
        """返回href或src绝对url"""
        return self.attr('href') or self.attr('src')

    @property
    def css_path(self):
        """返回css path路径"""
        return self._get_ele_path('css')

    @property
    def xpath(self):
        """返回xpath路径"""
        return self._get_ele_path('xpath')

    @property
    def comments(self):
        """返回元素注释文本组成的列表"""
        return self.eles('xpath:.//comment()')

    def texts(self, text_node_only=False):
        """返回元素内所有直接子节点的文本，包括元素和文本节点
        :param text_node_only: 是否只返回文本节点
        :return: 文本列表
        """
        if text_node_only:
            texts = self.eles('xpath:/text()')
        else:
            texts = [x if isinstance(x, str) else x.text for x in self.eles('xpath:./text() | *')]

        return [format_html(x.strip(' ').rstrip('\n')) for x in texts if x and sub('[\r\n\t ]', '', x) != '']

    def parent(self, level_or_loc=1, index=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，1开始，或定位符
        :param index: 当level_or_loc传入定位符，使用此参数选择第几个结果，1开始
        :return: 上级元素对象
        """
        if isinstance(level_or_loc, int):
            loc = f'xpath:./ancestor::*[{level_or_loc}]'

        elif isinstance(level_or_loc, (tuple, str)):
            loc = get_loc(level_or_loc, True)

            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')

            loc = f'xpath:./ancestor::{loc[1].lstrip(". / ")}[{index}]'

        else:
            raise TypeError('level_or_loc参数只能是tuple、int或str。')

        return self._ele(loc, timeout=0, relative=True, raise_err=False, method='parent()')

    def child(self, locator='', index=1, timeout=None, ele_only=True):
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param index: 第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        if isinstance(locator, int):
            index = locator
            locator = ''
        if not locator:
            loc = '*' if ele_only else 'node()'
        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
            loc = loc[1].lstrip('./')

        node = self._ele(f'xpath:./{loc}', timeout=timeout, index=index, relative=True, raise_err=False)
        return node if node else NoneElement(self.owner, 'child()',
                                             {'locator': locator, 'index': index, 'ele_only': ele_only})

    def prev(self, locator='', index=1, timeout=None, ele_only=True):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素
        """
        return self._get_relative('prev()', 'preceding', True, locator, index, timeout, ele_only)

    def next(self, locator='', index=1, timeout=None, ele_only=True):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素
        """
        return self._get_relative('next()', 'following', True, locator, index, timeout, ele_only)

    def before(self, locator='', index=1, timeout=None, ele_only=True):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        return self._get_relative('before()', 'preceding', False, locator, index, timeout, ele_only)

    def after(self, locator='', index=1, timeout=None, ele_only=True):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param locator: 用于筛选的查询语法
        :param index: 后面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的某个元素或节点
        """
        return self._get_relative('after()', 'following', False, locator, index, timeout, ele_only)

    def children(self, locator='', timeout=None, ele_only=True):
        """返回直接子元素元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 直接子元素或节点文本组成的列表
        """
        if not locator:
            loc = '*' if ele_only else 'node()'
        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
            loc = loc[1].lstrip('./')

        loc = f'xpath:./{loc}'
        nodes = self._ele(loc, timeout=timeout, index=None, relative=True)
        return [e for e in nodes if not (isinstance(e, str) and sub('[ \n\t\r]', '', e) == '')]

    def prevs(self, locator='', timeout=None, ele_only=True):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return self._get_relatives(locator=locator, direction='preceding', timeout=timeout, ele_only=ele_only)

    def nexts(self, locator='', timeout=None, ele_only=True):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 兄弟元素或节点文本组成的列表
        """
        return self._get_relatives(locator=locator, direction='following', timeout=timeout, ele_only=ele_only)

    def befores(self, locator='', timeout=None, ele_only=True):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的元素或节点组成的列表
        """
        return self._get_relatives(locator=locator, direction='preceding',
                                   brother=False, timeout=timeout, ele_only=ele_only)

    def afters(self, locator='', timeout=None, ele_only=True):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param locator: 用于筛选的查询语法
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素后面的元素或节点组成的列表
        """
        return self._get_relatives(locator=locator, direction='following',
                                   brother=False, timeout=timeout, ele_only=ele_only)

    def _get_relative(self, func, direction, brother, locator='', index=1, timeout=None, ele_only=True):
        """获取一个亲戚元素或节点，可用查询语法筛选，可指定返回筛选结果的第几个
        :param func: 方法名称
        :param direction: 方向，'following' 或 'preceding'
        :param locator: 用于筛选的查询语法
        :param index: 前面第几个查询结果，1开始
        :param timeout: 查找节点的超时时间（秒）
        :param ele_only: 是否只获取元素，为False时把文本、注释节点也纳入
        :return: 本元素前面的某个元素或节点
        """
        if isinstance(locator, int):
            index = locator
            locator = ''
        node = self._get_relatives(index, locator, direction, brother, timeout, ele_only)
        return node if node else NoneElement(self.owner, func,
                                             {'locator': locator, 'index': index, 'ele_only': ele_only})

    def _get_relatives(self, index=None, locator='', direction='following', brother=True, timeout=.5, ele_only=True):
        """按要求返回兄弟元素或节点组成的列表
        :param index: 获取第几个，该参数不为None时只获取该编号的元素
        :param locator: 用于筛选的查询语法
        :param direction: 'following' 或 'preceding'，查找的方向
        :param brother: 查找范围，在同级查找还是整个dom前后查找
        :param timeout: 查找等待时间（秒）
        :return: 元素对象或字符串
        """
        brother = '-sibling' if brother else ''

        if not locator:
            loc = '*' if ele_only else 'node()'

        else:
            loc = get_loc(locator, True)  # 把定位符转换为xpath
            if loc[0] == 'css selector':
                raise ValueError('此css selector语法不受支持，请换成xpath。')
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
    def attr(self, name: str):
        return ''

    def _get_ele_path(self, mode):
        return ''

    def _find_elements(self, locator, timeout=None, index=1, relative=False, raise_err=None):
        pass


class BasePage(BaseParser):
    """页面类的基类"""

    def __init__(self):
        """初始化函数"""
        self._url = None
        self._timeout = 10
        self._url_available = None
        self.retry_times = 3
        self.retry_interval = 2
        self._DownloadKit = None
        self._download_path = None
        self._none_ele_return_value = False
        self._none_ele_value = None
        self._type = 'BasePage'

    @property
    def title(self):
        """返回网页title"""
        ele = self._ele('xpath://title', raise_err=False, method='title')
        return ele.text if ele else None

    @property
    def timeout(self):
        """返回查找元素时等待的秒数"""
        return self._timeout

    @timeout.setter
    def timeout(self, second):
        """设置查找元素时等待的秒数"""
        self._timeout = second

    @property
    def url_available(self):
        """返回当前访问的url有效性"""
        return self._url_available

    @property
    def download_path(self):
        """返回默认下载路径"""
        return self._download_path

    @property
    def download(self):
        """返回下载器对象"""
        if self._DownloadKit is None:
            self._DownloadKit = DownloadKit(driver=self, goal_path=self.download_path)
        return self._DownloadKit

    def _before_connect(self, url, retry, interval):
        """连接前的准备
        :param url: 要访问的url
        :param retry: 重试次数
        :param interval: 重试间隔
        :return: 重试次数、间隔、是否文件组成的tuple
        """
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
    def cookies(self, as_dict=False, all_info=False):
        return {}

    @abstractmethod
    def get(self, url, show_errmsg=False, retry=None, interval=None):
        pass

    def _ele(self, locator, timeout=None, index=1, raise_err=None, method=None):
        """调用获取元素的方法
        :param locator: 定位符
        :param timeout: 超时时间（秒）
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param raise_err: 找不到时是否抛出异常
        :param method: 调用的方法名
        :return: 元素对象或它们组成的列表
        """
        if not locator:
            raise ElementNotFoundError(None, method, {'locator': locator})

        r = self._find_elements(locator, timeout=timeout, index=index, raise_err=raise_err)

        if r or isinstance(r, list):
            return r
        if Settings.raise_when_ele_not_found or raise_err is True:
            raise ElementNotFoundError(None, method, {'locator': locator, 'index': index})

        r.method = method
        r.args = {'locator': locator, 'index': index}
        return r
