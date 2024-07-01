# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from base64 import b64decode
from json import JSONDecodeError, loads
from queue import Queue
from re import search
from time import perf_counter, sleep

from requests.structures import CaseInsensitiveDict

from .._base.driver import Driver
from .._functions.settings import Settings
from ..errors import WaitTimeoutError


class Listener(object):
    """监听器基类"""

    def __init__(self, owner):
        """
        :param owner: ChromiumBase对象
        """
        self._owner = owner
        self._address = owner.address
        self._target_id = owner._target_id
        self._driver = None
        self._running_requests = 0
        self._running_targets = 0

        self._caught = None
        self._request_ids = None
        self._extra_info_ids = None

        self.listening = False
        self.tab_id = None

        self._targets = True
        self._is_regex = False
        self._method = ('GET', 'POST')
        self._res_type = True

    @property
    def targets(self):
        """返回监听目标"""
        return self._targets

    def set_targets(self, targets=True, is_regex=False, method=('GET', 'POST'), res_type=True):
        """指定要等待的数据包
        :param targets: 要匹配的数据包url特征，可用list等传入多个，为True时获取所有
        :param is_regex: 设置的target是否正则表达式
        :param method: 设置监听的请求类型，可指定多个，为True时监听全部
        :param res_type: 设置监听的资源类型，可指定多个，为True时监听全部，可指定的值有：
        Document, Stylesheet, Image, Media, Font, Script, TextTrack, XHR, Fetch, Prefetch, EventSource, WebSocket,
        Manifest, SignedExchange, Ping, CSPViolationReport, Preflight, Other
        :return: None
        """
        if targets is not None:
            if not isinstance(targets, (str, list, tuple, set)) and targets is not True:
                raise TypeError('targets只能是str、list、tuple、set、True。')
            if targets is True:
                self._targets = True
            else:
                self._targets = {targets} if isinstance(targets, str) else set(targets)

        if is_regex is not None:
            self._is_regex = is_regex

        if method is not None:
            if isinstance(method, str):
                self._method = {method.upper()}
            elif isinstance(method, (list, tuple, set)):
                self._method = set(i.upper() for i in method)
            elif method is True:
                self._method = True
            else:
                raise TypeError('method参数只能是str、list、tuple、set、True类型。')

        if res_type is not None:
            if isinstance(res_type, str):
                self._res_type = {res_type.upper()}
            elif isinstance(res_type, (list, tuple, set)):
                self._res_type = set(i.upper() for i in res_type)
            elif res_type is True:
                self._res_type = True
            else:
                raise TypeError('res_type参数只能是str、list、tuple、set、True类型。')

    def start(self, targets=None, is_regex=None, method=None, res_type=None):
        """拦截目标请求，每次拦截前清空结果
        :param targets: 要匹配的数据包url特征，可用list等传入多个，为True时获取所有
        :param is_regex: 设置的target是否正则表达式，为None时保持原来设置
        :param method: 设置监听的请求类型，可指定多个，默认('GET', 'POST')，为True时监听全部，为None时保持原来设置
        :param res_type: 设置监听的资源类型，可指定多个，默认为True时监听全部，为None时保持原来设置，可指定的值有：
        Document, Stylesheet, Image, Media, Font, Script, TextTrack, XHR, Fetch, Prefetch, EventSource, WebSocket,
        Manifest, SignedExchange, Ping, CSPViolationReport, Preflight, Other
        :return: None
        """
        if targets is not None:
            if is_regex is None:
                is_regex = False
        if targets or is_regex is not None or method or res_type:
            self.set_targets(targets, is_regex, method, res_type)
        self.clear()

        if self.listening:
            return

        self._driver = Driver(self._target_id, 'page', self._address)
        self._driver.run('Network.enable')

        self._set_callback()
        self.listening = True

    def wait(self, count=1, timeout=None, fit_count=True, raise_err=None):
        """等待符合要求的数据包到达指定数量
        :param count: 需要捕捉的数据包数量
        :param timeout: 超时时间（秒），为None无限等待
        :param fit_count: 是否必须满足总数要求，发生超时，为True返回False，为False返回已捕捉到的数据包
        :param raise_err: 超时时是否抛出错误，为None时根据Settings设置
        :return: count为1时返回数据包对象，大于1时返回列表，超时且fit_count为True时返回False
        """
        if not self.listening:
            raise RuntimeError('监听未启动或已暂停。')
        if not timeout:
            while self._caught.qsize() < count:
                sleep(.03)
            fail = False

        else:
            end = perf_counter() + timeout
            while True:
                if perf_counter() > end:
                    fail = True
                    break
                if self._caught.qsize() >= count:
                    fail = False
                    break
                sleep(.03)

        if fail:
            if fit_count or not self._caught.qsize():
                if raise_err is True or Settings.raise_when_wait_failed is True:
                    raise WaitTimeoutError(f'等待数据包失败（等待{timeout}秒）。')
                else:
                    return False
            else:
                return [self._caught.get_nowait() for _ in range(self._caught.qsize())]

        if count == 1:
            return self._caught.get_nowait()

        return [self._caught.get_nowait() for _ in range(count)]

    def steps(self, count=None, timeout=None, gap=1):
        """用于单步操作，可实现每收到若干个数据包执行一步操作（如翻页）
        :param count: 需捕获的数据包总数，为None表示无限
        :param timeout: 每个数据包等待时间（秒），为None表示无限
        :param gap: 每接收到多少个数据包返回一次数据
        :return: 用于在接收到监听目标时触发动作的可迭代对象
        """
        if not self.listening:
            raise RuntimeError('监听未启动或已暂停。')
        caught = 0
        end = perf_counter() + timeout if timeout else None
        while True:
            if (timeout and perf_counter() > end) or self._driver._stopped.is_set():
                return
            if self._caught.qsize() >= gap:
                yield self._caught.get_nowait() if gap == 1 else [self._caught.get_nowait() for _ in range(gap)]
                if timeout:
                    end = perf_counter() + timeout
                if count:
                    caught += gap
                    if caught >= count:
                        return
            sleep(.03)

    def stop(self):
        """停止监听，清空已监听到的列表"""
        if self.listening:
            self.pause()
            self.clear()
        self._driver.stop()
        self._driver = None

    def pause(self, clear=True):
        """暂停监听
        :param clear: 是否清空已获取队列
        :return: None
        """
        if self.listening:
            self._driver.set_callback('Network.requestWillBeSent', None)
            self._driver.set_callback('Network.responseReceived', None)
            self._driver.set_callback('Network.loadingFinished', None)
            self._driver.set_callback('Network.loadingFailed', None)
            self.listening = False
        if clear:
            self.clear()

    def resume(self):
        """继续暂停的监听"""
        if self.listening:
            return
        self._set_callback()
        self.listening = True

    def clear(self):
        """清空结果"""
        self._request_ids = {}
        self._extra_info_ids = {}
        self._caught = Queue(maxsize=0)
        self._running_requests = 0
        self._running_targets = 0

    def wait_silent(self, timeout=None, targets_only=False, limit=0):
        """等待所有请求结束
        :param timeout: 超时时间（秒），为None时无限等待
        :param targets_only: 是否只等待targets指定的请求结束
        :param limit: 剩下多少个连接时视为结束
        :return: 返回是否等待成功
        """
        if not self.listening:
            raise RuntimeError('监听未启动或已暂停。')
        if timeout is None:
            while ((not targets_only and self._running_requests > limit)
                   or (targets_only and self._running_targets > limit)):
                sleep(.1)
            return True

        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if ((not targets_only and self._running_requests <= limit)
                    or (targets_only and self._running_targets <= limit)):
                return True
            sleep(.1)
        else:
            return False

    def _to_target(self, target_id, address, owner):
        """切换监听的页面对象
        :param target_id: 新页面对象_target_id
        :param address: 新页面对象address
        :param owner: 新页面对象
        :return: None
        """
        self._target_id = target_id
        self._address = address
        self._owner = owner
        # debug = False
        if self._driver:
            # debug = self._driver._debug
            self._driver.stop()
        if self.listening:
            self._driver = Driver(self._target_id, 'page', self._address)
            # self._driver._debug = debug
            self._driver.run('Network.enable')
            self._set_callback()

    def _set_callback(self):
        """设置监听请求的回调函数"""
        self._driver.set_callback('Network.requestWillBeSent', self._requestWillBeSent)
        self._driver.set_callback('Network.requestWillBeSentExtraInfo', self._requestWillBeSentExtraInfo)
        self._driver.set_callback('Network.responseReceived', self._response_received)
        self._driver.set_callback('Network.responseReceivedExtraInfo', self._responseReceivedExtraInfo)
        self._driver.set_callback('Network.loadingFinished', self._loading_finished)
        self._driver.set_callback('Network.loadingFailed', self._loading_failed)

    def _requestWillBeSent(self, **kwargs):
        """接收到请求时的回调函数"""
        self._running_requests += 1
        p = None
        if self._targets is True:
            if ((self._method is True or kwargs['request']['method'] in self._method)
                    and (self._res_type is True or kwargs.get('type', '').upper() in self._res_type)):
                self._running_targets += 1
                rid = kwargs['requestId']
                p = self._request_ids.setdefault(rid, DataPacket(self._owner.tab_id, True))
                p._raw_request = kwargs
                if kwargs['request'].get('hasPostData', None) and not kwargs['request'].get('postData', None):
                    p._raw_post_data = self._driver.run('Network.getRequestPostData',
                                                        requestId=rid).get('postData', None)

        else:
            rid = kwargs['requestId']
            for target in self._targets:
                if (((self._is_regex and search(target, kwargs['request']['url']))
                     or (not self._is_regex and target in kwargs['request']['url']))
                        and (self._method is True or kwargs['request']['method'] in self._method)
                        and (self._res_type is True or kwargs.get('type', '').upper() in self._res_type)):
                    self._running_targets += 1
                    p = self._request_ids.setdefault(rid, DataPacket(self._owner.tab_id, target))
                    p._raw_request = kwargs
                    break

        self._extra_info_ids.setdefault(kwargs['requestId'], {})['obj'] = p if p else False

    def _requestWillBeSentExtraInfo(self, **kwargs):
        """接收到请求额外信息时的回调函数"""
        self._running_requests += 1
        self._extra_info_ids.setdefault(kwargs['requestId'], {})['request'] = kwargs

    def _response_received(self, **kwargs):
        """接收到返回信息时处理方法"""
        request = self._request_ids.get(kwargs['requestId'], None)
        if request:
            request._raw_response = kwargs['response']
            request._resource_type = kwargs['type']

    def _responseReceivedExtraInfo(self, **kwargs):
        """接收到返回额外信息时的回调函数"""
        self._running_requests -= 1
        r = self._extra_info_ids.get(kwargs['requestId'], None)
        if r:
            obj = r.get('obj', None)
            if obj is False:
                self._extra_info_ids.pop(kwargs['requestId'], None)
            elif isinstance(obj, DataPacket):
                obj._requestExtraInfo = r.get('request', None)
                obj._responseExtraInfo = kwargs
                self._extra_info_ids.pop(kwargs['requestId'], None)
            else:
                r['response'] = kwargs

    def _loading_finished(self, **kwargs):
        """请求完成时处理方法"""
        self._running_requests -= 1
        rid = kwargs['requestId']
        packet = self._request_ids.get(rid)
        if packet:
            r = self._driver.run('Network.getResponseBody', requestId=rid)
            if 'body' in r:
                packet._raw_body = r['body']
                packet._base64_body = r['base64Encoded']
            else:
                packet._raw_body = ''
                packet._base64_body = False

            if (packet._raw_request['request'].get('hasPostData', None)
                    and not packet._raw_request['request'].get('postData', None)):
                r = self._driver.run('Network.getRequestPostData', requestId=rid, _timeout=1)
                packet._raw_post_data = r.get('postData', None)

        r = self._extra_info_ids.get(kwargs['requestId'], None)
        if r:
            obj = r.get('obj', None)
            if obj is False or (isinstance(obj, DataPacket) and not self._extra_info_ids.get('request')):
                self._extra_info_ids.pop(kwargs['requestId'], None)
            elif isinstance(obj, DataPacket) and self._extra_info_ids.get('response'):
                response = r.get('response')
                obj._requestExtraInfo = r['request']
                obj._responseExtraInfo = response
                self._extra_info_ids.pop(kwargs['requestId'], None)

        self._request_ids.pop(rid, None)

        if packet:
            self._caught.put(packet)
            self._running_targets -= 1

    def _loading_failed(self, **kwargs):
        """请求失败时的回调方法"""
        self._running_requests -= 1
        r_id = kwargs['requestId']
        data_packet = self._request_ids.get(r_id, None)
        if data_packet:
            data_packet._raw_fail_info = kwargs
            data_packet._resource_type = kwargs['type']
            data_packet.is_failed = True

        r = self._extra_info_ids.get(kwargs['requestId'], None)
        if r:
            obj = r.get('obj', None)
            if obj is False and r.get('response'):
                self._extra_info_ids.pop(kwargs['requestId'], None)
            elif isinstance(obj, DataPacket):
                response = r.get('response')
                if response:
                    obj._requestExtraInfo = r['request']
                    obj._responseExtraInfo = response
                    self._extra_info_ids.pop(kwargs['requestId'], None)

        self._request_ids.pop(r_id, None)

        if data_packet:
            self._caught.put(data_packet)
            self._running_targets -= 1


