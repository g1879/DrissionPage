## 🔦 Basic Usage

## ✅️️ Methods for finding elements

### 📌 `ele()`

Both the page object and the element object have this method, used to find an element that matches a specific condition.

The `ele()` method parameters have slightly different names for page objects and element objects, but the usage is the same.

The methods for obtaining elements in `SessionPage` and `ChromiumPage` are the same, but the former returns a `SessionElement` object, while the latter returns a `ChromiumElement` object.

|      Parameter Name       |              Type               | Default | Description                                                  |
| :-----------------------: | :-----------------------------: | :-----: | ------------------------------------------------------------ |
| `loc_or_str` (element object) |       `str` `Tuple[str, str]`      | Required | The locating information of the element. Can be a query string or a loc tuple |
| `loc_or_ele` (page object) | `str` `SessionElement` `Tuple[str, str]` | Required | The locating information of the element. Can be a query string, loc tuple, or a `SessionElement` object |
|          `index`          |              `int`               |   `1`   | The index of the element to retrieve. Starts from `1`, negative numbers can be used to count from the end |
|         `timeout`         |             `float`              |  `None` | The timeout for waiting for the element to appear. If `None`, the value set in the page object will be used, and it is invalid in `SessionPage` |

|     Return Type      | Description                                                  |
| :-----------------: | ------------------------------------------------------------ |
| `SessionElement`  | The first element object that matches the condition found by `SessionPage` or `SessionElement` |
| `ChromiumElement` | The first element object that matches the condition found by the browser page object or element object |
|  `ChromiumFrame`  | Returns `ChromiumFrame` when the result is a frame element, but this tip is not included in the IDE |
|   `NoneElement`   | Returns when no element that matches the condition is found |

Notes:

-   The loc tuple refers to the Selenium locator, for example: `(By.ID, 'XXXXX')`. The same below.
-   `ele('xxxx', index=2)` is the same as `eles('xxxx')[1]`, but the former is much faster.

**Example:**

```python
from DrissionPage import SessionPage

page = SessionPage()

# Find an element within the page
ele1 = page.ele('#one')

# Find a descendant element within ele1
ele2 = ele1.ele('The second row')

```

___

### 📌 `eles()`

This method is similar to `ele()`, but it returns a list of all matching elements.

Both the page object and the element object can call this method.

`eles()` returns a regular list, and indexing is needed for chained operations, such as `page.eles('...')[0].ele('...')`.

|  Parameter Name  |         Type          | Default | Description                                                  |
| :--------------: | :-------------------: | :-----: | ------------------------------------------------------------ |
| `loc_or_str` | `str` `Tuple[str, str]` | Required | The locating information of the element. Can be a query string or a loc tuple |
|    `timeout`    |        `float`        |  `None` | The timeout for waiting for the element to appear. If `None`, the value set in the page object will be used, and it is invalid in `SessionPage` |

|          Return Type           | Description                                                    |
| :---------------------------: | --------------------------------------------------------------- |
|    `List[SessionElement]`    | A list of all elements found by `SessionPage` or `SessionElement` |
| `List[ChromiumElement, ChromiumFrame]` | A list of all elements found by the browser page object or element object |

**Example:**

```python
# Get all p elements within the page
p_eles = page.eles('tag:p')

# Get all p elements within ele1
p_eles = ele1.eles('tag:p')

# Print the text of the first p element
print(p_eles[0])
```

___

## ✅️️ Matching Modes

The matching mode refers to the way in which the matching conditions are applied in a query and there are four types: exact matching, fuzzy matching, matching at the beginning, and matching at the end.

### 📌 Exact Matching `=`

Represents exact matching, matches the text or attribute that exactly matches the specified value.

```python
# Get the element with name attribute 'row1'
ele = page.ele('@name=row1')
```

___

### 📌 Fuzzy Matching `:`

Represents fuzzy matching, matches the text or attribute that contains the specified string.

