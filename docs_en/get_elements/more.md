🔦 More Usages
---

This section introduces the ways to access element objects in a browser page.

The methods for obtaining element objects using `SessionPage` are the same as those for obtaining element objects using `SessionPage`, but there are more features in this section that will be introduced.

## ✅️️ Finding Elements in Static Mode

Static elements refer to the `SessionElement` element objects in the s mode, which are made up of pure text, so they can handle tasks very quickly.  
For complex web pages, when collecting data from hundreds or thousands of elements, converting them into static elements can significantly improve the speed by several orders of magnitude.  
The author once used the same logic to convert elements into static elements only, which accelerated a web page that took 30 seconds to complete to complete in a few seconds.  
We can even convert the entire web page into static elements and then extract information from it.  
Of course, these elements cannot be interacted with, such as clicking.  
You can use the `s_ele()` method to convert the found dynamic elements into static elements, or to get a static copy of an element or the page itself.

### 📌 `s_ele()`

Both the page object and element object have this method, which is used to find the first matching element and get its static version.

The `s_ele()` method has slightly different parameter names for page objects and element objects, but the usage is the same.

|     Parameter Name    |                             Type                             | Default Value | Description                                                                                                                                                       |
|:------------------------:|:--------------------------------------------------------:|:-----------------:|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `locator` (for element object) |            `str`<br/>`Tuple[str, str]`             |     required       | The locator information of the element, can be a query string or `loc` tuple.                                                                                          |
| `locator` (for page object)    | `str`<br/>`ChromiumElement`<br/>`Tuple[str, str]` |     required       | The locator information of the element, can be a query string, `loc` tuple, or a `ChromiumElement` object. |

|  Return Type  |                                    Description                                    |
|:----------------:|----------------------------------------------------------------------------------------|
| `SessionElement` |   Returns the static version of the first element object that meets the conditions.   |
|  `NoneElement`  |   Returns the `NoneElement` object if no element that meets the conditions is found within the specified time limit. |

:::warning Note
    The `s_ele()` method of a page object or element object cannot search for elements within an `<iframe>`, and the static version of a page object cannot search for elements within an `<iframe>` either.
    To use the static version of an element within an `<iframe>`, you can first obtain the element and then convert it into a static version. However, if you use the `ChromiumFrame` object, you can directly use `s_ele()` to find elements in it, which will be explained in later chapters.
:::

:::tip Tips
    The `SessionElement` version obtained from a `ChromiumElement` element can still use relative positioning methods to locate ancestor or sibling elements.
:::

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()

# Find an element in the page and get its static version
ele1 = page.s_ele('search text')

# Find an element in a dynamic element and get its static version
ele = page.ele('search text')
ele2 = ele.s_ele()

# Get the static copy of a page element (no parameter passed in)
s_page = page.s_ele()

# Get the static copy of a dynamic element
s_ele = ele.s_ele()

# Search for descendant elements in the static copy (since it is already a static element, the result of using ele() to find elements is also static)
ele3 = s_page.ele('search text')
ele4 = s_ele.ele('search text')
```

---

### 📌 `s_eles()`

This method is similar to `s_ele()`, but it returns a list of all matching elements or a list of attribute values.

|  Parameter Name   |             Type             | Default Value | Description                             |
|:---------------------:|:--------------------------:|----------------:|------------------------------------------|
| `locator` | `str`<br/>`Tuple[str, str]` |   required       | The locator information of the element, can be a query string or `loc` tuple. |

|     Return Type      |                               Description                                |
|:------------------------:|----------------------------------------------------------------------------------|
| `List[SessionElement]` |   Returns a list of `SessionElement` versions of all found elements.  |

**Example:**

```python
from DrissionPage import WebPage

page = WebPage()
for ele in page.s_eles('search text'):
    print(ele.text)
