🚤 Element Interaction
---

This section introduces the interaction with browser elements. The browser element object is `ChromiumElement`.

## ✅️️ Clicking Elements

### 📌 `click()` and `click.left()`

These two methods have the same effect, used to left-click on elements. They can simulate clicking or use JavaScript to click.

|    Parameter    |   Type    |  Default  | Description                                                                                      |
|:----------:|:-------:|:-------:|------------------------------------------------------------------------------------------------|
|   `by_js`   | `bool`  | `False` | Specifies the way to click.<br/>If `None`, simulate clicking if not obstructed, otherwise click with JS.<br/>If `True`, click directly with JS.<br/>If `False`, force simulated clicking, even if obstructed |
|  `timeout`  | `float` |  `1.5`  | Timeout for simulating clicks, waiting for the element to become visible, available, and entering the viewport                                                                       |
| `wait_stop` | `bool`  | `True`  | Whether to wait for the element to stop moving before clicking                                                                                  |

|   Return   | Description                                    |
|:-------:|---------------------------------------|
| `False` | When `by_js` is `False` and the element is not available or visible, returns `False` |
| `True`  | Returns `True` in all other cases                   |

**Example:**

```python
# Simulate clicking on the element ele, click if obstructed
ele.click()

# Click the element ele with JS, regardless of any coverings
ele.click(by_js=True)

# If the element is not obstructed, simulate clicking, otherwise click with JS
ele.click(by_js=None)
```

By default, `by_js` is `None`, which means simulated clicking is preferred. If there are obstructions, the element is not available, not visible, or unable to automatically enter the viewport, it will wait until the timeout is reached and then click with JS.

When `by_js` is `False`, the program will force simulated clicking, even if the element is obstructed. If the element is not visible or available, it will return `False`. If the element cannot be automatically scrolled into the viewport, click with JS instead.

When `by_js` is `True`, it is possible to ignore any obstructions. As long as the element is in the DOM, it can be clicked, but whether the element responds to the click depends on the architecture of the web page.

The elements can be flexibly operated as needed.

Before simulating a click, the program will attempt to scroll the element into the viewport.

By default, if a simulated click cannot be performed (the element cannot enter the viewport, is not available, or is hidden), a left-click will return `False`. However, it can also be set globally to throw an exception:

```python
from DrissionPage.common import Settings

Settings.raise_click_failed = True
ele.click()  # Throw an exception if unable to click
```

---

### 📌 `click.right()`

This method performs a right-click on the element.

**Parameters:** None

**Returns:** `None`

**Example:**

```python
ele.click.right()
```

---

### 📌 `click.middle()`

This method performs a middle-click on the element.

**Parameters:** None

**Returns:** `None`

**Example:**

```python
ele.click.middle()
```

---

### 📌 `click.multiple()`

This method performs multiple left-clicks on the element.

|  Parameter   |  Type   | Default | Description   |
|:-------:|:-----:|:---:|------|
| `times` | `int` | `2` | Number of clicks |

**Returns:** `None`

---

### 📌 `click.at()`

This method is used to click on the element with offsets relative to the top-left corner of the element. Clicking the middle of the element when `offset_x` and `offset_y` are not provided.   
The target of the click does not have to be on the element, negative values or values greater than the size of the element can be used to click areas near the element. Positive values are to the right and down, and negative values are to the left and up.

|   Parameter   |   Type    |   Default    | Description                                                         |
|:----------:|:-------:|:--------:|-------------------------------------------------------------------|
| `offset_x` | `float` |  `None`  | The x-axis offset relative to the top-left corner of the element, positive to the right and down                                   |
| `offset_y` | `float` |  `None`  | The y-axis offset relative to the top-left corner of the element, positive to the right and down                                   |
|  `button`  |  `str`  | `'left'` | The button to click, pass in `'left'`, `'right'`, `'middle'`, `'back'`, `'forward'` |
|  `count`   |  `int`  |   `1`    | Number of clicks                                                   |

**Returns:** `None`

**Example:**

```python
# Click 50*50 above the element
ele.click.at(50, -50)

# Click the upper middle part of the element, offset_x is 50 relative to the top-left corner to the right, offset_y stays at the middle of the element
ele.click.at(offset_x=50)

# Same as click(), but without retrying
ele.click.at()
```

