# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from re import search
from time import sleep
from urllib.parse import urlparse

from DownloadKit import DownloadKit
from requests import Session, Response
from requests.structures import CaseInsensitiveDict
from tldextract import extract

from .base import BasePage
from .config import SessionOptions, cookies_to_tuple, cookie_to_dict
from .session_element import SessionElement, make_session_ele


class SessionPage(BasePage):
    """SessionPage封装了页面操作的常用功能，使用requests来获取、解析网页"""

    def __init__(self, session_or_options=None, timeout=10):
        """初始化                                                     \n
        :param session_or_options: Session对象或SessionOptions对象
        :param timeout: 连接超时时间
        """
        super().__init__(timeout)
        self._response = None
        self._create_session(session_or_options)

    def _create_session(self, Session_or_Options):
        """创建内建Session对象
        :param Session_or_Options: Session对象或SessionOptions对象
        :return: None
        """
        if Session_or_Options is None or isinstance(Session_or_Options, SessionOptions):
            options = Session_or_Options or SessionOptions()
            self._set_session(options.as_dict())
        elif isinstance(Session_or_Options, Session):
            self._session = Session_or_Options

    def _set_session(self, data):
        """根据传入字典对session进行设置    \n
        :param data: session配置字典
        :return: None
        """
        self._session = Session()

        if 'headers' in data:
            self._session.headers = CaseInsensitiveDict(data['headers'])
        if 'cookies' in data:
            self.set_cookies(data['cookies'])

        attrs = ['auth', 'proxies', 'hooks', 'params', 'verify',
                 'cert', 'stream', 'trust_env', 'max_redirects']  # , 'adapters'
        for i in attrs:
            if i in data:
                self._session.__setattr__(i, data[i])

    def set_cookies(self, cookies):
        cookies = cookies_to_tuple(cookies)
        for cookie in cookies:
            if cookie['value'] is None:
                cookie['value'] = ''

            kwargs = {x: cookie[x] for x in cookie
                      if x.lower() in ('version', 'port', 'domain', 'path', 'secure',
                                       'expires', 'discard', 'comment', 'comment_url', 'rest')}

            if 'expiry' in cookie:
                kwargs['expires'] = cookie['expiry']

            self.session.cookies.set(cookie['name'], cookie['value'], **kwargs)

    def set_headers(self, headers):
        """设置通用的headers，设置的headers值回逐个覆盖原有的，不会清理原来的        \n
        :param headers: dict形式的headers
        :return: None
        """
        headers = CaseInsensitiveDict(headers)
        for i in headers:
            self.session.headers[i] = headers[i]

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素                                                  \n
        例：ele2 = ele1('@id=ele_id')                                     \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性文本
        """
        return self.ele(loc_or_str)

    # -----------------共有属性和方法-------------------
    @property
    def url(self):
        """返回当前访问url"""
        return self._url

    @property
    def html(self):
        """返回页面的html文本"""
        return self.response.text if self.response else ''

    @property
    def json(self):
        """当返回内容是json格式时，返回对应的字典，非json格式时返回None"""
        try:
            return self.response.json()
        except Exception:
            return None

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        """用get方式跳转到url                                 \n
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param timeout: 连接超时时间（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        return self._s_connect(url, 'get', None, show_errmsg, retry, interval, **kwargs)

    def ele(self, loc_or_ele, timeout=None):
        """返回页面中符合条件的第一个元素、属性或节点文本                            \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_ele)

    def eles(self, loc_or_str, timeout=None):
        """返回页面中所有符合条件的元素、属性或节点文本                          \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和DriverElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, single=False)

    def s_ele(self, loc_or_ele=None):
        """返回页面中符合条件的第一个元素、属性或节点文本                          \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self.html) if loc_or_ele is None else self._ele(loc_or_ele)

    def s_eles(self, loc_or_str=None):
        """返回页面中符合条件的所有元素、属性或节点文本                              \n
        :param loc_or_str: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return self._ele(loc_or_str, single=False)

    def _ele(self, loc_or_ele, timeout=None, single=True):
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个                                           \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和父类对应
        :param single: True则返回第一个，False则返回全部
        :return: SessionElement对象
        """
        return loc_or_ele if isinstance(loc_or_ele, SessionElement) else make_session_ele(self, loc_or_ele, single)

    def get_cookies(self, as_dict=False, all_domains=False):
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
            return [cookie_to_dict(cookie) for cookie in cookies]

    # ----------------session独有属性和方法-----------------------
    @property
    def session(self):
        """返回session对象"""
        return self._session

    @property
    def response(self):
        """返回访问url得到的response对象"""
        return self._response

    @property
    def download(self):
        """返回下载器对象"""
        if not hasattr(self, '_download_kit'):
            self._download_kit = DownloadKit(session=self)

        return self._download_kit

    def post(self, url, data=None, show_errmsg=False, retry=None, interval=None, **kwargs):
        """用post方式跳转到url                                 \n
        :param url: 目标url
        :param data: 提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        return self._s_connect(url, 'post', data, show_errmsg, retry, interval, **kwargs)

    def _s_connect(self, url, mode, data=None, show_errmsg=False, retry=None, interval=None, **kwargs):
        """执行get或post连接                                 \n
        :param url: 目标url
        :param mode: 'get' 或 'post'
        :param data: 提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        retry, interval = self._before_connect(url, retry, interval)
        self._response, info = self._make_response(self._url, mode, data, retry, interval, show_errmsg, **kwargs)

        if self._response is None:
            self._url_available = False

        else:
            if self._response.ok:
                self._url_available = True

            else:
                if show_errmsg:
                    raise ConnectionError(f'状态码：{self._response.status_code}.')
                self._url_available = False

        return self._url_available

    def _make_response(self, url, mode='get', data=None, retry=None, interval=None, show_errmsg=False, **kwargs):
        """生成Response对象                                                    \n
        :param url: 目标url
        :param mode: 'get' 或 'post'
        :param data: post方式要提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param kwargs: 其它参数
        :return: tuple，第一位为Response或None，第二位为出错信息或'Success'
        """
        kwargs = CaseInsensitiveDict(kwargs)
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        else:
            kwargs['headers'] = CaseInsensitiveDict(kwargs['headers'])

        # 设置referer和host值
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        scheme = parsed_url.scheme
        if not check_headers(kwargs, self.session.headers, 'Referer'):
            kwargs['headers']['Referer'] = self.url if self.url else f'{scheme}://{hostname}'
        if 'Host' not in kwargs['headers']:
            kwargs['headers']['Host'] = hostname

        if not check_headers(kwargs, self.session.headers, 'timeout'):
            kwargs['timeout'] = self.timeout

        if 'allow_redirects' not in kwargs:
            kwargs['allow_redirects'] = False

        r = err = None
        retry = retry if retry is not None else self.retry_times
        interval = interval if interval is not None else self.retry_interval
        for i in range(retry + 1):
            try:
                if mode == 'get':
                    r = self.session.get(url, **kwargs)
                elif mode == 'post':
                    r = self.session.post(url, data=data, **kwargs)

                if r:
                    return set_charset(r), 'Success'

            except Exception as e:
                err = e

            # if r and r.status_code in (403, 404):
            #     break

            if i < retry:
                sleep(interval)
                if show_errmsg:
                    print(f'重试 {url}')

        if r is None:
            if show_errmsg:
                if err:
                    raise err
                else:
                    raise ConnectionError('连接失败')
            return None, '连接失败' if err is None else err

        if not r.ok:
            if show_errmsg:
                raise ConnectionError(f'状态码：{r.status_code}')
            return r, f'状态码：{r.status_code}'


def check_headers(kwargs, headers, arg) -> bool:
    """检查kwargs或headers中是否有arg所示属性"""
    return arg in kwargs['headers'] or arg in headers


def set_charset(response) -> Response:
    """设置Response对象的编码"""
    # 在headers中获取编码
    content_type = response.headers.get('content-type', '').lower()
    charset = search(r'charset[=: ]*(.*)?[;]', content_type)

    if charset:
        response.encoding = charset.group(1)

    # 在headers中获取不到编码，且如果是网页
    elif content_type.replace(' ', '').startswith('text/html'):
        re_result = search(b'<meta.*?charset=[ \\\'"]*([^"\\\' />]+).*?>', response.content)

        if re_result:
            charset = re_result.group(1).decode()
        else:
            charset = response.apparent_encoding

        response.encoding = charset

    return response
