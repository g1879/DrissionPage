⭐ Comparison with requests
---

The following code achieves the same functionality, comparing the amount of code for each:

🔸 Get element content

```python
url = 'https://baike.baidu.com/item/python'

# Using requests:
from lxml import etree
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
response = requests.get(url, headers = headers)
html = etree.HTML(response.text)
element = html.xpath('//h1')[0]
title = element.text

# Using DrissionPage:
page = WebPage('s')
page.get(url)
title = page('tag:h1').text
```

:::tip Tips
    DrissionPage comes with default headers
:::

🔸 Download file

```python
url = 'https://www.baidu.com/img/flexible/logo/pc/result.png'
save_path = r'C:\download'

# Using requests:
r = requests.get(url)
with open(f'{save_path}\\img.png', 'wb') as fd:
   for chunk in r.iter_content():
       fd.write(chunk)

# Using DrissionPage:
page.download(url, save_path, 'img')  # Supports renaming, handles filename conflicts
```

