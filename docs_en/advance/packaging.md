⚙️ Packaging Program
---

This section describes things to consider when packaging a program.

## ✅️️ Use a new virtual environment!

Develop the good habit of using a newly created virtual environment and only install necessary libraries for packaging, which can reduce the size of the packaged exe file. The size of the program packaged in an environment with only DrissionPage installed is approximately 14M.

If the size of the program you packaged is huge, please try this method.

---

## ✅️️ Solve the problem of missing ini file error

Because the program uses an ini file, and the ini file is not automatically included when packaging, directly packaging will cause runtime errors.

Solution:

- Manually include the ini file and specify the path in the program
- Write the configuration information in the program without using the ini file

### 📌 Include the ini file

Specify the ini file using relative path in the program and copy the ini file to the program folder.

```python
from DrissionPage import WebPage, ChromiumOptions, SessionOptions

co = ChromiumOptions(ini_path=r'.\configs.ini')
so = SessionOptions(ini_path=r'.\configs.ini')
page = WebPage(chromium_options=co, session_or_options=so)
```

You can use the `configs_to_here()` method to automatically copy the ini file.

Create a new py file in the project, enter the following content and run it.

```python
from DrissionPage.common import configs_to_here

configs_to_here()
```

After that, the project folder will have an additional `'dp_configs.ini'` file. The page object will prioritize reading this file during initialization.

Just put it together with the packaged executable file.

---

### 📌 Do not use ini

Specify not to use the ini file in the program to avoid errors. In this method, all configuration information needs to be written in the code.

Take `WebPage` as an example, the usage of `ChromiumPage` and `SessionPage` is the same.

```python
from DrissionPage import WebPage, ChromiumOptions, SessionOptions

co = ChromiumOptions(read_file=False)  # Create a new configuration object without reading the file
co.set_browser_path(r'.\chrome.exe')  # Enter the configuration information
so = SessionOptions(read_file=False)

page = WebPage(chromium_options=co, session_or_options=so)
```

Note that both the driver and session parameters need to be entered when using this method. If one of them does not need to be set, you can enter `False`:

```python
page = WebPage(chromium_options=co, session_or_options=False)
```

---

## ✅️️ Practical examples

Usually, I will put a portable browser and the packaged exe file together, and use relative paths in the program to point to the browser. This way, the program can be used normally on other computers as well.

```python
from DrissionPage import WebPage, ChromiumOptions

co = ChromiumOptions(read_file=False).set_paths(local_port='9888',
                                                browser_path=r'.\Chrome\chrome.exe',
                                                user_data_path=r'.\Chrome\userData')
page = WebPage(chromium_options=co, session_or_options=False)
# Note: session_or_options=False

page.get('https://www.baidu.com')
```

Note the following two points and the program will skip reading the ini file:

- Set `read_file=False` in `ChromiumOptions()`
- If you do not pass the configuration for a certain mode (in the example, it is the s mode), set the corresponding parameter to `False` when initializing the page object.

