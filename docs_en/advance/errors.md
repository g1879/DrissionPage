⚙️ Usage of Exceptions
---

This section introduces custom exceptions in DrissionPage.

## ✅️️ Import

Various exceptions are located in the `DrissionPage.errors` path.

```python
from DrissionPage.errors import *
```

## ✅️️ Exception Introduction

### 📌 `ElementNotFoundError`

Raised when an element cannot be found.

---

### 📌 `AlertExistsError`

Thrown when executing JS or calling functions implemented through JS, if there is an unhandled alert present.

---

### 📌 `ContextLostError`

Raised when elements are called after the page has been refreshed.

---

### 📌 `ElementLostError`

Thrown when an element becomes invalid due to page or self-refresh, but is still called.

---

### 📌 `CDPError`

Thrown when an exception occurs while invoking cdp methods.

---

### 📌 `PageDisconnectedError`

Raised when the page is closed or the connection is disconnected, but its functions are still called.

---

### 📌 `JavaScriptError`

Thrown when there is a JavaScript runtime error.

---

### 📌 `NoRectError`

Raised when attempting to retrieve size and position information for an element that doesn't have any.

---

### 📌 `BrowserConnectError`

Thrown when there is an error connecting to the browser.

---

### 📌 `NoResourceError`

Thrown when accessing resources fails for the browser element's `src()` and `save()` methods.

---

### 📌 `CanNotClickError`

Thrown when clicking on an element that is not clickable and is set to allow the exception to be thrown.

### 📌 `GetDocumentError`

Thrown when getting the page document fails.

---

Thrown when getting the page document fails.

### 📌 `WaitTimeoutError`

Thrown when automatic waiting fails and is set to allow the exception to be thrown.

---

### 📌 `WrongURLError`

Thrown when accessing a url with an incorrect format.

---

### 📌 `StorageError`

Thrown when there is a prohibition on operating data, such as a website prohibiting the operation.

---

### 📌 `CookieFormatError`

Thrown when importing a cookie with an incorrect format.

