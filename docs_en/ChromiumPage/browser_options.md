🚤 Browser Startup Settings
---

The browser's startup configuration is very complicated. This library uses the `ChromiumOptions` class to manage startup configurations and provides built-in interfaces for commonly used configurations.

:::warning Note
    This object can only be used for browser startup. After the browser is started, modifying this configuration has no effect. When taking over an already opened browser, the startup configuration is also invalid.
:::

## ✅️️ Creating Objects

### 📌 Import

```python
from DrissionPage import ChromiumOptions
```

---

### 📌 `ChromiumOptions`

The `ChromiumOptions` object is used to manage browser initialization configurations. Configurations can be read from a configuration file for initialization.

| Initialization Parameter |       Type       | Default Value | Description                                                  |
| :----------------------: | :--------------: | :-----------: | ------------------------------------------------------------ |
|       `read_file`        |      `bool`      |    `True`     | Whether to read configurations from an ini file.<br/>If `False`, default configurations will be used. |
|        `ini_path`        | `Path`<br/>`str` |    `None`     | The path to the ini file. If `None`, the built-in ini file will be used. |

Creating the configuration object:

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions()
```

By default, the `ChromiumOptions` object reads configurations from an ini file. If the `read_file` parameter is set to `False`, default configurations will be used.

---

## ✅️️ Usage

After creating the configuration object, you can adjust the configuration content and pass it as a parameter when creating a page object. The page object will initialize the browser based on the configuration object.

The configuration object supports chaining operations.

```python
from DrissionPage import WebPage, ChromiumOptions

# Creating the configuration object (reading configurations from an ini file by default)
co = ChromiumOptions()
# Setting not to load images and mute
co.no_imgs(True).mute(True)

# Creating the page object with this configuration
page = WebPage(chromium_options=co)
```

```python
from DrissionPage import ChromiumOptions, ChromiumPage

