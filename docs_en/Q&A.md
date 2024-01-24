# ❓ Q&A'
hide:
  - navigation
---

This page collects some frequently asked questions from users during the usage process.

Developers are welcome to contribute by submitting issues, PRs, or writing blog articles and sending the links to the author of this repository.

## ❓ How to use on headless Linux?

**Answer:**

For CentOS, please refer to this article: [Linux deployment instructions](https://blog.csdn.net/sinat_39327967/article/details/132181129?spm=1001.2014.3001.5501)

For Ubuntu, please refer to this article: [The usage of DrissionPage on Ubuntu Linux](https://zhuanlan.zhihu.com/p/674687748)

---

## ❓ Why can't the browser exit headless mode?

> Why does the browser still enter headless mode even if `headless()` is not set in the next run after setting headless before?

**Answer:**

This is because the previously opened browser has not been closed and it is just not visible due to headless mode. The program continues to control it.

To close the browser, you can use the `page.quit()` statement at the end of the program.

You can also set `co.headless(False)`, and the program will automatically close the previous headless browser and start a new one.

Also note that the `page.close()` function closes the current tab, not the browser, unless the browser has only one tab.

---

## ❓ How to disable the popup prompts from the browser, such as whether to save passwords or restore the page?

**Answer:**

When the browser popup prompts appear, you can close them manually. Not closing them will not affect automatic operations. It is also possible to prevent them from being displayed in the code.
Add some browser configuration code to disable the corresponding prompts. You need to add code like this:

```python
co = ChromiumOptions()

# Disable the prompt bubble for "Save Password"
co.set_pref('credentials_enable_service', False)

# Disable the prompt bubble for "Do you want to restore this page? Chrome didn't shut down correctly."
co.set_argument('--hide-crash-restore-bubble')

page = ChromiumPage(co)
```

---

## ❓ When using `.click()`, it reports an error "The element has no position and size". How to solve it?

**Answer:**

It is normal for an element to have no position and size, as many elements do not have them.

At this time, you need to check if there are elements with the same name in the page, and whether the locator is accurate and retrieves another element.

If the element you want to click really has no position, you can force click by using JavaScript, the usage is `.click(by_js=True)`, which can be simplified as `.click('js')`.

---

## ❓ Other automation tools seem to be able to use advanced features of the browser (launch options, user preferences, experimental flags). How can I use them in DrissionPage?

**Answer:**

### Launch Options (arguments)
- Usage reference: [https://g1879.gitee.io/drissionpagedocs/ChromiumPage/browser_opt#-set_argument](https://g1879.gitee.io/drissionpagedocs/ChromiumPage/browser_opt#-set_argument)
- Parameter details: [https://peter.sh/experiments/chromium-command-line-switches/](https://peter.sh/experiments/chromium-command-line-switches/)

### User Preferences (prefs)
- Usage reference: [https://g1879.gitee.io/drissionpagedocs/ChromiumPage/browser_opt#-set_pref](https://g1879.gitee.io/drissionpagedocs/ChromiumPage/browser_opt#-set_pref)
- Parameter details: [https://src.chromium.org/viewvc/chrome/trunk/src/chrome/common/pref_names.cc](https://src.chromium.org/viewvc/chrome/trunk/src/chrome/common/pref_names.cc)

### Experimental Flags (flags)
- Usage reference: [https://g1879.gitee.io/drissionpagedocs/ChromiumPage/browser_opt#-set_flag](https://g1879.gitee.io/drissionpagedocs/ChromiumPage/browser_opt#-set_flag)
- Parameter details: [chrome://flags](chrome://flags)

:::warning Note
    External links are for reference only. Please use any advanced features with caution and only when you have full control, as using these features may result in loss of browser data or compromise security and privacy.

