# 🌏 Import
---

## ✅️ Page Classes

Page classes are the main tools used to control the browser or send/receive data packets.

`DrissionPage` contains three main page classes. Choose one based on your needs.

### 📌 `ChromiumPage`

If you only need to control the browser, import `ChromiumPage`.

```python
from DrissionPage import ChromiumPage
```

---

### 📌 `SessionPage`

If you only need to send/receive data packets, import `SessionPage`.

```python
from DrissionPage import SessionPage
```

---

### 📌 `WebPage`

`WebPage` is the most comprehensive page class, allowing you to control the browser and send/receive data packets.

```python
from DrissionPage import WebPage
```

---

## ✅️ Configuration Tools

### 📌 `ChromiumOptions`

The `ChromiumOptions` class is used to set browser startup options.

These options only take effect when launching the browser and do not affect an already running browser.

```python
from DrissionPage import ChromiumOptions
```

---

### 📌 `SessionOptions`

The `SessionOptions` class is used to set the startup options for the `Session` object.

This is used to configure the connection parameters for `SessionPage` or `WebPage` modes.

```python
from DrissionPage import SessionOptions
```

---

### 📌 `Settings`

`Settings` is used to set global runtime configurations, such as whether to throw exceptions when an element is not found.

```python
from DrissionPage.common import Settings
```

---

## ✅️ Other Tools

Other tools that may be used are located in the `DrissionPage.common` path.

### 📌 `Keys`

The `Keys` class represents keyboard keys, used to simulate pressing control, alt, and other keys.

```python
from DrissionPage.common import Keys
```

---

### 📌 `Actions`

The `Actions` class represents a sequence of actions.

It is already built-in to the browser page object and does not need to be explicitly imported unless specifically required.

```python
from DrissionPage.common import Actions
```

---

### 📌 `By`

The `By` class is similar to the one used in Selenium, making it easier to migrate projects.

```python
from DrissionPage.common import By
```

---

### 📌 Other Tools

 - `wait_until`: waits until the given method returns `True`
 - `make_session_ele`: generates a `ChromiumElement` object from an HTML string
 - `configs_to_here`: copies configuration files to the current path
 - `get_blob`: retrieves a specified blob resource

```python
from DrissionPage.common import wait_until
from DrissionPage.common import make_session_ele
from DrissionPage.common import configs_to_here
```

---

## ✅️ Exceptions

Exceptions are located in the `DrissionPage.errors` path.

For a complete list of exceptions, refer to the Advanced Usage section.

```python
from DrissionPage.errors import ElementNotFoundError
```

---

## ✅️ Derived Object Types

Objects such as Tab and Element are generated from Page objects. To perform type checking during development, import these types from the `DrissionPage.items` path.

```python
from DrissionPage.items import SessionElement
from DrissionPage.items import ChromiumElement
from DrissionPage.items import ShadowRoot
from DrissionPage.items import NoneElement
from DrissionPage.items import ChromiumTab
from DrissionPage.items import WebPageTab
from DrissionPage.items import ChromiumFrame
```

