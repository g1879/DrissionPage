# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from html import unescape
from http.cookiejar import Cookie
from re import sub
from urllib.parse import urlparse, urljoin, urlunparse

from requests.cookies import RequestsCookieJar


def get_ele_txt(e):
    """获取元素内所有文本
    :param e: 元素对象
    :return: 元素内所有文本
    """
    # 前面无须换行的元素
    nowrap_list = ('br', 'sub', 'sup', 'em', 'strong', 'a', 'font', 'b', 'span', 's', 'i', 'del', 'ins', 'img', 'td',
                   'th', 'abbr', 'bdi', 'bdo', 'cite', 'code', 'data', 'dfn', 'kbd', 'mark', 'q', 'rp', 'rt', 'ruby',
                   'samp', 'small', 'time', 'u', 'var', 'wbr', 'button', 'slot', 'content')
    # 后面添加换行的元素
    wrap_after_list = ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'li', 'blockquote', 'header',
                       'footer', 'address' 'article', 'aside', 'main', 'nav', 'section', 'figcaption', 'summary')
    # 不获取文本的元素
    noText_list = ('script', 'style', 'video', 'audio', 'iframe', 'embed', 'noscript', 'canvas', 'template')
    # 用/t分隔的元素
    tab_list = ('td', 'th')

    if e.tag in noText_list:
        return e.raw_text

    def get_node_txt(ele, pre: bool = False):
        tag = ele.tag
        if tag == 'br':
            return [True]
        if not pre and tag == 'pre':
            pre = True

        str_list = []
        if tag in noText_list and not pre:  # 标签内的文本不返回
            return str_list

        nodes = ele.eles('xpath:./text() | *')
        prev_ele = ''
        for el in nodes:
            if isinstance(el, str):  # 字符节点
                if pre:
                    str_list.append(el)

                else:
                    if sub('[ \n\t\r]', '', el) != '':  # 字符除了回车和空格还有其它内容
                        txt = el
                        if not pre:
                            txt = txt.replace('\n', ' ').strip(' ')
                            txt = sub(r' {2,}', ' ', txt)
                        str_list.append(txt)

            else:  # 元素节点
                if el.tag not in nowrap_list and str_list and str_list[-1] != '\n':  # 元素间换行的情况
                    str_list.append('\n')
                if el.tag in tab_list and prev_ele in tab_list:  # 表格的行
                    str_list.append('\t')

                str_list.extend(get_node_txt(el, pre))
                prev_ele = el.tag

        if tag in wrap_after_list and str_list and str_list[-1] not in ('\n', True):  # 有些元素后面要添加回车
            str_list.append('\n')

        return str_list

    re_str = get_node_txt(e)
    if re_str and re_str[-1] == '\n':
        re_str.pop()
    re_str = ''.join([i if i is not True else '\n' for i in re_str])
    return format_html(re_str)


def format_html(text):
    """处理html编码字符
    :param text: html文本
    :return: 格式化后的html文本
    """
    return unescape(text).replace('\xa0', ' ') if text else text


def location_in_viewport(page, loc_x, loc_y):
    """判断给定的坐标是否在视口中          |n
    :param page: ChromePage对象
    :param loc_x: 页面绝对坐标x
    :param loc_y: 页面绝对坐标y
    :return:
    """
    js = f'''function(){{var x = {loc_x}; var y = {loc_y};
    const scrollLeft = document.documentElement.scrollLeft;
    const scrollTop = document.documentElement.scrollTop;
    const vWidth = document.documentElement.clientWidth;
    const vHeight = document.documentElement.clientHeight;
    if (x< scrollLeft || y < scrollTop || x > vWidth + scrollLeft || y > vHeight + scrollTop){{return false;}}
    return true;}}'''
    return page.run_js(js)
    # const vWidth = window.innerWidth || document.documentElement.clientWidth;
    # const vHeight = window.innerHeight || document.documentElement.clientHeight;


