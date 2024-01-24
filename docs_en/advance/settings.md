⚙️ Global Settings
---

There are some global settings at runtime that can control certain behaviors of the program.

## ✅️️ Usage

Global settings are located in the `DrissionPage.common` path.

Use assignment to modify the properties of the `Settings` object.

Usage:

```python
from DrissionPage.common import Settings

Settings.raise_when_wait_failed = True
```

---

## ✅️️ Settings Options

### 📌 `raise_when_ele_not_found`

Sets whether or not to raise an exception when an element is not found. Default is `False`.

---

### 📌 `raise_when_click_failed`

Sets whether or not to raise an exception when clicking fails. Default is `False`.

---

### 📌 `raise_when_wait_failed`

Sets whether or not to raise an exception when waiting fails. Default is `False`.

---

### 📌 `singleton_tab_obj`

Sets whether or not the Tab object should use the singleton pattern. Default is `True`.

---

## ✅️️ Examples

This example sets to immediately raise an exception when an element is not found (instead of returning `NoneElement`).

You can execute it directly to see the effect.

```python
from DrissionPage import SessionPage
from DrissionPage.common import Settings

Settings.raise_when_ele_not_found = True

page = SessionPage()
page.get('https://www.baidu.com')
ele = page('#abcd')
```

**Output:**

```shell
...omitted...
DrissionPage.errors.ElementNotFoundError: 
Element not found.
method: ele()
args: {'locator': '#abcd'}
```

