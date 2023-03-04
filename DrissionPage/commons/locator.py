# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from re import split
from .by import By


def get_loc(loc, translate_css=False):
    """接收selenium定位元组或本库定位语法，转换为标准定位元组，可翻译css selector为xpath
    :param loc: selenium定位元组或本库定位语法
    :param translate_css: 是否翻译css selector为xpath
    :return: DrissionPage定位元组
    """
    if isinstance(loc, tuple):
        loc = translate_loc(loc)

    elif isinstance(loc, str):
        loc = str_to_loc(loc)

    else:
        raise TypeError('loc参数只能是tuple或str。')

    if loc[0] == 'css selector' and translate_css:
        from lxml.cssselect import CSSSelector, ExpressionError
        try:
            path = str(CSSSelector(loc[1], translator='html').path)
            path = path[20:] if path.startswith('descendant-or-self::') else path
            loc = 'xpath', path
        except ExpressionError:
            pass

    return loc


def str_to_loc(loc):
    """处理元素查找语句
    查找方式：属性、tag name及属性、文本、xpath、css selector、id、class
    @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串
    """
    loc_by = 'xpath'

    if loc.startswith('.'):
        if loc.startswith(('.=', '.:',)):
            loc = loc.replace('.', '@class', 1)
        else:
            loc = loc.replace('.', '@class=', 1)

    elif loc.startswith('#'):
        if loc.startswith(('#=', '#:',)):
            loc = loc.replace('#', '@id', 1)
        else:
            loc = loc.replace('#', '@id=', 1)

    elif loc.startswith(('t:', 't=')):
        loc = f'tag:{loc[2:]}'

    elif loc.startswith(('tx:', 'tx=')):
        loc = f'text{loc[2:]}'

    # ------------------------------------------------------------------
    # 多属性查找
    if loc.startswith('@@') and loc != '@@':
        loc_str = _make_multi_xpath_str('*', loc)

    elif loc.startswith('@|') and loc != '@|':
        loc_str = _make_multi_xpath_str('*', loc, False)

    # 单属性查找
    elif loc.startswith('@') and loc != '@':
        loc_str = _make_single_xpath_str('*', loc)

    # 根据tag name查找
    elif loc.startswith(('tag:', 'tag=')) and loc not in ('tag:', 'tag='):
        at_ind = loc.find('@')
        if at_ind == -1:
            loc_str = f'//*[name()="{loc[4:]}"]'
        else:
            if loc[at_ind:].startswith('@@'):
                loc_str = _make_multi_xpath_str(loc[4:at_ind], loc[at_ind:])
            elif loc[at_ind:].startswith('@|'):
                loc_str = _make_multi_xpath_str(loc[4:at_ind], loc[at_ind:], False)
            else:
                loc_str = _make_single_xpath_str(loc[4:at_ind], loc[at_ind:])

    # 根据文本查找
    elif loc.startswith('text='):
        loc_str = f'//*[text()={_make_search_str(loc[5:])}]'
    elif loc.startswith('text:') and loc != 'text:':
        loc_str = f'//*/text()[contains(., {_make_search_str(loc[5:])})]/..'

    # 用xpath查找
    elif loc.startswith(('xpath:', 'xpath=')) and loc not in ('xpath:', 'xpath='):
        loc_str = loc[6:]
    elif loc.startswith(('x:', 'x=')) and loc not in ('x:', 'x='):
        loc_str = loc[2:]

    # 用css selector查找
    elif loc.startswith(('css:', 'css=')) and loc not in ('css:', 'css='):
        loc_by = 'css selector'
        loc_str = loc[4:]
    elif loc.startswith(('c:', 'c=')) and loc not in ('c:', 'c='):
        loc_by = 'css selector'
        loc_str = loc[2:]

    # 根据文本模糊查找
    elif loc:
        loc_str = f'//*/text()[contains(., {_make_search_str(loc)})]/..'
    else:
        loc_str = '//*'

    return loc_by, loc_str