```

---

## ✅️ Accessing the Currently Focused Element

Use the `active_ele` attribute to get the currently focused element on the page.

```python
ele = page.active_ele
```

---

## ✅️️ `<iframe>` Elements

### 📌 Finding `<iframe>` Elements

`<iframe>` and `<frame>` elements can also be found using `ele()`, and the generated objects are `ChromiumFrame` objects instead of `ChromiumElement` objects.

However, it is not recommended to use `ele()` to get `<iframe>` elements, because the IDE cannot correctly prompt subsequent operations.

It is recommended to use the `get_frame()` method of the Page object.

The usage is the same as `ele()`, you can use locators to search for the elements. It also adds the ability to locate elements using index, id, and name attributes.

**Example:**

```python
iframe = page.get_frame(1)  # Get the first iframe element on the page
iframe = page.get_frame('#theFrame')  # Get the iframe element object with the id "theFrame"
```

---

### 📌 Finding Elements in a Different Level under the Page



Unlike selenium, this library can directly search for elements within a same-origin `<iframe>`.
And regardless of the hierarchy, it can directly access elements within multiple layers of `<iframe>`. This greatly simplifies the program logic and makes it more convenient to use.

Assuming there is a two-level `<iframe>` in the page, and there is an element `<div id='abc'></div>`, it can be retrieved in the following way:

```python
page = ChromiumPage()
ele = page('#abc')
```

There is no need to switch in and out before and after retrieval, and it does not affect the retrieval of other elements on the page.

If using selenium, it needs to be written like this:

```python
driver = webdriver.Chrome()
driver.switch_to.frame(0)
driver.switch_to.frame(0)
ele = driver.find_element(By.ID, 'abc')
driver.switch_to.default_content()
```

Obviously, it is more cumbersome, and it is not possible to operate on elements outside the `<iframe>` after switching into the `<iframe>`.

:::warning Attention
    - Cross-level search is only supported by the page object, the element object cannot directly search for elements inside the iframe.
    - Cross-level search can only be used for `<iframe>` with the same domain as the main frame, for different domains, please use the following method.
:::

---

### 📌 Searching within an iframe element

This library treats `<iframe>` as a special element/page object, which allows the simultaneous operation of multiple `<iframe>` without the need to switch back and forth.

For `<iframe>` with a different domain name, we cannot directly search for elements inside it through the page, but we can first get the `<iframe>` element, and then search within it. Of course, this operation can also be done for non-cross-domain `<iframe>` elements.

Assuming the id of an `<iframe>` is `'iframe1'`, and we want to find an element with an id of `'abc'` within it:

```python
page = ChromiumPage()
iframe = page('#iframe1')
ele = iframe('#abc')
```

This `<iframe>` element is a page object, so it can continue to search for elements across `<iframe>` (relative to this `<iframe>` without cross-domain).

---

## ✅️️ `ShadowRoot`

This library treats shadow-root as an element object, referred to as the `ShadowRoot` object.
This object can search for sub-elements and perform relative positioning within the DOM, just like ordinary elements.
When positioning relative to a `ShadowRoot` object, it is regarded as the first object within its parent object, and the rest of the positioning logic is the same as ordinary objects.

The `ShadowRoot` object can be obtained using the `shadow_root` property of the element object.

:::warning Attention
    - If there are other `ShadowRoot` elements among the sub-elements of the `ShadowRoot` element, these sub-`ShadowRoot` elements cannot be directly located using positioning statements. Only the parent element can be located first, and then the `shadow_root` property can be used to locate them.
:::

```python
# Get a shadow-root element
sr_ele = page.ele('#app').shadow_root

# Find sub-elements under this element
ele1 = sr_ele.ele('tag:div')

# Get other elements through relative positioning
ele1 = sr_ele.parent(2)
ele1 = sr_ele.next('tag:div', 1)
ele1 = sr_ele.after('tag:div', 1)
eles = sr_ele.nexts('tag:div')

# Locate shadow-root elements in sub-elements
sr_ele2 = sr_ele.ele('tag:div').shadow_root
```

Since shadow-root cannot perform cross-level search, chained operations are very common. Therefore, a shorthand notation `sr` is designed, which has the same function as `shadow_root`, both of which are used to obtain the `ShadowRoot` within an element.

**Example of chained operations for multiple levels of shadow-root:**

The following code prints the first page of the browser history, which is obtained through multiple levels of shadow-root.

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('chrome://history/')

items = page('#history-app').sr('#history').sr.eles('t:history-item')
for i in items:
    print(i.sr('#item-container').text.replace('\n', ''))
```

---

## ✅️️ Waiting

Due to factors such as network and the uncertainty of JS execution time, it is often necessary to wait for elements to be loaded into the DOM before they can be used.

All element search operations in the browser have built-in waiting functionality. The waiting time defaults to the `timeout` attribute of the page where the element is located (default is 10 seconds), and can also be set separately each time the search is performed. The waiting time set separately does not change the original setting of the page.

```python
from DrissionPage import ChromiumPage

# Set the timeout for searching elements to 15 seconds when initializing the page
page = ChromiumPage(timeout=15)
# Set the timeout for searching elements to 5 seconds
page.set.timeouts(5)

# Use the page timeout to search for elements (5 seconds)
ele1 = page.ele('search text')
# Set an independent waiting time for this search (1 second)
ele1 = page.ele('search text', timeout=1)
# Search for descendant elements, using the page timeout (5 seconds)
ele2 = ele1.ele('search text')
# Search for descendant elements, using the separately set timeout (1 second)
ele2 = ele1.ele('some text', timeout=1)  
```

