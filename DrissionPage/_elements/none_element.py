# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from .._functions.settings import Settings
from ..errors import ElementNotFoundError


class NoneElement(object):
    def __init__(self, page=None, method=None, args=None):
        """
        :param page: 元素所在页面
        :param method: 查找元素的方法
        :param args: 查找元素的参数
        """
        if method and Settings.raise_when_ele_not_found:  # 无传入method时不自动抛出，由调用者处理
            raise ElementNotFoundError(None, method=method, arguments=args)

        if page:
            self._none_ele_value = page._none_ele_value
            self._none_ele_return_value = page._none_ele_return_value
        else:
            self._none_ele_value = None
            self._none_ele_return_value = False
        self.method = method
        self.args = args
        self._get = None

    def __call__(self, *args, **kwargs):
        if not self._none_ele_return_value:
            raise ElementNotFoundError(None, self.method, self.args)
        else:
            return self

    def __getattr__(self, item):
        if not self._none_ele_return_value:
            raise ElementNotFoundError(None, self.method, self.args)
        elif item in ('ele', 's_ele', 'parent', 'child', 'next', 'prev', 'before',
                      'after', 'get_frame', 'shadow_root', 'sr'):
            return self
        else:
            if item in ('size', 'link', 'css_path', 'xpath', 'comments', 'texts', 'tag', 'html', 'inner_html',
                        'attrs', 'text', 'raw_text', 'value', 'attr', 'style', 'src', 'property'):
                return self._none_ele_value
            else:
                raise ElementNotFoundError(None, self.method, self.args)

    def __eq__(self, other):
        if other is None:
            return True

    def __bool__(self):
        return False

    def __repr__(self):
        return 'None'
