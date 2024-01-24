🚤 Automatic Waiting
---

In unstable network environments, it is difficult to determine the execution time of JavaScript on a webpage. When automating processes, it is often necessary to wait for certain conditions to be met.

Using `sleep()` all the time is not elegant and can waste time. Not waiting enough can lead to errors.

Therefore, it is important for a program to be able to wait smartly. `DrissionPage` provides built-in waiting methods that can improve program stability and efficiency.

These methods are accessible through the `wait` attribute of the page and element objects.

All waiting methods have a `timeout` parameter that can be set to a specific timeout duration. The parameter can also be set to determine whether the method should return `False` or raise an exception upon timeout.

## ✅️️ Waiting Methods for Page Objects

**Example:**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('http://g1879.gitee.io/drissionpagedocs/')
page.wait.ele_displayed('tag:div')
```

### 📌 `wait.load_start()`

This method is used to wait for the page to enter the loading state.

Often, we navigate to another webpage by clicking an element and immediately want to access elements on the new page. However, if the previous page contains elements with the same locators as the elements on the new page, we may inadvertently access elements that become invalid after the navigation. By using this method, the program will be blocked, and execution will be delayed until the page starts loading, avoiding the aforementioned issue.

Usually, we only need to wait for the page to start loading, and the program will automatically wait for the loading to finish.

| Parameter | Type                | Default | Description                                                                                         |
|:---------:|:-------------------:|:-------:| --------------------------------------------------------------------------------------------------- |
| `timeout` | `float`<br/>`None`<br/>`True` | `None`   | The timeout duration. If `None` or `True`, the page's `timeout` setting will be used.<br/>If it's a number, the program will wait for the specified duration. |
| `raise_err` | `bool`          | `None`   | Determines whether an error should be raised upon timeout. If `None`, the behavior is determined by `Settings`.               |

| Return Type | Description                                                                      |
|:-----------:| -------------------------------------------------------------------------------- |
| `bool`      | Whether entering the loading state was completed when the waiting ended. |

**Example:**

```python
ele.click()  # Click a certain element
page.wait.load_start()  # Wait for the page to start loading
# Perform actions on the new page
print(page.title)
```

---

### 📌 `wait.doc_loaded()`

This method is used to wait for the page document to finish loading.

In general, developers don't need to use this method explicitly, as most actions in the program will automatically wait for the document to finish loading before execution.

:::warning Note
    - This feature is only used to wait for the main document of the page to load and cannot be used to wait for changes loaded by JavaScript.
    - The `get()` method already contains this functionality, so it is unnecessary to append this wait afterwards.
:::

| Parameter | Type                | Default | Description                                                                                         |
|:---------:|:-------------------:|:-------:| --------------------------------------------------------------------------------------------------- |
| `timeout` | `float`<br/>`None`<br/>`True` | `None`   | The timeout duration. If `None` or `True`, the page's `timeout` setting will be used.<br/>If it's a number, the program will wait for the specified duration. |
| `raise_err` | `bool`          | `None`   | Determines whether an error should be raised upon timeout. If `None`, the behavior is determined by `Settings`.               |

| Return Type | Description                                                                                      |
|:-----------:| ----------------------------------------------------------------------------------------------- |
| `bool`      | Whether the loading was completed when the waiting ended. |

---

### 📌 `wait.ele_loaded()`

This method is used to wait for an element to be loaded in the DOM.

Sometimes, the appearance of an element is a prerequisite for the next step of an action. Using this method can prevent inadvertent actions caused by some elements loading slower than the program executes.

| Parameter    | Type                                         | Default | Description                                                |
|:------------:|:--------------------------------------------:|:-------:| ---------------------------------------------------------- |
| `locator`    | `str`<br/>`Tuple[str, str]`                   | Required| The element to wait for, specified by locator.              |
| `timeout`    | `float`                                      | `None`  | The timeout duration. If `None`, the page's `timeout` setting will be used. |
| `raise_err`  | `bool`         | `None`    | Determines whether an error should be raised upon timeout. If `None`, the behavior is determined by `Settings`.          |

| Return Type        | Description                                                |
|:------------------:| ---------------------------------------------------------- |
| `ChromiumElement`  | The element object if waiting is successful.               |
| `False`            | If waiting fails.                                          |

**Example:**

```python
ele1.click()  # Click a certain element
page.wait.ele_loaded('#div1')  # Wait for the element with id 'div1' to load
ele2.click()  # Proceed with the next step after the 'div1' element has finished loading
```

---

### 📌 `wait.ele_displayed()`

This method is used to wait for an element to become displayed. If the specified element cannot be found in the DOM, it will automatically wait for the element to be loaded and displayed.

An element is considered hidden when it is present in the DOM but in a hidden state (even if it's within the viewport and not obscured). If a parent element is hidden, its child elements will also be considered hidden.

| Parameter         | Type                                                      | Default | Description                                                |
|:-----------------:|:---------------------------------------------------------:|:-------:| ---------------------------------------------------------|
| `loc_or_ele`      | `str`<br/>`Tuple[str, str]`<br/>`ChromiumElement`          |Required | The element to wait for. It can be an element or a locator. |
| `timeout`         | `float`                                                   | `None`  | The timeout duration. If `None`, the page's `timeout` setting will be used. |
| `raise_err`  | `bool`         | `None`    | Determines whether an error should be raised upon timeout. If `None`, the behavior is determined by `Settings`.          |

| Return Type | Description     |
|:-----------:|-----------------|
| `bool`      | Whether to wait successfully |

**Example：**

```python
# Wait for the element with id "div1" to be displayed, using the page settings for timeout
page.wait.ele_displayed('#div1')

