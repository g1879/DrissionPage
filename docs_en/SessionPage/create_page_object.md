🚄 Creating Page Objects
---

Both the `SessionPage` and `WebPage` objects can send and receive packets. In this section, we will only focus on creating the `SessionPage` object. The `WebPage` object will be introduced in the chapter about web pages.

## ✅️️ Initialization Parameters for `SessionPage`

The `SessionPage` object is the simplest among the three page objects.

| Initialization Parameter | Type                                     | Default Value | Description                                                                 |
|-------------------------|------------------------------------------|---------------|-----------------------------------------------------------------------------|
| `session_or_options`     | `Session`<br/>`SessionOptions`              | `None`        | If a `Session` object is provided, it will be used to send and receive packets. If a `SessionOptions` object is provided, it will be used to create a `Session` object with the specified configuration. |
| `timeout`                | `float`                                    | `None`        | The connection timeout. If `None`, it will be read from the configuration file. |

---

## ✅️️ Create Directly

This method is the most concise, as the program will automatically generate the page object by reading the configuration from the configuration file.

```python
from DrissionPage import SessionPage

page = SessionPage()
```

`SessionPage` does not require controlling the browser or any additional configuration.

:::warning Warning
    Programs created using this method cannot be directly packaged, as they rely on an ini file. Please refer to the "Packaging Programs" section for a solution.
:::

---

## ✅️️ Create Using Configuration Information

If you need to configure the page object before using it, you can use `SessionOptions`. It is specifically designed for setting the initial state of a `Session` object and comes with built-in common configurations. For detailed usage instructions, please refer to the "Startup Configuration" section.

### 📌 Usage

When creating a `SessionPage`, pass the already created and configured `SessionOptions` object as a parameter.

| Initialization Parameter | Type    | Default Value | Description                          |
|-------------------------|---------|---------------|--------------------------------------|
| `read_file`             | `bool`  | `True`        | Whether to read the configuration information from an ini file. |
| `ini_path`              | `str`   | `None`        | The file path. If `None`, it will read from the default ini file. |

:::warning Warning
    Modifying this configuration after creating the `Session` object will have no effect.
:::

```python
# Import SessionOptions
from DrissionPage import SessionPage, SessionOptions

# Create a configuration object and set the proxy information
so = SessionOptions().set_proxies(http='127.0.0.1:1080')
# Create the page object using this configuration
page = SessionPage(session_or_options=so)
```

:::tip Tips
    You can save the configuration to a configuration file for automatic reading in the future. Please refer to the "Startup Configuration" chapter for more information.
:::

---

### 📌 Create from a Specified ini File

The above methods use the configuration information saved in the default ini file to create the object. However, you can save an ini file somewhere else and specify its location when creating the object.

```python
from DrissionPage import SessionPage, SessionOptions

# Specify the ini file path when creating the configuration object
so = SessionOptions(ini_path=r'./config1.ini')
# Create the page object using this configuration object
page = SessionPage(session_or_options=so)
```

---

### 📌 Do Not Use an ini File

By default, an ini file is used. However, for convenience, you can specify the configuration in the code instead of an ini file.

```python
from DrissionPage import SessionPage, SessionOptions

so = SessionOptions(read_file=False)  # Set `read_file` to False
so.set_retry(5)
page = SessionPage(so)
```

---

## ✅️️ Passing Control

When multiple page objects need to work together to operate on a single page, you can pass a `Session` object from one page object to another to allow them to share the same `Session` object.

```python
# Create a page object
page1 = SessionPage()
# Get the built-in Session object from the page object
session = page1.session
# Pass the session object when initializing the second page object
page2 = SessionPage(session_or_options=session)
```

