# Download Files

DrissionPage comes with a convenient downloader that allows you to easily download files with just one line of code.

```python
from DrissionPage import WebPage

url = 'https://www.baidu.com/img/flexible/logo/pc/result.png'
save_path = r'C:\download'

page = WebPage('s')
page.download(url, save_path)
```

