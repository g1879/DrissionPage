🚤 Screenshots and Recordings
---

## ✅️️ Page Screenshots

Use the `get_screenshot()` method of the page object to take screenshots of the page, including the entire webpage, visible webpage, or a specified area.

Taking screenshots outside the visible range requires browser support of version 90 or above.

Choose one of the following three parameters: `as_bytes`>`as_base64`>`path`.

| Parameter Name | Type   | Default | Description                                               |
| :------------: | :----: | :-----: | --------------------------------------------------------- |
|    `path`      | string | `None`  | The path to save the image. Defaults to the current folder.                           |
|    `name`      | string | `None`  | The complete file name. Optional extensions: `'jpg'`, `'jpeg'`, `'png'`, `'webp'`. Defaults to jpg.                                                  |
|   `as_bytes`   | string | `True`  | Whether to return the image as bytes. Optional extensions: `'jpg'`, `'jpeg'`, `'png'`, `'webp'`, `None`, `True`. If not `None`, the `path` parameter is ignored. Defaults to jpg.                   |
|  `as_base64`   | string | `None`  | Whether to return the image as base64 encoded string. Optional extensions: `'jpg'`, `'jpeg'`, `'png'`, `'webp'`, `None`, `True`. If not `None`, the `path` parameter is ignored. Defaults to jpg. |
|  `full_page`   | boolean| `False` | Whether to take a full-page screenshot. Set to `True` for the entire webpage, `False` for the visible viewport only.                            |
|   `left_top`   | tuple  | `None`  | The top-left coordinates of the screenshot area.                                         |
| `right_bottom` | tuple  | `None`  | The bottom-right coordinates of the screenshot area.                                     |

| Return Type | Description                                                           |
| :--------: | --------------------------------------------------------------------- |
|   bytes    | Returns the image bytes when `as_bytes` is in effect.                    |
|   string   | Returns the complete path of the image when `as_bytes` and `as_base64` are `None`. |
|   string   | Returns the base64 encoded string when `as_base64` is in effect.          |

:::info Information
    If `path` contains the filename, the `name` parameter is ignored.
:::

**Example:**

```python
# Take a full-page screenshot and save it
page.get_screenshot(path='tmp', name='pic.jpg', full_page=True)
```

## ️️ ✅️️ Element Screenshots

Use the `get_screenshot()` method of the element object to take screenshots of the element.

If the element is outside the viewport, it requires browser support of version 90 or above.

Choose one of the following three parameters: `as_bytes`>`as_base64`>`path`.

|  Parameter Name  |    Type    |  Default | Description                                                      |
| :-------------: | :-------: | :------: | ---------------------------------------------------------------- |
|     `path`     |  string | `None`  | The path to save the image. Defaults to the current folder.                        |
|     `name`     |  string | `None`  | The complete file name. Optional extensions: `'jpg'`, `'jpeg'`, `'png'`, `'webp'`. Defaults to jpg.                                   |
|   `as_bytes`   |  string | `None`  | Whether to return the image as bytes. Optional extensions: `'jpg'`, `'jpeg'`, `'png'`, `'webp'`, `None`, `True`. If not `None`, the `path` and `as_base64` parameters are ignored. Defaults to jpg. |
|  `as_base64`  |  string | `None`  | Whether to return the image as base64 encoded string. Optional extensions: `'jpg'`, `'jpeg'`, `'png'`, `'webp'`, `None`, `True`. If not `None`, the `path` parameter is ignored. Defaults to jpg.       |
| `scroll_to_center` | boolean | `True` | Whether to scroll to the center of the viewport before taking the screenshot. |

| Return Type | Description                                                           |
| :--------: | --------------------------------------------------------------------- |
|   bytes    | Returns the image bytes when `as_bytes` is in effect.                    |
|   string   | Returns the complete path of the image when `as_bytes` and `as_base64` are `None`. |
|   string   | Returns the base64 encoded string when `as_base64` is in effect.          |

:::info Information
    If `path` contains the filename, the `name` parameter is ignored.
:::

**Example:**

```python
img = page('tag:img')
img.get_screenshot()
bytes_str = img.get_screenshot(as_bytes='png')  # Returns the screenshot as a binary string
```

---

## ✅️️ Screen Recording

Use the `screencast` functionality of the page object to take screenshots or record screen videos.

### 📌 Set Recording Mode

There are a total of 5 recording modes, which can be set using the `screencast.set_mode.xxx_mode()` method.

| Mode                   | Description                                             |
|:----------------------:| ------------------------------------------------------- |
| `video_mode()`         | Continuously records the page and generates a video without sound when stopped. |
| `frugal_video_mode()`  | Records the page only when there is a change, and generates a video without sound when stopped. |
| `js_video_mode()`🧪    | Generates a video with sound, but needs to be manually started. This feature is still in testing phase. |
| `imgs_mode()`          | Continuously takes screenshots of the page.              |
| `frugal_imgs_mode()`   | Takes screenshots of the page only when there is a change. |

### 📌 Set Save Path

Use `screencast.set_save_path()` to set the path to save the recording results.

| Parameter     | Type              | Default | Description              |
|:-------------:|:-----------------:|:-------:| ------------------------ |
| `save_path`   | `str`<br/>`Path` | `None`  | Path to save images or videos. |

**Returns:** `None`

### 📌 `screencast.start()`

This method is used to start recording the browser window.

| Parameter     | Type              | Default | Description              |
|:-------------:|:-----------------:|:-------:| ------------------------ |
| `save_path`   | `str`<br/>`Path` | `None`  | Path to save images or videos. |

**Returns:** `None`

:::warning Note
    The save path must be set, regardless of whether it is set using `screencast.set()` or `screencast.start()`.
:::

### 📌 `screencast.stop()`

This method is used to stop recording the screen.

| Parameter     | Type    | Default | Description                          |
|:-------------:|:-------:|:-------:| ----------------------------------- |
| `video_name`  | `str`   | `None`  | Video file name. If `None`, it is named with the current time. |

| Return Type   | Description                                         |
|:-------------:| --------------------------------------------------- |
| `str`         | Returns the path of the video file if saved as a video, otherwise returns the folder path of the saved image. |

### 📌 Note

- When using `video_mode` and `frugal_video_mode`, the save path and file name must be in English.

- When using `video_mode` and `frugal_video_mode`, the opencv library needs to be installed first. `pip install opencv-python`

- When using `js_video_mode`, the target to be recorded needs to be manually selected with the mouse before recording can begin.

- When using `js_video_mode`, if recording of a window is desired, recording needs to be started in another window. Otherwise, if the window jumps, the recording will be invalidated.

### 📌 Example

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.screencast.set_save_path('video')  # Set the video save path
page.screencast.set_mode.video_mode()  # Set the recording mode
page.screencast.start()  # Start recording
sleep(3)
page.screencast.stop()  # Stop recording
```

