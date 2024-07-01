# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from copy import copy
from pathlib import Path

from requests import Session
from requests.structures import CaseInsensitiveDict

from .options_manage import OptionsManager
from .._functions.web import cookies_to_tuple, set_session_cookies, format_headers


class SessionOptions(object):
    """requests的Session对象配置类"""

    def __init__(self, read_file=True, ini_path=None):
        """
        :param read_file: 是否从文件读取配置
        :param ini_path: ini文件路径
        """
        self.ini_path = None
        self._download_path = None
        self._timeout = 10
        self._del_set = set()  # 记录要从ini文件删除的参数

        if read_file is False:
            ini_path = False
            self.ini_path = None
        elif ini_path:
            ini_path = Path(ini_path).absolute()
            if not ini_path.exists():
                raise ValueError(f'文件不存在：{ini_path}')
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
        self._download_path = om.paths.get('download_path', None) or None

        others = om.others
        self._retry_times = others.get('retry_times', 3)
        self._retry_interval = others.get('retry_interval', 2)

    # ===========须独立处理的项开始============
    @property
    def download_path(self):
        """返回默认下载路径属性信息"""
        return self._download_path

    def set_download_path(self, path):
        """设置默认下载路径
        :param path: 下载路径
        :return: 返回当前对象
        """
        self._download_path = str(path)
        return self

    @property
    def timeout(self):
        """返回timeout属性信息"""
        return self._timeout

    def set_timeout(self, second):
        """设置超时信息
        :param second: 秒数
        :return: 返回当前对象
        """
        self._timeout = second
        return self

    @property
    def proxies(self):
        """返回proxies设置信息"""
        if self._proxies is None:
            self._proxies = {}
        return self._proxies

    def set_proxies(self, http=None, https=None):
        """设置proxies参数
        :param http: http代理地址
        :param https: https代理地址
        :return: 返回当前对象
        """
        self._sets('proxies', {'http': http, 'https': https})
        return self

    @property
    def retry_times(self):
        """返回连接失败时的重试次数"""
        return self._retry_times

    @property
    def retry_interval(self):
        """返回连接失败时的重试间隔（秒）"""
        return self._retry_interval

    def set_retry(self, times=None, interval=None):
        """设置连接失败时的重试操作
        :param times: 重试次数
        :param interval: 重试间隔
        :return: 当前对象
        """
        if times is not None:
            self._retry_times = times
        if interval is not None:
            self._retry_interval = interval
        return self

    # ===========须独立处理的项结束============

    @property
    def headers(self):
        """返回headers设置信息"""
        if self._headers is None:
            self._headers = {}
        return self._headers

    def set_headers(self, headers):
        """设置headers参数
        :param headers: 参数值，传入None可在ini文件标记删除
        :return: 返回当前对象
        """
        if headers is None:
            self._headers = None
            self._del_set.add('headers')
        else:
            headers = format_headers(headers)
            self._headers = {key.lower(): headers[key] for key in headers}
        return self

    def set_a_header(self, name, value):
        """设置headers中一个项
        :param name: 设置名称
        :param value: 设置值
        :return: 返回当前对象
        """
        if self._headers is None:
            self._headers = {}

        self._headers[name.lower()] = value
        return self

    def remove_a_header(self, name):
        """从headers中删除一个设置
        :param name: 要删除的设置
        :return: 返回当前对象
        """
        if self._headers is None:
            return self

        self._headers.pop(name.lower(), None)

        return self

    def clear_headers(self):
        """清空已设置的header参数"""
        self._headers = None
        self._del_set.add('headers')

    @property
    def cookies(self):
        """以list形式返回cookies"""
        if self._cookies is None:
            self._cookies = []
        return self._cookies

    def set_cookies(self, cookies):
        """设置一个或多个cookies信息
        :param cookies: cookies，可为Cookie, CookieJar, list, tuple, str, dict，传入None可在ini文件标记删除
        :return: 返回当前对象
        """
        cookies = cookies if cookies is None else list(cookies_to_tuple(cookies))
        self._sets('cookies', cookies)
        return self

    @property
    def auth(self):
        """返回认证设置信息"""
        return self._auth

    def set_auth(self, auth):
        """设置认证元组或对象
        :param auth: 认证元组或对象
        :return: 返回当前对象
        """
        self._sets('auth', auth)
        return self

    @property
    def hooks(self):
        """返回回调方法"""
        if self._hooks is None:
            self._hooks = {}
        return self._hooks

    def set_hooks(self, hooks):
        """设置回调方法
        :param hooks: 回调方法
        :return: 返回当前对象
        """
        self._hooks = hooks
        return self

    @property
    def params(self):
        """返回连接参数设置信息"""
        if self._params is None:
            self._params = {}
        return self._params

    def set_params(self, params):
        """设置查询参数字典
        :param params: 查询参数字典
        :return: 返回当前对象
        """
        self._sets('params', params)
        return self

    @property
    def verify(self):
        """返回是否验证SSL证书设置"""
        return self._verify

    def set_verify(self, on_off):
        """设置是否验证SSL证书
        :param on_off: 是否验证 SSL 证书
        :return: 返回当前对象
        """
        self._sets('verify', on_off)
        return self

    @property
    def cert(self):
        """返回SSL证书设置信息"""
        return self._cert

    def set_cert(self, cert):
        """SSL客户端证书文件的路径(.pem格式)，或(‘cert’, ‘key’)元组
        :param cert: 证书路径或元组
        :return: 返回当前对象
        """
        self._sets('cert', cert)
        return self

    @property
    def adapters(self):
        """返回适配器设置信息"""
        if self._adapters is None:
            self._adapters = []
        return self._adapters

    def add_adapter(self, url, adapter):
        """添加适配器
        :param url: 适配器对应url
        :param adapter: 适配器对象
        :return: 返回当前对象
        """
        self._adapters.append((url, adapter))
        return self

    @property
    def stream(self):
        """返回是否使用流式响应内容设置信息"""
        return self._stream

    def set_stream(self, on_off):
        """设置是否使用流式响应内容
        :param on_off: 是否使用流式响应内容
        :return: 返回当前对象
        """
        self._sets('stream', on_off)
        return self

    @property
    def trust_env(self):
        """返回是否信任环境设置信息"""
        return self._trust_env

    def set_trust_env(self, on_off):
        """设置是否信任环境
        :param on_off: 是否信任环境
        :return: 返回当前对象
        """
        self._sets('trust_env', on_off)
        return self

    @property
    def max_redirects(self):
        """返回最大重定向次数"""
        return self._max_redirects

    def set_max_redirects(self, times):
        """设置最大重定向次数
        :param times: 最大重定向次数
        :return: 返回当前对象
        """
        self._sets('max_redirects', times)
        return self

    def _sets(self, arg, val):
        """给属性赋值或标记删除
        :param arg: 属性名称
        :param val: 参数值
        :return: None
        """
        if val is None:
            self.__setattr__(f'_{arg}', None)
            self._del_set.add(arg)
        else:
            self.__setattr__(f'_{arg}', val)
            if arg in self._del_set:
                self._del_set.remove(arg)

    def save(self, path=None):
        """保存设置到文件
        :param path: ini文件的路径，传入 'default' 保存到默认ini文件
        :return: 保存文件的绝对路径
        """
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
        """保存当前配置到默认ini文件"""
        return self.save('default')

    def as_dict(self):
        """以字典形式返回本对象"""
        return session_options_to_dict(self)

    def make_session(self):
        """根据内在的配置生成Session对象，ua从对象中分离"""
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
        """从Session对象中读取配置
        :param session: Session对象
        :param headers: headers
        :return: 当前对象
        """
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

    def __repr__(self):
        return f'<SessionOptions at {id(self)}>'


def session_options_to_dict(options):
    """把session配置对象转换为字典
    :param options: session配置对象或字典
    :return: 配置字典
    """
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
