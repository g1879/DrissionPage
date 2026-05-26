🚤 iframe Operation
---

The `<iframe>` element is a special element that is both an element and a page, so a separate section is dedicated to its introduction.

Unlike selenium, DrissionPage can handle `<iframe>` elements without switching in and out. Therefore, it can realize operations such as cross-level element search, separate navigation within elements, simultaneous operation of inside and outside elements of `<iframe>`, multi-threaded control of multiple `<iframe>`, etc., with more flexible functions and clearer logic.

We use the Runoob online editor for demonstration:

[Runoob Online Editor](https://www.runoob.com/try/try.php?filename=tryhtml_iframe)

Make some adjustments to the content in the source code box, and then click "Run":

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Runoob.com</title>
</head>

<body>
<iframe id="sss" src="https://www.runoob.com">
    <p>Your browser does not support iframe tags.</p>
</iframe>
</body>
</html>
```

Press `F12`, you can see a two-layer `<iframe>` on the right side of the web page. The `<iframe>` with an id of `'iframeResult'` has an `<iframe>` with an id of `'sss'` inside. The innermost `<iframe>` page points to https://www.runoob.com.

---

## ✅️ Get `<iframe>` Object

There are two methods to get the `<iframe>` object. You can use the same method as getting a normal element, or use the `get_frame()` method. It is recommended to use the `get_frame()` method, because when obtaining it as a normal element, the IDE cannot correctly recognize the `<iframe>` element obtained.

### 📌 `get_frame()`

This method is used to get a `<frame>` or `<iframe>` object in the page.

| Parameter Name |         Type         | Default | Description                                                 |
|:--------------:|:--------------------:|:-------:|-------------------------------------------------------------|
| `loc_ind_ele`  | `str`<br/>`int`<br/>`ChromiumFrame` | Required | Locator<br/>Index of `<iframe>` element (starts from `1`, negative numbers represent reverse index)<br/>`ChromiumFrame object`<br/>`id` attribute content<br/>`name` attribute content |
|   `timeout`    |       `float`        | `None`  | Timeout, use the page timeout if `None`                                 |

|  Return Type  | Description                                          |
|:------------:|------------------------------------------------------|
| `ChromiumFrame` | Object of `<frame>` or `<iframe>` element |
| `NoneElement` | Returns `NoneElement` when not found         |

:::warning Note
    It should be noted that if there are nested `<iframe>` in the page, obtaining it by index may be inaccurate.
    For example, in the website mentioned above, `get_frames()` can obtain 6 elements, but `get_frame(6)` cannot obtain the last one.
    This is because there are two nested `<iframe>`, which causes the inaccuracy of the obtained result.
:::

**Example:**

```python
# Get it using a locator
iframe = page.get_frame('#sss')

# Get the second iframe
iframe = page.get_frame(1)
```

---

### 📌 `get_frames()`

This method is used to get multiple `<frame>` or `<iframe>` objects that meet the conditions in the page.

| Parameter Name |         Type         | Default | Description                       |
|:--------------:|:--------------------:|:-------:|-----------------------------------|
| `loc_ind_ele`  | `str`<br/>`int`<br/>`ChromiumFrame` | `None`  | Locator, returns all if `None` |
|   `timeout`    |       `float`        | `None`  | Timeout, use the page timeout if `None` |

|    Return Type     | Description                                              |
|:-----------------:|----------------------------------------------------------|
| `List[ChromiumFrame]` | List composed of `<frame>` or `<iframe>` element objects |

---

### 📌 Normal Element Method

You can also obtain the `<iframe>` object using the same method as obtaining a normal element:

```python
iframe = page('#sss')
print(iframe.html)
```

**Output:**

```shell
<iframe id="sss" src="https://www.runoob.com"><html><head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Runoob.com - Learning is not just technology, it's dreams!</title>

  <meta name="robots" content="max-image-preview:large">

...truncated...
```

This `ChromiumFrame` object is both a page and an element. Since the IDE does not prompt the properties and methods related to the `<iframe>` element object, it is recommended to wrap it with `get_frame()` when using this method to obtain it:

```python
iframe = page('#sss')
iframe = page.get_frame(iframe)
```

---

## ✅️ Find Elements Inside `<iframe>`

From the obtained element object just now, we can see that we do not need to switch to the `<iframe>` with an id of `'iframeResult'` to obtain the elements inside it. Therefore, it is not necessary to first obtain the `ChromiumFrame` object in order to obtain the elements. 

### 📌 Find Inside `<iframe>`

With the element we obtained just now, we can find elements inside it:

```python
ele = iframe('Home')
print(ele)
```

**Output:**

```shell
<ChromiumElement a href='https://www.runoob.com/' data-id='index' title='菜鸟教程' class='current'>
```

---

### 📌 Cross Page Search of `<iframe>`

If the URL of the `<iframe>` element is in the same domain as the main page, we can directly search for elements inside the `<iframe>` using the page object without obtaining a `ChromiumFrame` object first:

```python
ele = page('Homepage')
print(ele)
```

**Output:**

```shell
<ChromiumElement a href='https://www.runoob.com/' data-id='index' title='菜鸟教程' class='current'>
```

If it is in the same domain, we can directly obtain the elements using the page object, regardless of how many levels of `<iframe>` it crosses.

---

### 📌 Comparison with Selenium

`WebPage`:

```python
from DrissionPage import WebPage

page = WebPage()
ele = page('Homepage')
```

Traditional Selenium workflow:

```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.switch_to.frame('iframeResult')
driver.switch_to.frame('sss')
ele = driver.find_element('xpath', '//*[text()=\"Homepage\"]')
driver.switch_to.default_content()
```

As you can see, the original logic of switching in and out is more cumbersome.

---

### 📌 Important Note

If the `<iframe>` is in a different domain from the current tab, you cannot directly search for elements inside it using the page object. Instead, you need to obtain its `ChromiumFrame` element object and then search within that object.

---

## ✅️ Element Properties of `ChromiumFrame`

As mentioned above, `ChromiumFrame` is both an element and a page. Below are the usage instructions for its element properties.

### 📌 `tag`

This property returns the name of the element.

**Type:** `str`

---

### 📌 `html`

This property returns the outerHTML text of the entire `<iframe>` element.

**Type:** `str`

---

### 📌 `inner_html`

This property returns the innerHTML text.

**Type:** `str`

---

### 📌 `attrs`

This property returns all attributes of the element as a dictionary.

**Type:** `dict`

---

### 📌 `xpath`

This property returns the xpath path of the element on its page.

**Type:** `str`

---

### 📌 `css_path`

This property returns the css selector path of the element on its page.

**Type:** `str`

---

### 📌 `attr()`

This method is used to retrieve an attribute of the element.

| Parameter | Type  | Default | Description |
|:---------:|:-----:|:------:|------------|
|   `attr`  | `str` |   N/A  | Attribute name |

|  Return Type | Description                   |
|:-----------:|-------------------------------|
|    `str`    | Attribute value text           |
|    `None`   | Returns `None` if no attribute exists |

---

### 📌 `set.attr()`

This method is used to set the attribute of the element.

| Parameter  |  Type  | Default | Description |
|:----------:|:-----:|:------:|------------|
|   `attr`   | `str` |   N/A  | Attribute name |
|  `value`   | `str` |   N/A  | Attribute value |

**Returns:** `None`

---

### 📌 `remove_attr()`

This method is used to remove an attribute of the element.

| Parameter | Type  | Default | Description |
|:---------:|:-----:|:------:|------------|
|   `attr`  | `str` |   N/A  | Attribute name |

**Returns:** `None`

---

### 📌 Relative Positioning

Relative positioning methods are the same as regular elements, please refer to the section about acquiring elements.

- `parent()`: Returns the parent element at a certain level.

- `prev()`: Returns the previous sibling element.

- `next()`: Returns the next sibling element.

- `before()`: Returns the element before the current element.

- `after()`: Returns the element after the current element.

- `prevs()`: Returns a list of all previous sibling elements or nodes.

- `nexts()`: Returns a list of all next sibling elements or nodes.

- `befores()`: Returns a list of all sibling elements or nodes after the current element that meet the conditions.

---

## ✅️ Page Properties of `ChromiumFrame`

### 📌 `url`

This property returns the current URL of the page.

**Type:** `str`

---

### 📌 `title`

This property returns the current title text of the page.

**Type:** `str`

---

### 📌 `cookies`

This property returns the current content of the cookies on the page.

**Type:** `dict`

---

### 📌 `get()`

This method is used to navigate to another page within the `<iframe>`, and the usage is the same as `ChromiumPage`.

```python
iframe.get('https://www.runoob.com/css3/css3-tutorial.html')
```

### 📌 `refresh()`

This method is used to refresh the page.

**Parameters**: None

**Returns**: `None`

```python
iframe.refresh()
```

---

### 📌 `active_ele`

This attribute returns the element on which the focus is currently placed in the page.

**Type**: `ChromiumElement`

---

### 📌 `run_js()`

This method is used to execute JavaScript scripts within the `<iframe>`.

| Parameter Name | Type   | Default Value | Description                                                  |
| -------------- | ------ | ------------- | ------------------------------------------------------------ |
| `script`       | `str`  | Required      | The JavaScript script text to be executed                    |
| `*args`        | -      | N/A           | The parameters to be passed to the script in the order of `arguments[0]`, `arguments[1]`, etc. |
| `as_expr`      | `bool` | `False`       | Whether to run the script as an expression, if `True`, the `args` parameter is ignored |
| `timeout`      | `float`| `None`        | The timeout for the script, if `None`, use the page `timeouts.script` setting |

| Return Type | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| `Any`       | The result of the script execution                           |

---

### 📌 `scroll`

The scrolling methods of `ChromiumFrame` are the same as those of the page or element.

**Example**: Scroll the `<iframe>` element down by 300 pixels

```python
iframe.scroll.down(300)
```

---

### 📌 `get_screenshot()`

This method is used to take a screenshot of the `<iframe>`. Due to technical limitations, only a viewport screenshot is available.

The three parameters below are mutually exclusive, with the order of priority: `as_bytes` > `as_base64` > `path`.

| Parameter Name | Type              | Default Value | Description                                                                                                                  |
| -------------- | ----------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `path`         | `str` <br/>`Path` | `None`        | The path to save the image, if `None`, the image will be saved in the current directory                                 |
| `name`         | `str`             | `None`        | The complete file name, the suffix can be `'jpg'`, `'jpeg'`, `'png'`, `'webp'`, if `None`, the image will be saved in jpg format |
| `as_bytes`     | `str` <br/>`True` | `None`        | Whether to return the image as bytes, can be `'jpg'`, `'jpeg'`, `'png'`, `'webp'`, `None`, `True`.<br/>When not `None`, the `path` and `as_base64` parameters are invalid. When `True`, jpg format is used |
| `as_base64`    | `str` <br/>`True` | `None`        | Whether to return the image as base64, can be `'jpg'`, `'jpeg'`, `'png'`, `'webp'`, `None`, `True`.<br/>When not `None`, the `path` parameter is invalid. When `True`, jpg format is used |

| Return Type | Description                                                           |
| ----------- | --------------------------------------------------------------------- |
| `bytes`     | Returns the image bytes when `as_bytes` is in effect                   |
| `str`       | Returns the complete path of the image when `as_bytes` and `as_base64` are `None` |
| `str`       | Returns the base64 formatted string when `as_base64` is in effect      |

---

## ✅️ Position and Size

### 📌 `rect.location`

This attribute returns the coordinates of the top left corner of the iframe element in the page. Format: (x, y), with the top left being (0, 0).

**Return Type**: `Tuple[float, float]`

---

### 📌 `rect.viewport_location`

This attribute returns the coordinates of the top left corner of the iframe element in the viewport. Format: (x, y), with the top left being (0, 0).

**Return Type**: `Tuple[float, float]`

---

### 📌 `rect.screen_location`

This attribute returns the coordinates of the top left corner of the iframe element on the screen. Format: (x, y), with the top left being (0, 0).

**Return Type**: `Tuple[float, float]`

---

### 📌 `rect.size`

This attribute returns the size of the page inside the frame. Format: (width, height).

**Return Type**: `Tuple[float, float]`

---

### 📌 `rect.viewport_size`

This attribute returns the size of the iframe viewport. Format: (width, height).

**Return Type**: `Tuple[float, float]`

---

### 📌 `rect.corners`

This attribute returns the coordinates of the four corners of the iframe element in the page. Order: top left, top right, bottom right, bottom left.

**Return Type**: `((float, float), (float, float), (float, float), (float, float),)`

---

### 📌 `rect.viewport_corners`

This attribute returns the coordinates of the four corners of the iframe element in the viewport. Order: top left, top right, bottom right, bottom left.

**Return Type**: `((float, float), (float, float), (float, float), (float, float),)`

---

## ✅️ Object States

### 📌 `states.is_loading`

This attribute returns whether the page is in loading state.

**Return Type**: `bool`

---

### 📌 `states.is_alive`

This attribute returns whether the frame element is available and still contains frames.

**Return Type**: `bool`

---

### 📌 `states.is_displayed`

This attribute returns whether the iframe is displayed.

**Return Type**: `bool`

---

### 📌 `states.ready_state`

This attribute returns the loading state, with 4 possible values:

- 'connecting': the web page is connecting
- 'loading': the document is still loading
- 'interactive': the DOM has loaded but the resources have not
- 'complete': all content has finished loading

**Return Type**: `str`

