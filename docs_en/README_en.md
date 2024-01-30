# ✨️ Overview

DrissionPage is a web automation tool based on Python.

It can control browsers, send and receive data packets, and combine the two.

It combines the ease of browser automation with the efficiency of requests.

It is powerful, with numerous user-friendly designs and convenient features.

Its syntax is simple and elegant, with less code and beginner-friendly.

---

<a href='https://gitee.com/g1879/DrissionPage/stargazers'><img src='https://gitee.com/g1879/DrissionPage/badge/star.svg?theme=dark' alt='star'></img></a> <a href='https://gitee.com/g1879/DrissionPage/members'><img src='https://gitee.com/g1879/DrissionPage/badge/fork.svg?theme=dark' alt='fork'></img></a>

Project links: [gitee](https://gitee.com/g1879/DrissionPage)    |    [github](https://github.com/g1879/DrissionPage) 

Your stars are the greatest support to me 💖

---

Supported systems: Windows, Linux, Mac

Python version: 3.6 and above

Supported browsers: Chromium-based browsers (such as Chrome and Edge), electron applications

---

**📖 Chinese documentation：**  [Click to view](http://g1879.gitee.io/drissionpagedocs)

**QQ group for communication：**  897838127[full]、558778073

**📖 Documentation：**  [Click to view](https://github.com/y0un9kane/DrissionPage/tree/master/docs_en)

**Telegram group：**   [@DrissionPage](https://t.me/DrissionPage)

---

# 🔥 Upcoming version preview

Check the next development plan: [Upcoming version preview](http://g1879.gitee.io/drissionpagedocs/whatsnew/3_3/)

---

# 📕 Background

When using requests for data collection and facing websites that require logging in, analyzing data packets and JS source code, constructing complex requests, and dealing with anti-crawling methods such as captchas, JS obfuscation, and signature parameters, the threshold is high and the development efficiency is not high. 
Using a browser can bypass many of these obstacles, but the efficiency of browser operation is not high.

Therefore, the original intention of this library is to merge them and achieve both "write fast" and "run fast". It can switch to the corresponding mode when needed, and provide a user-friendly usage method to improve development and running efficiency. 
In addition to merging the two, this library encapsulates common functions on a webpage basis, providing very convenient operations and statements, allowing users to reduce consideration of details and focus on functionality implementation. By implementing powerful functions in a simple way, the code becomes more elegant.

Previous versions were implemented by re-encapsulating selenium. From version 3.0 onwards, the author started from scratch, redeveloped the underlying framework, broke free from the dependence on selenium, enhanced functionality, and improved runtime efficiency.

---

# 💡 Philosophy

Simplicity! Ease of use! Convenience!

---

# ☀️ Features and Highlights

After long-term practice and countless trials, the author has summarized the experience and written them all into this library.

## 🎇 Powerful self-developed engine

This library adopts a self-developed engine, with built-in numerous practical functions, and has the following advantages compared to selenium by integrating and optimizing common functions:

- No webdriver characteristics

- No need to download different drivers for different versions of browsers

- Faster runtime speed

- Can search for elements across `<iframe>` without having to switch in and out

- Treats `<iframe>` as regular elements, allowing direct element search within them for clearer logic

- Can operate on multiple tabs in the browser simultaneously, even if the tabs are inactive, without the need to switch

- Can directly read browser cache to save images without needing to click "Save As" using GUI

- Can take screenshots of the entire webpage, including portions outside the viewport (supported by versions 90 and above)

- Can handle non-`open` status shadow-root

## 🎇 Highlighted features

In addition to the above advantages, this library also includes numerous user-friendly designs.

- Minimalistic syntax rules. Integrates many common functions, leading to more elegant code

- Easier element locating with more powerful and stable functionality

- Ubiquitous waiting and automatic retry functions. Makes unstable networks easier to control, providing program stability and peace of mind in writing code

- Provides powerful download tools. Allows for quick and reliable downloads when operating on the browser

- Allows reuse of already open browsers. No need to start the browser from scratch every time, making debugging extremely convenient

- Saves common configurations in ini files and automatically calls them, providing convenient settings and avoiding complex configuration settings

- Uses built-in lxml as the parsing engine, significantly improving parsing speed

- Wrapped in POM (Page Object Model) pattern, can be directly used for testing and easy to extend

- Highly integrated convenient functionalities, demonstrating excellence in every detail.

- There are many details that are not listed here, welcome to experience them in actual use:）

---

# 🛠 User Manual

[Click here to jump to the user manual](http://g1879.gitee.io/drissionpage)

---

# 🔖 Version History

[Click here to view the version history](http://g1879.gitee.io/drissionpagedocs/history/3.x/)

---

# 🖐🏻 Disclaimer

Please do not use DrissionPage in any work that may violate laws and moral constraints. Please use DrissionPage in a friendly manner and comply with the spider agreement. Do not use DrissionPage for any illegal purposes. By choosing to use DrissionPage, you agree to this agreement, and the author is not responsible for any legal risks and losses resulting from your violation of this agreement. You are responsible for all consequences.

---


# ☕ Buy Me a Coffee

If this project has been helpful to you, you may consider buying me a cup of coffee:）

![](http://g1879.gitee.io/drissionpagedocs/imgs/code.jpg)






### Table of contents
* [Getting started guide](#section1)
    + [Installation](https://github.com/y0un9kane/DrissionPage/blob/master/docs_en/get_start/installation.md)
    + [Import](#section3)
    + [before start](#section4)
    + [examples](#section5)
* [SessionPage](#SessionPage)
    + [intro](#intro)
    + [create page obj](#create page obj)
    + [open web](#open web)
    + [get page info](#get page info)
    + [get element info](#get element info)
    + [page settings](#gpage settings)
    + [startup configuration](#startup configuration)
* [ChromiumPage](#ChromiumPage)
    + [intro](#intro)
    + [create page obj](#create page obj)
    + [open web](#open web)
    + [page operation](#page operation)
    + [get element info](#get element info)
    + [element operation](#element operation)
    + [Auto waiting](#Auto waiting)
    + [File upload](#File upload)
    + [tab operation](#tab operation)
    + [iframe operation](#iframe operation)
    + [listen in network data](#listen in network data)
    + [Action chains](#Action chains)
    + [Screenshot and recording](#Screenshot and recording)
    + [Browser startup settings](#Browser startup settings)
* [WebPage](#WebPage)
    + [intro](#intro)
    + [create page obj](#create page obj)
    + [Mode switching](#Mode switching)
    + [Exclusive features](#Exclusive features)
* [Find element](#Find element)
    + [intro](#intro)
    + [Basic Usage](#Basic Usage)
    + [More Usages](#More Usages)
    + [Simplified](#Simplified)
    + [When Element Not Found](#When Element Not Found)
    + [Syntax Quick Reference Table](#Syntax Quick Reference Table)
* [Download file](#Download file)
    + [intro](#intro)
    + [DownloadKit](#DownloadKit)
    + [downloads](#downloads)
* [Advanced usage](#Advanced usage)
    + [Usage of Configuration Files](#Usage of Configuration Files)
    + [Global Settings](#Global Settings)
    + [CMD Usage](#CMD Usage)
    + [Usage Exceptions](#Usage Exceptions)
    + [Accelerated Data Reading](#Accelerated Data Reading)
    + [Packaging the Program](#Packaging the Program)
    + [Small Tools](#Small Tools)
