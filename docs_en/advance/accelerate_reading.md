⚙️ Speed Up Data Retrieval
---

This section demonstrates a black technology that can greatly accelerate data collection on web pages.

## ✅️️ Example

Let's take a relatively large webpage as an example, such as the homepage of [https://www.163.com](https://www.163.com).

Let's count the number of `<a>` elements within this webpage:

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://www.163.com')
print(len(page('t:body').eles('t:a')))
```

**Output:**

```shell
1613
```

Hmm, that's quite a number, indicating an obvious effect.

Suppose our task is now to print the text of all the links. The common approach is to iterate through all the elements and print them.

Here we introduce a timing tool written by the library author, which can measure the execution time of a code segment. You can also use other methods to measure time.

```python
from DrissionPage import ChromiumPage
from TimePinner import Pinner  # Import the timing tool

pinner = Pinner()  # Create a timer object
page = ChromiumPage()
page.get('https://www.163.com')

pinner.pin()  # Mark the start of recording

# Get all link objects and iterate through them
links = page('t:body').eles('t:a')
for lnk in links:
    print(lnk.text)

pinner.pin('Time Elapsed')  # Record and print the time elapsed
```

**Output:**

```shell
0.0

网络大过年_网易政务_网易网
网易首页
...middle part omitted...
不良信息举报 Complaint Center
廉正举报
Time Elapsed: 4.057772700001806
```

It took 4 seconds.

Now, let's make a small modification.

Change `page('t:body').eles('t:a')` to `page('t:body').s_eles('t:a')` and execute it again.

```python
from DrissionPage import ChromiumPage
from TimePinner import Pinner  # Import the timing tool

pinner = Pinner()  # Create a timer object
page = ChromiumPage()
page.get('https://www.163.com')

pinner.pin()  # Mark the start of recording

# Get all link objects and iterate through them
links = page('t:body').s_eles('t:a')
for lnk in links:
    print(lnk.text)

pinner.pin('Time Elapsed')  # Record and print the time elapsed
```

**Output:**

```shell
0.0

网络大过年_网易政务_网易网
网易首页
...middle part omitted...
不良信息举报 Complaint Center
廉正举报
Time Elapsed: 0.2797656000002462
```

Isn't it magical? The data collection time that used to be 4 seconds now only takes 0.28 seconds.

---

## ✅️️ Interpretation

The difference between `s_eles()` and `eles()` is that the former converts the entire page or dynamic element into a static element, and then retrieves sub-elements or information within it. Because static elements are plain text and do not have attributes, interactions, or other resource-consuming components, their execution speed is very fast.

The author once collected a very complex webpage, which took 30 seconds using dynamic elements, but it only took 0.X seconds after converting them into static elements, demonstrating a significant acceleration effect.

We can obtain content containers within the page (such as `<body>` in the example) and convert them into static elements to retrieve information within them.

Of course, static elements do not have interactive functions. They are only copies and do not affect the original dynamic elements.

