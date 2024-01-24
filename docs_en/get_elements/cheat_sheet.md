🔦 Syntax Cheat Sheet
---

## ✅️ Syntax for Positioning

### 📌 Basic Usage

The following syntax only appears at the beginning of a statement.

|   Syntax    |    Exact Match    |   Fuzzy Match   |    Match at Start    |    Match at End    |                  Description                 |
|:-------:|:-----------------:|:---------------:|:--------------------:|:-----------------:|:--------------------------------------------:|
| `@property`  |    `@property=`     |    `@property:`    |     `@property^`     |     `@property$`     |             Find elements by property              |
| `@!property` |   `@!property=`    |   `@!property:`   |    `@!property^`    |    `@!property$`    |      Find elements where property does not match     |
| `text`  |      `text=`      | `text:` or none |     `text^`     |     `text$`     |             Find elements by text              |
| `@text()` |    `@text()=`     |    `@text():`   |   `text()^`   |   `text()$`   | Replace `text` with `text()` when used with `@` or `@@`, commonly used for multiple condition matching |
|  `tag`  |   `tag=` or `tag:`   |       None      |       None       |       None       |                Find elements of certain type                |
| `xpath` | `xpath=` or `xpath:` |       None      |       None       |       None       |             Find elements using xpath              |
|  `css`  |   `css=` or `css:`   |       None      |       None       |       None       |          Find elements using css selector          |

---

### 📌 Combination Usage

|         Syntax         |         Description          |
|:----------------------:|:----------------------------:|
|   `@@property1@@property2`   | Find elements that meet multiple conditions simultaneously |
|   `@@property1@!property2`   | Use multiple property matching in conjunction with negation |
|   `@|property1@|property2` | Find elements that meet any of multiple conditions |
|   `tag:xx@property`    | Use tag in conjunction with property matching  |
|   `tag:xx@@property1@@property2` | Use tag in conjunction with multiple property matching |
|   `tag:xx@|property1@|property2`      | Use tag in conjunction with multiple property matching |
|   `tab:@@text()=text@@property`   | Use tab in conjunction with text and property matching  |

---

### 📌 Simplified Syntax

|    Original Syntax    |  Simplified Syntax   |    Exact Match    |   Fuzzy Match   |    Match at Start    |    Match at End    |       Note      |
|:---------------------:|:-------------------:|:-----------------:|:--------------:|:--------------------:|:-----------------:|:--------------:|
|   `@id`   |   `#`   | `#` or `#=`  |   `#:`   |   `#^`   |   `#$`   | Simplified syntax can only be used alone |
| `@class`  |   `.`   | `.` or `.=`  |   `.:`   |   `.^`   |   `.$`   | Simplified syntax can only be used alone |
|   `tag`   |   `t`   | `t:` or `t=` |    None     |    None     |    None     |    Can only be used at the beginning    |
|  `text`   |  `tx`   |   `tx=`   | `tx:` or none |  `tx^`   |  `tx$`   | Fuzzy match text is used when there are no tags |
| `@text()` | `@tx()` | `@tx()=`  | `@tx():` | `@tx()^` | `@tx()$` |              |
|  `xpath`  |   `x`   | `x:` or `x=` | None     |    None     |    None |    Can only be used alone    |
|   `css`   |   `c`   | `c:` or `c=` | None     |    None     |    None |    Can only be used alone    |

---

## ✅️ Relative Positioning

|      Method      |          Description           |
|:------------:|:---------------------------:|
|  `parent()`  |     Find the parent element of the current element      |
|  `child()`   |     Find a direct child node of the current element     |
| `children()` |  Find all direct child nodes of the current element that match the condition  |
|   `next()`   |    Find the first sibling node after the current element that matches the condition    |
|  `nexts()`   |  Find all sibling nodes after the current element that match the condition  |
|   `prev()`   |    Find the first sibling node before the current element that matches the condition    |
|  `prevs()`   |  Find all sibling nodes before the current element that match the condition  |
|  `after()`   |    Find the first node after the current element in the document that matches the condition   |
|  `afters()`  | Find all nodes after the current element in the document that match the condition  |
|  `before()`  |    Find the first node before the current element in the document that matches the condition   |
| `befores()`  | Find all nodes before the current element in the document that match the condition  |

## ✅️ Miscellaneous

| Method | Simplified Writing | Description | Note |
|:------:|:------------------:|:-----------:|:----:|
| `get_frame()` | N/A | Find an `<iframe>` element on the page | Only available for page objects |
| `shadow_root` | `sr` | Get the shadow root object within the current element | Only available for element objects |

