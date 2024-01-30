⚙️ Using Configuration Files
---

This library uses ini files to record the startup configuration of browsers or `Session` objects. It facilitates configuration reuse and avoids adding cumbersome configuration information in the code.  
By default, the configuration information in the file is automatically loaded when the page object is started.  
You can also modify the default configuration and save it to the ini file using a simple method.  
Multiple ini files can be saved and called according to different project needs.

:::warning Note
    - Ini files are only used to manage startup configurations. Modifying the ini file after creating the page object has no effect.
    - These settings also have no effect if you take over an already opened browser.
    - Every time this library is upgraded, the ini file will be reset. You can save it to another path to avoid resetting.
:::

## ✅️️ Content of ini Files

The initial content of ini files is as follows.

```ini
[paths]
download_path = 
tmp_path = 

[chromium_options]
address = 127.0.0.1:9222
browser_path = chrome
arguments = ['--no-default-browser-check', '--disable-suggestions-ui', '--no-first-run', '--disable-infobars', '--disable-popup-blocking', '--disable-popup-blocking']
extensions = []
prefs = {'profile.default_content_settings.popups': 0, 'profile.default_content_setting_values': {'notifications': 2}}
flags = {}
load_mode = normal
user = Default
auto_port = False
system_user_path = False
existing_only = False

[session_options]
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'connection': 'keep-alive', 'accept-charset': 'GB2312,utf-8;q=0.7,*;q=0.7'}

[timeouts]
base = 10
page_load = 30
script = 30

[proxies]
http =
https = 

[others]
retry_times = 3
retry_interval = 2
```

---

## ✅️️ File Location

The default configuration file is stored in the _configs folder of the DrissionPage library, with the file name configs.ini.  
Users can save other configuration files or read configurations from saved files, but the location and name of the default file will not change.

---

## ✅️️ Starting with the Default Configuration File

### 📌 Automatically Loading with Page Object

This is the default startup method.

```python
from DrissionPage import WebPage

page = WebPage()
```

---

### 📌 Loading with Configuration Object

This method is generally used when the configuration needs to be further modified after loading.

```python
from DrissionPage import ChromiumOptions, SessionOptions, WebPage

co = ChromiumOptions(ini_path=r'D:\setting.ini')
so = SessionOptions(ini_path=r'D:\setting.ini')

page = WebPage(chromium_options=co, session_or_options=so)
```

---

## ✅️️ Saving/Creating a New ini File

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions()

# Modify some settings
co.no_imgs()

# Save to the currently opened ini file
co.save()
# Save to a specified location for the configuration file
co.save(r'D:\config1.ini')
# Save to the default configuration file
co.save_to_default()
```

---

## ✅️️ Using ini Files in Project Paths

The default ini file is stored in the DrissionPage installation directory, and modifications need to be made through code, which is inconvenient for debugging.

Therefore, a method is provided to conveniently copy the default ini file to the current project folder, and the program will prioritize using the ini file in the project folder for initialization configuration.

In this way, developers can easily manually change the configuration. Project packaging can also be done directly without causing any file not found issues.

The ini file copied to the project is named `'dp_configs.ini'`, and the program will read the configuration of this file by default.

### 📌 `configs_to_here()`

This method is located in the `DrissionPage.common` path and is used to copy the default ini file to the current path and rename it to `'dp_configs.ini'`.

| Parameter    | Type   | Default Value | Description                                                     |
| ------------ | ------ | ------------- | --------------------------------------------------------------- |
| `save_name`  | `str`  | `None`        | Specifies the file name. If `None`, it will be named `'dp_configs.ini'`. |

**Returns:** `None`

**Example:**

Create a new .py file in the project and enter the following content, then run it

```python
from DrissionPage.common import configs_to_here

configs_to_here()
```

Afterwards, the project folder will have a new `'dp_configs.ini'` file. This file will be prioritized when initializing the page object.

### 📌 Copying Using Command Line

In addition to using the `configs_to_here()` method to copy the ini file to the project folder, you can also use the command line to copy.

Run the following command in the project folder:

```shell
dp --configs-to-here
```

The effect is the same as `configs_to_here()`, but you cannot specify the file name.

