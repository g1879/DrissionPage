# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from re import split

from .by import By
from .._functions.settings import Settings as _S
from ..errors import LocatorError


def locator_to_tuple(loc):
    loc = _preprocess(loc)

    # 多属性查找
    if loc.startswith(('@@', '@|', '@!')) and loc not in ('@@', '@|', '@!'):
        args = _get_args(loc)

    # 单属性查找
    elif loc.startswith('@') and loc != '@':
        arg = _get_arg(loc[1:])
        arg.append(False)
        args = {'and': True, 'args': [arg]}

    # 根据tag name查找
    elif loc.startswith(('tag:', 'tag=', 'tag^', 'tag$')) and loc not in ('tag:', 'tag=', 'tag^', 'tag$'):
        at_ind = loc.find('@')
        if at_ind == -1:
            args = {'and': True, 'args': [['tag()', '=', loc[4:].lower(), False]]}
        else:
            args_str = loc[at_ind:]
            if args_str.startswith(('@@', '@|', '@!')):
                args = _get_args(args_str)
                args['args'].append([f'tag()', '=', loc[4:at_ind].lower(), False])
            else:  # t:div@aa=bb的格式
                arg = _get_arg(loc[at_ind + 1:])
                arg.append(False)
                args = {'and': True, 'args': [['tag()', '=', loc[4:at_ind].lower(), False], arg]}

    # 根据文本查找
    elif loc.startswith(('text=', 'text:', 'text^', 'text$')):
        args = {'and': True, 'args': [['text()', loc[4], loc[5:], False]]}

    # 根据文本模糊查找
    else:
        args = {'and': True, 'args': [['text()', '=', loc, False]]}

    return args


def _get_args(text: str = '') -> dict:
    """解析定位参数字符串生成dict格式数据
    :param text: 待处理的字符串
    :return: 格式： {'and': bool, 'args': ['属性名称', '匹配方式', '属性值', 是否否定]}
    """
    arg_list = []
    args = split(r'(@!|@@|@\|)', text)[1:]
    if '@@' in args and '@|' in args:
        raise LocatorError(_S._lang.SYMBOL_CONFLICT, VALUE=text)
    _and = '@|' not in args

    for k in range(0, len(args) - 1, 2):
        arg = _get_arg(args[k + 1])
        if arg:
            arg.append(True if args[k] == '@!' else False)  # 是否去除某个属性
        arg_list.append(arg)

    return {'and': _and, 'args': arg_list}


def _get_arg(text) -> list:
    """解析arg=abc格式字符串，生成格式：['属性名称', '匹配方式', '属性值', 是否否定]，不是式子的返回None"""
    r = split(r'([:=$^])', text, maxsplit=1)
    if not r[0]:
        return [None, None, None, None]
    # !=时只有属性名没有属性内容，查询是否存在该属性
    name = r[0] if r[0] != 'tx()' else 'text()'
    name = name if name != 't()' else 'teg()'
    return [name, None, None] if len(r) != 3 else [name, r[1], r[2]]


def is_str_loc(text):
    return text.startswith(('.', '#', '@', 't:', 't=', 'tag:', 'tag=', 'tx:', 'tx=', 'tx^', 'tx$', 'text:', 'text=',
                            'text^', 'text$', 'xpath:', 'xpath=', 'x:', 'x=', 'css:', 'css=', 'c:', 'c='))


def is_selenium_loc(loc):
    return (isinstance(loc, tuple) and len(loc) == 2 and loc[0].lower() in (
        'id', 'xpath', 'link text', 'partial link text', 'name', 'tag name', 'class name', 'css selector')
            and isinstance(loc[1], str))


def get_loc(loc, translate_css=False, css_mode=False):
    if isinstance(loc, tuple):
        loc = translate_css_loc(loc) if css_mode else translate_loc(loc)

    elif isinstance(loc, str):
        loc = str_to_css_loc(loc) if css_mode else str_to_xpath_loc(loc)

    else:
        raise LocatorError(ALLOW_TYPE=_S._lang.LOC_FORMAT, CURR_VAL=loc)

    if loc[0] == 'css selector' and translate_css:
        from lxml.cssselect import CSSSelector, ExpressionError
        try:
            path = str(CSSSelector(loc[1], translator='html').path)
            path = path[20:] if path.startswith('descendant-or-self::') else path
            loc = 'xpath', path
        except ExpressionError:
            pass

    return loc


