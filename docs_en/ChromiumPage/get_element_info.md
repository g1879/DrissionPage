🚤 Get Element Information
---

The objects corresponding to browser elements are `ChromiumElement` and `ShadowRoot`. In this section, we will discuss how to retrieve information about an element after obtaining its object.

`ChromiumElement` inherits all the properties of `SessionElement` and provides additional information specific to the browser. This section focuses on how to retrieve browser-specific element information.

## ✅️️ Common Information with `SessionElement`

Here is a list of attributes and methods that are shared with `SessionElement`. For detailed usage, please refer to the "Retrieve Element Information" section of the "Send and Receive Data Packets" part.

| Attribute/Method | Description |
|:-------------:|-------------|
|    `html`    | This attribute returns the `outerHTML` text of the element |
| `inner_html` | This attribute returns the `innerHTML` text of the element |
|    `tag`     | This attribute returns the tag name of the element |
|    `text`    | This attribute returns a string that represents the combined text of all contents within the element |
|  `raw_text`  | This attribute returns the raw text within the element |
|  `texts()`   | This method returns the text of all **direct** child nodes of the element, including elements and text nodes |
|  `comments`  | This attribute returns a list of comments within the element |
|   `attrs`    | This attribute returns a dictionary of all attributes and their values for the element |
|   `attr()`   | This method returns the value of a specific `attribute` of the element |
|    `link`    | This method returns the `href` or `src` attribute of the element |
|    `page`    | This attribute returns the page object the element belongs to |
|   `xpath`    | This attribute returns the absolute xpath of the element within the page |
|  `css_path`  | This attribute returns the absolute css selector of the element within the page |

---

## ✅️️ Size and Position

### 📌 `rect.size`

This attribute returns the size of the element as a tuple.

**Type:** `Tuple[float, float]`

```python
size = ele.rect.size
# Returns: (50, 50)
```

---

### 📌 `rect.location`

This attribute returns the coordinates of the **top-left corner** of the element on the **entire page** as a tuple.

**Type:** `Tuple[float, float]`

```python
loc = ele.rect.location
# Returns: (50, 50)
```

---

### 📌 `rect.midpoint`

This attribute returns the coordinates of the **center** of the element on the **entire page** as a tuple.

**Type:** `Tuple[float, float]`

```python
loc = ele.rect.midpoint
# Returns: (55, 55)
```

---

### 📌 `rect.click_point`

This attribute returns the coordinates of the **clicking point** of the element on the **entire page** as a tuple.

The clicking point refers to the position where `click()` method would click and is located at the top part of the element.

**Type:** `Tuple[float, float]`

---

### 📌 `rect.viewport_location`

This attribute returns the coordinates of the **top-left corner** of the element in the **current viewport** as a tuple.

**Type:** `Tuple[float, float]`

---

### 📌 `rect.viewport_midpoint`

This attribute returns the coordinates of the **center** of the element in the **current viewport** as a tuple.

**Type:** `Tuple[float, float]`

---

### 📌 `rect.viewport_click_point`

This attribute returns the coordinates of the **clicking point** of the element in the **current viewport** as a tuple.

**Type:** `Tuple[float, float]`

---

### 📌 `rect.screen_location`

This attribute returns the coordinates of the **top-left corner** of the element on the **screen** as a tuple.

**Type:** `Tuple[float, float]`

---

### 📌 `rect.screen_midpoint`

This attribute returns the coordinates of the **center** of the element on the **screen** as a tuple.

**Type:** `Tuple[float, float]`

---

### 📌 `rect.screen_click_point`

This attribute returns the coordinates of the **clicking point** of the element on the **screen** as a tuple.

**Type:** `Tuple[float, float]`

---

### 📌 `rect.corners`

This attribute returns the coordinates of the four corners of the element within the page as a list. The order of corners is: top-left, top-right, bottom-right, bottom-left.

**Type:** `((float, float), (float, float), (float, float), (float, float),)`

---

### 📌 `rect.viewport_corners`

This attribute returns the coordinates of the four corners of the element within the viewport as a list. The order of corners is: top-left, top-right, bottom-right, bottom-left.

**Type:** `list[(float, float), (float, float), (float, float), (float, float)]`

---

### 📌 `rect.viewport_rect`

This attribute returns the coordinates of the four corners of the element within the viewport as a list. The order of corners is: top-left, top-right, bottom-right, bottom-left.

**Type:** `List[(float, float), (float, float), (float, float), (float, float)]`

---

## ✅️️ Attributes and Content

### 📌 `pseudo.before`

This attribute returns the content of the `::before` pseudo-element of the current element as a text.

**Type:** `str`

```python
before_txt = ele.pseudo.before
```

---

### 📌 `pseudo.after`

This attribute returns the content of the `::after` pseudo-element of the current element as a text.

**Type:** `str`

```python
after_txt = ele.pseudo.after
```

---

### 📌 `style()`

This method returns the value of a CSS style property of the element, including properties of pseudo-elements. It takes two parameters: `style` for the style property name, and `pseudo_ele` for the pseudo-element name. If `pseudo_ele` is omitted, it retrieves the style property of a normal element.

| Parameter Name | Type  | Default Value | Description |
|:------------:|:-----:|:----:|-----------|
|   `style`    | `str` | Mandatory  | Style name |
| `pseudo_element` | `str` | `''` | Pseudo element name (if any) |

| Return Type  | Description    |
|:-----:|-------|
| `str` | Style property value |

**Example:**

```python
# Get the color value of the CSS property
prop = ele.style('color')

# Get the content of the after pseudo element
prop = ele.style('content', 'after')
```

---

### 📌 `prop()`

This method returns the value of a given `property`. It takes a string parameter and returns the value of that property.