---

## ✅️️ Inputting Content

### 📌 `clear()`

This method is used to clear the text of the element, and can choose to simulate keystrokes or use JS.

This is a Markdown file, translate it into English, do not modify any existing Markdown commands:


The simulated keystroke method will automatically input the `ctrl-a-del` combination key to clear the text box, while the js method directly sets the value attribute of the element to `''`.

| Parameter Name | Type   | Default Value | Description                                    |
|:----------:|:-------:|:------------:|-------------------------------------------|
| `by_js`    | `bool`  | `False`      | Whether to clear the text box by js method |

**Return:** `None`

**Example:**

```python
ele.clear()
```

---

### 📌 `input()`

This method is used to input text or combination keys to the element, and can also be used to input file paths to the upload control. You can choose whether to clear the element before inputting.

| Parameter Name | Type   | Default Value | Description                                                                                               |
|:----------:|:-------:|:------------:|------------------------------------------------------------------------------------------------------|
| `vals`     | `Any`   | `False`      | Text value or keystroke combination<br/>When inputting a path string or a list of paths to the file upload control |
| `clear`    | `bool`  | `True`       | Whether to clear the text box before inputting                                                        |
| `by_js`    | `bool`  | `False`      | Whether to use js method for inputting, it cannot input combination keys when set to `True`              |

**Return:** `None`

:::tip Tips
    - Some text boxes can receive the enter key instead of clicking the button, and you can directly add `'\n'` to the end of the text.
    - Non-`str` data will be automatically converted to `str`.
:::

**Example:**

```python
# Input text
ele.input('Hello world!')

# Input text and press enter
ele.input('Hello world!\n')
```

---

### 📌 Input Combination Keys

Before using combination keys or special keys, you need to import the key class `Keys`.

```python
from DrissionPage.common import Keys
```

Then put the combination keys in a `tuple` and pass it to `element.input()`.

```python
ele.input((Keys.CTRL, 'a', Keys.DEL))  # ctrl+a+del
```

---

### 📌 `focus()`

This method is used to make the element get focus.

**Parameter:** None

**Return:** `None`

---

## ✅️️ Drag and Hover

:::tip Tips
    In addition to the methods mentioned below, this library also provides more flexible action chain functions, see the later sections for details.
:::

### 📌 `drag()`

This method is used to drag the element to a new position relative to the current position, and the speed can be set.

| Parameter Name | Type    | Default Value | Description                                                     |
|:----------:|:------:|:-------------:|----------------------------------------------------------------|
| `offset_x` |  `int` |     `0`      | x-axis offset, positive when moving down or to the right         |
| `offset_y` |  `int` |     `0`      | y-axis offset, positive when moving down or to the right         |
| `duration` | `float`|    `0.5`     | Time used, in seconds, input `0` to reach instantaneously       |

**Return:** `None`

**Example:**

```python
# Drag the current element to the position 50*50, taking 1 second
ele.drag(50, 50, 1)
```

---

### 📌 `drag_to()`

This method is used to drag the element to another element or a coordinate.

|  Parameter Name |                           Type                          | Default Value | Description                  |
|:------------:|:-----------------------------------------------------:|:-------------:|-----------------------------|
| `ele_or_loc` | `ChromiumElement`<br/>`Tuple[int, int]`                |    Required   | Another element object or coordinate tuple |
|  `duration`  |                      `float`                          |    `0.5`      | Time used, in seconds, input `0` to reach instantaneously |

**Return:** `None`

**Example:**

```python
# Drag ele1 to ele2
ele1 = page.ele('#div1')
ele2 = page.ele('#div2')
ele1.drag_to(ele2)

# Drag ele1 to the position 50, 50 on the webpage
ele1.drag_to((50, 50))
```

---

### 📌 `hover()`

This method is used to simulate hovering the mouse over the element, and can accept offsets, the offsets are relative to the upper left corner of the element. When no`offset_x` and `offset_y` values are passed, the hover is on the center of the element.

| Parameter Name | Type   | Default Value | Description                                   |
|:----------:|:-----:|:------------:|----------------------------------------------|
| `offset_x` | `int` |    `None`    | x-axis offset relative to the upper left corner of the element, positive when moving down or to the right |
| `offset_y` | `int` |    `None`    | y-axis offset relative to the upper left corner of the element, positive when moving down or to the right |

