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

from .._functions.settings import Settings as _S
from .._functions.tools import wait_until
from ..errors import WaitTimeoutError


class Listener(object):
    def __init__(self, owner):
        self._owner = owner
        self._running_requests = 0
        self._running_targets = 0

        self._caught = None
        self._request_ids = None
        self._extra_info_ids = None
        self._ws_info = {}

        self.listening = False
        self.tab_id = None

        self._targets = True
        self._is_regex = False
        self._method = {'GET', 'POST'}
        self._res_type = True
        self._listen_ws = False

        self._method_setter = None
        self._res_type_setter = None

    @property
    def targets(self):
        return self._targets

    @property
    def set_method(self):
        if self._method_setter is None:
            self._method_setter = MethodSetter(self)
        return self._method_setter

    @property
    def set_res_type(self):
        if self._res_type_setter is None:
            self._res_type_setter = ResTypeSetter(self)
        return self._res_type_setter

    def set_targets(self, targets=True, is_regex=False):
        if targets is not None:
            if not isinstance(targets, (str, list, tuple, set)) and targets is not True:
                raise ValueError(_S._lang.joinn(_S._lang.INCORRECT_TYPE_, 'targets',
                                                ALLOW_TYPE='str, list, tuple, set, True', CURR_TYPE=type(targets)))
            if targets is True:
                self._targets = True
            else:
                self._targets = {targets} if isinstance(targets, str) else set(targets)

        if is_regex is not None:
            self._is_regex = is_regex

    def start(self, targets=None, is_regex=None):
        if targets is not None:
            if is_regex is None:
                is_regex = False
        if targets or is_regex is not None:
            self.set_targets(targets, is_regex)
        self.clear()
        self.resume()
        self._owner._enable_domain('Network')

    def wait(self, count=1, timeout=None, fit_count=True, raise_err=None):
        if not self.listening:
            raise RuntimeError(_S._lang.joinn(_S._lang.NOT_LISTENING))
        success = False
        if not timeout:
            while self._owner._messenger_running and self.listening and self._caught.qsize() < count:
                sleep(.02)
            success = self._owner._messenger_running

        else:
            end = perf_counter() + timeout
            while self._owner._messenger_running and self.listening and perf_counter() < end:
                if self._caught.qsize() >= count:
                    success = True
                    break
                sleep(.02)

        if success:
            if count == 1:
                return self._caught.get_nowait()
            return [self._caught.get_nowait() for _ in range(count)]

        if fit_count or not self._caught.qsize():
            if raise_err is True or (_S.raise_when_wait_failed is True and raise_err is None):
                raise WaitTimeoutError(_S._lang.WAITING_FAILED_, _S._lang.DATA_PACKET, timeout)
            else:
                return False
        else:
            return [self._caught.get_nowait() for _ in range(self._caught.qsize())]

    def steps(self, count=None, timeout=None, gap=1):
        if not self.listening:
            raise RuntimeError(_S._lang.joinn(_S._lang.NOT_LISTENING))
        caught = 0
        if timeout is None:
            while self._owner._messenger_running and self.listening:
                if self._caught.qsize() >= gap:
                    yield self._caught.get_nowait() if gap == 1 else [self._caught.get_nowait() for _ in range(gap)]
                    if count:
                        caught += gap
                        if caught >= count:
                            return None
                sleep(.03)

        else:
            end = perf_counter() + timeout
            while self._owner._messenger_running and self.listening and perf_counter() < end:
                if self._caught.qsize() >= gap:
                    yield self._caught.get_nowait() if gap == 1 else [self._caught.get_nowait() for _ in range(gap)]
                    end = perf_counter() + timeout
                    if count:
                        caught += gap
                        if caught >= count:
                            return None
                sleep(.03)
            return False

    def stop(self):
        if self.listening:
            self.pause(clear=True)
        self._owner._disable_domain('Network')

    def pause(self, clear=True):
        if self.listening:
            self._owner._set_callback('Network.requestWillBeSent', None)
            self._owner._set_callback('Network.responseReceived', None)
            self._owner._set_callback('Network.loadingFinished', None)
            self._owner._set_callback('Network.loadingFailed', None)
            self._owner._set_callback('Network.requestWillBeSentExtraInfo', None)
            self._owner._set_callback('Network.responseReceivedExtraInfo', None)
            self._owner._set_callback('Network.webSocketFrameSent', None)
            self._owner._set_callback('Network.webSocketFrameReceived', None)
            self._owner._set_callback('Network.webSocketCreated', None)
            self._owner._set_callback('Network.webSocketHandshakeResponseReceived', None)
            self._owner._set_callback('Network.webSocketWillSendHandshakeRequest', None)
            self._owner._set_callback('Network.webSocketClosed', None)
            self.listening = False
        if clear:
            self.clear()

    def resume(self):
        if self.listening:
            return
        self._init_callback()
        self.listening = True

    def clear(self):
        self._request_ids = {}
        self._extra_info_ids = {}
        self._ws_info = {}
        self._caught = Queue(maxsize=0)
        self._running_requests = 0
        self._running_targets = 0

    def wait_silent(self, timeout=None, targets_only=False, limit=0):
        if not self.listening:
            raise RuntimeError(_S._lang.joinn(_S._lang.NOT_LISTENING))
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

    def _to_target(self, target_id, owner):
        self._target_id = target_id
        self._owner = owner
        if self.listening:
            self.stop()
            self.start()

    def _init_callback(self):
        if self._res_type is True or self._res_type - {'WEBSOCKET'}:
            self._owner._set_callback('Network.requestWillBeSent', self._requestWillBeSent)
            self._owner._set_callback('Network.responseReceived', self._response_received)
            self._owner._set_callback('Network.loadingFinished', self._loading_finished)
            self._owner._set_callback('Network.loadingFailed', self._loading_failed)
            self._owner._set_callback('Network.requestWillBeSentExtraInfo', self._requestWillBeSentExtraInfo)
            self._owner._set_callback('Network.responseReceivedExtraInfo', self._responseReceivedExtraInfo)
        if self._res_type is True or 'WEBSOCKET' in self._res_type:
            self._owner._set_callback('Network.webSocketFrameSent', self._webSocketFrameSent)
            self._owner._set_callback('Network.webSocketFrameReceived', self._webSocketFrameReceived)
            self._owner._set_callback('Network.webSocketCreated', self._webSocketCreated)
            self._owner._set_callback('Network.webSocketHandshakeResponseReceived',
                                      self._webSocketHandshakeResponseReceived)
            self._owner._set_callback('Network.webSocketWillSendHandshakeRequest',
                                      self._webSocketWillSendHandshakeRequest)
            self._owner._set_callback('Network.webSocketClosed', self._webSocketClosed)
        if self._res_type is True or 'EVENTSOURCE' in self._res_type:
            self._owner._set_callback('Network.eventSourceMessageReceived', self._eventSourceMessageReceived)

    def _eventSourceMessageReceived(self, **kwargs):
        i = self._request_ids.get(kwargs['requestId'])
        if self._targets is True or i:
            p = SSEPacket(self._owner, i.target if i else None, kwargs)
            if i:
                p._connect_info = i
            self._caught.put(p)

    def _webSocketFrameSent(self, **kwargs):
        i = self._ws_info.get(kwargs['requestId'])
        if self._targets is True or i:
            p = WebSocketPacket(self._owner, i.target if i else None, kwargs, True)
            if i:
                p._connect_info = i
            self._caught.put(p)

    def _webSocketFrameReceived(self, **kwargs):
        i = self._ws_info.get(kwargs['requestId'])
        if self._targets is True or i:
            p = WebSocketPacket(self._owner, i.target if i else None, kwargs, False)
            if i:
                p._connect_info = i
            self._caught.put(p)

    def _webSocketCreated(self, **kwargs):
        target = in_targets(self, kwargs['url'], True, True)
        if target:
            self._ws_info[kwargs['requestId']] = WebSocketConnectInfo(self._owner, target, kwargs['requestId'],
                                                                      kwargs['url'], kwargs.get('initiator'))

    def _webSocketClosed(self, **kwargs):
        self._ws_info.pop(kwargs['requestId'], None)

    def _webSocketHandshakeResponseReceived(self, **kwargs):
        i = self._ws_info.get(kwargs['requestId'])
        if i:
            i.response = kwargs

    def _webSocketWillSendHandshakeRequest(self, **kwargs):
        i = self._ws_info.get(kwargs['requestId'])
        if i:
            i.request = kwargs

    def _requestWillBeSent(self, **kwargs):
        self._running_requests += 1
        p = False
        target = in_targets(self, kwargs['request']['url'], kwargs['request']['method'], kwargs.get('type', ''))
        if target:
            self._running_targets += 1
            rid = kwargs['requestId']
            p = self._request_ids.setdefault(rid, DataPacket(self._owner, target))
            p._raw_request = kwargs
            if kwargs['request'].get('hasPostData') and not kwargs['request'].get('postData'):
                p._raw_post_data = self._owner._run_cdp('Network.getRequestPostData',
                                                        requestId=rid, _ignore=True).get('postData')
        self._extra_info_ids.setdefault(kwargs['requestId'], {})['obj'] = p

    def _requestWillBeSentExtraInfo(self, **kwargs):
        self._running_requests += 1
        self._extra_info_ids.setdefault(kwargs['requestId'], {})['request'] = kwargs

    def _response_received(self, **kwargs):
        request = self._request_ids.get(kwargs['requestId'])
        if request:
            request._raw_response = kwargs['response']
            request._resource_type = kwargs['type']

    def _responseReceivedExtraInfo(self, **kwargs):
        self._running_requests -= 1
        r = self._extra_info_ids.get(kwargs['requestId'])
        if r:
            obj = r.get('obj')
            if obj is False:
                self._extra_info_ids.pop(kwargs['requestId'], None)
            elif isinstance(obj, DataPacket):
                obj._requestExtraInfo = r.get('request')
                obj._responseExtraInfo = kwargs
                self._extra_info_ids.pop(kwargs['requestId'], None)
            else:
                r['response'] = kwargs

    def _loading_finished(self, **kwargs):
        self._running_requests -= 1
        rid = kwargs['requestId']
        packet = self._request_ids.get(rid)
        if packet:
            r = self._owner._run_cdp('Network.getResponseBody', requestId=rid, _ignore=True)
            if 'body' in r:
                packet._raw_body = r['body']
                packet._base64_body = r['base64Encoded']
            else:
                packet._raw_body = ''
                packet._base64_body = False

            if (packet._raw_request['request'].get('hasPostData')
                    and not packet._raw_request['request'].get('postData')):
                r = self._owner._run_cdp('Network.getRequestPostData', requestId=rid, _timeout=1, _ignore=True)
                packet._raw_post_data = r.get('postData')

        r = self._extra_info_ids.get(kwargs['requestId'])
        if r:
            obj = r.get('obj')
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
        data_packet = self._request_ids.get(r_id)
        if data_packet:
            data_packet._raw_fail_info = kwargs
            data_packet._resource_type = kwargs['type']
            data_packet.is_failed = True

        r = self._extra_info_ids.get(kwargs['requestId'])
        if r:
            obj = r.get('obj')
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


