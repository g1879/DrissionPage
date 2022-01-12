# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_element.py
"""
from os import sep
from pathlib import Path
from time import time, perf_counter
from typing import Union, List, Any, Tuple

from selenium.common.exceptions import TimeoutException, JavascriptException, InvalidElementStateException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from .base import DrissionElement, BaseElement
from .common import str_to_loc, get_usable_path, format_html, get_ele_txt, get_loc
from .session_element import make_session_ele


class DriverElement(DrissionElement):
    """driver模式的元素对象，包装了一个WebElement对象，并封装了常用功能"""

    def __init__(self, ele: WebElement, page=None):
        """初始化对象                          \n
        :param ele: 被包装的WebElement元素
        :param page: 元素所在页面
        """
        super().__init__(ele, page)
        self._select = None

    def __repr__(self) -> str:
        attrs = [f"{attr}='{self.attrs[attr]}'" for attr in self.attrs]
        return f'<DriverElement {self.tag} {" ".join(attrs)}>'

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 timeout: float = None):
        """在内部查找元素                                             \n
        例：ele2 = ele1('@id=ele_id')                               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: DriverElement对象或属性、文本
        """
        return self.ele(loc_or_str, timeout)

    # -----------------共有属性和方法-------------------
    @property
    def tag(self) -> str:
        """返回元素类型"""
        return self._inner_ele.tag_name.lower()

    @property
    def html(self) -> str:
        """返回元素outerHTML文本"""
        return self.inner_ele.get_attribute('outerHTML')

    @property
    def inner_html(self) -> str:
        """返回元素innerHTML文本"""
        return self.inner_ele.get_attribute('innerHTML')

    @property
    def attrs(self) -> dict:
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
    def text(self) -> str:
        """返回元素内所有文本"""
        return get_ele_txt(make_session_ele(self.html))

    @property
    def raw_text(self) -> str:
        """返回未格式化处理的元素内文本"""
        return self.inner_ele.get_attribute('innerText')

    def attr(self, attr: str) -> str:
        """获取attribute属性值            \n
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

    def ele(self,
            loc_or_str: Union[Tuple[str, str], str],
            timeout: float = None):
        """返回当前元素下级符合条件的第一个元素、属性或节点文本                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: DriverElement对象或属性、文本
        """
        return self._ele(loc_or_str, timeout)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与元素所在页面等待时间一致
        :return: DriverElement对象或属性、文本组成的列表
        """
        return self._ele(loc_or_str, timeout=timeout, single=False)

    def s_ele(self, loc_or_str: Union[Tuple[str, str], str] = None):
        """查找第一个符合条件的元素以SessionElement形式返回，处理复杂页面时效率很高        \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :return: SessionElement对象或属性、文本
        """
        return make_session_ele(self, loc_or_str)

    def s_eles(self, loc_or_str: Union[Tuple[str, str], str] = None):
        """查找所有符合条件的元素以SessionElement列表形式返回                         \n
        :param loc_or_str: 定位符
        :return: SessionElement或属性、文本组成的列表
        """
        return make_session_ele(self, loc_or_str, single=False)

    def _ele(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None,
             single: bool = True):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个                                      \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param single: True则返回第一个，False则返回全部
        :return: DriverElement对象
        """
        return make_driver_ele(self, loc_or_str, single, timeout)

    def _get_ele_path(self, mode) -> str:
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
    def size(self) -> dict:
        """返回元素宽和高"""
        return self.inner_ele.size

    @property
    def location(self) -> dict:
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
    def pseudo_before(self) -> str:
        """返回当前元素的::before伪元素内容"""
        return self.style('content', 'before')

    @property
    def pseudo_after(self) -> str:
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

    def left(self, index: int = 1, filter_loc: Union[tuple, str] = '') -> 'DriverElement':
        """获取网页上显示在当前元素左边的某个元素，可设置选取条件，可指定结果中第几个               \n
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('left', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def right(self, index: int = 1, filter_loc: Union[tuple, str] = '') -> 'DriverElement':
        """获取网页上显示在当前元素右边的某个元素，可设置选取条件，可指定结果中第几个               \n
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('right', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def above(self, index: int = 1, filter_loc: Union[tuple, str] = '') -> 'DriverElement':
        """获取网页上显示在当前元素上边的某个元素，可设置选取条件，可指定结果中第几个               \n
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('left', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def below(self, index: int = 1, filter_loc: Union[tuple, str] = '') -> 'DriverElement':
        """获取网页上显示在当前元素下边的某个元素，可设置选取条件，可指定结果中第几个               \n
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('left', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def near(self, index: int = 1, filter_loc: Union[tuple, str] = '') -> 'DriverElement':
        """获取网页上显示在当前元素最近的某个元素，可设置选取条件，可指定结果中第几个               \n
        :param index: 获取第几个
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        eles = self._get_relative_eles('near', filter_loc)
        return eles[index - 1] if index <= len(eles) else None

    def lefts(self, filter_loc: Union[tuple, str] = '') -> List['DriverElement']:
        """获取网页上显示在当前元素左边的所有元素，可设置选取条件，从近到远排列                    \n
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('left', filter_loc)

    def rights(self, filter_loc: Union[tuple, str] = '') -> List['DriverElement']:
        """获取网页上显示在当前元素右边的所有元，可设置选取条件，从近到远排列                    \n
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('right', filter_loc)

    def aboves(self, filter_loc: Union[tuple, str] = '') -> List['DriverElement']:
        """获取网页上显示在当前元素上边的所有元素，可设置选取条件，从近到远排列                    \n
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('left', filter_loc)

    def belows(self, filter_loc: Union[tuple, str] = '') -> List['DriverElement']:
        """获取网页上显示在当前元素下边的所有元素，可设置选取条件，从近到远排列                    \n
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('left', filter_loc)

    def nears(self, filter_loc: Union[tuple, str] = '') -> List['DriverElement']:
        """获取网页上显示在当前元素附近元素，可设置选取条件，从近到远排列                    \n
        :param filter_loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象组成的列表
        """
        return self._get_relative_eles('near', filter_loc)

    def wait_ele(self,
                 loc_or_ele: Union[str, tuple, DrissionElement, WebElement],
                 mode: str,
                 timeout: float = None) -> bool:
        """等待子元素从dom删除、显示、隐藏                             \n
        :param loc_or_ele: 可以是元素、查询字符串、loc元组
        :param mode: 等待方式，可选：'del', 'display', 'hidden'
        :param timeout: 等待超时时间
        :return: 等待是否成功
        """
        return _wait_ele(self, loc_or_ele, mode, timeout)

    def style(self, style: str, pseudo_ele: str = '') -> str:
        """返回元素样式属性值，可获取伪元素属性值                \n
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称（如有）
        :return: 样式属性的值
        """
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"' if pseudo_ele.startswith(':') else f', "::{pseudo_ele}"'
        r = self.run_script(f'return window.getComputedStyle(arguments[0]{pseudo_ele}).getPropertyValue("{style}");')

        return None if r == 'none' else r

    def click(self, by_js: bool = None, timeout: float = None) -> bool:
        """点击元素                                                                      \n
        尝试点击直到超时，若都失败就改用js点击                                                \n
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

    def click_at(self,
                 x: Union[int, str] = None,
                 y: Union[int, str] = None,
                 by_js: bool = False) -> None:
        """带偏移量点击本元素，相对于左上角坐标。不传入x或y值时点击元素中点    \n
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

    def r_click(self) -> None:
        """右键单击"""
        from selenium.webdriver import ActionChains
        ActionChains(self.page.driver).context_click(self.inner_ele).perform()

    def r_click_at(self, x: Union[int, str] = None, y: Union[int, str] = None) -> None:
        """带偏移量右键单击本元素，相对于左上角坐标。不传入x或y值时点击元素中点    \n
        :param x: 相对元素左上角坐标的x轴偏移量
        :param y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        x = int(x) if x is not None else self.size['width'] // 2
        y = int(y) if y is not None else self.size['height'] // 2
        from selenium.webdriver import ActionChains
        ActionChains(self.page.driver).move_to_element_with_offset(self.inner_ele, x, y).context_click().perform()

    def input(self,
              vals: Union[str, tuple],
              clear: bool = True,
              insure: bool = True,
              timeout: float = None) -> bool:
        """输入文本或组合键，也可用于输入文件路径到input元素（文件间用\n间隔）                          \n
        :param vals: 文本值或按键组合
        :param clear: 输入前是否清空文本框
        :param insure: 确保输入正确，解决文本框有时输入失效的问题，不能用于输入组合键
        :param timeout: 尝试输入的超时时间，不指定则使用父页面的超时时间，只在insure_input为True时生效
        :return: bool
        """
        if not insure or self.tag != 'input' or self.prop('type') != 'text':  # 普通输入
            if clear:
                self.inner_ele.clear()

            self.inner_ele.send_keys(*vals)
            return True

        else:  # 确保输入正确
            if not isinstance(vals, str):
                raise TypeError('insure_input参数生效时vals只能接收str数据。')
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

    def run_script(self, script: str, *args) -> Any:
        """执行js代码，代码中用arguments[0]表示自己    \n
        :param script: js文本
        :param args: 传入的参数
        :return: js执行结果
        """
        return self.inner_ele.parent.execute_script(script, self.inner_ele, *args)

    def scroll_to(self, mode: str = 'bottom', pixel: int = 300) -> None:
        """按参数指示方式滚动元素                                                                                    \n
        :param mode: 可选滚动方向：'top', 'bottom', 'half', 'rightmost', 'leftmost', 'up', 'down', 'left', 'right'
        :param pixel: 滚动的像素
        :return: None
        """
        if mode == 'top':
            self.run_script("arguments[0].scrollTo(arguments[0].scrollLeft,0);")

        elif mode == 'bottom':
            self.run_script("arguments[0].scrollTo(arguments[0].scrollLeft,arguments[0].scrollHeight);")

        elif mode == 'half':
            self.run_script("arguments[0].scrollTo(arguments[0].scrollLeft,arguments[0].scrollHeight/2);")

        elif mode == 'rightmost':
            self.run_script("arguments[0].scrollTo(arguments[0].scrollWidth,arguments[0].scrollTop);")

        elif mode == 'leftmost':
            self.run_script("arguments[0].scrollTo(0,arguments[0].scrollTop);")

        elif mode == 'up':
            pixel = pixel if pixel >= 0 else -pixel
            self.run_script(f"arguments[0].scrollBy(0,{pixel});")

        elif mode == 'down':
            self.run_script(f"arguments[0].scrollBy(0,{pixel});")

        elif mode == 'left':
            pixel = pixel if pixel >= 0 else -pixel
            self.run_script(f"arguments[0].scrollBy({pixel},0);")

        elif mode == 'right':
            self.run_script(f"arguments[0].scrollBy({pixel},0);")

        else:
            raise ValueError("mode参数只能是'top', 'bottom', 'half', 'rightmost', "
                             "'leftmost', 'up', 'down', 'left', 'right'。")

    def submit(self) -> Union[bool, None]:
        """提交表单"""
        try:
            self.inner_ele.submit()
            return True
        except Exception:
            pass

    def clear(self, insure_clear: bool = True) -> Union[None, bool]:
        """清空元素文本                                    \n
        :param insure_clear: 是否确保清空
        :return: 是否清空成功，不能清空的元素返回None
        """
        if insure_clear:
            return self.input('')

        else:
            try:
                self.inner_ele.clear()
                return True
            except InvalidElementStateException:
                return None

    def is_selected(self) -> bool:
        """是否选中"""
        return self.inner_ele.is_selected()

    def is_enabled(self) -> bool:
        """是否可用"""
        return self.inner_ele.is_enabled()

    def is_displayed(self) -> bool:
        """是否可见"""
        return self.inner_ele.is_displayed()

    def is_valid(self) -> bool:
        """用于判断元素是否还在DOM内，应对页面跳转元素不能用的情况"""
        try:
            self.is_enabled()
            return True
        except Exception:
            return False

    def screenshot(self, path: str, filename: str = None) -> str:
        """对元素进行截图                                          \n
        :param path: 保存路径
        :param filename: 图片文件名，不传入时以元素tag name命名
        :return: 图片完整路径
        """
        name = filename or self.tag
        path = Path(path).absolute()
        path.mkdir(parents=True, exist_ok=True)
        if not name.lower().endswith('.png'):
            name = f'{name}.png'

        # 等待元素加载完成
        if self.tag == 'img':
            js = ('return arguments[0].complete && typeof arguments[0].naturalWidth != "undefined" '
                  '&& arguments[0].naturalWidth > 0')
            while not self.run_script(js):
                pass

        img_path = str(get_usable_path(f'{path}{sep}{name}'))
        self.inner_ele.screenshot(img_path)

        return img_path

    def prop(self, prop: str) -> str:
        """获取property属性值            \n
        :param prop: 属性名
        :return: 属性值文本
        """
        return format_html(self.inner_ele.get_property(prop))

    def set_prop(self, prop: str, value: str) -> bool:
        """设置元素property属性          \n
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

    def set_attr(self, attr: str, value: str) -> bool:
        """设置元素attribute属性          \n
        :param attr: 属性名
        :param value: 属性值
        :return: 是否设置成功
        """
        try:
            self.run_script(f"arguments[0].setAttribute(arguments[1], arguments[2]);", attr, value)
            return True
        except Exception:
            return False

    def remove_attr(self, attr: str) -> bool:
        """删除元素attribute属性          \n
        :param attr: 属性名
        :return: 是否删除成功
        """
        try:
            self.run_script(f'arguments[0].removeAttribute("{attr}");')
            return True
        except Exception:
            return False

    def drag(self, x: int, y: int, speed: int = 40, shake: bool = True) -> bool:
        """拖拽当前元素到相对位置                   \n
        :param x: x变化值
        :param y: y变化值
        :param speed: 拖动的速度，传入0即瞬间到达
        :param shake: 是否随机抖动
        :return: 是否推拽成功
        """
        x += self.location['x'] + self.size['width'] // 2
        y += self.location['y'] + self.size['height'] // 2
        return self.drag_to((x, y), speed, shake)

    def drag_to(self,
                ele_or_loc: Union[tuple, WebElement, DrissionElement],
                speed: int = 40,
                shake: bool = True) -> bool:
        """拖拽当前元素，目标为另一个元素或坐标元组                     \n
        :param ele_or_loc: 另一个元素或坐标元组，坐标为元素中点的坐标
        :param speed: 拖动的速度，传入0即瞬间到达
        :param shake: 是否随机抖动
        :return: 是否拖拽成功
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
        loc1 = self.location

        # 逐个访问要经过的点
        for x, y in points:
            if shake:
                x += randint(-3, 4)
                y += randint(-3, 4)
            actions.move_by_offset(x - current_x, y - current_y)
            current_x, current_y = x, y
        actions.release().perform()

        return False if self.location == loc1 else True

    def hover(self, x: int = None, y: int = None) -> None:
        """鼠标悬停，可接受偏移量，偏移量相对于元素左上角坐标。不传入x或y值时悬停在元素中点    \n
        :param x: 相对元素左上角坐标的x轴偏移量
        :param y: 相对元素左上角坐标的y轴偏移量
        :return: None
        """
        from selenium.webdriver import ActionChains
        x = int(x) if x is not None else self.size['width'] // 2
        y = int(y) if y is not None else self.size['height'] // 2
        ActionChains(self.page.driver).move_to_element_with_offset(self.inner_ele, x, y).perform()

    def _get_relative_eles(self,
                           mode: str,
                           loc: Union[tuple, str] = '') -> Union[List['DriverElement'], 'DriverElement']:
        """获取网页上相对于当前元素周围的某个元素，可设置选取条件                          \n
        :param mode: 可选：'left', 'right', 'above', 'below', 'near'
        :param loc: 筛选条件，可用selenium的(By, str)，也可用本库定位语法
        :return: DriverElement对象
        """
        try:
            from selenium.webdriver.support.relative_locator import RelativeBy
        except ImportError:
            raise ImportError('该方法只支持selenium4及以上版本。')

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


def make_driver_ele(page_or_ele,
                    loc: Union[str, Tuple[str, str]],
                    single: bool = True,
                    timeout: float = None) -> Union[DriverElement, List[DriverElement], str, None]:
    """执行driver模式元素的查找                               \n
    页面查找元素及元素查找下级元素皆使用此方法                   \n
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

    def __init__(self, page, xpath: str = None, single: bool = False, timeout: float = 10):
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

    def __call__(self, ele_or_driver: Union[WebDriver, WebElement]) \
            -> Union[str, DriverElement, None, List[str or DriverElement]]:

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

        if isinstance(ele_or_driver, WebDriver):
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
        """初始化                      \n
        :param ele: select 元素对象
        """
        if ele.tag != 'select':
            raise TypeError(f"select方法只能在<select>元素使用，现在是：{ele.tag}。")

        from selenium.webdriver.support.select import Select
        self.inner_ele = ele
        self.select_ele = Select(ele.inner_ele)

    def __call__(self,
                 text_value_index: Union[str, int, list, tuple] = None,
                 para_type: str = 'text',
                 deselect: bool = False) -> bool:
        """选定或取消选定下拉列表中子元素                                                             \n
        :param text_value_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param deselect: 是否取消选择
        :return: 是否选择成功
        """
        return self.select(text_value_index, para_type, deselect)

    @property
    def is_multi(self) -> bool:
        """返回是否多选表单"""
        return self.select_ele.is_multiple

    @property
    def options(self) -> List[DriverElement]:
        """返回所有选项元素组成的列表"""
        return self.inner_ele.eles('tag:option')

    @property
    def selected_option(self) -> Union[DriverElement, None]:
        """返回第一个被选中的option元素        \n
        :return: DriverElement对象或None
        """
        ele = self.inner_ele.run_script('return arguments[0].options[arguments[0].selectedIndex];')
        return None if ele is None else DriverElement(ele, self.inner_ele.page)

    @property
    def selected_options(self) -> List[DriverElement]:
        """返回所有被选中的option元素列表        \n
        :return: DriverElement对象组成的列表
        """
        return [x for x in self.options if x.is_selected()]

    def clear(self) -> None:
        """清除所有已选项"""
        self.select_ele.deselect_all()

    def select(self,
               text_value_index: Union[str, int, list, tuple] = None,
               para_type: str = 'text',
               deselect: bool = False) -> bool:
        """选定或取消选定下拉列表中子元素                                                             \n
        :param text_value_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param deselect: 是否取消选择
        :return: 是否选择成功
        """
        if not self.is_multi and isinstance(text_value_index, (list, tuple)):
            raise TypeError('单选下拉列表不能传入list和tuple')

        if isinstance(text_value_index, (str, int)):
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

            except Exception:
                return False

        elif isinstance(text_value_index, (list, tuple)):
            self.select_multi(text_value_index, para_type, deselect)

        else:
            raise TypeError('只能传入str、int、list和tuple类型。')

    def select_multi(self,
                     text_value_index: Union[list, tuple] = None,
                     para_type: str = 'text',
                     deselect: bool = False) -> Union[bool, list]:
        """选定或取消选定下拉列表中多个子元素                                                             \n
        :param text_value_index: 根据文本、值选或序号择选多项
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :param deselect: 是否取消选择
        :return: 是否选择成功
        """
        if para_type not in ('text', 'value', 'index'):
            raise ValueError('para_type参数只能传入“text”、“value”或“index”')

        if isinstance(text_value_index, (list, tuple)):
            fail_list = []
            for i in text_value_index:
                if not isinstance(i, (int, str)):
                    raise TypeError('列表只能由str或int组成')

                if not self.select(i, para_type, deselect):
                    fail_list.append(i)

            return fail_list or True

        else:
            raise TypeError('只能传入list或tuple类型。')

    def deselect(self,
                 text_value_index: Union[str, int, list, tuple] = None,
                 para_type: str = 'text') -> bool:
        """取消选定下拉列表中子元素                                                             \n
        :param text_value_index: 根据文本、值选或序号择选项，若允许多选，传入list或tuple可多选
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :return: 是否选择成功
        """
        return self.select(text_value_index, para_type, True)

    def deselect_multi(self,
                       text_value_index: Union[list, tuple] = None,
                       para_type: str = 'text') -> Union[bool, list]:
        """取消选定下拉列表中多个子元素                                                             \n
        :param text_value_index: 根据文本、值选或序号取消择选多项
        :param para_type: 参数类型，可选 'text'、'value'、'index'
        :return: 是否选择成功
        """
        return self.select_multi(text_value_index, para_type, True)

    def invert(self) -> None:
        """反选"""
        if not self.is_multi:
            raise NotImplementedError("只能对多项选框执行反选。")

        for i in self.options:
            i.click()


def _wait_ele(page_or_ele,
              loc_or_ele: Union[str, tuple, DriverElement, WebElement],
              mode: str,
              timeout: float = None) -> bool:
    """等待元素从dom删除、显示、隐藏                             \n
    :param page_or_ele: 要等待子元素的页面或元素
    :param loc_or_ele: 可以是元素、查询字符串、loc元组
    :param mode: 等待方式，可选：'del', 'display', 'hidden'
    :param timeout: 等待超时时间
    :return: 等待是否成功
    """
    if mode.lower() not in ('del', 'display', 'hidden'):
        raise ValueError('mode参数只能是"del"、"display"或"hidden"。')

    if isinstance(page_or_ele, BaseElement):
        page = page_or_ele.page
        ele_or_driver = page_or_ele.inner_ele
    else:
        page = page_or_ele
        ele_or_driver = page_or_ele.driver

    timeout = timeout or page.timeout
    is_ele = False

    if isinstance(loc_or_ele, DriverElement):
        loc_or_ele = loc_or_ele.inner_ele
        is_ele = True

    elif isinstance(loc_or_ele, WebElement):
        is_ele = True

    elif isinstance(loc_or_ele, str):
        loc_or_ele = str_to_loc(loc_or_ele)

    elif isinstance(loc_or_ele, tuple):
        pass

    else:
        raise TypeError('loc_or_ele参数只能是str、tuple、DriverElement 或 WebElement类型')

    # 当传入参数是元素对象时
    if is_ele:
        end_time = time() + timeout

        while time() < end_time:
            if mode == 'del':
                try:
                    loc_or_ele.is_enabled()
                except Exception:
                    return True

            elif mode == 'display' and loc_or_ele.is_displayed():
                return True

            elif mode == 'hidden' and not loc_or_ele.is_displayed():
                return True

        return False

    # 当传入参数是控制字符串或元组时
    else:
        try:
            if mode == 'del':
                WebDriverWait(ele_or_driver, timeout).until_not(ec.presence_of_element_located(loc_or_ele))

            elif mode == 'display':
                WebDriverWait(ele_or_driver, timeout).until(ec.visibility_of_element_located(loc_or_ele))

            elif mode == 'hidden':
                WebDriverWait(ele_or_driver, timeout).until_not(ec.visibility_of_element_located(loc_or_ele))

            return True

        except Exception:
            return False