# Wait for the element with id "div1" to be displayed, set timeout to 3 seconds
page.wait.ele_displayed('#div1', timeout=3)

# Wait for the already obtained element to be displayed
ele = page.ele('#div1')
page.wait.ele_displayed(ele)
```

---

### 📌 `wait.ele_hidden()`

This method is used to wait for an element to become hidden. If the specified element cannot be found in the current DOM, it will automatically wait for the element to be loaded and then wait for it to be hidden.

Element hiding means that the element is in the DOM but in a hidden state (even if it is in the viewport and not occluded). Child elements are also hidden when the parent element is hidden.

| Parameter    | Type                                              | Default | Description                  |
|:------------:|:-------------------------------------------------:|:-------:|------------------------------|
| `loc_or_ele` | `str`<br/>`Tuple[str, str]`<br/>`ChromiumElement` | Required | The element to wait for, can be an element or a locator |
| `timeout`    | `float`                                           | `None`  | Timeout, if `None`, use the page `timeout` setting |
| `raise_err`  | `bool`                                            | `None`  | Whether to raise an error when waiting fails, if `None`, based on the `Settings` |

| Return Type | Description     |
|:-----------:|-----------------|
| `bool`      | Whether to wait successfully |

---

### 📌 `wait.ele_deleted()`

This method is used to wait for an element to be deleted from the DOM.

| Parameter    | Type                                              | Default | Description                  |
|:------------:|:-------------------------------------------------:|:-------:|------------------------------|
| `loc_or_ele` | `str`<br/>`Tuple[str, str]`<br/>`ChromiumElement` | Required | The element to wait for, can be an element or a locator |
| `timeout`    | `float`                                           | `None`  | Timeout, if `None`, use the page `timeout` setting |
| `raise_err`  | `bool`                                            | `None`  | Whether to raise an error when waiting fails, if `None`, based on the `Settings` |

| Return Type | Description     |
|:-----------:|-----------------|
| `bool`      | Whether to wait successfully |

---

### 📌 `wait.download_begin()`

This method is used to wait for the start of a download, see the download section for details.

| Parameter | Type    | Default | Description                                          |
|:---------:|---------|---------|------------------------------------------------------|
| `timeout` | `float` | `None`  | Timeout, if `None`, use the page `timeout` setting |
| `raise_err`  | `bool`                                            | `None`  | Whether to raise an error when waiting fails, if `None`, based on the `Settings` |

| Return Type | Description     |
|:-----------:|-----------------|
| `bool`      | Whether to wait successfully |

**Example：**

```python
page('#download_btn').click()  # Click the button to trigger the download
page.wait.download_begin()  # Wait for the download to start
```

---

### 📌 `wait.upload_paths_inputted()`

This method is used to wait for automatically filling in the file upload path. See the file upload section for details.

**Parameters:** None

**Returns:** `None`

**Example：**

```python
# Set the file path to be uploaded
page.set.upload_files('demo.txt')
# Click the button to trigger the file selection dialog
btn_ele.click()
# Wait for the path to be filled in
page.wait.upload_paths_inputted()
```

---

### 📌 `wait.new_tab()`

This method is used to wait for a new tab to appear.

| Parameter | Type    | Default | Description                                          |
|:---------:|---------|---------|------------------------------------------------------|
| `timeout` | `float` | `None`  | Timeout, if `None`, use the page `timeout` setting |
| `raise_err`  | `bool`                                            | `None`  | Whether to raise an error when waiting fails, if `None`, based on the `Settings` |

| Return Type | Description                     |
|:-----------:|---------------------------------|
| `str`       | The id of the new tab being waited for |
| `False`     | `False` if waiting fails       |

---

### 📌 `wait.title_change()`

This method is used to wait for the title to contain or not contain the specified text.

| Parameter   | Type    | Default | Description                                                  |
|:------------:|---------|---------|--------------------------------------------------------------|
| `text`     | `str`   | Required| The text used for identification                              |
| `exclude`  | `bool`  | `False` | Whether to exclude, if `True`, `True` is returned when the title does not contain the specified `text` |
| `timeout`  | `bool`  | `float` | Timeout                                                      |
| `raise_err` | `bool`  | `None`  | Whether to raise an error when waiting fails, if `None`, based on the `Settings` |

| Return Type | Description     |
|:-----------:|-----------------|
| `bool`      | Whether to wait successfully |

---

### 📌 `wait.url_change()`

This method is used to wait for the url to contain or not contain the specified text.

For example, some websites will undergo multiple redirections during login, and the url will change multiple times. This function can be used to wait for the final page needed.

| Parameter Name | Type    | Default Value | Description                                                                                |
| -------------- | ------- | ------------- | ------------------------------------------------------------------------------------------ |
| `text`         | `str`   | Required -   | Text for identification                                                                     |
| `exclude`      | `bool`  | `False`       | When `True`, returns `True` if the URL does not contain the specified `text`               |
| `timeout`      | `float` | Required -   | Timeout                                                                                     |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails. Use `Settings` if `None` is specified         |

| Return Type | Description   |
| ----------- | ------------- |
| `bool`      | Whether to wait for success   |

**Example:**

```python
# Access the website
page.get('https://www.*****.cn/login/')  # Access the login page
page.ele('#username').input('***')  # Execute login logic
page.ele('#password').input('***\n')

