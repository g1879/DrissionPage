# 简介
***

DrissionPage，即driver和session的合体。  
它是一个python库，是个Web自动化操作集成工具。  
它整合了selenium和requests_html，实现了它们之间的无缝切换。  
因此可以兼顾selenium的便利性和requests的高效率。  
它封装了页面元素常用的方法，很适合自动化操作PO模式的扩展。  
更棒的是，它的使用方式非常人性化，代码量少，对新手友好。  

# 背景

***

新手学习爬虫时，面对须要登录的网站，要分析数据包、JS源码，构造复杂的请求，往往还要应付验证码、JS混淆、签名参数等反爬手段，学习门槛较高。获取数据时，有的数据是由JS计算生成的，若只拿到源数据，还须重现计算过程，体验不好，开发效率不高。

使用selenium，可以很大程度上绕过这些坑，但selenium效率不高。因此，这个库要做的，是将selenium和requests合而为一，不同须要时切换相应模式，并提供一种人性化的使用方法，提高开发和运行效率。

除了合并两者，本库还以网页为单位封装了常用功能，简化了selenium的操作和语句，在用于网页自动化操作时，减少考虑细节，专注功能实现，使用更方便。

# 特性

***

- 允许在selenium和requests间无缝切换，共享session。  
- 两种模式提供统一的操作方法，使用体验一致。  
- 以页面为单位封装常用方法，便于PO模式扩展。  
- 人性化的页面元素操作方法，减轻页面分析工作量和编码量。  
- 对某些常用功能（如点击）作了优化，更符合实际使用需要。  

# 简单演示

***

例：用selenium登录网站，然后切换到requests读取网页，打印元素属性。

```python
from DrissionPage import *
from time import sleep

drission = Drission()  # 创建驱动器对象
page = MixPage(drission)  # 创建页面对象，默认driver模式
page.get('https://gitee.com/profile')  # 访问个人中心页面（未登录，重定向到登录页面）

# 使用selenium输入账号密码登录
page.ele('@id:user_login').input('your_user_name')
page.ele('@id:user_password').input('your_password\n')
sleep(1)  # 等待登录

page.change_mode()  # 切换到session模式

print('登录后title：', page.title, '\n')  # 登录后session模式的输出

# 获取并打印属性
foot = page.ele('@id:footer-left')  # 用id查找元素
first_col = foot.ele('css:>div')  # 使用css selector在元素的下级中查找元素（第一个）
lnk = first_col.ele('text:命令学')  # 使用文本内容查找元素
text = lnk.text  # 获取元素文本
href = lnk.attr('href')  # 获取元素属性值

print(first_col)
print(text, href)
```

输出：

```
登录后title： 个人资料 - 码云 Gitee.com

<SessionElement div class='column'>
Git 命令学习 https://oschina.gitee.io/learn-git-branching/
```

# 安装

***

