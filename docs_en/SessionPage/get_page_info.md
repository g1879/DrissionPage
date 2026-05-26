🚄 Get Page Info
---

After successfully accessing the webpage, you can use the attributes and methods of `SessionPage` to get page information.

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('http://www.baidu.com')
# Get page title
print(page.title)
# Get page html
print(page.html)
```

**Output:**

```shell
百度一下，你就知道
<!DOCTYPE html>
<!--STATUS OK--><html> <head><meta http-equi...
```

---

## ✅️️ Page Information

### 📌 `url`

This property returns the current URL being accessed.

**Type:** `str`

---

### 📌 `url_available`

This property returns a boolean value indicating whether the current link is available.

**Type:** `bool`

---

### 📌 `title`

This property returns the text of the current page's `title`.

**Type:** `str`

---

### 📌 `raw_data`

This property returns the accessed element data, which is the `content` attribute of the `Response` object.

**Type:** `bytes`

---

### 📌 `html`

This property returns the HTML text of the current page.

**Type:** `str`

---

### 📌 `json`

This property parses the returned content into JSON format.  
For example, when requesting an API, if the returned content is in JSON format, using the `html` property to retrieve it will return a string. Use this property to parse it into a `dict`.

**Type:** `dict`

---

### 📌 `user_agent`

This property returns the user_agent information of the current page.  

**Type:** `str`

---

## ✅️️ Runtime Parameter Information

### 📌 `timeout`

This property returns the network request timeout time. The default is 10 and can be set by assigning a value.

**Type:** `int`, `float`

```python
# Specify the timeout when creating the page object
page = SessionPage(timeout=5)

# Modify the timeout
page.timeout = 20
```

---

### 📌 `retry_times`

This property is the number of retries when a network connection fails. The default is 3 and can be set by assigning a value.

**Type:** `int`

```python
# Modify the number of retries
page.retry_times = 5
```

---

### 📌 `retry_interval`

This property is the waiting interval in seconds between retries when a network connection fails. The default is 2 and can be set by assigning a value.

**Type:** `int`, `float`

```python
# Modify the waiting interval for retries
page.retry_interval = 1.5
```

---

### 📌 `encoding`

This property returns the encoding format set by the user.

---

## ✅️️ Cookies Information

### 📌 `cookies()`

This method retrieves cookies and returns a `CookiesList` object.

Note that if different subdomains use the same `name` attribute, conversion to `{name: value}` may overwrite same-name entries.

---

### 📌 `cookies()` (options)

| Parameter Name | Type   | Default Value | Description                                                                               |
|:-------------:|:------:|:-------------:|-------------------------------------------------------------------------------------------|
| `all_domains` | `bool` | `False`       | Whether to return cookies of all domains. If `False`, it only returns the cookies of the current domain.                                                       |
| `all_info`    | `bool` | `False`       | Whether the returned cookies include all information. When `False`, it only includes the `name`, `value`, and `domain` information.                      |

| Return Type | Description |
|:------:|-------------|
| `CookiesList` | Cookie list object. Use `.as_dict()` when a dictionary is needed. |

**Example:**

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('http://www.baidu.com')
page.get('http://gitee.com')

for i in page.cookies(all_domains=True):
    print(i)
```

**Output:**

```
{'domain': '.baidu.com', 'domain_specified': True, ......}
......
{'domain': 'gitee.com', 'domain_specified': False, ......}
......
```

---

## ✅️️ Embedded Objects

### 📌 `session`

This property returns the `Session` object used by the current page object.

**Type:** `Session`

---

### 📌 `response`

This property is the `Response` object generated after requesting the webpage. For features not implemented in this library, you can directly access this property to use the native features of the requests library.

**Type:** `Response`

```python
# Print connection status
r = page.response
print(r.status_code)
```

