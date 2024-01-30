🔦 Overview
---

This chapter introduces how to get element objects.

Positioning elements is a critical skill in automation. Although you can directly copy the absolute path in the developer tools, there are several drawbacks to doing so:

- The code is lengthy and not readable.
- Dynamic pages can cause elements to become invalid.
- Relative positioning cannot be used.
- If there are any changes to the web page or temporary elements appear, the code becomes less error-tolerant.
- It is not possible to search for elements across `<iframe>`.

Therefore, the author strongly recommends against using the right-click copy element path.

This library provides a set of concise and easy-to-use syntax for quickly locating elements, with built-in waiting functionality and support for chained searches, reducing code complexity.

It also supports css selectors, xpath, and the loc tuple native to Selenium.

There are roughly three methods for locating elements:

- Finding child elements within a page or element
- Relative positioning based on DOM structure
- Relative positioning based on page layout

## ✅️️ Usage

All page objects and element objects can search for elements within themselves, with element objects also able to locate other elements relative to themselves.

Page objects include: `SessionPage`, `ChromiumPage`, `ChromiumTab`, `ChromiumFrame`, `WebPage`, `WebPageTab`

Element objects include: `SessionElement`, `ChromiumElement`, `ShadowRoot`

### 📌 Searching within a page

Use the `ele()` and `eles()` methods of page objects to retrieve specified element objects within a page.

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('https://www.baidu.com')
ele = page.ele('#su')
```

---

### 📌 Searching within an element

Use the `ele()`, `eles()`, `child()`, and `children()` methods of element objects to retrieve specified descendant element objects within an element.

```python
ele1 = page.ele('#s_fm')
ele2 = ele1.ele('#su')

son = ele1.child('tag:div')  # Get the first direct child div element
sons = ele1.children('tag:div')  # Get all direct child div elements
```

---

### 📌 Chained searching

Because objects themselves can search for objects, chained operations are supported, and the above examples can be merged as follows:

```python
ele = page.ele('#s_fm').ele('#su')
```

---

### 📌 Relative searching

Element objects can execute relative searches based on themselves.

```python
ele = page.ele('#su')

parent = ele.parent(2)  # Get the second level parent element of the ele element
brother = ele.next('tag:a')  # Get the first a element after the ele element
after = ele.after('tag:div')  # Get the first div element in the document after the ele element
```

---

### 📌 shadow root

Use the `shadow_root` attribute of browser element objects to retrieve the `ShadowRoot` object under that element.

```python
shadow = page.ele('#ele1').shadow_root
```

Searching within a shadow root element follows the same methods as a regular element.

```python
shadow = page.ele('#ele1').shadow_root
ele = shadow.ele('#ele2')
```

---

## ✅️️ Examples

First, let's look at some examples. The usage will be explained in detail later.

### 📌 Simple examples

Suppose we have a page like this, which will be used for the examples in this chapter:

```html
<html>
<body>
<div id="one">
    <p class="p_cls" name="row1">First line</p>
    <p class="p_cls" name="row2">Second line</p>
    <p class="p_cls">Third line</p>
</div>
<div id="two">
    Second div
</div>
</body>
</html>
```

We can use the page object to retrieve elements from it:

```python
# Get the element with id one
div1 = page.ele('#one')

# Get the element with name attribute row1
p1 = page.ele('@name=row1')

# Get the element that contains the text "Second div"
div2 = page.ele('Second div')

# Get all div elements
div_list = page.eles('tag:div')
```

We can also retrieve an element and search for elements within it or around it:

```python
# Retrieve an element div1
div1 = page.ele('#one')

# Search for all p elements within div1
p_list = div1.eles('tag:p')

# Get the next element after div1
div2 = div1.next()
```

---

### 📌 Practical examples

Copy this code and run it directly to see the results.

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('https://gitee.com/explore')

# Get the ul element that contains the text "Recommended Projects"
ul_ele = page.ele('tag:ul@@text():Recommended Projects')  

# Get all a elements under this ul element
titles = ul_ele.eles('tag:a')  

# Iterate over the list and print the text of each a element
for i in titles:  
    print(i.text)
```

**Output:**

```shell
Recommended Projects
Cutting-edge Technologies
Smart Hardware
IOT/Internet of Things/Edge Computing
In-car Applications
...
```