```python
# Get the element with name attribute containing 'row1'
ele = page.ele('@name:row1')
```

___

### 📌 Matching at the Beginning `^`

Represents matching at the beginning, matches the text or attribute that begins with the specified string.

```python
# Get the element with name attribute starting with 'row1'
ele = page.ele('@name^ro')
```

___

### 📌 Matching at the End `$`

Represents matching at the end, matches the text or attribute that ends with the specified string.

```python
# Get the element with name attribute ending with 'w1'
ele = page.ele('@name$w1')
```

___

## ✅️️ Query Syntax

The keyword is placed at the leftmost side of the query statement to indicate which method to use to search for elements. It only takes effect when used at the beginning of the statement and used alone.

## 

```python
# Find the element with the id attribute equal to "one" on the page
ele1 = page.ele('#one')

# Find the element within ele1 that has an id attribute containing the text "ne"
ele2 = ele1.ele('#:ne')
```

___

### 📌 Class selector `.`

Represents the `class` attribute and is only effective when used at the beginning of the statement and on its own. It can be used in conjunction with matching patterns.

```python
# Find the element with the class attribute equal to "p_cls"
ele2 = ele1.ele('.p_cls')

# Find the element with the class attribute starting with "_cls"
ele2 = ele1.ele('.^_cls')
```

When using only `.`, it defaults to exact matching of the `class` attribute of the element. If an element has multiple class names, the complete value of the `class` attribute must be specified (the order of class names should also be unchanged). If you need to match only one of the multiple class names, you can use the fuzzy matching operator `:`.

```python
# Exact matching of the element with the class attribute equal to "p_cls1 p_cls2"
ele2 = ele1.ele('.p_cls1 p_cls2')

# Fuzzy matching of the element with the class attribute containing the class name 'p_cls2'
ele2 = ele1.ele('.:p_cls2')
```

If you still need a more complex matching method, please use the multiple attribute matching operator.

___

### 📌 Single attribute selector `@`

Represents a single attribute and matches only one attribute.

The `@` keyword has only one simple functionality, which is to match the content after `@` and not parse the string afterwards. Therefore, even if the following string also contains `@` or `@@`, it will be treated as content to be matched. So for multiple attribute matching, including all attributes including the first attribute, they must all start with `@@`.

Note:

If the attribute includes special characters (such as `@`), this method cannot match it correctly and needs to use the CSS selector method. Special characters need to be escaped with `\`.

```python
# Find the element with the name attribute equal to "row1"
ele2 = ele1.ele('@name=row1')

# Find the element with the name attribute containing the text "row"
ele2 = ele1.ele('@name:row')

# Find the element with the name attribute starting with "row"
ele2 = ele1.ele('@name^row')

# Find elements with a name attribute
ele2 = ele1.ele('@name')

# Find elements with no attributes
ele2 = ele1.ele('@')

# Find the element with the email attribute equal to "abc@def.com", even if there are multiple @, it will not be repeated
ele2 = ele1.ele('@email=abc@def.com')

# Example of attribute with special characters, match elements with the attribute abc@def equal to v
ele2 = ele1.ele('css:div[abc\@def="v"]')
```

___

### 📌 Multiple attribute and selector `@@`

Used when matching elements that meet multiple conditions simultaneously, each condition is preceded by `@@`.

Note:

-   When matching text or attributes with `@@`, `@|`, or `@!`, multiple attribute matching cannot be used. Xpath needs to be used instead.
-   If the attribute includes special characters (such as `@`), this method cannot match it correctly and needs to use the CSS selector method. Special characters need to be escaped with `\`.

```python
# Find elements with the name attribute equal to "row1" and the class attribute containing the text "cls"
ele2 = ele1.ele('@@name=row1@@class:cls')
```

`@@` can be used in combination with the `tag` introduced below:

```python
ele = page.ele('tag:div@@class=p_cls@@name=row1')
```

___

### 📌 Multiple attribute or selector `@|`

Used when matching elements that meet any of multiple conditions, each condition is preceded by `@|`.

The usage is the same as `@@`, and the precautions are the same as `@@`.

```python
# Find elements with the id attribute equal to "one" or the id attribute equal to "two"
ele2 = ele1.ele('@|id=one@|id=two')
```

`@|` can be used in combination with the `tag` introduced below:

```python
ele = page.ele('tag:div@|class=p_cls@|name=row1')
```

___

### 📌 Attribute negation selector `@!`

Used to negate a condition, can be used in conjunction with `@@` or `@|`, or used alone.

When used in combination with `@@` or `@|`, the relationship between `@@` or `@|` determines whether it is "and" or "or".

**Example:**

```python
# Match elements with arg1 equal to "abc" and arg2 not equal to "def"
page.ele('@@arg1=abc@!arg2=def')

