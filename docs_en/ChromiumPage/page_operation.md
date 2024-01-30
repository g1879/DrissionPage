🚤 Page Interaction
---

This section introduces the browser page interaction feature, while element interaction is covered in the next section.

A Tab object (`ChromiumTab` and `WebPageTab`) controls a browser tab and is the main unit of page control.

`ChromiumPage` and `WebPage` also control a tab, but they provide additional browser-wide control capabilities.

The features described below can be used by Tab objects except for closing the browser.

## ✅️️ Page Navigation

### 📌 `get()`

This method is used to navigate to a URL. The program will retry when the connection fails.

|   Parameter Name   |   Type    |  Default Value  | Description                           |
|:------------------:|:---------:|:--------------:|---------------------------------------|
|      `url`         |  `str`    |   required     | Target URL                            |
|  `show_errmsg`     | `bool`    |   `False`      | Whether to display and raise an exception when the connection fails |
|    `retry`         |  `int`    |     `None`     | Number of retries, uses the page parameter by default when it is `None` |
|   `interval`       | `float`   |     `None`     | Retry interval (seconds), uses the page parameter by default when it is `None` |
|   `timeout`        | `float`   |     None`      | Load timeout (seconds)                |

|   Return Type   | Description   |
|:------------:|--------------|
|   `bool`     | Whether the connection is successful |

**Example:**

```python
page.get('https://www.baidu.com')
```

---

### 📌 `back()`

This method is used to navigate backward in the browsing history.

|  Parameter Name  |  Type  |  Default Value  | Description |
|:----------------:|:-----:|:--------------:|--------------|
|    `steps`      | `int` |     `1`        | Number of steps to go back |

**Returns:** `None`

**Example:**

```python
page.back(2)  # Go back two web pages
```

---

### 📌 `forward()`

This method is used to navigate forward in the browsing history.

|  Parameter Name  |  Type  |  Default Value  | Description |
|:----------------:|:-----:|:--------------:|--------------|
|    `steps`      | `int` |     `1`        | Number of steps to go forward |

**Returns:** `None`

```python
page.forward(2)  # Go forward two steps
```

---

### 📌 `refresh()`

This method is used to refresh the current page.

|   Parameter Name   |   Type    |  Default Value  | Description                             |
|:------------------:|:---------:|:--------------:|-----------------------------------------|
|  `ignore_cache`    | `bool`    |    `False`     | Whether to ignore cache when refreshing  |

**Returns:** `None`

**Example:**

```python
page.refresh()  # Refresh the page
```

---

### 📌 `stop_loading()`

This method is used to force stop the current page from loading.

**Parameter:** None

**Returns:** `None`

---

### 📌 `set.blocked_urls()`

This method is used to set ignored URLs.

|    Parameter Name  |                  Type                      | Default Value | Description                                                     |
|:------------------:|:------------------------------------------:|:------------:|-----------------------------------------------------------------|
|       `urls`       | `str`<br/>`list`<br/>`tuple`<br/>`None`    |   required   | URLs to be ignored, can pass multiple, can use `'*'` as wildcard, clear the set items when `None` is provided |

**Returns:** `None`

**Example:**

```python
page.set.blocked_urls('*.css*')  # Do not load CSS files
```

---

## ✅️️ Element Management

### 📌 `remove_ele()`

This method is used to remove an element from the page.

|    Parameter Name    |                          Type                        | Default Value | Description          |
|:--------------------:|:---------------------------------------------------:|:------------:|----------------------|
|    `loc_or_ele`      | `str`<br/>`Tuple[str, str]`<br/>`ChromiumElement`    |   required   | The element to be removed, can be an element or a locator |

**Returns:** `None`

**Example:**

```python
# Remove an element that has been obtained
ele = page('tag:a')
page.remove_ele(ele)

