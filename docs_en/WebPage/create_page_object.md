🛸 Create Page Object
---

This section introduces the creation of the `WebPage` object.

The `WebPage` object has two modes: "d" mode for manipulating the browser and "s" mode for sending and receiving packets.

## ✅️️ `WebPage` Initialization Parameters

| Initialization Parameter  | Type                                              | Default | Description                                                                                                                                 |
|:------------------------:|:-------------------------------------------------:|:-------:| ------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                   | `str`                                             | `'d'`   | Can only receive `'d'` or `'s'`, indicating initial selection for manipulating the browser or sending and receiving packets                                          |
| `timeout`                | `float`                                           | `None`  | Overall timeout, if `None`, read from the configuration file, default is 10                                                                 |
| `chromium_options`       | `ChromiumOptions`<br/>`False`                     | `None`  | Default is `None`, indicating reading the configuration from the ini file<br/>When receive `ChromiumOptions`, use this configuration to start or take over the browser<br/>If not using d mode, receive `False` to avoid packaging errors       |
| `session_or_options`     | `Session`<br/>`SessionOptions`<br/>`False`        | `None`  | Default is `None`, indicating reading the configuration from the ini file<br/>When receive `Session`, directly use an already created `Session` object<br/>When receive `SessionOptions`, use this configuration to create a `Session` object<br/>If not using s mode, receive `False` to avoid packaging errors |

---

## ✅️️ Creating Directly

This method has the simplest code and the program will read the configuration from the default ini file and generate the page object automatically.

When creating, you can specify the initial mode.

```python
from DrissionPage import WebPage

# Create an object in d mode by default
page = WebPage()

# Create an object in s mode
page = WebPage('s')
```

Creating `WebPage` object in d mode will start the browser on the specified port or take over the existing browser on that port.

By default, the program uses port 9222 and the executable file path of the browser is `'chrome'`. If the browser executable file is not found in the path, the program will search for the path in the registry on Windows system. If it is still not found, the next method needs to be configured manually.

:::warning Note
    Programs created using this method cannot be packaged directly because they use the ini file. Refer to the methods in the "Packaging Programs" section.
:::

:::tip Tips
    You can modify the configuration in the configuration file to start as you need for all programs. Refer to the "Startup Configuration" section for details.
:::

---

## ✅️️ Creating with Configuration Information

If you need to start the browser in a specified way, you can use `ChromiumOptions` and `SessionOptions`. Their usage has been introduced in their respective sections, and here we only demonstrate how to use them when creating `WebPage`.

### 📌 Usage

Create two configuration objects and pass them to the initialization method of `WebPage`.

```python
from DrissionPage import WebPage, ChromiumOptions, SessionOptions

co = ChromiumOptions()
so = SessionOptions()

page = WebPage(chromium_options=co, session_or_options=so)
```

If you only need to modify the configuration for one mode and use the configuration from the ini file for the other mode, you can only pass one type of configuration object.

```python
from DrissionPage import WebPage, ChromiumOptions

co = ChromiumOptions()
page = WebPage(chromium_options=co)
```

:::info Note
    When both `ChromiumOptions` and `SessionOptions` are passed, the attributes both have will refer to the `ChromiumOptions`. For example, `timeout` and `download_path`.
:::

---

### 📌 Creating with a Specified ini File

The above methods create objects using the configuration information saved in the default ini file. You can save an ini file to another location and specify to use it when creating objects.

```python
from DrissionPage import WebPage, ChromiumOptions, SessionOptions

co = ChromiumOptions(ini_path=r'./config1.ini')
so = SessionOptions(ini_path=r'./config1.ini')

page = ChromiumPage(addr_or_opts=co, session_or_options=so)
```

---