co = ChromiumOptions()
co.incognito()  # Incognito mode
co.headless()  # Headless mode
co.set_argument('--no-sandbox')  # No sandbox mode
page = ChromiumPage(co)
```

---

## ✅️️ Command Line Arguments

The Chromium-based browsers have a series of startup configurations that start with `--`. They can be passed in when creating the browser to control browser behavior and initial state.

There are many startup parameters. For details, see: [List of Chromium Command Line Switches](https://peter.sh/experiments/chromium-command-line-switches/)

The `set_argument()` and `remove_argument()` methods are used to set command line arguments for browser startup.

### 📌 `set_argument()`

This method is used to set a startup argument.

|   Parameter   |         Type           |  Default Value  | Description                                        |
|:-------------:|:----------------------:|:---------------:|----------------------------------------------------|
|     `arg`     |         `str`          |      Required         | The name of the startup argument.                                             |
|    `value`    |     `str`<br/>`None`<br/>`False`  |      `None`       | The value of the argument. For arguments with values, pass the desired value. For arguments without values, pass `None`.<br/>If `False` is passed, the argument will be removed. |

|     Return Type         | Description                                        |
|:----------------------:|----------------------------------------------------|
|   `ChromiumOptions`   | The configuration object itself. |

**Example:** Setting arguments with and without values

```python
# Setting to start in maximized mode
co.set_argument('--start-maximized')
# Setting the initial window size
co.set_argument('--window-size', '800,600')
# Opening the browser in guest mode
co.set_argument('--guest')
```

---

### 📌 `remove_argument()`

This method is used to remove a startup argument from the configuration. Simply pass the argument name, no value is needed.

|    Parameter    |          Type          | Default Value  | Description                                        |
|:---------------:|:----------------------:|:--------------:|----------------------------------------------------|
|      `arg`      |         `str`          |    Required         | The name of the argument to be removed.                                             |

|     Return Type         | Description                                        |
|:----------------------:|----------------------------------------------------|
|   `ChromiumOptions`   | The configuration object itself. |

**Example:** Removing arguments with and without values

```python
# Removing the --start-maximized argument
co.remove_argument('--start-maximized')
# Removing the --window-size argument
co.remove_argument('--window-size')
```

---

## ✅️️ Running Path and Port

This section is for settings related to browser path, user folder path, and port.

### 📌 `set_browser_path()`

This method is used to set the path to the browser executable.

|     Parameter   |        Type        |  Default Value   | Description                                      |
|:---------------:|:-----------------:|:----------------:|--------------------------------------------------|
|      `path`     | `str`<br/>`Path`  |      Required          | The path to the browser executable file.          |

|    Return Type       | Description                                      |
|:-------------------:|--------------------------------------------------|
|   `ChromiumOptions` | The configuration object itself. |

If the passed string is not a path to a browser executable file, the default path will be used.

---

### 📌 `set_tmp_path()`

This method is used to set the path for temporary files.

|     Parameter   |        Type        |  Default Value   | Description                                      |
|:---------------:|:-----------------:|:----------------:|--------------------------------------------------|
|      `path`     | `str`<br/>`Path`  |      Required          | The path for temporary files.          |

|    Return Type       | Description                                      |
|:-------------------:|--------------------------------------------------|
|   `ChromiumOptions` | The configuration object itself. |

---

### 📌 `set_local_port()`

This method is used to set the local startup port.

| Parameter Name |     Type    | Default Value | Description |
|:--------------:|:-----------:|:-------------:|-------------|
|    `port`      | `str`<br/>`int` |    Required   | Port number |

| Return Type         | Description |
|---------------------|-------------|
| `ChromiumOptions`  | Configuration object itself |

---

### 📌 `set_address()`

This method is used to set the browser address in the format 'ip:port'.

It is mutually exclusive with `set_local_port()`.

| Parameter Name |  Type  | Default Value | Description |
|:--------------:|:-----:|:-----:|------------|
|   `address`    | `str` | Required | Browser address |

| Return Type         | Description |
|---------------------|-------------|
| `ChromiumOptions`  | Configuration object itself |

---

### 📌 `auto_port()`

This method is used to set whether to use an automatically assigned port and start a new browser.

If set to `True`, the program will automatically find an available port and create a folder in the specified path or the system temporary folder to store browser data.

Since the port and user folder are unique, browsers started in this way will not conflict with each other, but they cannot take over the same browser when starting the program multiple times.

The `set_local_port()`, `set_address()`, and `set_user_data_path()` methods will override `auto_port()`, i.e., the most recent call takes effect.

:::warning Note
    `auto_port()` supports multithreading but not multiprocessing.  
    When using multiprocessing, you can specify the port range for each process using the `scope` parameter to avoid conflicts.
:::

|   Parameter Name  |          Type          | Default Value |           Description           |
|:-----------------:|:---------------------:|:-------------:|---------------------------------|
|     `on_off`      |         `bool`         |     `True`    | Whether to enable automatic allocation of port and user folder |
|    `tmp_path`     | `str` `Path` object |     `None`    | Temporary file storage path. If `None`, it is saved in the system temporary folder. This parameter is invalid when `on_off` is `False` |
|      `scope`      |   `Tuple[int, int]`    |     `None`    | Specify the port range, excluding the last number. If `None`, use `[9600-19600)` |

| Return Type         | Description |
|---------------------|-------------|
| `ChromiumOptions`  | Configuration object itself |

**Example:**

```python
co.auto_port(True)
```

:::warning Note
    Once this feature is enabled, the port and a new temporary user data folder will be obtained. If you save the configuration to an ini file using the `save()` method at this time, the settings in the ini file will be overridden by the port and folder path. This override does not have a significant impact on usage.
:::

---

### 📌 `set_user_data_path()`

This method is used to set the user folder path. The user folder is used to store traces left by the account logged in the browser when using the browser, including setting options.

Usually, the name of the user folder is `User Data`. For the Chrome browser in Windows installed by default, this folder is located at `%USERPROFILE%\AppData\Local\Google\Chrome\User Data\`, which is inside the user directory of the current system login. The actual situation may vary. Please enter `chrome://version/` in the browser to check the `Profile Path` or `User Data Directory`. If you want to use independent user information, you can copy the entire `User Data` directory to another custom location and use the `set_user_data_path()` method in the code to fill in the custom location path. This way, you can use an independent user folder.

