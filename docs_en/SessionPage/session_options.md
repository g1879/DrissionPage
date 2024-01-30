🚄 Session Options
---

This section introduces the startup configuration of the `SessionPage`.

We manage the initial configuration of the `SessionPage` object using the `SessionOptions` object.

:::warning Note
    `SessionOptions` is only used to manage the startup configuration and cannot be modified after the program starts.
:::

## ✅️️ Creating an Object

### 📌 Import

```python
from DrissionPage import SessionOptions
```

---

### 📌 `SessionOptions`

The `SessionOptions` object is used to manage the initialization configuration of the `Session` object. Configuration can be read from a configuration file for initialization.

| Initialization Parameter | Type              | Default Value | Description                                    |
|:------------------------:|:-----------------:|:-------------:| ---------------------------------------------- |
| `read_file`              | `bool`            | `True`        | Whether to read the configuration from an ini file. If `False`, the default configuration will be used. |
| `ini_path`               | `Path`<br/>`str`  | `None`        | The path to the ini file. If `None`, the built-in ini file will be read.    |

Create a configuration object:

```python
from DrissionPage import SessionOptions

so = SessionOptions()
```

By default, the `SessionOptions` object will read the configuration from an ini file. If the `read_file` parameter is specified as `False`, it will be created with the default configuration.

---

## ✅️️ Usage

After creating the configuration object, you can adjust the configuration content and then pass the configuration object as a parameter when creating the page object.

```python
from DrissionPage import SessionPage, SessionOptions

# Create a configuration object (read configuration from ini file by default)
so = SessionOptions()
# Set the proxy
so.set_proxies('http://localhost:1080')
# Set cookies
cookies = ['key1=val1; domain=xxxx', 'key2=val2; domain=xxxx']
so.set_cookies(cookies)

# Create the page object with this configuration
page = SessionPage(session_or_options=so)
```

---

## ✅️️ Methods for Setting Configuration

### 📌 `set_headers()`

This method is used to set the entire `headers` parameter, and the value passed in will override the original `headers`.

| Parameter Name  | Type     | Default Value | Description                  |
|:---------------:|:--------:|:-------------:| ---------------------------- |
| `headers`       | `dict`   | Required      | Complete headers dictionary  |

| Return Type              | Description                                |
|--------------------------|--------------------------------------------|
| `SessionOptions`         | The configuration object itself             |

**Example:**

```python
so.set_headers = {'user-agent': 'Mozilla/5.0 (Macint...', 'connection': 'keep-alive' ...}
```

---

### 📌 `set_a_header()`

This method is used to set an item in the `headers`.

| Parameter Name  | Type     | Default Value | Description |
|:---------------:|:--------:|:-------------:| ----------- |
| `attr`          | `str`    | Required      | Name        |
| `value`         | `str`    | Required      | Value       |

| Return Type              | Description                                |
|--------------------------|--------------------------------------------|
| `SessionOptions`         | The configuration object itself             |

**Example:**

```python
so.set_a_header('accept', 'text/html')
so.set_a_header('Accept-Charset', 'GB2312')
```

**Output:**

```
{'accept': 'text/html', 'accept-charset': 'GB2312'}
```

---

### 📌 `remove_a_header()`

This method is used to remove a setting from the `headers`.

| Parameter Name  | Type     | Default Value | Description |
|:---------------:|:--------:|:-------------:| ----------- |
| `attr`          | `str`    | Required      | Setting to remove |

| Return Type              | Description                                |
|--------------------------|--------------------------------------------|
| `SessionOptions`         | The configuration object itself             |

**Example:**

```python
so.remove_a_header('accept')
```

---

### 📌 `set_cookies()`

This method is used to set cookie information. Each setting will overwrite all previously set cookie information.

| Parameter Name   | Type                                                          | Default Value | Description |
|:----------------:|:-------------------------------------------------------------:|:-------------:| ----------- |
| `cookies`        | `RequestsCookieJar`<br/>`list`<br/>`tuple`<br/>`str`<br/>`dict` | Required      | Cookies     |

| Return Type              | Description                                |
|--------------------------|--------------------------------------------|
| `SessionOptions`         | The configuration object itself             |

**Example:**

```python
cookies = ['key1=val1; domain=xxxx', 'key2=val2; domain=xxxx']
so.set_cookies(cookies)
```

---

### 📌 `set_timeout()`

This method is used to set the connection timeout attribute.

| Parameter Name  | Type     | Default Value | Description     |
|:---------------:|:--------:|:-------------:| ----------------|
| `second`        | `float`  | Required      | Connection waiting time in seconds |

| Return Type              | Description                                |
|--------------------------|--------------------------------------------|
| `SessionOptions`         | The configuration object itself             |

---

### 📌 `set_retry()`

This method is used to set the number of retries and the interval when the connection times out.

