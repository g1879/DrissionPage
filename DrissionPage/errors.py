# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""


class BaseError(Exception):
    _info = None

    def __init__(self, ErrorInfo=None):
        self._info = ErrorInfo or self._info

    def __str__(self):
        return self._info


class ElementNotFoundError(BaseError):
    _info = '\n没有找到元素。'

    def __init__(self, ErrorInfo=None, method=None, arguments=None):
        super().__init__(ErrorInfo=ErrorInfo)
        self.method = method
        self.arguments = arguments

    def __str__(self):
        method = f'\nmethod: {self.method}' if self.method else ''
        arguments = f'\nargs: {self.arguments}' if self.arguments else ''
        return f'{self._info}{method}{arguments}'


class AlertExistsError(BaseError):
    _info = '存在未处理的提示框。'


class ContextLostError(BaseError):
    _info = '页面被刷新，请操作前尝试等待页面刷新或加载完成。'


class ElementLostError(BaseError):
    _info = '元素对象已失效。可能是页面整体刷新，或js局部刷新把元素替换或去除了。'


class CDPError(BaseError):
    _info = '方法调用错误。'


class PageDisconnectedError(BaseError):
    _info = '与页面的连接已断开。'


class JavaScriptError(BaseError):
    _info = 'JavaScript运行错误。'


class NoRectError(BaseError):
    _info = '该元素没有位置及大小。'


class BrowserConnectError(BaseError):
    _info = '浏览器连接失败。'


class NoResourceError(BaseError):
    _info = '该元素无可保存的内容或保存失败。'


class CanNotClickError(BaseError):
    _info = '该元素无法滚动到视口或被遮挡，无法点击。'


class GetDocumentError(BaseError):
    _info = '获取文档失败。'


class WaitTimeoutError(BaseError):
    _info = '等待失败。'


class WrongURLError(BaseError):
    _info = '无效的url。'


class StorageError(BaseError):
    _info = '无法操作当前存储数据。'


class CookieFormatError(BaseError):
    _info = 'cookie格式不正确。'


class TargetNotFoundError(BaseError):
    _info = '找不到指定页面。'
