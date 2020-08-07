# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_element.py
"""
from html import unescape
from pathlib import Path
from time import sleep
from typing import Union, List, Any

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from .common import DrissionElement, get_loc_from_str, translate_loc_to_xpath, avoid_duplicate_name


class DriverElement(DrissionElement):
    """driver模式的元素对象，包装了一个WebElement对象，并封装了常用功能"""

    def __init__(self, ele: WebElement, timeout: float = 10):
        super().__init__(ele)
        self.timeout = timeout
        self._driver = ele.parent

    def __repr__(self):
        attrs = [f"{attr}='{self.attrs[attr]}'" for attr in self.attrs]
        return f'<DriverElement {self.tag} {" ".join(attrs)}>'

    @property
    def driver(self) -> WebDriver:
        """返回控制元素的WebDriver对象"""
        return self._driver

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
        attrs = dict()
        for attr in eval(self.run_script(js)):
            attrs[attr] = self.attr(attr)
        return attrs

    @property
    def text(self) -> str:
        """返回元素内所有文本"""
        return unescape(self.attr('innerText')).replace('\xa0', ' ')

    @property
    def html(self) -> str:
        """返回元素innerHTML文本"""
        return unescape(self.attr('innerHTML')).replace('\xa0', ' ')

    @property
    def tag(self) -> str:
        """返回元素类型"""
        return self._inner_ele.tag_name

    @property
    def parent(self):
        """返回父级元素"""
        return self.parents()

    @property
    def next(self):
        """返回后一个兄弟元素"""
        return self.nexts()

    @property
    def prev(self):
        """返回前一个兄弟元素"""
        return self.prevs()

    def parents(self, num: int = 1):
        """返回上面第num级父元素              \n
        :param num: 第几级父元素
        :return: DriverElement对象
        """
        loc = 'xpath', f'.{"/.." * num}'
        return self.ele(loc, timeout=1, show_errmsg=False)

    def nexts(self, num: int = 1):
        """返回后面第num个兄弟元素      \n
        :param num: 后面第几个兄弟元素
        :return: DriverElement对象
        """
        loc = 'xpath', f'./following-sibling::*[{num}]'
        return self.ele(loc, timeout=1, show_errmsg=False)

    def prevs(self, num: int = 1):
        """返回前面第num个兄弟元素        \n
        :param num: 前面第几个兄弟元素
        :return: DriverElement对象
        """
        loc = 'xpath', f'./preceding-sibling::*[{num}]'
        return self.ele(loc, timeout=1, show_errmsg=False)

    def attr(self, attr: str) -> str:
        """获取属性值            \n
        :param attr: 属性名
        :return: 属性值文本
        """
        if attr == 'text':
            return self.text
        else:
            # return self.attrs[attr]
            return self.inner_ele.get_attribute(attr)

    def ele(self,
            loc_or_str: Union[tuple, str],
            mode: str = None,
            timeout: float = None,
            show_errmsg: bool = False):
        """返回当前元素下级符合条件的子元素，默认返回第一个                                                 \n
        示例：                                                                                           \n
        - 用loc元组查找：                                                                                 \n
            ele.ele((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的子元素                       \n
        - 用查询字符串查找：                                                                               \n
            查找方式：属性、tag name和属性、文本、xpath、css selector                                        \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                          \n
            ele.ele('@class:ele_class')                 - 返回第一个class含有ele_class的子元素              \n
            ele.ele('@name=ele_name')                   - 返回第一个name等于ele_name的子元素                \n
            ele.ele('@placeholder')                     - 返回第一个带placeholder属性的子元素               \n
            ele.ele('tag:p')                            - 返回第一个<p>子元素                              \n
            ele.ele('tag:div@class:ele_class')          - 返回第一个class含有ele_class的div子元素           \n
            ele.ele('tag:div@class=ele_class')          - 返回第一个class等于ele_class的div子元素           \n
            ele.ele('tag:div@text():some_text')         - 返回第一个文本含有some_text的div子元素             \n
            ele.ele('tag:div@text()=some_text')         - 返回第一个文本等于some_text的div子元素             \n
            ele.ele('text:some_text')                   - 返回第一个文本含有some_text的子元素                \n
            ele.ele('some_text')                        - 返回第一个文本含有some_text的子元素（等价于上一行）  \n
            ele.ele('text=some_text')                   - 返回第一个文本等于some_text的子元素                \n
            ele.ele('xpath://div[@class="ele_class"]')  - 返回第一个符合xpath的子元素                        \n
            ele.ele('css:div.ele_class')                - 返回第一个符合css selector的子元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param mode: 'single' 或 'all‘，对应查找一个或全部
        :param timeout: 查找元素超时时间
        :param show_errmsg: 出现异常时是否打印信息
        :return: DriverElement对象
        """
        if isinstance(loc_or_str, str):
            loc_or_str = get_loc_from_str(loc_or_str)
        elif isinstance(loc_or_str, tuple) and len(loc_or_str) == 2:
            pass
        else:
            raise ValueError('Argument loc_or_str can only be tuple or str.')

        if loc_or_str[0] == 'xpath':
            # 确保查询语句最前面是.
            loc_str = f'.{loc_or_str[1]}' if not loc_or_str[1].startswith('.') else loc_or_str[1]
            loc_or_str = loc_or_str[0], loc_str

        timeout = timeout or self.timeout
        return execute_driver_find(self.inner_ele, loc_or_str, mode, show_errmsg, timeout)

    def eles(self,
             loc_or_str: Union[tuple, str],
             timeout: float = None,
             show_errmsg: bool = False) -> list:
        """返回当前元素下级所有符合条件的子元素                                                           \n
        示例：                                                                                          \n
        - 用loc元组查找：                                                                                \n
            ele.eles((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的子元素                     \n
        - 用查询字符串查找：                                                                              \n
            查找方式：属性、tag name和属性、文本、xpath、css selector                                       \n
            其中，@表示属性，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串                         \n
            ele.eles('@class:ele_class')                 - 返回所有class含有ele_class的子元素              \n
            ele.eles('@name=ele_name')                   - 返回所有name等于ele_name的子元素                \n
            ele.eles('@placeholder')                     - 返回所有带placeholder属性的子元素               \n
            ele.eles('tag:p')                            - 返回所有<p>子元素                              \n
            ele.eles('tag:div@class:ele_class')          - 返回所有class含有ele_class的div子元素           \n
            ele.eles('tag:div@class=ele_class')          - 返回所有class等于ele_class的div子元素           \n
            ele.eles('tag:div@text():some_text')         - 返回所有文本含有some_text的div子元素             \n
            ele.eles('tag:div@text()=some_text')         - 返回所有文本等于some_text的div子元素             \n
            ele.eles('text:some_text')                   - 返回所有文本含有some_text的子元素                \n
            ele.eles('some_text')                        - 返回所有文本含有some_text的子元素（等价于上一行）  \n
            ele.eles('text=some_text')                   - 返回所有文本等于some_text的子元素                \n
            ele.eles('xpath://div[@class="ele_class"]')  - 返回所有符合xpath的子元素                        \n
            ele.eles('css:div.ele_class')                - 返回所有符合css selector的子元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :param show_errmsg: 出现异常时是否打印信息
        :return: DriverElement对象组成的列表
        """
        if not isinstance(loc_or_str, tuple) or not isinstance(loc_or_str, str):
            raise TypeError('Type of loc_or_str can only be tuple or str.')
        return self.ele(loc_or_str, mode='all', show_errmsg=show_errmsg, timeout=timeout)

    # -----------------以下为driver独占-------------------
    def click(self, by_js=None) -> bool:
        """点击元素                                                                      \n
        尝试点击10次，若都失败就改用js点击                                                  \n
        :param by_js: 是否用js点击，为True时直接用js点击，为False时重试失败也不会改用js
        :return: 是否点击成功
        """
        if not by_js:
            for _ in range(10):
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

    def input(self, value, clear: bool = True) -> bool:
        """输入文本                          \n
        :param value: 文本值
        :param clear: 输入前是否清空文本框
        :return: 是否输入成功
        """
        try:
            if clear:
                self.clear()
            self.inner_ele.send_keys(value)
            return True
        except Exception as e:
            print(e)
            return False

    def run_script(self, script: str) -> Any:
        """执行js                   \n
        :param script: js文本
        :return: js执行结果
        """
        return self.inner_ele.parent.execute_script(script, self.inner_ele)

    def submit(self) -> None:
        """提交表单"""
        self.inner_ele.submit()

    def clear(self) -> None:
        """清空元素文本"""
        self.run_script("arguments[0].value=''")
        # self.ele.clear()

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
        """用于判断元素是否还能用，应对页面跳转元素不能用的情况"""
        try:
            self.is_enabled()
            return True
        except:
            return False

    @property
    def size(self) -> dict:
        """返回元素宽和高"""
        return self.inner_ele.size

    @property
    def location(self) -> dict:
        """返回元素左上角坐标"""
        return self.inner_ele.location

    def screenshot(self, path: str, filename: str = None) -> str:
        """对元素进行截图                                          \n
        :param path: 保存路径
        :param filename: 图片文件名，不传入时以元素tag name命名
        :return: 图片完整路径
        """
        name = filename or self.tag
        path = Path(path).absolute()
        path.mkdir(parents=True, exist_ok=True)
        name = avoid_duplicate_name(str(path), f'{name}.png')
        # 等待元素加载完成
        if self.tag == 'img':
            js = 'return arguments[0].complete && typeof arguments[0].naturalWidth != "undefined" ' \
                 '&& arguments[0].naturalWidth > 0'
            while not self.run_script(js):
                pass
        img_path = f'{path}\\{name}'
        self.inner_ele.screenshot(img_path)
        return img_path

    def select(self, text: str) -> bool:
        """选择下拉列表中子元素       \n
        :param text: 要选择的文本
        :return: 是否选择成功
        """
        from selenium.webdriver.support.select import Select
        ele = Select(self.inner_ele)
        try:
            ele.select_by_visible_text(text)
            return True
        except:
            return False

    def set_attr(self, attr: str, value: str) -> bool:
        """设置元素属性          \n
        :param attr: 属性名
        :param value: 属性值
        :return: 是否设置成功
        """
        try:
            self.run_script(f"arguments[0].{attr} = '{value}';")
            return True
        except Exception as e:
            print(e)
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
        # x, y：目标坐标点
        if isinstance(ele_or_loc, DriverElement) or isinstance(ele_or_loc, WebElement):
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
        actions = ActionChains(self.driver)
        actions.click_and_hold(self.inner_ele)
        loc1 = self.location
        for x, y in points:  # 逐个访问要经过的点
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
        ActionChains(self._driver).move_to_element(self.inner_ele).perform()


def execute_driver_find(page_or_ele: Union[WebElement, WebDriver],
                        loc: tuple,
                        mode: str = 'single',
                        show_errmsg: bool = False,
                        timeout: float = 10) -> Union[DriverElement, List[DriverElement]]:
    """执行driver模式元素的查找                               \n
    页面查找元素及元素查找下级元素皆使用此方法                   \n
    :param page_or_ele: WebDriver对象或WebElement元素对象
    :param loc: 元素定位元组
    :param mode: 'single' 或 'all'，对应获取第一个或全部
    :param show_errmsg: 出现异常时是否显示错误信息
    :param timeout: 查找元素超时时间
    :return: 返回DriverElement元素或它们组成的列表
    """
    mode = mode or 'single'
    if mode not in ['single', 'all']:
        raise ValueError("Argument mode can only be 'single' or 'all'.")
    msg = result = None
    try:
        wait = WebDriverWait(page_or_ele, timeout=timeout)
        if mode == 'single':
            msg = 'Element not found.'
            result = DriverElement(wait.until(ec.presence_of_element_located(loc)))
        elif mode == 'all':
            msg = 'Elements not found.'
            eles = wait.until(ec.presence_of_all_elements_located(loc))
            result = [DriverElement(ele) for ele in eles]
        return result
    except:
        if show_errmsg:
            print(msg, loc)
            raise
        return [] if mode == 'all' else None