class FrameListener(Listener):
    def _requestWillBeSent(self, **kwargs):
        """接收到请求时的回调函数"""
        if not self._owner._is_diff_domain and kwargs.get('frameId', None) != self._owner._frame_id:
            return
        super()._requestWillBeSent(**kwargs)

    def _response_received(self, **kwargs):
        """接收到返回信息时处理方法"""
        if not self._owner._is_diff_domain and kwargs.get('frameId', None) != self._owner._frame_id:
            return
        super()._response_received(**kwargs)


class DataPacket(object):
    """返回的数据包管理类"""

    def __init__(self, tab_id, target):
        """
        :param tab_id: 产生这个数据包的tab的id
        :param target: 监听目标
        """
        self.tab_id = tab_id
        self.target = target
        self.is_failed = False

        self._raw_request = None
        self._raw_post_data = None
        self._raw_response = None
        self._raw_body = None
        self._raw_fail_info = None

        self._request = None
        self._response = None
        self._fail_info = None

        self._base64_body = False
        self._requestExtraInfo = None
        self._responseExtraInfo = None
        self._resource_type = None

    def __repr__(self):
        t = f'"{self.target}"' if self.target is not True else True
        return f'<DataPacket target={t} url="{self.url}">'

    @property
    def _request_extra_info(self):
        return self._requestExtraInfo

    @property
    def _response_extra_info(self):
        return self._responseExtraInfo

    @property
    def url(self):
        return self.request.url

    @property
    def method(self):
        return self.request.method

    @property
    def frameId(self):
        return self._raw_request.get('frameId')

    @property
    def resourceType(self):
        return self._resource_type

    @property
    def request(self):
        if self._request is None:
            self._request = Request(self, self._raw_request['request'], self._raw_post_data)
        return self._request

    @property
    def response(self):
        if self._response is None:
            self._response = Response(self, self._raw_response, self._raw_body, self._base64_body)
        return self._response

    @property
    def fail_info(self):
        if self._fail_info is None:
            self._fail_info = FailInfo(self, self._raw_fail_info)
        return self._fail_info

    def wait_extra_info(self, timeout=None):
        """等待额外的信息加载完成
        :param timeout: 超时时间（秒），None为无限等待
        :return: 是否等待成功
        """
        if timeout is None:
            while self._responseExtraInfo is None:
                sleep(.1)
            return True

        else:
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                if self._responseExtraInfo is not None:
                    return True
                sleep(.1)
            else:
                return False


