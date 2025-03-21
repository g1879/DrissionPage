# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from ._functions.settings import Settings as _S


class BaseError(Exception):

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._args = args if args else [_S._lang.get(self.__class__.__name__.upper())]

    def __str__(self):
        return _S._lang.join(*self._args, **self._kwargs)


class ElementNotFoundError(BaseError):
    pass


class AlertExistsError(BaseError):
    pass


class ContextLostError(BaseError):
    pass


class ElementLostError(BaseError):
    pass


class CDPError(BaseError):
    pass


class PageDisconnectedError(BaseError):
    pass


class JavaScriptError(BaseError):
    pass


class NoRectError(BaseError):
    pass


class BrowserConnectError(BaseError):
    pass


class NoResourceError(BaseError):
    pass


class CanNotClickError(BaseError):
    pass


class GetDocumentError(BaseError):
    pass


class WaitTimeoutError(BaseError):
    pass


class IncorrectURLError(BaseError):
    pass


class StorageError(BaseError):
    pass


class CookieFormatError(BaseError):
    pass


class TargetNotFoundError(BaseError):
    pass


class LocatorError(BaseError):
    pass


class UnknownError(BaseError):
    pass
