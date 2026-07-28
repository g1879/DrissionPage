# 四项低风险 Bug 修复详解

本文解释 `tests/known_issues_cost_benefit.md` 中 #1、#2、#4、#6 的根因、调用链、修复选择和回归覆盖。

这四项修复遵循同一边界：不改公开方法签名，不增加依赖，不改变原有合法输入的返回类型，只修正已经存在但中途断掉的参数或数据传递。

| 编号 | 修复点 | 根因 | 最终生效位置 |
| --- | --- | --- | --- |
| #1 | `SessionOptions.add_adapter()` | 绕过了负责延迟初始化的 `adapters` 属性 | `requests.Session.mount()` |
| #2 | `SessionElementsList.texts` | 把合法的字符串文本节点当成元素对象 | `SessionElementsList.texts` 返回值 |
| #4 | `convert_argument()` | 普通 `float` 分支提前截获 CDP 特殊数值 | `Runtime.callFunctionOn.arguments` |
| #6 | `ChromiumTab.post()` | 桥接到 `SessionPage.post()` 时漏传显式 `timeout` | `requests.Session.post(timeout=...)` |

## #1 `SessionOptions.add_adapter()` 在新对象上崩溃

### 调用链

```text
SessionOptions(read_file=False)
  -> __init__(): self._adapters = None
  -> add_adapter(url, adapter)
  -> adapters 属性把 None 延迟初始化为 []
  -> append((url, adapter))
  -> make_session()
  -> requests.Session.mount(url, adapter)
```

相关代码：

- `DrissionPage/_configs/session_options.py:48`：新对象的 `_adapters` 初始值是 `None`。
- `DrissionPage/_configs/session_options.py:225`：`adapters` 属性负责把 `None` 转成空列表。
- `DrissionPage/_configs/session_options.py:231`：`add_adapter()` 添加配置。
- `DrissionPage/_configs/session_options.py:321`：`make_session()` 将配置挂载到真实 `requests.Session`。

### 根因

修复前：

```python
def add_adapter(self, url, adapter):
    self._adapters.append((url, adapter))
    return self
```

`_adapters` 使用 `None` 表示“尚未初始化”。类中已经提供 `adapters` 属性来完成延迟初始化，但 `add_adapter()` 直接访问了底层字段，因此新对象上的第一次调用等价于：

```python
None.append((url, adapter))
```

问题不在 `requests`，也不在 adapter 类型，而是在进入 `requests` 之前配置列表就没有建立。

### 修复

```python
def add_adapter(self, url, adapter):
    self.adapters.append((url, adapter))
    return self
```

只把 `_adapters` 改为 `adapters`。属性读取时会完成：

```python
if self._adapters is None:
    self._adapters = []
```

随后仍然向同一个 `_adapters` 列表追加数据。

### 为什么这样修

1. `adapters` 属性本来就是这个字段的规范化入口，修复复用了现有生命周期。
2. 不把构造函数的 `_adapters = None` 改成 `[]`，避免扩大到初始化、配置导入和 `from_session()` 的状态语义。
3. `add_adapter()` 仍返回 `self`，链式调用不变。
4. adapter 的顺序和 `(url, adapter)` 数据结构不变。
5. `make_session()` 的挂载逻辑不变，修复只是确保它能拿到有效列表。

### 兼容性覆盖

`tests/feature_cases/test_low_risk_bug_fixes.py:36` 覆盖：

- 新对象第一次添加不崩溃；
- 连续添加多个 adapter；
- 返回当前对象，保留链式调用；
- 保留插入顺序；
- `make_session()` 后两个 adapter 都实际出现在 `requests.Session.adapters` 中。

因此测试不只检查“不报错”，还检查配置确实沿完整链路生效。

## #2 `SessionElementsList.texts` 遇到文本节点崩溃

### 调用链

```text
SessionPage.eles()/s_eles() 或 SessionElement.s_eles()
  -> _ele(..., index=None)
  -> _find_elements()
  -> make_session_ele()
  -> lxml.html.HtmlElement.xpath()
  -> HtmlElement 包装为 SessionElement
     字符串文本节点原样保留
  -> SessionElementsList
  -> .texts
```

相关代码：