**Return:** `None`

**Example:**

```python
# Hover 50*50 above the element at the upper right corner
ele.hover(50, -50)

# Hover in the middle of the element, x offset 50 relative to the upper left corner, y remains at the center of the element
ele.hover(offset_x=50)

# Hover in the center of the element
ele.hover()
```

---

## ✅️️ Modify Element

### 📌 `set.innerHTML()`

This method is used to set the innerHTML content of the element.

| Parameter Name | Type   | Default Value | Description                                    |
|:----------:|:-----:|:------------:|--------------------------------------------|
| `html`     | `str` |   Required   | HTML text                                  |

**Return:** `None`

---

### 📌 `set.prop()`

This method is used to set the `property` attribute of the element.

| Parameter Name | Type  | Default Value | Description |
|:--------------:|:-----:|:-------------:|-------------|
|     prop       | `str` |    Required   | Property name |
|     value      | `str` |    Required   | Property value |

**Returns:** `None`

**Example:**

```python
ele.set.prop('value', 'Hello world!')
```

---

### 📌 `set.attr()`

This method is used to set the `attribute` property of an element.

| Parameter Name | Type  | Default Value | Description |
|:--------------:|:-----:|:-------------:|-------------|
|     attr       | `str` |    Required   | Attribute name |
|     value      | `str` |    Required   | Attribute value |

**Returns:** `None`

**Example:**

```python
ele.set.attr('href', 'http://www.gitee.com')
```

---

### 📌 `remove_attr()`

This method is used to remove an element's `attribute` property.

| Parameter Name | Type  | Default Value | Description |
|:--------------:|:-----:|:-------------:|-------------|
|     attr       | `str` |    Required   | Attribute name |

**Returns:** `None`

**Example:**

```python
ele.remove_attr('href')
```

---

### 📌 `check()`

This method is used to select or deselect an element.

| Parameter Name | Type   | Default Value | Description |
|:--------------:|:------:|:-------------:|-------------|
|    uncheck     | `bool` |    `False`    | Whether to deselect |
|    by_js       | `bool` |    `False`    | Whether to select with JS |

**Returns:** `None`

---

## ✅️️ Execute JavaScript code

### 📌 `run_js()`

This method is used to execute JS code on an element, where `this` represents the element itself.

|  Parameter Name |  Type  | Default Value | Description                                            |
|:------------:|:-----:|:-------------:|-------------------------------------------------------|
|    script    | `str` |    Required   | JS script text                                         |
|    *args     |   -   |       -       | Arguments passed, corresponding to `arguments[0]`, `arguments[1]`, ... in the JS script |
|   as_expr    | `bool`|    `False`    | Whether to run as an expression. When `True`, `args` parameter is invalid |
|   timetout   |`float`|     `None`    | JS timeout, use the page `timeouts.script` setting when `None`|

| Return Type | Description           |
|:-----------:|-----------------------|
|   `Any`     | Result of the script  |

:::warning Note
    Remember to include `return` in the JS code to get the result.
:::

**Example:**

```python
# Click on the element by executing JS
ele.run_js('this.click();')

# Get the height of the element using JS
height = ele.run_js('return this.offsetHeight;')
```

---

### 📌 `run_async_js()`

This method is used to execute JS code asynchronously on an element, where `this` represents the element itself.

|  Parameter Name |  Type  | Default Value | Description                                            |
|:------------:|:-----:|:-------------:|-------------------------------------------------------|
|    script    | `str` |    Required   | JS script text                                         |
|    *args     |   -   |       -       | Arguments passed, corresponding to `arguments[0]`, `arguments[1]`, ... in the JS script |
|   as_expr    | `bool`|    `False`    | Whether to run as an expression. When `True`, `args` parameter is invalid |

**Returns:** `None`

---

### 📌 `add_init_js()`

This method is used to add initialization script to be executed before any script is loaded on the page.

|  Parameter Name |  Type  | Default Value | Description                                            |
|:------------:|:-----:|:-------------:|-------------------------------------------------------|
|    script    | `str` |    Required   | JS script text                                         |

