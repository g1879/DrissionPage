# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from time import perf_counter, sleep

from .locator import is_loc
from .._elements.none_element import NoneElement


class SessionElementsList(list):
    def __init__(self, owner=None, *args):
        super().__init__(*args)
        self._owner = owner

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
               have_rect=None, have_text=None, tag=None):
        return _search(self, displayed=displayed, checked=checked, selected=selected, enabled=enabled,
                       clickable=clickable, have_rect=have_rect, have_text=have_text, tag=tag)

    def search_one(self, index=1, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
                   have_rect=None, have_text=None, tag=None):
        return _search_one(self, index=index, displayed=displayed, checked=checked, selected=selected,
                           enabled=enabled, clickable=clickable, have_rect=have_rect, have_text=have_text, tag=tag)


class SessionFilterOne(object):
    def __init__(self, _list):
        self._list = _list
        self._index = 1

    def __call__(self, index=1):
        self._index = index
        return self

    def tag(self, name, equal=True):
        num = 0
        name = name.lower()
        if equal:
            for i in self._list:
                if not isinstance(i, str) and i.tag == name:
                    num += 1
                    if self._index == num:
                        return i
        else:
            for i in self._list:
                if not isinstance(i, str) and i.tag != name:
                    num += 1
                    if self._index == num:
                        return i
        return NoneElement(self._list._owner, 'tag()', args={'name': name, 'equal': equal, 'index': self._index})

    def attr(self, name, value, equal=True):
        return self._get_attr(name, value, 'attr', equal=equal)

    def text(self, text, fuzzy=True, contain=True):
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
        return NoneElement(self._list._owner, 'text()',
                           args={'text': text, 'fuzzy': fuzzy, 'contain': contain, 'index': self._index})

    def _get_attr(self, name, value, method, equal=True):
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
        return NoneElement(self._list._owner, f'{method}()',
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
        return self._list.get

    def tag(self, name, equal=True):
        self._list = _tag_all(self._list, SessionElementsList(owner=self._list._owner), name=name, equal=equal)
        return self

    def text(self, text, fuzzy=True, contain=True):
        self._list = _text_all(self._list, SessionElementsList(owner=self._list._owner),
                               text=text, fuzzy=fuzzy, contain=contain)
        return self

    def _get_attr(self, name, value, method, equal=True):
        self._list = _attr_all(self._list, SessionElementsList(owner=self._list._owner),
                               name=name, value=value, method=method, equal=equal)
        return self


class ChromiumFilterOne(SessionFilterOne):

    def displayed(self, equal=True):
        return self._any_state('is_displayed', equal=equal)

    def checked(self, equal=True):
        return self._any_state('is_checked', equal=equal)

    def selected(self, equal=True):
        return self._any_state('is_selected', equal=equal)

    def enabled(self, equal=True):
        return self._any_state('is_enabled', equal=equal)

    def clickable(self, equal=True):
        return self._any_state('is_clickable', equal=equal)

    def have_rect(self, equal=True):
        return self._any_state('has_rect', equal=equal)

    def style(self, name, value, equal=True):
        return self._get_attr(name, value, 'style', equal=equal)

    def property(self, name, value, equal=True):
        return self._get_attr(name, value, 'property', equal=equal)

    def _any_state(self, name, equal=True):
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
        return NoneElement(self._list._owner, f'{name}()', args={'equal': equal, 'index': self._index})


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
        return self._list.get

    def search_one(self, index=1, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
                   have_rect=None, have_text=None, tag=None):
        return _search_one(self._list, index=index, displayed=displayed, checked=checked, selected=selected,
                           enabled=enabled, clickable=clickable, have_rect=have_rect, have_text=have_text, tag=tag)

    def search(self, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
               have_rect=None, have_text=None, tag=None):
        return _search(self._list, displayed=displayed, checked=checked, selected=selected, enabled=enabled,
                       clickable=clickable, have_rect=have_rect, have_text=have_text, tag=tag)

    def tag(self, name, equal=True):
        self._list = _tag_all(self._list, ChromiumElementsList(owner=self._list._owner), name=name, equal=equal)
        return self

    def text(self, text, fuzzy=True, contain=True):
        self._list = _text_all(self._list, ChromiumElementsList(owner=self._list._owner),
                               text=text, fuzzy=fuzzy, contain=contain)
        return self

    def _get_attr(self, name, value, method, equal=True):
        self._list = _attr_all(self._list, ChromiumElementsList(owner=self._list._owner),
                               name=name, value=value, method=method, equal=equal)
        return self

    def _any_state(self, name, equal=True):
        r = ChromiumElementsList(owner=self._list._owner)
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
        return [e.link for e in self._list if not isinstance(e, str)]

    def texts(self):
        return [e if isinstance(e, str) else e.text for e in self._list]

    def attrs(self, name):
        return [e.attr(name) for e in self._list if not isinstance(e, str)]


def get_eles(locators, owner, any_one=False, first_ele=True, timeout=10):
    if isinstance(locators, str):
        locators = (locators,)
    res = {loc: None for loc in locators}

    if timeout == 0:
        for loc in locators:
            ele = owner._ele(loc, timeout=0, raise_err=False, index=1 if first_ele else None, method='find()')
            res[loc] = ele
            if ele and any_one:
                return res
        return res

    end_time = perf_counter() + timeout
    while perf_counter() <= end_time:
        for loc in locators:
            if res[loc]:
                continue
            ele = owner._ele(loc, timeout=0, raise_err=False, index=1 if first_ele else None, method='find()')
            res[loc] = ele
            if ele and any_one:
                return res
        if all(res.values()):
            return res
        sleep(.05)

    return res


def get_frame(owner, loc_ind_ele, timeout=None):
    if isinstance(loc_ind_ele, str):
        if not is_loc(loc_ind_ele):
            xpath = f'xpath://*[(name()="iframe" or name()="frame") and ' \
                    f'(@name="{loc_ind_ele}" or @id="{loc_ind_ele}")]'
        else:
            xpath = loc_ind_ele
        ele = owner._ele(xpath, timeout=timeout)
        if ele and ele._type != 'ChromiumFrame':
            raise TypeError('该定位符不是指向frame元素。')
        r = ele

    elif isinstance(loc_ind_ele, tuple):
        ele = owner._ele(loc_ind_ele, timeout=timeout)
        if ele and ele._type != 'ChromiumFrame':
            raise TypeError('该定位符不是指向frame元素。')
        r = ele

    elif isinstance(loc_ind_ele, int):
        if loc_ind_ele == 0:
            loc_ind_ele = 1
        elif loc_ind_ele < 0:
            loc_ind_ele = f'last()+{loc_ind_ele}+1'
        xpath = f'xpath:(//*[name()="frame" or name()="iframe"])[{loc_ind_ele}]'
        r = owner._ele(xpath, timeout=timeout)

    elif loc_ind_ele._type == 'ChromiumFrame':
        r = loc_ind_ele

    else:
        raise TypeError('必须传入定位符、iframe序号、id、name、ChromiumFrame对象其中之一。')

    if isinstance(r, NoneElement):
        r.method = 'get_frame()'
        r.args = {'loc_ind_ele': loc_ind_ele}
    return r


def _attr_all(src_list, aim_list, name, value, method, equal=True):
    if equal:
        for i in src_list:
            if not isinstance(i, str) and getattr(i, method)(name) == value:
                aim_list.append(i)
    else:
        for i in src_list:
            if not isinstance(i, str) and getattr(i, method)(name) != value:
                aim_list.append(i)
    return aim_list


def _tag_all(src_list, aim_list, name, equal=True):
    name = name.lower()
    if equal:
        for i in src_list:
            if not isinstance(i, str) and i.tag == name:
                aim_list.append(i)
    else:
        for i in src_list:
            if not isinstance(i, str) and i.tag != name:
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
            have_rect=None, have_text=None, tag=None):
    """或关系筛选元素
    :param displayed: 是否显示，bool，None为忽略该项
    :param checked: 是否被选中，bool，None为忽略该项
    :param selected: 是否被选择，bool，None为忽略该项
    :param enabled: 是否可用，bool，None为忽略该项
    :param clickable: 是否可点击，bool，None为忽略该项
    :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
    :param have_text: 是否含有文本，bool，None为忽略该项
    :param tag: 元素类型
    :return: 筛选结果
    """
    r = ChromiumElementsList(owner=_list._owner)
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
                    or (have_text is False and not i.raw_text))
                or (tag is not None and i.tag == tag.lower())):
            r.append(i)
    return ChromiumFilter(r)


def _search_one(_list, index=1, displayed=None, checked=None, selected=None, enabled=None, clickable=None,
                have_rect=None, have_text=None, tag=None):
    """或关系筛选元素，获取一个结果
    :param index: 元素序号，从1开始
    :param displayed: 是否显示，bool，None为忽略该项
    :param checked: 是否被选中，bool，None为忽略该项
    :param selected: 是否被选择，bool，None为忽略该项
    :param enabled: 是否可用，bool，None为忽略该项
    :param clickable: 是否可点击，bool，None为忽略该项
    :param have_rect: 是否拥有大小和位置，bool，None为忽略该项
    :param have_text: 是否含有文本，bool，None为忽略该项
    :param tag: 元素类型
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
                    or (have_text is False and not i.raw_text))
                or (tag is not None and i.tag == tag.lower())):
            num += 1
            if num == index:
                return i

    return NoneElement(_list._owner, method='filter()', args={'displayed': displayed, 'checked': checked,
                                                              'selected': selected, 'enabled': enabled,
                                                              'clickable': clickable, 'have_rect': have_rect,
                                                              'have_text': have_text, 'tag': tag})