| Parameter Name |      Type       | Default Value |    Description    |
|:--------------:|:--------------:|:-------------:|------------------|
|     `path`     | `str`  `Path` |    Required   | User folder path |



| Return Type         | Description |
|---------------------|-------------|
| `ChromiumOptions`  | Configuration object itself |

---

### 📌 `use_system_user_path()`

This method sets whether to use the default user folder of the system-installed browser.

|  Parameter Name  |  Type  | Default Value |     Description     |
|:----------------:|:-----:|:-------------:|---------------------|
|     `on_off`     | `bool` |    `True`     | Boolean representing the on/off switch |

| Return Type         | Description |
|---------------------|-------------|
| `ChromiumOptions`  | Configuration object itself |

---

### 📌 `set_cache_path()`

This method is used to set the cache path.

| Parameter Name |      Type       | Default Value | Description |
|:--------------:|:--------------:|:-------------:|-------------|
|     `path`     | `str`<br/>`Path` |    Required   | Cache path |

| Return Type         | Description |
|---------------------|-------------|
| `ChromiumOptions`  | Configuration object itself |

---

### 📌 `existing_only()`

This method sets whether to only use an already started browser. If failed to connect to the target browser, an exception will be thrown and a new browser will not be started.

|  Parameter Name  |  Type  | Default Value |     Description     |
|:----------------:|:-----:|:-------------:|---------------------|
|     `on_off`     | `bool` |    `True`     | Boolean representing the on/off switch |

## 翻译 private_upload\default_user\2024-01-24-17-01-44\browser_options.md.part-2.md

# ✅️️ Using Plugins

`add_extension()` and `remove_extensions()` are used to set the plugins to be loaded when the browser starts. You can specify an unlimited number of plugins.

### 📌 `add_extension()`

This method is used to add a plugin to the browser.

| Parameter | Type            | Default | Description |
|-----------|-----------------|---------|-------------|
| `path`    | `str`<br/>`Path` | Required | Plugin path |

| Return Type      | Description          |
|------------------|----------------------|
| `ChromiumOptions` | The configuration object itself |

:::tip Tips
    According to the author's experience, it is more stable to unzip the plugin files into a separate folder and then point the plugin path to this folder.
:::

**Example:**

```python
co.add_extension(r'D:\SwitchyOmega')
```

---

### 📌 `remove_extensions()`

This method is used to remove all saved plugin paths in the configuration object. if you want to remove specific plugins, please remove all plugins first and then re-add the plugins you need.

**Parameters:** None

**Return:** The configuration object itself

```python
co.remove_extensions()
```

---

# ✅️️ User File Settings

In addition to startup parameters, a large amount of configuration information is saved in the browser's `preferences` file. If you want to use a separate user file for configuration information, refer to the [`set_user_data_path()`](https://g1879.gitee.io/drissionpagedocs/ChromiumPage/browser_options/#set_user_data_path) method on this page.

:::warning Note
    The `preferences` file is the configuration file for Chromium-based browsers, which is completely different from DrissionPage's `configs.ini`.
:::

The following methods are used to configure browser user files.

### 📌 `set_user()`

The Chromium browser supports multiple user configurations, and we can choose which one to use. The default is `'Default'`.

| Parameter | Type   | Default     | Description               |
|-----------|--------|-------------|---------------------------|
| `user`    | `str`  | `'Default'` | User profile folder name  |

| Return Type      | Description          |
|------------------|----------------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.set_user(user='Profile 1')
```

---

### 📌 `set_pref()`

This method is used to set a configuration item in the user profile.

Where can all the configuration items be found? The author couldn't find them either. Please let me know if you know. Thank you.

| Parameter | Type   | Default | Description    |
|-----------|--------|---------|----------------|
| `arg`     | `str`  | Required | Setting name   |
| `value`   | `str`  | Required | Setting value  |

| Return Type      | Description          |
|------------------|----------------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
# Disable all pop-up windows
co.set_pref(arg='profile.default_content_settings.popups', value='0')
# Hide the prompt to save passwords
co.set_pref('credentials_enable_service', False)
```

