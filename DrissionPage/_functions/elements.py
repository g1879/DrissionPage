# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from time import perf_counter

from .._elements.none_element import NoneElement


class SessionElementsList(list):
    def __init__(self, page=None, *args):
        super().__init__(*args)
        self._page = page

    @property
    def get(self):
        return Getter(self)

    @property
    def filter(self):
        return SessionFilter(self)

    @property
    def filter_one(self):
        return SessionFilterOne(self)


class ChromiumElementsList(SessionElementsList):

    @property
    def filter(self):
        return ChromiumFilter(self)

    @property
    def filter_one(self):
        return ChromiumFilterOne(self)

    def search(self, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
               have_rect=None, have_text=None):
        """或关系筛选元素
        :param displayed: 是否显示，bool，None为忽略该项
        :param checked: 是否被选中，bool，None为忽略该项
        :param selected: 是否被选择，bool，None为忽略该项
        :param enabled: 是否可用，bool，None为忽略该项
        :param clickable: 是否可点击，bool，None为忽略该项
        :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
        :param have_text: 是否含有文本，bool，None为忽略该项
        :return: 筛选结果
        """
        return _search(self, displayed=displayed, checked=checked, selected=selected, enabled=enabled,
                       clickable=clickable, have_rect=have_rect, have_text=have_text)

    def search_one(self, index=1, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
                   have_rect=None, have_text=None):
        """或关系筛选元素，获取一个结果
        :param index: 元素序号，从1开始
        :param displayed: 是否显示，bool，None为忽略该项
        :param checked: 是否被选中，bool，None为忽略该项
        :param selected: 是否被选择，bool，None为忽略该项
        :param enabled: 是否可用，bool，None为忽略该项
        :param clickable: 是否可点击，bool，None为忽略该项
        :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
        :param have_text: 是否含有文本，bool，None为忽略该项
        :return: 筛选结果
        """
        return _search_one(self, index=index, displayed=displayed, checked=checked, selected=selected,
                           enabled=enabled, clickable=clickable, have_rect=have_rect, have_text=have_text)


