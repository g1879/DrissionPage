🚤 Getting Page Information
---

After successfully accessing the web page, you can use the properties and methods of `ChromiumPage` to obtain page information.

In addition to `ChromiumPage`, there are two other types of page objects, `ChromiumTab` and `ChromiumFrame`, which correspond to tab and `<iframe>` element objects, respectively. These will be covered in separate sections.

## ✅️️ Page Information

### 📌 `html`

This property returns the current page's HTML text.

**Return type:** `str`

---

### 📌 `json`

This property parses the request content into json.

If you visit a URL that returns JSON data, the browser will display the JSON data. This property can convert the data into a `dict` format.

**Return type:** `dict`

---

### 📌 `title`

This property returns the current page's `title` text.

**Return type:** `str`

---

### 📌 `user_agent`

This property returns the current page's user agent information.

**Return type:** `str`

---

### 📌 `save()`

This method saves the current page as a file and returns the saved content.

If both the `path` and `name` parameters are `None`, only the content is returned without saving the file.

Both the Page object and Tab object have this method.

|    Parameter    |       Type        |   Default   | Description                                 |
|:---------:|:-------------:|:-------:|-------------------------------------------|
|   `path`  | `str`<br/>`Path` | `None`  | The save path. If `None` and `name` is not `None`, it saves to the current path |
|   `name`  |      `str`      | `None`  | The name of the saved file. If `None` and `path` is not `None`, the title value is used |
| `as_pdf` |     `bool`     | `False` | If `True`, save as pdf; otherwise, save as mhtml and ignore `kwargs` parameters |
| `**kwargs`|    multiple   |   None  | PDF generation parameters                  |

PDF generation parameters include: `landscape`, `displayHeaderFooter`, `printBackground`, `scale`, `paperWidth`, `paperHeight`, `marginTop`, `marginBottom`, `marginLeft`, `marginRight`, `pageRanges`, `headerTemplate`, `footerTemplate`, `preferCSSPageSize`, `generateTaggedPDF`, `generateDocumentOutline`

| Return Type |              Description                |
|:-----------:|:--------------------------------------:|
|   `str`     |  Return mhtml text when `as_pdf` is `False` |
|   `bytes`   |     Return file byte data when `as_pdf` is `True`     |

---

## ✅️️ Running Status Information

### 📌 `url`

This property returns the current visited URL.

**Return type:** `str`

---

### 📌 `address`

This property returns the page address and port controlled by the current object.

**Return type:** `str`

```python
print(page.address)
```

**Output:**

```
127.0.0.1:9222
```

---

### 📌 `tab_id`

**Return type:** `str`

This property returns the id of the current tab.

---

### 📌 `process_id`

This property returns the browser process id.

**Return type:** `int` or `None`

---

### 📌 `states.is_loading`

This property returns whether the page is currently loading.

**Return type:** `bool`

---

### 📌 `states.is_alive`

This property returns whether the page is still alive. If the tab has been closed, it returns `False`.

**Return type:** `bool`

---

### 📌 `states.ready_state`

This property returns the current loading state of the page, which can be one of the following:

- 'connecting': The web page is connecting
- 'loading': The document is still loading
- 'interactive': The DOM has loaded, but resources are still loading
- 'complete': All content has finished loading

**Return type:** `str`

---

### 📌 `url_available`

This property returns a boolean value indicating whether the current link is available.

**Return type:** `bool`

---

### 📌 `states.has_alert`

This property returns a boolean value indicating whether an alert is present on the page.

**Return type:** `bool`

---

## ✅️️ Window Information

### 📌 `size` and `rect.page_size`

These two properties return the page size as a `tuple` in the format (width, height).

**Return type:** `Tuple[int, int]`

---

### 📌 `rect.window_size`

This property returns the window size as a `tuple` in the format (width, height).

**Return type:** `Tuple[int, int]`

---

### 📌 `rect.window_location`

This property returns the window's coordinates on the screen as a `tuple`, with the top-left corner as (0, 0).

**Return type:** `Tuple[int, int]`

---

### 📌 `rect.window_state`

This property returns the current state of the window, which can be one of the following: `'normal'`, `'fullscreen'`, `'maximized'`, `'minimized'`.

**Return type:** `str`

---

### 📌 `rect.viewport_size`

This property returns the viewport size as a `tuple`, excluding scrollbars, in the format (width, height).

**Return type:** `Tuple[int, int]`

---

### 📌 `rect.viewport_size_with_scrollbar`

This property returns the browser window size, including scrollbars, as a `tuple`, in the format (width, height).

**Return type:** `Tuple[int, int]`

---

