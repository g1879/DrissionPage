🚤 Visit Web Page
---

Both `ChromiumPage` and `WebPage` objects can control browser access to web pages. Here we will only explain `ChromiumPage`, and `WebPage` will be introduced separately in later chapters.

## ✅️️ `get()`

This method is used to navigate to a URL. When the connection fails, the program will retry.

| Parameter Name | Type    | Default | Description          |
| :------------: | :-----: | :-----: | -------------------- |
| `url`          | `str`   | Required| Target URL           |
| `show_errmsg`  | `bool`  | `False` | Whether to display and raise exceptions when a connection error occurs |
| `retry`        | `int`   | `None`  | Number of retries, defaults to 3 |
| `interval`     | `float` | `None`  | Retry interval (seconds), defaults to 2 |
| `timeout`      | `float` | `None`  | Timeout for loading (seconds) |

| Return Type | Description |
| :---------: | ----------- |
| `bool`      | Whether the connection is successful |

**Example:**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://www.baidu.com')
```

---

## ✅️️ Setting Timeout and Retry

When the network is unstable, accessing a web page may not always be successful. The `get()` method has built-in timeout and retry functions. They can be set using the `retry`, `interval`, and `timeout` parameters.  
If the `timeout` parameter is not specified, it will use the value in the `page_load` parameter of `ChromiumPage`'s `timeouts` attribute.

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://g1879.gitee.io/drissionpagedocs', retry=1, interval=1, timeout=1.5)
```

---

## ✅️️ Load Strategies

### 📌 Overview

The load strategy refers to the behavior pattern of the program during the page loading phase. There are three types:

- `normal()`: Normal mode, will wait for the page to finish loading and automatically retry or stop if timeout (default mode)
- `eager()`: Load DOM or stop loading immediately if timeout, without loading page resources
- `none()`: Will not automatically stop even if timeout, will trigger load complete event

In the first two modes, the page loading process will block the program and only perform subsequent operations when loading is complete.

In the `none()` mode, the program is only blocked during the connection phase, and the loading phase can be manually stopped by calling `stop_loading()` according to the situation.

This provides users with great flexibility, allowing them to stop page loading actively when key data packets or elements appear, greatly improving execution efficiency.

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_strategy.eager()
page.get('https://g1879.gitee.io/drissionpagedocs')
```

---

### 📌 Setting Strategies

Load strategies can be set using an ini file, `ChromiumOptions` object, or the `set.load_mode.xxxx()` methods of the page object.

They can also be dynamically set during runtime.

**Setting in Configuration Object**

```python
from DrissionPage import ChromiumOptions, ChromiumPage

co = ChromiumOptions().set_load_mode('none')
page = ChromiumPage(co)
```

**Setting During Runtime**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_mode.none()
```

---

### 📌 `none` Mode Tips

**Example 1, with a Listener**

When used with a listener, it can actively stop loading when the desired data packet is obtained.

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_mode.none()  # Set the load mode to none

page.listen.start('api/getkeydata')  # Specify the target to listen and start listening
page.get('http://www.hao123.com/')  # Access the website
packet = page.listen.wait()  # Wait for the data packet
page.stop_loading()  # Actively stop loading
print(packet.response.body)  # Print the body of the data packet
```

**Example 2, with Element Retrieval**

When used with element retrieval, it can actively stop loading when a specific element is obtained.

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_mode.none()  # Set the load mode to none

page.get('http://www.hao123.com/')  # Access the website
ele = page.ele('中国日报')  # Retrieve the element with text containing "中国日报"
page.stop_loading()  # Actively stop loading
print(ele.text)  # Print element text
```

**Example 2, with Page Features**

It can actively stop loading when the page reaches a certain state. For example, when performing multi-level login, it can wait for the title to change to the final target URL and then stop.

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_mode.none()  # Set the load mode to none

page.get('http://www.hao123.com/')  # Access the website
page.wait.title_change('hao123')  # Wait for the title to change to the target text
page.stop_loading()  # Actively stop loading
```