# Match div elements with arg1 equal to "abc" or arg2 not equal to "def"
page.ele('t:div@|arg1=abc@!arg2=def')

# Match elements with arg1 not equal to "abc"
page.ele('@!arg1=abc')

# Match elements with no arg1 attribute
page.ele('@!arg1')
```

___

## 

### 📌 Text Matching Operator `text`

The text to be matched. If the query string does not start with any keywords, it indicates a fuzzy search based on the input text.  
If there are multiple direct text nodes within an element, when performing an exact search, it can match the concatenation of all text nodes into a string, and when performing a fuzzy search, it can match each text node individually.

When there are no matching operators specified, it defaults to matching text.

```python
# Find the element with text "第二行"
ele2 = ele1.ele('text=第二行')

# Find the element with text containing "第二"
ele2 = ele1.ele('text:第二')

# Equivalent to the previous line
ele2 = ele1.ele('第二')  
```

Tips

If the text to be searched contains `text:`, it can be written as follows, where the first `text:` is a keyword and the second one is the content to be searched:

```python
ele2 = page.ele('text:text:')
```

___

### 📌 Text Matching Operator `text()`

The text keyword used when searching for attributes, must be used with `@` or `@@`.

```python
# Find the element with text "第二行"
ele2 = ele1.ele('@text()=第二行')

# Find the element with text containing "第二行"
ele2 = ele1.ele('@text():二行')

# Find the element with text starting with "第二" and class attribute "p_cls"
ele2 = ele1.ele('@@text()^第二@@class=p_cls')

# Find the element with text "二行" and no attributes (because the first @@ is empty)
ele2 = ele1.ele('@@@@text():二行')

# Find the element with direct child text containing the string "二行"
ele = page.ele('@text():二行')
```

___

### 📌 Tips for `@@text()`

It is worth mentioning that `text()` combined with `@@` or `@|` can achieve a very convenient search method.

In web pages, elements and text are often interspersed, for example:

```python

<li class="explore-categories__item">
    <a href="/explore/new-tech" class="">
        <i class="explore"></i>
        前沿技术
    </a>
</li>
<li class="explore-categories__item">
    <a href="/explore/program-develop" class="">
        <i class="explore"></i>
        程序开发
    </a>
</li>
```

In the example above, to find the `<a>` element that contains the text `'前沿技术'`, you can write:

```python
ele = page.ele('text:前沿技术')
# Or
ele = page.ele('@text():前沿技术')
```

Both of these methods can find the element containing direct text content.

But if you want to find the `<li>` element using text, you can't find it because the text is not its direct content.

You can write it like this:

```python
ele = page.ele('tag:li@@text():前沿技术')
```

The difference between `@@text()` and `@text()` is that the former can search for all text within the element, not just direct text, so it can achieve some very flexible searches.

Note

When using `@@` or `@|`, do not use `text()` as the sole query condition, otherwise it will locate the highest-level element in the entire document.

❌ Incorrect usage:

```python
ele = page.ele('@@text():前沿技术')
ele = page.ele('@|text():前沿技术@|text():程序开发')
```

⭕ Correct usage:

```python
ele = page.ele('tag:li@|text():前沿技术@|text():程序开发')
```

___

### 📌 Tag Matching Operator `tag`

Indicates the tag of the element. It only takes effect when it is used at the beginning of the statement and used alone, and it can be used with `@`, `@@`, or `@|`. `tag:` has the same effect as `tag=`, there is no `tag^` and `tag$` syntax.

```python
# Locate the div element
ele2 = ele1.ele('tag:div')

