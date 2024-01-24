## 🚤 Actions Chain

Actions Chain can perform a series of interactive actions on the browser, such as mouse movement, mouse clicks, keyboard input, etc.

The `ChromiumPage`, `WebPage`, `ChromiumTab`, and `ChromiumFrame` objects support the use of actions chains.

Actions can be chained together or executed separately, and each action takes effect immediately without the need for `perform()`.

These actions are all simulated, so the actual mouse will not move, allowing multiple tabs to be operated simultaneously.

## ✅️ Usage

You can call the actions chain using the built-in `actions` attribute of the aforementioned objects, or you can create an actions chain object and pass in the page object to use.

The only difference between these two methods is that the former will wait for the page to finish loading before executing, while the latter will not.

### 📌 Using the built-in `actions` attribute

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://www.baidu.com')
page.actions.move_to('#kw').click().type('DrissionPage')
page.actions.move_to('#su').click()
```

---

### 📌 Using a new object

Import the actions chain using `from DrissionPage.common import Actions`.

Just pass in the `WebPage` object or `ChromiumPage` object. The actions chain only works on this page.

| Initialization Parameter |                       Type                       | Default | Description                               |
|:------------------------:|:-----------------------------------------------:|:-------:|-------------------------------------------|
|           page           | ChromiumPage<br/>WebPage<br/>ChromiumTab | Required | The browser page that the actions chain should operate on |

**Example:**

```python
from DrissionPage import ChromiumPage
from DrissionPage.common import Actions

