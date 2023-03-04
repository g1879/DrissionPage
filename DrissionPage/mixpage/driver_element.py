# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from os import sep
from pathlib import Path
from time import time, perf_counter, sleep

from selenium.common.exceptions import TimeoutException, JavascriptException, InvalidElementStateException, \
    NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from .base import DrissionElement, BaseElement
from DrissionPage.commons.locator import str_to_loc, get_loc
from DrissionPage.commons.tools import get_usable_path
from DrissionPage.commons.web import format_html, get_ele_txt
from .session_element import make_session_ele


class DriverElement(DrissionElement):
    """driver模式的元素对象，包装了一个WebElement对象，并封装了常用功能"""

    def __init__(self, ele, page=None):
        """初始化对象
        :param ele: 被包装的WebElement元素
        :param page: 元素所在页面
        """
        super().__init__(page)
        self._select = None
        self._scroll = None
        self._inner_ele = ele

    def __repr__(self):
        attrs = [f"{attr}='{self.attrs[attr]}'" for attr in self.attrs]
        return f'<DriverElement {self.tag} {" ".join(attrs)}>'

    def __call__(self, loc_or_str, timeout=None):
        """在内部查找元素
        例：ele2 = ele1('@id=ele_id')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: DriverElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    # -----------------共有属性和方法-------------------
    @property
    def inner_ele(self):
        return self._inner_ele

    @property
    def tag(self):
        """返回元素类型"""
        return self._inner_ele.tag_name.lower()

    @property
    def html(self):
        """返回元素outerHTML文本"""
        return self.inner_ele.get_attribute('outerHTML')

    @property
    def inner_html(self):
        """返回元素innerHTML文本"""
        return self.inner_ele.get_attribute('innerHTML')

    @property
    def attrs(self):
        """返回元素所有属性及值"""
        js = '''
        var dom=arguments[0];
        var names="(";
        var len = dom.attributes.length;
        for(var i=0;i<len;i++){
            let it = dom.attributes[i];
            let localName = it.localName;
            //let value = it.value;
            //names += "'" + localName + "':'" + value.replace(/'/g,"\\\\'") + "', ";  
            names += "'" + localName + "',";  
        }
        names+=")"
        return names;  
        '''
        return {attr: self.attr(attr) for attr in eval(self.run_script(js))}

    @property
    def text(self):
        """返回元素内所有文本"""
        return get_ele_txt(make_session_ele(self.html))

    @property
    def raw_text(self):
        """返回未格式化处理的元素内文本"""
        return self.inner_ele.get_attribute('innerText')

    def attr(self, attr):
        """获取attribute属性值
        :param attr: 属性名
        :return: 属性值文本
        """
        if attr == 'text':
            return self.text
        elif attr == 'innerText':
            return self.raw_text
        elif attr in ('html', 'outerHTML'):
            return self.html
        elif attr == 'innerHTML':
            return self.inner_html
        else:
            return format_html(self.inner_ele.get_attribute(attr))

    def ele(self, loc_or_str, timeout=None):
        """返回当前元素下级符合条件的第一个元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: DriverElement对象或属性、文本
        """
        return self._ele(loc_or_str, timeout)

    def eles(self, loc_or_str, timeout=None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: DriverElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_str=None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_str)

    def s_eles(self, loc_or_str):
        """查找所有符合条件的元素以SessionElement列表形式返回
        :param loc_or_str: 定位符
        :return: SessionElement或属性、文本组成的列表
        """
        return make_session_ele(self, loc_or_str, single=False)

    def _ele(self, loc_or_str, timeout=None, single=True, relative=False):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :param relative: WebPage用的表示是否相对定位的参数
        :return: DriverElement对象
        """
        return make_driver_ele(self, loc_or_str, single, timeout)

    def _get_ele_path(self, mode):
        """返获取css路径或xpath路径"""
        if mode == 'xpath':
            txt1 = 'var tag = el.nodeName.toLowerCase();'
            # txt2 = '''return '//' + tag + '[@id="' + el.id + '"]'  + path;'''
            txt3 = ''' && sib.nodeName.toLowerCase()==tag'''
            txt4 = '''
            if(nth>1){path = '/' + tag + '[' + nth + ']' + path;}
                    else{path = '/' + tag + path;}'''
            txt5 = '''return path;'''

        elif mode == 'css':
            txt1 = ''
            # txt2 = '''return '#' + el.id + path;'''
            txt3 = ''
            txt4 = '''path = '>' + ":nth-child(" + nth + ")" + path;'''
            txt5 = '''return path.substr(1);'''

        else:
            raise ValueError(f"mode参数只能是'xpath'或'css'，现在是：'{mode}'。")

        js = '''
        function e(el) {
            if (!(el instanceof Element)) return;
            var path = '';
            while (el.nodeType === Node.ELEMENT_NODE) {
                ''' + txt1 + '''
                    var sib = el, nth = 0;
                    while (sib) {
                        if(sib.nodeType === Node.ELEMENT_NODE''' + txt3 + '''){nth += 1;}
                        sib = sib.previousSibling;
                    }
                    ''' + txt4 + '''
                el = el.parentNode;
            }
            ''' + txt5 + '''
        }
        return e(arguments[0]);
        '''
        res_txt = self.run_script(js)
        return f':root{res_txt}' if mode == 'css' else res_txt

    # -----------------driver独有属性和方法-------------------
    @property
    def size(self):
        """返回元素宽和高"""
        return self.inner_ele.size

    @property
    def location(self):
        """返回元素左上角坐标"""
        return self.inner_ele.location

    @property
    def shadow_root(self):
        """返回当前元素的shadow_root元素对象"""
        shadow = self.run_script('return arguments[0].shadowRoot')
        if shadow:
            from .shadow_root_element import ShadowRootElement
            return ShadowRootElement(shadow, self)

    @property
    def sr(self):
        """返回当前元素的shadow_root元素对象"""
        return self.shadow_root

    @property
    def pseudo_before(self):
        """返回当前元素的::before伪元素内容"""
        return self.style('content', 'before')

    @property
    def pseudo_after(self):
        """返回当前元素的::after伪元素内容"""
        return self.style('content', 'after')

    @property
    def select(self):
        """返回专门处理下拉列表的Select类，非下拉列表元素返回False"""
        if self._select is None:
            if self.tag != 'select':
                self._select = False
            else:
                self._select = Select(self)

        return self._select

    @property
    def scroll(self):
        """用于滚动滚动条的对象"""
        if self._scroll is None:
            self._scroll = Scroll(self)
        return self._scroll

    def parent(self, level_or_loc=1):
        """返回上面某一级父元素，可指定层数或用查询语法定位
        :param level_or_loc: 第几级父元素，或定位符
        :return: 上级元素对象
        """
        return super().parent(level_or_loc)

    def prev(self, index=1, filter_loc='', timeout=0):
        """返回前面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param index: 前面第几个查询结果元素
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        index, filter_loc = _exchange_arguments(index, filter_loc)
        return super().prev(index, filter_loc, timeout)

    def next(self, index=1, filter_loc='', timeout=0):
        """返回后面的一个兄弟元素，可用查询语法筛选，可指定返回筛选结果的第几个
        :param index: 后面第几个查询结果元素
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素
        """
        index, filter_loc = _exchange_arguments(index, filter_loc)
        return super().next(index, filter_loc, timeout)

    def before(self, index=1, filter_loc='', timeout=None):
        """返回当前元素前面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元，而是整个DOM文档
        :param index: 前面第几个查询结果元素
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的某个元素或节点
        """
        index, filter_loc = _exchange_arguments(index, filter_loc)
        return super().before(index, filter_loc, timeout)

    def after(self, index=1, filter_loc='', timeout=None):
        """返回当前元素后面的一个元素，可指定筛选条件和第几个。查找范围不限兄弟元，而是整个DOM文档
        :param index: 后面第几个查询结果元素
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素后面的某个元素或节点
        """
        index, filter_loc = _exchange_arguments(index, filter_loc)
        return super().after(index, filter_loc, timeout)

    def prevs(self, filter_loc='', timeout=0):
        """返回前面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        return super().prevs(filter_loc, timeout)

    def nexts(self, filter_loc='', timeout=0):
        """返回后面全部兄弟元素或节点组成的列表，可用查询语法筛选
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 兄弟元素或节点文本组成的列表
        """
        return super().nexts(filter_loc, timeout)

    def befores(self, filter_loc='', timeout=None):
        """返回当前元素后面符合条件的全部兄弟元素或节点组成的列表，可用查询语法筛选。查找范围不限兄弟元，而是整个DOM文档
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素前面的元素或节点组成的列表
        """
        return super().befores(filter_loc, timeout)

    def afters(self, filter_loc='', timeout=None):
        """返回当前元素前面符合条件的全部兄弟元素或节点组成的列表，可用查询语法筛选。查找范围不限兄弟元，而是整个DOM文档
        :param filter_loc: 用于筛选元素的查询语法
        :param timeout: 查找元素的超时时间
        :return: 本元素后面的元素或节点组成的列表
        """
        return super().afters(filter_loc, timeout)

    def left(self, index=1, filter_loc=''):
        """获取网页上显示在当前元素左边的某个元素，可设置选取条件，可指定结果中第几个
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('left', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def right(self, index=1, filter_loc=''):
        """获取网页上显示在当前元素右边的某个元素，可设置选取条件，可指定结果中第几个
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('right', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def above(self, index=1, filter_loc=''):
        """获取网页上显示在当前元素上边的某个元素，可设置选取条件，可指定结果中第几个
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('left', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def below(self, index=1, filter_loc=''):
        """获取网页上显示在当前元素下边的某个元素，可设置选取条件，可指定结果中第几个
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('left', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def near(self, index=1, filter_loc=''):
        """获取网页上显示在当前元素最近的某个元素，可设置选取条件，可指定结果中第几个
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('near', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def lefts(self, filter_loc=''):
        """获取网页上显示在当前元素左边的所有元素，可设置选取条件，从近到远排列
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('left', filter_loc)

    def rights(self, filter_loc=''):
        """获取网页上显示在当前元素右边的所有元，可设置选取条件，从近到远排列
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('right', filter_loc)

    def aboves(self, filter_loc=''):
        """获取网页上显示在当前元素上边的所有元素，可设置选取条件，从近到远排列
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('left', filter_loc)

    def belows(self, filter_loc=''):
        """获取网页上显示在当前元素下边的所有元素，可设置选取条件，从近到远排列
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('left', filter_loc)

    def nears(self, filter_loc=''):
        """获取网页上显示在当前元素附近元素，可设置选取条件，从近到远排列
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('near', filter_loc)

    def wait_ele(self, loc_or_ele, timeout=None):
        """等待子元素从dom删除、显示、隐藏
        :param loc_or_ele: 可以是元素、查询字符串、loc元组
        :param timeout: 等待超时时间
        :return: 等待是否成功
        """
        return ElementWaiter(self, loc_or_ele, timeout)

    def style(self, style, pseudo_ele=''):
        """返回元素样式属性值，可获取伪元素属性值
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"' if pseudo_ele.startswith(':') else f', "::{pseudo_ele}"'
        r = self.run_script(f'return window.getComputedStyle(arguments[0]{pseudo_ele}).getPropertyValue("{style}");')

        return None if r == 'none' else r

    def click(self, by_js=None, timeout=None):
        """点击元素
        尝试点击直到超时，若都失败就改用js点击
        :param by_js: 是否用js点击，为True时直接用js点击，为False时重试失败也不会改用js
        :param timeout: 尝试点击的超时时间，不指定则使用父页面的超时时间
        :return: 是否点击成功
        """

        def do_it() -> bool:
            try:
                self.inner_ele.click()
                return True
            except Exception:
                return False

        if not by_js:
            timeout = timeout if timeout is not None else self.page.timeout
            t1 = perf_counter()
            click = do_it()
            while not click and perf_counter() - t1 <= timeout:
                click = do_it()

            if click:
                return True

        # 若点击失败，用js方式点击
        if by_js is not False:
            self.run_script('arguments[0].click()')
            return True

        return False

    def click_at(self, x=None, y=None, by_js=False):
        """带偏移量点击本元素，相对于左上角坐标。不传入x或y值时点击元素中点
        :param x: 相对元素左上角坐标的x轴偏移量
        :param y: 相对元素左上角坐标的y轴偏移量
        :param by_js: 是否用js点击
        :return: None
        """
        if by_js:
            x = self.location['x'] + int(x) if x is not None else self.location['x'] + self.size['width'] // 2
            y = self.location['y'] + int(y) if y is not None else self.location['y'] + self.size['height'] // 2
            js = f"""
            var ev = document.createEvent('HTMLEvents'); 
            ev.clientX = {x};
            ev.clientY = {y};
            ev.initEvent('click', false, true);
            arguments[0].dispatchEvent(ev);
            """
            self.run_script(js)

        else:
            x = int(x) if x is not None else self.size['width'] // 2
            y = int(y) if y is not None else self.size['height'] // 2

            from selenium.webdriver import ActionChains
            ActionChains(self.page.driver).move_to_element_with_offset(self.inner_ele, x, y).click().perform()

    def r_click(self):
        """右键单击"""
        from selenium.webdriver import ActionChains
        ActionChains(self.page.driver).context_click(self.inner_ele).perform()

    def r_click_at(self, x=None, y=None):
        """带偏移量右键单击本元素，相对于左上角坐标。不传入x或y值时点击元素中点
        :param x: 相对元素左上角坐标的x轴偏移量
        :param y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        x = int(x) if x is not None else self.size['width'] // 2
        y = int(y) if y is not None else self.size['height'] // 2
        from selenium.webdriver import ActionChains
        ActionChains(self.page.driver).move_to_element_with_offset(self.inner_ele, x, y).context_click().perform()

    def input(self, vals, clear=True, insure=True, timeout=None):
        """输入文本或组合键，也可用于输入文件路径到input元素（文件间用\n间隔）
        :param vals: 文本值或按键组合
        :param clear: 输入前是否清空文本框
        :param insure: 确保输入正确，解决文本框有时输入失效的问题，不能用于输入组合键
        :param timeout: 尝试输入的超时时间，不指定则使用父页面的超时时间，只在insure为True时生效
        :return: bool
        """
        if not insure or self.tag != 'input' or self.prop('type') != 'text':  # 普通输入
            if not isinstance(vals, (str, tuple)):
                vals = str(vals)
            if clear:
                self.inner_ele.clear()

            self.inner_ele.send_keys(*vals)
            return True

        else:  # 确保输入正确
            if not isinstance(vals, str):
                vals = str(vals)
            enter = '\n' if vals.endswith('\n') else None
            full_txt = vals if clear else f'{self.attr("value")}{vals}'
            full_txt = full_txt.rstrip('\n')

            self.click(by_js=True)
            timeout = timeout if timeout is not None else self.page.timeout
            t1 = perf_counter()
            while self.is_valid() and self.attr('value') != full_txt and perf_counter() - t1 <= timeout:
                try:
                    if clear:
                        self.inner_ele.send_keys(u'\ue009', 'a', u'\ue017')  # 有些ui下clear()不生效，用CTRL+a代替
                    self.inner_ele.send_keys(vals)

                except Exception:
                    pass

            if not self.is_valid():
                return False
            else:
                if self.attr('value') != full_txt:
                    return False
                else:
                    if enter:
                        self.inner_ele.send_keys(enter)
                    return True

    def run_script(self, script, *args):
        """执行js代码，代码中用arguments[0]表示自己
        :param script: js文本
        :param args: 传入的参数
        :return: js执行结果
        """
        return self.inner_ele.parent.execute_script(script, self.inner_ele, *args)

    def submit(self):
        """提交表单"""
        try:
            self.inner_ele.submit()
            return True
        except Exception:
            pass

    def clear(self, insure=True):
        """清空元素文本
        :param insure: 是否确保清空
        :return: 是否清空成功，不能清空的元素返回None
        """
        if insure:
            return self.input('')

        else:
            try:
                self.inner_ele.clear()
                return True
            except InvalidElementStateException:
                return None

    def is_selected(self):
        """是否选中"""
        return self.inner_ele.is_selected()

    def is_enabled(self):
        """是否可用"""
        return self.inner_ele.is_enabled()

    def is_displayed(self):
        """是否可见"""
        return self.inner_ele.is_displayed()

    def is_valid(self):
        """用于判断元素是否还在DOM内，应对页面跳转元素不能用的情况"""
        try:
            self.is_enabled()
            return True
        except Exception:
            return False

    def screenshot(self, path=None, filename=None, as_bytes=False):
        """对元素进行截图
        :param path: 保存路径
        :param filename: 图片文件名，不传入时以元素tag name命名
        :param as_bytes: 是否已字节形式返回图片，为True时上面两个参数失效
        :return: 图片完整路径或字节文本
        """
        # 等待元素加载完成
        if self.tag == 'img':
            js = ('return arguments[0].complete && typeof arguments[0].naturalWidth != "undefined" '
                  '&& arguments[0].naturalWidth > 0 && typeof arguments[0].naturalHeight != "undefined" '
                  '&& arguments[0].naturalHeight > 0')
            t1 = perf_counter()
            while not self.run_script(js) and perf_counter() - t1 < self.page.timeout:
                sleep(.1)

        if as_bytes:
            return self.inner_ele.screenshot_as_png

        name = filename or self.tag
        path = Path(path or '.').absolute()
        path.mkdir(parents=True, exist_ok=True)
        if not name.lower().endswith('.png'):
            name = f'{name}.png'

        img_path = str(get_usable_path(f'{path}{sep}{name}'))
        self.inner_ele.screenshot(img_path)

        return img_path

    def prop(self, prop):
        """获取property属性值
        :param prop: 属性名
        :return: 属性值文本
        """
        return format_html(self.inner_ele.get_property(prop))

    def set_prop(self, prop, value):
        """设置元素property属性
        :param prop: 属性名
        :param value: 属性值
        :return: 是否设置成功
        """
        try:
            value = value.replace("'", "\\'")
            self.run_script(f"arguments[0].{prop}='{value}';")
            return True
        except Exception:
            return False

    def set_attr(self, attr, value):
        """设置元素attribute属性
        :param attr: 属性名
        :param value: 属性值
        :return: 是否设置成功
        """
        try:
            self.run_script(f"arguments[0].setAttribute(arguments[1], arguments[2]);", attr, value)
            return True
        except Exception:
            return False

    def remove_attr(self, attr):
        """删除元素attribute属性
        :param attr: 属性名
        :return: 是否删除成功
        """
        try:
            self.run_script(f'arguments[0].removeAttribute("{attr}");')
            return True
        except Exception:
            return False

    def drag(self, x, y, speed=40, shake=True):
        """拖拽当前元素到相对位置
        :param x: x变化值
        :param y: y变化值
        :param speed: 拖动的速度，传入0即瞬间到达
        :param shake: 是否随机抖动
        :return: None
        """
        x += self.location['x'] + self.size['width'] // 2
        y += self.location['y'] + self.size['height'] // 2
        self.drag_to((x, y), speed, shake)

    def drag_to(self, ele_or_loc, speed=40, shake=True):
        """拖拽当前元素，目标为另一个元素或坐标元组
        :param ele_or_loc: 另一个元素或坐标元组，坐标为元素中点的坐标
        :param speed: 拖动的速度，传入0即瞬间到达
        :param shake: 是否随机抖动
        :return: None
        """
        # x, y：目标点坐标
        if isinstance(ele_or_loc, (DriverElement, WebElement)):
            target_x = ele_or_loc.location['x'] + ele_or_loc.size['width'] // 2
            target_y = ele_or_loc.location['y'] + ele_or_loc.size['height'] // 2
        elif isinstance(ele_or_loc, tuple):
            target_x, target_y = ele_or_loc
        else:
            raise TypeError('需要DriverElement、WebElement对象或坐标。')

        current_x = self.location['x'] + self.size['width'] // 2
        current_y = self.location['y'] + self.size['height'] // 2
        width = target_x - current_x
        height = target_y - current_y
        num = 0 if not speed else int(((abs(width) ** 2 + abs(height) ** 2) ** .5) // speed)

        # 将要经过的点存入列表
        points = [(int(current_x + i * (width / num)), int(current_y + i * (height / num))) for i in range(1, num)]
        points.append((target_x, target_y))

        from selenium.webdriver import ActionChains
        from random import randint
        actions = ActionChains(self.page.driver)
        actions.click_and_hold(self.inner_ele)

        # 逐个访问要经过的点
        for x, y in points:
            if shake:
                x += randint(-3, 4)
                y += randint(-3, 4)
            actions.move_by_offset(x - current_x, y - current_y)
            current_x, current_y = x, y
        actions.release().perform()

    def hover(self, x=None, y=None):
        """鼠标悬停，可接受偏移量，偏移量相对于元素左上角坐标。不传入x或y值时悬停在元素中点
        :param x: 相对元素左上角坐标的x轴偏移量
        :param y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        from selenium.webdriver import ActionChains
        x = int(x) if x is not None else self.size['width'] // 2
        y = int(y) if y is not None else self.size['height'] // 2
        ActionChains(self.page.driver).move_to_element_with_offset(self.inner_ele, x, y).perform()

    def _get_relative_eles(self, mode, loc=''):
        """获取网页上相对于当前元素周围的某个元素，可设置选取条件
        :param mode: 可选：'left', 'right', 'above', 'below', 'near'
        :param loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        from selenium.webdriver.support.relative_locator import RelativeBy

        if isinstance(loc, str):
            loc = str_to_loc(loc)

        try:
            if mode == 'left':
                eles = self.page.driver.find_elements(RelativeBy({loc[0]: loc[1]}).to_left_of(self.inner_ele))
            elif mode == 'right':
                eles = self.page.driver.find_elements(RelativeBy({loc[0]: loc[1]}).to_right_of(self.inner_ele))
            elif mode == 'above':
                eles = self.page.driver.find_elements(RelativeBy({loc[0]: loc[1]}).above(self.inner_ele))
            elif mode == 'below':
                eles = self.page.driver.find_elements(RelativeBy({loc[0]: loc[1]}).below(self.inner_ele))
            else:  # 'near'
                eles = self.page.driver.find_elements(RelativeBy({loc[0]: loc[1]}).near(self.inner_ele))

            return [self.page.ele(e) for e in eles]

        except IndexError:
            raise ValueError('未找到元素，请检查浏览器版本，低版本的浏览器无法使用此方法。')


def make_driver_ele(page_or_ele, loc, single=True, timeout=None):
    """执行driver模式元素的查找
    页面查找元素及元素查找下级元素皆使用此方法
    :param page_or_ele: DriverPage对象或DriverElement对象
    :param loc: 元素定位元组
    :param single: True则返回第一个，False则返回全部
    :param timeout: 查找元素超时时间
    :return: 返回DriverElement元素或它们组成的列表
    """
    # ---------------处理定位符---------------
    if isinstance(loc, (str, tuple)):
        loc = get_loc(loc)

    elif str(type(loc)).endswith('RelativeBy'):
        page = page_or_ele.page if isinstance(page_or_ele, BaseElement) else page_or_ele
        driver = page.driver
        eles = driver.find_elements(loc)
        return DriverElement(eles[0], page) if single else [DriverElement(ele, page) for ele in eles]

    else:
        raise ValueError("定位符必须为str、长度为2的tuple、或RelativeBy对象。")

    # ---------------设置 page 和 driver---------------
    if isinstance(page_or_ele, BaseElement):  # 传入DriverElement 或 ShadowRootElement
        loc_str = loc[1]
        if loc[0] == 'xpath' and loc[1].lstrip().startswith('/'):
            loc_str = f'.{loc_str}'
        elif loc[0] == 'css selector' and loc[1].lstrip().startswith('>') and isinstance(page_or_ele, DriverElement):
            loc_str = f'{page_or_ele.css_path}{loc[1]}'
        loc = loc[0], loc_str

        page = page_or_ele.page
        driver = page_or_ele.inner_ele

    else:  # 传入的是DriverPage对象
        page = page_or_ele
        driver = page_or_ele.driver

    # -----------------设置等待对象-----------------
    if timeout is not None and timeout != page.timeout:
        wait = WebDriverWait(driver, timeout=timeout)
    else:
        page.wait_object._driver = driver
        wait = page.wait_object

    # ---------------执行查找-----------------
    try:
        # 使用xpath查找
        if loc[0] == 'xpath':
            return wait.until(ElementsByXpath(page, loc[1], single, timeout))

        # 使用css selector查找
        else:
            if single:
                return DriverElement(wait.until(ec.presence_of_element_located(loc)), page)
            else:
                eles = wait.until(ec.presence_of_all_elements_located(loc))
                return [DriverElement(ele, page) for ele in eles]

    except TimeoutException:
        return [] if not single else None

    except InvalidElementStateException:
        raise ValueError(f'无效的查找语句：{loc}')


class ElementsByXpath(object):
    """用js通过xpath获取元素、节点或属性，与WebDriverWait配合使用"""

    def __init__(self, page, xpath=None, single=False, timeout=10):
        """
        :param page: DrissionPage对象
        :param xpath: xpath文本
        :param single: True则返回第一个，False则返回全部
        :param timeout: 超时时间
        """
        self.page = page
        self.xpath = xpath
        self.single = single
        self.timeout = timeout

    def __call__(self, ele_or_driver):

        def get_nodes(node=None, xpath_txt=None, type_txt='7'):
            """用js通过xpath获取元素、节点或属性
            :param node: 'document' 或 元素对象
            :param xpath_txt: xpath语句
            :param type_txt: resultType,参考 https://developer.mozilla.org/zh-CN/docs/Web/API/Document/evaluate
            :return: 元素对象或属性、文本字符串
            """
            node_txt = 'document' if not node or node == 'document' else 'arguments[0]'
            for_txt = ''

            # 获取第一个元素、节点或属性
            if type_txt == '9':
                return_txt = '''
                    if(e.singleNodeValue.constructor.name=="Text"){return e.singleNodeValue.data;}
                    else if(e.singleNodeValue.constructor.name=="Attr"){return e.singleNodeValue.nodeValue;}
                    else if(e.singleNodeValue.constructor.name=="Comment"){return e.singleNodeValue.nodeValue;}
                    else{return e.singleNodeValue;}
                    '''

            # 按顺序获取所有元素、节点或属性
            elif type_txt == '7':
                for_txt = """
                    var a=new Array();
                    for(var i = 0; i <e.snapshotLength ; i++){
                        if(e.snapshotItem(i).constructor.name=="Text"){a.push(e.snapshotItem(i).data);}
                        else if(e.snapshotItem(i).constructor.name=="Attr"){a.push(e.snapshotItem(i).nodeValue);}
                        else if(e.snapshotItem(i).constructor.name=="Comment"){a.push(e.snapshotItem(i).nodeValue);}
                        else{a.push(e.snapshotItem(i));}
                    }
                    """
                return_txt = 'return a;'

            elif type_txt == '2':
                return_txt = 'return e.stringValue;'
            elif type_txt == '1':
                return_txt = 'return e.numberValue;'
            else:
                return_txt = 'return e.singleNodeValue;'

            js = """
                var e=document.evaluate(arguments[1], """ + node_txt + """, null, """ + type_txt + """,null);
                """ + for_txt + """
                """ + return_txt + """
                """
            return driver.execute_script(js, node, xpath_txt)

        if isinstance(ele_or_driver, RemoteWebDriver):
            driver, the_node = ele_or_driver, 'document'
        else:
            driver, the_node = ele_or_driver.parent, ele_or_driver

        # 把lxml元素对象包装成DriverElement对象并按需要返回第一个或全部
        if self.single:
            try:
                e = get_nodes(the_node, xpath_txt=self.xpath, type_txt='9')

                if isinstance(e, WebElement):
                    return DriverElement(e, self.page)
                elif isinstance(e, str):
                    return format_html(e)
                else:
                    return e

            # 找不到目标时
            except JavascriptException as err:
                if 'The result is not a node set' in err.msg:
                    try:
                        return get_nodes(the_node, xpath_txt=self.xpath, type_txt='1')
                    except JavascriptException:
                        return None
                else:
                    return None

        else:  # 返回全部
            return ([DriverElement(x, self.page) if isinstance(x, WebElement)
                     else format_html(x)
                     for x in get_nodes(the_node, xpath_txt=self.xpath)
                     if x != '\n'])


class Select(object):
    """Select 类专门用于处理 d 模式下 select 标签"""

    def __init__(self, ele: DriverElement):
        """
        :param ele: select 元素对象
        """
        if ele.tag != 'select':
            raise TypeError(f"select方法只能在<select>元素使用，现在是：{ele.tag}。")

        from selenium.webdriver.support.select import Select as SeleniumSelect
        self.inner_ele = ele
        self.select_ele = SeleniumSelect(ele.inner_ele)

    def __call__(self, text_or_index, timeout=None):
        """选定下拉列表中子元素
        :param text_or_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: None
        """
        timeout = timeout if timeout is not None else self.inner_ele.page.timeout
        return self.select(text_or_index, timeout=timeout)

    @property
    def is_multi(self):
        """返回是否多选表单"""
        return self.select_ele.is_multiple

    @property
    def options(self):
        """返回所有选项元素组成的列表"""
        return self.inner_ele.eles('tag:option')

    @property
    def selected_option(self):
        """返回第一个被选中的option元素
        :return: DriverElement对象或None
        """
        ele = self.inner_ele.run_script('return arguments[0].options[arguments[0].selectedIndex];')
        return None if ele is None else DriverElement(ele, self.inner_ele.page)

    @property
    def selected_options(self):
        """返回所有被选中的option元素列表
        :return: DriverElement对象组成的列表
        """
        return [x for x in self.options if x.is_selected()]

    def clear(self):
        """清除所有已选项"""
        self.select_ele.deselect_all()

    def select(self, text_or_index, timeout=None):
        """选定下拉列表中子元素
        :param text_or_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: 是否选择成功
        """
        i = 'index' if isinstance(text_or_index, int) else 'text'
        timeout = timeout if timeout is not None else self.inner_ele.page.timeout
        return self._select(text_or_index, i, False, timeout)

    def select_by_value(self, value, timeout=None):
        """此方法用于根据value值选择项。当元素是多选列表时，可以接收list或tuple
        :param value: value属性值，传入list或tuple可选择多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: None
        """
        timeout = timeout if timeout is not None else self.inner_ele.page.timeout
        return self._select(value, 'value', False, timeout)

    def deselect(self, text_or_index, timeout=None):
        """取消选定下拉列表中子元素
        :param text_or_index: 根据文本或序号取消择选项，若允许多选，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: None
        """
        i = 'index' if isinstance(text_or_index, int) else 'text'
        timeout = timeout if timeout is not None else self.inner_ele.page.timeout
        return self._select(text_or_index, i, True, timeout)

    def deselect_by_value(self, value, timeout=None):
        """此方法用于根据value值取消选择项。当元素是多选列表时，可以接收list或tuple
        :param value: value属性值，传入list或tuple可取消多项
        :param timeout: 超时时间，不输入默认实用页面超时时间
        :return: None
        """
        timeout = timeout if timeout is not None else self.inner_ele.page.timeout
        return self._select(value, 'value', True, timeout)

    def invert(self):
        """反选"""
        if not self.is_multi:
            raise NotImplementedError("只能对多项选框执行反选。")

        for i in self.options:
            i.click(by_js=True)

    def _select(self, text_value_index, para_type='text', deselect=False, timeout=None):
        """选定或取消选定下拉列表中子元素
        :param text_value_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param deselect: 是否取消选择
        :return: 是否选择成功
        """
        if not self.is_multi and isinstance(text_value_index, (list, tuple)):
            raise TypeError('单选下拉列表不能传入list和tuple')

        def do_select():
            try:
                if para_type == 'text':
                    if deselect:
                        self.select_ele.deselect_by_visible_text(text_value_index)
                    else:
                        self.select_ele.select_by_visible_text(text_value_index)
                elif para_type == 'value':
                    if deselect:
                        self.select_ele.deselect_by_value(text_value_index)
                    else:
                        self.select_ele.select_by_value(text_value_index)
                elif para_type == 'index':
                    if deselect:
                        self.select_ele.deselect_by_index(int(text_value_index))
                    else:
                        self.select_ele.select_by_index(int(text_value_index))
                else:
                    raise ValueError('para_type参数只能传入"text"、"value"或"index"。')

                return True

            except NoSuchElementException:
                return False

        if isinstance(text_value_index, (str, int)):
            t1 = perf_counter()
            ok = do_select()
            while not ok and perf_counter() - t1 < timeout:
                sleep(.2)
                ok = do_select()
            return ok

        elif isinstance(text_value_index, (list, tuple)):
            return self._select_multi(text_value_index, para_type, deselect)

        else:
            raise TypeError('只能传入str、int、list和tuple类型。')

    def _select_multi(self, text_value_index=None, para_type='text', deselect=False) -> bool:
        """选定或取消选定下拉列表中多个子元素
        :param text_value_index: 根据文本、值选或序号择选多项
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param deselect: 是否取消选择
        :return: 是否选择成功
        """
        if para_type not in ('text', 'value', 'index'):
            raise ValueError('para_type参数只能传入“text”、“value”或“index”')

        if not isinstance(text_value_index, (list, tuple)):
            raise TypeError('只能传入list或tuple类型。')

        success = True
        for i in text_value_index:
            if not isinstance(i, (int, str)):
                raise TypeError('列表只能由str或int组成')

            p = 'index' if isinstance(i, int) else para_type
            if not self._select(i, p, deselect):
                success = False

        return success


class ElementWaiter(object):
    """等待元素在dom中某种状态，如删除、显示、隐藏"""

    def __init__(self, page_or_ele, loc_or_ele, timeout=None):
        """等待元素在dom中某种状态，如删除、显示、隐藏
        :param page_or_ele: 页面或父元素
        :param loc_or_ele: 要等待的元素，可以是已有元素、定位符
        :param timeout: 超时时间，默认读取页面超时时间
        """
        if isinstance(page_or_ele, DriverElement):
            page = page_or_ele.page
            self.driver = page_or_ele.inner_ele
        else:
            page = page_or_ele
            self.driver = page_or_ele.driver

        if isinstance(loc_or_ele, DriverElement):
            self.target = loc_or_ele.inner_ele

        elif isinstance(loc_or_ele, WebElement):
            self.target = loc_or_ele

        elif isinstance(loc_or_ele, str):
            self.target = str_to_loc(loc_or_ele)

        elif isinstance(loc_or_ele, tuple):
            self.target = loc_or_ele

        else:
            raise TypeError('loc_or_ele参数只能是str、tuple、DriverElement 或 WebElement类型。')

        self.timeout = timeout if timeout is not None else page.timeout

    def delete(self):
        """等待元素从dom删除"""
        return self._wait_ele('del')

    def display(self):
        """等待元素从dom显示"""
        return self._wait_ele('display')

    def hidden(self):
        """等待元素从dom隐藏"""
        return self._wait_ele('hidden')

    def _wait_ele(self, mode):
        """执行等待
        :param mode: 等待模式
        :return: 是否等待成功
        """
        if isinstance(self.target, WebElement):
            end_time = time() + self.timeout
            while time() < end_time:
                if mode == 'del':
                    try:
                        self.target.is_enabled()
                    except Exception:
                        return True

                elif mode == 'display' and self.target.is_displayed():
                    return True

                elif mode == 'hidden' and not self.target.is_displayed():
                    return True

            return False

        else:
            try:
                if mode == 'del':
                    WebDriverWait(self.driver, self.timeout).until_not(ec.presence_of_element_located(self.target))

                elif mode == 'display':
                    WebDriverWait(self.driver, self.timeout).until(ec.visibility_of_element_located(self.target))

                elif mode == 'hidden':
                    WebDriverWait(self.driver, self.timeout).until_not(ec.visibility_of_element_located(self.target))

                return True

            except Exception:
                return False


class Scroll(object):
    """用于滚动的对象"""

    def __init__(self, page_or_ele):
        """
        :param page_or_ele: DriverPage或DriverElement
        """
        self.driver = page_or_ele
        if isinstance(page_or_ele, DriverElement):
            self.t1 = self.t2 = 'arguments[0]'
        else:
            self.t1 = 'window'
            self.t2 = 'document.documentElement'

    def to_top(self):
        """滚动到顶端，水平位置不变"""
        self.driver.run_script(f'{self.t1}.scrollTo({self.t2}.scrollLeft,0);')

    def to_bottom(self):
        """滚动到底端，水平位置不变"""
        self.driver.run_script(f'{self.t1}.scrollTo({self.t2}.scrollLeft,{self.t2}.scrollHeight);')

    def to_half(self):
        """滚动到垂直中间位置，水平位置不变"""
        self.driver.run_script(f'{self.t1}.scrollTo({self.t2}.scrollLeft,{self.t2}.scrollHeight/2);')

    def to_rightmost(self):
        """滚动到最右边，垂直位置不变"""
        self.driver.run_script(f'{self.t1}.scrollTo({self.t2}.scrollWidth,{self.t2}.scrollTop);')

    def to_leftmost(self):
        """滚动到最左边，垂直位置不变"""
        self.driver.run_script(f'{self.t1}.scrollTo(0,{self.t2}.scrollTop);')

    def to_location(self, x, y):
        """滚动到指定位置
        :param x: 水平距离
        :param y: 垂直距离
        :return: None
        """
        self.driver.run_script(f'{self.t1}.scrollTo({x},{y});')

    def up(self, pixel=300):
        """向上滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        pixel = -pixel
        self.driver.run_script(f'{self.t1}.scrollBy(0,{pixel});')

    def down(self, pixel=300):
        """向下滚动若干像素，水平位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        self.driver.run_script(f'{self.t1}.scrollBy(0,{pixel});')

    def left(self, pixel=300):
        """向左滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        pixel = -pixel
        self.driver.run_script(f'{self.t1}.scrollBy({pixel},0);')

    def right(self, pixel=300):
        """向右滚动若干像素，垂直位置不变
        :param pixel: 滚动的像素
        :return: None
        """
        self.driver.run_script(f'{self.t1}.scrollBy({pixel},0);')


def _exchange_arguments(index, filter_loc):
    # 此方法用于兼容MixPage参数顺序相反的情况
    if isinstance(index, str) and isinstance(filter_loc, int):
        index, filter_loc = filter_loc, index
    elif isinstance(index, int) and filter_loc == 1:
        filter_loc = ''
    elif isinstance(filter_loc, str) and index == '':
        index = 1
    return index, filter_loc