def offset_scroll(ele, offset_x, offset_y):
    """接收元素及偏移坐标，把坐标滚动到页面中间，返回该点在视口中的坐标
    有偏移量时以元素左上角坐标为基准，没有时以click_point为基准
    :param ele: 元素对象
    :param offset_x: 偏移量x
    :param offset_y: 偏移量y
    :return: 视口中的坐标
    """
    loc_x, loc_y = ele.location
    cp_x, cp_y = ele.locations.click_point
    lx = loc_x + offset_x if offset_x else cp_x
    ly = loc_y + offset_y if offset_y else cp_y
    if not location_in_viewport(ele.page, lx, ly):
        clientWidth = ele.page.run_js('return document.body.clientWidth;')
        clientHeight = ele.page.run_js('return document.body.clientHeight;')
        ele.page.scroll.to_location(lx - clientWidth // 2, ly - clientHeight // 2)
    cl_x, cl_y = ele.locations.viewport_location
    ccp_x, ccp_y = ele.locations.viewport_click_point
    cx = cl_x + offset_x if offset_x else ccp_x
    cy = cl_y + offset_y if offset_y else ccp_y
    return cx, cy


def make_absolute_link(link, page=None):
    """获取绝对url
    :param link: 超链接
    :param page: 页面对象
    :return: 绝对链接
    """
    if not link:
        return link

    parsed = urlparse(link)._asdict()

    # 是相对路径，与页面url拼接并返回
    if not parsed['netloc']:
        return urljoin(page.url, link) if page else link

    # 是绝对路径但缺少协议，从页面url获取协议并修复
    if not parsed['scheme'] and page:
        parsed['scheme'] = urlparse(page.url).scheme
        parsed = tuple(v for v in parsed.values())
        return urlunparse(parsed)

    # 绝对路径且不缺协议，直接返回
    return link


def is_js_func(func):
    """检查文本是否js函数"""
    func = func.strip()
    if func.startswith('function') or func.startswith('async '):
        return True
    elif '=>' in func:
        return True
    return False


def cookie_to_dict(cookie):
    """把Cookie对象转为dict格式
    :param cookie: Cookie对象
    :return: cookie字典
    """
    if isinstance(cookie, Cookie):
        cookie_dict = cookie.__dict__.copy()
        cookie_dict.pop('rfc2109')
        cookie_dict.pop('_rest')
        return cookie_dict

    elif isinstance(cookie, dict):
        cookie_dict = cookie

    elif isinstance(cookie, str):
        cookie = cookie.split(',' if ',' in cookie else ';')
        cookie_dict = {}

        for key, attr in enumerate(cookie):
            attr_val = attr.lstrip().split('=')

            if key == 0:
                cookie_dict['name'] = attr_val[0]
                cookie_dict['value'] = attr_val[1] if len(attr_val) == 2 else ''
            else:
                cookie_dict[attr_val[0]] = attr_val[1] if len(attr_val) == 2 else ''

        return cookie_dict

    else:
        raise TypeError('cookie参数必须为Cookie、str或dict类型。')

    return cookie_dict


def cookies_to_tuple(cookies):
    """把cookies转为tuple格式
    :param cookies: cookies信息，可为CookieJar, list, tuple, str, dict
    :return: 返回tuple形式的cookies
    """
    if isinstance(cookies, (list, tuple, RequestsCookieJar)):
        cookies = tuple(cookie_to_dict(cookie) for cookie in cookies)

    elif isinstance(cookies, str):
        cookies = tuple(cookie_to_dict(cookie.lstrip()) for cookie in cookies.split(";"))

    elif isinstance(cookies, dict):
        cookies = tuple({'name': cookie, 'value': cookies[cookie]} for cookie in cookies)

    else:
        raise TypeError('cookies参数必须为RequestsCookieJar、list、tuple、str或dict类型。')

    return cookies


def set_session_cookies(session, cookies):
    """设置Session对象的cookies
    :param session: Session对象
    :param cookies: cookies信息
    :return: None
    """
    cookies = cookies_to_tuple(cookies)
    for cookie in cookies:
        if cookie['value'] is None:
            cookie['value'] = ''

        kwargs = {x: cookie[x] for x in cookie
                  if x.lower() in ('version', 'port', 'domain', 'path', 'secure',
                                   'expires', 'discard', 'comment', 'comment_url', 'rest')}

        if 'expiry' in cookie:
            kwargs['expires'] = cookie['expiry']

        session.cookies.set(cookie['name'], cookie['value'], **kwargs)