# Locate the p element with class attribute "p_cls"
ele2 = ele1.ele('tag:p@class=p_cls')

# Locate the p element with text "第二行"
ele2 = ele1.ele('tag:p@text()=第二行')

# Locate the p element with class attribute "p_cls" and text "第二行"
ele2 = ele1.ele('tag:p@@class=p_cls@@text()=第二行')

# Locate the p element with class attribute "p_cls" or text "第二行"
ele2 = ele1.ele('tag:p@|class=p_cls@|text()=第二行')

## 翻译 private_upload\default_user\2024-01-24-19-46-31\get_elements_基本用法_DrissionPage.md.part-3.md

# Find p elements containing the string "二行" in direct text nodes
ele2 = ele1.ele('tag:p@text():二行')

# Find p elements containing the string "二行" in internal text nodes
ele2 = ele1.ele('tag:p@@text():二行')
```
Note

There is a difference between `tag:div@text():text` and `tag:div@@text():text`. The former only searches in the direct text nodes of the `div` element, while the latter searches in the entire internal content of the `div` element.

---

### 📌 css selector matching symbol `css`

Represents finding elements using css selector. `css:` and `css=` have the same effect, and there is no syntax like `css^` and `css$`.

```python
# Find div elements
ele2 = ele1.ele('css:.div')

# Find div child elements, this syntax is unique to this library and not natively supported
ele2 = ele1.ele('css:>div')
```

---

### 📌 xpath matching symbol `xpath`

Represents finding elements using xpath. `xpath:` and `xpath=` have the same effect, and there is no syntax like `xpath^` and `xpath$`.

Additionally, the `ele()` method of the element object supports the complete xpath syntax, such as being able to directly retrieve the attributes (as strings) of elements using xpath.

```python
# Find the first div element in descendants
ele2 = ele1.ele('xpath:.//div')

# Same as the previous line, when finding descendants of an element, the `.` in front of `//` can be omitted
ele2 = ele1.ele('xpath://div')

# Use xpath to retrieve the class attribute of a div element (this functionality is not available in the page source)
ele_class_str = ele1.ele('xpath://div/@class')
```

Tips

When finding descendants of an element, the selenium native code requires a `.` to be added in front of xpath; otherwise, it will search throughout the entire page. The author considers this design to be unnecessary, as we should only search for elements within the element that has already been found. Therefore, when using xpath to find elements under an element, the `.` in front of `//` or `/` can be omitted.

---

### 📌 selenium loc tuple

The find methods can directly accept the native selenium locators for locating elements, making it easier for project migration.

```python
from DrissionPage.common import By

# Find the element with id "one"
loc1 = (By.ID, 'one')
ele = page.ele(loc1)

# Find using xpath
loc2 = (By.XPATH, '//p[@class="p_cls"]')
ele = page.ele(loc2)
```

---

## ✅️️ Relative positioning

The following methods allow you to obtain direct child nodes, sibling nodes, ancestor elements, and adjacent nodes in the DOM based on a specific element.

Tips

Here, we are referring to "nodes" and not just "elements," as relative positioning can retrieve nodes other than elements, including text and comment nodes.

Note

If the element is within an `<iframe>`, the relative positioning cannot go beyond the `<iframe>` document.

### 📌 Get parent element

🔸 `parent()`

This method retrieves a certain level of parent element of the current element, either by specifying a filter or a level.

