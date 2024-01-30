⤵️ Browser Download
---

This section introduces the functionality for setting up browser download tasks.

## ✅️ Overview

### 📌 Functionality

DrissionPage provides the following functionality for controlling browser download tasks:

- Each tab object can independently set the file save path.
- The file name can be specified before downloading to achieve file renaming.
- The handling method for existing files with the same name can be configured.
- The download progress of tasks can be obtained.
- Waiting for the download tasks to finish.
- Cancelling tasks.
- Intercepting download tasks and obtaining their information.

---

### 📌 Supported Objects

The following objects support the above functions:

- `ChromiumPage`
- `WebPage`
- `ChromiumTab`
- `WebPageTab`
- `ChromiumFrame`

---

### 📌 Required Concepts

Before we start, let's clarify some concepts.

Page objects include both Page objects and Tab objects.

The Page object (`ChromiumPage` and `WebPage`) controls a tab and serves as the manager for all tabs, i.e., the browser.

Each Tab object (`ChromiumTab` and `WebPageTab`) controls a tab.

A tab can be controlled by multiple page objects.

They have the following characteristics in terms of download settings:

- Newly created Tab objects inherit the path settings of the Page object by default.
- Newly created Page or Tab objects use the `'rename'` method to handle file name conflicts by default.
- For the same tab, multiple page objects share a set of download settings. If one object modifies the settings, the others will be affected.
- Download tasks triggered by `<iframe>` elements also use the download settings of the Tab object they belong to.
- If download settings are applied to `<iframe>` elements, the settings of the Tab object it belongs to will be modified.

:::tip Tips
    Some download tasks create a temporary tab, trigger downloads, and then immediately close. These tasks use the download settings of the Page object. That is, if a tab is not controlled by a Tab or Page object, the download tasks it triggers will be set according to the Page's settings, including save path and renaming.
:::

---

## ⚠️ Cautions

### 📌 Remember to Wait for Task Completion

Due to technical reasons, the program can only rename the file after the download is complete. Before that, the file name is the temporary task ID.

Therefore, it is necessary to wait for the download to complete before the file name can be correctly named. This is the case whether or not a file name is specified.

**Example:**

```python
page = ChromiumPage()
page('#button').click()  # Click the download button
page.wait.download_begin()  # Wait for the download to start
page.wait.all_downloads_done()  # Wait for all tasks to finish
```

---

### 📌 Recommended to Set a Temporary Path When Operating with Multiple Tabs

Because the program needs to download tasks to a specified location and then move them to the target path, if the program involves multiple Tab objects triggering download tasks, it is best to set a download path for the Page object.

Even if each Tab object sets its own path.

**Example:**

```python
page = ChromiumPage()
page.set.download_path('tmp')  # Set the overall path

tab1 = page.get_tab(page.tabs[1])
tab1.set.download_path('path1')

tab2 = page.get_tab(page.tabs[2])
tab2.set.download_path('path2')
```

:::tip Tips
    In this example, `page` itself is a tab, so there are 3 tabs here.
    If `get_tab()` is used to get the tab of `page` for settings, it will override the settings of `page`.
:::

---

### 📌 Enabling Download Management Functionality

The download management functionality introduced in this section is not enabled by default. At this time, triggering download tasks and manual operations have no difference.

The management functionality will be enabled when the download path is set in the configuration or when the `set.download_path()` method is called.

---

## ✅️ Set Download Path

### 📌 Set Overall Download Path

Use the `set.download_path()` method of the Page object to set the download path. If not set, the default is to download to the current path of the program.

After setting the download path of the Page object, all subsequently created Tab objects will use this address. If the previously created Tab objects have not set their own path, they will also use the new path.

When using this method, the download paths of built-in `DownloadKit` objects (if any) will also change at the same time.

|  Parameter Name  |       Type       | Default Value | Description |
|:---------------:|:---------------:|:-------------:|-------------|
|      `path`     | `str`<br/>`Path` |   Required    | Download path |

**Returns:** `None`

**Example:**

```python
page = ChromiumPage()
page.set.download_path(r'C:\tmp')
```

---

### 📌 Set Tab Download Path

The method is used in the same way as setting the Page, but only takes effect in the current Tab object.

**Example:**

```python
page = ChromiumPage()
tab = page.get_tab(page.tabs[1])  # Create a Tab object
tab.set.download_path(r'C:\tmp1')  # Set the Tab download path
```

---

## ✅️ Set File Name

The `download_file_name()` method can be used to set the file name before downloading, achieving file renaming.

The set file name can be without an extension, and the program will automatically add the extension based on the downloaded file.

If the set file name contains a `'.'` and the extension is different from the network file, the program will use the extension of the network file.

If you want to modify the file extension, simply set the `suffix` parameter.

After each trigger for downloading, this setting will be cleared.

| Parameter Name |   Type  | Default Value | Description            |
|:--------------:|:-------:|:-------------:|------------------------|
|     `name`     | `str`   |     `None`    | The file name          |
|    `suffix`    | `str`   |     `None`    | The file extension, pass `''` to remove the extension |

**Returns:** None

**Example:**

```python
page = ChromiumPage()
page.set.download_file_name('new_file')
page('t:a').click()  # Click a link that triggers the download
page.wait.download_begin()
page.wait.all_download_done()  # Remember to wait for the task to trigger and end
```

---

## ✅️ Waiting

### 📌 Waiting for Download to Begin

After clicking on a download link, the download does not trigger instantly and needs to be waited for in order to catch it.

