⭐ Comparison with selenium
---

The following code achieves the same functionality, comparing the code size of both:

🔸 Using explicit wait to find the first element containing some text.

```python
# Using selenium:
element = WebDriverWait(driver).until(ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "some text")]')))

# Using DrissionPage:
element = page('some text')
```

🔸 Switching to a tab

```python
# Using selenium:
driver.switch_to.window(driver.window_handles[0])

# Using DrissionPage:
tab = page.get_tab(1)
```

🔸 Selecting from a dropdown list by text

```python
# Using selenium:
from selenium.webdriver.support.select import Select
select_element = Select(element)
select_element.select_by_visible_text('text')

# Using DrissionPage:
element.select('text')
```

🔸 Dragging an element

```python
# Using selenium:
ActionChains(driver).drag_and_drop(ele1, ele2).perform()

# Using DrissionPage:
ele1.drag_to(ele2)
```

🔸 Scrolling to the bottom of the window (keeping the horizontal scrollbar unchanged)

```python
# Using selenium:
driver.execute_script("window.scrollTo(document.documentElement.scrollLeft, document.body.scrollHeight);")

# Using DrissionPage:
page.scroll.to_bottom()
```

🔸 Setting headless mode

```python
# Using selenium:
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# Using DrissionPage:
set_headless(True)
```

🔸 Getting the content of a pseudo-element

```python
# Using selenium:
text = webdriver.execute_script('return window.getComputedStyle(arguments[0], "::after").getPropertyValue("content");', element)

# Using DrissionPage:
text = element.pseudo.after
```

🔸 Getting shadow-root

The latest version of selenium can directly get the shadow-root, but the generated ShadowRoot object has very limited features.

```python
# Using selenium:
shadow_element = webdriver.execute_script('return arguments[0].shadowRoot', element)

# Using DrissionPage:
shadow_element = element.shadow_root
```

🔸 Directly getting attributes or text nodes using xpath (returning text)

```python
# Using selenium:
Very complex

# Using DrissionPage:
class_name = element('xpath://div[@id="div_id"]/@class')
text = element('xpath://div[@id="div_id"]/text()[2]')
```

