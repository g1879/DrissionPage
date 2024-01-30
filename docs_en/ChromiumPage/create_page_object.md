🚤 Create Page Object
---

Both `ChromiumPage` and `WebPage` objects can send and receive data packets in d-mode. This section only introduces the creation of the `ChromiumPage` object, and will be further discussed in the chapter of `WebPage`.

Use `ChromiumPage()` to create a page object. Depending on different configurations, you can take over an already open browser or start a new browser.

When the program ends, the opened browser will not close automatically so that it can be used for the next program run. Beginners using headless mode should be aware that when the program is closed, the browser process is still running, just not visible.

Both `ChromiumPage` and `WebPage` objects are singletons and there can only be one object per browser. The same object will be obtained when repeating the use of `ChromiumPage` for the same browser.

## ✅️ Initialization Parameters for `ChromiumPage`

|   Initialization Parameters  |              Type              | Default | Explanation                                                                                 |
|:---------------------------:|:-----------------------------:|:-------:| ------------------------------------------------------------------------------------------- |
|       `addr_or_opts`        | `str`<br/>`int`<br/>`ChromiumOptions` |  `None` | Browser startup configuration or takeover information.<br/>When passing in a string with the format 'ip:port', a port number, or a `ChromiumOptions` object, the browser will be started or taken over according to the configuration;<br/>If `None`, the browser will be started using the configuration file. |
|          `tab_id`           |            `str`              |  `None` | The ID of the tab to be controlled. If `None`, the active tab will be controlled.               |
|         `timeout`           |           `float`             |  `None` | The overall timeout period. If `None`, it will be read from the configuration file, with a default value of 10. |

---

## ✅️ Create Directly

This method has the simplest code. The program will read the configuration from the default ini file and generate a page object automatically.

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
```

When creating a `ChromiumPage` object, the browser will be started on the specified port or take over an existing browser on that port.

By default, the program uses port 9222 and the path to the browser executable is `'chrome'`. If the browser executable is not found in the path, on Windows, the program will search for it in the registry.

If it is still not found, manual configuration using the next method is required.

:::warning Note
    Programs created using this method cannot be directly packaged because they rely on the ini file. Please refer to the methods in the section "Packaging Programs".
:::

:::tip Tips
    You can modify the configuration in the ini file to start all programs according to your needs. See the chapter "Startup Configuration" for more details.
:::

---

## ✅️ Creating Using Configuration Information

If you need to start the browser in a specified way, you can use `ChromiumOptions` for configuration. It is a class specifically used to set the initial status of the browser and comes with built-in common configurations. See the section "Browser Startup Configuration" for detailed usage methods.

### 📌 Usage

`ChromiumOptions` is used to manage the configuration when creating the browser. It comes with built-in common configurations and supports chain operations. See the section "Startup Configuration" for detailed usage methods.

|   Initialization Parameters  |              Type              | Default | Explanation                 |
|:---------------------------:|:-----------------------------:|:-------:| -------------------------- |
|       `read_file`           |          `bool`               |  `True` | Whether to read the configuration information from the ini file. If `False`, use the default configuration. |
|       `ini_path`            |           `str`               |  `None` | The path of the file. If `None`, read the default ini file.   |

:::warning Note
    - Configuration objects only take effect when the browser is started.
    - Modifying these configurations after the browser is created will have no effect.
    - Changing the configuration when taking over an already opened browser will also have no effect.
:::

```python
# Import ChromiumOptions
from DrissionPage import ChromiumPage, ChromiumOptions

# Create a browser configuration object and specify the browser path
co = ChromiumOptions().set_browser_path(r'D:\chrome.exe')
# Create a page object using this configuration
page = ChromiumPage(addr_or_opts=co)
```

---

### 📌 Creating Directly with a Specified Address

`ChromiumPage` can create a page directly by accepting the browser address in the format 'ip:port'.

Using this method, if the browser already exists, the program will directly take it over; if it does not exist, the program will read the configuration from the default ini file and start the browser on the specified port.

```python
page = ChromiumPage(addr_or_opts='127.0.0.1:9333')
```

---

### 📌 Creating Using a Specified ini File

The above methods create objects by using configuration information saved in the default ini file. You can save an ini file to another location and specify to use it when creating objects.

```python
from DrissionPage import ChromiumPage, ChromiumOptions

# Specify the ini file path when creating the configuration object
co = ChromiumOptions(ini_path=r'./config1.ini')
# Use this configuration object to create the page
page = ChromiumPage(addr_or_opts=co)
```

---

## ✅️ Taking Over an Already Opened Browser

When creating a page object, as long as there is already a browser running on the specified address (ip: port), it will be directly taken over, regardless of how the browser was started.

### 📌 Browser Started by the Program

By default, when creating a browser page object, it will automatically start a browser. As long as this browser is not closed, it will be taken over and continued to operate in the next program run (the configured ip: port information remains the same).

This method greatly facilitates program debugging, allowing the program to debug a specific function without having to restart every time.

```python
from DrissionPage import ChromiumPage

# Create an object and start the browser. If the browser already exists, take over it.
page = ChromiumPage()
```

---

### 📌 Manually Opened Browser

If you need to manually open the browser before taking over, you can do the following:

- Right-click on the browser icon and select Properties.

- Add ` --remote-debugging-port=port number --remote-allow-origins=*` after the "Target" path (note that there is a space at the beginning).

- Click OK.

- Specify the browser being taken over by the program in the browser configuration.

Target path of the file shortcut:

```
D:\chrome.exe --remote-debugging-port=9222 --remote-allow-origins=*
```

Program code:

```python
from DrissionPage import ChromiumPage, ChromiumOptions