|  Parameter Name  |  Type   | Default Value | Description |
|:------:|:-----:|:---:|------|
| `prop` | `str` | Mandatory  | Property name |

| Return Type  | Description  |
|:-----:|-----|
| `str` | Property value |

---

### 📌 `shadow_root`

This attribute returns the shadow-root object inside the element, or `None` if there is none.

**Type:** `ShadowRoot`

---

## ✅️️ State Information

State information is stored in the `states` attribute.

### 📌`states.is_in_viewport`

This attribute returns a boolean value indicating whether the element is in the viewport, based on the clickability of the element.

**Type:** `bool`

---

### 📌`states.is_whole_in_viewport`

This attribute returns a boolean value indicating whether the entire element is in the viewport.

**Type:** `bool`

---

### 📌`states.is_whole_in_viewport`

This attribute returns a boolean value indicating whether the entire element is in the viewport.

**Type:** `bool`

---

### 📌`states.is_alive`

This attribute returns a boolean value indicating whether the element is still alive. It is used to determine if the element is no longer valid due to a page refresh in D mode.

**Type:** `bool`

---

### 📌 `states.is_checked`

This attribute returns a boolean value indicating whether a form radio or checkbox element is selected.

**Type:** `bool`

---

### 📌 `states.is_selected`

This attribute returns a boolean value indicating whether an item in a `<select>` element is selected.

**Type:** `bool`

---

### 📌 `states.is_enabled`

This attribute returns a boolean value indicating whether the element is enabled.

**Type:** `bool`

---

### 📌 `states.is_displayed`

This attribute returns a boolean value indicating whether the element is visible.

**Type:** `bool`

---

### 📌 `states.is_covered`

This attribute returns whether the element is covered by another element. If it is covered, the ID of the covering element is returned. Otherwise, it returns `False`.

|  Return Type   |       Description       |
|:-------:|:--------------:|
| `False` | Not covered, returns `False`  |
|  `int`   | If covered, returns the ID of the covering element |

---

### 📌 `states.has_rect`

This attribute returns whether the element has size and position information. If it does, it returns a list of coordinates of the four corners of the element on the page. If it doesn't, it returns `False`.

|  Return Type   | Description                                                        |
|:-------:|-----------------------------------------------------------|
| `list`  | If size and position information exists, it returns the coordinates of the four corners of the element as [(int, int), ...], in the order: top-left, top-right, bottom-right, bottom-left |
| `False` | If it doesn't exist, it returns `False`                                             |

---

## ✅️️ Save and Screenshot

The save feature is a unique feature of this library, which can directly read from the browser cache without relying on another UI library or re-downloading to save page resources.

For comparison, Selenium cannot save images by itself, often requiring the use of UI tools for assistance, which is not only inefficient and unreliable but also consumes keyboard and mouse resources.

### 📌 `get_src()`

This method returns the resource used by the `src` attribute of the element. Base64 data can be returned as `bytes`, while other resources are returned as `str`. If there is no resource, it returns `None`.

For example, you can retrieve the byte data of an image on the page for content recognition or save it to a file. JavaScript text can also be obtained from `<script>` tags.

|     Parameter Name      |      Type       |  Default Value  | Description                                     |
|:-----------------------:|:---------------:|:--------------:|-------------------------------------------------|
|   `timeout`             |     `float`     |     `None`     | Timeout for resource loading. If `None`, use the `timeout` attribute of the element's page |
| `base64_to_bytes`       |     `bool`      |     `True`     | If `True`, convert base64 data to `bytes` format |

|  Return Type  | Description           |
|:------:|-----------------------|
| `str`  | Resource string        |
| `None` | Returns `None` if no resource |

**Example:**

```python
img = page('tag:img')
src = img.get_src()
```

---

### 📌 `save()`

This method saves the resource obtained from the `get_src()` method to a file.

|     Parameter Name    |         Type         |  Default Value  | Description                                     |
|:---------------------:|:--------------------:|:--------------:|-------------------------------------------------|
|  `path`               | `str`<br/>`Path`     |     `None`     | File saving path. If `None`, save to the current folder |
|  `name`               |         `str`        |     `None`     | File name, including the extension. If `None`, get from the resource URL |
| `timeout`             |        `float`       |     `None`     | Timeout for resource loading. If `None`, use the `timeout` attribute of the element's page |

|  Return Type  | Description           |
|:------:|-----------------------|
| `str`  | Saving path           |

**Example:**

```python
img = page('tag:img')
img.save('D:\\img.png')
```

---

## ✅️️ `ShadowRoot` property

This library treats the shadow dom's `root` as an element to process, which can retrieve attributes and perform searches on its descendants. It follows the same logic as `ChromiumElement`, but with fewer properties. The available properties are as follows:

### 📌 `tag`

This property returns the element's tag name, which is `'shadow-root'`.

**Type:** `str`

---

### 📌 `html`

This property returns the html text of the `shadow_root`, wrapped in `<shadow_root></shadow_root>` tags.

**Type:** `str`

---

### 📌 `inner_html`

This property returns the inner html text of the `shadow_root`.

**Type:** `str`

---

### 📌 `page`

This property returns the page object where the element is located.

**Type:** `ChromiumPage`, `ChromiumTab`, `ChromiumFrame`, `WebPage`

---

### 📌 `parent_ele`

This property returns the attached regular element object.

**Type:** `ChromiumElement`

---

### 📌 `states.is_enabled`

Same as `ChromiumElement`.

**Type:** `bool`

---

### 📌 `states.is_alive`

Same as `ChromiumElement`.

**Type:** `bool`

---

## ✅️️ Compare Elements

Two element objects can be compared using `==` to determine if they refer to the same element.

**Example:**

```python
ele1 = page('t:div')
ele2 = page('t:div')
print(ele1==ele2)  # Outputs True
```