|  Parameter Name  |               Type                | Default Value | Description                                             |
| :--------------: | :------------------------------: | :-----------: | ------------------------------------------------------- |
| `level_or_loc`   | `int` `str` `Tuple[str, str]`    |     `1`       | Level of the parent element, starting from `1`, or use a locator to filter in the ancestor elements |
|     `index`      |              `int`               |     `1`       | When `level_or_loc` is a locator, use this parameter to select which result to choose, counting from the current element upwards. This parameter is not valid when `level_or_loc` is a number. |

| Return Type | Description |
| --- | --- |
| `SessionElement` | The found element object |
| `NoneElement` | Returns `NoneElement` when no result is obtained |

**Example:**

```python
# Get the second level parent element of ele1
ele2 = ele1.parent(2)

# Get the element with id "id1" in the parent element of ele1
ele2 = ele1.parent('#id1')
```

---

### 📌 Get direct child nodes

🔸 `child()`

This method returns a direct child node of the current element, with the option to specify a filter and the index of the result.

|   Parameter Name   |              Type               | Default Value | Description                                               |
| :----------------: | :----------------------------: | :-----------: | --------------------------------------------------------- |
|  `filter_loc`      | `str` `Tuple[str, str]` `int`  |     `''`      | Query syntax used to filter nodes, when it is of type `int`, the `index` parameter is ignored |
|     `index`        |              `int`             |     `1`       | Which result to retrieve from the query results, starting from `1`. A negative number can be inputted to count from the end |
|    `timeout`       |             `float`            |    `None`     | No actual effect                                          |
|   `ele_only`       |             `bool`             |    `True`     | Whether to only find elements. When set to `False`, it includes text and comment nodes in the search range |

| Return Type | Description |
| --- | --- |
| `SessionElement` | The found element object |
| `str` | Returns a string when a non-element node is obtained |
| `NoneElement` | Returns `NoneElement` when no result is obtained |

## 

🔸 `children()`

This method returns a list of all the direct child nodes of the current element that meet the specified conditions. Query syntax can be used for filtering.

|   Parameter   |         Type          | Default | Description                                               |
| :-----------: | :------------------: | :-----: | --------------------------------------------------------- |
| `filter_loc`  | `str` `Tuple[str, str]` |  `''`   | Query syntax used for filtering the nodes                 |
|   `timeout`   |        `float`       | `None`  | Not applicable                                            |
|  `ele_only`   |       `bool`        |  `True` | If `False`, the search includes text and comment nodes     |

| Return Type | Description                                            |
| ----------- | ------------------------------------------------------ |
| `List[SessionElement, str]` | List of results                                         |

___

### 📌 Get the Next Sibling Node

🔸 `next()`

This method returns a specific sibling node after the current element, based on the specified conditions and index.

|   Parameter   |           Type           | Default | Description                                               |
| :-----------: | :----------------------: | :-----: | --------------------------------------------------------- |
| `filter_loc`  | `str` `Tuple[str, str]` `int` |  `''`   | Query syntax used for filtering the nodes. If `int` type is used, the `index` parameter is ignored |
|   `index`     |           `int`          |   `1`   | Index of the query result, starting from `1`. Negative numbers can be used to indicate reverse indexing |
|  `timeout`    |         `float`          | `None`  | Not applicable                                            |
|  `ele_only`   |          `bool`          |  `True` | If `False`, the search includes text and comment nodes     |

| Return Type | Description                                            |
| ----------- | ------------------------------------------------------ |
| `SessionElement` | Found element object                                  |
| `str` | Returns a string when a non-element node is obtained    |
| `NoneElement` | Returns `NoneElement` when no result is obtained        |

**Example:**

```python
# Get the first sibling element after ele1
ele2 = ele1.next()

# Get the third sibling element after ele1
ele2 = ele1.next(3)

# Get the third sibling div element after ele1
ele2 = ele1.next('tag:div', 3)

# Get the text of the first text node after ele1
txt = ele1.next('xpath:text()', 1)
```

___

🔸 `nexts()`