page.wait.url_change('https://www.*****.cn/center/')  # Wait for the URL to change to the background URL
```

---

### 📌 `wait()`

This method is used to wait for a certain number of seconds, and there is no difference with `sleep()`, but the author is too lazy to write another import statement.

| Parameter Name | Type    | Default Value | Description                                      |
| -------------- | ------- | ------------- | ------------------------------------------------ |
| `second`       | `float` | Required -   | Wait for a certain number of seconds               |

**Return:** `None`

**Example:**

```python
page.wait(1)  # Wait for 1 second forcefully

import time
time.sleep(1)  # No difference with this line
```

---

## ✅️️ Waiting Methods of Element Objects

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('http://g1879.gitee.io/drissionpagedocs/')
ele = page('tag:div')
ele.wait.covered()
```

### 📌 `wait.displayed()`

This method is used to wait for an element to change from a hidden state to a displayed state.

An element is hidden when it is in the DOM but in a hidden state (even if it is in the viewport and not covered). The child elements are also hidden when the parent elements are hidden.

| Parameter Name | Type    | Default Value | Description                                      |
| -------------- | ------- | ------------- | ------------------------------------------------ |
| `timeout`      | `float` | `None`        | Timeout. Use the timeout of the element's page if `None` is specified                        |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails. Use `Settings` if `None` is specified         |

| Return Type | Description   |
| ----------- | ------------- |
| `bool`      | Whether waiting is successful   |

**Example:**

```python
# Wait for the element to be displayed. Use the timeout of the ele's page
ele.wait.displayed()
```

---

### 📌 `wait.hidden()`

This method is used to wait for an element to change from a displayed state to a hidden state.

An element is hidden when it is in the DOM but in a hidden state (even if it is in the viewport and not covered). The child elements are also hidden when the parent elements are hidden.

| Parameter Name | Type    | Default Value | Description                                      |
| -------------- | ------- | ------------- | ------------------------------------------------ |
| `timeout`      | `float` | `None`        | Timeout. Use the timeout of the element's page if `None` is specified                        |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails. Use `Settings` if `None` is specified         |

| Return Type | Description   |
| ----------- | ------------- |
| `bool`      | Whether waiting is successful   |

**Example:**

```python
# Wait for the element to be hidden for 3 seconds
ele.wait.hidden(timeout=3)
```

---

