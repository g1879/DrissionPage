# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   session_page.py
"""
from os import path as os_PATH
from random import randint
from re import search
from time import time, sleep
from typing import Union, List, Tuple
from urllib.parse import urlparse, quote, unquote

from requests import Session, Response
from tldextract import extract
from DownloadKit import DownloadKit

from .base import BasePage
from .config import _cookie_to_dict
from .session_element import SessionElement, make_session_ele


class SessionPage(BasePage):
    """SessionPage封装了页面操作的常用功能，使用requests来获取、解析网页"""

    def __init__(self, session: Session, timeout: float = 10):
        """初始化函数"""
        super().__init__(timeout)
        self._session = session
        self._response = None
        self._download_kit = None

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, SessionElement],
                 timeout=None) -> Union[SessionElement, str, None]:
        """在内部查找元素                                                  \n
        例：ele2 = ele1('@id=ele_id')                                     \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性文本
        """
        return self.ele(loc_or_str)

    # -----------------共有属性和方法-------------------
    @property
    def url(self) -> str:
        """返回当前访问url"""
        return self._url

    @property
    def html(self) -> str:
        """返回页面的html文本"""
        return self.response.text if self.response else ''

    @property
    def json(self) -> dict:
        """当返回内容是json格式时，返回对应的字典"""
        return self.response.json()

    def get(self,
            url: str,
            show_errmsg: bool = False,
            retry: int = None,
            interval: float = None,
            **kwargs) -> bool:
        """用get方式跳转到url                                 \n
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        to_url = quote(url, safe='/:&?=%;#@+!')
        retry = retry if retry is not None else self.retry_times
        interval = interval if interval is not None else self.retry_interval

        if not url:
            raise ValueError('没有传入url。')

        self._url = to_url
        self._response = self._try_to_connect(to_url, times=retry, interval=interval, show_errmsg=show_errmsg, **kwargs)

        if self._response is None:
            self._url_available = False

        else:
            if self._response.ok:
                self._url_available = True

            else:
                if show_errmsg:
                    raise ConnectionError(f'{to_url}\n连接状态码：{self._response.status_code}.')

                self._url_available = False

        return self._url_available

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, SessionElement],
            timeout: float = None) -> Union[SessionElement, str, None]:
        """返回页面中符合条件的第一个元素、属性或节点文本                            \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_ele)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[SessionElement, str]]:
        """返回页面中所有符合条件的元素、属性或节点文本                          \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, single=False)

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str, SessionElement] = None) -> Union[SessionElement, str, None]:
        """返回页面中符合条件的第一个元素、属性或节点文本                          \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self.html) if loc_or_ele is None else self._ele(loc_or_ele)

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = None) -> List[Union[SessionElement, str]]:
        """返回页面中符合条件的所有元素、属性或节点文本                              \n
        :param loc_or_str: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_str, single=False)

    def _ele(self,
             loc_or_ele: Union[Tuple[str, str], str, SessionElement],
             timeout: float = None,
             single: bool = True) -> Union[SessionElement, str, None, List[Union[SessionElement, str]]]:
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个                                           \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和父类对应
        :param single: True则返回第一个，False则返回全部
        :return: SessionElement对象
        """
        return loc_or_ele if isinstance(loc_or_ele, SessionElement) else make_session_ele(self, loc_or_ele, single)

    def get_cookies(self, as_dict: bool = False, all_domains: bool = False) -> Union[dict, list]:
        """返回cookies                               \n
        :param as_dict: 是否以字典方式返回
        :param all_domains: 是否返回所有域的cookies
        :return: cookies信息
        """
        if all_domains:
            cookies = self.session.cookies
        else:
            if self.url:
                url = extract(self.url)
                domain = f'{url.domain}.{url.suffix}'
                cookies = tuple(x for x in self.session.cookies if domain in x.domain or x.domain == '')
            else:
                cookies = tuple(x for x in self.session.cookies)

        if as_dict:
            return {x.name: x.value for x in cookies}
        else:
            return [_cookie_to_dict(cookie) for cookie in cookies]

    def _try_to_connect(self,
                        to_url: str,
                        times: int = 0,
                        interval: float = 1,
                        mode: str = 'get',
                        data: Union[dict, str] = None,
                        show_errmsg: bool = False,
                        **kwargs) -> Union[Response, None]:
        """尝试连接，重试若干次                            \n
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param mode: 连接方式，'get' 或 'post'
        :param data: post方式提交的数据
        :param show_errmsg: 是否抛出异常
        :param kwargs: 连接参数
        :return: HTMLResponse对象
        """
        err = None
        r = None

        for _ in range(times + 1):
            try:
                r = self._make_response(to_url, mode=mode, data=data, show_errmsg=True, **kwargs)[0]
            except Exception as e:
                err = e
                r = None

            if r and (r.content != b'' or r.status_code in (403, 404)):
                break

            if _ < times:
                sleep(interval)
                if show_errmsg:
                    print(f'重试 {to_url}')

        if not r and show_errmsg:
            raise err if err is not None else ConnectionError(f'连接异常。{r.status_code if r is not None else ""}')

        return r

    # ----------------session独有属性和方法-----------------------
    @property
    def session(self) -> Session:
        """返回session对象"""
        return self._session

    @property
    def response(self) -> Response:
        """返回访问url得到的response对象"""
        return self._response

    @property
    def download(self) -> DownloadKit:
        if self._download_kit is None:
            self._download_kit = DownloadKit(session=self.session, timeout=self.timeout)
            self._download_kit.retry = self.retry_times
            self._download_kit.interval = self.retry_interval

        return self._download_kit

    def post(self,
             url: str,
             data: Union[dict, str] = None,
             show_errmsg: bool = False,
             retry: int = None,
             interval: float = None,
             **kwargs) -> bool:
        """用post方式跳转到url                                 \n
        :param url: 目标url
        :param data: 提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        to_url = quote(url, safe='/:&?=%;#@+!')
        retry = retry if retry is not None else self.retry_times
        interval = interval if interval is not None else self.retry_interval

        if not url:
            raise ValueError('没有传入url。')

        self._url = to_url
        self._response = self._try_to_connect(to_url, retry, interval, 'post', data, show_errmsg, **kwargs)

        if self._response is None:
            self._url_available = False

        else:
            if self._response.ok:
                self._url_available = True

            else:
                if show_errmsg:
                    raise ConnectionError(f'连接状态码：{self._response.status_code}.')
                self._url_available = False

        return self._url_available

    def _make_response(self,
                       url: str,
                       mode: str = 'get',
                       data: Union[dict, str] = None,
                       show_errmsg: bool = False,
                       **kwargs) -> tuple:
        """生成response对象                     \n
        :param url: 目标url
        :param mode: 'get', 'post' 中选择
        :param data: post方式要提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param kwargs: 其它参数
        :return: tuple，第一位为Response或None，第二位为出错信息或'Success'
        """
        if not url:
            if show_errmsg:
                raise ValueError('URL为空。')
            return None, 'URL为空。'

        if mode not in ('get', 'post'):
            raise ValueError("mode参数只能是'get'或'post'。")

        url = quote(url, safe='/:&?=%;#@+!')

        # 设置referer和host值
        kwargs_set = set(x.lower() for x in kwargs)

        if 'headers' in kwargs_set:
            header_set = set(x.lower() for x in kwargs['headers'])

            if self.url and 'referer' not in header_set:
                kwargs['headers']['Referer'] = self.url

            if 'host' not in header_set:
                kwargs['headers']['Host'] = urlparse(url).hostname

        else:
            kwargs['headers'] = self.session.headers
            kwargs['headers']['Host'] = urlparse(url).hostname

            if self.url:
                kwargs['headers']['Referer'] = self.url

        if 'timeout' not in kwargs_set:
            kwargs['timeout'] = self.timeout

        try:
            r = None

            if mode == 'get':
                r = self.session.get(url, **kwargs)
            elif mode == 'post':
                r = self.session.post(url, data=data, **kwargs)

        except Exception as e:
            if show_errmsg:
                raise e

            return None, e

        else:
            # ----------------获取并设置编码开始-----------------
            # 在headers中获取编码
            content_type = r.headers.get('content-type', '').lower()
            charset = search(r'charset[=: ]*(.*)?[;]', content_type)

            if charset:
                r.encoding = charset.group(1)

            # 在headers中获取不到编码，且如果是网页
            elif content_type.replace(' ', '').startswith('text/html'):
                re_result = search(b'<meta.*?charset=[ \\\'"]*([^"\\\' />]+).*?>', r.content)

                if re_result:
                    charset = re_result.group(1).decode()
                else:
                    charset = r.apparent_encoding

                r.encoding = charset
            # ----------------获取并设置编码结束-----------------

            return r, 'Success'


def _get_download_file_name(url, response) -> str:
    """从headers或url中获取文件名，如果获取不到，生成一个随机文件名
    :param url: 文件url
    :param response: 返回的response
    :return: 下载文件的文件名
    """
    file_name = ''
    charset = ''
    content_disposition = response.headers.get('content-disposition', '').replace(' ', '')

    # 使用header里的文件名
    if content_disposition:
        txt = search(r'filename\*="?([^";]+)', content_disposition)
        if txt:  # 文件名自带编码方式
            txt = txt.group(1).split("''", 1)
            if len(txt) == 2:
                charset, file_name = txt
            else:
                file_name = txt[0]

        else:  # 文件名没带编码方式
            txt = search(r'filename="?([^";]+)', content_disposition)
            if txt:
                file_name = txt.group(1)

                # 获取编码（如有）
                charset = response.encoding

        file_name = file_name.strip("'")

    # 在url里获取文件名
    if not file_name and os_PATH.basename(url):
        file_name = os_PATH.basename(url).split("?")[0]

    # 找不到则用时间和随机数生成文件名
    if not file_name:
        file_name = f'untitled_{time()}_{randint(0, 100)}'

    # 去除非法字符
    charset = charset or 'utf-8'
    return unquote(file_name, charset)
