# DrissionPage

> 当前测试线：**5.0.0b0**。本版本删除 `ChromiumPage`，升级前请阅读下方兼容性告知。

- 官方网站：[https://DrissionPage.cn](https://drissionpage.cn)
- 项目地址：[GitHub](https://github.com/g1879/DrissionPage) | [Gitee](https://gitee.com/g1879/DrissionPage) | [GitCode](https://gitcode.com/g1879/DrissionPage)
- 英文文档：[README_EN.md](./README_EN.md)
- 更新日志：[CHANGELOG.md](./CHANGELOG.md)

## 快速目录

### 升级与版本

- [5.0.0b0 兼容性告知](#500b0-兼容性告知)
- [5.0.0b0 迭代内容](#500b0-迭代内容)
- [迁移速览](#迁移速览)
- [历史功能说明](#历史功能说明)
- [完整更新日志](./CHANGELOG.md)
- [English README](./README_EN.md)

### 项目说明

- [概述](#概述)
- [运行环境](#运行环境)
- [如何使用](#如何使用)
- [理念](#理念)
- [特性和亮点](#特性和亮点)
- [使用条款](#使用条款)

---

## 5.0.0b0 兼容性告知

由于测试版升级功能较多，并且底层实现进行了较大规模重构，项目不再继续发布 4.2 正式版，直接进入 5.0 测试线。

5.0.0b0 是兼容性断点版本。随着新功能增加，旧 `ChromiumPage` 抽象与新版浏览器、标签页、上下文和监听模型的冲突越来越多，因此本版本彻底删除 `ChromiumPage`。升级前请检查项目中与浏览器入口、标签页管理、定位符、Edge 启动方式相关的代码。

详细变更见：[CHANGELOG.md](./CHANGELOG.md)。

<a id="历史功能说明"></a>

## 历史功能说明

- [4.2 功能说明](http://drissionpage.cn/features/4.2)
- [4.1 功能说明](http://drissionpage.cn/features/4.1)
- [4.0 功能说明](http://drissionpage.cn/features/4)
- [3.x 功能说明](http://drissionpage.cn/features/3)

## 5.0.0b0 迭代内容

相比 4.2.0b20，5.0.0b0 的主要变化如下：

### 破坏性变更

- 彻底删除 `ChromiumPage`。
- 定位符仅以 `.` 或 `#` 开头时按 CSS 匹配；后接 `=`、`:`、`^`、`$` 时才按 DrissionPage 定位符逻辑处理。
- `ChromiumOptions.set_browser_path()` 删除 `edge` 参数。

### 新增与恢复

- 适配 `<object>` 元素。
- `get_tabs()` 补回 `as_id` 参数。
- `ChromiumOptions` 增加 `use_edge()` 方法。

### 行为调整

- `tab_ids` 属性忽略插件标签页。
- `get_tab()` 的 `id_or_num` 参数为数字时，后面的 `title`、`url`、`tab_type` 三个条件参数现在会生效。

### 修复

- 修复监听 WebSocket 时某些情况下获取不到数据包的问题。
- 修复控制手机 Edge 创建 tab 时卡住的问题。

## 迁移速览

### 从 `ChromiumPage` 迁移到 `Chromium`

旧写法：

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://example.com')
```

新写法：

```python
from DrissionPage import Chromium

browser = Chromium()
tab = browser.latest_tab
tab.get('https://example.com')
```

### Edge 启动方式

旧写法：

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions().set_browser_path(edge=True)
```

新写法：

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions().use_edge()
```

### 定位符检查

如果旧代码依赖 `.name` 或 `#id` 的 DrissionPage 定位符解析，请重新确认语义。5.0.0b0 中，单独以 `.` 或 `#` 开头的定位符会按 CSS 选择器处理。

---

<a id="概述"></a>

# ✨️ 概述

DrissionPage 是一个基于 Python 的网页自动化工具。

简洁优雅，功能强大。

官方网站：[https://DrissionPage.cn](https://drissionpage.cn)

项目地址：[gitee](https://gitee.com/g1879/DrissionPage)    |    [github](https://github.com/g1879/DrissionPage)     |    [gitcode](https://gitcode.com/g1879/DrissionPage)

您的星星是对我最大的支持💖

---

# ♾️ 交流群

![](https://drissionpage.cn/img/yrx2.png)

与猿人学平哥建立的 DrissionPage AI 逆向微信交流群。
扫码并备注 “dp” 即可申请加入。
交流 AI 逆向，dp 使用方法、实践案例，以及后续功能更新，欢迎加入。

---

## IPWO爬虫代理资源为采集、跨境与测试项目提供支持(免费试用，爬虫使用强烈推荐!!!)

<a href="https://www.ipwo.net/?ref=giteeg1879" target="_blank"><img src="https://drissionpage.cn/img/ad.png"/></a>
<a href="https://www.ipwo.net/?ref=giteeg1879" target="_blank">学习者务必遵循法律！IPWO提供的真实住宅 IP，大幅降低被封禁风险。195 + 国家 / 地区精准定位，轻松应对大型爬虫任务。让爬虫更简单，让数据更安全。戳本信息注册可获得有效保护账号的高匿名ip流量。专属折扣码“<span style="color:red">dpdp</span>”。点击访问IPWO官网</a>

---

<a id="运行环境"></a>

# 🛠 运行环境

支持系统：Windows、Linux、Mac

python 版本：3.6 及以上

支持浏览器：Chromium 内核浏览器(如 Chrome 和 Edge)，electron 应用

---

<a id="如何使用"></a>

# 🛠 如何使用

点击查看：[教程](https://drissionpage.cn/tutorials/xingqiu)

---

## DolOffer

<img src="https://drissionpage.cn/img/doloffer.png" alt="DolOffer" width=300/>

感谢 DolOffer 对本项目的支持！DolOffer 是一个专注于数字产品推荐与优惠分享的平台，帮助用户快速发现值得关注的工具、服务和限时福利。平台提供 YouTube Premium、Claude、ChatGPT Plus、Spotify、Apple Music 等多种热门订阅服务，价格低至官方价的 3 折甚至更低，正版稳定，售后无忧。
现在通过我们的专属链接注册，并在充值时输入优惠码 AI8888，即可额外享受 9 折优惠。

点击查看：<a href="https://doloffer.com/" target="_blank" >🔸官网</a> <a href="https://github.com/Doloffer-g/guide" target="_blank" >🔸详细介绍</a>

<a href="https://www.lajiaohttp.com/?kwd=hyj-dp" target="_blank"><img src="https://drissionpage.cn/img/lajiao.png"/></a>
<a href="https://www.lajiaohttp.com/?kwd=hyj-dp" target="_blank">辣椒HTTP｜真实纯净家庭住宅IP｜爬虫/跨境/多账号必备！|行业底价超高性价比方案
<br/>
🔥新用户免费试用（最高领10GB），企业也支持测试哦！
💰动态IP仅3.8元/GB起｜静态长效9.9元/个/7天起
<br/>
🌍190+国家/地区｜城市级精准定位｜千万级纯净住宅IP池｜每日更新10万+｜双ISP冗余自动切换｜99.9%连通率｜响应＜0.5秒｜HTTP/HTTPS/SOCKS5全协议</a>

---

<a id="理念"></a>

# 💡 理念

简洁而强大！

---

<a id="特性和亮点"></a>

# ☀️ 特性和亮点

作者经过长期实践，踩过无数坑，总结出的经验全写到这个库里了。

## 🎇 强大的自研内核

本库采用全自研的内核，内置无数实用功能，对常用功能作了整合和优化，对比 selenium，有以下优点：

- 不基于 webdriver
- 无需为不同版本的浏览器下载不同的驱动
- 运行速度更快
- 可以跨 iframe 查找元素，无需切入切出
- 把 iframe 看作普通元素，逻辑更清晰
- 可同时操作多个标签页，无需切换
- 可以直接读取浏览器缓存保存图片，无需用 GUI 点击另存
- 可以对整个网页截图，包括视口外的部分
- 可处理非`open`状态的 shadow-root

## 🎇 亮点功能

除了以上优点，本库还内置了无数人性化设计。

- 极简的定位语法，查找元素更加容易
- 集成大量常用功能，代码更优雅，功能强大稳定
- 无处不在的等待和自动重试，使不稳定的网络变得易于控制，程序更稳定，编写更省心
- 提供强大的下载工具，操作浏览器时也能享受快捷可靠的下载功能
- 允许反复使用已经打开的浏览器，无需每次运行从头启动浏览器，调试方便
- 使用 ini 文件保存常用配置，自动调用，提供便捷的设置，远离繁杂的配置项
- 内置 lxml 作为解析引擎，解析速度成几个数量级提升
- 使用 POM 模式封装，可直接用于测试，便于扩展
- 高度集成的便利功能，从每个细节中体现
- 还有很多细节，这里不一一列举，欢迎实际使用中体验：D

---

# ☕ 请我喝咖啡

作者是个人开发者，开发和写文档工作量较为繁重。

如果本项目对您有所帮助，不妨打赏一下作者 ：）

![](https://drissionpage.cn/img/code.jpg)

---

<a id="使用条款"></a>

# 📝 使用条款

允许任何人以个人身份使用或分发本项目源代码，但仅限于学习和合法非盈利目的。
个人或组织如未获得版权持有人授权，不得将本项目以源代码或二进制形式用于商业行为。

使用本项目需满足以下条款，如使用过程中出现违反任意一项条款的情形，授权自动失效。
- 禁止将DrissionPage应用到任何可能违反当地法律规定和道德约束的项目中
- 禁止将DrissionPage用于任何可能有损他人利益的项目中
- 禁止将DrissionPage用于攻击与骚扰行为
- 遵守Robots协议，禁止将DrissionPage用于采集法律或系统Robots协议不允许的数据

使用DrissionPage发生的一切行为均由使用人自行负责。
因使用DrissionPage进行任何行为所产生的一切纠纷及后果均与版权持有人无关，
版权持有人不承担任何使用DrissionPage带来的风险和损失。
版权持有人不对DrissionPage可能存在的缺陷导致的任何损失负任何责任。