def str_to_xpath_loc(loc):
    loc_by = 'xpath'
    loc = _preprocess(loc)

    # 多属性查找
    if loc.startswith(('@@', '@|', '@!')) and loc not in ('@@', '@|', '@!'):
        loc_str = _make_multi_xpath_str('*', loc)[1]

    # 单属性查找
    elif loc.startswith('@') and loc != '@':
        loc_str = _make_single_xpath_str('*', loc)[1]

    # 根据tag name查找
    elif loc.startswith(('tag:', 'tag=', 'tag^', 'tag$')) and loc not in ('tag:', 'tag=', 'tag^', 'tag$'):
        at_ind = loc.find('@')
        if at_ind == -1:
            loc_str = f'//*[name()="{loc[4:]}"]'
        elif loc[at_ind:].startswith(('@@', '@|', '@!')):
            loc_str = _make_multi_xpath_str(loc[4:at_ind], loc[at_ind:])[1]
        else:
            loc_str = _make_single_xpath_str(loc[4:at_ind], loc[at_ind:])[1]

    # 根据文本查找
    elif loc.startswith('text='):
        loc_str = f'//*[text()={_quotes_escape(loc[5:])}]'
    elif loc.startswith('text:') and loc != 'text:':
        loc_str = f'//*/text()[contains(., {_quotes_escape(loc[5:])})]/..'
    elif loc.startswith('text^') and loc != 'text^':
        loc_str = f'//*/text()[starts-with(., {_quotes_escape(loc[5:])})]/..'
    elif loc.startswith('text$') and loc != 'text$':
        loc_str = (f'//*/text()[substring(., string-length(.) - string-length({_quotes_escape(loc[5:])}) +1) = '
                   f'{_quotes_escape(loc[5:])}]/..')

    # 用xpath查找
    elif loc.startswith(('xpath:', 'xpath=')) and loc not in ('xpath:', 'xpath='):
        loc_str = loc[6:]

    # 用css selector查找
    elif loc.startswith(('css:', 'css=')) and loc not in ('css:', 'css='):
        loc_by = 'css selector'
        loc_str = loc[4:]

    # 根据文本模糊查找
    elif loc:
        loc_str = f'//*/text()[contains(., {_quotes_escape(loc)})]/..'
    else:
        loc_str = '//*'

    return loc_by, loc_str


def str_to_css_loc(loc):
    loc_by = 'css selector'
    loc = _preprocess(loc)

    # 多属性查找
    if loc.startswith(('@@', '@|', '@!')) and loc not in ('@@', '@|', '@!'):
        loc_str = _make_multi_css_str('*', loc)[1]

    # 单属性查找
    elif loc.startswith('@') and loc != '@':
        loc_by, loc_str = _make_single_css_str('*', loc)

    # 根据tag name查找
    elif loc.startswith(('tag:', 'tag=', 'tag^', 'tag$')) and loc not in ('tag:', 'tag=', 'tag^', 'tag$'):
        at_ind = loc.find('@')
        if at_ind == -1:
            loc_str = loc[4:]
        elif loc[at_ind:].startswith(('@@', '@|', '@!')):
            loc_by, loc_str = _make_multi_css_str(loc[4:at_ind], loc[at_ind:])
        else:
            loc_by, loc_str = _make_single_css_str(loc[4:at_ind], loc[at_ind:])

    # 根据文本查找
    elif loc.startswith(('text=', 'text:', 'text^', 'text$', 'xpath=', 'xpath:')):
        loc_by, loc_str = str_to_xpath_loc(loc)

    # 用css selector查找
    elif loc.startswith(('css:', 'css=')) and loc not in ('css:', 'css='):
        loc_str = loc[4:]

    # 根据文本模糊查找
    elif loc:
        loc_by, loc_str = str_to_xpath_loc(loc)

    else:
        loc_str = '*'

    return loc_by, loc_str


