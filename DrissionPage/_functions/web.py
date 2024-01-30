# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from datetime import datetime
from html import unescape
from http.cookiejar import Cookie
from re import sub
from urllib.parse import urlparse, urljoin, urlunparse

from requests.cookies import RequestsCookieJar
from tldextract import extract


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
                            txt = txt.replace('\r\n', ' ').replace('\n', ' ').strip(' ')
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
    :return: bool
    """
    js = f'''function(){{var x = {loc_x}; var y = {loc_y};
    const scrollLeft = document.documentElement.scrollLeft;
    const scrollTop = document.documentElement.scrollTop;
    const vWidth = document.documentElement.clientWidth;
    const vHeight = document.documentElement.clientHeight;
    if (x< scrollLeft || y < scrollTop || x > vWidth + scrollLeft || y > vHeight + scrollTop){{return false;}}
    return true;}}'''
    return page.run_js(js)


def offset_scroll(ele, offset_x, offset_y):
    """接收元素及偏移坐标，把坐标滚动到页面中间，返回该点在视口中的坐标
    有偏移量时以元素左上角坐标为基准，没有时以click_point为基准
    :param ele: 元素对象
    :param offset_x: 偏移量x
    :param offset_y: 偏移量y
    :return: 视口中的坐标
    """
    loc_x, loc_y = ele.rect.location
    cp_x, cp_y = ele.rect.click_point
    lx = loc_x + offset_x if offset_x else cp_x
    ly = loc_y + offset_y if offset_y else cp_y
    if not location_in_viewport(ele.page, lx, ly):
        clientWidth = ele.page.run_js('return document.body.clientWidth;')
        clientHeight = ele.page.run_js('return document.body.clientHeight;')
        ele.page.scroll.to_location(lx - clientWidth // 2, ly - clientHeight // 2)
    cl_x, cl_y = ele.rect.viewport_location
    ccp_x, ccp_y = ele.rect.viewport_click_point
    cx = cl_x + offset_x if offset_x else ccp_x
    cy = cl_y + offset_y if offset_y else ccp_y
    return cx, cy


def make_absolute_link(link, baseURI=None):
    """获取绝对url
    :param link: 超链接
    :param baseURI: 页面或iframe的url
    :return: 绝对链接
    """
    if not link:
        return link

    link = link.strip()
    parsed = urlparse(link)._asdict()

    # 是相对路径，与页面url拼接并返回
    if not parsed['netloc']:
        return urljoin(baseURI, link) if baseURI else link

    # 是绝对路径但缺少协议，从页面url获取协议并修复
    if not parsed['scheme'] and baseURI:
        parsed['scheme'] = urlparse(baseURI).scheme
        parsed = tuple(v for v in parsed.values())
        return urlunparse(parsed)

    # 绝对路径且不缺协议，直接返回
    return link


def is_js_func(func):
    """检查文本是否js函数"""
    func = func.strip()
    if (func.startswith('function') or func.startswith('async ')) and func.endswith('}'):
        return True
    # elif '=>' in func:
    #     return True
    return False


def cookie_to_dict(cookie):
    """把Cookie对象转为dict格式
    :param cookie: Cookie对象、字符串或字典
    :return: cookie字典
    """
    if isinstance(cookie, Cookie):
        cookie_dict = cookie.__dict__.copy()
        cookie_dict.pop('rfc2109', None)
        cookie_dict.pop('_rest', None)
        return cookie_dict

    elif isinstance(cookie, dict):
        cookie_dict = cookie

    elif isinstance(cookie, str):
        cookie = cookie.rstrip(';,').split(',' if ',' in cookie else ';')
        cookie_dict = {}

        for key, attr in enumerate(cookie):
            attr_val = attr.lstrip().split('=', 1)

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
        cookies = tuple(cookie_to_dict(c.lstrip()) for c in cookies.rstrip(';,').split(',' if ',' in cookies else ';'))

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


def set_browser_cookies(page, cookies):
    """设置cookies值
    :param page: 页面对象
    :param cookies: cookies信息
    :return: None
    """
    for cookie in cookies_to_tuple(cookies):
        if 'expiry' in cookie:
            cookie['expires'] = int(cookie['expiry'])
            cookie.pop('expiry')

        if 'expires' in cookie:
            if not cookie['expires']:
                cookie.pop('expires')

            elif isinstance(cookie['expires'], str):
                if cookie['expires'].isdigit():
                    cookie['expires'] = int(cookie['expires'])

                elif cookie['expires'].replace('.', '').isdigit():
                    cookie['expires'] = float(cookie['expires'])

                else:
                    try:
                        cookie['expires'] = datetime.strptime(cookie['expires'],
                                                              '%a, %d %b %Y %H:%M:%S GMT').timestamp()
                    except ValueError:
                        cookie['expires'] = datetime.strptime(cookie['expires'],
                                                              '%a, %d %b %y %H:%M:%S GMT').timestamp()

        if cookie['value'] is None:
            cookie['value'] = ''
        elif not isinstance(cookie['value'], str):
            cookie['value'] = str(cookie['value'])
        if cookie['name'].startswith('__Secure-'):
            cookie['secure'] = True

        if cookie['name'].startswith('__Host-'):
            cookie['path'] = '/'
            cookie['secure'] = True
            cookie['url'] = page.url
            page.run_cdp_loaded('Network.setCookie', **cookie)
            continue  # 不用设置域名，可退出

        if cookie.get('domain', None):
            try:
                page.run_cdp_loaded('Network.setCookie', **cookie)
                if is_cookie_in_driver(page, cookie):
                    continue
            except Exception:
                pass

        ex_url = extract(page._browser_url)
        d_list = ex_url.subdomain.split('.')
        d_list.append(f'{ex_url.domain}.{ex_url.suffix}' if ex_url.suffix else ex_url.domain)

        tmp = [d_list[0]]
        if len(d_list) > 1:
            for i in d_list[1:]:
                tmp.append('.')
                tmp.append(i)

        for i in range(len(tmp)):
            d = ''.join(tmp[i:])
            cookie['domain'] = d
            page.run_cdp_loaded('Network.setCookie', **cookie)
            if is_cookie_in_driver(page, cookie):
                break


def is_cookie_in_driver(page, cookie):
    """查询cookie是否在浏览器内
    :param page: BasePage对象
    :param cookie: dict格式cookie
    :return: bool
    """
    if 'domain' in cookie:
        for c in page.get_cookies(all_domains=True):
            if cookie['name'] == c['name'] and cookie['value'] == c['value'] and cookie['domain'] == c.get('domain',
                                                                                                           None):
                return True
    else:
        for c in page.get_cookies(all_domains=True):
            if cookie['name'] == c['name'] and cookie['value'] == c['value']:
                return True
    return False


def get_blob(page, url, as_bytes=True):
    """获取知道blob资源
    :param page: 资源所在页面对象
    :param url: 资源url
    :param as_bytes: 是否以字节形式返回
    :return: 资源内容
    """
    if not url.startswith('blob'):
        raise TypeError('该链接非blob类型。')
    js = """
       function fetchData(url) {
      return new Promise((resolve, reject) => {
        var xhr = new XMLHttpRequest();
        xhr.responseType = 'blob';
        xhr.onload = function() {
          var reader  = new FileReader();
          reader.onloadend = function(){resolve(reader.result);}
          reader.readAsDataURL(xhr.response);
        };
        xhr.open('GET', url, true);
        xhr.send();
      });
    }
"""
    try:
        result = page.run_js(js, url)
    except:
        raise RuntimeError('无法获取该资源。')
    if as_bytes:
        from base64 import b64decode
        return b64decode(result.split(',', 1)[-1])
    else:
        return result
