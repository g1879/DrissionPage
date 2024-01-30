# -*- coding:utf-8 -*-
from pathlib import Path
from time import perf_counter, sleep

from requests import Response
from tldextract import extract

from .._elements.none_element import NoneElement
from .._functions.locator import is_loc
from .._functions.web import format_html, make_absolute_link, get_blob, cookie_to_dict
from ..errors import CDPError


class Getter(object):
    def __init__(self, obj):
        self._obj = obj


class ChromiumElementGetter(Getter):

    def screenshot(self, path=None, name=None, as_bytes=None, as_base64=None, scroll_to_center=True):
        """对当前元素截图，可保存到文件，或以字节方式返回
                :param path: 文件保存路径
                :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
                :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
                :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
                :param scroll_to_center: 截图前是否滚动到视口中央
                :return: 图片完整路径或字节文本
                """
        if self._obj.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" && this.naturalWidth > 0 '
                  '&& typeof this.naturalHeight != "undefined" && this.naturalHeight > 0')
            end_time = perf_counter() + self._obj.page.timeout
            while not self._obj.run_js(js) and perf_counter() < end_time:
                sleep(.1)
        if scroll_to_center:
            self._obj.scroll.to_see(center=True)

        left, top = self._obj.rect.location
        width, height = self._obj.rect.size
        left_top = (left, top)
        right_bottom = (left + width, top + height)
        if not name:
            name = f'{self._obj.tag}.jpg'

        return self._obj.page._get_screenshot(path, name, as_bytes=as_bytes, as_base64=as_base64, full_page=False,
                                              left_top=left_top, right_bottom=right_bottom, ele=self._obj)

    def property(self, name):
        """获取一个property属性值
        :param name: 属性名
        :return: 属性值文本
        """
        try:
            value = self._obj.run_js(f'return this.{name};')
            return format_html(value) if isinstance(value, str) else value
        except:
            return None

    def attribute(self, name):
        """返回一个attribute属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        attrs = self._obj.attributes
        if name == 'href':  # 获取href属性时返回绝对url
            link = attrs.get('href', None)
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link
            else:
                return make_absolute_link(link, self.property('baseURI'))

        elif name == 'src':
            return make_absolute_link(attrs.get('src', None), self.property('baseURI'))

        elif name == 'text':
            return self._obj.text

        elif name == 'innerText':
            return self._obj.raw_text

        elif name in ('html', 'outerHTML'):
            return self._obj.html

        elif name == 'innerHTML':
            return self._obj.inner_html

        else:
            return attrs.get(name, None)

    def style(self, style, pseudo_ele=''):
        """返回元素样式属性值，可获取伪元素属性值
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"' if pseudo_ele.startswith(':') else f', "::{pseudo_ele}"'
        return self._obj.run_js(f'return window.getComputedStyle(this{pseudo_ele}).getPropertyValue("{style}");')

    def source(self, timeout=None, base64_to_bytes=True):
        """返回元素src资源，base64的可转为bytes返回，其它返回str
        :param timeout: 等待资源加载的超时时间（秒）
        :param base64_to_bytes: 为True时，如果是base64数据，转换为bytes格式
        :return: 资源内容
        """
        timeout = self._obj.page.timeout if timeout is None else timeout
        if self._obj.tag == 'img':  # 等待图片加载完成
            js = ('return this.complete && typeof this.naturalWidth != "undefined" '
                  '&& this.naturalWidth > 0 && typeof this.naturalHeight != "undefined" '
                  '&& this.naturalHeight > 0')
            end_time = perf_counter() + timeout
            while not self._obj.run_js(js) and perf_counter() < end_time:
                sleep(.1)

        src = self.attribute('src')
        if src.lower().startswith('data:image'):
            if base64_to_bytes:
                from base64 import b64decode
                return b64decode(src.split(',', 1)[-1])

            else:
                return src.split(',', 1)[-1]

        is_blob = src.startswith('blob')
        result = None
        end_time = perf_counter() + timeout
        while perf_counter() < end_time:
            if is_blob:
                result = get_blob(self._obj.page, src, base64_to_bytes)
                if result:
                    break

            else:
                src = self.property('currentSrc')
                if not src:
                    continue

                node = self._obj.page.run_cdp('DOM.describeNode', backendNodeId=self._obj._backend_id)['node']
                frame = node.get('frameId', None) or self._obj.page._frame_id

                try:
                    result = self._obj.page.run_cdp('Page.getResourceContent', frameId=frame, url=src)
                    break
                except CDPError:
                    sleep(.1)

        if not result:
            return None

        elif is_blob:
            return result

        elif result['base64Encoded'] and base64_to_bytes:
            from base64 import b64decode
            return b64decode(result['content'])
        else:
            return result['content']