This method returns a list of all the sibling nodes after the current element that meet the specified conditions. Query syntax can be used for filtering.

|   Parameter   |         Type          | Default | Description                                               |
| :-----------: | :------------------: | :-----: | --------------------------------------------------------- |
| `filter_loc`  | `str` `Tuple[str, str]` |  `''`   | Query syntax used for filtering the nodes                 |
|   `timeout`   |        `float`       | `None`  | Not applicable                                            |
|  `ele_only`   |       `bool`        |  `True` | If `False`, the search includes text and comment nodes     |

| Return Type | Description                                            |
| ----------- | ------------------------------------------------------ |
| `List[SessionElement, str]` | List of results                                         |

**Example:**

```python
# Get all the sibling elements after ele1
eles = ele1.nexts()

# Get all the sibling div elements after ele1
divs = ele1.nexts('tag:div')

# Get all the text nodes after ele1
txts = ele1.nexts('xpath:text()')
```

___

### 📌 Get the Previous Sibling Node

🔸 `prev()`

This method returns a specific sibling node before the current element, based on the specified conditions and index.

|   Parameter   |           Type           | Default | Description                                               |
| :-----------: | :----------------------: | :-----: | --------------------------------------------------------- |
| `filter_loc`  | `str` `Tuple[str, str]` `int` |  `''`   | Query syntax used for filtering the nodes. If `int` type is used, the `index` parameter is ignored |
|   `index`     |           `int`          |   `1`   | Index of the query result, starting from `1`. Negative numbers can be used to indicate reverse indexing |
|  `timeout`    |         `float`          | `None`  | Not applicable                                            |
|  `ele_only`   |          `bool`          |  `True` | If `False`, the search includes text and comment nodes     |

| Return Type | Description                                            |
| ----------- | ------------------------------------------------------ |
| `SessionElement` | Found element object                                  |
| `str` | Returns a string when a non-element node is obtained    |
| `NoneElement` | Returns `NoneElement` when no result is obtained        |

**Example:**

```python
# Get the first sibling element before ele1
ele2 = ele1.prev()

# Get the third sibling element before ele1
ele2 = ele1.prev(3)

# Get the third sibling div element before ele1
ele2 = ele1.prev(3, 'tag:div')

# Get the text of the first text node before ele1
txt = ele1.prev(1, 'xpath:text()')
```

___

🔸 `prevs()`

This method returns a list of all the sibling nodes before the current element that meet the specified conditions. Query syntax can be used for filtering.

## 

| Parameter Name |        Type        | Default Value | Description                                           |
| :------------: | :----------------: | :-----------: | ----------------------------------------------------- |
|  `filter_loc`  | `str` `Tuple[str, str]` |     `''`    | Query syntax used for filtering nodes                  |
|   `timeout`    |      `float`       |    `None`     | No actual effect                                       |
|  `ele_only`    |       `bool`       |    `True`     | Whether to search for elements only, including text and comment nodes when set to `False` |

|  Return Type  | Description |
| :-----------: | ----------- |
| `List[SessionElement, str]` | List of results |

**Example:**

```python
# Get all preceding sibling elements of ele1
eles = ele1.prevs()

# Get all preceding sibling div elements of ele1
divs = ele1.prevs('tag:div')
```

___

### 📌 Find Nodes in Subsequent Document

🔸 `after()`

This method returns a certain node after the current element, with the option to specify filter conditions and the position of the node. The search scope is not limited to sibling nodes, but the entire DOM document.

| Parameter Name |      Type       | Default Value | Description                                                                                             |
| :------------: | :-------------: | :-----------: | ------------------------------------------------------------------------------------------------------- |
|  `filter_loc`  | `str` `Tuple[str, str]` `int` |     `''`    | Query syntax used for filtering nodes. `index` parameter is invalid when `filter_loc` is of type `int`. |
|    `index`     |      `int`      |      `1`      | The position of the queried result. Starts from `1`, negative numbers can be used to indicate the end. |
|   `timeout`    |     `float`     |    `None`    | No actual effect                                                                                         |
|  `ele_only`    |      `bool`     |    `True`     | Whether to search for elements only, including text and comment nodes when set to `False` |

