# ⤵️ DownloadKit

The `DrissionPage` module comes with a built-in download tool called DownloadKit, which provides functionalities such as task management, multithreaded concurrency, large file chunking, automatic reconnection, and filename conflict handling.

The DownloadKit tool has been packaged as a separate library and its detailed usage can be found at: [DownloadKit](https://gitee.com/g1879/DownloadKit).

This document only introduces the main features of DownloadKit. For specific usage and configuration methods, please refer to the official documentation.

## ✅️️ Functionality Overview

### 📌 Supported Objects

DownloadKit supports the following objects:

- `SessionPage`
- `ChromiumPage`
- `WebPage`
- `ChromiumTab`
- `WebPageTab`
- `ChromiumFrame`

---

### 📌 Downloader Features

- Able to download files from specific URLs
- Supports multi-threaded concurrent downloading of multiple files
- Automatically splits and downloads large files using multiple threads
- Can append data to existing files
- Automatically creates the destination path
- Supports file renaming during download
- Automatically handles filename conflicts
- Automatically removes illegal characters from paths and filenames
- Supports POST requests
- Supports custom connection parameters
- Automatically retries failed tasks

:::warning Note
    DownloadKit is a wrapper around the `requests` library and does not call browser functions.
    If the download target has specific requirements such as headers or data, they need to be manually added.
:::

---

## ✅️️ Adding Tasks

### 📌 Single-threaded Task

The `download()` method can be used to add a single-threaded task. This method is blocking and only uses one thread.

**Example:**

```python
from DrissionPage import SessionPage

page = SessionPage()
url = 'https://www.baidu.com/img/flexible/logo/pc/result.png'
save_path = r'C:\download'

res = page.download(url, save_path)
print(res)
```

Output:

```shell
url: https://www.baidu.com/img/flexible/logo/pc/result.png
filename: result.png
destination path: C:\download
100% download complete C:\download\result.png

('success', 'C:\\download\\result.png')
```

---

### 📌 Concurrent Tasks

Use the `download.add()` method to add concurrent tasks.

**Example:**

```python
url1 = 'https://dldir1.qq.com/qqfile/qq/TIM3.4.8/TIM3.4.8.22092.exe'
url2 = 'https://dldir1.qq.com/qqfile/qq/PCQQ9.7.16/QQ9.7.16.29187.exe'
save_path = 'files'

page = SessionPage()
page.download.add(url1, save_path)
page.download.add(url2, save_path)
```

---

### 📌 Parallel Chunked Download

The `split` parameter of the `download.add()` method can be used to enable or disable chunked downloading for large files.

The `download.set.block_size()` method can be used to set the chunk size.

By default, files larger than 50MB will be automatically downloaded in chunks.

**Example:**

```python
page = SessionPage()
page.download.set.block_size('30m')  # Set the chunk size
page.download.add('http://xxxx/demo.zip')  # Download with default chunking
page.download.add('http://xxxx/demo.zip', split=False)  # Download without chunking
```

---

### 📌 Blocking Multi-threaded Task

When using parallel chunked downloads, tasks can also be downloaded one by one using the `add()` method followed by `wait()`.

**Example:**

```python
page = SessionPage()
page.download.add('http://xxxx/demo.zip').wait()
page.download.add('http://xxxx/demo.zip').wait()
```

---

### 📌 Detailed Documentation

The examples above are simplified versions. For detailed usage, please refer to the [DownloadKit Adding Tasks](http://g1879.gitee.io/downloadkitdocs/usage/add_missions/) documentation.

---

## ✅️️ Download Settings

### 📌 Global Settings

The `download.set.xxxx()` methods can be used to configure the default download behavior.

These settings include:

- Save path
- Maximum number of threads allowed
- Enable or disable chunked downloads
- Chunk size
- Number of retry attempts for connection failures
- Retry interval
- Connection timeout
- Filename conflict handling
- Logging and display settings

---

### 📌 Individual Task Settings

When creating a new task, the `download()` and `add()` methods' parameters can be used to set specific parameters for the current task, overriding the global settings.

Refer to the previous section on adding parameters for more details.

---

### 📌 Detailed Documentation

For detailed configuration options, please refer to the [DownloadKit Runtime Settings](http://g1879.gitee.io/downloadkitdocs/usage/settings/) documentation.

---

## ✅️️ Task Management

### 📌 Mission Objects

The `Mission` object is used to manage tasks and provides the following functionalities:

- View task status, information, and progress
- Save task parameters such as URL and connection parameters
- Cancel ongoing tasks
- Delete downloaded files

---

### 📌 Getting a Single Mission Object

When using the `download.add()` method to add a task, a mission object will be returned.

**Example:**

```python
mission = page.download.add('http://xxxx.pdf')
print(mission.id)  # Get the task ID
print(mission.rate)  # Print the download progress (percentage)
print(mission.state)  # Print the task status
print(mission.info)  # Print the task information
print(mission.result)  # Print the task result
```

In addition to getting the object when adding a task, you can also use the `download.get_mission()` method. As seen in the previous example, the mission object has a `id` attribute. Pass the mission ID to this method to get the corresponding mission object.

**Example:**

```python
mission_id = mission.id
mission = page.download.get_mission(mission_id)
```

---

### 📌 Getting All Mission Objects

Using the `download.missions` attribute of the page object, you can get all the download tasks. This attribute returns a `dict` that contains all the download tasks, with the task object's `id` as the key.

```python
page.download_set.save_path(r'D:\download')
page.download('http://xxxxx/xxx1.pdf')
page.download('http://xxxxx/xxx1.pdf')
print(page.download.missions)
```

**Output:**

```
{
    1: <Mission 1 D:\download\xxx1.pdf xxx1.pdf>
    2: <Mission 2 D:\download\xxx1_1.pdf xxx1_1.pdf>
    ...
}
```

---

### 📌 Get failed missions

You can use the `download.get_failed_missions()` method to get a list of failed download missions.

```python
page.download_set.save_path(r'D:\download')
page.download('http://xxxxx/xxx1.pdf')
page.download('http://xxxxx/xxx1.pdf')
print(page.download.get_failed_missions()
```

**Output:**

```
[
    <Mission 1 Status code: 404 None>,
    <Mission 2 Status code: 404 None>
    ...
]
```

:::tip Tips
    After getting the failed mission object, you can retrieve the task content from its `data` attribute for logging purposes or for retrying at a later time.
:::

---

### 📌 Detailed documentation

For detailed configuration options, please refer to: [DownloadKit Mission Management](http://g1879.gitee.io/downloadkitdocs/usage/misssions/)

