🚤 Tab Page Operations
---

This section introduces the management and usage skills of browser tabs.

A Tab object (`ChromiumTab` and `WebPageTab`) controls a browser tab and is the main unit of page control.

A tab can also be controlled by multiple Tab objects at the same time (singleton needs to be disabled).

`ChromiumPage` and `WebPage` are tab managers that also control a tab, but they add some overall browser control functions.

:::info Explanation
    `ChromiumPage` and `WebPage` have all the functionality of tab control.
    `ChromiumTab` and `WebPageTab`, on the other hand, only have the ability to close and activate themselves.
:::

## ✅️️ Multi-Tab Usage

Selenium does not have a tab object, and the driver can only manipulate one tab at a time. When using multiple tabs, you need to switch back and forth between different tabs, and when switching, you will lose the elements that you have previously acquired, making it inefficient and inconvenient to use.

DrissionPage supports the coexistence of multiple tab objects, which do not affect each other, and tabs can be operated without being activated. In addition, the focus switching handles the complexity and stability issues maintained by the proxy.

Therefore, DrissionPage does not provide the ability to switch in and out of tabs. Instead, you can use the `get_tab()` or `new_tab()` methods to get the specified tab object for operation.

The logic of operation is the same as that of the Page object.

**Example 1: Create a new tab**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
tab = page.new_tab()  # Create a new tab and get the tab object
tab.get('https://www.baidu.com')  # Operate the tab using the tab object
```

**Example 2: Get a specific tab**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.ele('Some link').click()  # Click on a link to create a new tab
page.wait.new_tab()  # Wait for the new tab to appear
tab = page.get_tab(page.latest_tab)  # Get the specified tab object
tab.get('https://www.baidu.com')  # Operate the tab using the tab object
```

---

## ✅️️ Tab Overview

### 📌 `tabs_count`

This property returns the number of tabs.

**Type:** `int`

```python
print(page.tabs_count)
```

**Output:**

```shell
2
```

---

### 📌 `tabs`

This property returns all tab IDs as a list.

**Type:** `List[str]`

```python
print(page.tabs)
```

**Output:**

```shell
['0B300BEA6F1F1F4D5DE406872B79B1AD', 'B838E91F38121B32940B47E8AC59D015']
```

---

## ✅️️ Create a New Tab

### 📌 `new_tab()`

This method is used to create a new tab at the end.

Only the Page object has this method.

|    Parameter    |        Type        | Default | Description                                                                   |
|:--------------:|:-----------------:|:-------:|-------------------------------------------------------------------------------|
|     `url`      | `str`<br/>`None` | `None`  | The URL to be visited by the new tab, if not passed in, an empty tab is created |
|  `new_window`  |       `bool`      | `False` | Whether to open the tab in a new window                                       |
|  `background`  |       `bool`      | `False` | Whether to not activate the new tab, invalid if `new_window` is `True`         |
| `new_context`  |       `bool`      | `False` | Whether to create a new context, if `True`, opens a new window in incognito mode, and the new window does not share cookies with other windows |

|   Return Type    | Description                                                   |
|:---------------:|--------------------------------------------------------------|
| `ChromiumTab`  | `ChromiumPage`'s `new_tab()` returns a `ChromiumTab` object      |
| `WebPageTab` | `WebPage`'s `new_tab()` returns a `WebPageTab` object |

**Example:**

```python
page.new_tab(url='https://www.baidu.com')
```

---

### 📌 `wait.new_tab()`

This method is used to wait for a new tab to appear.

Only the Page object has this method.

| Parameter |  Type  |  Default  | Description                                         |
|:---------:|:------:|:---------:|-----------------------------------------------------|
| `timeout` | `float` |   `None`  | Timeout in seconds, if `None`, uses the page's `timeout` setting |
| `raise_err` | `bool` |   `None`  | Whether to raise an error if waiting fails, if `None`, follows the `Settings` setting |

|  Return Type  | Description                 |
|:------------:|-----------------------------|
|    `str`     | Returns the ID of the new tab if successful |
|    `False`   | Returns `False` if waiting fails |

---

## ✅️️ Get Tab Object

### 📌 `get_tab()`

This method is used to get a tab object. You can specify the index or ID of the tab.

Only the Page object has this method.

|   Parameter   |           Type          |  Default | Description                                              |
|:------------:|:----------------------:|:--------:|----------------------------------------------------------|
| `id_or_num` | `str`<br/>`int`<br/>`None` | `None` | The ID or index (starting from `1` and negative numbers indicating reverse) of the tab to get, default is `None` to get the current tab |

|   Return Type    |                            Description                            |
|:---------------:|-------------------------------------------------------------------|
|  `ChromiumTab`  | The tab object                                               |

:::warning Warning
    If a sequence number is passed, the sequence number may not correspond to the visual order of the tabs, but will be arranged based on the activation order.
:::

**Example:**

```python
tab = page.get_tab()  # Get the current tab object
tab = page.get_tab(1)  # Get the object of the second tab in the list
tab = page.get_tab('5399F4ADFE3A27503FFAA56390344EE5')  # Get the object of the specified id tab in the list
```

