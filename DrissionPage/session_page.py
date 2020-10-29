# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   session_page.py
"""
import re
from os import path as os_PATH
from pathlib import Path
from random import randint
from re import search as re_SEARCH
from re import sub as re_SUB
from time import time, sleep
from typing import Union, List
from urllib import parse
from urllib.parse import urlparse, quote

from requests_html import HTMLSession, HTMLResponse, Element

from .common import get_loc_from_str, translate_loc_to_xpath, get_available_file_name
from .config import OptionsManager
from .session_element import SessionElement, execute_session_find


class SessionPage(object):
    """SessionPage封装了页面操作的常用功能，使用requests_html来获取、解析网页。"""

    def __init__(self, session: HTMLSession, timeout: float = 10):
        """初始化函数"""
        self._session = session
        self.timeout = timeout
        self._url = None
        self._url_available = None
        self._response = None

    @property
    def session(self) -> HTMLSession:
        """返回session对象"""
        return self._session

    @property
    def response(self) -> HTMLResponse:
        """返回访问url得到的response对象"""
        return self._response

    @property
    def url(self) -> str:
        """返回当前访问url"""
        return self._url

    @property
    def url_available(self) -> bool:
        """返回当前访问的url有效性"""
        return self._url_available

    @property
    def cookies(self) -> dict:
        """返回session的cookies"""
        return self.session.cookies.get_dict()

    @property
    def title(self) -> str:
        """返回网页title"""
        return self.ele(('css selector', 'title')).text

    @property
    def html(self) -> str:
        """返回页面html文本"""
        return self.response.html.html

    def ele(self,
            loc_or_ele: Union[tuple, str, SessionElement, Element],
            mode: str = None,
            show_errmsg: bool = False) -> Union[SessionElement, List[SessionElement], None]:
        """返回页面中符合条件的元素，默认返回第一个                                                          \n
        示例：                                                                                           \n
        - 接收到元素对象时：                                                                              \n
            返回SessionElement对象                                                                        \n
        - 用loc元组查找：                                                                                 \n
            ele.ele((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的子元素                       \n
        - 用查询字符串查找：                                                                               \n
            查找方式：属性、tag name和属性、文本、xpath、css selector                                        \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                          \n
            page.ele('@class:ele_class')                 - 返回第一个class含有ele_class的元素              \n
            page.ele('@name=ele_name')                   - 返回第一个name等于ele_name的元素                \n
            page.ele('@placeholder')                     - 返回第一个带placeholder属性的元素               \n
            page.ele('tag:p')                            - 返回第一个<p>元素                              \n
            page.ele('tag:div@class:ele_class')          - 返回第一个class含有ele_class的div元素           \n
            page.ele('tag:div@class=ele_class')          - 返回第一个class等于ele_class的div元素           \n
            page.ele('tag:div@text():some_text')         - 返回第一个文本含有some_text的div元素             \n
            page.ele('tag:div@text()=some_text')         - 返回第一个文本等于some_text的div元素             \n
            page.ele('text:some_text')                   - 返回第一个文本含有some_text的元素                \n
            page.ele('some_text')                        - 返回第一个文本含有some_text的元素（等价于上一行）  \n
            page.ele('text=some_text')                   - 返回第一个文本等于some_text的元素                \n
            page.ele('xpath://div[@class="ele_class"]')  - 返回第一个符合xpath的元素                        \n
            page.ele('css:div.ele_class')                - 返回第一个符合css selector的元素                 \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param mode: 'single' 或 'all‘，对应查找一个或全部
        :param show_errmsg: 出现异常时是否打印信息
        :return: SessionElement对象
        """
        if isinstance(loc_or_ele, str):
            loc_or_ele = get_loc_from_str(loc_or_ele)
            if loc_or_ele[0] == 'xpath' and not loc_or_ele[1].startswith('/'):
                loc_or_ele = 'xpath', f'//{loc_or_ele[1]}'
        elif isinstance(loc_or_ele, tuple) and len(loc_or_ele) == 2:
            loc_or_ele = translate_loc_to_xpath(loc_or_ele)
            if loc_or_ele[0] == 'xpath' and not loc_or_ele[1].startswith('/'):
                loc_or_ele = 'xpath', f'//{loc_or_ele[1]}'
        elif isinstance(loc_or_ele, SessionElement):
            return loc_or_ele
        elif isinstance(loc_or_ele, Element):
            return SessionElement(loc_or_ele)
        else:
            raise ValueError('Argument loc_or_str can only be tuple, str, SessionElement, Element.')
        return execute_session_find(self.response.html, loc_or_ele, mode, show_errmsg)
        # return execute_session_find(self, loc_or_ele, mode, show_errmsg)

    def eles(self, loc_or_str: Union[tuple, str], show_errmsg: bool = False) -> List[SessionElement]:
        """返回页面中所有符合条件的元素                                                                    \n
        示例：                                                                                          \n
        - 用loc元组查找：                                                                                \n
            page.eles((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的元素                     \n
        - 用查询字符串查找：                                                                              \n
            查找方式：属性、tag name和属性、文本、xpath、css selector                                       \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                         \n
            page.eles('@class:ele_class')                 - 返回所有class含有ele_class的元素              \n
            page.eles('@name=ele_name')                   - 返回所有name等于ele_name的元素                \n
            page.eles('@placeholder')                     - 返回所有带placeholder属性的元素               \n
            page.eles('tag:p')                            - 返回所有<p>元素                              \n
            page.eles('tag:div@class:ele_class')          - 返回所有class含有ele_class的div元素           \n
            page.eles('tag:div@class=ele_class')          - 返回所有class等于ele_class的div元素           \n
            page.eles('tag:div@text():some_text')         - 返回所有文本含有some_text的div元素             \n
            page.eles('tag:div@text()=some_text')         - 返回所有文本等于some_text的div元素             \n
            page.eles('text:some_text')                   - 返回所有文本含有some_text的元素                \n
            page.eles('some_text')                        - 返回所有文本含有some_text的元素（等价于上一行）  \n
            page.eles('text=some_text')                   - 返回所有文本等于some_text的元素                \n
            page.eles('xpath://div[@class="ele_class"]')  - 返回所有符合xpath的元素                        \n
            page.eles('css:div.ele_class')                - 返回所有符合css selector的元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param show_errmsg: 出现异常时是否打印信息
        :return: SessionElement对象组成的列表
        """
        if not isinstance(loc_or_str, (tuple, str)):
            raise TypeError('Type of loc_or_str can only be tuple or str.')
        return self.ele(loc_or_str, mode='all', show_errmsg=True)

    def _try_to_get(self,
                    to_url: str,
                    times: int = 0,
                    interval: float = 1,
                    show_errmsg: bool = False,
                    **kwargs) -> HTMLResponse:
        """尝试连接，重试若干次                            \n
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :param kwargs: 连接参数
        :return: HTMLResponse对象
        """
        r = self._make_response(to_url, show_errmsg=show_errmsg, **kwargs)[0]
        while times and (not r or r.content == b''):
            if r is not None and r.status_code in (403, 404):
                break
            print('重试', to_url)
            sleep(interval)
            r = self._make_response(to_url, show_errmsg=show_errmsg, **kwargs)[0]
            times -= 1
        return r

    def get(self,
            url: str,
            go_anyway: bool = False,
            show_errmsg: bool = False,
            retry: int = 0,
            interval: float = 1,
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
        to_url = quote(url, safe='/:&?=%;#@+')
        if not url or (not go_anyway and self.url == to_url):
            return
        self._url = to_url
        self._response = self._try_to_get(to_url, times=retry, interval=interval, show_errmsg=show_errmsg, **kwargs)
        if self._response is None:
            self._url_available = False
        else:
            if self._response.ok:
                self._url_available = True
            else:
                if show_errmsg:
                    raise ConnectionError(f'Status code: {self._response.status_code}.')
                self._url_available = False
        return self._url_available

    def post(self,
             url: str,
             data: dict = None,
             go_anyway: bool = True,
             show_errmsg: bool = False,
             **kwargs) -> Union[bool, None]:
        """用post方式跳转到url                                 \n
        :param url: 目标url
        :param data: 提交的数据
        :param go_anyway: 若目标url与当前url一致，是否强制跳转
        :param show_errmsg: 是否显示和抛出异常
        :param kwargs: 连接参数
        :return: url是否可用
        """
        to_url = quote(url, safe='/:&?=%;#@')
        if not url or (not go_anyway and self._url == to_url):
            return
        self._url = to_url
        self._response = self._make_response(to_url, mode='post', data=data, show_errmsg=show_errmsg, **kwargs)[0]
        if self._response is None:
            self._url_available = False
        else:
            if self._response.ok:
                self._url_available = True
            else:
                if show_errmsg:
                    raise ConnectionError(f'Status code: {self._response.status_code}.')
                self._url_available = False
        return self._url_available

    def download(self,
                 file_url: str,
                 goal_path: str = None,
                 rename: str = None,
                 file_exists: str = 'rename',
                 post_data: dict = None,
                 show_msg: bool = False,
                 show_errmsg: bool = False,
                 **kwargs) -> tuple:
        """下载一个文件                                                                   \n
        :param file_url: 文件url
        :param goal_path: 存放路径
        :param rename: 重命名文件，可不写扩展名
        :param file_exists: 若存在同名文件，可选择 'rename', 'overwrite', 'skip' 方式处理
        :param show_msg: 是否显示下载信息
        :param show_errmsg: 是否抛出和显示异常
        :param kwargs: 连接参数
        :return: 下载是否成功（bool）和状态信息（成功时信息为文件路径）的元组
        """
        # 生成的response不写入self._response，是临时的
        goal_path = goal_path or OptionsManager().get_value('paths', 'global_tmp_path')
        if not goal_path:
            raise IOError('No path specified.')

        kwargs['stream'] = True
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 20

        if not post_data:
            r, info = self._make_response(file_url, mode='get', show_errmsg=show_errmsg, **kwargs)
        else:
            r, info = self._make_response(file_url, mode='post', data=post_data, show_errmsg=show_errmsg, **kwargs)
        if r is None:
            if show_msg:
                print(info)
            return False, info
        if not r.ok:
            if show_errmsg:
                raise ConnectionError(f'Status code: {r.status_code}.')
            return False, f'Status code: {r.status_code}.'

        # -------------------获取文件名-------------------
        file_name = ''
        content_disposition = tuple(x for x in r.headers if x.lower() == 'content-disposition')
        if content_disposition:  # header里有文件名，则使用它
            file_name = r.headers[content_disposition[0]].encode('ISO-8859-1').decode('utf-8')
            file_name = re.search(r'filename *= *"?([^";]+)', file_name)
            if file_name:
                file_name = file_name.group(1)
            if file_name[0] == file_name[-1] == "'":
                file_name = file_name.strip("'")
        if not file_name and os_PATH.basename(file_url):  # 在url里获取文件名
            file_name = os_PATH.basename(file_url).split("?")[0]
        if not file_name:  # 找不到则用时间和随机数生成文件名
            file_name = f'untitled_{time()}_{randint(0, 100)}'
        file_name = re_SUB(r'[\\/*:|<>?"]', '', file_name).strip()  # 去除非法字符
        file_name = parse.unquote(file_name)

        # -------------------重命名文件名-------------------
        if rename:  # 重命名文件，不改变扩展名
            rename = re_SUB(r'[\\/*:|<>?"]', '', rename).strip()
            ext_name = file_name.split('.')[-1]
            if '.' in rename or ext_name == file_name:
                full_name = rename
            else:
                full_name = f'{rename}.{ext_name}'
        else:
            full_name = file_name

        # -------------------生成路径-------------------
        goal_Path = Path(goal_path)
        goal_path = ''
        for key, i in enumerate(goal_Path.parts):  # 去除路径中的非法字符
            goal_path += goal_Path.drive if key == 0 and goal_Path.drive else re_SUB(r'[*:|<>?"]', '', i).strip()
            goal_path += '\\' if i != '\\' and key < len(goal_Path.parts) - 1 else ''
        goal_Path = Path(goal_path)
        goal_Path.mkdir(parents=True, exist_ok=True)
        goal_path = goal_Path.absolute()
        full_path = Path(f'{goal_path}\\{full_name}')

        if full_path.exists():
            if file_exists == 'skip':
                return False, 'A file with the same name already exists.'
            elif file_exists == 'overwrite':
                pass
            elif file_exists == 'rename':
                full_name = get_available_file_name(goal_path, full_name)
                full_path = Path(f'{goal_path}\\{full_name}')
            else:
                raise ValueError("Argument file_exists can only be 'skip', 'overwrite', 'rename'.")

        # -------------------打印要下载的文件-------------------
        if show_msg:
            print(full_name if file_name == full_name else f'{file_name} -> {full_name}')
            print(f'Downloading to: {goal_path}')

        # -------------------开始下载-------------------
        # 获取远程文件大小
        content_length = tuple(x for x in r.headers if x.lower() == 'content-length')
        file_size = int(r.headers[content_length]) if content_length else None
        downloaded_size, download_status = 0, False  # 已下载文件大小和下载状态
        try:
            with open(str(full_path), 'wb') as tmpFile:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        tmpFile.write(chunk)
                        if show_msg and file_size:  # 如表头有返回文件大小，显示进度
                            downloaded_size += 1024
                            rate = downloaded_size / file_size if downloaded_size < file_size else 1
                            print('\r {:.0%} '.format(rate), end="")
        except Exception as e:
            if show_errmsg:
                raise ConnectionError(e)
            download_status, info = False, f'Download failed.\n{e}'
        else:
            if full_path.stat().st_size == 0:
                if show_errmsg:
                    raise ValueError('File size is 0.')
                download_status, info = False, 'File size is 0.'
            else:
                download_status, info = True, 'Success.'
        finally:
            if not download_status and full_path.exists():
                full_path.unlink()  # 删除下载出错文件
            r.close()

        # -------------------显示并返回值-------------------
        if show_msg:
            print(info)
        info = f'{goal_path}\\{full_name}' if download_status else info
        return download_status, info

    def _make_response(self,
                       url: str,
                       mode: str = 'get',
                       data: dict = None,
                       show_errmsg: bool = False,
                       **kwargs) -> tuple:
        """生成response对象                     \n
        :param url: 目标url
        :param mode: 'get', 'post' 中选择
        :param data: post方式要提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param kwargs: 其它参数
        :return: tuple，第一位为Response或None，第二位为出错信息或'Sussess'
        """
        if mode not in ['get', 'post']:
            raise ValueError("Argument mode can only be 'get' or 'post'.")
        url = quote(url, safe='/:&?=%;#@+')

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
            headers = dict(r.headers)
            content_type = tuple(x for x in headers if x.lower() == 'content-type')
            stream = tuple(x for x in kwargs if x.lower() == 'stream')
            not_stream = (not stream or not kwargs[stream[0]]) and not self.session.stream
            charset = None
            if not content_type or 'charset' not in headers[content_type[0]].lower():
                if not_stream:
                    re_result = re_SEARCH(r'<meta.*?charset=[ \'"]*([^"\' />]+).*?>',
                                          r.iter_content(chunk_size=512).__next__().decode())
                    try:
                        charset = re_result.group(1)
                    except:
                        charset = r.apparent_encoding
            else:
                charset = headers[content_type[0]].split('=')[1]

            if not_stream:  # 加载网页时修复编码
                r._content = r.content.replace(b'\x08', b'\\b')  # 避免存在退格符导致乱码或解析出错
                r.html.encoding = r.encoding  # 修复requests_html丢失编码方式的bug
            if charset:
                r.encoding = charset
            return r, 'Success'
