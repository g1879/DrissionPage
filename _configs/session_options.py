# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from copy import copy
from pathlib import Path

from requests import Session
from requests.structures import CaseInsensitiveDict

from .options_manage import OptionsManager
from .._functions.cookies import cookies_to_tuple, set_session_cookies
from .._functions.settings import Settings as _S
from .._functions.web import format_headers


class SessionOptions(object):

    def __init__(self, read_file=True, ini_path=None):
        self.ini_path = None
        self._download_path = '.'
        self._timeout = 10
        self._del_set = set()  # 记录要从ini文件删除的参数

        if read_file is False:
            ini_path = False
            self.ini_path = None
        elif ini_path:
            ini_path = Path(ini_path).absolute()
            if not ini_path.exists():
                raise FileNotFoundError(_S._lang.join(_S._lang.INI_NOT_FOUND, PATH=ini_path))
            self.ini_path = str(ini_path)
        else:
            self.ini_path = str(Path(__file__).parent / 'configs.ini')
        om = OptionsManager(ini_path)

        self._headers = None
        self._cookies = None
        self._auth = None
        self._proxies = None
        self._hooks = None
        self._params = None
        self._verify = None
        self._cert = None
        self._adapters = None
        self._stream = None
        self._trust_env = None
        self._max_redirects = None

        options = om.session_options
        if options.get('headers', None) is not None:
            self.set_headers(options['headers'])

        if options.get('cookies', None) is not None:
            self.set_cookies(options['cookies'])

        if options.get('auth', None) is not None:
            self._auth = options['auth']

        if options.get('params', None) is not None:
            self._params = options['params']

        if options.get('verify', None) is not None:
            self._verify = options['verify']

        if options.get('cert', None) is not None:
            self._cert = options['cert']

        if options.get('stream', None) is not None:
            self._stream = options['stream']

        if options.get('trust_env', None) is not None:
            self._trust_env = options['trust_env']

        if options.get('max_redirects', None) is not None:
            self._max_redirects = options['max_redirects']

        self.set_proxies(om.proxies.get('http', None), om.proxies.get('https', None))
        self._timeout = om.timeouts.get('base', 10)
        self._download_path = om.paths.get('download_path', '.') or '.'

        others = om.others
        self._retry_times = others.get('retry_times', 3)
        self._retry_interval = others.get('retry_interval', 2)

    def __repr__(self):
        return f'<SessionOptions at {id(self)}>'

    # ===========须独立处理的项开始============
    @property
    def download_path(self):
        return self._download_path

    def set_download_path(self, path):
        self._download_path = '.' if path is None else str(path)
        return self

    @property
    def timeout(self):
        return self._timeout

    def set_timeout(self, second):
        self._timeout = second
        return self

    @property
    def proxies(self):
        if self._proxies is None:
            self._proxies = {}
        return self._proxies

    def set_proxies(self, http=None, https=None):
        self._sets('proxies', {'http': http, 'https': https})
        return self

    @property
    def retry_times(self):
        return self._retry_times

    @property
    def retry_interval(self):
        return self._retry_interval

    def set_retry(self, times=None, interval=None):
        if times is not None:
            self._retry_times = times
        if interval is not None:
            self._retry_interval = interval
        return self

    # ===========须独立处理的项结束============

    @property
    def headers(self):
        if self._headers is None:
            self._headers = {}
        return self._headers

    def set_headers(self, headers):
        if headers is None:
            self._headers = None
            self._del_set.add('headers')
        else:
            headers = format_headers(headers)
            self._headers = {key.lower(): headers[key] for key in headers}
        return self

    def set_a_header(self, name, value):
        if self._headers is None:
            self._headers = {}

        self._headers[name.lower()] = value
        return self

    def remove_a_header(self, name):
        if self._headers is None:
            return self

        self._headers.pop(name.lower(), None)

        return self

    def clear_headers(self):
        self._headers = None
        self._del_set.add('headers')

    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = []
        return self._cookies

    def set_cookies(self, cookies):
        cookies = cookies if cookies is None else list(cookies_to_tuple(cookies))
        self._sets('cookies', cookies)
        return self

    @property
    def auth(self):
        return self._auth

    def set_auth(self, auth):
        self._sets('auth', auth)
        return self

    @property
    def hooks(self):
        if self._hooks is None:
            self._hooks = {}
        return self._hooks

    def set_hooks(self, hooks):
        self._hooks = hooks
        return self

    @property
    def params(self):
        if self._params is None:
            self._params = {}
        return self._params

    def set_params(self, params):
        self._sets('params', params)
        return self

    @property
    def verify(self):
        return self._verify

    def set_verify(self, on_off):
        self._sets('verify', on_off)
        return self

    @property
    def cert(self):
        return self._cert

    def set_cert(self, cert):
        self._sets('cert', cert)
        return self

    @property
    def adapters(self):
        if self._adapters is None:
            self._adapters = []
        return self._adapters

    def add_adapter(self, url, adapter):
        self._adapters.append((url, adapter))
        return self

    @property
    def stream(self):
        return self._stream

    def set_stream(self, on_off):
        self._sets('stream', on_off)
        return self

    @property
    def trust_env(self):
        return self._trust_env

    def set_trust_env(self, on_off):
        self._sets('trust_env', on_off)
        return self

    @property
    def max_redirects(self):
        return self._max_redirects

    def set_max_redirects(self, times):
        self._sets('max_redirects', times)
        return self

    def _sets(self, arg, val):
        if val is None:
            self.__setattr__(f'_{arg}', None)
            self._del_set.add(arg)
        else:
            self.__setattr__(f'_{arg}', val)
            if arg in self._del_set:
                self._del_set.remove(arg)

    def save(self, path=None):
        if path == 'default':
            path = (Path(__file__).parent / 'configs.ini').absolute()

        elif path is None:
            if self.ini_path:
                path = Path(self.ini_path).absolute()
            else:
                path = (Path(__file__).parent / 'configs.ini').absolute()

        else:
            path = Path(path).absolute()

        path = path / 'config.ini' if path.is_dir() else path

        if path.exists():
            om = OptionsManager(path)
        else:
            om = OptionsManager(self.ini_path or (Path(__file__).parent / 'configs.ini'))

        options = session_options_to_dict(self)

        for i in options:
            if i not in ('download_path', 'timeout', 'proxies'):
                om.set_item('session_options', i, options[i])

        om.set_item('paths', 'download_path', self.download_path or '')
        om.set_item('timeouts', 'base', self.timeout)
        om.set_item('proxies', 'http', self.proxies.get('http', ''))
        om.set_item('proxies', 'https', self.proxies.get('https', ''))
        om.set_item('others', 'retry_times', self.retry_times)
        om.set_item('others', 'retry_interval', self.retry_interval)

        for i in self._del_set:
            if i == 'download_path':
                om.set_item('paths', 'download_path', '')
            elif i == 'proxies':
                om.set_item('proxies', 'http', '')
                om.set_item('proxies', 'https', '')
            else:
                om.remove_item('session_options', i)

        path = str(path)
        om.save(path)

        return path

    def save_to_default(self):
        return self.save('default')

    def as_dict(self):
        return session_options_to_dict(self)

    def make_session(self):
        s = Session()
        h = CaseInsensitiveDict(self.headers) if self.headers else CaseInsensitiveDict()

        if self.cookies:
            set_session_cookies(s, self.cookies)
        if self.adapters:
            for url, adapter in self.adapters:
                s.mount(url, adapter)

        for i in ['auth', 'proxies', 'hooks', 'params', 'verify', 'cert', 'stream', 'trust_env', 'max_redirects']:
            attr = self.__getattribute__(i)
            if attr:
                s.__setattr__(i, attr)

        return s, h

    def from_session(self, session, headers=None):
        self._headers = CaseInsensitiveDict(copy(session.headers).update(headers)) if headers else session.headers
        self._cookies = session.cookies
        self._auth = session.auth
        self._proxies = session.proxies
        self._hooks = session.hooks
        self._params = session.params
        self._verify = session.verify
        self._cert = session.cert
        self._stream = session.stream
        self._trust_env = session.trust_env
        self._max_redirects = session.max_redirects
        if session.adapters:
            self._adapters = [(k, i) for k, i in session.adapters.items()]
        return self


def session_options_to_dict(options):
    if options in (False, None):
        return SessionOptions(read_file=False).as_dict()

    if isinstance(options, dict):
        return options

    re_dict = dict()
    attrs = ['headers', 'cookies', 'proxies', 'params', 'verify', 'stream', 'trust_env', 'cert',
             'max_redirects', 'timeout', 'download_path']

    for attr in attrs:
        val = options.__getattribute__(f'_{attr}')
        if val is not None:
            re_dict[attr] = val

    return re_dict
