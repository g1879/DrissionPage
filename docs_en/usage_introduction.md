Introduction to Usage
---

This chapter provides a detailed overview of several page objects and their usage.

In the "Getting Started > Basic Concepts" section, we briefly introduced several page objects, which will not be repeated here.

## ✅️️ `SessionPage`

A page object used for sending and receiving data packets. It can only send and receive data packets and cannot control the browser.

### 📌 `SessionElement`

An element object obtained from `SessionPage`, which allows reading element information. It can also be used as a reference to obtain surrounding or descendant elements.

---

## ✅️️ `ChromiumPage`

An object used to control the browser. In addition to controlling a page, it can also perform operations on the overall browser, such as adjusting window size and position, managing file downloads, adding and deleting tabs, etc.

### 📌 `ChromiumTab`

A browser tab object, similar to `ChromiumPage`. It can control functions within a page but cannot control the overall browser functions.

---

### 📌 `ChromiumFrame`

A `<frame>` or `<iframe>` element object, which serves as both a page object and an element with characteristics. It can perform operations such as page navigation and retrieving internal elements.

---

### 📌 `ChromiumElement`

An element object obtained from the aforementioned browser page objects. It supports interactions such as clicking, entering text, dragging, etc.

---

### 📌 `ChromiumShadowElement`

A shadow-root object, with element characteristics, which allows obtaining descendant elements within it.

---

## ✅️️ `WebPage`

A page element that integrates the functionalities of both `SessionPage` and `ChromiumPage`. It possesses all the functionalities of both elements combined. It has two modes, namely s and d modes, which can synchronize login information between the two modes.

### 📌 s mode

The s mode functionality is the same as `SessionPage`, and the generated elements are instances of `SessionElement`.

---

### 📌 d mode

The d mode functionality is the same as `ChromiumPage`, and the generated elements are instances of `ChromiumElement`.

---

## ✅️️ Configuration Objects

Configuration objects are used to provide initialization information when creating page objects. They only take effect when the page objects are created and cannot be modified after creation.

### 📌 `SessionOptions`

A configuration object used for `SessionPage` and `WebPage` s mode.

---

### 📌 `ChromiumOptions`

A configuration object used for `ChromiumPage` and `WebPage` d mode.

---

## ✅️️ Relationship Diagram

The following diagram lists the generation relationships between various objects used in this library.

```
├─ SessionPage
|     └─ SessionElement
|           └─ SessionElement
├─ ChromiumPage
|     ├─ ChromiumTab
|     |     └─ ChromiumElement
|     |     └─ SessionElement
|     ├─ ChromiumFrame
|     |     └─ ChromiumElement
|     |     └─ SessionElement
|     ├─ ChromiumElement
|     |     └─ ChromiumElement
|     |     └─ SessionElement
|     └─ ChromiumShadowElement
|           └─ ChromiumElement
|           └─ SessionElement
├─ WebPage
|     ├─ ChromiumTab
|     |     └─ ChromiumElement
|     |     └─ SessionElement
|     ├─ ChromiumFrame
|     |     └─ ChromiumElement
|     |     └─ SessionElement
|     ├─ ChromiumElement
|     |     └─ ChromiumElement
|     |     └─ SessionElement
|     ├─ ChromiumShadowElement
|     |     └─ ChromiumElement
|     |     └─ SessionElement
|     └─ SessionElement
|           └─ SessionElement
├─ SessionOptions
└─ ChromiumOptions
```


