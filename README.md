# ✨️ 概述

DrissionPage 是一个基于 python 的网页自动化工具。

它既能控制浏览器，也能收发数据包，还能把两者合而为一。

可兼顾浏览器自动化的便利性和 requests 的高效率。

它功能强大，内置无数人性化设计和便捷功能。

它的语法简洁而优雅，代码量少，对新手友好。

官方网站：[https://DrissionPage.cn](https://drissionpage.cn)

项目地址：[gitee](https://gitee.com/g1879/DrissionPage)    |    [github](https://github.com/g1879/DrissionPage)     |    [gitcode](https://gitcode.com/g1879/DrissionPage) 

您的星星是对我最大的支持💖

--- 

<table>
<tr>
<td width="50%"><a href="https://proxy-seller.com/?utm_source=drissionpage&utm_medium=referral&utm_campaign=partner_promo&utm_term=drissionpage&partner=889CD46F1F2942CD" target="_blank"><img src="https://drissionpage.cn/img/Proxy-Seller.png"/></a><a href="https://proxy-seller.com/?utm_source=drissionpage&utm_medium=referral&utm_campaign=partner_promo&utm_term=drissionpage&partner=889CD46F1F2942CD" target="_blank">
Proxy-Seller - Reliable Proxies for Web Scraping & Automation
<br/>Proxy-Seller provides high-quality Residential, ISP, Datacenter IPv4/IPv6, and Mobile proxies across 195+ locations worldwide. With HTTP(S) and SOCKS5 support, flexible pricing starting at just $0.70 per IP, and 24/7 customer support, Proxy-Seller is an excellent choice for web scraping, data collection, browser automation, and other online tasks.
<br/>Exclusive 15% Discount - Use Code: DRISSIONPAGE</a></td>

<td width="50%"><a href="https://proxylane.dev/redeem?code=DRISSIONPAGE3GB&utm_source=drissionpage&utm_medium=partnership&utm_campaign=drissionpage_sponsor_202610&utm_content=github_readme" target="_blank"><img src="https://drissionpage.cn/img/proxylane.png"/></a><br/>
<a href="https://proxylane.dev/redeem?code=DRISSIONPAGE3GB&utm_source=drissionpage&utm_medium=partnership&utm_campaign=drissionpage_sponsor_202610&utm_content=github_readme" target="_blank">ProxyLane 住宅代理覆盖 195 个国家，含中国电信、联通、移动住宅 IP；95%+ IP 获 Scamalytics 低风险评级，可按城市、ISP、ASN 定向，粘性会话最长 72 小时。DrissionPage 5.0 起，set_proxy() 和 new_context(proxy=...) 直接支持账号密码代理：每个上下文一个会话名、一个独立住宅 IP，适合多账号、批量注册、AI Agent 和分地区采集。新用户凭优惠码 DRISSIONPAGE3GB 注册即可免费领取 3GB，付费流量永不过期。</a></td>
</tr>
  
<tr>
<td width="50%"><a href="https://mooproxy.net/?utm_source=drissionpage"><img src="https://drissionpage.cn/img/mooproxy.jpeg"/></a><br/>
<a href="https://mooproxy.net/?utm_source=drissionpage">Mooproxy 全球住宅代理 IP｜海量优质 IP 池，拥有1亿优质住宅IP资源，一手自营IP池，低至 0.2 U/GB｜注册即送 500M 免费流量，先体验，好用再买｜流量永久有效，不限使用时间，大规模 IP 池、低门槛体验、长期有效流量，让代理预算真正花在业务上！</a></td>

<td width="50%"><a href="https://www.nextproxy.com?utm_source=drissionpage" target="_blank"><img src="https://www.nextproxy.com/affiliate-banners/zh/nextproxy-1500x176-motion.svg?v=aligned-layout-20260910"/></a>
<a href="https://www.nextproxy.com?utm_source=drissionpage" target="_blank">NextProxy 是面向开发者与企业的全球优质代理服务商，拥有 1 亿+高纯度住宅 IP，出口来自真实家庭网络，支持国家、州省及城市级定位。独立出口配合指纹隔离，可降低账号关联与风控概率，适用于跨境电商、社媒运营、广告验证和数据采集。</a></td>   
  </tr>
  
<tr>
<td width="50%"><a href="https://www.ipwo.net/?ref=giteeg1879" target="_blank"><img src="https://drissionpage.cn/img/ipwo.png"/></a><a href="https://www.ipwo.net/?ref=giteeg1879" target="_blank">IPWO 提供全球多个地区的住宅代理 IP，为网页自动化和数据采集项目提供代理网络选择。<br/>对于使用 DrissionPage 的开发者，可根据任务需求配置不同地区的代理，用于网页访问、跨境数据采集、市场调研及自动化测试等场景。</a></td>

<td width="50%"></td>
  </tr>

  </table>

---

# 💡 理念

简洁而强大！

--- 

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

---  

# ☕ 请我喝咖啡

作者是个人开发者，开发和写文档工作量较为繁重。

如果本项目对您有所帮助，不妨打赏一下作者 ：）

![](https://drissionpage.cn/img/code.jpg)