class Request(object):
    def __init__(self, data_packet, raw_request, post_data):
        self._data_packet = data_packet
        self._request = raw_request
        self._raw_post_data = post_data
        self._postData = None
        self._headers = None

    def __getattr__(self, item):
        return self._request.get(item, None)

    @property
    def headers(self):
        """以大小写不敏感字典返回headers数据"""
        if self._headers is None:
            self._headers = CaseInsensitiveDict(self._request['headers'])
        return self._headers

    @property
    def postData(self):
        """返回postData数据"""
        if self._postData is None:
            if self._raw_post_data:
                postData = self._raw_post_data
            elif self._request.get('postData', None):
                postData = self._request['postData']
            else:
                postData = False
            try:
                self._postData = loads(postData)
            except (JSONDecodeError, TypeError):
                self._postData = postData
        return self._postData

    @property
    def cookies(self):
        """以list形式返回发送的cookies"""
        return [c['cookie'] for c in self.extra_info.associatedCookies if not c['blockedReasons']]

    @property
    def extra_info(self):
        """返回额外数据"""
        return RequestExtraInfo(self._data_packet._request_extra_info or {})


class Response(object):
    def __init__(self, data_packet, raw_response, raw_body, base64_body):
        self._data_packet = data_packet
        self._response = raw_response
        self._raw_body = raw_body
        self._is_base64_body = base64_body
        self._body = None
        self._headers = None

    def __getattr__(self, item):
        return self._response.get(item, None) if self._response else None

    @property
    def headers(self):
        """以大小写不敏感字典返回headers数据"""
        if self._headers is None:
            self._headers = CaseInsensitiveDict(self._response['headers'])
        return self._headers

    @property
    def raw_body(self):
        """返回未被处理的body文本"""
        return self._raw_body

    @property
    def body(self):
        """返回body内容，如果是json格式，自动进行转换，如果时图片格式，进行base64转换，其它格式直接返回文本"""
        if self._body is None:
            if self._is_base64_body:
                self._body = b64decode(self._raw_body)

            else:
                try:
                    self._body = loads(self._raw_body)
                except (JSONDecodeError, TypeError):
                    self._body = self._raw_body

        return self._body

    @property
    def extra_info(self):
        return ResponseExtraInfo(self._data_packet._response_extra_info or {})


class ExtraInfo(object):
    def __init__(self, extra_info):
        self._extra_info = extra_info

    @property
    def all_info(self):
        """以dict形式返回所有额外信息"""
        return self._extra_info

    def __getattr__(self, item):
        return self._extra_info.get(item, None)


class RequestExtraInfo(ExtraInfo):
    pass


class ResponseExtraInfo(ExtraInfo):
    pass


class FailInfo(object):
    def __init__(self, data_packet, fail_info):
        self._data_packet = data_packet
        self._fail_info = fail_info

    def __getattr__(self, item):
        return self._fail_info.get(item, None) if self._fail_info else None
