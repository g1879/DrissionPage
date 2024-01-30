💖 Intimate Design
---

Here is an introduction to some of the user-friendly designs built into this library.

## ✅️️ Universal Waiting

In an unstable network environment, programs often need to wait for a while before they can continue running. Waiting too little can cause errors in the program, while waiting too much can waste time. To solve these problems, this library has built-in timeout functionality in many sections that require waiting and can be flexibly set at any time, significantly reducing program complexity.

- Built-in waiting for element lookup. The waiting time can be set individually for each element lookup. Some pages may display prompt messages irregularly. If waiting all the time would be too time-consuming, a very short timeout can be set independently to avoid waste.

- Waiting for dropdown list options. Many dropdown lists are loaded using JavaScript. When selecting a dropdown list, this library will automatically wait for the list items to appear.

- Waiting for pop-up windows. Sometimes the expected alert may not appear immediately. This library can also set a waiting time for handling pop-up messages.

- Waiting for element state changes. The `wait.ele()` method can wait for elements to appear, disappear, or be deleted.

- Waiting for page loading or completion. This not only saves time but also greatly improves program stability.

- The clicking function also has built-in waiting. If an element is blocked, it can be continuously retried for clicking.

- Setting page loading time limit and loading strategy. Sometimes it is not necessary to load complete page resources, and the loading strategy can be set according to actual needs.

---

## ✅️️ Automatic Retrying of Connections

When accessing a website, network instability may cause connection failures. This library has a feature that automatically retries connections. When a webpage connection fails, it will be retried 3 times by default. Of course, the number of retries and the interval can also be manually set.

```python
page.get('xxxxxx', retry=5, interval=3)  # Retry 5 times with a 3-second interval when an error occurs
```

---

## ✅️️ Minimalistic Locator Syntax

This library has developed a concise and efficient syntax for locating elements, supporting chain operations and relative positioning. Compared to the cumbersome syntax of selenium, it is extremely convenient.

Every time a search is performed, there is a built-in waiting period, and the timeout for each search can be set independently.

Let's compare the use of timed searches:

```python
# Using selenium:
element = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "some text")]')))

# Using DrissionPage:
element = page('some text', timeout=10)
```

---

## ✅️️ No Need to Switch In and Out, Clear Logic

Those who have used selenium know that selenium can only operate one tab or `<iframe>` element at a time. To operate other tabs or `<iframe>` elements, the `switch_to()` method needs to be used to switch, and after the operation, it needs to be switched back. If there are multiple levels of `<iframe>`, it needs to be switched in layer by layer, which is quite cumbersome.

DrissionPage does not require these cumbersome operations. It treats each tab and `<iframe>` as independent objects that can be operated concurrently, and can directly cross multiple levels of `<iframe>` to obtain elements inside and process them directly, which is very convenient.

Let's compare getting an element with an id of `'div1'` in a 2-level `<iframe>`:

```python
# Using selenium:
driver.switch_to.frame(0)
driver.switch_to.frame(0)
ele = driver.find_element(By.ID, 'div1')
driver.switch_to.default_content()

# Using DrissionPage:
ele = page('#div1')
```

Concurrently operating multiple tabs, selenium does not have this feature:

```python
tab1 = page.get_tab(page.tabs[0])
tab2 = page.get_tab(page.tabs[1])

tab1.get('https://www.baidu.com')
tab2.get('https://www.163.com')
```

---

## ✅️️ Fully Integrated Convenience Features

Many operation methods integrate common functions, such as the `click()` method, which has a built-in `by_js` parameter that allows direct clicking using JavaScript without the need for separate JavaScript statements.

---

## ✅️️ Powerful Downloading Functionality

DrissionPage has a built-in download tool that can download large files in multiple threads and blocks. It can also directly read cache data to save images without the need for controlling the page to perform a save operation.

```python
img = page('tag:img')
img.save('img.png')  # Save the image directly to a folder
```

---

## ✅️️ More Convenient Features

- The entire webpage can be captured as a screenshot, including areas outside the viewport.

- Each time the program runs, the already opened browser can be reused without starting from scratch.

- The 's' mode automatically corrects encoding when accessing webpages, without the need for manual settings.

- The 's' mode automatically fills in the `Host` and `Referer` properties based on the current domain when connecting.

- The download tool supports various ways to handle filename conflicts, automatically create target paths, and retry broken links.

- `MixPage` can automatically download the appropriate version of chromedriver, eliminating the hassle of configuration.

- Supports directly getting the content of `after` and `before` pseudo-elements.

- Can intercept the file selection box and enter the path directly when uploading a file, without relying on a GUI or searching for `<input>` elements to input.

