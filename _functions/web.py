# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from html import unescape
from os.path import sep
from pathlib import Path
from re import sub
from urllib.parse import urlparse, urljoin, urlunparse

from DataRecorder.tools import make_valid_name
from requests.structures import CaseInsensitiveDict

from .._functions.settings import Settings as _S


def get_ele_txt(e):
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

    def get_node_txt(ele, pre=False) -> list:
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
                            txt = txt.replace('\r\n', ' ').replace('\n', ' ')
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

    l = len(re_str)
    if l > 1:
        r = []
        for i in range(l - 1):
            i1 = re_str[i]
            i2 = re_str[i + 1]
            if i1 is True:
                r.append('\n')
                continue
            elif i2 is True:
                r.append(i1)
                continue
            elif i1.endswith(' ') and i2.startswith(' '):
                i1 = i1[:-1]
            r.append(i1)
        r.append('\n' if re_str[-1] is True else re_str[-1])
        re_str = ''.join(r)

    elif not l:
        re_str = ''
    else:
        re_str = re_str[0] if re_str[0] is not True else '\n'

    return format_html(re_str.strip())


def format_html(text):
    return unescape(text).replace('\xa0', ' ') if text else text


def location_in_viewport(page, loc_x, loc_y):
    js = f'''function(){{let x = {loc_x}; let y = {loc_y};
    const scrollLeft = document.documentElement.scrollLeft;
    const scrollTop = document.documentElement.scrollTop;
    const vWidth = document.documentElement.clientWidth;
    const vHeight = document.documentElement.clientHeight;
    if (x< scrollLeft || y < scrollTop || x > vWidth + scrollLeft || y > vHeight + scrollTop){{return false;}}
    return true;}}'''
    return page._run_js(js)