| Return Type | Description            |
|:-----------:|------------------------|
|    `str`    | ID of the added script |

---

### 📌 `remove_init_js()`

This method is used to remove initialization scripts. Use `None` for `script_id` to remove all.

|  Parameter Name |  Type  | Default Value | Description |
|:------------:|:-----:|:-------------:|-------------|
|  script_id   | `str` |     `None`    | Script ID, `None` to remove all scripts |

**Returns:** `None`

---

## ✅️️ Element scrolling

The element scrolling functionality is hidden in the `scroll` attribute. It is used to scroll the contents of a scrollable container element or scroll the element itself into view.

```python
# Scroll to the bottom
ele.scroll.to_bottom()

# Scroll to the rightmost
ele.scroll.to_rightmost()

# Scroll down 200 pixels
ele.scroll.down(200)

# Scroll to a specific position
ele.scroll.to_location(100, 300)

# Scroll the page to make the element visible
ele.scroll.to_see()
```

---

### 📌 `scroll.to_top()`

This method is used to scroll the element to the top, while the horizontal position remains unchanged.

**Parameters:** None

**Returns:** `None`

**Example:**

```python
page.scroll.to_top()
```

---

### 📌 `scroll.to_bottom()`

This method is used to scroll the element to the bottom, while the horizontal position remains unchanged.

This method is used to select an option from the dropdown list by its value.

| Parameter Name |   Type   | Default Value | Description                 |
|:-------------:|:-------:|:-----------:|---------------------------|
|    `value`    | `str`<br/>`list`<br/>`tuple` |    Required   | The value of the option(s) to be selected. If a list or tuple is passed, multiple options can be selected. |
|   `timeout`   |  `float`  |     `None`    | The timeout duration. If `None`, the default page timeout will be used. |

| Return Type | Description   |
|:-----------:|-------------|
|    `bool`   | Whether the selection was successful. |

This method is used to select list items based on the `value` attribute. If it is a multiple selection list, you can select multiple items.

|   Parameter   |             Type             | Default | Description                               |
|:------------:|:---------------------------:|:-------:|-------------------------------------------|
|    `value`   | `str`<br/>`list`<br/>`tuple` | Required | The `value` value used as the selection condition, passing in a `list` or `tuple` can select multiple items |
|   `timeout`  |           `float`           |  `None`  | The timeout duration, `None` by default, uses the page timeout duration if not specified |

| Return Type | Description |
|:------------:|-------------|
|    `bool`    | Whether the selection is successful or not |

---

### 📌 `select.by_index()`

This method is used to select list items based on their index, starting from `1`. If it is a multiple selection list, you can select multiple items.

|   Parameter   |             Type             | Default | Description                                               |
|:------------:|:---------------------------:|:-------:|-----------------------------------------------------------|
|    `index`   | `int`<br/>`list`<br/>`tuple` | Required | The index of the item to be selected, passing in a `list` or `tuple` can select multiple items |
|   `timeout`  |           `float`           |  `None`  | The timeout duration, `None` by default, uses the page timeout duration if not specified |

| Return Type | Description |
|:------------:|-------------|
|    `bool`    | Whether the selection is successful or not |

---

### 📌 `select.by_locator()`

This method can be used to select option elements by using locators. If it is a multiple selection list, you can select multiple items.

|   Parameter   |             Type             | Default | Description                                         |
|:------------:|:---------------------------:|:-------:|-----------------------------------------------------|
|   `locator`  | `str`<br/>`list`<br/>`tuple` | Required | The locator, passing in a `list` or `tuple` can select multiple items |
|   `timeout`  |           `float`           |  `None`  | The timeout duration, `None` by default, uses the page timeout duration if not specified |

| Return Type | Description |
|:------------:|-------------|
|    `bool`    | Whether the selection is successful or not |

---

### 📌 `select.by_option()`

This method is used to select single or multiple list items. If it is a multiple selection list, you can select multiple items.

| Parameter  |                          Type                          | Default | Description                                                   |
|:---------:|:-----------------------------------------------------:|:-------:|---------------------------------------------------------------|
|  `option` | `ChromiumElement`<br/>`List[ChromiumElement]` | Required | The `<option>` element(s) or a list of such elements |

**Returns:** `None`

