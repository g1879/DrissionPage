🔦 Simplified Syntax
---

To further simplify the code, the syntax for positioning can be expressed in a simplified form, making the statements shorter and chain operations clearer.

## ✅️ Simplified Locator Syntax

- There are simplified forms for positioning syntax.
- Both pages and element objects have implemented the `__call__()` method, so `page.ele('...')` can be simplified to `page('...')`.
- The search methods all support chain operations.

Example:

```python
# Find elements with tag div
ele = page.ele('tag:div')  # Original syntax
ele = page('t:div')  # Simplified syntax

# Find elements with xpath
ele = page.ele('xpath://xxxxx')  # Original syntax
ele = page('x://xxxxx')  # Simplified syntax

# Find elements with text 'something'
ele = page.ele('text=something')  # Original syntax
ele = page('tx=something')  # Simplified syntax
```

Simplified syntax mapping table

| Original Syntax | Simplified Syntax |         Description         |
|:--------------:|:----------------:|:-----------------------------:|
|     `@id`      |       `#`        |  Represents the id attribute. The simplified syntax only takes effect when the statement is used at the beginning and separately.   |
|    `@class`    |       `.`        | Represents the class attribute. The simplified syntax only takes effect when the statement is used at the beginning and separately. |
|     `text`     |       `tx`       |           Match by text          |
|   `@text()`   |    `@tx()`      |        Match elements by text using @ or @@       |
|      `tag`     |       `t`        |           Match by element tag           |
|     `xpath`    |       `x`        |       Find elements using xpath        |
|      `css`     |       `c`        |    Find elements using css selector    |

---

## ✅️ Simplified Shadow Root

When obtaining the shadow root element of an element, `ele.shadow_root` is commonly used.

Since this property is often used for a large number of chain operations, its name is too long and affects readability. Therefore, it can be simplified as `ele.sr`.

**Example:**

```python
txt = ele.sr('t:div').text
```

---

## ✅️ Simplified Relative Positioning Parameters

When using relative positioning, sometimes it is necessary to get a specific element after the current element, regardless of the type of the element. It is usually written as `ele.next(index=2)`.

However, there is a simplified syntax that can be directly written as `ele.next(2)`.

When the first argument `filter_loc` accepts a number, it will automatically treat it as an index, replacing the `index` parameter. Therefore, the writing can be slightly simplified.

**Example:**

```python
ele2 = ele1.parent(2)
ele2 = ele1.next(2)('tx=xxxxx')
ele2 = ele1.before(2)
# and so on
```

