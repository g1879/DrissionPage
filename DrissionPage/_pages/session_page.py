# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from copy import copy
from pathlib import Path
from re import search, DOTALL
from time import sleep
from urllib.parse import urlparse

from requests import Session, Response
from requests.structures import CaseInsensitiveDict
from tldextract import extract

from .._base.base import BasePage
from .._configs.session_options import SessionOptions
from .._elements.session_element import SessionElement, make_session_ele
from .._functions.web import cookie_to_dict, format_headers
from .._units.setter import SessionPageSetter


class SessionPage(BasePage):
    """SessionPage封装了页面操作的常用功能，使用requests来获取、解析网页"""

    def __init__(self, session_or_options=None, timeout=None):
        """
        :param session_or_options: Session对象或SessionOptions对象
        :param timeout: 连接超时时间（秒），为None时从ini文件读取或默认10
        """
        super(SessionPage, SessionPage).__init__(self)
        self._headers = None
        self._response = None
        self._session = None
        self._set = None
        self._encoding = None
        self._type = 'SessionPage'
        self._page = self
        self._s_set_start_options(session_or_options)
        self._s_set_runtime_settings()
        self._create_session()
        if timeout is not None:
            self.timeout = timeout

    def _s_set_start_options(self, session_or_options):
        """启动配置
        :param session_or_options: Session、SessionOptions对象
        :return: None
        """
        if not session_or_options:
            self._session_options = SessionOptions(session_or_options)

        elif isinstance(session_or_options, SessionOptions):
            self._session_options = session_or_options

        elif isinstance(session_or_options, Session):
            self._session_options = SessionOptions()
            self._session = copy(session_or_options)
            self._headers = self._session.headers
            self._session.headers = None

    def _s_set_runtime_settings(self):
        """设置运行时用到的属性"""
        self._timeout = self._session_options.timeout
        self._download_path = None if self._session_options.download_path is None \
            else str(Path(self._session_options.download_path).absolute())
        self.retry_times = self._session_options.retry_times
        self.retry_interval = self._session_options.retry_interval

    def _create_session(self):
        """创建内建Session对象"""
        if not self._session:
            self._session, self._headers = self._session_options.make_session()

    def __call__(self, locator, index=1, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性文本
        """
        return self.ele(locator, index=index)

    # -----------------共有属性和方法-------------------
    @property
    def title(self):
        """返回网页title"""
        ele = self._ele('xpath://title', raise_err=False)
        return ele.text if ele else None

    @property
    def url(self):
        """返回当前访问url"""
        return self._url

    @property
    def _session_url(self):
        """返回当前访问url"""
        return self._url

    @property
    def raw_data(self):
        """返回页面原始数据"""
        return self.response.content if self.response else b''

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

    @property
    def user_agent(self):
        """返回user agent"""
        return self._headers.get('user-agent', '')

    @property
    def session(self):
        """返回Session对象"""
        return self._session

    @property
    def response(self):
        """返回访问url得到的Response对象"""
        return self._response

    @property
    def encoding(self):
        """返回设置的编码"""
        return self._encoding

    @property
    def set(self):
        """返回用于设置的对象"""
        if self._set is None:
            self._set = SessionPageSetter(self)
        return self._set

    def get(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        """用get方式跳转到url，可输入文件路径
        :param url: 目标url，可指定本地文件路径
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param timeout: 连接超时时间（秒），为None时使用页面对象timeout属性值
        :param kwargs: 连接参数
        :return: url是否可用
        """
        retry, interval, is_file = self._before_connect(url.lstrip('file:///'), retry, interval)
        if is_file:
            with open(self._url, 'rb') as f:
                r = Response()
                r._content = f.read()
                r.status_code = 200
                r.url = self._url
                self._response = r
            return True
        return self._s_connect(self._url, 'get', show_errmsg, retry, interval, **kwargs)

    def post(self, url, show_errmsg=False, retry=None, interval=None, **kwargs):
        """用post方式跳转到url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象timeout属性值
        :param kwargs: 连接参数
        :return: url是否可用
        """
        return self._s_connect(url, 'post', show_errmsg, retry, interval, **kwargs)

    def ele(self, locator, index=1, timeout=None):
        """返回页面中符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本
        """
        return self._ele(locator, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        """返回页面中所有符合条件的元素、属性或节点文本
        :param locator: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和ChromiumElement对应，便于无差别调用
        :return: SessionElement对象或属性、文本组成的列表
        """
        return self._ele(locator, index=None)

    def s_ele(self, locator=None, index=1):
        """返回页面中符合条件的一个元素、属性或节点文本
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param index: 获取第几个，从1开始，可传入负数获取倒数第几个
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self) if locator is None else self._ele(locator, index=index, method='s_ele()')

    def s_eles(self, locator):
        """返回页面中符合条件的所有元素、属性或节点文本
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return self._ele(locator, index=None)

    def _find_elements(self, locator, timeout=None, index=1, relative=True, raise_err=None):
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个
        :param locator: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 不起实际作用，用于和父类对应
        :param index: 第几个结果，从1开始，可传入负数获取倒数第几个，为None返回所有
        :param raise_err: 找不到元素是是否抛出异常，为None时根据全局设置
        :return: SessionElement对象
        """
        return locator if isinstance(locator, SessionElement) else make_session_ele(self, locator, index=index)

    def cookies(self, as_dict=False, all_domains=False, all_info=False):
        """返回cookies
        :param as_dict: 为True时以dict格式返回，为False时返回list且all_info无效
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，False则只返回name、value、domain
        :return: cookies信息
        """
        if all_domains:
            cookies = self.session.cookies
        else:
            if self.url:
                ex_url = extract(self._session_url)
                domain = f'{ex_url.domain}.{ex_url.suffix}' if ex_url.suffix else ex_url.domain

                cookies = tuple(x for x in self.session.cookies if domain in x.domain or x.domain == '')
            else:
                cookies = tuple(x for x in self.session.cookies)

        if as_dict:
            return {x.name: x.value for x in cookies}
        elif all_info:
            return [cookie_to_dict(cookie) for cookie in cookies]
        else:
            r = []
            for c in cookies:
                c = cookie_to_dict(c)
                r.append({'name': c['name'], 'value': c['value'], 'domain': c['domain']})
            return r

    def close(self):
        """关闭Session对象"""
        self._session.close()
        if self._response is not None:
            self._response.close()

    def _s_connect(self, url, mode, show_errmsg=False, retry=None, interval=None, **kwargs):
        """执行get或post连接
        :param url: 目标url
        :param mode: 'get' 或 'post'
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        retry, interval, is_file = self._before_connect(url, retry, interval)
        self._response, info = self._make_response(self._url, mode, retry, interval, show_errmsg, **kwargs)

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

    def _make_response(self, url, mode='get', retry=None, interval=None, show_errmsg=False, **kwargs):
        """生成Response对象
        :param url: 目标url
        :param mode: 'get' 或 'post'
        :param show_errmsg: 是否显示和抛出异常
        :param kwargs: 其它参数
        :return: tuple，第一位为Response或None，第二位为出错信息或 'Success'
        """
        kwargs = CaseInsensitiveDict(kwargs)
        if 'headers' not in kwargs:
            kwargs['headers'] = CaseInsensitiveDict()
        else:
            kwargs['headers'] = CaseInsensitiveDict(format_headers(kwargs['headers']))

        # 设置referer和host值
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        scheme = parsed_url.scheme
        if not check_headers(kwargs['headers'], self._headers, 'Referer'):
            kwargs['headers']['Referer'] = self.url if self.url else f'{scheme}://{hostname}'
        if not check_headers(kwargs['headers'], self._headers, 'Host'):
            kwargs['headers']['Host'] = hostname
        if not check_headers(kwargs, self._headers, 'timeout'):
            kwargs['timeout'] = self.timeout

        h = CaseInsensitiveDict(self._headers)
        for k, v in kwargs['headers'].items():
            h[k] = v
        kwargs['headers'] = h

        r = err = None
        retry = retry if retry is not None else self.retry_times
        interval = interval if interval is not None else self.retry_interval
        for i in range(retry + 1):
            try:
                if mode == 'get':
                    r = self.session.get(url, **kwargs)
                elif mode == 'post':
                    r = self.session.post(url, **kwargs)

                if r and r.content:
                    if self._encoding:
                        r.encoding = self._encoding
                        return r, 'Success'
                    return set_charset(r), 'Success'

            except Exception as e:
                err = e

            # if r and r.status_code in (403, 404):
            #     break

            if i < retry:
                sleep(interval)
                if show_errmsg:
                    print(f'重试 {url}')

        if show_errmsg:
            if err:
                raise err
            elif r is not None:
                raise ConnectionError(f'状态码：{r.status_code}') if r.content else ConnectionError('返回内容为空。')
            else:
                raise ConnectionError('连接失败')

        else:
            if r is not None:
                return (r, f'状态码：{r.status_code}') if r.content else (None, '返回内容为空')
            else:
                return None, '连接失败' if err is None else err

    def __repr__(self):
        return f'<SessionPage url={self.url}>'


def check_headers(kwargs, headers, arg):
    """检查kwargs或headers中是否有arg所示属性"""
    return arg in kwargs or arg in headers


def set_charset(response):
    """设置Response对象的编码"""
    # 在headers中获取编码
    content_type = response.headers.get('content-type', '').lower()
    if not content_type.endswith(';'):
        content_type += ';'
    charset = search(r'charset[=: ]*(.*)?;?', content_type)

    if charset:
        response.encoding = charset.group(1)

    # 在headers中获取不到编码，且如果是网页
    elif content_type.replace(' ', '').startswith('text/html'):
        re_result = search(b'<meta.*?charset=[ \\\'"]*([^"\\\' />]+).*?>', response.content, DOTALL)

        if re_result:
            charset = re_result.group(1).decode()
        else:
            charset = response.apparent_encoding

        response.encoding = charset

    return response