**Example:**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
select = page('t:select')
option = select('t:option')
select.select.by_option(option)
```

---

### 📌 `select.cancel_by_text()`

This method is used to cancel the selection of list items based on their text. If it is a multiple selection list, you can cancel multiple items.

|   Parameter   |             Type             | Default | Description                                                     |
|:------------:|:---------------------------:|:-------:|-----------------------------------------------------------------|
|    `text`    | `str`<br/>`list`<br/>`tuple` | Required | The text used as the selection condition, passing in a `list` or `tuple` can select multiple items |
|   `timeout`  |           `float`           |  `None`  | The timeout duration, `None` by default, uses the page timeout duration if not specified |

| Return Type | Description |
|:------------:|-------------|
|    `bool`    | Whether the selection is successful or not |

---

### 📌 `select.cancel_by_value()`

This method is used to cancel the selection of list items based on the `value` attribute. If it is a multiple selection list, you can cancel multiple items.

|   Parameter   |             Type             | Default | Description                                                     |
|:------------:|:---------------------------:|:-------:|-----------------------------------------------------------------|
|    `value`   | `str`<br/>`list`<br/>`tuple` | Required | The `value` value used as the selection condition, passing in a `list` or `tuple` can select multiple items |
|   `timeout`  |           `float`           |  `None`  | The timeout duration, `None` by default, uses the page timeout duration if not specified |

| Return Type | Description |
|:------------:|-------------|
|    `bool`    | Whether the selection is successful or not |

---

### 📌 `select.cancel_by_index()`

This method is used to cancel the selection of list items based on their index, starting from `1`. If it is a multiple selection list, you can cancel multiple items.

|   Parameter   |             Type             | Default | Description                                               |
|:------------:|:---------------------------:|:-------:|-----------------------------------------------------------|
|    `index`   | `int`<br/>`list`<br/>`tuple` | Required | The index of the item to be canceled, passing in a `list` or `tuple` can select multiple items |
|   `timeout`  |           `float`           |  `None`  | The timeout duration, `None` by default, uses the page timeout duration if not specified |

| Return Type | Description |
|:------------:|-------------|
|    `bool`    | Whether the selection is successful or not |

---

### 📌 `select.cancel_by_locator()`

This method can be used to cancel the selection of option elements by using locators. If it is a multiple selection list, you can cancel multiple items.

|   Parameter   |             Type             | Default | Description                                         |
|:------------:|:---------------------------:|:-------:|-----------------------------------------------------|
|   `locator`  | `str`<br/>`list`<br/>`tuple` | Required | The locator, passing in a `list` or `tuple` can select multiple items |
|   `timeout`  |           `float`           |  `None`  | The timeout duration, `None` by default, uses the page timeout duration if not specified |

| Return Type | Description |
|:------------:|-------------|
|    `bool`    | Whether the selection is successful or not |

---

### 📌 `select.cancel_by_option()`

This method is used to cancel the selection of single or multiple list items. If it is a multiple selection list, you can select multiple items.

| Parameter Name | Type                                  | Default Value | Description                                                         |
|:--------------:|:-------------------------------------:|:-------------:|---------------------------------------------------------------------|
| `option`       | `ChromiumElement`<br/>`List[ChromiumElement]` | Required      | `<option>` element or a list of `<option>` elements                   |

**Returns:** `None`

---

### 📌 `select.all()`

This method is used to select all items. It only applies to multi-select lists.

**Parameters:** None

**Returns:** `None`

---

### 📌 `select.clear()`

This method is used to deselect all items. It only applies to multi-select lists.

**Parameters:** None

**Returns:** `None`

---

### 📌 `select.invert()`

This method is used to invert the selection. It only applies to multi-select lists.

**Parameters:** None

**Returns:** `None`

---

### 📌 `select.is_multi`

This attribute returns whether the current element is a multi-select list.

**Return Type:** `bool`

---

### 📌 `select.options`

This attribute returns all option elements of the current list element.

**Return Type:** `ChromiumElement`

---

### 📌 `select.selected_option`

This attribute returns the selected option of the current element (for single-select lists).

**Return Type:** `bool`

---

### 📌 `select.selected_options`

This attribute returns all selected options of the current element (for multi-select lists).

**Return Type:** `List[ChromiumElement]`