---

### 📌 `find_tabs()`

This method is used to find tabs that meet the specified conditions. Only Page objects have this method.

The `title`, `url`, and `tab_type` parameters are three search conditions, and they are connected with the "and" relationship.

The parameters `title`, `url`, and `tab_type` are connected with the relationship "and".

| Parameter Name |        Type       | Default | Description                                            |
|:--------------:|:-----------------:|:-------:|--------------------------------------------------------|
|     `title`    |       `str`       | `None`  | Match tabs that contain this text in the title, match all when `None` |
|      `url`     |       `str`       | `None`  | Match tabs that contain this text in the URL, match all when `None` |
|  `tab_type`    | `str`, `list`, `tuple`, `set` | `None` | Match tabs of this type, you can enter multiple types, match all when `None` |
|    `single`    |       `bool`      |  `True` | If `True`, return the id of the first result; if `False`, return all information |

|   Return Type  | Description                                            |
|:--------------:|--------------------------------------------------------|
|     `str`      | When `single` is `True`, return the tab id               |
| `List[dict]`   | When `single` is `False`, return all tab information     |

**Example:**

Find tabs that contain `'baidu.com'` in the URL and create an object:

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://www.baidu.com')

tab_id = page.find_tabs(url='baidu.com')
print(tab_id)
```

**Output:**

```shell
'8460E5D55BCA5798AF83BC4D243652A9'
```

Get all tab information:

```python
tabs = page.find_tabs(single=False)
print(tab)
```

**Output:**

```shell
[{'description': '',
  'devtoolsFrontendUrl': '/devtools/inspector.html?ws=127.0.0.1:9222/devtools/page/8460E5D55BCA5798AF83BC4D243652A9',
  'faviconUrl': 'https://www.baidu.com/img/baidu_85beaf5496f291521eb75ba38eacbd87.svg',
  'id': '8460E5D55BCA5798AF83BC4D243652A9',
  'title': '百度一下，你就知道',
  'type': 'page',
  'url': 'https://www.baidu.com/',
  'webSocketDebuggerUrl': 'ws://127.0.0.1:9222/devtools/page/8460E5D55BCA5798AF83BC4D243652A9'}]
```

---

### 📌 `latest_tab`

This property returns the id of the last activated tab, which refers to the most recently appeared or newly activated tab.

Only Page objects have this property.

**Type:** `str`

**Example:**

```python
# Open a tab
ele.click()
# Get the object of the latest tab
tab = page.get_tab(page.latest_tab)  # Equivalent to page.get_tab(0)
```

---

## ✅️️ Using Multiple Instances

By default, a Tab object is a singleton, which means that each tab has only one object, even if `get_tab()` is used repeatedly, the same object will be obtained.

This is mainly to prevent beginners from misunderstanding the mechanism and creating multiple connections repeatedly, which may cause resource waste.

Multiple Tab objects are allowed to be operated on the same tab at the same time, each responsible for different tasks. For example, one Tab object executes the main logic flow, and the other monitors the page and handles various pop-ups.

To allow multiple instances, use `Settings` to set:

```python
from DrissionPage.common import Settings

Settings.singleton_tab_obj = False
```

**Example:**

```python
from DrissionPage import ChromiumPage
from DrissionPage.common import Settings

page = ChromiumPage()
page.new_tab()
page.new_tab()

# Without using multiple instances:
tab1 = page.get_tab(1)
tab2 = page.get_tab(1)
print(id(tab1), id(tab2))

# Using multiple instances:
Settings.singleton_tab_obj = False
tab1 = page.get_tab(1)
tab2 = page.get_tab(1)
print(id(tab1), id(tab2))
```

**Output:**

The first output shows that the two Tab objects are the same, while the second output shows that they are independent.

```shell
2347582903056 2347582903056
2347588741840 2347588877712
```

---

## ✅️️ Closing and Reconnecting

### 📌 `close()`

This method is used to close the tab.

This method can be called on both Page objects and Tab objects.

It should be noted that the Page object can still manage other tabs after closing a tab.

**Parameters:** None

**Returns:** None

---

### 📌 `disconnect()`

This method is used to disconnect the page object from the browser, but does not close the tab. After disconnecting, the object cannot perform operations on the tab.

Both the Page object and Tab object have this method.

It should be noted that the Page object can still manage tabs after disconnecting from the browser.

**Parameters:** None

**Returns:** None

---

### 📌 `reconnect()`

This method is used to close the connection to the page and then rebuild a new connection.

This is mainly used to cope with long-term running causing excessive memory usage. Disconnecting can release memory, and then reconnect to continue controlling the browser.

Both the Page, Tab, and `ChromiumFrame` objects have this method.

| Parameter Name |  Type  | Default Value | Description |
|:-------------:|:-----:|:-------------:|----------------------|
|     `wait`    |  float  |       0       |  How many seconds to wait before reconnecting after closing |

**Returns:** None

---

### 📌 `close_tabs()`

This method is used to close the specified tabs, and multiple tabs can be closed. The current tab is closed by default.

If the closed tabs include the current tab, it will switch to the first remaining tab, but not necessarily the visually first one.

Only the Page object has this method.

|  Parameter Name   |                                                                                                                                              Type                                                                                                                                               | Default Value |                                  Description                                  |
|:----------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------:|-------------------------------------------------------------------------------|
|  `tabs_or_ids`   | `str`, `None`, `ChromiumTab`, `List[str, ChromiumTab]`, `Tuple[str, ChromiumTab]`                                                                                                                                                                                                            |     None      | The tab objects or IDs to be processed, can be passed in as a list or tuple, `None` means process the current tab                            |
|     `others`     |                                                                                                                                               bool                                                                                                                                               |     True      | Whether to close tabs other than the specified ones                                                                                                                                                  |

**Returns:** None

**Example:**

```python
# Close the current tab
page.close_tabs()