class SessionFilterOne(object):
    def __init__(self, _list):
        self._list = _list
        self._index = 1

    def __call__(self, index=1):
        """返回结果中第几个元素
        :param index: 元素序号，从1开始
        :return: 对象自身
        """
        self._index = index
        return self

    def attr(self, name, value, equal=True):
        """以是否拥有某个attribute值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        return self._get_attr(name, value, 'attr', equal=equal)

    def text(self, text, fuzzy=True, contain=True):
        """以是否含有指定文本为条件筛选元素
        :param text: 用于匹配的文本
        :param fuzzy: 是否模糊匹配
        :param contain: 是否包含该字符串，False表示不包含
        :return: 筛选结果
        """
        num = 0
        if contain:
            for i in self._list:
                t = i if isinstance(i, str) else i.raw_text
                if (fuzzy and text in t) or (not fuzzy and text == t):
                    num += 1
                    if self._index == num:
                        return i
        else:
            for i in self._list:
                t = i if isinstance(i, str) else i.raw_text
                if (fuzzy and text not in t) or (not fuzzy and text != t):
                    num += 1
                    if self._index == num:
                        return i
        return NoneElement(self._list._page, 'text()',
                           args={'text': text, 'fuzzy': fuzzy, 'contain': contain, 'index': self._index})

    def _get_attr(self, name, value, method, equal=True):
        """返回通过某个方法可获得某个值的元素
        :param name: 属性名称
        :param value: 属性值
        :param method: 方法名称
        :return: 筛选结果
        """
        num = 0
        if equal:
            for i in self._list:
                if not isinstance(i, str) and getattr(i, method)(name) == value:
                    num += 1
                    if self._index == num:
                        return i
        else:
            for i in self._list:
                if not isinstance(i, str) and getattr(i, method)(name) != value:
                    num += 1
                    if self._index == num:
                        return i
        return NoneElement(self._list._page, f'{method}()',
                           args={'name': name, 'value': value, 'equal': equal, 'index': self._index})


class SessionFilter(SessionFilterOne):

    def __iter__(self):
        return iter(self._list)

    def __next__(self):
        return next(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, item):
        return self._list[item]

    @property
    def get(self):
        """返回用于获取元素属性的对象"""
        return self._list.get

    def text(self, text, fuzzy=True, contain=True):
        """以是否含有指定文本为条件筛选元素
        :param text: 用于匹配的文本
        :param fuzzy: 是否模糊匹配
        :param contain: 是否包含该字符串，False表示不包含
        :return: 筛选结果
        """
        self._list = _text_all(self._list, SessionElementsList(page=self._list._page),
                               text=text, fuzzy=fuzzy, contain=contain)

    def _get_attr(self, name, value, method, equal=True):
        """返回通过某个方法可获得某个值的元素
        :param name: 属性名称
        :param value: 属性值
        :param method: 方法名称
        :return: 筛选结果
        """
        self._list = _get_attr_all(self._list, SessionElementsList(page=self._list._page),
                                   name=name, value=value, method=method, equal=equal)
        return self


class ChromiumFilterOne(SessionFilterOne):

    def displayed(self, equal=True):
        """以是否显示为条件筛选元素
        :param equal: 是否匹配显示的元素，False匹配不显示的
        :return: 筛选结果
        """
        return self._any_state('is_displayed', equal=equal)

    def checked(self, equal=True):
        """以是否被选中为条件筛选元素
        :param equal: 是否匹配被选中的元素，False匹配不被选中的
        :return: 筛选结果
        """
        return self._any_state('is_checked', equal=equal)

    def selected(self, equal=True):
        """以是否被选择为条件筛选元素，用于<select>元素项目
        :param equal: 是否匹配被选择的元素，False匹配不被选择的
        :return: 筛选结果
        """
        return self._any_state('is_selected', equal=equal)

    def enabled(self, equal=True):
        """以是否可用为条件筛选元素
        :param equal: 是否匹配可用的元素，False表示匹配disabled状态的
        :return: 筛选结果
        """
        return self._any_state('is_enabled', equal=equal)

    def clickable(self, equal=True):
        """以是否可点击为条件筛选元素
        :param equal: 是否匹配可点击的元素，False表示匹配不是可点击的
        :return: 筛选结果
        """
        return self._any_state('is_clickable', equal=equal)

    def have_rect(self, equal=True):
        """以是否有大小为条件筛选元素
        :param equal: 是否匹配有大小的元素，False表示匹配没有大小的
        :return: 筛选结果
        """
        return self._any_state('has_rect', equal=equal)

    def style(self, name, value, equal=True):
        """以是否拥有某个style值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        return self._get_attr(name, value, 'style', equal=equal)

    def property(self, name, value, equal=True):
        """以是否拥有某个property值为条件筛选元素
        :param name: 属性名称
        :param value: 属性值
        :param equal: True表示匹配name值为value值的元素，False表示匹配name值不为value值的
        :return: 筛选结果
        """
        return self._get_attr(name, value, 'property', equal=equal)

    def _any_state(self, name, equal=True):
        """
        :param name: 状态名称
        :param equal: 是否是指定状态，False表示否定状态
        :return: 选中的元素
        """
        num = 0
        if equal:
            for i in self._list:
                if not isinstance(i, str) and getattr(i.states, name):
                    num += 1
                    if self._index == num:
                        return i
        else:
            for i in self._list:
                if not isinstance(i, str) and not getattr(i.states, name):
                    num += 1
                    if self._index == num:
                        return i
        return NoneElement(self._list._page, f'{name}()', args={'equal': equal, 'index': self._index})


