🚄 Page Settings
---

This section introduces the settings of `SessionPage`.

These settings are global parameters, and they will be used for each request after being set.

**Example:**

```python
from DrissionPage import SessionPage

page = SessionPage()
page.set.cookies([{'name': 'a', 'value': '1'}, {'name': 'b', 'value': '2'}])
```

## ✅️️ `set.retry_times()`

This method is used to set the number of retries when the connection fails.

| Parameter Name | Type | Default Value | Explanation |
| -------------- | ---- | ------------- | ----------- |
| `times` | `int` | Required | Number of times |

**Returns:** `None`

## ✅️️ `set.retry_interval()`

This method is used to set the interval between retries when the connection fails.

| Parameter Name | Type   | Default Value | Explanation |
| -------------- | ------ | ------------- | ----------- |
| `interval`     | `float` | Required      | Number of seconds |

**Returns:** `None`

## ✅️️ `set.timeout()`

This method is used to set the connection timeout.

| Parameter Name | Type   | Default Value | Explanation |
| -------------- | ------ | ------------- | ----------- |
| `second`       | `float` | Required      | Number of seconds |

**Returns:** `None`

**Example:**

```python
page.set.timeout(20)
```

---

## ✅️️ `set.encoding()`

This method is used to set the webpage encoding.

By default, the program will automatically retrieve the encoding from headers and the webpage. However, some webpages may have inaccurate encoding. In this case, you can set the encoding manually.

You can set it for a retrieved `Response` object or set it globally for all subsequent connections.

| Parameter Name | Type   | Default Value | Explanation |
| -------------- | ------ | ------------- | ----------- |
| `encoding`     | `str`  | Required      | The name of the encoding. To cancel the previous setting, pass `None`. |
| `set_all`      | `bool` | `True`        | Whether to set the object parameter. If `False`, only the current `Response` object will be set. |

**Returns:** `None`

---

## ✅️️ `set.cookies()`

This method is used to set one or more cookies.

| Parameter Name | Type                                                          | Default Value | Explanation |
| -------------- | ------------------------------------------------------------- | ------------- | ----------- |
| `cookies`      | `RequestsCookieJar`<br/>`list`<br/>`tuple`<br/>`str`<br/>`dict` | Required      | Accepts cookies in various formats |

**Returns:** `None`

---

## ✅️️ `set.cookies.clear()`

This method is used to clear all cookies.

**Parameters:** None

**Returns:** `None`

---

## ✅️️ `set.cookies.remove()`

This method is used to remove a cookie.

| Parameter Name | Type   | Default Value | Explanation       |
| -------------- | ------ | ------------- | ----------------- |
| `name`         | `str`  | Required      | The name of the cookie |

**Returns:** `None`

---

## ✅️️ `set.headers()`

This method is used to set headers, which will replace existing headers.

| Parameter Name | Type   | Default Value | Explanation      |
| -------------- | ------ | ------------- | ---------------- |
| `headers`      | `dict` | Required      | Universal headers |

**Returns:** `None`

---

## ✅️️ `set.header()`

This method is used to set an item in the headers.

| Parameter Name | Type   | Default Value | Explanation |
| -------------- | ------ | ------------- | ----------- |
| `attr`         | `str`  | Required      | The name of the setting |
| `value`        | `str`  | Required      | The value of the setting |

**Returns:** `None`

---

## ✅️️ `set.user_agent()`

This method is used to set the user_agent.

| Parameter Name | Type   | Default Value | Explanation     |
| -------------- | ------ | ------------- | --------------- |
| `ua`           | `str`  | Required      | User_agent info |

**Returns:** `None`

---

## ✅️️ `set.proxies()`

This method is used to set the proxy IP.

| Parameter Name | Type   | Default Value | Explanation                                          |
| -------------- | ------ | ------------- | ---------------------------------------------------- |
| `http`         | `str`  | Required      | The http proxy address                               |
| `https`        | `str`  | `None`        | The https proxy address. If `None`, the value of `http` will be used. |

**Returns:** `None`

---

## ✅️️ `set.auth()`

This method is used to set the authentication tuple or object.

| Parameter Name | Type                                   | Default Value | Explanation           |
| -------------- | -------------------------------------- | ------------- | --------------------- |
| `auth`         | `Tuple[str, str]`<br/>`HTTPBasicAuth` | Required      | The authentication tuple or object |

**Returns:** `None`

---

## ✅️️ `set.hooks()`

This method is used to set callback functions.

| Parameter Name | Type   | Default Value | Explanation |
| -------------- | ------ | ------------- | ----------- |
| `hooks`        | `dict` | Required      | Callback functions |

**Returns:** `None`

---

## ✅️️ `set.params()`

This method is used to set query parameter dictionary.

| Parameter Name | Type   | Default Value | Explanation      |
| -------------- | ------ | ------------- | ---------------- |
| `params`       | `dict` | Required      | Query parameter dictionary |

**Returns:** `None`

---

## ✅️️ `set.verify()`

This method is used to set whether to verify the SSL certificate.

| Parameter Name | Type   | Default Value | Explanation                         |
| -------------- | ------ | ------------- | ----------------------------------- |
| `on_off`       | `bool` | Required      | `bool` indicates on or off |

**Returns:** `None`

## ✅️️ `set.cert()`

This method is used to set the SSL client certificate.

| Parameter   | Type                         | Default | Description                                   |
|:------:|:--------------------------:|:---:| ---------------------------------------- |
| `cert` | `str`<br/>`Tuple[str, str]` | Required  | Path to the SSL client certificate file (.pem format), or a tuple of ('cert', 'key') |

**Returns:** `None`

---

## ✅️️ `set.stream()`

This method is used to set whether to use streaming response content.

| Parameter     | Type     | Default | Description          |
|:--------:|:------:|:---:| ----------- |
| `on_off` | `bool` | Required  | `bool` to represent on or off |

**Returns:** `None`

---

## ✅️️ `set.trust_env()`

This method is used to set whether to trust the environment.

| Parameter     | Type     | Default | Description          |
|:--------:|:------:|:---:| ----------- |
| `on_off` | `bool` | Required  | `bool` to represent on or off |

**Returns:** `None`

---

## ✅️️ `set.max_redirects()`

This method is used to set the maximum number of redirects.

| Parameter    | Type    | Default | Description      |
|:-------:|:-----:|:---:| ------- |
| ``times | `int` | Required  | Maximum number of redirects |

**Returns:** `None`

---

## ✅️️ `set.add_adapter()`

This method is used to add an adapter.

| Parameter      | Type            | Default | Description       |
|:---------:|:-------------:|:---:| -------- |
| `url`     | `str`         | Required  | URL corresponding to the adapter |
| `adapter` | `HTTPAdapter` | Required  | Adapter object    |

**Returns:** `None`

---

## ✅️️ `close()`

This method is used to close the connection.

**Parameters:** None

**Returns:** `None`

---

