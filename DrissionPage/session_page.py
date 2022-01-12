# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   session_page.py
"""
from os import path as os_PATH, sep
from pathlib import Path
from random import randint
from re import search, sub
from time import time, sleep
from typing import Union, List, Tuple
from urllib.parse import urlparse, quote, unquote

from requests import Session, Response
from tldextract import extract

from .base import BasePage
from .common import get_usable_path, make_valid_name
from .config import _cookie_to_dict
from .session_element import SessionElement, make_session_ele


class SessionPage(BasePage):
    """SessionPage封装了页面操作的常用功能，使用requests来获取、解析网页"""

    def __init__(self, session: Session, timeout: float = 10):
        """初始化函数"""
        super().__init__(timeout)
        self._session = session
        self._response = None

    def __call__(self, loc_or_str: Union[Tuple[str, str], str, SessionElement], timeout=None) \
            -> Union[SessionElement, List[SessionElement], str]:
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
            go_anyway: bool = False,
            show_errmsg: bool = False,
            retry: int = None,
            interval: float = None,
            **kwargs) -> Union[bool, None]:
        """用get方式跳转到url                                 \n
        :param url: 目标url
        :param go_anyway: 若目标url与当前url一致，是否强制跳转
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        to_url = quote(url, safe='/:&?=%;#@+!')
        retry = int(retry) if retry is not None else int(self.retry_times)
        interval = int(interval) if interval is not None else int(self.retry_interval)

        if not url or (not go_anyway and self.url == to_url):
            return

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

    def ele(self, loc_or_ele: Union[Tuple[str, str], str, SessionElement], timeout: float = None) \
            -> Union[SessionElement, List[SessionElement], str, None]:
        """返回页面中符合条件的第一个元素、属性或节点文本                            \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_ele)

    def eles(self, loc_or_str: Union[Tuple[str, str], str], timeout: float = None) -> List[SessionElement]:
        """返回页面中所有符合条件的元素、属性或节点文本                          \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, single=False)

    def s_ele(self, loc_or_ele: Union[Tuple[str, str], str, SessionElement] = None):
        """返回页面中符合条件的第一个元素、属性或节点文本                          \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self.html) if loc_or_ele is None else self._ele(loc_or_ele)

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = None):
        """返回页面中符合条件的所有元素、属性或节点文本                              \n
        :param loc_or_str: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_str, single=False)

    def _ele(self,
             loc_or_ele: Union[Tuple[str, str], str, SessionElement],
             timeout: float = None,
             single: bool = True) -> Union[SessionElement, List[SessionElement], str, None]:
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
                        **kwargs) -> Response:
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
                print(f'重试 {to_url}')

        if not r and show_errmsg:
            raise err if err is not None else ConnectionError('连接异常。')

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

    def post(self,
             url: str,
             data: Union[dict, str] = None,
             go_anyway: bool = True,
             show_errmsg: bool = False,
             retry: int = None,
             interval: float = None,
             **kwargs) -> Union[bool, None]:
        """用post方式跳转到url                                 \n
        :param url: 目标url
        :param data: 提交的数据
        :param go_anyway: 若目标url与当前url一致，是否强制跳转
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        to_url = quote(url, safe='/:&?=%;#@+!')
        retry = int(retry) if retry is not None else int(self.retry_times)
        interval = int(interval) if interval is not None else int(self.retry_interval)

        if not url or (not go_anyway and self._url == to_url):
            return

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

    def download(self,
                 file_url: str,
                 goal_path: str,
                 rename: str = None,
                 file_exists: str = 'rename',
                 post_data: Union[str, dict] = None,
                 show_msg: bool = False,
                 show_errmsg: bool = False,
                 retry: int = None,
                 interval: float = None,
                 **kwargs) -> tuple:
        """下载一个文件                                                                   \n
        :param file_url: 文件url
        :param goal_path: 存放路径
        :param rename: 重命名文件，可不写扩展名
        :param file_exists: 若存在同名文件，可选择 'rename', 'overwrite', 'skip' 方式处理
        :param post_data: post方式的数据，这个参数不为None时自动转成post方式
        :param show_msg: 是否显示下载信息
        :param show_errmsg: 是否抛出和显示异常
        :param retry: 重试次数
        :param interval: 重试间隔时间
        :param kwargs: 连接参数
        :return: 下载是否成功（bool）和状态信息（成功时信息为文件路径）的元组，跳过时第一位为None
        """
        if file_exists == 'skip' and Path(f'{goal_path}{sep}{rename}').exists():
            if show_msg:
                print(f'{file_url}\n{goal_path}{sep}{rename}\n存在同名文件，已跳过。\n')
            return None, '已跳过，因存在同名文件。'

        def do() -> tuple:
            kwargs['stream'] = True
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 20

            # 生成临时的response
            mode = 'post' if post_data is not None else 'get'
            r, info = self._make_response(file_url, mode=mode, data=post_data, show_errmsg=show_errmsg, **kwargs)

            if r is None:
                if show_msg:
                    print(info)
                return False, info

            if not r.ok:
                if show_errmsg:
                    raise ConnectionError(f'连接状态码：{r.status_code}')
                return False, f'状态码：{r.status_code}'

            # -------------------获取文件名-------------------
            file_name = _get_download_file_name(file_url, r)

            # -------------------重命名，不改变扩展名-------------------
            if rename:
                ext_name = file_name.split('.')[-1]
                if '.' in rename or ext_name == file_name:  # 新文件名带后缀或原文件名没有后缀
                    full_name = rename
                else:
                    full_name = f'{rename}.{ext_name}'
            else:
                full_name = file_name

            full_name = make_valid_name(full_name)

            # -------------------生成路径-------------------
            goal_Path = Path(goal_path)
            skip = False

            # 按windows规则去除路径中的非法字符
            goal = goal_Path.anchor + sub(r'[*:|<>?"]', '', goal_path.lstrip(goal_Path.anchor)).strip()
            Path(goal).absolute().mkdir(parents=True, exist_ok=True)
            full_path = Path(f'{goal}{sep}{full_name}')

            if full_path.exists():
                if file_exists == 'rename':
                    full_path = get_usable_path(f'{goal}{sep}{full_name}')
                    full_name = full_path.name

                elif file_exists == 'skip':
                    skip = True

                elif file_exists == 'overwrite':
                    pass

                else:
                    raise ValueError("file_exists参数只能是'skip'、'overwrite' 或 'rename'。")

            # -------------------打印要下载的文件-------------------
            if show_msg:
                print(file_url)
                print(full_name if file_name == full_name else f'{file_name} -> {full_name}')
                print(f'正在下载到：{goal}')
                if skip:
                    print('存在同名文件，已跳过。\n')

            # -------------------开始下载-------------------
            if skip:
                return None, '已跳过，因存在同名文件。'

            # 获取远程文件大小
            content_length = r.headers.get('content-length')
            file_size = int(content_length) if content_length else None

            # 已下载文件大小和下载状态
            downloaded_size, download_status = 0, False

            try:
                with open(str(full_path), 'wb') as tmpFile:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            tmpFile.write(chunk)

                            # 如表头有返回文件大小，显示进度
                            if show_msg and file_size:
                                downloaded_size += 1024
                                rate = downloaded_size / file_size if downloaded_size < file_size else 1
                                print('\r{:.0%} '.format(rate), end="")

            except Exception as e:
                if show_errmsg:
                    raise ConnectionError(e)
                download_status, info = False, f'下载失败。\n{e}'

            else:
                if full_path.stat().st_size == 0:
                    if show_errmsg:
                        raise ValueError('文件大小为0。')
                    download_status, info = False, '文件大小为0。'

                else:
                    download_status, info = True, str(full_path)

            finally:
                if download_status is False and full_path.exists():
                    full_path.unlink()  # 删除下载出错文件
                r.close()

            # -------------------显示并返回值-------------------
            if show_msg:
                print(info, '\n')

            info = f'{goal}{sep}{full_name}' if download_status else info
            return download_status, info

        retry_times = retry or self.retry_times
        retry_interval = interval or self.retry_interval
        result = do()

        if result[0] is False:  # 第一位为None表示跳过的情况
            for i in range(retry_times):
                sleep(retry_interval)
                if show_msg:
                    print(f'\n重试 {file_url}')

                result = do()
                if result[0] is not False:
                    break

        return result

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