---

### 📌 `remove_pref()`

This method is used to delete a `pref` configuration item in the current configuration object.

| Parameter | Type   | Default | Description    |
|-----------|--------|---------|----------------|
| `arg`     | `str`  | Required | Setting name   |

| Return Type      | Description          |
|------------------|----------------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.remove_pref(arg='profile.default_content_settings.popups')
```

---

### 📌 `remove_pref_from_file()`

This method is used to delete a configuration item in the user profile. Note that it is different from the previous method. If a certain item already exists in the user profile, it cannot be deleted using `remove_pref()`, but can only be deleted using `remove_pref_from_file()`.

| Parameter | Type   | Default | Description    |
|-----------|--------|---------|----------------|
| `arg`     | `str`  | Required | Setting name   |

| Return Type      | Description          |
|------------------|----------------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.remove_pref_from_file(arg='profile.default_content_settings.popups')
```

---

# ✅️️ Running Parameter Settings

The parameters required for the page object to run can also be set in `ChromiumOptions`.

### 📌 `set_timeouts()`

This method is used to set several timeout times in seconds. For the usage of timeout, refer to the Usage section.

| Parameter | Type   | Default | Description                                                                                                                                                                      |
|-----------|--------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `base`    | `float` | `None`  | Default timeout, used for element waiting, alert waiting, `WebPage`'s s mode connection, etc.  In scenes other than the following two parameters, this setting is used by default. |
| `pageLoad`   | `float` | `None`  | Page loading timeout                                                                                                                              |
| `script`  | `float` | `None`  | JavaScript execution timeout                                                                                                                      |

| Return Type      | Description          |
|------------------|----------------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.set_timeouts(base=10)
```

---

### 📌 `set_retry()`

This method is used to set the number of retries and interval when the page connection times out.

This method is used to set whether to disable JavaScript.

| Parameter Name | Type  | Default Value | Description |
|:--------------:|:-----:|:-------------:|-------------|
|   `on_off`     | `bool`|     `True`    | `True` to enable, `False` to disable |

| Return Type     | Description |
|-----------------|-------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.no_js(True)
```

This method is used to set whether JavaScript is disabled.

| Parameter Name | Type  | Default Value | Description |
|--------------|------|--------------|------------|
| `on_off`     | `bool` | `True`       | `True` and `False` indicate on or off |

| Return Type      | Description |
|------------------|-------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.no_js(True)
```

---

### 📌 `mute()`

This method is used to set whether to mute.

| Parameter Name | Type  | Default Value | Description |
|--------------|------|--------------|------------|
| `on_off`     | `bool` | `True`       | `True` and `False` indicate on or off |

| Return Type      | Description |
|------------------|-------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.mute(True)
```

---

### 📌 `set_user_agent()`

This method is used to set the user agent.

|   Parameter Name    | Type  | Default Value | Description |
|--------------------|-------|--------------|------------|
| `user_agent`       | `str` | Required     | user agent text |

