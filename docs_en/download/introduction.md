⤵️ Overview
---

DrissionPage provides powerful file download management capabilities.

It can initiate download tasks actively and also manage download tasks triggered by the browser.

## ✅️️ `download()` method

This method can actively initiate download tasks and provide features such as task management, multi-threading, large file chunking, automatic reconnection, and file name conflict handling.

This method is supported by page objects, tab objects, and `<iframe>` element objects.

:::tip Tips
    When using this method, the program automatically synchronizes the cookies information of the object on which the method is called.
:::

**Example:**

```python
from DrissionPage import SessionPage

page = SessionPage()
page.download('https://dldir1.qq.com/qqfile/qq/TIM3.4.8/TIM3.4.8.22092.exe')
```

---

## ✅️️ Browser download tasks

Browser page objects, tab objects, and `<iframe>` objects can control browser download tasks.

The following features are included:

- Each tab object can independently specify a download URL
- It is possible to specify a renamed file name before downloading
- Intercept download tasks and obtain task information

**Example:**

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.download_path('save_path')  # Set the file save path
page.set.download_file_name('file_name')  # Set the renamed file name
page('t:a').click()  # Click on a link that triggers a download
page.wait.download_begin()  # Wait for the download to begin
page.wait.downloads_done()  # Wait for the download to finish
```