# Remove an element found using a locator
page.remove_ele('tag:a')
```

---

## ✅️️ Execute Scripts or Commands

### 📌 `run_js()`

This method is used to execute a JavaScript script.

|   Parameter Name   |   Type    |   Default Value  | Description                                                     |
|:------------------:|:---------:|:---------------:|-----------------------------------------------------------------|
|    `script`        |  `str`    |    required     | JavaScript script text                                          |
|      `*args`       |     -     |       None      | Pass the arguments, which correspond to `arguments[0]`, `arguments[1]`, and so on in the JavaScript script |
|    `as_expr`       | `bool`    |     `False`     | Whether to run as an expression, `args` parameter is invalid when `True` |
|    `timetout`      | `float`   |     `None`      | JavaScript timeout, use the page `timeouts.script` setting if `None` |

|   Return Type   | Description   |
|:------------:|--------------|
|     `Any`    | Script execution result |

**Example:**

```python
# Execute the JavaScript script by passing in the arguments, displaying a popup with the message Hello world!
page.run_js('alert(arguments[0]+arguments[1]);', 'Hello', ' world!')
```

:::warning Attention
- If `as_expr` is `True`, the script should return a result and should not have a `return`.
- If `as_expr` is not `True`, the script should be written as a method as much as possible.
:::

---

### 📌 `run_js_loaded()`

This method is used to run JavaScript scripts after the page has finished loading.

|   Parameter   |   Type   |  Default  | Description                                              |
|:-------------:|:-------:|:--------:|-------------------------------------------------------|
|    `script`   |  `str`  | Required | JavaScript script text                                   |
|    `*args`    |    -    |    N/A   | Arguments passed to the script, corresponding to `arguments[0]`, `arguments[1]`, ... in the JavaScript text |
|  `as_expr`    | `bool`  | `False`  | Whether to run as an expression, when `True` the `args` argument is invalid                   |
|  `timetout`   | `float` |   `None`  | JavaScript timeout in seconds, if `None` the page's `timeouts.script` setting will be used   |

| Return Type | Description |
|:-----------:|-------------|
|    `Any`    | Script execution result |

---

### 📌 `run_async_js()`

This method is used to execute JavaScript code asynchronously.

**Parameters:**

|   Parameter   |   Type   |  Default  | Description                                              |
|:-------------:|:-------:|:--------:|-------------------------------------------------------|
|    `script`   |  `str`  | Required | JavaScript script text                                   |
|    `*args`    |    -    |    N/A   | Arguments passed to the script, corresponding to `arguments[0]`, `arguments[1]`, ... in the JavaScript text |
|  `as_expr`    | `bool`  | `False`  | Whether to run as an expression, when `True` the `args` argument is invalid                   |

**Return:** `None`

---

### 📌 `run_cdp()`

This method is used to execute Chrome DevTools Protocol statements.

For more information on using cdp, please see [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

|  Parameter Name  |  Type  | Default | Description |
|:----------------:|:-----:|:-------:|-------------|
|      `cmd`       | `str` | Required | Protocol item |
| `**cmd_args` |   -   |  N/A  | Project parameters |

| Return Type | Description |
|:-----------:|-------------|
|    `dict`    | Execution result returned |

**Example:**

```python
# Stop loading the page
page.run_cdp('Page.stopLoading')
```

---

### 📌 `run_cdp_loaded()`

This method is used to execute Chrome DevTools Protocol statements after making sure the page has finished loading.

|  Parameter Name  |  Type  | Default | Description |
|:----------------:|:-----:|:-------:|-------------|
|      `cmd`       | `str` | Required | Protocol item |
| `**cmd_args` |   -   |  N/A  | Project parameters |

| Return Type | Description |
|:-----------:|-------------|
|    `dict`    | Execution result returned |

---

## ✅️️ Cookies and Cache

### 📌 `set_cookies()`

This method is used to set cookies.

It can accept cookies in the formats of `CookieJar`, `list`, `tuple`, `str`, and `dict`. Note that this method does not have the `item` and `value` parameters of the latter two methods.

|  Parameter Name   |                                  Type                                  | Default | Description        |
|:-----------------:|:---------------------------------------------------------------------:|:-------:|--------------------|
|     `cookies`     | `RequestsCookieJar`<br/>`list`<br/>`tuple`<br/>`str`<br/>`dict` | Required | Cookies information |

**Return:** `None`

**Example:**

```python
# It can accept multiple types of parameters
cookies1 = ['name1=value1', 'name2=value2'],
cookies2 = ('name1=value1', 'name2=value2', 'secure')
cookies3 = 'name1=value1; name2=value2; path=/; domain=.example.com; secure'
cookies4 = {'name1': 'value1', 'name2': 'value2'}
page.set_cookies(cookies1)
```

---

### 📌 `clear_cookies()`

This method is used to clear all cookies.

**Parameters:** None

**Return:** `None`

---

### 📌 `remove_cookies()`

This method is used to delete a cookie.

| Parameter Name |  Type   |  Default  |      Description      |
|:--------------:|:-------:|:---------:|-----------------------|
|     `name`     |  `str`  |  Required | The name field of the cookie |
|      `url`     |  `str`  |  `None`   | The url field of the cookie |
|    `domain`    |  `str`  |  `None`   | The domain field of the cookie |
|     `path`     |  `str`  |  `None`   | The path field of the cookie |

**Return:** `None`

---

### 📌 `set_session_storage()`

This method is used to set or delete a particular sessionStorage item.

| Parameter Name |         Type         | Default |  Description      |
|:--------------:|:-------------------:|:-------:|-------------------|
|     `item`     |      `str`          | Required | The item to be set |
|    `value`     | `str`<br/>`False` | Required | When `False`, delete the item |

**Return:** `None`

**Example:**

```python
page.set_session_storage(item='abc', value='123')
```

---

### 📌 `set_local_storage()`

This method is used to set or delete a particular localStorage item.

| Parameter Name | Type               | Default Value | Description            |
|:--------------:|:------------------:|:-------------:|------------------------|
| `item`         | `str`              | Required      | The item to be set     |
| `value`        | `str`<br/>`False` | Required      | When `False`, delete the item |

**Returns:** `None`

---

### 📌 `clear_cache()`

This method is used to clear the cache and can choose the items to clear.

| Parameter Name  | Type    | Default Value | Description               |
|:--------------:|:------:|:------------:|---------------------------|
| `session_storage` | `bool` | `True`        | Whether to clear session storage |
| `local_storage`  | `bool` | `True`        | Whether to clear local storage   |
| `cache`        | `bool` | `True`        | Whether to clear cache        |
| `cookies`      | `bool` | `True`        | Whether to clear cookies      |

**Returns:** `None`

**Example:**

```python
page.clear_cache(cookies=False)  # Clear everything except cookies
```

---

## ✅️️ Run parameter settings

Various settings are hidden in the `set` attribute.

### 📌 `set.retry_times()`

This method is used to set the number of retries when the connection fails.

| Parameter Name | Type   | Default Value | Description |
|:-------------:|:------:|:-----------:|-------------|
| `times`       | `int`  | Required    | Number of times |

**Returns:** `None`

### 📌 `set.retry_interval()`

This method is used to set the interval between retries when the connection fails.

| Parameter Name | Type   | Default Value | Description |
|:-------------:|:------:|:------------:|-------------|
| `interval`    | `float` | Required    | Number of seconds |

**Returns:** `None`

### 📌 `set.timeouts()`

This method is used to set three types of timeout times, in seconds. Can be set individually, `None` means not to change the original settings.

| Parameter Name  | Type   | Default Value | Description     |
|:--------------:|:------:|:------------:|-----------------|
| `base`         | `float` | `None`       | Overall timeout |
| `page_load`    | `float` | `None`       | Page load timeout |
| `script`       | `float` | `None`       | Script runtime timeout |

**Returns:** `None`

**Example:**

```python
page.set.timeouts(base=10, page_load=30)
```

---

### 📌 `set.load_strategy`

This property is used to set the page loading strategy, call its method to choose a strategy.

| Method Name  | Parameter | Description                                  |
|:------------:|:--------:|----------------------------------------------|
| `normal()`   | None     | Wait for the page to be completely loaded, default |
| `eager()`    | None     | Wait for the document to be loaded and do not wait for resources |
| `none()`     | None     | Finish loading the page |

**Example:**

```python
page.set.load_strategy.normal()
page.set.load_strategy.eager()
page.set.load_strategy.none()
```

---

### 📌 `set.user_agent()`

This method is used to set the user agent for the current browser tab.

| Parameter Name | Type   | Default Value | Description            |
|:-------------:|:------:|:------------:|------------------------|
| `ua`          | `str`  | Required    | User agent string      |
| `platform`    | `str`  | `None`       | Platform type, such as `'android'` |

**Returns:** `None`

---

### 📌 `set.headers()`

This method is used to set additional parameters to add to the current page request headers.

| Parameter Name | Type   | Default Value | Description            |
|:-------------:|:------:|:------------:|------------------------|
| `headers`     | `dict` | Required    | Headers in dict format |

**Returns:** `None`

**Example:**

```python
h = {'connection': 'keep-alive', 'accept-charset': 'GB2312,utf-8;q=0.7,*;q=0.7'}
page.set.headers(headers=h)
```

---

## ✅️️ Window management

Window management functions are hidden in the `set.window` attribute.

### 📌 `set.window.max()`

This method is used to maximize the window.

**Parameter:** None

**Returns:** `None`

**Example:**

```python
page.set.window.max()
```

---

### 📌 `set.window.mini()`

This method is used to minimize the window.

**Parameter:** None

**Returns:** `None`

---

### 📌 `set.window.full()`

This method is used to switch the window to full screen mode.

**Parameter:** None

**Returns:** `None`

---

### 📌 `set.window.normal()`

This method is used to switch the window to normal mode.

**Parameter:** None

**Returns:** `None`

---

### 📌 `set.window.size()`

This method is used to set the window size. When only one parameter is passed, the other parameter will not change.

| Parameter Name | Type   | Default Value | Description |
|:-------------:|:------:|:------------:|-------------|
| `width`       | `int`  | `None`       | Window width |
| `height`      | `int`  | `None`       | Window height |

**Returns:** `None`

**Example:**

```python
page.set.window.size(500, 500)
```

---

### 📌 `set.window.location()`

This method is used to set the position of the window. When only one parameter is passed, the other parameter will not change.

| Parameter Name |   Type  |  Default Value | Description |
|:--------------:|:-------:|:-------------:|-------------|
|      `x`       | `int`   |     `None`    |  Distance from the top |
|      `y`       | `int`   |     `None`    | Distance from the left |

**Returns:** `None`

**Example:**

```python
page.set.window.location(500, 500)
```

---

### 📌 `set.window.hide()`

This method is used to hide the browser window.

Unlike headless mode, this method directly hides the browser process. It will also disappear from the taskbar. It only supports Windows system and requires the installation of the pypiwin32 library to be used.

However, after the window is hidden, if a new window appears, the entire browser will become visible again.

**Parameters:** None

**Returns:** `None`

**Example:**

```python
page.set.window.hide()
```

:::warning Note
   - After hiding the browser, it is not closed. The hidden browser will be taken over by the next program run.
   - After the browser is hidden, if new tabs are opened, they will be displayed automatically.
:::

---

### 📌 `set.window.show()`

This method is used to show the current browser window.

**Parameters:** None

**Returns:** `None`

---

## ✅️️ Page Scrolling

The functionality of page scrolling is hidden in the `scroll` attribute.

### 📌 `scroll.to_top()`

This method is used to scroll the page to the top, with the horizontal position unchanged.

**Parameters:** None

**Returns:** `None`

**Example:**

```python
page.scroll.to_top()
```

---

### 📌 `scroll.to_bottom()`

This method is used to scroll the page to the bottom, with the horizontal position unchanged.

**Parameters:** None

**Returns:** `None`

---

### 📌 `scroll.to_half()`

This method is used to scroll the page to the middle vertical position, with the horizontal position unchanged.

**Parameters:** None

**Returns:** `None`

---

### 📌 `scroll.to_rightmost()`

This method is used to scroll the page to the rightmost position, with the vertical position unchanged.

**Parameters:** None

**Returns:** `None`

---

### 📌 `scroll.to_leftmost()`

This method is used to scroll the page to the leftmost position, with the vertical position unchanged.

**Parameters:** None

**Returns:** `None`

---

### 📌 `scroll.to_location()`

This method is used to scroll the page to the specified location.

| Method |  Parameter | Description |
|:------:|:----------:|-------------|
|   `x`  |  Required  | Horizontal position |
|   `y`  |  Required  | Vertical position |

**Returns:** `None`

**Example:**

```python
page.scroll.to_location(300, 50)
```

---

### 📌 `scroll.up()`

This method is used to scroll the page up by a certain number of pixels, with the horizontal position unchanged.

|  Method  | Parameter | Description |
|:-------:|:---------:|-------------|
| `pixel` |  Required | Scrolling pixels |

**Returns:** `None`

**Example:**

```python
page.scroll.up(30)
```

---

### 📌 `scroll.down()`

This method is used to scroll the page down by a certain number of pixels, with the horizontal position unchanged.

|  Method  | Parameter | Description |
|:-------:|:---------:|-------------|
| `pixel` |  Required | Scrolling pixels |

**Returns:** `None`

---

### 📌 `scroll.right()`

This method is used to scroll the page to the right by a certain number of pixels, with the vertical position unchanged.

|  Method  | Parameter | Description |
|:-------:|:---------:|-------------|
| `pixel` |  Required | Scrolling pixels |

**Returns:** `None`

---

### 📌 `scroll.left()`

This method is used to scroll the page to the left by a certain number of pixels, with the vertical position unchanged.

|  Method  | Parameter | Description |
|:-------:|:---------:|-------------|
| `pixel` |  Required | Scrolling pixels |

**Returns:** `None`

### 📌 `scroll.to_see()`

This method is used to scroll the page until the element is visible.

| Parameter Name | Type                                | Default | Description                                             |
| -------------- | ----------------------------------- | ------- | ------------------------------------------------------- |
| `loc_or_ele`   | `str`<br/>`tuple`<br/>`ChromiumElement` | Required  | Location information of the element, can be element or locator |
| `center`       | `bool`<br/>`None`                    | `None`  | Whether to scroll to the center of the page, if `None`, scroll to the center if blocked |

**Returns:** `None`

**Example:**

```python
# Scroll to an element already obtained
ele = page.ele('tag:div')
page.scroll.to_see(ele)

