How to use: [Documents](https://DrissionPage.cn)

This project is mainly updated in gitee, and will be submitted to GitHub after producing a stable version.
Check out the latest developments at [gitee](https://gitee.com/g1879/DrissionPage).

# ✨️ Overview

DrissionPage is a python-based web page automation tool.
It can control the browser, send and receive data packets, and combine the two into one.
It can take into account the convenience of browser automation and the high efficiency of requests.
It is powerful and has countless built-in user-friendly designs and convenient functions.
Its syntax is concise and elegant, the amount of code is small, and it is friendly to novices.

Your star is the greatest support for me.💖

---

# ☕ Buy me coffee

If this project is helpful to you, why not buy the author a cup of coffee :)

![](https://drissionpage.cn/code2.jpg)

---

<a href="https://hellogithub.com/repository/dad1ecb7fbd34898a3380f5f0948ceb6" target="_blank"><img src="https://api.hellogithub.com/v1/widgets/recommend.svg?rid=dad1ecb7fbd34898a3380f5f0948ceb6&claim_uid=5jzhYcST8nxeLiH&theme=dark" alt="Featured｜HelloGitHub" style="width: 250px; height: 54px;" width="250" height="54" /></a>

# 📕 background

When using requests for data collection, when facing a website to log in to, you have to analyze data packets and JS source code, construct complex requests, and often have to deal with anti-crawling methods such as verification codes, JS obfuscation, and signature parameters. The threshold is high and the development efficiency is low. high.
Using a browser can largely bypass these pitfalls, but the browser is not very efficient.

Therefore, the original intention of this library is to combine them into one and achieve "fast writing" and "fast running" at the same time. It can switch the corresponding mode when different needs are needed, and provide a humanized usage method to improve development and operation efficiency.
In addition to merging the two, this library also encapsulates commonly used functions in web page units, providing very simple operations and statements, allowing users to reduce considerations of details and focus on function implementation. Implement powerful functions in a simple way and make your code more elegant.

The previous version was implemented by repackaging selenium. Starting from 3.0, the author started from scratch, redeveloped the bottom layer, got rid of the dependence on selenium, enhanced functions, and improved operating efficiency.

---

# 💡 Concept

Simple yet powerful!

---

# ☀️ Features and Highlights

After long-term practice, the author has stepped through countless pitfalls, and all the experiences he has summarized have been written down in this library.

## 🎇 Powerful self-developed core

This library uses a fully self-developed kernel, has built-in N number of practical functions, and has integrated and optimized common functions. Compared with selenium, it has the following advantages:

- No webdriver features
- No need to download different drivers for different browser versions
- Runs faster
- Can find elements across `<iframe>` without switching in and out
- Treat `<iframe>` as a normal element. After obtaining it, you can directly search for elements in it, making the logic clearer.
- You can operate multiple tabs in the browser at the same time, even if the tab is inactive, no need to switch
- Can directly read the browser cache to save images without using the GUI to click save
- You can take screenshots of the entire web page, including parts outside the viewport (supported by browsers 90 and above)
- Can handle shadow-root in non-open state

## 🎇 Highlighted features

In addition to the above advantages, this library also has numerous built-in humanized designs.

- Minimalist grammar rules. Integrate a large number of commonly used functions to make the code more elegant
- Positioning elements is easier and the function is more powerful and stable
- Ubiquitous wait and auto-retry functionality. Make unstable networks easier to control, programs more stable, and writing more worry-free
- Provide powerful download tools. You can also enjoy fast and reliable download functions when operating the browser
- Allows repeated use of already open browsers. No need to start the browser from scratch every time, making debugging very convenient
- Use ini files to save commonly used configurations and call them automatically, providing convenient settings and staying away from complicated configuration items.
- Built-in lxml as a parsing engine, the parsing speed is improved by several orders of magnitude
- Encapsulated using POM mode, which can be directly used for testing and easy to expand.
- Highly integrated convenient functions, reflected in every detail
- There are many details, so I won’t list them all here. You are welcome to experience them in actual use:)

---

# 🖐🏻 Disclaimer

Please do not apply DrissionPage to any work that may violate legal regulations and moral constraints. Please use DrissionPage in a friendly manner, comply with the spider agreement, and do not use DrissionPage for any illegal purposes. If you choose to use DrissionPage
This means that you abide by this agreement. The author does not bear any legal risks and losses caused by your violation of this agreement. You will be responsible for all consequences.