Use the `wait.download_begin()` method to wait for the download to begin.

Generally, for download tasks triggered by a tab, use the Tab object to wait, and for downloads triggered by uncontrolled tabs, use the Page object to wait.

When the `cancel_it` parameter is set to True, the task will be canceled when it is caught, so that the returned download information can be used for other purposes.

|  Parameter Name |   Type  | Default Value | Description                |
|:--------------:|:-------:|:-------------:|----------------------------|
|    `timeout`   | `float` |     `None`    | Timeout period, `None` for the default waiting time |
|   `cancel_it`  | `bool`  |    `False`    | Whether to cancel the task when caught           |

|   Return Type   | Description                    |
|:--------------:|--------------------------------|
| `DownloadMission` | Returns the download task object when waiting is successful |
|     `False`    | Returns `False` when waiting fails |

**Example:**

```python
page = ChromiumPage()
page('t:a').click()  # Click a link that triggers the download
page.wait.download_begin()
```

---

### 📌 Waiting for All Download Tasks to Finish

Use the `page.wait.all_downloads_done()` method of the Page object to wait for all download tasks in the browser to finish.

|   Parameter Name    |   Type  | Default Value | Description            |
|:-------------------:|:-------:|:-------------:|------------------------|
|      `timeout`      | `float` |     `None`    | Timeout period, `None` for unlimited waiting |
| `cancel_if_timeout` | `bool`  |    `False`    | Whether to cancel unfinished tasks if timeout     |

|  Return Type  | Description               |
|:------------:|---------------------------|
|    `bool`    | Whether it successfully waited |

---

### 📌 Waiting for All Download Tasks of Tab to Finish

Use the `tab.wait.downloads_done()` method of the Tab object to wait for the download tasks triggered by the Tab object to finish.

This method should be used for waiting for the tasks triggered by the Page object, as the Page object itself also controls a tab.

|   Parameter Name    |   Type  | Default Value | Description            |
|:-------------------:|:-------:|:-------------:|------------------------|
|      `timeout`      | `float` |     `None`    | Timeout period, `None` for unlimited waiting |
| `cancel_if_timeout` | `bool`  |    `False`    | Whether to cancel unfinished tasks if timeout     |

|  Return Type  | Description               |
|:------------:|---------------------------|
|    `bool`    | Whether it successfully waited |

---

## ✅️ Intercepting Download Tasks

The `wait.download_begin()` method has a `cancel_it` parameter that, when set to True, cancels the download task.

At this time, you can use the task information returned by this method for the next operation, such as downloading using the `download()` method.

**Example:**

```python
page = ChromiumPage()
page('t:a').click()
data = page.wait.download_begin(cancel_it=True)
page.download(data['url'])
```

---

## ✅️ Handling Same-Name Files

When encountering files with the same name during downloading, you can choose from three options: automatically rename, overwrite, or skip.

Use `set.when_download_file_exists('xxxx')` to set the handling method.

Where `xxxx` can be `'rename'`, `'overwrite'`, or `'skip'`.

You can also use the first letter of each option: `'r'`, `'o'`, or `'s'`.

### 📌 Automatically Rename

Method: `page.set.when_download_file_exists('rename')`

This method will automatically rename the new file by adding a serial number at the end.

For example, if there is already a file named 'abc.zip' in the save path, and another 'abc.zip' is downloaded, the new file will be automatically renamed to 'abc_1.zip'.

Subsequent downloads will be named 'abc_2.zip', and so on.

---

### 📌 Overwrite Existing Files

Method: `page.set.when_download_file_exists('overwrite')`

This method will replace the existing file with the newly downloaded one.

---

### 📌 Skip

Method: `page.set.when_download_file_exists('skip')`

This method will cancel the download task when a file with the same name is found.

---

## ✅️ Task Management

The `wait.download_begin()` method returns a `DownloadMission` object for managing browser download tasks.

### 📌 Get Task Information

You can get the task status, progress, save path, file name, and other information.

| Attribute Name | Type | Description |
|:--------------:|:----:|-------------|
| `url` | `str` | Returns the URL of the task |
| `tab_id` | `str` | Id of the Tab object that triggered the task |
| `id` | `str` | Task ID |
| `path` | `str` | Save path, excluding the file name |
| `name` | `str` | File name |
| `state` | `str` | Task state, 'running', 'done', 'canceled', 'skipped' |
| `total_bytes` | `int` | Total number of bytes |
| `received_bytes` | `int` | Number of bytes received |
| `final_path` | `str` or `None` | The final complete path, generated only after the task is completed |

**Example:**

Print the progress of the task in real-time.

```python
mission = page.wait.download_begin()

while not mission.is_done:
    print(f'\r{mission.rate}%', end='')
```

---

### 📌 Wait for Task Completion

By using the `wait()` method of the `DownloadMission` object, you can wait for the task to complete.

| Parameter Name | Type | Default Value | Description |
|:--------------:|:----:|:-------------:|-------------|
| `show` | `bool` | `True` | Whether to print download information |
| `timeout` | `float` | `None` | Timeout duration, `None` for infinite waiting |
| `cancel_if_timeout` | `bool` | `False` | Whether to cancel the task if timeout |

| Return Type | Description |
|:-----------:|-------------|
| `str` | Returns the final saved path when the download is complete |
| `False` | Returns `False` if timeout or canceled |

---

### 📌 Cancel Task

By using the `cancel()` method of the `DownloadMission` object, you can cancel the task.

When this method is called, the downloaded file will be deleted, even if the task has been completed.

