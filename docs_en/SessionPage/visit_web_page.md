🚄 Visit Web Page
---

The s mode of `SessionPage` and `WebPage` is based on the requests library for network connections, so all request methods built into requests can be used, including `get()`, `post()`, `head()`, `options()`, `put()`, `patch()`, and `delete()`. However, this library currently only encapsulates and optimizes `get()` and `post()` methods, and other methods can be used by calling the builtin `Session` object of the page. This document only explains `SessionPage`, and `WebPage` will be introduced in separate sections.

## ✅️️ `get()`

### 📌 Visit Online Web Pages

The syntax of the `get()` method is the same as the `get()` method of requests, with the addition of retrying connection failures. Unlike requests, it does not return a `Response` object.

| Parameter Name | Type   | Default | Description                          |
| -------------- | ------ | ------- | ------------------------------------ |
| `url`          | `str`  | required | Target URL                            |
| `show_errmsg`  | `bool` | `False` | Whether to display and raise an exception when a connection error occurs |
| `retry`        | `int`  | `None`  | Number of retries, if `None`, use the page parameter, default is 3 |
| `interval`     | `float`| `None`  | Retry interval (in seconds), if `None`, use the page parameter, default is 2 |
| `timeout`      | `float`| `None`  | Loading timeout (in seconds)                  |
| `**kwargs`     | -      | `None`  | Other parameters required for connection, see the requests documentation for details |

| Return Type | Description     |
| ----------- | --------------- |
| `bool`      | Whether the connection is successful |

The `**kwargs` parameter has the same usage as the corresponding parameter in requests. However, if a certain item is set in this parameter (e.g., `headers`), each item in that item will override the corresponding item read from the configuration instead of completely replacing it. 
That means if you want to continue using the `headers` information in the configuration and only want to modify one item, you only need to pass the value of that item. This simplifies the code logic.

Practical Features:

- The program automatically adds the `Host` and `Referer` items to `headers` based on the website to be accessed
- The program automatically determines the encoding from the returned content, so manual setting is generally not required

Simple access to web pages:

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('http://g1879.gitee.io/drissionpage')
```

Access web pages with connection parameters:

```python
from DrissionPage import SessionPage

page = SessionPage()

url = 'https://www.baidu.com'
headers = {'referer': 'gitee.com'}
cookies = {'name': 'value'}
proxies = {'http': '127.0.0.1:1080', 'https': '127.0.0.1:1080'}
page.get(url, headers=headers, cookies=cookies, proxies=proxies)
```

---

### 📌 Read Local Files

The `url` parameter of `get()` can point to a local file to implement local HTML parsing.

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get(r'D:\demo.html')
```

---

## ✅️️ `post()`

This method requests a page using the POST method. It can be used in the same way as `get()`.

| Parameter Name | Type   | Default | Description                          |
| -------------- | ------ | ------- | ------------------------------------ |
| `url`          | `str`  | required | Target URL                            |
| `show_errmsg`  | `bool` | `False` | Whether to display and raise an exception when a connection error occurs |
| `retry`        | `int`  | `None`  | Number of retries, if `None`, use the page parameter, default is 3 |
| `interval`     | `float`| `None`  | Retry interval (in seconds), if `None`, use the page parameter, default is 2 |
| `**kwargs`     | -      | `None`  | Other parameters required for connection, see the requests documentation for details |

| Return Type | Description     |
| ----------- | --------------- |
| `bool`      | Whether the connection is successful |

```python
from DrissionPage import SessionPage

page = SessionPage()
data = {'username': 'xxxxx', 'pwd': 'xxxxx'}

page.post('http://example.com', data=data)
# Or
page.post('http://example.com', json=data)
```

Both the `data` parameter and `json` parameter can accept `str` and `dict` format data, which means there are 4 ways to pass data:

```python
# Pass a string to the data parameter
page.post(url, data='abc=123')

# Pass a dictionary to the data parameter
page.post(url, data={'abc': '123'})

# Pass a string to the json parameter
page.post(url, json='abc=123')

# Pass a dictionary to the json parameter
page.post(url, json={'abc': '123'})
```

Which one to use depends on the server requirements.

---

## ✅️️ Other Request Methods

This library only optimizes the commonly used get and post methods, but other request methods can also be executed in the native requests code manner by extracting the `Session` object inside the page object.

```python
from DrissionPage import SessionPage

page = SessionPage()
# Get the builtin session object
session = page.session
# Send a request using the head method
response = session.head('https://www.baidu.com')
print(response.headers)
```

**Output:**

```shell
{'Accept-Ranges': 'bytes', 'Cache-Control': 'private, no-cache, no-store, proxy-revalidate, no-transform', 'Connection': 'keep-alive', 'Content-Length': '277', 'Content-Type': 'text/html', 'Date': 'Tue, 04 Jan 2022 06:49:18 GMT', 'Etag': '"575e1f72-115"', 'Last-Modified': 'Mon, 13 Jun 2016 02:50:26 GMT', 'Pragma': 'no-cache', 'Server': 'bfe/1.0.8.18'}
```

