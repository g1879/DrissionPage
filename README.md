# 简洁！易用 ！方便！

# 简介

***

DrissionPage，即 driver 和 session 组合而成的 page。  
是个基于 python 的 Web 自动化操作集成工具。  
它实现了 selenium 和 requests 之间的无缝切换。  
可以兼顾 selenium 的便利性和 requests 的高效率。  
它集成了页面常用功能，两种模式系统一致的 API，使用便捷。  
它用 POM 模式封装了页面元素常用的方法，适合自动化操作功能扩展。  
更棒的是，它的使用方式非常简洁和人性化，代码量少，对新手友好。

**示例地址：** [使用DrissionPage的网页自动化及爬虫示例](https://gitee.com/g1879/DrissionPage-demos)

**交流QQ群：**  897838127            **联系邮箱：**  g1879@qq.com

## 背景

requests 爬虫面对要登录的网站时，要分析数据包、JS 源码，构造复杂的请求，往往还要应付验证码、JS 混淆、签名参数等反爬手段，门槛较高。若数据是由 JS 计算生成的，还须重现计算过程，体验不好，开发效率不高。  
使用 selenium，可以很大程度上绕过这些坑，但 selenium 效率不高。因此，这个库将 selenium 和 requests 合而为一，不同须要时切换相应模式，并提供一种人性化的使用方法，提高开发和运行效率。  
除了合并两者，本库还以网页为单位封装了常用功能，简化了 selenium 的操作和语句，在用于网页自动化操作时，减少考虑细节，专注功能实现，使用更方便。  
一切从简，尽量提供简单直接的使用方法，对新手更友好。

# 特性和亮点

***

作者有多年自动化和爬虫经验，踩过无数坑，总结出的经验全写到这个库里了。内置了N多实用功能，对常用功能作了整合和优化。

## 特性

- 代码高度集成，以简洁的代码为第一追求。
- 页面对象可在 selenium 和 requests 模式间任意切换，保留登录状态。
- 极简单但强大的元素定位语法，支持链式操作，代码极其简洁。
- 两种模式提供一致的 API，使用体验一致。
- 人性化设计，集成众多实用功能，大大降低开发工作量。

## 亮点

- 每次运行程序可以反复使用已经打开的浏览器。如手动设置网页到某个状态，再用程序接管，或手动处理登录，再用程序爬内容。无须每次运行从头启动浏览器，超级方便。
- 使用 ini 文件保存常用配置，自动调用，也提供便捷的设置api，远离繁杂的配置项。
- 极致简明的定位语法，支持直接按文本定位元素，支持直接获取前后兄弟元素和父元素等。
- 强大的下载工具，操作浏览器时也能享受快捷可靠的下载功能。
- 下载工具支持多种方式处理文件名冲突、自动创建目标路径、断链重试等。
- 访问网址带自动重试功能，可设置间隔和超时时间。
- 访问网页能自动识别编码，无须手动设置。
- 链接参数默认自动生成 Host 和 Referer 属性。
- 可随时直接隐藏或显示浏览器进程窗口，非 headless 或最小化。
- 可自动下载合适版本的 chromedriver，免去麻烦的配置。
- d 模式查找元素内置等待，可任意设置全局等待时间或单次查找等待时间。
- 点击元素集成 js 点击方式，一个参数即可切换点击方式。
- 点击支持失败重试，可用于保证点击成功、判读网页遮罩层是否消失等。
- 输入文本能自动判断是否成功并重试，避免某些情况下输入或清空失效的情况。
- d 模式下支持全功能的 xpath，可直接获取元素的某个属性，selenium 原生无此功能。
- 支持直接获取 shadow-root，和普通元素一样操作其下的元素。
- 支持直接获取 after 和 before 伪元素的内容。
- 可以在元素下直接使用 > 以 css selector 方式获取当前元素直接子元素。原生不支持这种写法。
- 可简单地使用 lxml 来解析 d 模式的页面或元素，爬取复杂页面数据时速度大幅提高。
- 输出的数据均已转码及处理基本排版，减少重复劳动。
- 可方便地与 selenium 或 requests 原生代码对接，便于项目迁移。
- 使用 POM 模式封装，可直接用于测试，便于扩展。
- d 模式配置可同时兼容 debugger 和其它参数，原生不能兼容。
- 还有很多这里不一一列举…………

# 简单演示

***

**与 selenium 代码对比**

以下代码实现一模一样的功能，对比两者的代码量：

- 用显性等待方式定位第一个文本包含 some text 的元素

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
shadow_element = element.sr

# 在 shadow_root 下可继续执行查找，获取普通元素
ele = shadow_element.ele('tag:div')
```

- 用 xpath 直接获取属性或文本节点（返回文本）

```python
# 使用 selenium：
相当复杂

# 使用 DrissionPage：
class_name = element('xpath://div[@id="div_id"]/@class')
text = element('xpath://div[@id="div_id"]/text()[2]')
```

- 随时让浏览器窗口消失和显示

```python
# selenium无此功能

# 使用 DrissionPage
page.hide_browser()  # 让浏览器窗口消失
page.show_browser()  # 重新显示浏览器窗口
```

注：本功能只支持 Windows，且须设置了 debugger_address 参数时才能生效

**与 requests 代码对比**

以下代码实现一模一样的功能，对比两者的代码量：

- 获取元素内容

```python
url = 'https://baike.baidu.com/item/python'

# 使用 requests：
from lxml import etree
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
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
page.download(url, save_path, 'img')  # 支持重命名，处理文件名冲突，自动创建目标文件夹
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

**获取并显示元素属性**

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

# 使用方法

***

请在 Wiki中查看：[点击跳转到wiki](https://gitee.com/g1879/DrissionPage/wikis/%E5%AE%89%E8%A3%85%E4%B8%8E%E5%AF%BC%E5%85%A5?sort_id=3201408)

# 版本历史

***

请在 Wiki中查看：[点击查看版本历史](https://gitee.com/g1879/DrissionPage/wikis/%E7%89%88%E6%9C%AC%E5%8E%86%E5%8F%B2?sort_id=3201403)

# APIs

***

请在 Wiki中查看：[点击查看APIs](https://gitee.com/g1879/DrissionPage/wikis/Drission%20%E7%B1%BB?sort_id=3159323)

