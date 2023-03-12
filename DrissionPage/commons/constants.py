# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from DrissionPage.errors import ElementNotFoundError

HANDLE_ALERT_METHOD = 'Page.handleJavaScriptDialog'
FRAME_ELEMENT = ('iframe', 'frame')
ERROR = 'error'


class Settings(object):
    raise_ele_not_found = False


class NoneElement(object):
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(NoneElement, cls).__new__(cls)
        return cls._instance

    def __call__(self, *args, **kwargs):
        raise ElementNotFoundError

    def __getattr__(self, item):
        raise ElementNotFoundError

    def __eq__(self, other):
        if other is None:
            return True

    def __bool__(self):
        return False

    def __repr__(self):
        return 'None'
