⭐ Get Element Attribute
---

```python
# Continuing from previous code
foot = page.ele('#footer-left')  # Find element by id
first_col = foot.ele('css:>div')  # Find element within the subordinates using css selector (the first one)
lnk = first_col.ele('text:命令学')  # Find element using text content
text = lnk.text  # Get element text
href = lnk.attr('href')  # Get element attribute value

print(text, href, '\n')

# Concise chaining mode
text = page('@id:footer-left')('css:>div')('text:命令学').text
print(text)
```

**Output:**

```shell
Learn Git Command https://oschina.gitee.io/learn-git-branching/

Learn Git Command
```