def _make_single_xpath_str(tag: str, text: str) -> tuple:
    """生成单属性xpath语句
    :param tag: 标签名
    :param text: 待处理的字符串
    :return: xpath字符串
    """
    arg_list = [] if tag == '*' else [f'name()="{tag}"']
    arg_str = txt_str = ''

    if text == '@':
        arg_str = 'not(@*)'

    else:
        r = split(r'([:=$^])', text, maxsplit=1)
        len_r = len(r)
        len_r0 = len(r[0])
        if len_r == 3 and len_r0 > 1:
            if r[0] in ('@tag()', '@t()'):
                arg_str = f'name()="{r[2].lower()}"'
            else:
                symbol = r[1]
                if symbol == '=':  # 精确查找
                    arg = 'text()' if r[0] in ('@text()', '@tx()') else r[0]
                    arg_str = f'{arg}={_quotes_escape(r[2])}'

                elif symbol == '^':  # 匹配开头
                    if r[0] in ('@text()', '@tx()'):
                        txt_str = f'/text()[starts-with(., {_quotes_escape(r[2])})]/..'
                        arg_str = ''
                    else:
                        arg_str = f"starts-with({r[0]},{_quotes_escape(r[2])})"

                elif symbol == '$':  # 匹配结尾
                    if r[0] in ('@text()', '@tx()'):
                        txt_str = (f'/text()[substring(., string-length(.) - string-length('
                                   f'{_quotes_escape(r[2])}) +1) = {_quotes_escape(r[2])}]/..')
                        arg_str = ''
                    else:
                        arg_str = (f'substring({r[0]}, string-length({r[0]}) - string-length('
                                   f'{_quotes_escape(r[2])}) +1) = {_quotes_escape(r[2])}')

                elif symbol == ':':  # 模糊查找
                    if r[0] in ('@text()', '@tx()'):
                        txt_str = f'/text()[contains(., {_quotes_escape(r[2])})]/..'
                        arg_str = ''
                    else:
                        arg_str = f"contains({r[0]},{_quotes_escape(r[2])})"

                else:
                    raise LocatorError(_S._lang.INCORRECT_SIGN_, symbol)

        elif len_r != 3 and len_r0 > 1:
            if r[0] in ('@tag()', '@t()'):
                arg_str = ''
            else:
                arg_str = 'normalize-space(text())' if r[0] in ('@text()', '@tx()') else f'{r[0]}'

    if arg_str:
        arg_list.append(arg_str)
    arg_str = ' and '.join(arg_list)
    return 'xpath', f'//*[{arg_str}]{txt_str}' if arg_str else f'//*{txt_str}'


def _make_multi_xpath_str(tag: str, text: str) -> tuple:
    """生成多属性查找的xpath语句
    :param tag: 标签名
    :param text: 待处理的字符串
    :return: xpath字符串
    """
    arg_list = []
    args = split(r'(@!|@@|@\|)', text)[1:]
    if '@@' in args and '@|' in args:
        raise LocatorError(_S._lang.SYMBOL_CONFLICT, VALUE=text)
    _and = '@|' not in args
    tags = [] if tag == '*' else [f'name()="{tag}"']
    tags_connect = ' or '

    for k in range(0, len(args) - 1, 2):
        r = split(r'([:=$^])', args[k + 1], maxsplit=1)
        arg_str = ''
        len_r = len(r)

        if not r[0]:  # 不查询任何属性
            arg_str = 'not(@*)'

        else:
            ignore = True if args[k] == '@!' else False  # 是否去除某个属性
            if len_r != 3:  # 只有属性名没有属性内容，查询是否存在该属性
                if r[0] in ('tag()', 't()'):
                    continue
                arg_str = 'normalize-space(text())' if r[0] in ('text()', 'tx()') else f'@{r[0]}'

            elif len_r == 3:  # 属性名和内容都有
                if r[0] in ('tag()', 't()'):
                    if ignore:
                        tags.append(f'not(name()="{r[2]}")')
                        tags_connect = ' and '
                    else:
                        tags.append(f'name()="{r[2]}"')
                    continue

                symbol = r[1]
                if r[0] in ('text()', 'tx()'):
                    arg = '.'
                    txt = r[2]
                else:
                    arg = f'@{r[0]}'
                    txt = r[2]

                if symbol == '=':
                    arg_str = f'{arg}={_quotes_escape(txt)}'

                elif symbol == ':':
                    arg_str = f'contains({arg},{_quotes_escape(txt)})'

                elif symbol == '^':
                    arg_str = f'starts-with({arg},{_quotes_escape(txt)})'

                elif symbol == '$':
                    arg_str = (f'substring({arg}, string-length({arg}) - string-length('
                               f'{_quotes_escape(txt)}) +1) = {_quotes_escape(txt)}')

                else:
                    raise LocatorError(_S._lang.INCORRECT_SIGN_, symbol)

            if arg_str and ignore:
                arg_str = f'not({arg_str})'

        if arg_str:
            arg_list.append(arg_str)

    arg_str = ' and '.join(arg_list) if _and else ' or '.join(arg_list)
    if tags:
        condition = f' and ({arg_str})' if arg_str else ''
        arg_str = f'({tags_connect.join(tags)}){condition}'

    return 'xpath', f'//*[{arg_str}]' if arg_str else f'//*'