|    Parameter Name    |   Type    |  Default Value | Description                   |
|:--------------------:|:---------:|:-------------:| ------------------------------|
| `times`              |  `int`    | `None`        | Number of retries when the connection fails    |
| `interval`           | `float`   | `None`        | The interval between failed connection attempts (in seconds)  |

| Return Type              | Description                                |
|--------------------------|--------------------------------------------|
| `ChromiumOptions`         | The configuration object itself             |

---

### 📌 `retry_times`

This property returns the number of retries when the connection fails.

**Type:** `int`

---

### 📌 `retry_interval`

This property returns the interval between failed connection attempts (in seconds).

**Type:** `float`

---

### 📌 `set_proxies()`

This method is used to set proxy information.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `http` | `str` | required | http proxy address |
| `https` | `str` | `None` | https proxy address, use the value of `http` parameter when `None` |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

**Example:**

```python
so.set_proxies('http://127.0.0.1:1080')
```

---

### 📌 `set_download_path()`

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `path` | `str`<br/>`Path` | required  | Default download save path |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `set_auth()`

This method is used to set authentication tuple information.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `auth` | `tuple`<br/>`HTTPBasicAuth` | required  | Authentication tuple or object |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `set_hooks()`

This method is used to set callback methods.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `hooks` | `dict` | required  | Callback method |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `set_params()`

This method is used to set query parameters.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `params` | `dict` | required  | Query parameter dictionary |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `set_cert()`

This method is used to set the path of the SSL client certificate file (.pem format) or ('cert', 'key') tuple.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `cert` | `str`<br/>`tuple` | required  | Certificate path or tuple |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `set_verify()`

This method is used to set whether to verify SSL certificate.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `on_off` | `bool` | required  | `bool` indicates on or off |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `add_adapter()`

This method is used to add an adapter.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `url` | `str` | required  | Adapter corresponding url |
| `adapter` | `HTTPAdapter` | required  | Adapter object |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `set_stream()`

This method is used to set whether to use streaming response content.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `on_off` | `bool` | required  | `bool` indicates on or off |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `set_trust_env()`

This method is used to set whether to trust the environment.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `on_off` | `bool` | required  | `bool` indicates on or off |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

### 📌 `set_max_redirects()`

This method is used to set the maximum number of redirects.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `times` | `int` | required  | Maximum number of redirects |

| Return Type | Description |
| ----------- | ----------- |
| `SessionOptions` | The configuration object itself |

---

## ✅️️ Save settings to file

You can save different configurations to their own ini files to adapt to different scenarios.

:::warning Note
    `hooks` and `adapters` configurations will not be saved in the file.
:::

### 📌 `save()`

This method is used to save configuration items to an ini file.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:| ----------- |
| `path` | `str`<br/>`Path` | `None` | The path of the ini file, pass `None` to save to the currently read configuration file |

| Return Type | Description |
| ----------- | ----------- |
| `str` | Absolute path of the saved ini file |

**Example:**

```python
# Save the currently read ini file
so.save()

# Save current configuration to a specified path
so.save(path=r'D:\tmp\settings.ini')
```

---

### 📌 `save_to_default()`

This method is used to save configuration items to a fixed default ini file. The default ini file refers to the one built-in with DrissionPage.

**Parameter:** None

| Return Type | Description                     |
| ----------- | ------------------------------- |
| `str`       | Absolute path of the saved ini file |

**Example:**

```python
so.save_to_default()
```

---

## ✅️️ `SessionOptions` Properties

### 📌 `headers`

This property returns the headers configuration.

**Type:** `dict`

---

### 📌 `cookies`

This property returns the cookies configuration in a `list` format.

**Type:** `list`

---

### 📌 `proxies`

This property returns the proxy configuration.

**Type:** `dict`
**Format:** `{'http': 'http://xx.xx.xx.xx:xxxx', 'https': 'http://xx.xx.xx.xx:xxxx'}`

---

### 📌 `auth`

This property returns the authentication configuration.

**Type:** `tuple`, `HTTPBasicAuth`

---

### 📌 `hooks`

This property returns the callback methods configuration.

**Type:** `dict`

---

### 📌 `params`

This property returns the query parameters configuration.

**Type:** `dict`

---

### 📌 `verify`

This property returns the SSL certificate verification configuration.

**Type:** `bool`

---

### 📌 `cert`

This property returns the SSL certificate configuration.

**Type:** `str`, `tuple`

---

### 📌 `adapters`

This property returns the adapter configuration.

**Type:** `List[HTTPAdapter]`

---

### 📌 `stream`

This property returns the streaming response configuration.

**Type:** `bool`

---

### 📌 `trust_env`

This property returns the trust environment configuration.

**Type:** `bool`

---

### 📌 `max_redirects`

This property returns the `max_redirects` configuration.

**Type:** `int`

---

### 📌 `timeout`

This property returns the connection timeout configuration.

**Type:** `int`, `float`

---

### 📌 `download_path`

This property returns the default download path configuration.

**Type:** `str`

