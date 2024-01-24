🚄 Get Element Information
---

The `SessionPage` object and `WebPage` object retrieve elements in `SessionElement` mode. This section introduces its attributes.

Assume `ele` is the object of the following `div` element, this section uses this element for examples:

```html
<div id="div1" class="divs">Hello World!
    <p>行元素</p>
    <!--这是注释-->
</div>
```

## ✅️️ `html`

This attribute returns the outerHTML text of the element.

**Return Type:** `str`

```python
print(ele.html)
```

**Output:**

```shell
<div id="div1" class="divs">Hello World!
    <p>行元素</p>
    <!--这是注释-->
</div>
```

---

## ✅️️ `inner_html`

This attribute returns the innerHTML text of the element.

**Return Type:** `str`

```python
print(ele.inner_html)
```

**Output:**

```shell
Hello World!
    <p>行元素</p>
    <!--这是注释-->
```

---

## ✅️️ `tag`

This attribute returns the tag name of the element.

**Return Type:** `str`

```python
print(ele.tag)
```

**Output:**

```shell
div
```

---

## ✅️️ `text`

This attribute returns a string that is the combination of all the texts inside the element.  
The string is formatted, i.e., encoded and removed extra line breaks, for a better readability.

**Return Type:** `str`

```python
print(ele.text)
```

**Output:**

```shell
Hello World!
行元素
```

---

## ✅️️ `raw_text`

This attribute returns the raw text inside the element.

**Return Type:** `str`

```python
print(ele.raw_text)
```

Output (note that the space and line breaks between elements are preserved):

```shell
Hello World!
    行元素
    
```

---

## ✅️️ `texts()`

This method returns the texts of all the **direct** child nodes inside the element, including element and text nodes. It has a parameter `text_node_only`, which controls whether only text nodes that are not wrapped by any element should be returned. This method is useful for cases where text nodes and element nodes are mixed.

| Parameter Name      | Type     | Default Value | Description                                 |
|:-------------------:|:--------:|:-------------:| ----------------------------------------- |
| `text_node_only`    | `bool`   | `False`       |  Whether to only return text nodes              |

| Return Type    | Description                          |
|:--------------:| ------------------------------------ |
| `List[str]`    | List of texts                         |

**Example:**

```python
print(e.texts())  
print(e.texts(text_node_only=True))  
```

**Output:**

```shell
['Hello World!', '行元素']
['Hello World!']
```

---

## ✅️️ `comments`

This attribute returns a list of comments inside the element.

**Return Type:** `List[str]`

```python
print(ele.comments)
```

**Output:**

```shell
[<!--这是注释-->]
```

---

## ✅️️ `attrs`

This attribute returns a dictionary of all attributes and their values of the element.

**Return Type:** `dict`

```python
print(ele.attrs)
```

**Output:**

```shell
{'id': 'div1', 'class': 'divs'}
```

---

## ✅️️ `attr()`

This method returns the value of a specific `attribute` of the element. It takes a string parameter `attr` and returns the value of that attribute as a string. If the attribute does not exist, `None` is returned.  
The returned `src` and `href` attributes are the complete paths. The `text` attribute is the formatted text.

**Return Type:** `str` or `None`

| Parameter Name   | Type     | Default Value | Description                           |
|:-------------:|:------:|:-------------:| --------------------------------- |
| `attr`        | `str`  | Required      |  Attribute name                      |

| Return Type   | Description                          |
|:-------------:| ------------------------------------ |
| `str`         | Attribute value text                  |
| `None`        | None is returned if the attribute does not exist |

**Example:**

```python
print(ele.attr('id'))
```

**Output:**

```shell
div1
```

---

## ✅️️ `link`

This method returns the `href` attribute or `src` attribute of the element. If neither of these two attributes exists, `None` is returned.

**Return Type:** `str`

```html
<a href='http://www.baidu.com'>百度</a>
```

Assume `a_ele` is the object of the above element:

```python
print(a_ele.link)
```

**Output:**

```shell
http://www.baidu.com
```

---

## ✅️️ `page`

This attribute returns the page object where the element is located. For `SessionElement` generated directly from html text, its `page` attribute is `None`.

**Return Type:** `SessionPage` or `WebPage`

```python
page = ele.page
```

---

## ✅️️ `xpath`

This attribute returns the absolute xpath of the element in the page.

**Return Type:** `str`

```python
print(ele.xpath)
```

**Output:**

```shell
/html/body/div
```

---

## ✅️️ `css_path`

This attribute returns the absolute css selector path of the element in the page.

**Return Type:** `str`

```python
print(ele.css_path)
```

**Output:**

```shell
:nth-child(1)>:nth-child(1)>:nth-child(1)
```

---

## ✅️️ Example

The following example can be directly run to view the results:

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('https://gitee.com/explore')

## 翻译 private_upload\default_user\2024-01-24-16-48-58\get_element_info.md.part-1.md

# Get all `a` elements under the recommended directory
li_eles = page('tag:ul@@text():Recommended projects').eles('t:a')

# Iterate through the list
for i in li_eles:  
    # Get and print the tag name, text, and href attribute
    print(i.tag, i.text, i.attr('href'))
```

**Output:**

```shell
a Recommended projects https://gitee.com/explore/all
a Cutting-edge technologies https://gitee.com/explore/new-tech
a Smart hardware https://gitee.com/explore/hardware
a IoT/Internet of Things/Edge computing https://gitee.com/explore/iot
a Vehicle applications https://gitee.com/explore/vehicle
...the rest is omitted


```