page = ChromiumPage()
ac = Actions(page)
page.get('https://www.baidu.com')
ac.move_to('#kw').click().type('DrissionPage')
ac.move_to('#su').click()
```

---

### 📌 Operation Modes

Multiple actions can be chained together:

```python
ac.move_to(ele).click().type('some text')
```

or the actions can be executed separately:

```python
ac.move_to(ele)
ac.click()
ac.type('some text')
```

Both methods produce the same result, and each action will be executed sequentially.

---

## ✅️ Moving the Mouse

### 📌 `move_to()`

This method moves the mouse to the center of an element or to an absolute coordinate on the page. You can set an offset, which is relative to the top-left corner of the element.

|   Initialization Parameter    |                       Type                        | Default | Description                                                                                                        |
|:----------------------------:|:------------------------------------------------:|:-------:|------------------------------------------------------------------------------------------------------------------|
|         `ele_or_loc`         | ChromiumElement<br/>str<br/>Tuple[int, int] | Required | The element object, text locator, or absolute coordinates (as a `tuple`(int, int))                                   |
|          `offset_x`          |                      int                       |   0   | The x-axis offset, with positive values to the right and negative values to the left                                |
|          `offset_y`          |                      int                       |   0   | The y-axis offset, with positive values downwards and negative values upwards                                       |
|          `duration`          |                     float                      |  0.5  | The duration of the movement, pass in `0` to instantly move                                                      |

|        Return Type         |                 Description                 |
|:------------------------:|--------------------------------------------|
|         `Actions`         | The actions chain object itself             |

**Example:** Move the mouse to the element `ele`

```python
ele = page('tag:a')
ac.move_to(ele_or_loc=ele)
```

---

### 📌 `move()`

This method moves the mouse a certain distance relative to its current position.

| Parameter Name |  Type   | Default | Description                             |
|:-------------:|:------:|:-------:|----------------------------------------|
|   `offset_x`  |  int   |    0    | The x-axis offset, with positive values to the right and negative values to the left |
|   `offset_y`  |  int   |    0    | The y-axis offset, with positive values downwards and negative values upwards     |
|   `duration`  | float  |   0.5   | The duration of the movement, pass in `0` to instantly move                     |

|        Return Type         |                 Description                 |
|:------------------------:|--------------------------------------------|
|         `Actions`         | The actions chain object itself             |

**Example:** Move the mouse 300 pixels to the right

```python
ac.move(300, 0)
```

---

### 📌 `up()`

This method moves the mouse a certain distance upwards from its current position.

| Parameter Name |  Type   | Default | Description        |
|:-------------:|:------:|:-------:|-------------------|
|     `pixel`    |  int   | Required   | The distance to move the mouse upwards |

|        Return Type         |                 Description                 |
|:------------------------:|--------------------------------------------|
|         `Actions`         | The actions chain object itself             |

**Example:** Move the mouse 50 pixels upwards

```python
ac.up(50)
```

---

### 📌 `down()`

This method moves the mouse a certain distance downwards from its current position.

| Parameter Name |  Type   | Default | Description          |
|:-------------:|:------:|:-------:|---------------------|
|   `pixel`    |  int   | Required   | The distance to move the mouse downwards |

|        Return Type         |                 Description                 |
|:------------------------:|--------------------------------------------|
|         `Actions`         | The actions chain object itself             |

**Example:**

This method is used to move the mouse left by a certain distance relative to the current position.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:|-------------|
| `pixel` | `int` | Required | The number of pixels to move the mouse by |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

**Example:**

```python
ac.left(50)
```

---

### 📌 `right()`

This method is used to move the mouse right by a certain distance relative to the current position.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:|-------------|
| `pixel` | `int` | Required | The number of pixels to move the mouse by |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

**Example:**

```python
ac.right(50)
```

---

## ✅️ Mouse Buttons

### 📌 `click()`

This method is used to click the left mouse button, and can be preceded by moving to an element.

| Parameter Name |                      Type                     | Default Value |    Description     |
|:--------------:|:---------------------------------------------:|:-------------:|:------------------:|
|   `on_ele`    | `ChromiumElement`<br/>`str` |     `None`    | The element object or text locator to click on |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

**Example:**

```python
ac.click('#div1')
```

---

### 📌 `r_click()`

This method is used to click the right mouse button, and can be preceded by moving to an element.

| Parameter Name |                      Type                     | Default Value |    Description     |
|:--------------:|:---------------------------------------------:|:-------------:|:------------------:|
|   `on_ele`    | `ChromiumElement`<br/>`str` |     `None`    | The element object or text locator to click on |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

**Example:**

```python
ac.r_click('#div1')
```

---

### 📌 `m_click()`

This method is used to click the middle mouse button, and can be preceded by moving to an element.

| Parameter Name |                      Type                     | Default Value |    Description     |
|:--------------:|:---------------------------------------------:|:-------------:|:------------------:|
|   `on_ele`    | `ChromiumElement`<br/>`str` |     `None`    | The element object or text locator to click on |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

**Example:**

```python
ac.m_click('#div1')
```

---

### 📌 `db_click()`

This method is used to double-click the left mouse button, and can be preceded by moving to an element.

| Parameter Name |                      Type                     | Default Value |    Description     |
|:--------------:|:---------------------------------------------:|:-------------:|:------------------:|
|   `on_ele`    | `ChromiumElement`<br/>`str` |     `None`    | The element object or text locator to click on |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

---

### 📌 `hold()`

This method is used to hold down the left mouse button without releasing it, and can be preceded by moving to an element.

| Parameter Name |                      Type                     | Default Value |    Description     |
|:--------------:|:---------------------------------------------:|:-------------:|:------------------:|
|   `on_ele`    | `ChromiumElement`<br/>`str` |     `None`    | The element object or text locator to hold down the button on |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

**Example:**

```python
ac.hold('#div1')
```

---

### 📌 `release()`

This method is used to release the left mouse button, and can be preceded by moving to an element.

| Parameter Name |                      Type                     | Default Value |    Description     |
|:--------------:|:---------------------------------------------:|:-------------:|:------------------:|
|   `on_ele`    | `ChromiumElement`<br/>`str` |     `None`    | The element object or text locator to release the button on |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

**Example:** Move to an element and then release the left mouse button

```python
ac.release('#div1')
```

---

### 📌 `r_hold()`

This method is used to hold down the right mouse button without releasing it, and can be preceded by moving to an element.

| Parameter Name |                      Type                     | Default Value |    Description     |
|:--------------:|:---------------------------------------------:|:-------------:|:------------------:|
|   `on_ele`    | `ChromiumElement`<br/>`str` |     `None`    | The element object or text locator to hold down the button on |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

---

### 📌 `r_release()`

This method is used to release the right mouse button, and can be preceded by moving to an element.

| Parameter Name |                      Type                     | Default Value |    Description     |
|:--------------:|:---------------------------------------------:|:-------------:|:------------------:|
|   `on_ele`    | `ChromiumElement`<br/>`str` |     `None`    | The element object or text locator to release the button on |

| Return Type | Description |
|:-----------:|-------------|
| `Actions` | The action chain object itself |

---

### 📌 `m_hold()`

This method is used to hold down the middle mouse button. You can move to the element before holding.

|   Parameter    |           Type           | Default | Description                        |
|:-------------:|:------------------------:|:-------:|-----------------------------------|
|   `on_ele`    | `ChromiumElement`<br/>`str` |  `None` | The element object or text locator to be held |

|  Return Type  | Description                   |
|:------------:|------------------------------|
|  `Actions`   | The action chain object itself |

---

### 📌 `m_release()`

This method is used to release the middle mouse button. You can move to the element before releasing.

|   Parameter    |           Type           | Default | Description                          |
|:-------------:|:------------------------:|:-------:|-------------------------------------|
|   `on_ele`    | `ChromiumElement`<br/>`str` |  `None` | The element object or text locator to be released |

|   Return Type   | Description                    |
|:--------------:|-------------------------------|
|   `Actions`    | The action chain object itself |

---

## ✅️ Scroll the Mouse Wheel

### 📌 `scroll()`

This method is used to scroll the mouse wheel. You can move to the element before scrolling.

|   Parameter   |  Type  | Default | Description                                        |
|:------------:|:-----:|:------:|---------------------------------------------------|
|  `delta_x`   | `int` |  `0`   | The change of the x-axis of the mouse wheel scrolling, positive when scrolling to the right and negative to the left |
|  `delta_y`   | `int` |  `0`   | The change of the y-axis of the mouse wheel scrolling, positive when scrolling down and negative when scrolling up |
|   `on_ele`   | `ChromiumElement`<br/>`str` | `None` | The element object or text locator to be scrolled |

| Return Type  | Description                   |
|:------------:|------------------------------|
|  `Actions`   | The action chain object itself |

---

## ✅️ Keyboard Keys and Text Input

### 📌 `key_down()`

This method is used to press a key on the keyboard. Non-string keys (such as ENTER) can input their names or use the Keys class to obtain them.

| Parameter |  Type  | Default | Description                                            |
|:---------:|:-----:|:------:|-------------------------------------------------------|
|   `key`   | `str` | Required  | The name of the key, or the key value obtained from `Keys` class |

|  Return Type  | Description                   |
|:------------:|------------------------------|
|  `Actions`   | The action chain object itself |

**Example:** Press the ENTER key

```python
from DrissionPage.common import Keys