def in_targets(listener, url, method, res_type):
    if listener._targets is True:
        if ((listener._method is True or method in listener._method)
                and (listener._res_type is True or res_type.upper() in listener._res_type)):
            return True
    else:
        for target in listener._targets:
            if (((listener._is_regex and search(target, url))
                 or (not listener._is_regex and target in url))
                    and (listener._method is True or method in listener._method)
                    and (listener._res_type is True or res_type.upper() in listener._res_type)):
                return target
    return False


class FrameListener(Listener):
    def _requestWillBeSent(self, **kwargs):
        if not self._owner._is_diff_domain and kwargs.get('frameId') != self._owner._frame_id:
            return
        super()._requestWillBeSent(**kwargs)

    def _response_received(self, **kwargs):
        if not self._owner._is_diff_domain and kwargs.get('frameId') != self._owner._frame_id:
            return
        super()._response_received(**kwargs)


class DataPacket(object):
    type = 'DataPacket'

    def __init__(self, tab, target):
        self.tab = tab
        self.tab_id = tab.tab_id
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
        def do():
            if not self.tab._messenger_running or not self.tab.listen.listening:
                return False
            return None if self._responseExtraInfo is None else True

        if timeout is None:
            timeout = self.tab.timeout
        return wait_until(do, timeout=timeout)


