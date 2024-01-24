# 🔦 Element Not Found

## ✅️ Default Behavior

By default, when an element is not found, an `NoneElement` object is returned instead of immediately throwing an exception.

This object evaluates to `False` when evaluated in an `if` statement, and calling its methods will throw an `ElementNotFoundError` exception.

This allows you to use an `if` statement to check if an element is found, or use a `try` block to catch the exception.

When multiple elements are searched for but not found, an empty `list` is returned.

**Example using `if` statement:**

```python
ele = page.ele('xxxxxxx')

# Check if the element is found
if ele:
    print('Element found.')

if not ele:
    print('Element not found.')
```

**Example using `try` block:**

```python
try:
    ele.click()
except ElementNotFoundError:
    print('Element not found.')
```

---

## ✅️ Immediate Exception Throwing

If you want to immediately throw an exception when an element is not found, you can use the following method to configure it.

This setting is globally applicable and only needs to be set once at the beginning of the project.

When multiple elements are searched for but not found, an empty `list` is still returned.

Setting the global variable:

```python
from DrissionPage.common import Settings

Settings.raise_when_ele_not_found = True
```

**Example:**

```python
from DrissionPage import ChromiumPage
from DrissionPage.common import Settings

Settings.raise_when_ele_not_found = True

page = ChromiumPage(timeout=1)
page.get('https://www.baidu.com')
ele = page('#abcd')  # ('#abcd') element does not exist
```

Output:

```console
DrissionPage.errors.ElementNotFoundError: 
Element not found.
method: ele()
args: {'locator': '#abcd'}
```

---

## ✅️ Set Default Return Value

If you want to retrieve an attribute after finding an element, but this element may not exist, or if one of the chained searches fails, you can set the value that is returned when the search fails instead of throwing an exception. This can simplify some scraping logic.

Use the `set.NoneElement_value()` method of the browser page object to set this value.

| Parameter |  Type  | Default | Description                  |
|:---------:|:------:|:-------:|------------------------------|
|  `value`  | `Any`  |  `None` | The value to be returned     |
| `on_off`  | `bool` |  `True` | Indicate whether to enable it |

**Returns:** `None`

**Example:**

For example, when iterating through multiple objects in a list on a page, but some of them may be missing certain child elements, you can write:

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.NoneElement_value('Not Found')
for li in page.eles('t:li'):
    name = li('.name').text
    age = li('.age').text
    phone = li('.phone').text
```

This way, if a child element does not exist, instead of throwing an exception, it will return the string `'Not Found'`.

