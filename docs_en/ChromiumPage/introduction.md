🚤 Overview
---

The `ChromiumPage` object and the `WebPage` object are d models for manipulating the browser. This chapter introduces `ChromiumPage`.

As the name suggests, `ChromiumPage` is a page of the Chromium kernel browser, which encapsulates the properties and methods required to manipulate web pages using POM.

Using it, we can interact with web pages, such as adjusting window size, scrolling pages, and operating pop-up windows, etc.

With the element objects obtained from it, we can also interact with elements on the page, such as entering text, clicking buttons, selecting drop-down menus, etc.

Even, we can run JavaScript code on the page or elements, modify element properties, add or remove elements, etc.

It can be said that most operations for manipulating the browser can be completed by `ChromiumPage` and its derivative objects, and their functions are constantly increasing.

In addition to interacting with pages and elements, `ChromiumPage` also acts as a browser controller. It can be said that a `ChromiumPage` object is a browser.

It can manage tabs, control download tasks, and generate independent page objects (`ChromiumTab`) for each tab, allowing simultaneous operation of multiple tabs without switching.

With the release of version 3.0, the author finally can unleash his imagination and add various interesting features to `ChromiumPage`. We will continue to improve it in the future.

Let's take a simple example to understand how `CromiumPage` works.

---

Search "Drissionpage" on Baidu and print the result.

```python
# Import
from DrissionPage import ChromiumPage

# Create an object
page = ChromiumPage()
# Access the web page
page.get('https://www.baidu.com')
# Enter text
page('#kw').input('DrissionPage')
# Click the button
page('#su').click()
# Wait for page redirection
page.wait.load_start()
# Get all results
links = page.eles('tag:h3')
# Traverse and print the results
for link in links:
    print(link.text)
```