class ChromiumFilter(ChromiumFilterOne):

    def __iter__(self):
        return iter(self._list)

    def __next__(self):
        return next(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, item):
        return self._list[item]

    @property
    def get(self):
        """返回用于获取元素属性的对象"""
        return self._list.get

    def search_one(self, index=1, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
                   have_rect=None, have_text=None):
        """或关系筛选元素，获取一个结果
        :param index: 元素序号，从1开始
        :param displayed: 是否显示，bool，None为忽略该项
        :param checked: 是否被选中，bool，None为忽略该项
        :param selected: 是否被选择，bool，None为忽略该项
        :param enabled: 是否可用，bool，None为忽略该项
        :param clickable: 是否可点击，bool，None为忽略该项
        :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
        :param have_text: 是否含有文本，bool，None为忽略该项
        :return: 筛选结果
        """
        return _search_one(self._list, index=index, displayed=displayed, checked=checked, selected=selected,
                           enabled=enabled, clickable=clickable, have_rect=have_rect, have_text=have_text)

    def search(self, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
               have_rect=None, have_text=None):
        """或关系筛选元素
        :param displayed: 是否显示，bool，None为忽略该项
        :param checked: 是否被选中，bool，None为忽略该项
        :param selected: 是否被选择，bool，None为忽略该项
        :param enabled: 是否可用，bool，None为忽略该项
        :param clickable: 是否可点击，bool，None为忽略该项
        :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
        :param have_text: 是否含有文本，bool，None为忽略该项
        :return: 筛选结果
        """
        return _search(self._list, displayed=displayed, checked=checked, selected=selected, enabled=enabled,
                       clickable=clickable, have_rect=have_rect, have_text=have_text)

    def text(self, text, fuzzy=True, contain=True):
        """以是否含有指定文本为条件筛选元素
        :param text: 用于匹配的文本
        :param fuzzy: 是否模糊匹配
        :param contain: 是否包含该字符串，False表示不包含
        :return: 筛选结果
        """
        self._list = _text_all(self._list, ChromiumElementsList(page=self._list._page),
                               text=text, fuzzy=fuzzy, contain=contain)
        return self

    def _get_attr(self, name, value, method, equal=True):
        """返回通过某个方法可获得某个值的元素
        :param name: 属性名称
        :param value: 属性值
        :param method: 方法名称
        :return: 筛选结果
        """
        self._list = _get_attr_all(self._list, ChromiumElementsList(page=self._list._page),
                                   name=name, value=value, method=method, equal=equal)
        return self

    def _any_state(self, name, equal=True):
        """
        :param name: 状态名称
        :param equal: 是否是指定状态，False表示否定状态
        :return: 选中的列表
        """
        r = ChromiumElementsList(page=self._list._page)
        if equal:
            for i in self._list:
                if not isinstance(i, str) and getattr(i.states, name):
                    r.append(i)
        else:
            for i in self._list:
                if not isinstance(i, str) and not getattr(i.states, name):
                    r.append(i)
        self._list = r
        return self


class Getter(object):
    def __init__(self, _list):
        self._list = _list

    def links(self):
        """返回所有元素的link属性组成的列表"""
        return [e.link for e in self._list if not isinstance(e, str)]

    def texts(self):
        """返回所有元素的text属性组成的列表"""
        return [e if isinstance(e, str) else e.text for e in self._list]

    def attrs(self, name):
        """返回所有元素指定的attr属性组成的列表
        :param name: 属性名称
        :return: 属性文本组成的列表
        """
        return [e.attr(name) for e in self._list if not isinstance(e, str)]


def get_eles(locators, owner, any_one=False, first_ele=True, timeout=10):
    """传入多个定位符，获取多个ele
    :param locators: 定位符组成的列表
    :param owner: 页面或元素对象
    :param any_one: 是否找到任何一个即返回
    :param first_ele: 每个定位符是否只获取第一个元素
    :param timeout: 超时时间（秒）
    :return: 多个定位符组成的dict
    """
    res = {loc: False for loc in locators}
    end_time = perf_counter() + timeout
    while perf_counter() <= end_time:
        for loc in locators:
            if res[loc] is not False:
                continue
            ele = owner.ele(loc, timeout=0) if first_ele else owner.eles(loc, timeout=0)
            if ele:
                res[loc] = ele
                if any_one:
                    return res
        if False not in res.values():
            break
    return res


def _get_attr_all(src_list, aim_list, name, value, method, equal=True):
    if equal:
        for i in src_list:
            if not isinstance(i, str) and getattr(i, method)(name) == value:
                aim_list.append(i)
    else:
        for i in src_list:
            if not isinstance(i, str) and getattr(i, method)(name) != value:
                aim_list.append(i)
    return aim_list