co = ChromiumOptions().set_local_port(9222)
page = ChromiumPage(addr_or_opts=co)
```

:::warning Note
    When taking over the browser, only the `local_port` and `address` parameters are valid.
:::

---

### 📌 Browser Started by bat File

You can write the target path setting of the previous method into a bat file (for Windows system), run the bat file to start the browser, and then take over with the program.

Create a new text file and enter the following content in it (change the path to your own computer's):

```shell
"D:\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=*
```

Save it and change the extension to bat, then double-click to run it to start a browser on port 9222. The program code is the same as the previous method.

---

## ✅️ Multiple Browsers Coexistence

If you want to operate multiple browsers at the same time, or if you are using one of them to surf the Internet and controlling the rest automatically, you need to set separate **ports** and **user folders** for these browsers controlled by the program, otherwise conflicts may occur.

### 📌 Specify Independent Ports and Data Folders

Each browser to be started uses a separate `ChromiumOptions` object for configuration:

```python
from DrissionPage import ChromiumPage, ChromiumOptions

# Create multiple configuration objects, each specifying a different port number and user folder path
do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'D:\data1')
do2 = ChromiumOptions().set_paths(local_port=9222, user_data_path=r'D:\data2')

# Create multiple page objects
page1 = ChromiumPage(addr_or_opts=do1)
page2 = ChromiumPage(addr_or_opts=do2)

# Each page object controls a browser
page1.get('https://www.baidu.com')
page2.get('http://www.163.com')
```

:::tip Tips
    Each browser must set a separate port number and user folder, none of them can be missing.
:::

---

### 📌 `auto_port()` Method

The `auto_port()` method of the `ChromiumOptions` object can be used to specify that the program creates a browser using an available port and a temporary user folder each time. Each browser must also use a separate `ChromiumOptions` object.

However, browsers created using this method cannot be reused.

:::tip Tips
    `auto_port()` supports multi-threading, but not multi-processing.  
    When using multi-processing, the `scope` parameter can be used to specify the range of ports used by each process to avoid conflicts.
:::

```python
from DrissionPage import ChromiumPage, ChromiumOptions

co1 = ChromiumOptions().auto_port()
co2 = ChromiumOptions().auto_port()

page1 = ChromiumPage(addr_or_opts=co1)
page2 = ChromiumPage(addr_or_opts=co2)

page1.get('https://www.baidu.com')
page2.get('http://www.163.com')
```

---

### 📌 Automatically Assign in ini File

The automatically assigned configuration can be recorded in an ini file, so there is no need to create `ChromiumOptions`, and each browser started is independent and does not conflict. However, like `auto_port()`, these browsers cannot be reused.

```python
from DrissionPage import ChromiumOptions

ChromiumOptions().auto_port().save()
```

This piece of code records this configuration to the ini file. It only needs to be executed once, and if you want to close it, change the parameter to `False` and run it again.

```python
from DrissionPage import ChromiumPage

page1 = ChromiumPage()
page2 = ChromiumPage()

page1.get('https://www.baidu.com')
page2.get('http://www.163.com')
```

## ✅️ Use the System Browser's User Directory

By default, under the initial default configuration, the program will create an empty user directory for each port used, and use it each time it takes over, which effectively avoids browser conflicts.

Sometimes we want to use the default user folder of the system-installed browser in order to reuse user information and plugins, etc.

We can set it up like this:

### 📌 Use `ChromiumOptions`

Configure it each time it is started using `ChromiumOptions`.

```python
from DrissionPage import ChromiumPage, ChromiumOptions

co = ChromiumOptions().use_system_user_path()
page = ChromiumPage(co)
```

### 📌 Use ini File

Record this configuration to an ini file, so you don't have to configure it every time.

```python
from DrissionPage import ChromiumOptions

ChromiumOptions().use_system_user_path().save()
```

### 📌 Handling conflicts

If conflicts occur with an already open browser, an exception will be thrown and the user will be notified to close the browser.

```shell
DrissionPage.errors.BrowserConnectError: 
Failed to connect to 127.0.0.1:9222.
Please make sure:
1. The port belongs to a browser.
2. '--remote-debugging-port=9222' flag has been added as a startup option.
3. There is no conflict with an already open browser in the user's folder.
4. For headless systems, '--headless=new' parameter should be added.
5. For Linux systems, '--no-sandbox' startup parameter might also be required.
You can set the port and user folder path using ChromiumOptions.
```

---

## ✅️ Creating a brand new browser

By default, the program reuses the previously used browser user data, including login data and browsing history.

If you want to open a completely new browser, you can use the following methods:

### 📌 Using `auto_port()`

As mentioned before, by setting `auto_port()` method, each opened browser will be completely new.

An example can be seen in the previous section.

---

### 📌 Manually specifying the port and path

To open a completely new browser, specify an empty path for the browser user data folder and choose an available port.

```python
from DrissionPage import ChromiumPage, ChromiumOptions

co = ChromiumOptions().set_local_port(9333).set_user_data_path(r'C:\tmp')
page = ChromiumPage(co)
```

