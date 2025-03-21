# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from pathlib import Path
from re import search, DOTALL
from time import sleep
from urllib.parse import urlparse

from requests import Response
from requests.structures import CaseInsensitiveDict
from tldextract import TLDExtract

from .._base.base import BasePage
from .._elements.session_element import SessionElement, make_session_ele
from .._functions.cookies import cookie_to_dict, CookiesList
from .._functions.settings import Settings as _S
from .._functions.web import format_headers
from .._units.setter import SessionPageSetter


class SessionPage(BasePage):
    def __init__(self, session_or_options=None, timeout=None):
        super().__init__()
        self._response = None
        self._set = None
        self._encoding = None
        self._type = 'SessionPage'
        self._page = self
        self._set_session_options(session_or_options)
        self._s_set_runtime_settings()
        if timeout is not None:  # 即将废弃
            self._timeout = timeout
        if not self._session:
            self._create_session()

    def __repr__(self):
        return f'<SessionPage url={self.url}>'

    def _s_set_runtime_settings(self):
        self._timeout = self._session_options.timeout
        self._download_path = str(Path(self._session_options.download_path or '.').absolute())
        self.retry_times = self._session_options.retry_times
        self.retry_interval = self._session_options.retry_interval

    def __call__(self, locator, index=1, timeout=None):
        return self.ele(locator, index=index)

    # -----------------共有属性和方法-------------------
    @property
    def title(self):
        ele = self._ele('xpath://title', raise_err=False)
        return ele.text if ele else None

    @property
    def url(self):
        return self._url

    @property
    def _session_url(self):
        return self._url

    @property
    def raw_data(self):
        return self.response.content if self.response else b''

    @property
    def html(self):
        return self.response.text if self.response else ''

    @property
    def json(self):
        try:
            return self.response.json()
        except Exception:
            return None

    @property
    def user_agent(self):
        return self._headers.get('user-agent', '')

    @property
    def session(self):
        return self._session

    @property
    def response(self):
        return self._response

    @property
    def encoding(self):
        return self._encoding

    @property
    def set(self):
        if self._set is None:
            self._set = SessionPageSetter(self)
        return self._set

    @property
    def timeout(self):
        return self._timeout

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
        retry, interval, is_file = self._before_connect(url.replace('file:///', '', 1), retry, interval)
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
        return self._ele(locator, index=index, method='ele()')

    def eles(self, locator, timeout=None):
        return self._ele(locator, index=None)

    def s_ele(self, locator=None, index=1):
        return make_session_ele(self) if locator is None else self._ele(locator, index=index, method='s_ele()')

    def s_eles(self, locator):
        return self._ele(locator, index=None)

    def _find_elements(self, locator, timeout, index=1, relative=True, raise_err=None):
        return locator if isinstance(locator, SessionElement) else make_session_ele(self, locator, index=index)

    def cookies(self, all_domains=False, all_info=False):
        if all_domains:
            cookies = self.session.cookies
        else:
            if self.url:
                ex_url = TLDExtract(
                    suffix_list_urls=["https://publicsuffix.org/list/public_suffix_list.dat",
                                      f"file:///{_S.suffixes_list}"]).extract_str(self._session_url)
                domain = f'{ex_url.domain}.{ex_url.suffix}' if ex_url.suffix else ex_url.domain
                cookies = tuple(c for c in self.session.cookies if domain in c.domain or c.domain == '')
            else:
                cookies = tuple(c for c in self.session.cookies)

        if all_info:
            r = CookiesList()
            for c in cookies:
                r.append(cookie_to_dict(c))
        else:
            r = CookiesList()
            for c in cookies:
                c = cookie_to_dict(c)
                r.append({'name': c['name'], 'value': c['value'], 'domain': c['domain']})
        return r

    def close(self):
        self._session.close()
        if self._response is not None:
            self._response.close()

    def _s_connect(self, url, mode, show_errmsg=False, retry=None, interval=None, **kwargs):
        retry, interval, is_file = self._before_connect(url, retry, interval)
        self._response = self._make_response(self._url, mode, retry, interval, show_errmsg, **kwargs)

        if self._response is None:
            self._url_available = False

        else:
            if self._response.ok:
                self._url_available = True

            else:
                if show_errmsg:
                    raise ConnectionError(_S._lang.STATUS_CODE_, self._response.status_code)
                self._url_available = False

        return self._url_available

    def _make_response(self, url, mode='get', retry=None, interval=None, show_errmsg=False, **kwargs):
        kwargs = CaseInsensitiveDict(kwargs)
        if 'headers' in kwargs:
            kwargs['headers'] = CaseInsensitiveDict(format_headers(kwargs['headers']))
        else:
            kwargs['headers'] = CaseInsensitiveDict()

        # 设置referer和host值
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        scheme = parsed_url.scheme
        if not check_headers(kwargs['headers'], self._headers, 'Referer'):
            kwargs['headers']['Referer'] = self.url if self.url else f'{scheme}://{hostname}'
        elif not kwargs['headers']['Referer']:
            kwargs['headers'].pop('Referer')
        if not check_headers(kwargs['headers'], self._headers, 'Host'):
            kwargs['headers']['Host'] = hostname
        elif not kwargs['headers']['Host']:
            kwargs['headers'].pop('Host')
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
                        return r
                    return set_charset(r)

            except Exception as e:
                err = e

            # if r and r.status_code in (403, 404):
            #     break

            if i < retry:
                sleep(interval)
                if show_errmsg:
                    print(f'{_S._lang.RETRY} {url}')

        if show_errmsg:
            if err:
                raise err
            elif r is not None:
                raise (ConnectionError(_S._lang.join(_S._lang.STATUS_CODE_, r.status_code)) if r.content
                       else ConnectionError(_S._lang.join(_S._lang.CONTENT_IS_EMPTY)))
            else:
                raise ConnectionError(_S._lang.join(_S._lang.CONNECT_ERR))

        else:
            if r is not None:
                return r if r.content else None
            else:
                return None


def check_headers(kwargs, headers, arg):
    return arg in kwargs or arg in headers


def set_charset(response):
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