def _make_single_xpath_str(tag: str, text: str) -> str:
    """生成xpath语句
    :param tag: 标签名
    :param text: 待处理的字符串
    :return: xpath字符串
    """
    arg_list = [] if tag == '*' else [f'name()="{tag}"']
    arg_str = txt_str = ''

    if text == '@':
        arg_str = 'not(@*)'

    else:
        r = split(r'([:=])', text, maxsplit=1)
        len_r = len(r)
        len_r0 = len(r[0])
        if len_r != 3 and len_r0 > 1:
            arg_str = 'normalize-space(text())' if r[0] in ('@text()', '@tx()') else f'{r[0]}'

        elif len_r == 3 and len_r0 > 1:
            if r[1] == '=':  # 精确查找
                arg = '.' if r[0] in ('@text()', '@tx()') else r[0]
                arg_str = f'{arg}={_make_search_str(r[2])}'

            else:  # 模糊查找
                if r[0] in ('@text()', '@tx()'):
                    txt_str = f'/text()[contains(., {_make_search_str(r[2])})]/..'
                    arg_str = ''
                else:
                    arg_str = f"contains({r[0]},{_make_search_str(r[2])})"

    if arg_str:
        arg_list.append(arg_str)
    arg_str = ' and '.join(arg_list)
    return f'//*[{arg_str}]{txt_str}' if arg_str else f'//*{txt_str}'


def _make_multi_xpath_str(tag: str, text: str, _and: bool = True) -> str:
    """生成多属性查找的xpath语句
    :param tag: 标签名
    :param text: 待处理的字符串
    :param _and: 是否与方式
    :return: xpath字符串
    """
    arg_list = []
    args = text.split('@@') if _and else text.split('@|')

    for arg in args[1:]:
        r = split(r'([:=])', arg, maxsplit=1)
        arg_str = ''
        len_r = len(r)

        if not r[0]:  # 不查询任何属性
            arg_str = 'not(@*)'

        else:
            r[0], ignore = (r[0][1:], True) if r[0][0] == '-' else (r[0], None)  # 是否去除某个属性

            if len_r != 3:  # 只有属性名没有属性内容，查询是否存在该属性
                arg_str = 'normalize-space(text())' if r[0] in ('text()', 'tx()') else f'@{r[0]}'

            elif len_r == 3:  # 属性名和内容都有
                arg = '.' if r[0] in ('text()', 'tx()') else f'@{r[0]}'
                if r[1] == '=':
                    arg_str = f'{arg}={_make_search_str(r[2])}'
                else:
                    arg_str = f'contains({arg},{_make_search_str(r[2])})'

            if arg_str and ignore:
                arg_str = f'not({arg_str})'

        if arg_str:
            arg_list.append(arg_str)

    arg_str = ' and '.join(arg_list) if _and else ' or '.join(arg_list)
    if tag != '*':
        condition = f' and ({arg_str})' if arg_str else ''
        arg_str = f'name()="{tag}"{condition}'

    return f'//*[{arg_str}]' if arg_str else f'//*'


def _make_search_str(search_str: str) -> str:
    """将"转义，不知何故不能直接用 \ 来转义
    :param search_str: 查询字符串
    :return: 把"转义后的字符串
    """
    parts = search_str.split('"')
    parts_num = len(parts)
    search_str = 'concat('

    for key, i in enumerate(parts):
        search_str += f'"{i}"'
        search_str += ',' + '\'"\',' if key < parts_num - 1 else ''

    search_str += ',"")'
    return search_str


def translate_loc(loc):
    """把By类型的loc元组转换为css selector或xpath类型的
    :param loc: By类型的loc元组
    :return: css selector或xpath类型的loc元组
    """
    if len(loc) != 2:
        raise ValueError('定位符长度必须为2。')

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

    elif loc_0 == By.PARTIAL_LINK_TEXT:
        loc_str = f'//a[text()="{loc[1]}"]'

    elif loc_0 == By.NAME:
        loc_str = f'//*[@name="{loc[1]}"]'

    elif loc_0 == By.TAG_NAME:
        loc_str = f'//*[name()="{loc[1]}"]'

    elif loc_0 == By.PARTIAL_LINK_TEXT:
        loc_str = f'//a[contains(text(),"{loc[1]}")]'

    else:
        raise ValueError('无法识别的定位符。')

    return loc_by, loc_str
