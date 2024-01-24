⚙️ Tools
---

The `DrissionPage.common` module provides several small tools.

## ✅️️ `make_session_ele()`

This method is used to convert a page object, element object, or HTML text into a `SessionElement` object, or to search for elements based on it and get their static versions.

|  Parameter Name |                                                                      Type                                                                      | Default | Description |
|:--------------:|:--------------------------------------------------------------------------------------------------------------------------------------------:|:-------:|-------------|
| `html_or_ele` | `str`<br/>`ChromiumElement`<br/>`ChromiumPage`<br/>`ChromiumTab`<br/>`WebPage`<br/>`WebPageTab`<br/>`ChromiumFrame`<br/>`ShdownRoot` | Required | HTML text, element, or page object |
|      `loc`     |                                                     `str`<br/>`Tuple[str, str]`                                                      |  None   | Location tuple or string. When it is `None`, no search in sub-elements and returns the root element |
|      `index`    |                                                                `int`                                                                 |   `1`   | Get the nth element, starting from `1`. A negative number can be passed to get the nth element from the end. `None` returns all elements |

|       Return Type       |                   Description                   |
|:----------------------:|:-----------------------------------------------:|
|    `SessionElement`    |  return a static element object when the index is a number   |
| `List[SessionElement]` | return a list of static element objects when the index is `None` |

**Example:**

```python
from DrissionPage.common import make_session_ele

html = '''
<html><body><div>abc</div></body></html>
'''
ele = make_session_ele(html)
print(ele.text)
```

**Output:**

```shell
abc
```

---

## ✅️️ `get_blob()`

This method is used to get the content of the specified blob resource.

:::warning Note
    - If the resource is inside an iframe element from another domain, you must get the iframe element object and pass it in to retrieve it
    - This method can only be used to get static resources and cannot be used for streaming media
:::

|  Parameter Name  |                                         Type                                          | Default | Description |
|:----------------:|:------------------------------------------------------------------------------------:|:-------:|-------------|
|      `page`     | `ChromiumPage`<br/>`ChromiumTab`<br/>`WebPage`<br/>`WebPageTab`<br/>`ChromiumFrame` | Required | The page object where the resource is located |
|     `url`      |                                        `str`                                        | Required | Blob resource url |
| `as_bytes` |                                       `bool`                                        | `True` | Whether to return as `bytes` type |

|   Return Type    |                         Description                          |
|:----------------:|:-----------------------------------------------------------:|
|      `str`       |    return as base64 format when the `as_bytes` is `False`     |
|     `bytes`     |              return as byte data when the `as_bytes` is `True`            |

---

## ✅️️ `configs_to_here()`

This method is used to copy the ini file to the current directory.

|  Parameter Name  |  Type  | Default | Description |
|:----------------:|:-----:|:-------:|-------------|
|      `save_name`     | `str` |  `None`   | Specify the file name. If it is `None`, it will be named as `'dp_configs.ini'` |

**Return:** `None`

---

## ✅️️ `wait_until()`

This method is used to wait until the return value of the passed method is not falsy. It will raise `TimeoutError` if timed out.

|  Parameter Name  |       Type       | Default | Description |
|:----------------:|:----------------:|:-------:|-------------|
|   `function`       | `callable` | Required | The method to be executed |
|    `kwargs`      |   `dict`   |  `None`  | Method parameters |
|    `timeout`    |   `float`   |   `10`   | Timeout in seconds |

**Return:** `Any`

