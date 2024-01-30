🛸 Unique Features
---

This section introduces the unique features of `WebPage`.

`WebPage` is integrated with `ChromiumPage` and `SessionPage`, and therefore has all the functionalities of both. For more details on these functionalities, refer to the relevant chapters. Here, we only introduce the unique features of `WebPage`.

## ✅️️ Cookie Handling

### 📌 `cookies_to_session()`

This method copies the cookies from the browser to the `session` object.

|  Parameter Name   |  Type  | Default Value | Description                            |
|:-----------------:|:------:|:-------------:|----------------------------------------|
|  `copy_user_agent` | `bool` |    `True`     | Specifies whether to copy user agent information |

**Returns:** `None`

---

### 📌 `cookies_to_browser()`

This method copies the cookies from the `session` object to the browser.

**Parameters:** None

**Returns:** `None`

---

## ✅️️ Property Settings

The values set by the `set_cookies()`, `set_headers()`, and `set_user_agent()` methods are only valid for the current mode. This means that when calling these methods in d mode, the browser will be set, but not the Session object, and vice versa.

## ✅️️ Tab

The `get_tab()` method of `WebPage` returns a Tab object, which is a WebPageTab that can also switch states. Except for not being able to control the download functionality of the tab and browser, all other functionalities are the same as those of `WebPage`.

When a `WebPageTab` is newly created, it is in d mode.

**Example:**

```python
from DrissionPage import WebPage

page = WebPage()
page.get('https://www.baidu.com')
tab = page.get_tab()
tab.change_mode()
tab.get('https://gitee.com')
print(tab.title)
```

## ✅️️ Closing Objects

### 📌 `close_driver()`

This method closes the built-in `Driver` object and the browser, and switches to s mode.

**Parameters:** None

**Returns:** `None`

---

### 📌 `close_session()`

This method closes the built-in `Session` object and the browser, and switches to d mode.

**Parameters:** None

**Returns:** `None`

---

### 📌 `close()`

This method is used to close the current tab and Session.

**Parameters:** None

**Returns:** `None`

---

### 📌 `quit()`

This method completely closes the built-in `Session` object and `Driver` object, and closes the browser (if open).

|  Parameter Name  |   Type   | Default Value | Description                                      |
|:----------------:|:--------:|:-------------:|--------------------------------------------------|
|    `timeout`     | `float`  |      `5`      | Timeout for waiting for the browser to close      |
|     `force`      | `bool`   |    `False`    | Specifies whether to forcefully terminate process |

**Returns:** `None`