ac.key_down('ENTER')  # Input the key name

ac.key_down(Keys.ENTER)  # Get the key from Keys
```

---

### 📌 `key_up()`

This method is used to release a key on the keyboard. Non-string keys (such as ENTER) can input their names or use the Keys class to obtain them.

| Parameter |  Type  | Default | Description                                            |
|:---------:|:-----:|:------:|-------------------------------------------------------|
|   `key`   | `str` | Required  | The name of the key, or the key value obtained from `Keys` class |

|  Return Type  | Description                   |
|:------------:|------------------------------|
|  `Actions`   | The action chain object itself |

**Example:** Release the ENTER key

```python
from DrissionPage.common import Keys

ac.key_up('ENTER')  # Input the key name

ac.key_up(Keys.ENTER)  # Get the key from Keys
```

---

### 📌 `type()`

This method is used to enter text or keys as if typing on the keyboard. Combining keys or entering multiple segments of text.

Only supports keys that exist on the keyboard. For other text input, use `actions.input()`.

|  Parameter  |           Type           | Default | Description                                                    |
|:----------:|:------------------------:|:-------:|----------------------------------------------------------------|
|   `keys`   | `str`<br/>`list`<br/>`tuple` | Required  | The text or keys to be entered. Multiple segments or combination keys can be passed in as a `list` or `tuple` |

|  Return Type  | Description                   |
|:------------:|------------------------------|
|  `Actions`   | The action chain object itself |

**Example:**

```python
# Enter a segment of text
ac.type('text')