def offset_scroll(ele, offset_x, offset_y):
    loc_x, loc_y = ele.rect.location
    cp_x, cp_y = ele.rect.click_point
    lx = loc_x + offset_x if offset_x else cp_x
    ly = loc_y + offset_y if offset_y else cp_y
    if not location_in_viewport(ele.owner, lx, ly):
        clientWidth = ele.owner._run_js('return document.body.clientWidth;')
        clientHeight = ele.owner._run_js('return document.body.clientHeight;')
        ele.owner.scroll.to_location(lx - clientWidth // 2, ly - clientHeight // 2)
    cl_x, cl_y = ele.rect.viewport_location
    ccp_x, ccp_y = ele.rect.viewport_click_point
    cx = cl_x + offset_x if offset_x else ccp_x
    cy = cl_y + offset_y if offset_y else ccp_y
    return cx, cy


def make_absolute_link(link, baseURI=None):
    if not link:
        return link

    link = link.strip().replace('\\', '/')
    parsed = urlparse(link)._asdict()
    if baseURI:
        baseURI = baseURI.rstrip('/\\')

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
    func = func.strip()
    if (func.startswith('function') or func.startswith('async ')) and func.endswith('}'):
        return True
    # elif '=>' in func:
    #     return True
    return False


def get_blob(page, url, as_bytes=True):
    if not url.startswith('blob'):
        raise ValueError(_S._lang.join(_S._lang.NOT_BLOB, url=url))
    js = """
       function fetchData(url) {
      return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.responseType = 'blob';
        xhr.onload = function() {
          let reader  = new FileReader();
          reader.onloadend = function(){resolve(reader.result);}
          reader.readAsDataURL(xhr.response);
        };
        xhr.open('GET', url, true);
        xhr.send();
      });
    }
"""
    try:
        result = page._run_js(js, url)
    except:
        raise RuntimeError(_S._lang.join(_S._lang.GET_BLOB_FAILED))
    if as_bytes:
        from base64 import b64decode
        return b64decode(result.split(',', 1)[-1])
    else:
        return result


def save_page(tab, path=None, name=None, as_pdf=False, kwargs=None):
    if name:
        if name.endswith('.pdf'):
            name = name[:-4]
            as_pdf = True
        elif name.endswith('.mhtml'):
            name = name[:-6]
            as_pdf = False

    if path:
        path = Path(path)
        if path.suffix.lower() == '.mhtml':
            name = path.stem
            path = path.parent
            as_pdf = False
        elif path.suffix.lower() == '.pdf':
            name = path.stem
            path = path.parent
            as_pdf = True

    return get_pdf(tab, path, name, kwargs) if as_pdf else get_mhtml(tab, path, name)


def get_mhtml(page, path=None, name=None):
    r = page._run_cdp('Page.captureSnapshot')['data']
    if path is None and name is None:
        return r

    path = path or '.'
    Path(path).mkdir(parents=True, exist_ok=True)
    name = make_valid_name(name or page.title)
    with open(f'{path}{sep}{name}.mhtml', 'w', encoding='utf-8') as f:
        f.write(r.replace('\r\n', '\n'))
    return r


def get_pdf(page, path=None, name=None, kwargs=None):
    if not kwargs:
        kwargs = {}
    kwargs['transferMode'] = 'ReturnAsBase64'
    if 'printBackground' not in kwargs:
        kwargs['printBackground'] = True
    try:
        r = page._run_cdp('Page.printToPDF', **kwargs)['data']
    except:
        raise RuntimeError(_S._lang.join(_S._lang.GET_PDF_FAILED))
    from base64 import b64decode
    r = b64decode(r)
    if path is None and name is None:
        return r

    path = path or '.'
    Path(path).mkdir(parents=True, exist_ok=True)
    name = make_valid_name(name or page.title)
    with open(f'{path}{sep}{name}.pdf', 'wb') as f:
        f.write(r)
    return r


def tree(ele_or_page, text=False, show_js=False, show_css=False):
    def _tree(obj, last_one=True, body=''):
        list_ele = obj.children()
        length = len(list_ele)
        body_unit = '    ' if last_one else '│   '
        tail = '├───'
        new_body = body + body_unit

        if length > 0:
            new_last_one = False
            for i in range(length):
                if i == length - 1:
                    tail = '└───'
                    new_last_one = True
                e = list_ele[i]

                attrs = ' '.join([f"{k}='{v}'" for k, v in e.attrs.items()])
                show_text = f'{new_body}{tail}<{e.tag} {attrs}>'.replace('\n', ' ')
                if text:
                    t = e('x:/text()')
                    if t:
                        t = t.replace('\n', ' ')
                        if (e.tag not in ('script', 'style') or (e.tag == 'script' and show_js)
                                or (e.tag == 'style' and show_css)):
                            if text is not True:
                                t = t[:text]
                            show_text = f'{show_text} {t}'
                print(show_text)

                _tree(e, new_last_one, new_body)

    ele = ele_or_page.s_ele()
    attrs = ' '.join([f"{k}='{v}'" for k, v in ele.attrs.items()])
    show_text = f'<{ele.tag} {attrs}>'.replace('\n', ' ')
    if text:
        t = ele('x:/text()')
        if t:
            t = t.replace('\n', ' ')
            if (ele.tag not in ('script', 'style') or (ele.tag == 'script' and show_js)
                    or (ele.tag == 'style' and show_css)):
                if text is not True:
                    t = t[:text]
                show_text = f'{show_text} {t}'
    print(show_text)
    _tree(ele)


def format_headers(txt):
    if isinstance(txt, (dict, CaseInsensitiveDict)):
        for k, v in txt.items():
            if v not in (None, False, True):
                txt[k] = str(v)
        for i in (':method', ':scheme', ':authority', ':path'):
            txt.pop(i, None)
        return txt
    headers = {}
    for header in txt.split('\n'):
        if header:
            name, value = header.split(': ', maxsplit=1)
            if name not in (':method', ':scheme', ':authority', ':path'):
                headers[name] = value
    return headers
