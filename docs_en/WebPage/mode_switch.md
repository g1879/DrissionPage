🛸 Mode Change
---

This section introduces the mode change function of `WebPage`.

The d mode of `WebPage` behaves the same as `ChromiumPage`, while the s mode behaves the same as `SessionPage`.

Use the `change_mode()` method to switch modes. When switching modes, login information will be synchronized.

## ✅️️ `mode`

**Type:** `str`

This property returns the current mode of `WebPage`.

**Example:**

```python
from DrissionPage import WebPage

page = WebPage()
print(page.mode)
```

**Output:**

```shell
d
```
---

## ✅️️ `change_mode()`

This method is used to switch the running mode of `WebPage`.

| Parameter        | Type             | Default Value | Description                                                |
|:----------------:|:----------------:|:-------------:| ---------------------------------------------------------- |
| `mode`           | `str`<br/>`None` | `None`        | Accepts 's' or 'd' to switch to the specified mode.<br/>Accepts `None` to switch to the other mode relative to the current one |
| `go`             | `bool`           | `True`        | Whether the target mode should navigate to the url of the original mode |
| `copy_cookies`   | `bool`           | `True`        | Whether to copy cookies to the target mode when switching  |

**Returns:** `None`

---

## ✅️️ Cross-mode Functionality

Some functionalities are exclusive to the d mode, such as `click()`, while others are exclusive to the s mode, such as `post()`.

In fact, regardless of the mode, the connection of the other mode still exists. Therefore, it is perfectly fine to call browser element clicks in the s mode, and they do not conflict with each other.

This design allows for great flexibility. For example, to synchronize login status, you only need to switch modes or pass cookies.

### 📌 `cookies_to_session()`

This method is used to copy the cookies of the current browser page to the `Session` object.

| Parameter               | Type      | Default Value | Description             |
|:-----------------------:|:---------:|:-------------:| ----------------------- |
| `copy_user_agent`       | `bool`    | `True`        | Whether to copy the user agent information |

**Returns:** `None`

### 📌 `cookies_to_browser()`

This method is used to copy the cookies of the `Session` object to the browser.

---

### 📌 Explanation of `post()` Return Value

The `post()` method of `SessionPage` returns whether the webpage is accessible, while the content is obtained using `page.html` or `page.json`.

In the s mode of `WebPage`, the usage of `post()` is the same.

However, in the d mode, since `post()` is a function of the s mode and conflicts with the `html` parameter of the d mode, `post()` in the d mode returns the obtained `Response` object, which is consistent with the usage of `requests`.

---

## ✅️️ Example

### 📌 Switching Modes

```python
from DrissionPage import WebPage

page = WebPage()
page.get('https://www.baidu.com')
print(page.mode)
page.change_mode()
print(page.mode)
print(page.title)
```

**Output:**

```shell
d
s
百度一下，你就知道
```

In this example, the following operations are performed:

- Initially, access Baidu in d mode.

- Switch to s mode, which will synchronize the login information to the s mode and access Baidu in the s mode.

- Print the page title accessed in the s mode.