def _quotes_escape(search_str: str) -> str:
    """将"转义，不知何故不能直接用 斜杠 来转义
    :param search_str: 查询字符串
    :return: 把"转义后的字符串
    """
    if '"' not in search_str:
        return f'"{search_str}"'

    parts = search_str.split('"')
    parts_num = len(parts)
    search_str = 'concat('

    for key, i in enumerate(parts):
        search_str += f'"{i}"'
        search_str += ',' + '\'"\',' if key < parts_num - 1 else ''

    search_str += ',"")'
    return search_str


def _make_multi_css_str(tag: str, text: str) -> tuple:
    """生成多属性查找的css selector语句
    :param tag: 标签名
    :param text: 待处理的字符串
    :return: css selector字符串
    """
    arg_list = []
    args = split(r'(@!|@@|@\|)', text)[1:]
    if '@@' in args and '@|' in args:
        raise LocatorError(_S._lang.SYMBOL_CONFLICT, LOCATOR=text)
    _and = '@|' not in args

    for k in range(0, len(args) - 1, 2):
        r = split(r'([:=$^])', args[k + 1], maxsplit=1)
        if not r[0] or r[0].startswith(('text()', 'tx()')):
            return _make_multi_xpath_str(tag, text)

        arg_str = ''
        len_r = len(r)
        ignore = True if args[k] == '@!' else False  # 是否去除某个属性
        if len_r != 3:  # 只有属性名没有属性内容，查询是否存在该属性
            if r[0] in ('tag()', 't()'):
                continue
            arg_str = f'[{r[0]}]'

        elif len_r == 3:  # 属性名和内容都有
            if r[0] in ('tag()', 't()'):
                if tag == '*':
                    tag = f':not({r[2].lower()})' if ignore else f'{r[2]}'
                else:
                    tag += f',:not({r[2].lower()})' if ignore else f',{r[2]}'
                continue

            d = {'=': '', '^': '^', '$': '$', ':': '*'}
            arg_str = f'[{r[0]}{d[r[1]]}={css_trans(r[2])}]'

        if arg_str and ignore:
            arg_str = f':not({arg_str})'

        if arg_str:
            arg_list.append(arg_str)

    if _and:
        return 'css selector', f'{tag}{"".join(arg_list)}'

    return 'css selector', f'{tag}{("," + tag).join(arg_list)}'


def _make_single_css_str(tag: str, text: str) -> tuple:
    """生成单属性css selector语句
    :param tag: 标签名
    :param text: 待处理的字符串
    :return: css selector字符串
    """
    if text == '@' or text.startswith(('@text()', '@tx()')):
        return _make_single_xpath_str(tag, text)

    r = split(r'([:=$^])', text, maxsplit=1)
    if r[0] in ('@tag()', '@t()'):
        return 'css selector', r[2]

    if len(r) == 3:
        d = {'=': '', '^': '^', '$': '$', ':': '*'}
        arg_str = f'[{r[0][1:]}{d[r[1]]}={css_trans(r[2])}]'

    else:
        arg_str = f'[{css_trans(r[0][1:])}]'

    return 'css selector', f'{tag}{arg_str}'


