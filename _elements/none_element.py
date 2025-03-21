# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from .._functions.settings import Settings
from ..errors import ElementNotFoundError


class NoneElement(object):
    def __init__(self, page=None, method=None, args=None):
        if method and Settings.raise_when_ele_not_found:  # 无传入method时不自动抛出，由调用者处理
            raise ElementNotFoundError(METHOD=method, ARGS=args)

        if page:
            self._none_ele_value = page._none_ele_value
            self._none_ele_return_value = page._none_ele_return_value
        else:
            self._none_ele_value = None
            self._none_ele_return_value = False
        self.method = method
        self.args = {} if args is None else args

    def __call__(self, *args, **kwargs):
        if not self._none_ele_return_value:
            raise ElementNotFoundError(METHOD=self.method, ARGS=self.args)
        else:
            return self

    def __repr__(self):
        return f'<NoneElement method={self.method}, {", ".join([f"{k}={v}" for k, v in self.args.items()])}>'

    def __getattr__(self, item):
        if not self._none_ele_return_value:
            raise ElementNotFoundError(METHOD=self.method, ARGS=self.args)
        elif item in ('ele', 's_ele', 'parent', 'child', 'next', 'prev', 'before', 'east', 'north', 'south', 'west',
                      'offset', 'over', 'after', 'get_frame', 'shadow_root', 'sr'):
            return self
        else:
            if item in ('size', 'link', 'css_path', 'xpath', 'comments', 'texts', 'tag', 'html', 'inner_html',
                        'attrs', 'text', 'raw_text', 'value', 'attr', 'style', 'src', 'property'):
                return self._none_ele_value
            else:
                raise ElementNotFoundError(METHOD=self.method, ARGS=self.args)

    def __eq__(self, other):
        return other is None

    def __bool__(self):
        return False
