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
        """
        :param ele: select 元素对象
        """
        if ele.tag != 'select':
            raise TypeError("select方法只能在<select>元素使用。")

        self._ele = ele

    def __call__(self, text_or_index, timeout=None):
        """选定下拉列表中子元素
        :param text_or_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param timeout: 超时时间（秒），不输入默认实用页面超时时间
        :return: None
        """
        para_type = 'index' if isinstance(text_or_index, int) else 'text'
        timeout = timeout if timeout is not None else self._ele.owner.timeout
        return self._select(text_or_index, para_type, timeout=timeout)

    @property
    def is_multi(self):
        """返回是否多选表单"""
        return self._ele.attr('multiple') is not None

    @property
    def options(self):
        """返回所有选项元素组成的列表"""
        return [i for i in self._ele.eles('xpath://option') if not isinstance(i, int)]

    @property
    def selected_option(self):
        """返回第一个被选中的option元素
        :return: ChromiumElement对象或None
        """
        ele = self._ele.run_js('return this.options[this.selectedIndex];')
        return ele

    @property
    def selected_options(self):
        """返回所有被选中的option元素列表
        :return: ChromiumElement对象组成的列表
        """
        return [x for x in self.options if x.states.is_selected]

    def all(self):
        """全选"""
        if not self.is_multi:
            raise TypeError("只能在多选菜单执行此操作。")
        return self._by_loc('tag:option', 1, False)

    def invert(self):
        """反选"""
        if not self.is_multi:
            raise TypeError("只能对多项选框执行反选。")
        change = False
        for i in self.options:
            change = True
            mode = 'false' if i.states.is_selected else 'true'
            i.run_js(f'this.selected={mode};')
        if change:
            self._dispatch_change()

    def clear(self):
        """清除所有已选项"""
        if not self.is_multi:
            raise TypeError("只能在多选菜单执行此操作。")
        return self._by_loc('tag:option', 1, True)

    def by_text(self, text, timeout=None):
        """此方法用于根据text值选择项。当元素是多选列表时，可以接收list或tuple
        :param text: text属性值，传入list或tuple可选择多项
        :param timeout: 超时时间（秒），为None默认使用页面超时时间
        :return: 是否选择成功
        """
        return self._select(text, 'text', False, timeout)

    def by_value(self, value, timeout=None):
        """此方法用于根据value值选择项。当元素是多选列表时，可以接收list或tuple
        :param value: value属性值，传入list或tuple可选择多项
        :param timeout: 超时时间，为None默认使用页面超时时间
        :return: 是否选择成功
        """
        return self._select(value, 'value', False, timeout)

    def by_index(self, index, timeout=None):
        """此方法用于根据index值选择项。当元素是多选列表时，可以接收list或tuple
        :param index: 序号，从1开始，可传入负数获取倒数第几个，传入list或tuple可选择多项
        :param timeout: 超时时间，为None默认使用页面超时时间
        :return: 是否选择成功
        """
        return self._select(index, 'index', False, timeout)

    def by_locator(self, locator, timeout=None):
        """用定位符选择指定的项
        :param locator: 定位符
        :param timeout: 超时时间
        :return: 是否选择成功
        """
        return self._by_loc(locator, timeout)

    def by_option(self, option):
        """选中单个或多个option元素
        :param option: option元素或它们组成的列表
        :return: None
        """
        self._select_options(option, 'true')

    def cancel_by_text(self, text, timeout=None):
        """此方法用于根据text值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param text: 文本，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        return self._select(text, 'text', True, timeout)

    def cancel_by_value(self, value, timeout=None):
        """此方法用于根据value值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param value: value属性值，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        return self._select(value, 'value', True, timeout)

    def cancel_by_index(self, index, timeout=None):
        """此方法用于根据index值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param index: 序号，从1开始，可传入负数获取倒数第几个，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否取消成功
        """
        return self._select(index, 'index', True, timeout)

    def cancel_by_locator(self, locator, timeout=None):
        """用定位符取消选择指定的项
        :param locator: 定位符
        :param timeout: 超时时间
        :return: 是否选择成功
        """
        return self._by_loc(locator, timeout, True)

    def cancel_by_option(self, option):
        """取消选中单个或多个option元素
        :param option: option元素或它们组成的列表
        :return: None
        """
        self._select_options(option, 'false')

    def _by_loc(self, loc, timeout=None, cancel=False):
        """用定位符取消选择指定的项
        :param loc: 定位符
        :param timeout: 超时时间
        :param cancel: 是否取消选择
        :return: 是否选择成功
        """
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
        """选定或取消选定下拉列表中子元素
        :param condition: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param cancel: 是否取消选择
        :return: 是否选择成功
        """
        if not self.is_multi and isinstance(condition, (list, tuple)):
            raise TypeError('单选列表只能传入str格式。')

        mode = 'false' if cancel else 'true'
        timeout = timeout if timeout is not None else self._ele.owner.timeout
        condition = set(condition) if isinstance(condition, (list, tuple)) else {condition}

        if para_type in ('text', 'value'):
            return self._text_value([str(i) for i in condition], para_type, mode, timeout)
        elif para_type == 'index':
            return self._index(condition, mode, timeout)

    def _text_value(self, condition, para_type, mode, timeout):
        """执行text和value搜索
        :param condition: 条件set
        :param para_type: 参数类型，可选 'text'、'value'
        :param mode: 'true' 或 'false'
        :param timeout: 超时时间
        :return: 是否选择成功
        """
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
        """执行index搜索
        :param condition: 条件set
        :param mode: 'true' 或 'false'
        :param timeout: 超时时间
        :return: 是否选择成功
        """
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
        """选中或取消某个选项
        :param option: options元素对象
        :param mode: 选中还是取消
        :return: None
        """
        if isinstance(option, (list, tuple, set)):
            if not self.is_multi and len(option) > 1:
                option = option[:1]
            for o in option:
                o.run_js(f'this.selected={mode};')
                self._dispatch_change()
        else:
            option.run_js(f'this.selected={mode};')
            self._dispatch_change()

    def _dispatch_change(self):
        """触发修改动作"""
        self._ele.run_js('this.dispatchEvent(new CustomEvent("change", {bubbles: true}));')