# Scroll to an element found by locator
page.scroll.to_see('tag:div')
```

---

## ✅️️ Scrolling Settings

There are two ways to scroll the page: directly jumping to the target position or smooth scrolling, which takes some time. The latter scrolling time is difficult to determine, which can lead to program instability and inaccurate clicks.

Some websites specify the use of smooth scrolling in the CSS settings, which is not what we want. However, in order to give developers the full right to choose, this library does not force modification, but provides two settings for developers to choose from.

### 📌 `set.scroll.smooth()`

This method sets whether the website is enabled for smooth scrolling. It is recommended to use this method to disable smooth scrolling for web pages.

| Parameter Name | Type  | Default | Description |
| -------------- | ----- | ------- | ----------- |
| `on_off`       | `bool` | `True`  | `bool` indicates on or off |

**Returns:** `None`

**Example:**

```python
page.set.scroll.smooth(on_off=False)
```

---

### 📌 `set.scroll.wait_complete()`

This method is used to set whether to wait for the scroll to complete after scrolling. When you do not want to turn off the smooth scrolling function of the web page, you can enable this setting to ensure that the scroll completes before performing the subsequent steps.

| Parameter Name | Type  | Default | Description |
| -------------- | ----- | ------- | ----------- |
| `on_off`       | `bool` | `True`  | `bool` indicates on or off |

**Returns:** `None`

**Example:**

```python
page.set.scroll.wait_complete(on_off=True)
```

---

## ✅️️ Popup Message Handling

### 📌 `handle_alert()`

This method is used to handle alert messages.
It can set the waiting time, so that the message box will not be processed until it appears. If the message box is not received within the timeout, it returns `False`.
It can also only get the text of the message box without processing the message box.
It can also handle the next prompt box that appears, which is very useful when handling pop-ups triggered when leaving the page.

:::warning Note
    The program cannot take over a browser or tab that has already displayed a prompt box.
:::

| Parameter Name | Type                 | Default | Description                                                                 |
| -------------- | -------------------- | ------- | --------------------------------------------------------------------------- |
| `accept`       | `bool`<br/>`None`    | `True`  | `True` to confirm, `False` to cancel, `None` does not click a button but still returns the text value |
| `send`         | `str`                | `None`  | When handling the prompt prompt box, you can enter text                      |
| `timeout`      | `float`              | `None`  | Timeout for waiting for the prompt box to appear, `None` uses the overall timeout of the page |
| `next_one`     | `bool`               | `False` | Whether to handle the next popup, `timeout` parameter is invalid when `True` |

| Return Type | Description                                       |
| ----------- | ------------------------------------------------- |
| `str`       | Text content of the prompt box                     |
| `False`     | Returns `False` if the prompt box is not received |

**Example:**

```python
# Confirm the alert and get the text content of the alert
txt = page.handle_alert()