### 📌 `wait.deleted()`

This method is used to wait for an element to be deleted from the DOM.

| Parameter Name | Type    | Default Value | Description                                      |
| -------------- | ------- | ------------- | ------------------------------------------------ |
| `timeout`      | `float` | `None`        | Timeout. Use the timeout of the element's page if `None` is specified                        |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails. Use `Settings` if `None` is specified         |

| Return Type | Description   |
| ----------- | ------------- |
| `bool`      | Whether waiting is successful   |

**Example:**

```python
# Wait for the element to be displayed. Use the timeout of the ele's page
ele.wait.deleted()
```

---

### 📌 `wait.covered()`

This method is used to wait for an element to be covered by other elements.

| Parameter Name | Type    | Default Value | Description                                      |
| -------------- | ------- | ------------- | ------------------------------------------------ |
| `timeout`      | `float` | `None`        | Timeout. Use the timeout of the element's page if `None` is specified                        |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails. Use `Settings` if `None` is specified         |

| Return Type | Description   |
| ----------- | ------------- |
| `bool`      | Whether waiting is successful   |

---

### 📌 `wait.not_covered()`

This method is used to wait for an element not to be covered by other elements.

It can be used to wait for the "loading" mask that covers the element being operated on to disappear.

| Parameter Name | Type   | Default Value | Description                                          |
|----------------|--------|---------------|------------------------------------------------------|
| `timeout`      | `float` | `None`        | Waiting timeout duration, if `None` then use the timeout duration of the element on the page |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails, if `None` then based on the `Settings` configuration |

| Return Type | Description           |
|-------------|-----------------------|
| `bool`      | Whether the wait succeeded |

---

### 📌 `wait.enabled()`

This method is used to wait for an element to become enabled.

An element in an disabled state is still in the DOM with a `disabled` attribute set to `False`.

| Parameter Name | Type   | Default Value | Description                                          |
|----------------|--------|---------------|------------------------------------------------------|
| `timeout`      | `float` | `None`        | Waiting timeout duration, if `None` then use the timeout duration of the element on the page |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails, if `None` then based on the `Settings` configuration |

| Return Type | Description           |
|-------------|-----------------------|
| `bool`      | Whether the wait succeeded |

---

### 📌 `wait.disabled()`

This method is used to wait for an element to become disabled.

An element in an disabled state is still in the DOM with a `disabled` attribute set to `True`.

| Parameter Name | Type   | Default Value | Description                                          |
|----------------|--------|---------------|------------------------------------------------------|
| `timeout`      | `float` | `None`        | Waiting timeout duration, if `None` then use the timeout duration of the element on the page |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails, if `None` then based on the `Settings` configuration |

| Return Type | Description           |
|-------------|-----------------------|
| `bool`      | Whether the wait succeeded |

---

### 📌 `wait.stop_moving()`

This method is used to wait for an element to stop moving. If the element does not have size and position information, a `NoRectError` exception will be thrown when the timeout is reached.

| Parameter Name | Type   | Default Value | Description                                                  |
|----------------|--------|---------------|--------------------------------------------------------------|
| `gap`          | `float` | `0.1`         | Time interval to check for movement                            |
| `timeout`      | `float` | `None`        | Waiting timeout duration, if `None` then use the timeout duration of the element on the page |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails, if `None` then based on the `Settings` configuration |

| Return Type | Description           |
|-------------|-----------------------|
| `bool`      | Whether the wait succeeded |

```python
# Wait for element to stabilize
page.ele('#button1').wait.stop_moving()
# Click on the element
page.ele('#button1').click()
```

---

### 📌 `wait.disable_or_deleted()`

This method is used to wait for an element to become disabled or deleted.

| Parameter Name | Type   | Default Value | Description                                          |
|----------------|--------|---------------|------------------------------------------------------|
| `timeout`      | `float` | `None`        | Waiting timeout duration, if `None` then use the timeout duration of the element on the page |
| `raise_err`    | `bool`  | `None`        | Whether to raise an error when waiting fails, if `None` then based on the `Settings` configuration |

| Return Type | Description           |
|-------------|-----------------------|
| `bool`      | Whether the wait succeeded |

---

### 📌 `wait()`

This method is used to wait for a certain number of seconds, same as `sleep()`.

| Parameter Name | Type   | Default Value | Description     |
|----------------|--------|---------------|-----------------|
| `second`       | `float` | Required      | Number of seconds to wait |

**Returns:** `None`