- `DrissionPage/_pages/session_page.py:128`：多元素查询使用 `index=None`。
- `DrissionPage/_elements/session_element.py:158`：`make_session_ele()` 解析 HTML 并执行定位。
- `DrissionPage/_elements/session_element.py:248`：XPath 由 lxml 执行。
- `DrissionPage/_elements/session_element.py:271`：元素节点包装为 `SessionElement`，其他合法结果原样保留。
- `DrissionPage/_functions/elements.py:42`：统一提取列表项文本。

### 根因

XPath 不只返回元素。以 `xpath://div/node()` 为例，lxml 会返回混合结果：

```python
[
    "leading text",       # 文本节点，str 或 str 子类
    HtmlElement("span"),  # 元素节点
    "trailing text",      # 文本节点，str 或 str 子类
]
```

`make_session_ele()` 的设计已经明确保留这种差异：

```python
r.append(SessionElement(e, page) if isinstance(e, HtmlElement) else e)
```

所以 `SessionElementsList` 合法地可以同时包含 `SessionElement` 和字符串。修复前的 `.texts` 却假定每一项都是元素：

```python
return [t.text for t in self]
```

遍历到文本节点时访问 `str.text`，因此抛出 `AttributeError`。

### 修复

```python
return [t if isinstance(t, str) else t.text for t in self]
```

字符串已经是最终文本，直接返回；元素继续读取原有 `.text` 属性。

### 为什么这样修

1. 修复承认列表现有的混合类型契约，没有修改 XPath 结果或丢弃文本节点。
2. 不把所有项统一执行 `str()`，否则元素会变成对象描述，而不是元素文本。
3. 不在 `make_session_ele()` 中把文本节点包装成新对象，避免引入新类型和扩大所有定位调用的行为面。
4. `isinstance(t, str)` 同时支持普通 `str` 和 lxml 返回的字符串子类。
5. 非字符串项仍按原逻辑访问 `.text`，不会掩盖真正放入了错误对象的问题。

同一模块的筛选逻辑原本就多处使用“字符串直接取值、元素读取属性”的分支，这个修复与现有数据模型一致。

### 兼容性覆盖

`tests/feature_cases/test_low_risk_bug_fixes.py:69` 覆盖：

- 空列表仍返回 `[]`；
- 纯元素列表仍返回元素 `.text`；
- 真实 lxml `node()` 查询产生的“文本 + 元素 + 文本”顺序不变；
- 切片后仍是 `SessionElementsList`，`.texts` 行为不变；
- 继承该属性的 `ChromiumElementsList` 仍保持原有元素行为。

## #4 `convert_argument()` 错误编码 CDP 特殊浮点数

### 调用链

页面和元素共用同一条参数编码链：

```text
ChromiumBase.run_js(...) / ChromiumElement.run_js(...)
  -> _run_js()
  -> chromium_element.run_js()
  -> [convert_argument(arg) for arg in args]
  -> _run_cdp("Runtime.callFunctionOn", arguments=...)
  -> CDP 消息序列化
  -> Chromium Runtime / V8 接收 JavaScript 参数
```

相关代码：

- `DrissionPage/_pages/chromium_base.py:400`：页面级 `run_js()` 入口。
- `DrissionPage/_elements/chromium_element.py:400`：元素级 `run_js()` 入口。
- `DrissionPage/_elements/chromium_element.py:1189`：页面和元素共用的 JS 执行函数。
- `DrissionPage/_elements/chromium_element.py:1226`：调用 `Runtime.callFunctionOn`，每个参数先经过 `convert_argument()`。
- `DrissionPage/_elements/chromium_element.py:1303`：Python 值到 CDP `CallArgument` 的转换。

### CDP 底层契约

`Runtime.callFunctionOn.arguments` 的每一项都是 `Runtime.CallArgument`。CDP 为参数提供三种表示方式：

```text
value                 可正常 JSON 序列化的值
unserializableValue   无法用普通 JSON 值准确表达的原始值
objectId              浏览器运行时中的远程对象引用
```

特殊数字应使用 `unserializableValue`：

| Python 输入 | CDP 参数 | JavaScript 验证 |
| --- | --- | --- |
| `float("inf")` | `{"unserializableValue": "Infinity"}` | `value === Infinity` |
| `float("-inf")` | `{"unserializableValue": "-Infinity"}` | `value === -Infinity` |
| `float("nan")` | `{"unserializableValue": "NaN"}` | `Number.isNaN(value)` |
| `-0.0` | `{"unserializableValue": "-0"}` | `Object.is(value, -0)` |