class Request(object):
    def __init__(self, data_packet, raw_request, post_data):
        self._data_packet = data_packet
        self._request = raw_request
        self._raw_post_data = post_data
        self._postData = None
        self._headers = None

    def __getattr__(self, item):
        return self._request.get(item)

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
            elif self._request.get('postData'):
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
        return self._response.get(item) if self._response else None

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
        return self._extra_info.get(item)


class RequestExtraInfo(ExtraInfo):
    pass


class ResponseExtraInfo(ExtraInfo):
    pass


class FailInfo(object):
    def __init__(self, data_packet, fail_info):
        self._data_packet = data_packet
        self._fail_info = fail_info

    def __getattr__(self, item):
        return self._fail_info.get(item) if self._fail_info else None


class WebSocketConnectInfo(object):
    def __init__(self, tab, target, request_id, url, initiator=None):
        self.tab = tab
        self.tab_id = tab.tab_id
        self.target = target
        self.request_id = request_id
        self.url = url
        self.initiator = initiator
        self.request = None
        self.response = None


class WebSocketPacket(object):
    type = 'WebSocketPacket'
    resourceType = 'WebSocket'

    def __init__(self, tab, target, raw_data, is_sent):
        self.tab = tab
        self.tab_id = tab.tab_id
        self.target = target
        self.is_sent = is_sent
        self._raw_data = raw_data
        self._payload = None
        self._connect_info = None
        self._request_id = raw_data['requestId']

    def __repr__(self):
        direction = 'sent' if self.is_sent else 'received'
        return f'<WebSocketPacket {direction} requestId={self._request_id} timestamp={self.timestamp}>'

    @property
    def connect_info(self):
        return self._connect_info

    @property
    def timestamp(self):
        return self._raw_data['timestamp']

    @property
    def payload(self):
        if self._payload is None:
            payload = self._raw_data['response']
            if payload['opcode'] == 1:
                try:
                    self._payload = loads(payload['payloadData'])
                except (JSONDecodeError, TypeError):
                    self._payload = payload['payloadData']
            else:
                self._payload = b64decode(payload['payloadData'])
        return self._payload


