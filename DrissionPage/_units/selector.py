# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from time import perf_counter, sleep


class SelectElement(object):
    """用于处理 select 标签"""

    def __init__(self, ele):
        if ele.tag != 'select':
            raise TypeError("select方法只能在<select>元素使用。")
        self._ele = ele

    def __call__(self, text_or_index, timeout=None):
        para_type = 'index' if isinstance(text_or_index, int) else 'text'
        if timeout is None:
            timeout = self._ele.timeout
        return self._select(text_or_index, para_type, timeout=timeout)

    @property
    def is_multi(self):
        return self._ele.attr('multiple') is not None

    @property
    def options(self):
        return [i for i in self._ele.eles('xpath://option') if not isinstance(i, int)]

    @property
    def selected_option(self):
        ele = self._ele._run_js('return this.options[this.selectedIndex];')
        return ele

    @property
    def selected_options(self):
        return [x for x in self.options if x.states.is_selected]

    def all(self):
        if not self.is_multi:
            raise TypeError("只能在多选菜单执行此操作。")
        return self._by_loc('tag:option', 1, False)

    def invert(self):
        if not self.is_multi:
            raise TypeError("只能对多项选框执行反选。")
        change = False
        for i in self.options:
            change = True
            mode = 'false' if i.states.is_selected else 'true'
            i._run_js(f'this.selected={mode};')
        if change:
            self._dispatch_change()

    def clear(self):
        if not self.is_multi:
            raise TypeError("只能在多选菜单执行此操作。")
        return self._by_loc('tag:option', 1, True)

    def by_text(self, text, timeout=None):
        return self._select(text, 'text', False, timeout)

    def by_value(self, value, timeout=None):
        return self._select(value, 'value', False, timeout)

    def by_index(self, index, timeout=None):
        return self._select(index, 'index', False, timeout)

    def by_locator(self, locator, timeout=None):
        return self._by_loc(locator, timeout)

    def by_option(self, option):
        self._select_options(option, 'true')

    def cancel_by_text(self, text, timeout=None):
        return self._select(text, 'text', True, timeout)

    def cancel_by_value(self, value, timeout=None):
        return self._select(value, 'value', True, timeout)

    def cancel_by_index(self, index, timeout=None):
        return self._select(index, 'index', True, timeout)

    def cancel_by_locator(self, locator, timeout=None):
        return self._by_loc(locator, timeout, True)

    def cancel_by_option(self, option):
        self._select_options(option, 'false')

    def _by_loc(self, loc, timeout=None, cancel=False):
        eles = self._ele.eles(loc, timeout)
        if not eles:
            return False

        mode = 'false' if cancel else 'true'
        if self.is_multi:
            self._select_options(eles, mode)
        else:
            self._select_options(eles[0], mode)
        return True

    def _select(self, condition, para_type='text', cancel=False, timeout=None):
        if not self.is_multi and isinstance(condition, (list, tuple)):
            raise TypeError('单选列表只能传入str格式。')

        mode = 'false' if cancel else 'true'
        if timeout is None:
            timeout = self._ele.timeout
        condition = set(condition) if isinstance(condition, (list, tuple)) else {condition}

        if para_type in ('text', 'value'):
            return self._text_value([str(i) for i in condition], para_type, mode, timeout)
        elif para_type == 'index':
            return self._index(condition, mode, timeout)

    def _text_value(self, condition, para_type, mode, timeout):
        ok = False
        text_len = len(condition)
        eles = []
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if para_type == 'text':
                eles = [i for i in self.options if i.text in condition]
            elif para_type == 'value':
                eles = [i for i in self.options if i.attr('value') in condition]

            if len(eles) >= text_len:
                ok = True
                break
            sleep(.01)

        if ok:
            self._select_options(eles, mode)
            return True

        return False

    def _index(self, condition, mode, timeout):
        ok = False
        condition = [int(i) for i in condition]
        text_len = abs(max(condition, key=abs))
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if len(self.options) >= text_len:
                ok = True
                break
            sleep(.01)

        if ok:
            eles = self.options
            eles = [eles[i - 1] if i > 0 else eles[i] for i in condition]
            self._select_options(eles, mode)
            return True

        return False

    def _select_options(self, option, mode):
        if isinstance(option, (list, tuple, set)):
            if not self.is_multi and len(option) > 1:
                option = option[:1]
            for o in option:
                o._run_js(f'this.selected={mode};')
                self._dispatch_change()
        else:
            option._run_js(f'this.selected={mode};')
            self._dispatch_change()

    def _dispatch_change(self):
        self._ele._run_js('this.dispatchEvent(new CustomEvent("change", {bubbles: true}));')