# Close the 1st and 3rd tabs
tabs = page.tabs
page.close_tabs(tabs_or_ids=(tabs[0], tabs[2]))
```

---

### 📌 `close_other_tabs()`

This method is used to close tabs other than the ones passed in, and the current tab is kept by default. Multiple tabs can be passed in.

If the closed tabs include the current tab, it will switch to the first remaining tab, but not necessarily the visually first one.

Only the Page object has this method.

|  Parameter Name   |                                                                                                                                              Type                                                                                                                                               | Default Value |                                  Description                                  |
|:----------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------:|-------------------------------------------------------------------------------|
|  `tabs_or_ids`   | `str`, `None`, `ChromiumTab`, `List[str, ChromiumTab]`, `Tuple[str, ChromiumTab]`                                                                                                                                                                                                            |     None      | The tab objects or IDs to be processed, can be passed in as a list or tuple, `None` means process the current tab                            |

**Returns:** None

**Example:**

```python
# Close all tabs except the current tab
page.close_other_tabs()

# Close all tabs except the first tab
page.close_other_tabs(page.tab[0])

# Close tabs except for specified IDs
reserve_list = ('0B300BEA6F...', 'B838E91...')
page.close_other_tabs(reserve_list)
```

---

## ✅️ Activate Tab

### 📌 `set.tab_to_front()`

This method is used to activate a tab and bring it to the front. However, it does not shift the focus to the tab.

Only the Page object has this method.

|  Parameter Name |         Type         | Default Value |                               Description                               |
|:--------------:|:--------------------:|:-------------:|:----------------------------------------------------------------------:|
|  `tab_or_id`   | `str`, `ChromiumTab`, `None` |     None      | The tab object or ID, the default is `None` which means the current tab |

**Returns:** None

---

### 📌 `set.activate()`

This method is used to activate the Tab object or Page object.

**Parameters:** None

**Returns:** None

---

## ✅️️ Multiple Tab Collaboration

When doing automation, we often encounter a scenario where we have a list page and need to open the links in the list one by one to get the content of the new page. Each link will open a new page.

If we use Selenium, after clicking on a link, we must switch the focus to the new tab, collect the information, and then go back to the original page and click on the next link. However, due to the focus switch, the information of the original elements has been lost, and we can only re-get all the links and click on the next link using counting, which is very ungraceful.

With `ChromiumPage`, there is no need to move the focus after opening a tab. You can directly generate a new page object for a new tab and collect the information on the new page, while the original list page object can continue to operate on the next link. You can even control multiple tabs using multithreading to achieve various black technologies.

Let's demonstrate this using the Gitee recommended projects page: [Latest recommended projects - Gitee.com](https://gitee.com/explore/all)

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://gitee.com/explore/all')

links = page.eles('t:h3')
for link in links[:-1]:
    # Click the link
    link.click()
    # Wait for the new tab to appear
    page.wait.new_tab()
    # Get the new tab object
    new_tab = page.get_tab(0)
    # Wait for the new tab to load
    new_tab.wait.load_start()
    # Print the title of the tab
    print(new_tab.title)
    # Close all tabs except the list page
    page.close_other_tabs()
```



**Output:**

```shell
wx-calendar: Native Mini Program Calendar Component (Scrollable, Markable, Disableable)
thingspanel-go: Open Source Plugin-based IoT Platform developed in Go. Supports MQTT, Modbus multi-protocol, multi-type device access and visualization, automation, alarm, rule engine and other functions. QQ Group: 371794256.
APITable: Community Edition of vika.cn, an open source low-code, multi-dimensional table tool. An open and free alternative to Airtable.
ideaseg: Chinese word segmentation plug-in based on NLP technology, with much higher accuracy than commonly used segmenters, also provides ElasticSearch and OpenSearch plug-ins.
vue-plugin-hiprint: hiprint for Vue2/Vue3 ⚡Printing, print design, visual designer, report design, element editing, visual print editing.
ExDUIR.NET: Lightweight DirectUI framework for Windows platform

The rest is omitted...
```

