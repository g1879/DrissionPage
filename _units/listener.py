# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from base64 import b64decode
from json import JSONDecodeError, loads
from queue import Queue
from re import search
from time import perf_counter, sleep

from requests.structures import CaseInsensitiveDict

from .._base.driver import Driver
from .._functions.settings import Settings as _S
from ..errors import WaitTimeoutError


class Listener(object):
    """监听器基类"""

    def __init__(self, owner):
        self._owner = owner
        self._address = owner.browser.address
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
        self._method = {'GET', 'POST'}
        self._res_type = True

    @property
    def targets(self):
        """返回监听目标"""
        return self._targets

    def set_targets(self, targets=True, is_regex=False, method=('GET', 'POST'), res_type=True):
        if targets is not None:
            if not isinstance(targets, (str, list, tuple, set)) and targets is not True:
                raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'targets',
                                               ALLOW_TYPE='str, list, tuple, set, True', CURR_TYPE=type(targets)))
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
                raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'method',
                                               ALLOW_TYPE='str, list, tuple, set, True', CURR_TYPE=type(method)))

        if res_type is not None:
            if isinstance(res_type, str):
                self._res_type = {res_type.upper()}
            elif isinstance(res_type, (list, tuple, set)):
                self._res_type = set(i.upper() for i in res_type)
            elif res_type is True:
                self._res_type = True
            else:
                raise ValueError(_S._lang.join(_S._lang.INCORRECT_TYPE_, 'res_type',
                                               ALLOW_TYPE='str, list, tuple, set, True', CURR_TYPE=type(res_type)))

    def start(self, targets=None, is_regex=None, method=None, res_type=None):
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
        if not self.listening:
            raise RuntimeError(_S._lang.join(_S._lang.NOT_LISTENING))
        if not timeout:
            while self._driver.is_running and self.listening and self._caught.qsize() < count:
                sleep(.03)
            fail = False

        else:
            end = perf_counter() + timeout
            while self._driver.is_running and self.listening:
                if perf_counter() > end:
                    fail = True
                    break
                if self._caught.qsize() >= count:
                    fail = False
                    break
                sleep(.03)

        if fail:
            if fit_count or not self._caught.qsize():
                if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
                    raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.DATA_PACKET, timeout)
                else:
                    return False
            else:
                return [self._caught.get_nowait() for _ in range(self._caught.qsize())]

        if count == 1:
            return self._caught.get_nowait()

        return [self._caught.get_nowait() for _ in range(count)]

    def steps(self, count=None, timeout=None, gap=1):
        if not self.listening:
            raise RuntimeError(_S._lang.join(_S._lang.NOT_LISTENING))
        caught = 0
        if timeout is None:
            while self._driver.is_running and self.listening:
                if self._caught.qsize() >= gap:
                    yield self._caught.get_nowait() if gap == 1 else [self._caught.get_nowait() for _ in range(gap)]
                    if count:
                        caught += gap
                        if caught >= count:
                            return
                sleep(.03)

        else:
            end = perf_counter() + timeout
            while self._driver.is_running and self.listening and perf_counter() < end:
                if self._caught.qsize() >= gap:
                    yield self._caught.get_nowait() if gap == 1 else [self._caught.get_nowait() for _ in range(gap)]
                    end = perf_counter() + timeout
                    if count:
                        caught += gap
                        if caught >= count:
                            return
                sleep(.03)
            return False

    def stop(self):
        if self.listening:
            self.pause()
            self.clear()
        self._driver.stop()
        self._driver = None

    def pause(self, clear=True):
        if self.listening:
            self._driver.set_callback('Network.requestWillBeSent', None)
            self._driver.set_callback('Network.responseReceived', None)
            self._driver.set_callback('Network.loadingFinished', None)
            self._driver.set_callback('Network.loadingFailed', None)
            self.listening = False
        if clear:
            self.clear()

    def resume(self):
        if self.listening:
            return
        self._set_callback()
        self.listening = True

    def clear(self):
        self._request_ids = {}
        self._extra_info_ids = {}
        self._caught = Queue(maxsize=0)
        self._running_requests = 0
        self._running_targets = 0

    def wait_silent(self, timeout=None, targets_only=False, limit=0):
        if not self.listening:
            raise RuntimeError(_S._lang.join(_S._lang.NOT_LISTENING))
        if timeout is None:
            while ((not targets_only and self._running_requests > limit)
                   or (targets_only and self._running_targets > limit)):
                sleep(.01)
            return True

        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if ((not targets_only and self._running_requests <= limit)
                    or (targets_only and self._running_targets <= limit)):
                return True
            sleep(.01)
        else:
            return False

    def _to_target(self, target_id, address, owner):
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
        self._driver.set_callback('Network.requestWillBeSent', self._requestWillBeSent)
        self._driver.set_callback('Network.requestWillBeSentExtraInfo', self._requestWillBeSentExtraInfo)
        self._driver.set_callback('Network.responseReceived', self._response_received)
        self._driver.set_callback('Network.responseReceivedExtraInfo', self._responseReceivedExtraInfo)
        self._driver.set_callback('Network.loadingFinished', self._loading_finished)
        self._driver.set_callback('Network.loadingFailed', self._loading_failed)

    def _requestWillBeSent(self, **kwargs):
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
        self._running_requests += 1
        self._extra_info_ids.setdefault(kwargs['requestId'], {})['request'] = kwargs

    def _response_received(self, **kwargs):
        request = self._request_ids.get(kwargs['requestId'], None)
        if request:
            request._raw_response = kwargs['response']
            request._resource_type = kwargs['type']

    def _responseReceivedExtraInfo(self, **kwargs):
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
        if not self._owner._is_diff_domain and kwargs.get('frameId', None) != self._owner._frame_id:
            return
        super()._requestWillBeSent(**kwargs)

    def _response_received(self, **kwargs):
        if not self._owner._is_diff_domain and kwargs.get('frameId', None) != self._owner._frame_id:
            return
        super()._response_received(**kwargs)


class DataPacket(object):

    def __init__(self, tab_id, target):
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
        if timeout is None:
            while self._responseExtraInfo is None:
                sleep(.01)
            return True

        else:
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                if self._responseExtraInfo is not None:
                    return True
                sleep(.01)
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
        if self._headers is None:
            self._headers = CaseInsensitiveDict(self._request['headers'])
            if self.extra_info.headers:
                h = CaseInsensitiveDict(self.extra_info.headers)
                for k, v in h.items():
                    if k not in self._headers:
                        self._headers[k] = v
        return self._headers

    @property
    def params(self):
        from urllib.parse import parse_qsl, urlparse
        return dict(parse_qsl(urlparse(self.url).query, keep_blank_values=True))

    @property
    def postData(self):
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
        return [c['cookie'] for c in self.extra_info.associatedCookies if not c['blockedReasons']]

    @property
    def extra_info(self):
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
        if self._headers is None:
            self._headers = CaseInsensitiveDict(self._response['headers'])
            if self.extra_info.headers:
                h = CaseInsensitiveDict(self.extra_info.headers)
                for k, v in h.items():
                    if k not in self._headers:
                        self._headers[k] = v
        return self._headers

    @property
    def raw_body(self):
        return self._raw_body

    @property
    def body(self):
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