| Return Type      | Description |
|------------------|-------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.set_user_agent(user_agent='Mozilla/5.0 (Macintos.....')
```

---

### 📌 `set_paths()`

This method is used to set various path information. Set the paths with input values, and ignore those with `None`.

The functionality of this method is repetitive with the previously introduced path setting methods, but integrates several methods together.

|    Parameter Name    |        Type        | Default Value | Description |
|----------------------|--------------------|---------------|-------------|
|  `browser_path`      | `str`<br/>`Path`   | `None`        | The path of the browser executable file |
|  `local_port`        | `str`<br/>`int`    | `None`        | The local port number that the browser will use |
|  `address`           | `str`              | `None`        | The browser address, e.g. 127.0.0.1:9222. If set together with` local_port`, it will override the value of `local_port` |
|  `download_path`     | `str`<br/>`Path`   | `None`        | The default save path for downloaded files |
|  `user_data_path`    | `str`<br/>`Path`   | `None`        | The path of the user data folder |
|  `cache_path`        | `str`<br/>`Path`   | `None`        | The path of the cache |

| Return Type      | Description |
|------------------|-------------|
| `ChromiumOptions` | The configuration object itself |

**Example:**

```python
co.set_paths(local_port=9333, user_data_path=r'D:\tmp')
```

---

## ✅️️ Save settings to file

The ini file is the configuration file of DrissionPage, which persistently records some configuration parameters. You can save different configurations to separate ini files in order to adapt to different scenarios.

### 📌 `save()`

This method is used to save configuration items to an ini file.

| Parameter Name |       Type        | Default Value | Description |
|--------------|----------------|---------------|-------------|
| `path`       | `str`<br/>`Path` | `None`        | The path of the ini file. If `None` is passed in, it will be saved to the currently read configuration file |

| Return Type  | Description |
|--------------|-------------|
| `str`        | The absolute path of the saved ini file |

**Example:**

```python
# Save the currently read ini file
co.save()

# Save the current configuration to the specified path
co.save(path=r'D:\tmp\settings.ini')
```

If the custom ini file path was not specified with ChromiumPage() before, then the default ini file will be used. This is when `save()` is used, its functionality is consistent with `save_to_default()`, both of which save to the default configuration file.

---

### 📌 `save_to_default()`

This method is used to save configuration items to a fixed default ini file. The default ini file refers to the one built into DrissionPage.

**Parameters:** None

| Return Type  | Description |
|--------------|-------------|
| `str`        | The absolute path of the saved ini file |

**Example:**

```python
co.save_to_default()
```

By default, the default ini file is located in the Python installation directory at `Lib\site-packages\DrissionPage\_configs\configs.ini`. Please do not modify the default ini file without necessity. For the initial contents of the ini file, please [click this link](https://g1879.gitee.io/drissionpagedocs/advance/ini_file/).

---

## ✅️️ `ChromiumOptions` Properties

### 📌 `address`

This property is the address of the browser to be controlled, in the format of ip:port, default is `'127.0.0.0:9222'`.

**Type:** `str`

---

### 📌 `browser_path`

This property returns the path to the browser executable file.

**Type:** `str`

---

### 📌 `user_data_path`

This property returns the path of the user data folder.

**Type:** `str`

---

### 📌 `tmp_path`

This property returns the path of the temporary folder, which can be used to save the automatically assigned user folder path.

**Type:** `str`

---

### 📌 `download_path`

This property returns the path of the default download path file.

**Type:** `str`

---

### 📌 `user`

This property returns the name of the user's configuration folder.

**Type:** `str`

---

### 📌 `page_load_strategy`

This property returns the page loading strategy. There are three options: `'normal'`, `'eager'`, and `'none'`.

**Type:** `str`

---

### 📌 `timeouts`

This property returns the timeout settings. It includes three options: `'base'`, `'pageLoad'`, `'script'`.

**Type:** `dict`

```python
print(co.timeouts)
```

**Output:**

```shell
{
    'base': 10,
    'pageLoad': 30,
    'script': 30
}
```

---

### 📌 `retry_times`

This property returns the number of retries when the connection fails.

**Type:** `int`

---

### 📌 `retry_interval`

This property returns the retry interval (in seconds) when the connection fails.

**Type:** `float`

---

### 📌 `proxy`

This property returns the proxy settings.

**Type:** `str`

---

### 📌 `arguments`

This property returns the browser startup arguments as a list.

**Type:** `list`

---

### 📌 `extensions`

This property returns the paths of the extensions to be loaded as a list.

**Type:** `list`

---

### 📌 `preferences`

This property returns the user preference configuration.

**Type:** `dict`

---

### 📌 `system_user_path`

This property returns whether to use the browser's user folder as per the system.

**Type:** `bool`

---

### 📌 `is_existing_only`

This property returns whether to only use already opened browsers.

**Type:** `bool`

---

### 📌 `is_auto_port`

This property returns whether to only use automatically assigned ports and user folder paths.

**Type:** `bool`

