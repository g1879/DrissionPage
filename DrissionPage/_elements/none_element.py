# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from ..errors import ElementNotFoundError


class NoneElement(object):
    def __init__(self, page=None, method=None, args=None):
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