class SSEPacket(object):
    type = 'SSEPacket'
    resourceType = 'EventSource'

    def __init__(self, tab, target, raw_data):
        self.tab = tab
        self.tab_id = tab.tab_id
        self.target = target
        self._raw_data = raw_data
        self._connect_info = None
        self._request_id = raw_data['requestId']

    def __repr__(self):
        return f'<SSEPacket requestId={self._request_id} timestamp={self.timestamp}>'

    @property
    def timestamp(self):
        return self._raw_data['timestamp']

    @property
    def name(self):
        return self._raw_data['eventName']

    @property
    def id(self):
        return self._raw_data['eventId']

    @property
    def data(self):
        return self._raw_data['data']

    @property
    def connect_info(self):
        return self._connect_info


class MethodSetter(object):
    _ALLOW = {'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'TRACE', 'CONNECT'}
    _REMOVE = {'remove_GET', 'remove_POST', 'remove_PUT', 'remove_DELETE', 'remove_HEAD', 'remove_OPTIONS',
               'remove_PATCH', 'remove_TRACE', 'remove_CONNECT'}
    _ATTR = '_method'

    def __init__(self, listener):
        self._listener = listener

    def all(self):
        setattr(self._listener, self._ATTR, True)
        return self

    def __getattr__(self, item):
        def _func(only=False):
            if item in self._ALLOW:
                i = item.upper()
                if only:
                    setattr(self._listener, self._ATTR, {i})
                elif getattr(self._listener, self._ATTR) is not True:
                    getattr(self._listener, self._ATTR).add(i)
                return self
            elif item in self._REMOVE:
                i = item.upper()
                if getattr(self._listener, self._ATTR) is True:
                    setattr(self._listener, self._ATTR, {i.upper() for i in self._ALLOW})
                getattr(self._listener, self._ATTR).discard(i[7:])
                return self
            raise ValueError()

        return _func


class ResTypeSetter(MethodSetter):
    _ALLOW = {'Document', 'Stylesheet', 'Image', 'Media', 'Font', 'Script', 'TextTrack', 'XHR', 'Fetch',
              'Prefetch', 'EventSource', 'WebSocket', 'Manifest', 'SignedExchange', 'Ping', 'CSPViolationReport',
              'Preflight', 'Other'}
    _REMOVE = {'remove_Document', 'remove_Stylesheet', 'remove_Image', 'remove_Media',
               'remove_Font', 'remove_Script', 'remove_TextTrack', 'remove_XHR', 'remove_Fetch', 'remove_Prefetch',
               'remove_EventSource', 'remove_WebSocket', 'remove_Manifest', 'remove_SignedExchange', 'remove_Ping',
               'remove_CSPViolationReport', 'remove_Preflight', 'remove_Other'}
    _ATTR = '_res_type'

    def ws(self, only=False):
        return self.__getattr__('WebSocket')(only=only)

    def remove_ws(self):
        return self.__getattr__('remove_WebSocket')()

    def sse(self, only=False):
        return self.__getattr__('EventSource')(only=only)

    def remove_sse(self):
        return self.__getattr__('remove_EventSource')()