### 📌 `rect.page_location`

This property returns the screen coordinates of the top-left corner of the page as a `tuple`, with the top-left corner of the screen as (0, 0).

**Return type:** `Tuple[int, int]`



### 📌 `rect.viewport_location`

This property returns the coordinate of the viewport in the screen as a tuple, with the top left corner as (0, 0).

**Return Type:** `Tuple[int, int]`

---

## ✅️️ Configuration Parameters

### 📌 `timeout`

This property sets the overall default timeout time, including timeouts for element finding, clicking, handling prompt boxes, list selection, and other places where timeouts are required. It uses this value as the default.  
Default is 10, can be assigned a new value.

**Return Type:** `int`, `float`

```python
# Specify when creating the page object
page = ChromiumPage(timeout=5)

# Modify the timeout
page.timeout = 20
```

---

### 📌 `timeouts`

This property returns three types of timeout values as a dictionary.

- `'base'`: Same as the `timeout` property
- `'page_load'`: Used for waiting for page load
- `'script'`: Used for waiting for script execution

**Return Type:** `dict`

```python
print(page.timeouts)
```

**Output:**

```
{'base': 10, 'pageLoad': 30.0, 'script': 30.0}
```

---

### 📌 `retry_times`

This property sets the number of retries when a network connection fails. Default is 3, can be assigned a new value.

**Return Type:** `int`

```python
# Modify the number of retries
page.retry_times = 5
```

---

### 📌 `retry_interval`

This property sets the waiting interval in seconds for retrying when a network connection fails. Default is 2, can be assigned a new value.

**Return Type:** `int`, `float`

```python
# Modify the waiting interval for retrying
page.retry_interval = 1.5
```

---

### 📌 `page_load_strategy`

This property returns the page load strategy, which has 3 available options:

- `'normal'`: Wait for all resources on the page to finish loading
- `'eager'`: Stop when the DOM is loaded
- `'none'`: Stop when the page finishes connecting

**Return Type:** `str`

---

## ✅️️ Cookies and Cache Information

### 📌 `cookies`

This property returns the cookies used by the current page as a dictionary.

Please note that if different subdomains use the same `name` attribute, the cookies returned by this property may be incomplete.

**Return Type:** `dict`

---

### 📌 `get_cookies()`

This method retrieves cookies and returns them as a list of cookie objects.

| Parameter Name | Type   | Default | Description                                                                                   |
|:-------------:|:------:|:-------:|----------------------------------------------------------------------------------------------|
| `as_dict`     | `bool` | `False` | Whether to return the results as a dictionary. When `True`, a dictionary of `{name: value}` pairs is returned and the `all_info` parameter is ignored. When `False`, a list of cookie objects is returned. |
| `all_domains` | `bool` | `False` | Whether to return all cookies. When `False`, only the cookies for the current URL are returned.                                                           |
| `all_info`    | `bool` | `False` | Whether the returned cookies include all information. When `False`, only `name`, `value`, and `domain` information are included.                                                  |

| Return Type | Description                                        |
|:------:| -------------------------------------------------- |
| `dict` | When `as_dict` is `True`, a dictionary of cookies is returned.    |
| `list` | When `as_dict` is `False`, a list of cookie objects is returned. |

**Example:**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('http://www.baidu.com')

for i in page.get_cookies(as_dict=False):
    print(i)
```

**Output:**

```
{'domain': '.baidu.com', 'domain_specified': True, ......}
......
```

---

### 📌 `get_session_storage()`

This method is used to retrieve sessionStorage information, and can retrieve all or a single item.

| Parameter Name | Type   | Default | Description                        |
|:-------------:|:------:|:-------:|------------------------------------|
| `item`        | `str`  | `None`  | The item to retrieve. If `None`, all items are returned as a dictionary. |

| Return Type | Description                                 |
|:------:| --------------------------------------------|
| `dict` | When `item` is `None`, all items are returned. |
| `str`  | When `item` is specified, the content of that item is returned.      |

---

### 📌 `get_local_storage()`

This method is used to retrieve localStorage information, and can retrieve all or a single item.

| Parameter Name | Type   | Default | Description                        |
|:-------------:|:------:|:-------:|------------------------------------|
| `item`        | `str`  | `None`  | The item to retrieve. If `None`, all items are returned as a dictionary. |

| Return Type | Description                                 |
|:------:| --------------------------------------------|
| `dict` | When `item` is `None`, all items are returned. |
| `str`  | When `item` is specified, the content of that item is returned.      |

---

## ✅️️ Embeded Objects

### 📌 `driver`

This property returns the `Driver` object used by the current page object.

**Return Type:** `Driver`