# Click cancel
page.handle_alert(accept=False)

# Enter text for the prompt box and click OK
page.handle_alert(accept=True, send='some text')

# Do not process the message box, just get the text content of the message box
txt = page.handle_alert(accept=None)
```

---

### 📌 Automatic Processing

You can use the `set.auto_handle_alert()` method to set automatic processing of the alert box, so that the alert box will not pop up and will be processed directly.

| Parameter Name | Type  | Default | Description                 |
| -------------- | ----- | ------- | --------------------------- |
| `on_off`       | `bool` | `True`  | `bool` indicates on or off    |
| `accept`       | `bool` | `True`  | `bool` indicates confirm or cancel |

**Returns:** `None`

**Example:**

```python
from DrissionPage import ChromiumPage

p = ChromiumPage()
p.set.auto_handle_alert()  # After this, pop-ups will be automatically confirmed
```

---

## ✅️️ Closing and Reconnecting

### 📌 `disconnect()`

This method is used to disconnect the connection between the page object and the page, but does not close the tab. After disconnecting, the object cannot operate on the tab.

Page, Tab, and `ChromiumFrame` objects all have this method.

It is worth noting that after the Page object breaks the connection with the browser, it can still manage tabs.

**Parameters:** None

**Returns:** `None`

---

### 📌 `reconnect()`

This method is used to close the connection to the page and then establish a new connection.

This is mainly used to deal with long-running processes that result in excessive memory usage. Disconnecting frees up memory, and then reconnecting allows for continued control of the browser.

The `Page`, `Tab`, and `ChromiumFrame` objects all have this method.

|  Parameter  |   Type    | Default Value | Description |
|:------:|:-------:|:---:|-------------|
| `wait` | `float` | `0` | Number of seconds to wait before reconnecting after closing |

**Returns:** `None`

---

### 📌 `quit()`

This method is used to close the browser.

|   Parameter    |   Type    |   Default Value   | Description                                         |
|:---------:|:-------:|:-------:|--------------------------------------------|
| `timeout` | `float` |   `5`   | Timeout for waiting for the browser to close |
|  `force`  | `bool`  | `False` | Whether to forcibly terminate the process immediately      |

**Returns:** `None`