协议依据：Chrome DevTools Protocol 的 [`Runtime.CallArgument`](https://chromedevtools.github.io/devtools-protocol/tot/Runtime/#type-CallArgument)。测试还会读取当前连接浏览器的 `/json/protocol`，不只依赖在线文档。

### 根因

修复前：

```python
elif isinstance(arg, (int, float, str, bool, dict)):
    return {"value": arg}

from math import inf
if arg == inf:
    return {"unserializableValue": "Infinity"}
elif arg == -inf:
    return {"unserializableValue": "-Infinity"}
```

所有 `float`，包括正负无穷，都会在前面的 `isinstance(..., float)` 分支直接返回。后面的无穷判断对浮点输入实际上不可达。

同时，原代码没有覆盖 `NaN` 和需要保留符号的 `-0.0`，因此没有完整实现 CDP 的特殊数字契约。

### 修复

`float` 被单独提前分类：

```python
elif isinstance(arg, float):
    if isnan(arg):
        return {"unserializableValue": "NaN"}
    elif isinf(arg):
        return {"unserializableValue": "Infinity" if arg > 0 else "-Infinity"}
    elif arg == 0 and copysign(1, arg) < 0:
        return {"unserializableValue": "-0"}
    return {"value": arg}
```

### 为什么这样修

1. `isnan()` 明确识别 `NaN`，不依赖 `NaN != NaN` 这种隐式技巧。
2. `isinf()` 同时覆盖正负无穷，再根据符号选择 CDP token。
3. `-0.0 == 0.0` 为真，普通相等比较无法区分；`copysign()` 可以保留并检测符号位。
4. 有限浮点仍使用 `{"value": arg}`，旧的正常数值路径不变。
5. 整数、字符串、布尔值、字典仍使用原有 `value` 路径。
6. `ChromiumElement` 仍使用原有 `objectId` 路径。
7. 不把特殊数字转换成普通字符串，因为那会让 JavaScript 收到 `"Infinity"`，类型从 number 变成 string。

### 兼容性和真实 CDP 覆盖

`tests/feature_cases/test_low_risk_bug_fixes.py:102` 做纯转换契约测试：

- 四种特殊数字的 CDP 字段和值；
- 普通整数、有限浮点、字符串、布尔值、字典不变；
- 元素 `objectId` 不变；
- 原本不支持的列表仍抛 `TypeError`。

`tests/feature_cases/test_cdp_argument_values.py:16` 做真实 Chromium 测试：

1. 调用 `Browser.getVersion` 记录实际浏览器产品版本；
2. 读取该浏览器自己的 `/json/protocol`；
3. 确认 `Runtime.CallArgument` 真的包含 `unserializableValue`；
4. 通过公开的 `tab.run_js()` 走完整调用链；
5. 在 V8 中分别用严格比较、`Number.isNaN()` 和 `Object.is()` 验证收到的值；
6. 额外验证普通字典参数仍能正常读取。

本次实测浏览器为 Chrome `150.0.7871.129`。这证明的不只是 Python 字典长得正确，而是协议参数确实被浏览器按预期还原。

## #6 `ChromiumTab.post(timeout=...)` 丢失显式超时

### 调用链

```text
ChromiumTab.post(url, timeout=用户值)
  -> d 模式时 cookies_to_session()
  -> _mode_obj.post(..., timeout=用户值)
  -> SessionPage.post()
  -> _s_connect(mode="post")
  -> _make_response()
  -> requests.Session.post(url, timeout=用户值)
```

`ChromiumTab` 的继承顺序是：

```text
ChromiumTab -> ChromiumBase -> SessionPage -> BasePage
```

POST 始终走 requests 会话：浏览器模式先同步 cookie，然后通过 `_mode_obj` 找到 `SessionPage.post()`；会话模式也直接使用 `SessionPage` 路径。

相关代码：

- `DrissionPage/_pages/chromium_tab.py:21`：多继承关系。
- `DrissionPage/_pages/chromium_tab.py:40`：默认浏览器模式的 `_mode_obj`。
- `DrissionPage/_pages/chromium_tab.py:134`：`ChromiumTab.post()` 桥接入口。
- `DrissionPage/_pages/chromium_tab.py:154`：模式切换时更新 `_mode_obj`。
- `DrissionPage/_pages/session_page.py:119`：requests POST 包装。
- `DrissionPage/_pages/session_page.py:169`：连接和 `NavResult` 组装。
- `DrissionPage/_pages/session_page.py:187`：最终调用 `requests.Session.post()`。

### 根因

修复前只有未传超时时才写入 `kwargs`：

```python
if timeout is None:
    kwargs["timeout"] = self.timeouts.page_load
```

当调用者传入 `timeout=3` 时，这个参数已经被 Python 绑定到局部变量 `timeout`，不会留在 `kwargs` 中。条件又因为 `timeout` 不是 `None` 而跳过，后续调用也没有显式传递它：

```python
self._mode_obj.post(..., **kwargs)
```

于是 `SessionPage.post()` 收到的仍是默认 `timeout=None`，再用自己的默认超时覆盖它。用户给出的 `3` 在 `ChromiumTab.post()` 这一层被截断。

### 修复

```python
kwargs["timeout"] = self.timeouts.page_load if timeout is None else timeout
```

无论使用默认值还是显式值，都把最终超时放入向下游传递的 `kwargs`。

### 为什么这样修

1. 修复点位于参数丢失的桥接层，不修改 `SessionPage` 或 requests 行为。
2. `timeout is None` 时继续使用原有的 `page_load` 默认值，默认行为不变。
3. 使用 `is None` 而不是真假判断，所以显式 `timeout=0` 不会被替换。
4. `retry`、`interval`、`raise_err` 和其余请求参数仍按原方式传递。
5. d 模式下的 cookie 同步顺序不变。
6. 返回值仍是下游生成的 `NavResult`，没有改公开返回契约。

### 兼容性覆盖

`tests/feature_cases/test_low_risk_bug_fixes.py:147` 的委托层测试覆盖：

- 显式 `timeout=3` 原样转发；
- 未传值仍使用 `page_load` 默认超时；
- 显式 `timeout=0` 不被当成未传值；
- `retry`、`interval`、`raise_err` 和 `data` 不丢失；
- 下游返回值原样返回；
- d 模式仍先同步 cookie。

`tests/feature_cases/test_low_risk_bug_fixes.py:180` 还启动本地慢速 HTTP 服务：

```text
服务端延迟 1 秒
ChromiumTab.post(timeout=0.1, retry=0)
```

测试确认请求在慢响应前结束，并返回 falsey `NavResult`。这证明 timeout 不只到达了 mock，而是最终到达 requests 并产生真实超时行为。

## 为什么这四项适合低风险修复

### 公开 API 不变

四项修复都没有修改：

- 类名、方法名和导入路径；
- 参数名称、默认值和位置；
- `.pyi` 中的公开签名；
- 正常输入的返回类型；
- 外部依赖。

因此不需要同步类型声明，也不需要在根 README 中宣布新 API。

### 修改位置就是数据断点

每项修改都落在实际丢失信息的位置：

- #1：初始化入口被绕过；
- #2：混合节点读取时类型假设错误；
- #4：CDP 参数编码分支顺序错误；
- #6：跨类委托时参数漏传。

没有为了修一个点重写上游解析器、下游 requests/CDP 驱动或公共对象模型。

### 回归测试同时锁定旧行为

测试不只覆盖新失败样例，也锁定相邻旧契约：

- 空值、默认值和普通值；
- 重复调用和链式返回；
- 顺序、切片和继承行为；
- 其他参数和返回值转发；
- 不支持输入仍按原方式报错；
- mock/纯函数检查之外的 requests 与真实 Chromium 端到端结果。

## 验证结果

当前改动已完成以下验证：

| 验证 | 结果 |
| --- | --- |
| 纯契约定向测试 | 通过 |
| stable 无浏览器套件 | `7/7` 通过 |
| stable 真实 Chromium 套件 | `24/24` 通过 |
| CDP runtime schema + V8 实参 | Chrome `150.0.7871.129` 通过 |
| `compileall` | 通过 |
| Ruff（忽略仓库既有 `E722`） | 通过 |
| `git diff --check` | 通过 |

Mypy 当前不能作为这次修复的发布门禁：仓库基线已有 28 个文件共 505 个错误，这些错误不是本次四项修改引入的。
