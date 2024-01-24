🚄 Overview
---

The `SessionPage` object and the `WebPage` object's s pattern allow you to access web pages in the form of sending and receiving data packets.

This chapter introduces `SessionPage`.

As the name suggests, `SessionPage` is a page that uses the `Session` (requests library) object. It encapsulates the functions of network connection and HTML parsing using the Page Object Model (POM) pattern, making it convenient to send and receive data packets just like operating a page.

Moreover, the library has also introduced its original methods for element lookup, making data collection much more convenient compared to combinations such as requests + beautifulsoup.

`SessionPage` is the simplest among the various page objects in this library, so let's start with it.

Let's take a simple example to understand how `SessionPage` works.

---

Get all the recommended projects on gitee's first page.

```python
# Import
from DrissionPage import SessionPage
# Create a page object
page = SessionPage()
# Access the webpage
page.get('https://gitee.com/explore/all')
# Find elements on the page
items = page.eles('t:h3')
# Iterate through the elements
for item in items[:-1]:
    # Get the <a> element under the current <h3> element
    lnk = item('tag:a')
    # Print the text and href attribute of the <a> element
    print(lnk.text, lnk.link)
```

**Output:**

```shell
七年觐汐/wx-calendar https://gitee.com/qq_connect-EC6BCC0B556624342/wx-calendar
ThingsPanel/thingspanel-go https://gitee.com/ThingsPanel/thingspanel-go
APITable/APITable https://gitee.com/apitable/APITable
Indexea/ideaseg https://gitee.com/indexea/ideaseg
CcSimple/vue-plugin-hiprint https://gitee.com/CcSimple/vue-plugin-hiprint
william_lzw/ExDUIR.NET https://gitee.com/william_lzw/ExDUIR.NET
anolis/ancert https://gitee.com/anolis/ancert
cozodb/cozo https://gitee.com/cozodb/cozo
... (omitted)
```