class SessionElementGetter(Getter):
    def attribute(self, name):
        """返回attribute属性值
        :param name: 属性名
        :return: 属性值文本，没有该属性返回None
        """
        # 获取href属性时返回绝对url
        if name == 'href':
            link = self._obj.inner_ele.get('href')
            # 若为链接为None、js或邮件，直接返回
            if not link or link.lower().startswith(('javascript:', 'mailto:')):
                return link

            else:  # 其它情况直接返回绝对url
                return make_absolute_link(link, self._obj.page.url)

        elif name == 'src':
            return make_absolute_link(self._obj.inner_ele.get('src'), self._obj.page.url)

        elif name == 'text':
            return self._obj.text

        elif name == 'innerText':
            return self._obj.raw_text

        elif name in ('html', 'outerHTML'):
            return self._obj.html

        elif name == 'innerHTML':
            return self._obj.inner_html

        else:
            return self._obj.inner_ele.get(name)


class ChromiumBaseGetter(Getter):
    def __call__(self, url, show_errmsg=False, retry=None, interval=None, timeout=None):
        """访问url
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param timeout: 连接超时时间（秒），为None时使用页面对象timeouts.page_load属性值
        :return: 目标url是否可用
        """
        retry, interval = self._obj._before_connect(url, retry, interval)
        self._url_available = self._obj._d_connect(self._obj._url, times=retry, interval=interval,
                                                   show_errmsg=show_errmsg, timeout=timeout)
        return self._obj._url_available

    def cookies(self, as_dict=False, all_domains=False, all_info=False):
        """获取cookies信息
        :param as_dict: 为True时返回由{name: value}键值对组成的dict，为True时返回list且all_info无效
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，为False时只返回name、value、domain
        :return: cookies信息
        """
        txt = 'Storage' if all_domains else 'Network'
        cookies = self._obj.run_cdp_loaded(f'{txt}.getCookies')['cookies']

        if as_dict:
            return {cookie['name']: cookie['value'] for cookie in cookies}
        elif all_info:
            return cookies
        else:
            return [{'name': cookie['name'], 'value': cookie['value'], 'domain': cookie['domain']}
                    for cookie in cookies]

    def frame(self, loc_ind_ele, timeout=None):
        """获取页面中一个frame对象
        :param loc_ind_ele: 定位符、iframe序号、ChromiumFrame对象，序号从1开始，可传入负数获取倒数第几个
        :param timeout: 查找元素超时时间（秒）
        :return: ChromiumFrame对象
        """
        if isinstance(loc_ind_ele, str):
            if not is_loc(loc_ind_ele):
                xpath = f'xpath://*[(name()="iframe" or name()="frame") and ' \
                        f'(@name="{loc_ind_ele}" or @id="{loc_ind_ele}")]'
            else:
                xpath = loc_ind_ele
            ele = self._obj._ele(xpath, timeout=timeout)
            if ele and ele._type != 'ChromiumFrame':
                raise TypeError('该定位符不是指向frame元素。')
            r = ele

        elif isinstance(loc_ind_ele, tuple):
            ele = self._obj._ele(loc_ind_ele, timeout=timeout)
            if ele and ele._type != 'ChromiumFrame':
                raise TypeError('该定位符不是指向frame元素。')
            r = ele

        elif isinstance(loc_ind_ele, int):
            if loc_ind_ele == 0:
                loc_ind_ele = 1
            elif loc_ind_ele < 0:
                loc_ind_ele = f'last()+{loc_ind_ele}+1'
            xpath = f'xpath:(//*[name()="frame" or name()="iframe"])[{loc_ind_ele}]'
            r = self._obj._ele(xpath, timeout=timeout)

        elif loc_ind_ele._type == 'ChromiumFrame':
            r = loc_ind_ele

        else:
            raise TypeError('必须传入定位符、iframe序号、id、name、ChromiumFrame对象其中之一。')

        if isinstance(r, NoneElement):
            r.method = 'get_frame()'
            r.args = {'loc_ind_ele': loc_ind_ele}
        return r

    def frames(self, locator=None, timeout=None):
        """获取所有符合条件的frame对象
        :param locator: 定位符，为None时返回所有
        :param timeout: 查找超时时间（秒）
        :return: ChromiumFrame对象组成的列表
        """
        locator = locator or 'xpath://*[name()="iframe" or name()="frame"]'
        frames = self._obj._ele(locator, timeout=timeout, index=None, raise_err=False)
        return [i for i in frames if i._type == 'ChromiumFrame']

    def session_storage(self, item=None):
        """获取sessionStorage信息，不设置item则获取全部
        :param item: 要获取的项，不设置则返回全部
        :return: sessionStorage一个或所有项内容
        """
        if item:
            js = f'sessionStorage.getItem("{item}");'
            return self._obj.run_js_loaded(js, as_expr=True)
        else:
            js = '''
            var dp_ls_len = sessionStorage.length;
            var dp_ls_arr = new Array();
            for(var i = 0; i < dp_ls_len; i++) {
                var getKey = sessionStorage.key(i);
                var getVal = sessionStorage.getItem(getKey);
                dp_ls_arr[i] = {'key': getKey, 'val': getVal}
            }
            return dp_ls_arr;
            '''
            return {i['key']: i['val'] for i in self._obj.run_js_loaded(js)}

    def local_storage(self, item=None):
        """获取localStorage信息，不设置item则获取全部
        :param item: 要获取的项目，不设置则返回全部
        :return: localStorage一个或所有项内容
        """
        if item:
            js = f'localStorage.getItem("{item}");'
            return self._obj.run_js_loaded(js, as_expr=True)
        else:
            js = '''
            var dp_ls_len = localStorage.length;
            var dp_ls_arr = new Array();
            for(var i = 0; i < dp_ls_len; i++) {
                var getKey = localStorage.key(i);
                var getVal = localStorage.getItem(getKey);
                dp_ls_arr[i] = {'key': getKey, 'val': getVal}
            }
            return dp_ls_arr;
            '''
            return {i['key']: i['val'] for i in self._obj.run_js_loaded(js)}

    def screenshot(self, path=None, name=None, as_bytes=None, as_base64=None,
                   full_page=False, left_top=None, right_bottom=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :param full_page: 是否整页截图，为True截取整个网页，为False截取可视窗口
        :param left_top: 截取范围左上角坐标
        :param right_bottom: 截取范围右下角角坐标
        :return: 图片完整路径或字节文本
        """
        return self._obj._get_screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64,
                                         full_page=full_page, left_top=left_top, right_bottom=right_bottom)


class ChromiumFrameGetter(ChromiumBaseGetter):

    def session_storage(self, item=None):
        """获取sessionStorage信息，不设置item则获取全部
        :param item: 要获取的项，不设置则返回全部
        :return: sessionStorage一个或所有项内容
        """
        if item:
            js = f'sessionStorage.getItem("{item}");'
            return self._obj._target_page.run_js_loaded(js, as_expr=True)
        else:
            js = '''
            var dp_ls_len = sessionStorage.length;
            var dp_ls_arr = new Array();
            for(var i = 0; i < dp_ls_len; i++) {
                var getKey = sessionStorage.key(i);
                var getVal = sessionStorage.getItem(getKey);
                dp_ls_arr[i] = {'key': getKey, 'val': getVal}
            }
            return dp_ls_arr;
            '''
            return {i['key']: i['val'] for i in self._obj._target_page.run_js_loaded(js)}

    def local_storage(self, item=None):
        """获取localStorage信息，不设置item则获取全部
        :param item: 要获取的项目，不设置则返回全部
        :return: localStorage一个或所有项内容
        """
        if item:
            js = f'localStorage.getItem("{item}");'
            return self._obj._target_page.run_js_loaded(js, as_expr=True)
        else:
            js = '''
            var dp_ls_len = localStorage.length;
            var dp_ls_arr = new Array();
            for(var i = 0; i < dp_ls_len; i++) {
                var getKey = localStorage.key(i);
                var getVal = localStorage.getItem(getKey);
                dp_ls_arr[i] = {'key': getKey, 'val': getVal}
            }
            return dp_ls_arr;
            '''
            return {i['key']: i['val'] for i in self._obj._target_page.run_js_loaded(js)}

    def screenshot(self, path=None, name=None, as_bytes=None, as_base64=None):
        """对页面进行截图，可对整个网页、可见网页、指定范围截图。对可视范围外截图需要90以上版本浏览器支持
        :param path: 文件保存路径
        :param name: 完整文件名，后缀可选 'jpg','jpeg','png','webp'
        :param as_bytes: 是否以字节形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数和as_base64参数无效
        :param as_base64: 是否以base64字符串形式返回图片，可选 'jpg','jpeg','png','webp'，生效时path参数无效
        :return: 图片完整路径或字节文本
        """
        return self._obj.frame_ele.get.screenshot(path=path, name=name, as_bytes=as_bytes, as_base64=as_base64)


class SessionPageGetter(Getter):
    def __call__(self, url, show_errmsg=False, retry=None, interval=None, timeout=None, **kwargs):
        """用get方式跳转到url，可输入文件路径
        :param url: 目标url，可指定本地文件路径
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数，为None时使用页面对象retry_times属性值
        :param interval: 重试间隔（秒），为None时使用页面对象retry_interval属性值
        :param timeout: 连接超时时间（秒），为None时使用页面对象timeout属性值
        :param kwargs: 连接参数
        :return: url是否可用
        """
        if isinstance(url, Path):
            url = str(url.absolute())
        if not url.lower().startswith('http'):
            if url.startswith('file:///'):
                url = url[8:]
            if Path(url).exists():
                with open(url, 'rb') as f:
                    r = Response()
                    r._content = f.read()
                    r.status_code = 200
                    self._response = r
                return
        return self._obj._s_connect(url, 'get', show_errmsg, retry, interval, **kwargs)

    def cookies(self, as_dict=False, all_domains=False, all_info=False):
        """返回cookies
        :param as_dict: 是否以字典方式返回，False则以list返回
        :param all_domains: 是否返回所有域的cookies
        :param all_info: 是否返回所有信息，False则只返回name、value、domain
        :return: cookies信息
        """
        if all_domains:
            cookies = self._obj.session.cookies
        else:
            if self._obj.url:
                ex_url = extract(self._obj._session_url)
                domain = f'{ex_url.domain}.{ex_url.suffix}' if ex_url.suffix else ex_url.domain

                cookies = tuple(x for x in self._obj.session.cookies if domain in x.domain or x.domain == '')
            else:
                cookies = tuple(x for x in self._obj.session.cookies)

        if as_dict:
            return {x.name: x.value for x in cookies}
        elif all_info:
            return [cookie_to_dict(cookie) for cookie in cookies]
        else:
            r = []
            for c in cookies:
                c = cookie_to_dict(c)
                r.append({'name': c['name'], 'value': c['value'], 'domain': c['domain']})
            return r