|  Return Type   | Description           |
| :------------: | --------------------- |
| `SessionElement` | Found element object  |
|      `str`     | Returns a string when a non-element node is fetched |
| `NoneElement`  | Returns `NoneElement` when no result is obtained |

**Example:**

```python
# Get the second element after ele1
ele2 = ele1.after(index=2)

# Get the third div element after ele1
ele2 = ele1.after('tag:div', 3)

# Get the text of the first text node after ele1
txt = ele1.after('xpath:text()', 1)
```

___

🔸 `afters()`

This method returns a list of all nodes that meet the conditions after the current element. Query syntax can be used for filtering. The search scope is not limited to sibling nodes, but the entire DOM document.

| Parameter Name |     Type      | Default Value | Description               |
| :------------: | :-----------: | :-----------: | ------------------------- |
|  `filter_loc`  | `str` `Tuple[str, str]` |     `''`    | Query syntax used for filtering nodes |
|   `timeout`    |    `float`    |    `None`     | No actual effect           |
|  `ele_only`    |     `bool`    |    `True`     | Whether to search for elements only, including text and comment nodes when set to `False` |

|  Return Type   | Description |
| :------------: | ----------- |
| `List[SessionElement, str]` | List of results |

**Example:**

```python
# Get all elements after ele1
eles = ele1.afters()

# Get all div elements after ele1
divs = ele1.afters('tag:div')
```

___

### 📌 Find Nodes in Previous Document

🔸 `before()`

This method returns a certain node before the current element, with the option to specify filter conditions and the position of the node. The search scope is not limited to sibling nodes, but the entire DOM document.

| Parameter Name |      Type       | Default Value | Description                                                                                            |
| :------------: | :-------------: | :-----------: | ------------------------------------------------------------------------------------------------------ |
|  `filter_loc`  | `str` `Tuple[str, str]` `int` |     `''`    | Query syntax used for filtering nodes. `index` parameter is invalid when `filter_loc` is of type `int`. |
|    `index`     |      `int`      |      `1`      | The position of the queried result. Starts from `1`, negative numbers can be used to indicate the end. |
|   `timeout`    |     `float`     |    `None`    | No actual effect                                                                                        |
|  `ele_only`    |      `bool`     |    `True`     | Whether to search for elements only, including text and comment nodes when set to `False` |

|  Return Type   | Description           |
| :------------: | --------------------- |
| `SessionElement` | Found element object  |
|      `str`     | Returns a string when a non-element node is fetched |
| `NoneElement`  | Returns `NoneElement` when no result is obtained |

**Example:**

```python
# Get the second element before ele1
ele2 = ele1.before(index=2)

# Get the third div element before ele1
ele2 = ele1.before('tag:div', 3)

# Get the text of the first text node before ele1
txt = ele1.before('xpath:text()', 1)
```

___

🔸 `befores()`

This method returns a list of all nodes that meet the conditions before the current element. Query syntax can be used for filtering. The search scope is not limited to sibling nodes, but the entire DOM document.

## 

| Parameter Name |      Type      | Default Value | Description                         |
| :------------: | :------------: | :-----------: | ----------------------------------- |
| `filter_loc`   | `str` `Tuple[str, str]` |     `''`      | Query syntax used for filtering nodes |
|   `timeout`    |     `float`    |    `None`     | No actual effect                     |
|   `ele_only`   |     `bool`     |    `True`     | Whether to search only for elements. When set to `False`, text and comment nodes are also included in the search range |

| Return Type                   | Description   |
| ---------------------------- | ------------- |
| `List[SessionElement, str]`  | List of results |

**Example:**

```python
# Get all elements before ele1
eles = ele1.befores()

# Get all div elements before ele1
divs = ele1.befores('tag:div')
```

