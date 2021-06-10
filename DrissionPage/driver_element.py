# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_element.py
"""
import re
from pathlib import Path
from time import sleep
from typing import Union, List, Any, Tuple

from selenium.common.exceptions import TimeoutException, JavascriptException, InvalidElementStateException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from .common import DrissionElement, str_to_loc, get_available_file_name, translate_loc, format_html


class DriverElement(DrissionElement):
    """driver模式的元素对象，包装了一个WebElement对象，并封装了常用功能"""

    def __init__(self, ele: WebElement, page=None):
        super().__init__(ele, page)
        self._select = None

    def __repr__(self):
        attrs = [f"{attr}='{self.attrs[attr]}'" for attr in self.attrs]
        return f'<DriverElement {self.tag} {" ".join(attrs)}>'

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str],
                 mode: str = 'single',
                 timeout: float = None):
        """实现查找元素的简化写法                                     \n
        例：ele2 = ele1('@id=ele_id')                               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param mode: 'single' 或 'all'，对应查找一个或全部
        :param timeout: 超时时间
        :return: DriverElement对象
        """
        return self.ele(loc_or_str, mode, timeout)

    # -----------------共有属性-------------------
    @property
    def html(self) -> str:
        """返回元素outerHTML文本"""
        return self.attr('outerHTML')

    @property
    def inner_html(self) -> str:
        """返回元素innerHTML文本"""
        return self.attr('innerHTML')

    @property
    def tag(self) -> str:
        """返回元素类型"""
        return self._inner_ele.tag_name.lower()

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
        # return format_html(self.inner_ele.get_attribute('innerText'), False)
        re_str = self.inner_ele.get_attribute('innerText')
        re_str = re.sub(r'\n{2,}', '\n', re_str)
        re_str = re.sub(r' {2,}', ' ', re_str)

        return format_html(re_str.strip('\n '), False)

    @property
    def raw_text(self) -> str:
        """返回未格式化处理的元素内文本"""
        return self.inner_ele.get_attribute('innerText')

    @property
    def link(self) -> str:
        """返回href或src绝对url"""
        return self.attr('href') or self.attr('src')

    @property
    def css_path(self) -> str:
        """返回当前元素的css路径"""
        return self._get_ele_path('css')

    @property
    def xpath(self) -> str:
        return self._get_ele_path('xpath')

    @property
    def parent(self):
        """返回父级元素"""
        return self.parents()

    @property
    def next(self):
        """返回后一个兄弟元素"""
        return self._get_brother(1, 'ele', 'next')

    @property
    def prev(self):
        """返回前一个兄弟元素"""
        return self._get_brother(1, 'ele', 'prev')

    @property
    def comments(self) -> list:
        """返回元素注释文本组成的列表"""
        return self.eles('xpath:.//comment()')

    # -----------------driver独占属性-------------------
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
    def before(self) -> str:
        """返回当前元素的::before伪元素内容"""
        return self.get_style_property('content', 'before')

    @property
    def after(self) -> str:
        """返回当前元素的::after伪元素内容"""
        return self.get_style_property('content', 'after')

    @property
    def select(self):
        """返回专门处理下拉列表的Select类，非下拉列表元素返回False"""
        if self._select is None:
            if self.tag != 'select':
                self._select = False
            else:
                self._select = Select(self)

        return self._select

    # -----------------共有函数-------------------

    def texts(self, text_node_only: bool = False) -> list:
        """返回元素内所有直接子节点的文本，包括元素和文本节点   \n
        :param text_node_only: 是否只返回文本节点
        :return: 文本列表
        """
        if text_node_only:
            texts = self.eles('xpath:/text()')
        else:
            texts = [x if isinstance(x, str) else x.text for x in self.eles('xpath:./text() | *')]

        return [x.strip(' ') for x in texts if x and x.replace('\n', '').replace('\t', '').replace(' ', '') != '']

    def parents(self, num: int = 1):
        """返回上面第num级父元素              \n
        :param num: 第几级父元素
        :return: DriverElement对象
        """
        loc = 'xpath', f'.{"/.." * num}'
        return self.ele(loc, timeout=0)

    def nexts(self, num: int = 1, mode: str = 'ele'):
        """返回后面第num个兄弟元素或节点文本                                   \n
        :param num: 后面第几个兄弟元素或节点
        :param mode: 'ele', 'node' 或 'text'，匹配元素、节点、或文本节点
        :return: DriverElement对象或字符串
        """
        return self._get_brother(num, mode, 'next')

    def prevs(self, num: int = 1, mode: str = 'ele'):
        """返回前面第num个兄弟元素或节点文本                                   \n
        :param num: 前面第几个兄弟元素或节点
        :param mode: 'ele', 'node' 或 'text'，匹配元素、节点、或文本节点
        :return: DriverElement对象或字符串
        """
        return self._get_brother(num, mode, 'prev')

    def attr(self, attr: str) -> str:
        """获取属性值            \n
        :param attr: 属性名
        :return: 属性值文本
        """
        # attr = 'innerText' if attr == 'text' else attr
        if attr in ('text', 'innerText'):
            return self.text

        return format_html(self.inner_ele.get_attribute(attr))

    def ele(self,
            loc_or_str: Union[Tuple[str, str], str],
            mode: str = None,
            timeout: float = None):
        """返回当前元素下级符合条件的子元素、属性或节点文本，默认返回第一个                                      \n
        示例：                                                                                            \n
        - 用loc元组查找：                                                                                 \n
            ele.ele((By.CLASS_NAME, 'ele_class'))       - 返回第一个class为ele_class的子元素               \n
        - 用查询字符串查找：                                                                               \n
            查找方式：属性、tag name和属性、文本、xpath、css selector、id、class                              \n
            @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串            \n
            ele.ele('.ele_class')                       - 返回第一个 class 为 ele_class 的子元素            \n
            ele.ele('.:ele_class')                      - 返回第一个 class 中含有 ele_class 的子元素         \n
            ele.ele('#ele_id')                          - 返回第一个 id 为 ele_id 的子元素                   \n
            ele.ele('#:ele_id')                         - 返回第一个 id 中含有 ele_id 的子元素               \n
            ele.ele('@class:ele_class')                 - 返回第一个class含有ele_class的子元素               \n
            ele.ele('@name=ele_name')                   - 返回第一个name等于ele_name的子元素                 \n
            ele.ele('@placeholder')                     - 返回第一个带placeholder属性的子元素                \n
            ele.ele('tag:p')                            - 返回第一个<p>子元素                               \n
            ele.ele('tag:div@class:ele_class')          - 返回第一个class含有ele_class的div子元素            \n
            ele.ele('tag:div@class=ele_class')          - 返回第一个class等于ele_class的div子元素            \n
            ele.ele('tag:div@text():some_text')         - 返回第一个文本含有some_text的div子元素              \n
            ele.ele('tag:div@text()=some_text')         - 返回第一个文本等于some_text的div子元素              \n
            ele.ele('text:some_text')                   - 返回第一个文本含有some_text的子元素                 \n
            ele.ele('some_text')                        - 返回第一个文本含有some_text的子元素（等价于上一行）   \n
            ele.ele('text=some_text')                   - 返回第一个文本等于some_text的子元素                 \n
            ele.ele('xpath://div[@class="ele_class"]')  - 返回第一个符合xpath的子元素                         \n
            ele.ele('css:div.ele_class')                - 返回第一个符合css selector的子元素                  \n
        - 查询字符串还有最精简模式，用x代替xpath、c代替css、t代替tag、tx代替text：                                \n
            ele.ele('x://div[@class="ele_class"]')      - 等同于 ele.ele('xpath://div[@class="ele_class"]') \n
            ele.ele('c:div.ele_class')                  - 等同于 ele.ele('css:div.ele_class')               \n
            ele.ele('t:div')                            - 等同于 ele.ele('tag:div')                         \n
            ele.ele('t:div@tx()=some_text')             - 等同于 ele.ele('tag:div@text()=some_text')        \n
            ele.ele('tx:some_text')                     - 等同于 ele.ele('text:some_text')                  \n
            ele.ele('tx=some_text')                     - 等同于 ele.ele('text=some_text')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param mode: 'single' 或 'all'，对应查找一个或全部
        :param timeout: 查找元素超时时间
        :return: DriverElement对象
        """
        if isinstance(loc_or_str, (str, tuple)):
            if isinstance(loc_or_str, str):
                loc_or_str = str_to_loc(loc_or_str)
            else:
                if len(loc_or_str) != 2:
                    raise ValueError("Len of loc_or_str must be 2 when it's a tuple.")

                loc_or_str = translate_loc(loc_or_str)

        else:
            raise ValueError('Argument loc_or_str can only be tuple or str.')

        loc_str = loc_or_str[1]

        if loc_or_str[0] == 'xpath' and loc_or_str[1].lstrip().startswith('/'):
            loc_str = f'.{loc_str}'

        if loc_or_str[0] == 'css selector' and loc_or_str[1].lstrip().startswith('>'):
            loc_str = f'{self.css_path}{loc_or_str[1]}'

        loc_or_str = loc_or_str[0], loc_str

        return execute_driver_find(self, loc_or_str, mode, timeout)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None):
        """返回当前元素下级所有符合条件的子元素、属性或节点文本                                                   \n
        示例：                                                                                              \n
        - 用loc元组查找：                                                                                    \n
            ele.eles((By.CLASS_NAME, 'ele_class'))       - 返回所有class为ele_class的子元素                   \n
        - 用查询字符串查找：                                                                                  \n
            查找方式：属性、tag name和属性、文本、xpath、css selector、id、class                                \n
            @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串              \n
            ele.eles('.ele_class')                       - 返回所有 class 为 ele_class 的子元素               \n
            ele.eles('.:ele_class')                      - 返回所有 class 中含有 ele_class 的子元素            \n
            ele.eles('#ele_id')                          - 返回所有 id 为 ele_id 的子元素                      \n
            ele.eles('#:ele_id')                         - 返回所有 id 中含有 ele_id 的子元素                  \n
            ele.eles('@class:ele_class')                 - 返回所有class含有ele_class的子元素                  \n
            ele.eles('@name=ele_name')                   - 返回所有name等于ele_name的子元素                    \n
            ele.eles('@placeholder')                     - 返回所有带placeholder属性的子元素                   \n
            ele.eles('tag:p')                            - 返回所有<p>子元素                                  \n
            ele.eles('tag:div@class:ele_class')          - 返回所有class含有ele_class的div子元素               \n
            ele.eles('tag:div@class=ele_class')          - 返回所有class等于ele_class的div子元素               \n
            ele.eles('tag:div@text():some_text')         - 返回所有文本含有some_text的div子元素                 \n
            ele.eles('tag:div@text()=some_text')         - 返回所有文本等于some_text的div子元素                 \n
            ele.eles('text:some_text')                   - 返回所有文本含有some_text的子元素                    \n
            ele.eles('some_text')                        - 返回所有文本含有some_text的子元素（等价于上一行）      \n
            ele.eles('text=some_text')                   - 返回所有文本等于some_text的子元素                    \n
            ele.eles('xpath://div[@class="ele_class"]')  - 返回所有符合xpath的子元素                            \n
            ele.eles('css:div.ele_class')                - 返回所有符合css selector的子元素                     \n
        - 查询字符串还有最精简模式，用x代替xpath、c代替css、t代替tag、tx代替text：                                  \n
            ele.eles('x://div[@class="ele_class"]')      - 等同于 ele.eles('xpath://div[@class="ele_class"]') \n
            ele.eles('c:div.ele_class')                  - 等同于 ele.eles('css:div.ele_class')               \n
            ele.eles('t:div')                            - 等同于 ele.eles('tag:div')                         \n
            ele.eles('t:div@tx()=some_text')             - 等同于 ele.eles('tag:div@text()=some_text')        \n
            ele.eles('tx:some_text')                     - 等同于 ele.eles('text:some_text')                  \n
            ele.eles('tx=some_text')                     - 等同于 ele.eles('text=some_text')
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :return: DriverElement对象组成的列表
        """
        return self.ele(loc_or_str, mode='all', timeout=timeout)

    # -----------------driver独占函数-------------------

    def get_style_property(self, style: str, pseudo_ele: str = '') -> str:
        """返回元素样式属性值
        :param style: 样式属性名称
        :param pseudo_ele: 伪元素名称
        :return: 样式属性的值
        """
        if pseudo_ele:
            pseudo_ele = f', "{pseudo_ele}"' if pseudo_ele.startswith(':') else f', "::{pseudo_ele}"'
        r = self.run_script(f'return window.getComputedStyle(arguments[0]{pseudo_ele}).getPropertyValue("{style}");')

        return None if r == 'none' else r

    def click(self, by_js: bool = None) -> bool:
        """点击元素                                                                      \n
        尝试点击3次，若都失败就改用js点击                                                  \n
        :param by_js: 是否用js点击，为True时直接用js点击，为False时重试失败也不会改用js
        :return: 是否点击成功
        """
        if not by_js:
            for _ in range(3):
                try:
                    self.inner_ele.click()
                    return True
                except:
                    sleep(0.2)

        # 若点击失败，用js方式点击
        if by_js is not False:
            self.run_script('arguments[0].click()')
            return True

        return False

    def click_at(self, x: Union[int, str] = None, y: Union[int, str] = None, by_js=False) -> None:
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

    def input(self, value: Union[str, tuple], clear: bool = True) -> bool:
        """输入文本或组合键                          \n
        :param value: 文本值或按键组合
        :param clear: 输入前是否清空文本框
        :return: 是否输入成功
        """
        try:
            if clear:
                self.clear()

            self.inner_ele.send_keys(*value)
            return True

        except Exception as e:
            print(e)
            return False

    def run_script(self, script: str, *args) -> Any:
        """执行js代码，传入自己为第一个参数  \n
        :param script: js文本
        :param args: 传入的参数
        :return: js执行结果
        """
        return self.inner_ele.parent.execute_script(script, self.inner_ele, *args)

    def submit(self) -> None:
        """提交表单"""
        self.inner_ele.submit()

    def clear(self) -> None:
        """清空元素文本"""
        self.run_script("arguments[0].value=''")
        # self.inner_ele.clear()

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
        except:
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
        name = f'{name}.png' if not name.endswith('.png') else name
        name = get_available_file_name(str(path), name)

        # 等待元素加载完成
        if self.tag == 'img':
            js = ('return arguments[0].complete && typeof arguments[0].naturalWidth != "undefined" '
                  '&& arguments[0].naturalWidth > 0')
            while not self.run_script(js):
                pass

        img_path = f'{path}\\{name}'
        self.inner_ele.screenshot(img_path)

        return img_path

    def set_property(self, prop: str, value: str) -> bool:
        """设置元素property属性          \n
        :param prop: 属性名
        :param value: 属性值
        :return: 是否设置成功
        """
        try:
            value = value.replace("'", "\\'")
            self.run_script(f"arguments[0].{prop}='{value}';")
            return True
        except:
            return False

    def set_attr(self, attr: str, value: str) -> bool:
        """设置元素attribute参数          \n
        :param attr: 参数名
        :param value: 参数值
        :return: 是否设置成功
        """
        try:
            self.run_script(f"arguments[0].setAttribute(arguments[1], arguments[2]);", attr, value)
            return True
        except:
            return False

    def remove_attr(self, attr: str) -> bool:
        """设置元素属性          \n
        :param attr: 属性名
        :return: 是否设置成功
        """
        try:
            self.run_script(f'arguments[0].removeAttribute("{attr}");')
            return True
        except:
            raise False

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
            raise TypeError('Need DriverElement, WebElement object or coordinate information.')

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

    def hover(self) -> None:
        """鼠标悬停"""
        from selenium.webdriver import ActionChains
        ActionChains(self.page.driver).move_to_element(self.inner_ele).perform()

    # -----------------私有函数-------------------
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
            raise ValueError(f"Argument mode can only be 'xpath' or 'css', not '{mode}'.")

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
        return self.run_script(js)

    def _get_brother(self, num: int = 1, mode: str = 'ele', direction: str = 'next'):
        """返回前面第num个兄弟节点或元素        \n
        :param num: 前面第几个兄弟节点或元素
        :param mode: 'ele', 'node' 或 'text'，匹配元素、节点、或文本节点
        :param direction: 'next' 或 'prev'，查找的方向
        :return: DriverElement对象或字符串
        """
        # 查找节点的类型
        if mode == 'ele':
            node_txt = '*'
        elif mode == 'node':
            node_txt = 'node()'
        elif mode == 'text':
            node_txt = 'text()'
        else:
            raise ValueError(f"Argument mode can only be 'node' ,'ele' or 'text', not '{mode}'.")

        # 查找节点的方向
        if direction == 'next':
            direction_txt = 'following'
        elif direction == 'prev':
            direction_txt = 'preceding'
        else:
            raise ValueError(f"Argument direction can only be 'next' or 'prev', not '{direction}'.")

        timeout = 0 if direction == 'prev' else .5

        # 获取节点
        ele_or_node = self.ele(f'xpath:./{direction_txt}-sibling::{node_txt}[{num}]', timeout=timeout)

        # 跳过元素间的换行符
        while isinstance(ele_or_node, str) and ele_or_node.replace('\n', '').replace('\t', '').replace(' ', '') == '':
            num += 1
            ele_or_node = self.ele(f'xpath:./{direction_txt}-sibling::{node_txt}[{num}]', timeout=timeout)

        return ele_or_node


def execute_driver_find(page_or_ele,
                        loc: Tuple[str, str],
                        mode: str = 'single',
                        timeout: float = None) -> Union[DriverElement, List[DriverElement], str, None]:
    """执行driver模式元素的查找                               \n
    页面查找元素及元素查找下级元素皆使用此方法                   \n
    :param page_or_ele: DriverPage对象或DriverElement对象
    :param loc: 元素定位元组
    :param mode: 'single' 或 'all'，对应获取第一个或全部
    :param timeout: 查找元素超时时间
    :return: 返回DriverElement元素或它们组成的列表
    """
    mode = mode or 'single'
    if mode not in ('single', 'all'):
        raise ValueError(f"Argument mode can only be 'single' or 'all', not '{mode}'.")

    if isinstance(page_or_ele, DrissionElement):
        page = page_or_ele.page
        driver = page_or_ele.inner_ele
    else:  # 传入的是DriverPage对象
        page = page_or_ele
        driver = page_or_ele.driver

    # 设置等待对象
    if timeout is not None and timeout != page.timeout:
        wait = WebDriverWait(driver, timeout=timeout)
    else:
        page.wait._driver = driver
        wait = page.wait

    try:
        # 使用xpath查找
        if loc[0] == 'xpath':
            return wait.until(ElementsByXpath(page, loc[1], mode, timeout))

        # 使用css selector查找
        else:
            if mode == 'single':
                return DriverElement(wait.until(ec.presence_of_element_located(loc)), page)
            elif mode == 'all':
                eles = wait.until(ec.presence_of_all_elements_located(loc))
                return [DriverElement(ele, page) for ele in eles]

    except TimeoutException:
        return [] if mode == 'all' else None

    except InvalidElementStateException:
        raise ValueError(f'Invalid query syntax. {loc}')


class ElementsByXpath(object):
    """用js通过xpath获取元素、节点或属性，与WebDriverWait配合使用"""

    def __init__(self, page, xpath: str = None, mode: str = 'all', timeout: float = 10):
        """
        :param page: DrissionPage对象
        :param xpath: xpath文本
        :param mode: 'all' 或 'single'
        :param timeout: 超时时间
        """
        self.page = page
        self.xpath = xpath
        self.mode = mode
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
        if self.mode == 'single':
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

        elif self.mode == 'all':
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
            raise TypeError(f"Select only works on <select> elements, not on {ele.tag}")

        from selenium.webdriver.support.select import Select as sl
        self.inner_ele = ele
        self.select_ele = sl(ele.inner_ele)

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

            except:
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
            raise NotImplementedError("You may only deselect options of a multi-select")

        for i in self.options:
            i.click()