def _text_all(src_list, aim_list, text, fuzzy=True, contain=True):
    """以是否含有指定文本为条件筛选元素
    :param text: 用于匹配的文本
    :param fuzzy: 是否模糊匹配
    :param contain: 是否包含该字符串，False表示不包含
    :return: 筛选结果
    """
    if contain:
        for i in src_list:
            t = i if isinstance(i, str) else i.raw_text
            if (fuzzy and text in t) or (not fuzzy and text == t):
                aim_list.append(i)
    else:
        for i in src_list:
            t = i if isinstance(i, str) else i.raw_text
            if (fuzzy and text not in t) or (not fuzzy and text != t):
                aim_list.append(i)
    return aim_list


def _search(_list, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
            have_rect=None, have_text=None):
    """或关系筛选元素
    :param displayed: 是否显示，bool，None为忽略该项
    :param checked: 是否被选中，bool，None为忽略该项
    :param selected: 是否被选择，bool，None为忽略该项
    :param enabled: 是否可用，bool，None为忽略该项
    :param clickable: 是否可点击，bool，None为忽略该项
    :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
    :param have_text: 是否含有文本，bool，None为忽略该项
    :return: 筛选结果
    """
    r = ChromiumElementsList(page=_list._page)
    for i in _list:
        if not isinstance(i, str) and (
                (displayed is not None and (displayed is True and i.states.is_displayed)
                 or (displayed is False and not i.states.is_displayed))
                or (checked is not None and (checked is True and i.states.is_checked)
                    or (checked is False and not i.states.is_checked))
                or (selected is not None and (selected is True and i.states.is_selected)
                    or (selected is False and not i.states.is_selected))
                or (enabled is not None and (enabled is True and i.states.is_enabled)
                    or (enabled is False and not i.states.is_enabled))
                or (clickable is not None and (clickable is True and i.states.is_clickable)
                    or (clickable is False and not i.states.is_clickable))
                or (have_rect is not None and (have_rect is True and i.states.has_rect)
                    or (have_rect is False and not i.states.has_rect))
                or (have_text is not None and (have_text is True and i.raw_text)
                    or (have_text is False and not i.raw_text))):
            r.append(i)
    return ChromiumFilter(r)


def _search_one(_list, index=1, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
                have_rect=None, have_text=None):
    """或关系筛选元素，获取一个结果
    :param index: 元素序号，从1开始
    :param displayed: 是否显示，bool，None为忽略该项
    :param checked: 是否被选中，bool，None为忽略该项
    :param selected: 是否被选择，bool，None为忽略该项
    :param enabled: 是否可用，bool，None为忽略该项
    :param clickable: 是否可点击，bool，None为忽略该项
    :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
    :param have_text: 是否含有文本，bool，None为忽略该项
    :return: 筛选结果
    """
    num = 0
    for i in _list:
        if not isinstance(i, str) and (
                (displayed is not None and (displayed is True and i.states.is_displayed)
                 or (displayed is False and not i.states.is_displayed))
                or (checked is not None and (checked is True and i.states.is_checked)
                    or (checked is False and not i.states.is_checked))
                or (selected is not None and (selected is True and i.states.is_selected)
                    or (selected is False and not i.states.is_selected))
                or (enabled is not None and (enabled is True and i.states.is_enabled)
                    or (enabled is False and not i.states.is_enabled))
                or (clickable is not None and (clickable is True and i.states.is_clickable)
                    or (clickable is False and not i.states.is_clickable))
                or (have_rect is not None and (have_rect is True and i.states.has_rect)
                    or (have_rect is False and not i.states.has_rect))
                or (have_text is not None and (have_text is True and i.raw_text)
                    or (have_text is False and not i.raw_text))):
            num += 1
            if num == index:
                return i

    return NoneElement(_list._page, method='filter()', args={'displayed': displayed,
                                                             'checked': checked, 'selected': selected,
                                                             'enabled': enabled, 'clickable': clickable,
                                                             'have_rect': have_rect, 'have_text': have_text})
