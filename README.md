# 简介

***

DrissionPage，即 driver 和 session 组合而成的 page。  
是个基于 python 的 Web 自动化操作集成工具。  
它实现了 selenium 和 requests 之间的无缝切换。  
可以兼顾 selenium 的便利性和 requests 的高效率。  
它集成了页面常用功能，两种模式系统一致的 API，使用便捷。  
它用 POM 模式封装了页面元素常用的方法，适合自动化操作功能扩展。  
更棒的是，它的使用方式非常简洁和人性化，代码量少，对新手友好。

**项目地址：**

- https://github.com/g1879/DrissionPage
- https://gitee.com/g1879/DrissionPage

**示例地址：** [使用DrissionPage的网页自动化及爬虫示例](https://gitee.com/g1879/DrissionPage-demos)

**联系邮箱：**  g1879@qq.com

**交流QQ群：**  897838127

**理念**

**简洁、易用 、可扩展**

**背景**

requests 爬虫面对要登录的网站时，要分析数据包、JS 源码，构造复杂的请求，往往还要应付验证码、JS 混淆、签名参数等反爬手段，门槛较高。若数据是由 JS 计算生成的，还须重现计算过程，体验不好，开发效率不高。  
使用 selenium，可以很大程度上绕过这些坑，但 selenium 效率不高。因此，这个库将 selenium 和 requests 合而为一，不同须要时切换相应模式，并提供一种人性化的使用方法，提高开发和运行效率。  
除了合并两者，本库还以网页为单位封装了常用功能，简化了 selenium 的操作和语句，在用于网页自动化操作时，减少考虑细节，专注功能实现，使用更方便。  
一切从简，尽量提供简单直接的使用方法，对新手更友好。

# 特性

***

- 以简洁的代码为第一追求。
- 允许在 selenium 和 requests 间无缝切换，共享 session。
- 两种模式提供一致的 API，使用体验一致。
- 人性化的页面元素操作方式，减轻页面分析工作量和编码量。
- 对常用功能作了整合和优化，更符合实际使用需要。
- 兼容 selenium 代码，便于项目迁移。
- 使用 POM 模式封装，便于扩展。
- 统一的文件下载方法，弥补浏览器下载的不足。
- 简易的配置方法，摆脱繁琐的浏览器配置。

# 项目结构

***

**结构图**

![](https://gitee.com/g1879/DrissionPage-demos/raw/master/pics/20201118170751.jpg)

**Drission 类**

管理负责与网页通讯的 WebDriver 对象和 Session 对象，相当于驱动器的角色。

**MixPage 类**

MixPage 封装了页面操作的常用功能，它调用 Drission 类中管理的驱动器，对页面进行访问、操作。可在 driver 和 session 模式间切换。切换的时候会自动同步登录状态。

**DriverElement 类**

driver 模式下的页面元素类，可对元素进行点击、输入文本、修改属性、运行 js 等操作，也可在其下级搜索后代元素。

**SessionElement 类**

session 模式下的页面元素类，可获取元素属性值，也可在其下级搜索后代元素。

# 简单演示

***

**与 selenium 代码对比**

以下代码实现一模一样的功能，对比两者的代码量：

- 用显性等待方式查找第一个文本包含 some text 的元素

```python
# 使用 selenium：
element = WebDriverWait(driver).until(ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "some text")]')))

# 使用 DrissionPage：
element = page('some text')
```

- 跳转到第一个标签页

```python
# 使用 selenium：
driver.switch_to.window(driver.window_handles[0])

# 使用 DrissionPage：
page.to_tab(0)
```

- 按文本选择下拉列表

```python
# 使用 selenium：
from selenium.webdriver.support.select import Select
select_element = Select(element)
select_element.select_by_visible_text('text')

# 使用 DrissionPage：
element.select('text')
```

- 拖拽一个元素

```python
# 使用 selenium：
ActionChains(driver).drag_and_drop(ele1, ele2).perform()

# 使用 DrissionPage：
ele1.drag_to(ele2)
```

- 滚动窗口到底部（保持水平滚动条不变）

```python
# 使用 selenium：
driver.execute_script("window.scrollTo(document.documentElement.scrollLeft, document.body.scrollHeight);")

# 使用 DrissionPage：
page.scroll_to('bottom')
```

- 设置 headless 模式

```python
# 使用 selenium：
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# 使用 DrissionPage：
set_headless()
```

- 获取伪元素内容

```python
# 使用 selenium：
text = webdriver.execute_script('return window.getComputedStyle(arguments[0], "::after").getPropertyValue("content");', element)

# 使用 DrissionPage：
text = element.after
```

- 获取 shadow-root

```python
# 使用 selenium：
shadow_element = webdriver.execute_script('return arguments[0].shadowRoot', element)

# 使用 DrissionPage：
shadow_element = element.shadow_root
```

- 用 xpath 直接获取属性或文本节点（返回文本）

```python
# 使用 selenium：
相当复杂

# 使用 DrissionPage：
class_name = element('xpath://div[@id="div_id"]/@class')
text = element('xpath://div[@id="div_id"]/text()[2]')
```

**与 requests 代码对比**

以下代码实现一模一样的功能，对比两者的代码量：

- 获取元素内容

```python
url = 'https://baike.baidu.com/item/python'

# 使用 requests：
from lxml import etree
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
response = requests.get(url, headers = headers)
html = etree.HTML(response.text)
element = html.xpath('//h1')[0]
title = element.text

# 使用 DrissionPage：
page = MixPage('s')
page.get(url)
title = page('tag:h1').text
```

Tips: DrissionPage 自带默认 headers

- 下载文件

```python
url = 'https://www.baidu.com/img/flexible/logo/pc/result.png'
save_path = r'C:\download'

# 使用 requests：
r = requests.get(url)
with open(f'{save_path}\\img.png', 'wb') as fd:
   for chunk in r.iter_content():
       fd.write(chunk)
        
# 使用 DrissionPage：
page.download(url, save_path, 'img')  # 支持重命名，处理文件名冲突
```

**模式切换**

用 selenium 登录网站，然后切换到 requests 读取网页。两者会共享登录信息。

```python
page = MixPage()  # 创建页面对象，默认 driver 模式
page.get('https://gitee.com/profile')  # 访问个人中心页面（未登录，重定向到登录页面）

page.ele('@id:user_login').input('your_user_name')  # 使用 selenium 输入账号密码登录
page.ele('@id:user_password').input('your_password\n')
sleep(1)

page.change_mode()  # 切换到 session 模式
print('登录后title：', page.title, '\n')  # 登录后 session 模式的输出
```

输出：

```
登录后title： 个人资料 - 码云 Gitee.com
```

**获取并打印元素属性**

```python
# 接上段代码
foot = page.ele('@id:footer-left')  # 用 id 查找元素
first_col = foot.ele('css:>div')  # 使用 css selector 在元素的下级中查找元素（第一个）
lnk = first_col.ele('text:命令学')  # 使用文本内容查找元素
text = lnk.text  # 获取元素文本
href = lnk.attr('href')  # 获取元素属性值

print(text, href, '\n')

# 简洁模式串联查找
text = page('@id:footer-left')('css:>div')('text:命令学').text
print(text)
```

输出：

```
Git 命令学习 https://oschina.gitee.io/learn-git-branching/

Git 命令学习
```

**下载文件**

```python
url = 'https://www.baidu.com/img/flexible/logo/pc/result.png'
save_path = r'C:\download'
page.download(url, save_path)
```

# 使用方法

***

## 安装及导入

**安装**

```
pip install DrissionPage
```

只支持 python3.6 及以上版本，driver 模式目前只支持 chrome，目前只在 Windows 环境下作了测试。  
若要使用 driver 模式，须配置 chrome 和 **对应版本** 的 chromedriver。[[chromedriver下载]](http://npm.taobao.org/mirrors/chromedriver)  
easy_set 工具中的 get_match_driver() 方法可自动识别 chrome 版本并下载匹配的 driver 。

**导入模块**

```python
from DrissionPage import MixPage
```

## 初始化

> 如果你只使用 session 模式，可跳过本节。

使用 selenium 前，必须配置 chrome.exe 和 chromedriver.exe 的路径，并确保它们版本匹配。  
新版本中，运行时若程序发现它们版本不匹配，会自动下载对应版本并设置路径。如无特殊须要，无须手动干预。

配置路径有四种方法：

- 直接运行，让程序自动完成设置（推荐）
- 使用 easy_set 工具的 get_match_driver() 方法
- 将路径写入本库的 ini 文件
- 将两个路径写入系统变量
- 在代码中填写路径

**自动设置**

新版本中，您无须做任何配置，只要直接运行程序，程序会获取系统中 chrome.exe 路径，并自动下载版本匹配的 chromedriver.exe。全程无感。如须自行设置所使用的 chrome.exe，可用下面的方法。

**使用 get_match_driver()  方法**

若你选择这种方式，请在第一次使用前，运行以下代码，程序会自动检测电脑安装的 chrome 版本，下载对应 driver，并记录到 ini 文件。

```python
from DrissionPage.easy_set import get_match_driver
get_match_driver()
```

输出：

```
ini文件中chrome.exe路径 D:\Google Chrome\Chrome\chrome.exe 

version 75.0.3770.100 

chromedriver_win32.zip
Downloading to: D:\python\projects\DrissionPage\DrissionPage
 100% Success.

解压路径 D:\python\projects\chromedriver.exe 

正在检测可用性...
版本匹配，可正常使用。
```

然后就可以开始使用了。

若你想使用指定的 chrome.exe（绿色版），及指定 ini 文件和 chromedriver.exe 的保存路径，可以这样写：

```python
get_match_driver(ini_path='ini文件路径', save_path='保存路径', chrome_path='chrome路径')
```

Tips：当指定 chrome_path 时，检测成功后程序会把这个路径写进 ini 文件。

**使用 set_paths() 方法**

若上一种方法失败，可自行下载 chromedriver.exe，然后运行以下代码，把路径记录到 ini 文件中。

```python
from DrissionPage.easy_set import set_paths
driver_path = 'D:\\chrome\\chromedriver.exe'  # 你的 chromedriver.exe 路径，若不填写会在系统变量中查找
chrome_path = 'D:\\chrome\\chrome.exe'  # 你的 chrome.exe 路径，若不填写会在系统变量中查找
set_paths(driver_path, chrome_path)
```

该方法还会检查 chrome 和 chromedriver 版本是否匹配，显示：

```
正在检测可用性...
版本匹配，可正常使用。
```

或

```
出现异常：
Message: session not created: Chrome version must be between 70 and 73
  (Driver info: chromedriver=73.0.3683.68 (47787ec04b6e38e22703e856e101e840b65afe72),platform=Windows NT 10.0.19631 x86_64)
可执行easy_set.get_match_driver()自动下载匹配的版本。
或自行从以下网址下载：https://chromedriver.chromium.org/downloads
```

检查通过后，即可正常使用 driver 模式。

除了上述两个路径，该方法还可以设置以下路径：

```python
debugger_address  # 调试浏览器地址，如：127.0.0.1:9222
download_path  # 下载文件路径
tmp_path  # 临时文件夹路径
user_data_path # 用户数据路径
cache_path # 缓存路径
```

Tips：

- 不同项目可能须要不同版本的 chrome 和 chromedriver，你还可保存多个 ini 文件，按须使用。
- 推荐使用绿色版 chrome，并手动设置路径，避免浏览器升级造成与 chromedriver 版本不匹配。
- 调试项目时推荐设置 debugger_address，使用手动打开的浏览器，再用程序接管，好处多多。

**其它方法**

若你不想使用 ini 文件（如要打包项目时），可在系统路径写入以上两个路径，或在程序中填写。后者的使用方法见下一节。

## Drission 对象

> 创建的步骤不是必须，若想快速上手，可跳过本节。MixPage 会自动创建该对象。

Drission 对象用于管理 driver 和 session 对象。在多个页面协同工作时，Drission 对象用于传递驱动器，使多个页面类可控制同一个浏览器或 Session 对象。  
可直接读取 ini 文件配置信息创建，也可以在初始化时传入配置信息。

```python
# 由默认 ini 文件创建
drission = Drission()  

# 由其它 ini 文件创建
drission = Drission(ini_path='D:\\settings.ini')  

# 不从 ini 文件创建
drission = Drission(read_file=False)
```

若要手动传入配置（不使用 ini 文件）：

```python
from DrissionPage.config import DriverOptions

# 创建 driver 配置对象，read_file = False 表示不读取 ini 文件
do = DriverOptions(read_file=False)  

# 设置路径，若已在系统变量设置，可忽略
do.set_paths(chrome_path='D:\\chrome\\chrome.exe',
             driver_path='D:\\chrome\\chromedriver.exe')  

# 用于 s 模式的设置
session_options = {'headers': {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)'}}

# 代理设置，可选
proxy = {'http': '127.0.0.1:1080', 'https': '127.0.0.1:1080'}

# 传入配置，driver_options 和 session_options 都是可选的，须要使用对应模式才须要传入
drission = Drission(driver_options, session_options, proxy=proxy)  
```

DriverOptions 和 SessionOptions 用法详见下文。

## MixPage 对象

MixPage 页面对象封装了常用的网页操作，并实现 driver 和 session 模式之间的切换。  
MixPage 须控制一个 Drission 对象并使用其中的 driver 或 session，如没有传入，MixPage 会自己创建一个（使用传入的配置信息或从默认 ini 文件读取）。

Tips: 多对象协同工作时，可将一个 MixPage 中的 Drission 对象传递给另一个，使多个对象共享登录信息或操作同一个页面。

**创建对象**

创建对象方式有3种：简易、传入 Drission 对象、传入配置。可根据实际需要选择。

```python
# 简易创建方式，以 ini 文件默认配置自动创建 Drission 对象
page = MixPage()
page = MixPage('s')

# 以传入 Drission 对象创建
page = MixPage(drission)
page = MixPage(drission, mode='s', timeout=5)  # session 模式，等待时间5秒（默认10秒）

# 传入配置信息，MixPage 根据配置在内部创建 Drission
page = MixPage(driver_options=do, session_options=so)  # 默认 d 模式
```

**访问网页**

```python
# 默认方式
page.get(url)
page.post(url, data, **kwargs)  # 只有 session 模式才有 post 方法

# 指定重试次数和间隔
page.get(url, retry=5, interval=0.5)
```

Tips：若连接出错，程序会自动重试2次，可指定重试次数和等待间隔。

**切换模式**

在 s 和 d 模式之间切换，切换时会自动同步 cookies 和正在访问的 url。

```python
page.change_mode(go=False)  # go 为 False 表示不跳转 url
```

Tips：使用某种模式独有的方法时会自动跳转到该模式。

**页面属性**

```python
page.url  # 当前访问的 url
page.mode  # 当前模式
page.drission  # 当前使用的 Dirssion 对象
page.driver  # 当前使用的 WebDirver 对象
page.session  # 当前使用的 Session 对象
page.cookies  # 获取 cookies 信息
page.html  # 页面源代码
page.title  # 当前页面标题

# d 模式独有：
page.tabs_count  # 返回标签页数量
page.tab_handles  # 返回所有标签页 handle 列表
page.current_tab_num  # 返回当前标签页序号
page.current_tab_handle  # 返回当前标签页 handle
```

**页面操作**

调用只属于 d 模式的方法，会自动切换到 d 模式。详细用法见 APIs。

```python
page.set_cookies()  # 设置cookies
page.get_cookies()  # 获取 cookies，可以 list 或 dict 方式返回
page.change_mode()  # 切换模式，会自动复制 cookies
page.cookies_to_session()  # 从 WebDriver 对象复制 cookies 到 Session 对象
page.cookies_to_driver()  # 从 Session 对象复制 cookies 到 WebDriver 对象
page.get(url, retry, interval, **kwargs)  # 用 get 方式访问网页，可指定重试次数及间隔时间
page.ele(loc_or_ele, timeout)  # 获取符合条件的第一个元素、节点或属性
page.eles(loc_or_ele, timeout)  # 获取所有符合条件的元素、节点或属性
page.download(url, save_path, rename, file_exists, **kwargs)  # 下载文件
page.close_driver()  # 关闭 WebDriver 对象
page.close_session()  # 关闭 Session 对象

# s 模式独有：
page.post(url, data, retry, interval, **kwargs)  # 以 post 方式访问网页，可指定重试次数及间隔时间

# d 模式独有：
page.wait_ele(loc_or_ele, mode, timeout)  # 等待元素从 dom 删除、显示、隐藏
page.run_script(js, *args)  # 运行 js 语句
page.create_tab(url)  # 新建并定位到一个标签页,该标签页在最后面
page.to_tab(num_or_handle)  # 跳转到标签页
page.close_current_tab()  # 关闭当前标签页
page.close_other_tabs(num_or_handles)  # 关闭其它标签页
page.to_iframe(iframe)  # 切入 iframe
page.screenshot(path)  # 页面截图
page.scroll_to_see(element)  # 滚动直到某元素可见
page.scroll_to(mode, pixel)  # 按参数指示方式滚动页面，可选滚动方向：'top', 'bottom', 'rightmost', 'leftmost', 'up', 'down', 'left', 'right'
page.refresh()  # 刷新当前页面
page.back()  # 浏览器后退
page.et_window_size(x, y)  # 设置浏览器窗口大小，默认最大化
page.check_page()  # 检测页面是否符合预期
page.chrome_downloading()  # 获取 chrome 正在下载的文件列表
page.process_alert(mode, text)  # 处理提示框
```

**cookies 的使用**

MixPage 支持获取和设置 cookies，具体使用方法如下：

```python
page.cookies  # 以字典形式返回 cookies，只会返回当前域名可用的 cookies
page.get_cookies(as_dict=False)  # 以列表形式返回当前域名可用 cookies，每个 cookie 包含所有详细信息
page.get_cookies(all_domains=True)  # 以列表形式返回所有 cookies，只有 s 模式有效
page.set_cookies(cookies)  # 设置 cookies，可传入 RequestsCookieJar, list, tuple, str, dict
```

Tips:

- d 模式设置 cookies 后要刷新页面才能看到效果。
- s 模式可在 ini 文件、SessionOptions、配置字典中设置 cookies，在 MixPage 初始化时即可传入，d 模式只能用 set_cookies() 函数设置。

## 查找元素

ele() 返回第一个符合条件的元素，eles() 返回所有符合条件的元素列表。  
你可在页面对象或元素对象下使用这两个函数，以查找下级元素。

page.eles() 和 element.eles() 查找返回符合条件的所有元素列表。

说明：

- 元素查找超时默认为10秒，超时或找到元素时停止等待，你也可以按需要设置。
- 下面的查找语句中，冒号 : 表示模糊匹配，等号 = 表示精确匹配
- 可用查询字符串或 selenium 原生的 loc 元组（s 模式也能用）查找元素
- 查询字符串有 @属性名、tag、text、xpath、css、.、# 等7种方法

```python
# 根据属性查找，@ 后面可跟任意属性
page.ele('@id:ele_id', timeout=2)  # 查找 id 为 ele_id 的元素，设置等待时间2秒  
page.eles('@class')  # 查找所有拥有 class 属性的元素
page.eles('@class:class_name')  # 查找所有 class 含有 ele_class 的元素 
page.eles('@class=class_name')  # 查找所有 class 等于 ele_class 的元素 

# 根据 class 或 id 查找
page.ele('#ele_id')  # 等价于 page.ele('@id=ele_id')
page.ele('#:ele_id')  # 等价于 page.ele('@id:ele_id')
page.ele('.ele_class')  # 等价于 page.ele('@class=ele_class')
page.ele('.:ele_class')  # 等价于 page.ele('@class:ele_class')

# 根据 tag name 查找
page.ele('tag:li')  # 查找第一个 li 元素  
page.eles('tag:li')  # 查找所有 li 元素  

# 根据 tag name 及属性查找
page.ele('tag:div@class=div_class')  # 查找 class 为 div_class 的 div 元素
page.ele('tag:div@class:ele_class')  # 查找 class 含有 ele_class 的 div 元素
page.ele('tag:div@class=ele_class')  # 查找 class 等于 ele_class 的 div 元素
page.ele('tag:div@text():search_text')  # 查找文本含有 search_text 的 div 元素
page.ele('tag:div@text()=search_text')  # 查找文本等于 search_text 的 div 元素

# 根据文本内容查找
page.ele('search text')  # 查找包含传入文本的元素  
page.eles('text:search text')  # 如文本以 @、tag:、css:、xpath:、text: 开头，则应在前加上 text: 避免冲突  
page.eles('text=search text')  # 文本等于 search_text 的元素

# 根据 xpath 或 css selector 查找
page.eles('xpath://div[@class="ele_class"]')
page.eles('css:div.ele_class')

# 根据 loc 查找
loc1 = By.ID, 'ele_id'
loc2 = By.XPATH, '//div[@class="ele_class"]'
page.ele(loc1)
page.ele(loc2)

# 查找下级元素
element = page.ele('@id:ele_id')
element.ele('@class:class_name')  # 在 element 下级查找第一个 class 为 ele_class 的元素
element.eles('tag:li')  # 在 ele_id 下级查找所有li元素

# 根据位置查找
element.parent  # 父元素  
element.next  # 下一个兄弟元素  
element.prev  # 上一个兄弟元素  

# 获取 shadow-root，把它作为元素对待。只支持 open 的 shadow-root
ele1 = element.shadow_root.ele('tag:div')

# 串连查找
page.ele('@id:ele_id').ele('tag:div').next.ele('some text').eles('tag:a')

# 简化写法
eles = page('@id:ele_id')('tag:div').next('some text').eles('tag:a')
ele2 = ele1('tag:li').next('some text')
```

## 获取元素属性

```python
element.html  # 返回元素 outerHTML
element.inner_html  # 返回元素 innerHTML
element.tag  # 返回元素 tag name
element.text  # 返回元素 innerText 值
element.link  # 返回元素 href 或 src 绝对 url
element.texts()  # 返回元素内所有直接子节点的文本，包括元素和文本节点，可指定只返回文本节点
element.attrs  # 返回元素所有属性的字典
element.attr(attr)  # 返回元素指定属性的值
element.css_path  # 返回元素绝对 css 路径
element.xpath  # 返回元素绝对 xpath 路径
element.parent  # 返回元素父元素
element.next  # 返回元素后一个兄弟元素
element.prev  # 返回元素前一个兄弟元素
element.parents(num)  # 返回第 num 级父元素
element.nexts(num, mode)  # 返回后面第几个元素或节点
element.prevs(num, mode)  # 返回前面第几个元素或节点
element.ele(loc_or_str, timeout)  # 返回当前元素下级第一个符合条件的子元素、属性或节点文本
element.eles(loc_or_str, timeout)  # 返回当前元素下级所有符合条件的子元素、属性或节点文本

# d 模式独有：
element.before  # 获取伪元素 before 内容
element.after  # 获取伪元素 after 内容
element.is_valid  # 用于判断元素是否还在dom中
element.size  # 获取元素大小
element.location  # 获取元素位置
element.shadow_root  # 获取元素下的 ShadowRoot 元素
element.get_style_property(style, pseudo_ele)  # 获取元素样式属性值，可获取伪元素的
element.is_selected()  # 返回元素是否被选中
element.is_enabled()  # 返回元素是否可用
element.is_displayed()  # 返回元素是否可见
```

## 元素操作

元素操作为 d 模式独有，调用以下方法会自动切换到 d 模式。

```python
element.click(by_js)  # 点击元素，可选择是否用 js 方式点击
element.input(value)  # 输入文本
element.run_script(js)  # 对元素运行 JavaScript 脚本
element.submit()  # 提交
element.clear()  # 清空元素
element.screenshot(path, filename)  # 对元素截图
element.select(text)  # 根据文本选择下拉列表
element.set_attr(attr, value)  # 设置元素属性值
element.remove_attr(attr)  # 删除属性
element.drag(x, y, speed, shake)  # 拖动元素相对距离，可设置速度和是否随机抖动
element.drag_to(ele_or_loc, speed, shake)  # 拖动元素到另一个元素或某个坐标，可设置速度和是否随机抖动
element.hover()  # 在元素上悬停鼠标
```

## shadow-dom 操作

d 模式独有，支持获取 shadow-root 及内部元素，获取到的 shadow-root 元素类型为 ShadowRootElement，用法和正常元素类似，但功能有所简化。

**注意：**

- 只能获取 open 的 shadow-root
- 查找 shadow-root 内部元素不能使用 xpath 方式

获取依附在普通元素内的 shadow-root 元素
```python
shadow_root_element = element.shadow_root  # element 为含有 shadow-root 的普通元素
```

属性及方法

```python
shadow_root_element.tag  # 返回 'shadow-root'
shadow_root_element.html  # html 内容
shadow_root_element.parent  # 父元素
shadow_root_element.next  # 下一个兄弟元素

shadow_root_element.parents(num)  # 获取向上 num 级父元素
shadow_root_element.nexts(num)  # 获取向后 num 个兄弟元素
shadow_root_element.ele(loc_or_str)  # 获取第一个符合条件的内部元素
shadow_root_element.eles(loc_or_str)  # 获取全部符合条件的内部元素
shadow_root_element.run_scrpit(js_text)  # 运行 js 脚本
shadow_root_element.is_enabled()  # 返回元素是否可用
shadow_root_element.is_valid()  # 返回元素是否还在 dom 内
```

**Tips:** 以上属性或方法获取到的元素是普通的 DriverElement，用法参考上文所述。

## 对接 selenium 及 requests

DrissionPage 代码可与 selenium 及 requests 代码无缝拼接。既可直接使用 selenium 的 WebDriver 对象，也可导出自身的 WebDriver 给 selenium 代码使用。requests 的
Session 对象也可直接传递。使已有项目的迁移非常方便。

**selenium 转 DrissionPage**

```python
driver = webdriver.Chrome()
driver.get('https://www.baidu.com')

page = MixPage(Drission(driver))  # 把 driver 传递给 Drission，创建 MixPage 对象
print(page.title)  # 打印结果：百度一下，你就知道
```

**DrissionPage 转 selenium**

```python
page = MixPage()
page.get('https://www.baidu.com')

driver = page.driver  # 从 MixPage 对象中获取 WebDriver 对象
print(driver.title)  # 打印结果：百度一下，你就知道
element = driver.find_element_by_xpath('//div')  # 使用 selenium 原生功能
```

**requests 转 DrissionPage**

``` python
session = requets.Session()
drission = Drission(session_or_options=session)
page = MixPage(drission, mode='s')

page.get('https://www.baidu.com')
```

**DrissionPage 转 requests**

```python
page = MixPage('s')
session = page.session

response = session.get('https://www.baidu.com')
```

## requests 功能使用

**连接参数**

除了在创建时传入配置信息及连接参数，如有必要，s 模式下也可在每次访问网址时设置连接参数。

```python
headers = {'User-Agent': '......', }
cookies = {'name': 'value', }
proxies = {'http': '127.0.0.1:1080', 'https': '127.0.0.1:1080'}
page.get(url, headers=headers, cookies=cookies, proxies=proxies)
```

Tips：

- 如果连接参数内没有指定，s 模式会根据当前域名自动填写 Host 和 Referer 属性
- 在创建 MixPage 时传入的 Session 配置是全局有效的

**Response 对象**

requests 获取到的 Response 对象存放在 page.response，可直接使用。如：

```python
print(page.response.status_code)
print(page.response.headers)
```

## 下载文件

selenium 缺乏对浏览器下载文件的有效管理，难以进行检测下载状态、重命名、失败管理。  
使用 requests 下载文件能较好实现以上功能，但代码较为繁琐。  
因此 DrissionPage 封装了 download 方法，整合了两者优点，可从 selenium 获取登录信息，用 requests 进行下载。  
弥补了 selenium 的不足，使下载简洁高效。

**功能**

- 指定下载路径
- 重命名文件，可不填写扩展名，程序自动补充
- 存在同名文件时，可选择重命名、覆盖、跳过等处理方式
- 显示下载进度
- 支持 post 方式
- 支持自定义连接参数

**演示**

```python
url = 'https://www.baidu.com/img/flexible/logo/pc/result.png'  # 文件 url
save_path = r'C:\download'  # 存放路径

# 重命名为img.png，存在重名时自动在文件名末尾加上序号，显示下载进度
page.download(url, save_path, 'img', 'rename', show_msg=True)
```

## Chrome 设置

chrome 的配置很繁琐，为简化使用，本库提供了常用配置的设置方法。

**DriverOptions 对象**

DriverOptions 对象继承自 selenium.webdriver.chrome.options 的 Options 对象，在其基础上增加了以下方法：

```python
options.remove_argument(value)  # 删除某 argument 值
options.remove_experimental_option(key)  # 删除某 experimental_option 设置
options.remove_all_extensions()  # 删除全部插件
options.save()  # 保存当前打开的 ini 文件
options.save('D:\\settings.ini')  # 保存到指定路径 ini 文件
options.save('default')  # 保存当前设置到默认 ini 文件
options.set_argument(arg, value)  # 设置 argument 属性
options.set_headless(on_off)  # 设置是否使用无界面模式
options.set_no_imgs(on_off)  # 设置是否加载图片
options.set_no_js(on_off)  # 设置是否禁用 js
options.set_mute(on_off)  # 设置是否静音
options.set_user_agent(user_agent)  # 设置 user agent
options.set_proxy(proxy)  # 设置代理地址
options.set_paths(driver_path, chrome_path, debugger_address, download_path, user_data_path, cache_path)  # 设置浏览器相关的路径
```

**使用方法**

```python
do = DriverOptions()  # 读取默认 ini 文件创建 DriverOptions 对象
do = DriverOptions('D:\\settings.ini')  # 读取指定 ini 文件创建 DriverOptions 对象
do = DriverOptions(read_file=False)  # 不读取 ini 文件，创建空的 DriverOptions 对象

do.set_headless(False)  # 显示浏览器界面
do.set_no_imgs(True)  # 不加载图片
do.set_paths(driver_path='D:\\chromedriver.exe', chrome_path='D:\\chrome.exe')  # 设置路径
do.set_headless(False).set_no_imgs(True)  # 支持链式操作

drission = Drission(driver_options=do)  # 用配置对象创建 Drission 对象
page = MixPage(driver_options=do)  # 用配置对象创建 MixPage 对象

do.save()  # 保存当前打开的 ini 文件
do.save('D:\\settings.ini')  # 保存到指定的 ini 文件
do.save('default')  # 保存当前设置到默认 ini 文件
```

## Session 设置

**SessionOPtions 对象**

SessionOptions 对象用于管理 Session 的配置信息。它创建时默认读取默认 ini 文件配置信息，也可手动设置所需信息。

可配置的属性：

headers、cookies、auth、proxies、hooks、params、verify、cert、adapters、stream、trust_env、max_redirects。

**Tips:** cookies 可接收 dict、list、tuple、str、RequestsCookieJar 等格式的信息。

**使用方法**

```python
so = SessionOptions()  # 读取默认 ini 文件创建 SessionOptions 对象
so = SessionOptions('D:\\settings.ini')  # 读取指定 ini 文件创建 SessionOptions 对象
so = SessionOptions(read_file=False)  # 不读取 ini 文件，创建空的 SessionOptions 对象

so.cookies = ['key1=val1; domain=xxxx', 'key2=val2; domain=xxxx']  # 设置 cookies
so.headers = {'User-Agent': 'xxxx', 'Accept-Charset': 'xxxx'}
so.set_a_header('Connection', 'keep-alive')

drission = Drission(session_options=so)  # 用配置对象创建 Drission 对象
page = MixPage(session_options=so)  # 用配置对象创建 MixPage 对象

so.save()  # 保存当前打开的 ini 文件
so.save('D:\\settings.ini')  # 保存到指定的 ini 文件
so.save('default')  # 保存当前设置到默认 ini 文件
```

## 保存配置

因 chrome 和 headers 配置繁多，故设置一个 ini 文件专门用于保存常用配置，你可使用 OptionsManager 对象获取和保存配置，用 DriverOptions 对象修改 chrome 配置。你也可以保存多个 ini
文件，按不同项目须要调用。

Tips：建议把常用配置文件保存到别的路径，以防本库升级时配置被重置。

**ini 文件内容**

ini 文件默认拥有三部分配置：paths、chrome_options、session_options，初始内容如下。

```ini
[paths]
; chromedriver.exe路径
chromedriver_path =
; 临时文件夹路径，用于保存截图、文件下载等
tmp_path =

[chrome_options]
; 已打开的浏览器地址和端口，如127.0.0.1:9222
debugger_address =
; chrome.exe路径
binary_location =
; 配置信息
arguments = [
            ; 静音
            '--mute-audio',
            ; 不使用沙盒
            '--no-sandbox',
            ; 谷歌文档提到需要加上这个属性来规避bug
            '--disable-gpu',
            ; 忽略警告
            'ignore-certificate-errors',
            ; 不显示信息栏
            '--disable-infobars'
            ]
; 插件
extensions = []
; 实验性配置
experimental_options = {
                       'prefs': {
                       ; 下载不弹出窗口
                       'profile.default_content_settings.popups': 0,
                       ; 无弹窗
                       'profile.default_content_setting_values': {'notifications': 2},
                       ; 禁用PDF插件
                       'plugins.plugins_list': [{"enabled": False, "name": "Chrome PDF Viewer"}]
                       },
                       ; 设置为开发者模式，防反爬虫
                       'excludeSwitches': ["enable-automation"],
                       'useAutomationExtension': False
                       }

[session_options]
headers = {
          "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "Connection": "keep-alive",
          "Accept-Charset": "utf-8;q=0.7,*;q=0.7"
          }
```

**OptionsManager 对象**

OptionsManager 对象用于读取、设置和保存配置。

```python
manager.paths  # 以字典形式返回路径设置
manager.chrome_options  # 以字典形式返回chrome设置
manager.session_options  # 以字典形式返回session设置
manager.get_value(section, item)  # 获取某个配置的值
manager.get_option(section)  # 以字典格式返回配置全部属性
manager.set_item(section, item, value)  # 设置配置属性
manager.manager.save()  # 保存当前打开的 ini 文件
manager.save('D:\\settings.ini')  # 保存到指定路径 ini 文件
manager.save('default')  # 保存当前设置到默认 ini 文件
```

**使用示例**

```python
from DrissionPage.configs import *

options_manager = OptionsManager()  # 从默认ini文件创建OptionsManager对象
options_manager = OptionsManager('D:\\settings.ini')  # 从其它ini文件创建OptionsManager对象
driver_path = options_manager.get_value('paths', 'chromedriver_path')  # 读取路径信息
options_manager.save()  # 保存当前打开的 ini 文件
options_manager.save('D:\\settings.ini')  # 保存到指定路径 ini 文件

drission = Drission(ini_path='D:\\settings.ini')  # 使用指定 ini 文件创建对象
```

## easy_set 方法

可快速地修改常用设置的方法。全部用于 driver 模式的设置。调用 easy_set 方法会修改默认 ini 文件相关内容。

```python
get_match_driver()  # 识别chrome版本并自动下载匹配的chromedriver.exe
show_settings()  # 打印所有设置
set_headless(True)  # 开启 headless 模式
set_no_imgs(True)  # 开启无图模式
set_no_js(True)  # 禁用 JS
set_mute(True)  # 开启静音模式
set_user_agent('Mozilla/5.0 (Macintosh; Int......')  # 设置 user agent
set_proxy('127.0.0.1:8888')  # 设置代理
set_paths(paths)  # 见 [初始化] 一节
set_argument(arg, value)  # 设置属性，若属性无值（如'zh_CN.UTF-8'），value 为 bool 表示开关；否则value为str，当 value为''或 False，删除该属性项
check_driver_version()  # 检查chrome和chromedriver版本是否匹配
```

## POM 模式

MixPage 封装了常用的页面操作，可方便地用于扩展。

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

## DriverPage 和 SessionPage

如果无须切换模式，可根据需要只使用 DriverPage 或 SessionPage，用法和 MixPage 一致。

```python
from DrissionPage.session_page import SessionPage
from DrissionPage.drission import Drission

session = Drission().session
page = SessionPage(session)  # 传入 Session 对象
page.get('http://www.baidu.com')
print(page.ele('@id:su').text)  # 输出：百度一下

driver = Drission().driver
page = DriverPage(driver)  # 传入 Driver 对象
page.get('http://www.baidu.com')
print(page.ele('@id:su').text)  # 输出：百度一下
```

# 版本历史

***

请在 Wiki中查看：[点击查看版本历史](https://gitee.com/g1879/DrissionPage/wikis/%E7%89%88%E6%9C%AC%E5%8E%86%E5%8F%B2?sort_id=3201403)

# APIs

***

请在 Wiki中查看：[点击查看APIs](https://gitee.com/g1879/DrissionPage/wikis/Drission%20%E7%B1%BB?sort_id=3159323)

