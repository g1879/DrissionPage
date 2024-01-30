🌠 Multi-threaded Operation of Tabs
---

This example demonstrates how to use multiple threads to simultaneously control multiple tabs of a browser for web scraping.

## ✅️️ Page Analysis

Target URLs:

- https://gitee.com/explore/ai

- https://gitee.com/explore/machine-learning

By pressing `F12`, you can see that the `class` attribute of each title element is `title project-namespace-path`, which can be obtained in batch.

---

## ✅️️ Encoding Idea

Although the list of open source projects on Gitee can be scraped in 's' mode, we will be using the browser for demonstration purposes to showcase multi-tab operations.

The `get_tab()` method of `ChromiumPage` is used to retrieve objects of two tabs for operation by different threads.

---

## ✅️️ Example Code

The following code can be executed directly.

It should be noted that a recorder object is used here, please see [DataRecorder](http://g1879.gitee.io/datarecorder) for details.

```python
from threading import Thread

from DrissionPage import ChromiumPage
from DataRecorder import Recorder


def collect(tab, recorder, title):
    """Method used for web scraping
    :param tab: ChromiumTab object
    :param recorder: Recorder object
    :param title: Category title
    :return: None
    """
    num = 1  # Current page number being scraped
    while True:
        # Traverse all title elements
        for i in tab.eles('.title project-namespace-path'):
            # Obtain the names of all repositories on a certain page and record them in the recorder
            recorder.add_data((title, i.text, num))

        # If there is a next page, click on it
        btn = tab('@rel=next', timeout=2)
        if btn:
            btn.click(by_js=True)
            tab.wait.load_start()
            num += 1

        # Otherwise, scraping is finished
        else:
            break


def main():
    # Create a page object
    page = ChromiumPage()
    # First tab visits the URL
    page.get('https://gitee.com/explore/ai')
    # Get the first tab object
    tab1 = page.get_tab()
    # Create a new tab and visit another URL
    tab2 = page.new_tab('https://gitee.com/explore/machine-learning')
    # Get the second tab object
    tab2 = page.get_tab(tab2)

    # Create a recorder object
    recorder = Recorder('data.csv')

    # Use multiple threads to process multiple pages simultaneously
    Thread(target=collect, args=(tab1, recorder, 'ai')).start()
    Thread(target=collect, args=(tab2, recorder, 'Machine Learning')).start()


if __name__ == '__main__':
    main()
```

---

## ✅️️ Result

The program generates a result file called `data.csv`, with the following content:

```csv
Machine Learning, MindSpore/mindspore, 1
Machine Learning, PaddlePaddle/Paddle, 1
Machine Learning, MindSpore/docs, 1
Machine Learning, scruel/Notes-ML-AndrewNg, 1
Machine Learning, MindSpore/graphengine, 1
Machine Learning, inspur-inna/inna1.0, 1
ai, drinkjava2/人工生命, 1
Machine Learning, MindSpore/course, 1

More content is omitted...
```

---

## ✅️️ Explanation

In this example, the `page` is actually a tab object, which is equivalent to `tab1`.

Creating a `tab1` object in the example is just for better readability, but it can be completely replaced by `page` in the position of `tab1`.