# Enter multiple segments of text
ac.type(('ab', 'cd'))

# Move the cursor to the left by one character and then enter text
ac.type((Keys.LEFT, 'abc'))
```

---

### 📌 `input()`

This method is used to enter a segment or multiple segments of text, or keys. Combining keys or entering multiple segments of text.

Multiple segments or combination keys are passed in as a list.

|  Parameter  |           Type           | Default | Description                                                    |
|:----------:|:------------------------:|:-------:|----------------------------------------------------------------|
|   `text`   | `str`<br/>`list`<br/>`tuple` | Required  | The text or keys to be entered. Multiple segments or combination keys can be passed in as a `list` or `tuple` |

|  Return Type  | Description                   |
|:------------:|------------------------------|
|  `Actions`   | The action chain object itself |

**Example:**

```python
from DrissionPage import ChromiumPage

p = ChromiumPage()
p.get('https://www.baidu.com')
p.actions.click('#kw').input('DrissionPage')
```

---

## ✅️ Waiting

### 📌 `wait()`

This method is used to pause the action chain.

| Parameter |  Type  | Default | Description                            |
|:---------:|:-----:|:------:|---------------------------------------|
| `second`  | `float` | Required  | The number of seconds to wait |

|  Return Type  | Description                   |
|:------------:|------------------------------|
|  `Actions`   | The action chain object itself |

**Example:** Pause for 3 seconds

```python
ac.wait(3)
```

---

## ✅️ Example

### 📌 Simulate pressing ctrl+a

```python
from DrissionPage import ChromiumPage
from DrissionPage.common import Keys, Actions

# Create a page
page = ChromiumPage()
# Create an Actions object
ac = Actions(page)

# Move the mouse to the <input> element
ac.move_to('tag:input')
# Click the mouse to place the cursor in the element
ac.click()
# Press the ctrl key
ac.key_down(Keys.CTRL)
# Type 'a'
ac.type('a')
# Release the ctrl key
ac.key_up(Keys.CTRL)
```

Chain writing:

```python
ac.click('tag:input').key_down(Keys.CTRL).type('a').key_up(Keys.CTRL)
```

---

### 📌 Dragging an element

Drag an element 300 pixels to the right:

```python
from DrissionPage import ChromiumPage
from DrissionPage.common import Actions

# Create a page
page = ChromiumPage()
# Create an Actions object
ac = Actions(page)

# Hold down the left mouse button on the element
ac.hold('#div1')
# Move the mouse 300 pixels to the right
ac.right(300)
# Release the left mouse button
ac.release()
```

Drag an element to another element:

```python
ac.hold('#div1').release('#div2')
```

## ✅️ Built-in Actions in the Page Object

The `actions` attribute of the Page Object provides an Actions object dedicated to that page object.

The usage of this object is the same as described above.

The only difference is that the built-in Actions object will wait for the page to finish loading before executing, while the external one will not.

**Example:**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.actions.move_to((300, 500)).hold().move(300).release()
```