```
pip install DrissionPage
```
只支持python3.6及以上版本，driver模式目前只支持chrome。  
若要使用driver模式，须下载chrome和对应版本的chromedriver。[[chromedriver下载]](https://chromedriver.chromium.org/downloads)  
目前只在Windows环境下作了测试。

# 使用方法

***

## 导入模块

```python
from DrissionPage import *
```



## 创建驱动器对象

Drission对象用于管理driver和session对象。本库维护了一个ini文件，可直接从里面的配置信息创建驱动器。详细方法见[保存配置](# 保存配置)。也可以在初始化时传入配置信息。

**driver模式注意事项（只使用session模式可忽略）：**

- 须指定driver_chrome.exe和chrome.exe路径。
- 两个路径可创建时传入，也可保存到ini文件中，还可以写入系统变量（三选一）。
- 注意chromedriver.exe和chrome.exe版本匹配。

```python
# 两个路径已写入系统变量
drission = Drission()  

# 用传入的配置信息创建
from DrissionPage.config import DriverOptions
driver_options = DriverOptions()  # 创建driver配置对象
driver_options.binary_location = 'D:\\chrome\\chrome.exe'  # chrome.exe路径
driver_path = 'C:\\chrome\\chromedriver.exe'  # driver_path路径
drission = Drission(driver_options = driver_options, driver_path = driver_path) 

# 保存到ini文件
from DrissionPage.config import OptionsManager
options = OptionsManager()
driver_path = 'C:\\chrome\\chromedriver.exe'  # driver_path路径
chrome_path = 'D:\\chrome\\chrome.exe'  # chrome.exe路径
options.set_item('paths', 'chromedriver_path', driver_path)  # 设置driver_path路径
options.set_item('chrome_options', 'binary_location', chrome_path)  # 设置chrome.exe路径
options.save()  # 保存到ini文件
drission = Drission()  # 以后可直接创建
```



## 使用页面对象

页面对象封装了常用的网页操作，并实现driver和session模式之间的切换。

```python
page = MixPage(drission)  # 默认driver模式
page = MixPage(drission, mode='s', timeout=10)  # session模式，元素等待时间5秒（默认10秒）

# 访问URL
page.get(url, **kwargs)
page.post(url, data, **kwargs)  # 只有session模式才有post方法

# 切换模式
page.change_mode()

# 操作页面
print(page.html)  # 页面源代码
page.run_script(js)  # 运行js语句
page.close_other_tabs(num)  # 关闭其它标签页
page.to_iframe(iframe)  # 切入iframe
page.screenshot(path)  # 页面截图
page.scrool_to_see(element)  # 滚动直到某元素可见
# 详见APIs...
```

注：调用只属于driver模式的方法，会自动切换到driver模式。



## 查找元素

可使用多种方法查找页面元素（eles函数会返回所有符合要求的元素对象列表）。  

注：元素查找超时默认为10秒，你也可以按需要设置。

```python
# 根据属性查找
page.ele('@id:ele_id', timeout = 2)  # 查找id为ele_id的元素，设置等待时间2秒
page.eles('@class:class_name')  # 查找所有class为class_name的元素   

# 根据tag name查找
page.ele('tag:li')  # 查找第一个li元素  
page.eles('tag:li')  # 查找所有li元素  

# 根据位置查找
page.ele('@id:ele_id').parent  # 父元素  
page.ele('@id:ele_id').next  # 下一个兄弟元素  
page.ele('@id:ele_id').prev  # 上一个兄弟元素  

# 根据文本内容查找
page.ele('search text')  # 查找包含传入文本的元素  
page.eles('text:search text')  # 如文本以@、tag:、css:、xpath:、text:开头，则在前面加上text:避免冲突  

# 根据xpath或css selector查找
page.eles('xpath://div[@class="ele_class"]')  
page.eles('css:div.ele_class')  

# 根据loc查找
loc1 = By.ID, 'ele_id'
loc2 = By.XPATH, '//div[@class="ele_class"]'
page.ele(loc1)
page.ele(loc2)

# 查找下级元素
element = page.ele('@id:ele_id')
element.ele('@class:class_name')  # 在element下级查找第一个class为ele_class的元素
element.eles('tag:li')  # 在ele_id下级查找所有li元素

# 串连查找
page.ele('@id:ele_id').ele('tag:div').next.ele('some text').eles('tag:a')
```



## 元素操作

```python
# 获取元素信息
element = page.ele('@id:ele_id')
element.html  # 返回元素内html
element.text  # 返回元素内去除html标签后的text值
element.tag  # 返回元素tag name
element.attrs  # 返回元素所有属性的字典
element.attr('class')  # 返回元素的class属性
element.is_valid  # driver模式独有，用于判断元素是否还可用

# 操作元素
element.click()  # 点击元素
element.input(text)  # 输入文字
element.run_script(js)  # 运行js
element.submit()  # 提交表单
element.clear()  # 清空元素
element.is_selected()  # 是否被选中
element.is_enabled()  # 是否可用
element.is_displayed()  # 是否可见
element.is_valid()  # 是否有效，用于判断页面跳转导致元素失效的情况
element.select(text)  # 选中下拉列表选项
element.set_attr(attr,value)  # 设置元素属性
element.size  # 元素大小
element.location  # 元素位置
```



## 保存配置

因chrome和headers配置繁多，故设置一个ini文件专门用于保存常用配置，你可使用OptionsManager对象获取和保存配置，用DriverOptions对象修改chrome配置。

### ini文件内容

ini文件默认拥有三部分配置：paths、chrome_options、session_options。

```ini
[paths]
chromedriver_path = 
; chromedriver.exe路径
global_tmp_path = 
; 临时文件夹路径，用于保存截图、文件下载等

[chrome_options]
debugger_address =
; 已打开的浏览器地址和端口，如127.0.0.1:9222
binary_location = 
; chrome.exe路径
arguments = []
; 配置信息，如'--headless',
extensions = []
; 插件
experimental_options = {}
; 实验性配置

[session_options]
headers = {
          "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "Accept-Language": "zh-cn",
          "Connection": "keep-alive",
          "Accept-Charset": "GB2312,utf-8;q=0.7,*;q=0.7"
          }
```

### OptionsManager对象

OptionsManager对象用于读取、设置和保存配置。

```python
get_value(section, item) -> str  # 获取某个配置的值
get_option(section) -> dict  # 以字典格式返回配置全部属性
set_item(section, item, value)  # 设置配置属性
save()  # 保存配置到ini文件
```

### DriverOptions对象

DriverOptions对象继承自selenium.webdriver.chrome.options的Options对象，在其基础上增加了以下方法：

```python
remove_argument(value)  # 删除某argument值
remove_experimental_option(key)  # 删除某experimental_option设置
remove_all_extensions()  # 删除全部插件
save()  # 保存配置到ini文件
```

### 使用示例

```python
from DrissionPage import *
from DrissionPage.configs import *

driver_options = DriverOptions()  # 默认从ini文件读取配置
driver_options.add_argument('--headless')  # 添加配置
driver_options.remove_experimental_options('prefs')  # 移除配置
driver_options.save()  # 保存配置

options_manager = OptionsManager()  # 创建OptionsManager对象
driver_path = options_manager.get_value('paths', 'chromedriver_path')  # 读取路径信息

drission = Drission(driver_options, driver_path)  # 使用配置创建Drission对象
```

# PO模式

***

MixPage封装了常用的页面操作，可方便地用于扩展。  

例：扩展一个列表页面读取类

```python
import re
from time import sleep
from DrissionPage import *

class ListPage(MixPage):
    """本类封装读取列表页面的方法，根据必须的4个元素，可读取同构的列表页面
    （中文变量真香）"""
    def __init__(self, drission: Drission, url: str = None, **xpaths):
        super().__init__(drission)
        self._url = url
        self.xpath_栏目名 = xpaths['栏目名']  # [xpath字符串, 正则表达式]
        self.xpath_下一页 = xpaths['下一页']
        self.xpath_行s = xpaths['行']
        self.xpath_页数 = xpaths['页数']  # [xpath字符串, 正则表达式]
        self.总页数 = self.get_总页数()
        if url:
            self.get(url)

    def get_栏目名称(self) -> str:
        if self.xpath_栏目名[1]:
            s = self.ele(f'xpath:{self.xpath_栏目名[0]}').text
            r = re.search(self.xpath_栏目名[1], s)
            return r.group(1)
        else:
            return self.ele(f'xpath:{self.xpath_栏目名[0]}').text

    def get_总页数(self) -> int:
        if self.xpath_页数[1]:
            s = self.ele(f'xpath:{self.xpath_页数[0]}').text
            r = re.search(self.xpath_页数[1], s)
            return int(r.group(1))
        else:
            return int(self.ele(f'xpath:{self.xpath_页数[0]}').text)

    def click_下一页(self, wait: float = None):
        self.ele(f'xpath:{self.xpath_下一页}').click()
        if wait:
            sleep(wait)

    def get_当前页列表(self, 待爬内容: list) -> list:
        """
        待爬内容格式：[[xpath1,参数1],[xpath2,参数2]...]
        返回列表格式：[[参数1,参数2...],[参数1,参数2...]...]
        """
        结果列表 = []
        行s = self.eles(f'xpath:{self.xpath_行s}')
        for 行 in 行s:
            行结果 = []
            for j in 待爬内容:
                行结果.append(行.ele(f'xpath:{j[0]}').attr(j[1]))
            结果列表.append(行结果)
            print(行结果)
        return 结果列表

    def get_列表(self, 待爬内容: list,  wait: float = None) -> list:
        列表 = self.get_当前页列表(待爬内容)
        for _ in range(self.总页数 - 1):
            self.click_下一页(wait)
            列表.extend(self.get_当前页列表(待爬内容))
        return 列表
```

# 其它

***

## DriverPage和SessionPage

如果无须切换模式，可根据需要只使用DriverPage或SessionPage，用法和MixPage一致。  

```python
from DrissionPage.session_page import SessionPage
from DrissionPage.drission import Drission

session = Drission().session
page = SessionPage(session)  # 传入Session对象
page.get('http://www.baidu.com')
print(page.ele('@id:su').text)  # 输出：百度一下

driver = Drission().driver
page = DriverPage(driver)  # 传入Driver对象
page.get('http://www.baidu.com')
print(page.ele('@id:su').text)  # 输出：百度一下
```

# APIs

***

## Drission类

class **Drission**(driver_options: Union[dict, Options] = None, session_options: dict = None, driver_path: str = None)

用于管理driver和session对象。参数说明：

- driver_options - chrome配置参数，可接收Options对象或字典
- session_options - session配置参数，接收字典
- driver_path - chromedriver.exe路径，如不设置，须在系统设置系统变量

### session

​	返回HTMLSession对象，调用时自动创建。

### driver

​	获取WebDriver对象，调用时自动创建，按传入配置或ini文件配置初始化。

### session_options

​	以字典格式返回或设置session配置。

### cookies_to_session

​	cookies_to_session(copy_user_agent: bool = False, driver: WebDriver = None, session: Session = None) -> None

​	把cookies从driver复制到session。默认复制self.driver到self.session，也可以接收driver和session进行操作。

​	参数说明：

- copy_user_agent - 是否复制user_agent到session
- driver - WebDriver对象，复制cookies
- session - Session对象，接收cookies

### cookies_to_driver

​	cookies_to_driver(url: str, driver: WebDriver = None, session: Session = None) -> None

​	把cookies从session复制到driver。默认复制self.session到self.driver，也可以接收driver和session进行操作。须要指定url或域名。

​	参数说明：

- url - cookies的域
- driver - WebDriver对象，接收cookies
- session - Session对象，复制cookies

### user_agent_to_session

​	user_agent_to_session(driver: WebDriver = None, session: Session = None) -> None

​	把user agent从driver复制到session。默认复制self.driver到self.session，也可以接收driver和session进行操作。

​	参数说明：

- driver - WebDriver对象，复制user agent
- session - Session对象，接收user agent

### close_driver

​	close_driver() -> None

​	关闭浏览器，driver置为None。

### close_session

​	close_session() -> None

​	关闭session并置为None。

### close

​	close() -> None

​	关闭driver和session。



## MixPage类

class **MixPage**(drission: Drission, mode='d', timeout: float = 10)

MixPage封装了页面操作的常用功能，可在driver和session模式间无缝切换。切换的时候会自动同步cookies。  
获取信息功能为两种模式共有，操作页面元素功能只有d模式有。调用某种模式独有的功能，会自动切换到该模式。  
它继承自DriverPage和SessionPage类，这些功能由这两个类实现，MixPage作为调度的角色存在。

参数说明：

- drission - Drission对象
- mode - 模式，可选'd'或's'，默认为'd'
- timeout - 查找元素超时时间（每次查找元素时还可单独设置）

### url  

​	返回当前访问的url。

### mode

​	返回当前模式（'s'或'd'）。

### drission

​	返回当前使用的Dirssion对象。

### driver

​	返回driver对象，如没有则创建，调用时会切换到driver模式。

###　session

​	返回session对象，如没有则创建。

### response

​	返回Response对象，调用时会切换到session模式。

### cookies

​	返回cookies，从当前模式获取。

### html

​	返回页面html文本。

### title

​	返回页面title文本。

### change_mode

​	change_mode(mode: str = None, go: bool = True) -> None

​	切换模式，可指定目标模式，若目标模式与当前模式一致，则直接返回。

​	参数说明：

- mode - 指定目标模式，'d'或's'。
- go - 切换模式后是否跳转到当前url

### get

​	get(url: str, params: dict = None, go_anyway=False, **kwargs) -> Union[bool, None]

​	跳转到一个url，跳转前先同步cookies，跳转后返回目标url是否可用。

​	参数说明：

- url - 目标url
- params - url参数
- go_anyway - 是否强制跳转。若目标url和当前url一致，默认不跳转。
- kwargs - 用于session模式时访问参数。

### ele

​	ele(loc_or_ele: Union[tuple, str, DriverElement, SessionElement], mode: str = None, timeout: float = None, show_errmsg: bool = False) -> Union[DriverElement, SessionElement]

​	根据查询参数获取元素，返回元素或元素列表。  
​	如查询参数是字符串，可选'@属性名:'、'tag:'、'text:'、'css:'、'xpath:'方式。无控制方式时默认用text方式查找。  
​	如是loc，直接按照内容查询。

​	参数说明：

- loc_or_str - 查询条件参数，如传入一个元素对象，则直接返回
- mode - 查找一个或多个，传入'single'或'all'
- timeout - 查找元素超时时间，driver模式下有效
- show_errmsg - 出现异常时是否抛出及显示

​	示例：

- page.ele('@id:ele_id') - 按照属性查找元素
- page.ele('tag:div') - 按照tag name查找元素
- page.ele('text:some text') - 按照文本查找元素
- page.ele('some text') - 按照文本查找元素
- page.ele('css:>div') - 按照css selector查找元素
- page.ele('xpath://div') - 按照xpath查找元素
- page.ele((By.ID, 'ele_id')) - 按照loc方式查找元素

### eles

​	eles(loc_or_str: Union[tuple, str], timeout: float = None, show_errmsg: bool = False) -> List[DriverElement]

​	根据查询参数获取符合条件的元素列表。查询参数使用方法和ele方法一致。

​	参数说明：

- loc_or_str - 查询条件参数
- timeout - 查找元素超时时间，driver模式下有效
- show_errmsg - 出现异常时是否抛出及显示

### cookies_to_session

​	cookies_to_session(copy_user_agent: bool = False) -> None

​	手动把cookies从driver复制到session。

​	参数说明：

- copy_user_agent - 是否同时复制user agent

### cookies_to_driver

​	cookies_to_driver(url=None) -> None

​	手动把cookies从session复制到driver。

​	参数说明：

- url - cookies的域或url

### post

​	post(url: str, params: dict = None, data: dict = None, go_anyway: bool = False, **kwargs) -> Union[bool, None]

​	以post方式跳转，调用时自动切换到session模式。

​	参数说明：

- url - 目标url
- parame - url参数
- data - 提交的数据
- go_anyway - 是否强制跳转。若目标url和当前url一致，默认不跳转。
- kwargs - headers等访问参数

### download

​	download(file_url: str, goal_path: str = None, rename: str = None, **kwargs) -> tuple

​	下载一个文件，返回是否成功和下载信息字符串。改方法会自动避免和目标路径现有文件重名。

​	参数说明：

- file_url - 文件URL
- goal_path - 存放路径，默认为ini文件中指定的临时文件夹
- rename - 重命名文件名，默认不重命名
- kwargs - 用于requests的连接参数



以下方法只有driver模式下生效，调用时会自动切换到driver模式

***

### check_page

​	check_page() -> bool

​	派生子类后用于检查域名是否符合预期，功能由子类实现。

### run_script

​	run_script(script: str) -> Any

​	执行JavaScript代码。

​	参数说明：

- script - JavaScript代码文本

### get_tabs_sum

​	get_tabs_sum() -> int

​	返回浏览器标签页数量。

### get_tab_num

​	get_tab_num() -> int

​	返回当前标签页序号。

### to_tab

​	to_tab(index: int = 0) -> None

​	跳转到某序号的标签页。

参数说明：

- index - 目标标签页序号，从0开始计算

### close_current_tab

​	close_current_tab() -> None

​	关闭当前标签页。

### close_other_tabs

​	close_other_tabs(tab_index: int = None) -> None

​	关闭除序号外的标签页。

​	参数说明：

- index - 保留的标签页序号，从0开始计算

### to_iframe

​	to_iframe(loc_or_ele: Union[str, tuple, WebElement] = 'main') -> bool

​	跳转到iframe，默认跳转到最高层级。

​	参数说明：

- loc_or_ele - 查找iframe元素的条件，和ele()方法的查找条件一致。

​	示例：
- to_iframe('@id:iframe_id')
- to_iframe(iframe_element)

### scroll_to_see

​	scroll_to_see(loc_or_ele: Union[WebElement, tuple]) -> None

​	滚动直到元素可见。

​	参数说明：

- loc_or_ele - 查找iframe元素的条件，和ele()方法的查找条件一致。

### scroll_to

​	scroll_to(mode: str = 'bottom', pixel: int = 300) -> None

​	滚动页面，按照参数决定如何滚动。

​	参数说明：

- mode - 滚动的方向，top、bottom、rightmost、leftmost、up、down、left、right
- pixel - 滚动的像素

### refresh

​	refresh() -> None

​	刷新页面。

### back

​	back() -> None

​	页面后退。

### set_window_size

​	set_window_size(x: int = None, y: int = None) -> None

​	设置窗口大小，默认最大化。

​	参数说明：

- x - 目标宽度
- y - 目标高度

### screenshot

​	screenshot(path: str = None, filename: str = None) -> str

​	网页截图，返回截图文件路径。

​	参数说明：

- path - 截图保存路径，默认为ini文件中指定的临时文件夹
- filename - 截图文件名，默认为页面title为文件名

### is_downloading

​	is_downloading(download_path: str = None) -> bool

​	检测浏览器是否下载完毕。

​	参数说明：

- download_path - 下载路径，默认为ini文件中定义的路径

### close_driver

​	close_driver() -> None

​	关闭driver及浏览器，切换到s模式。

### close_session

​	close_session() -> None

​	关闭session，切换到d模式。

## DriverElement类

class DriverElement(ele: WebElement, timeout: float = 10)

driver模式的元素对象，包装了一个WebElement对象，并封装了常用功能。

参数说明：

- ele - WebElement对象
- timeout - 查找元素超时时间（每次查找元素时还可单独设置）

### inner_ele

​	被包装的WebElement对象。

### attrs

​	以字典方式返回元素所有属性及值。

### text

​	返回元素内的文本。

### html

​	返回元素内html文本。

### tag

​	返回元素标签名文本。

### parent

​	返回父级元素对象。

### next

​	返回下一个兄弟元素对象。

### prev

​	返回上一个兄弟元素对象。

### size

​	以字典方式返回元素大小。

### location

​	以字典方式放回元素坐标。

### ele

​	ele(loc_or_str: Union[tuple, str], mode: str = None, show_errmsg: bool = False, timeout: float = None) -> Union[DriverElement, List[DriverElement], None]

​	根据查询参数获取元素。  
​	如查询参数是字符串，可选'@属性名:'、'tag:'、'text:'、'css:'、'xpath:'方式。无控制方式时默认用text方式查找。  
​	如是loc，直接按照内容查询。

​	参数说明：

- loc_or_str - 查询条件参数
- mode - 查找一个或多个，传入'single'或'all'
- show_errmsg - 出现异常时是否抛出及显示
- timeout - 查找元素超时时间

​	示例：

- element.ele('@id:ele_id') - 按照属性查找元素
- element.ele('tag:div') - 按照tag name查找元素
- element.ele('text:some text') - 按照文本查找元素
- element.ele('some text') - 按照文本查找元素
- element.ele('css:>div') - 按照css selector查找元素
- element.ele('xpath://div') - 按照xpath查找元素
- element.ele((By.ID, 'ele_id')) - 按照loc方式查找元素

### eles

​	eles(loc_or_str: Union[tuple, str], show_errmsg: bool = False, timeout: float = None) ->  List[DriverElement]

​	根据查询参数获取符合条件的元素列表。查询参数使用方法和ele方法一致。

​	参数说明：

- loc_or_str - 查询条件参数
- show_errmsg - 出现异常时是否抛出及显示
- timeout - 查找元素超时时间

### attr

​	attr(attr: str) -> str

​	获取元素某个属性的值。

​	参数说明：

- attr - 属性名称

### click

​	click(by_js=False) -> bool

​	点击元素，如不成功则用js方式点击，可指定用js方式点击。

​	参数说明：

- by_js - 是否用js方式点击

### input

​	input(value, clear: bool = True) -> bool

​	输入文本。

​	参数说明：

- value - 文本值
- clear - 输入前是否清除文本框

### run_script

​	run_script(script: str) -> Any

​	在元素上运行JavaScript。

​	参数说明：

- script - JavaScript文本

### submit

​	submit() -> None

​	提交表单。

### clear

​	clear() -> None

​	清空文本框。

### is_selected

​	is_selected() -> bool

​	元素是否被选中。

### is_enabled

​	is_enabled() -> bool

​	元素在页面中是否可用。

### is_displayed

​	is_displayed() -> bool

​	元素是否可见。

### is_valid

​	is_valid() -> bool

​	元素是否有效。该方法用于判断页面跳转元素不能用的情况

### screenshot

​	screenshot(path: str = None, filename: str = None) -> str

​	网页截图，返回截图文件路径。

​	参数说明：

- path - 截图保存路径，默认为ini文件中指定的临时文件夹
- filename - 截图文件名，默认为页面title为文件名

### select

​	select(text: str) -> bool

​	在下拉列表中选择。

​	参数说明：

- text - 选项文本

### set_attr

​	set_attr(attr: str, value: str) -> bool

​	设置元素属性。

​	参数说明：

- attr - 参数名
- value - 参数值



## SessionElement类

class SessionElement(ele: Element)

session模式的元素对象，包装了一个Element对象，并封装了常用功能。

参数说明：

- ele - requests_html库的Element对象

### inner_ele

​	被包装的Element对象。

### attrs

​	以字典格式返回元素所有属性的名称和值。

### text

​	返回元素内的文本。

### html

​	返回元素内html文本。

### tag

​	返回元素标签名文本。

### parent

​	返回父级元素对象。

### next

​	返回下一个兄弟元素对象。

### prev 

​	返回上一个兄弟元素对象。

### ele

​	ele(loc_or_str: Union[tuple, str], mode: str = None, show_errmsg: bool = False) -> Union[SessionElement, List[SessionElement], None]

​	根据查询参数获取元素。  
​	如查询参数是字符串，可选'@属性名:'、'tag:'、'text:'、'css:'、'xpath:'方式。无控制方式时默认用text方式查找。  
​	如是loc，直接按照内容查询。

​	参数说明：

- loc_or_str - 查询条件参数

- mode - 查找一个或多个，传入'single'或'all'

- show_errmsg - 出现异常时是否抛出及显示

​	示例：

- element.ele('@id:ele_id') - 按照属性查找元素
- element.ele('tag:div') - 按照tag name查找元素
- element.ele('text:some text') - 按照文本查找元素
- element.ele('some text') - 按照文本查找元素
- element.ele('css:>div') - 按照css selector查找元素
- element.ele('xpath://div') - 按照xpath查找元素
- element.ele((By.ID, 'ele_id')) - 按照loc方式查找元素

### eles

​	eles(loc_or_str: Union[tuple, str], show_errmsg: bool = False) ->  List[SessionElement]

​	根据查询参数获取符合条件的元素列表。查询参数使用方法和ele方法一致。

​	参数说明：

- loc_or_str - 查询条件参数
- show_errmsg - 出现异常时是否抛出及显示

### attr

​	attr(attr: str) -> str

​	获取元素某个属性的值。

​	参数说明：

- attr - 属性名称



## OptionsManager类

​	class OptionsManager(path: str = None)

​	管理配置文件内容的类。

​	参数说明：

- path - ini文件路径，不传入则默认读取当前文件夹下的configs.ini文件

### get_value

​	get_value(section: str, item: str) -> Any

​	获取配置的值。

​	参数说明：

- section - 段落名称
- item - 配置项名称

### get_option

​	get_option(section: str) -> dict

​	以字典的格式返回整个段落的配置信息。

​	参数说明：

- section - 段落名称

### set_item

​	set_item(section: str, item: str, value: str) -> None

​	设置配置值。

​	参数说明：

- section - 段落名称
- item - 配置项名称
- value - 值内容

### save

​	save() -> None

​	保存设置到文件。



## DriverOptions类

​	class DriverOptions(read_file=True)

​	chrome浏览器配置类，继承自selenium.webdriver.chrome.options的Options类，增加了删除配置和保存到文件方法。

​	参数说明：

- read_file - 布尔型，指定创建时是否从ini文件读取配置信息

### remove_argument

​	remove_argument(value: str) -> None

​	移除一个设置。

​	参数说明：

- value - 要移除的属性值

### remove_experimental_option

​	remove_experimental_option(key: str) -> None

​	移除一个实验设置，传入key值删除。

​	参数说明：

- key - 要移除的实验设置key值

### remove_argument

​	remove_argument() -> None

​	移除所有插件，因插件是以整个文件储存，难以移除其中一个，故如须设置则全部移除再重设。

### save()

​	save() -> None

​	保存设置到文件。