def translate_loc(loc):
    if len(loc) != 2:
        raise LocatorError(_S._lang.LOC_LEN, LOCATOR=loc)

    loc_by = By.XPATH
    loc_0 = loc[0].lower()

    if loc_0 == By.XPATH:
        loc_str = loc[1]

    elif loc_0 == By.CSS_SELECTOR:
        loc_by = loc_0
        loc_str = loc[1]

    elif loc_0 == By.ID:
        loc_str = f'//*[@id="{loc[1]}"]'

    elif loc_0 == By.CLASS_NAME:
        loc_str = f'//*[@class="{loc[1]}"]'

    elif loc_0 == By.LINK_TEXT:
        loc_str = f'//a[text()="{loc[1]}"]'

    elif loc_0 == By.NAME:
        loc_str = f'//*[@name="{loc[1]}"]'

    elif loc_0 == By.TAG_NAME:
        loc_str = f'//*[name()="{loc[1]}"]'

    elif loc_0 == By.PARTIAL_LINK_TEXT:
        loc_str = f'//a[contains(text(),"{loc[1]}")]'

    else:
        raise LocatorError(_S._lang.INVALID_LOC, LOCATOR=loc)

    return loc_by, loc_str


def translate_css_loc(loc):
    if len(loc) != 2:
        raise LocatorError(_S._lang.LOC_LEN, LOCATOR=loc)

    loc_by = By.CSS_SELECTOR
    loc_0 = loc[0].lower()
    if loc_0 == By.XPATH:
        loc_by = By.XPATH
        loc_str = loc[1]

    elif loc_0 == By.CSS_SELECTOR:
        loc_by = loc_0
        loc_str = loc[1]

    elif loc_0 == By.ID:
        loc_str = f'#{css_trans(loc[1])}'

    elif loc_0 == By.CLASS_NAME:
        loc_str = f'.{css_trans(loc[1])}'

    elif loc_0 == By.LINK_TEXT:
        loc_by = By.XPATH
        loc_str = f'//a[text()="{css_trans(loc[1])}"]'

    elif loc_0 == By.NAME:
        loc_str = f'*[@name={css_trans(loc[1])}]'

    elif loc_0 == By.TAG_NAME:
        loc_str = loc[1]

    elif loc_0 == By.PARTIAL_LINK_TEXT:
        loc_by = By.XPATH
        loc_str = f'//a[contains(text(),"{loc[1]}")]'

    else:
        raise LocatorError(_S._lang.INVALID_LOC, LOCATOR=loc)

    return loc_by, loc_str


def css_trans(txt):
    c = ('!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@',
         '[', '\\', ']', '^', '`', ',', '{', '|', '}', '~', ' ')
    return ''.join([fr'\{i}' if i in c else i for i in txt])


def _preprocess(loc):
    """对缩写进行处理，替换回完整写法"""
    if loc.startswith('.'):
        if loc.startswith(('.=', '.:', '.^', '.$')):
            loc = loc.replace('.', '@class', 1)
        else:
            loc = loc.replace('.', '@class=', 1)

    elif loc.startswith('#'):
        if loc.startswith(('#=', '#:', '#^', '#$')):
            loc = loc.replace('#', '@id', 1)
        else:
            loc = loc.replace('#', '@id=', 1)

    elif loc.startswith(('t:', 't=')):
        loc = f'tag:{loc[2:]}'

    elif loc.startswith(('tx:', 'tx=', 'tx^', 'tx$')):
        loc = f'text{loc[2:]}'

    elif loc.startswith(('c:', 'c=')):
        loc = f'css:{loc[2:]}'

    elif loc.startswith(('x:', 'x=')):
        loc = f'xpath:{loc[2:]}'

    return loc
