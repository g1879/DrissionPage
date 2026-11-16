这是一份**可直接用于立项与编码实现**的完整设计方案。它以方案一的强分隔符文法为根基，修补了其词法、XPath 谓词嵌套和 `_check_ele` 一致性漏洞，并融合了方案二的 `Q` Builder、正则匹配 `/=`、`explain()` 调试工具与混合下推执行引擎。

---

# DrissionPage 定位层设计方案（v1.5 融合版）

> **定位**：在不破坏任何现有语法的前提下，为 DrissionPage 增加一套**词法无歧义、顺序无关、可组合、可调试、动静分离**的现代定位层。
>
> **双前端设计**：
> - **静态/交互调试**：`?` 前缀字符串 DSL（如 `tab.ele('?a && .btn && text*=登录')`）
> - **动态/工程代码**：Python `Q` Builder（如 `tab.ele(Q('a') & Q.cls('btn') & Q.text.contains(kw))`）
> - 两者编译为**同一棵不可变 AST**，共享同一套编译、执行、缓存与报错体系。

---

## 0. 核心决策与设计不变量

| 决策项 | 结论 | 说明 |
|---|---|---|
| **兼容策略** | **100% Opt-in** | 旧语法一行不改，零破坏性迁移；字符串以 `?` 开头或传入 `Q` 对象时走新引擎 |
| **逻辑分隔** | **显式运算符强制分隔** | 必须写 `&&`/`\|\|`/`!`/`()`；**严禁**“并排即与”或“空格即与”，彻底消除裸值截断悖论 |
| **保留键与转义** | `tag`、`text`、`owntext` | 永不当作属性名；同名属性用 `@` 转义（`@tag=x`） |
| **文本默认语义** | `text` = 深层文本，`owntext` = 直属文本 | 与 `ele.text` 的直觉层级对齐 |
| **否定机制** | 统一 `!` 前缀 | 不设 `!=` 运算符（写入 `!=` 时报错并提示改写为 `!key=val`） |
| **执行架构** | **XPath 下推 + 本地过滤混合引擎** | 纯 XPath 表达的查询零额外开销；含正则 `/=` 时自动“XPath 缩减候选集 + 本地精筛” |
| **错误处理** | **非法必报 `LocatorError`** | 带字符偏移指针与修改建议，**绝不**静默降级为模糊文本搜索 |

---

## 1. 整体架构

```text
  '?input && type=filter && text/="\\d+"'         Q('input', type='filter') & Q.text.regex(r'\d+')
                    │                                                   │
           词法/递归下降解析（lru_cache）                                 │
                    └───────────────────────┬───────────────────────────┘
                                            ▼
                                  不可变 AST（QueryNode）
                         ┌──────────────────┼──────────────────┐
                         ▼                  ▼                  ▼
                 纯 XPath 表达式？      含本地过滤节点？      相对定位 (_check_ele)
                 (无 /= 等本地算子)      (如 /= 正则)         offset / east / north...
                         │                  │                  │
                         ▼                  ▼                  ▼
                单一 XPath 1.0 查询    Sound Over-Approx     AST.match(ele)
                (CDP / lxml 原生)     XPath 预筛 + 本地精筛   (直接执行布尔树)
```

---

## 2. AST 核心模型

所有前端最终归约到以下 7 种不可变（`frozen=True`）节点，天然支持 `lru_cache` 与结构化打印：

```python
class Op(Enum):
    EQ = '='          # 全等
    CONTAINS = '*='   # 子串包含
    STARTS = '^='     # 前缀
    ENDS = '$='       # 后缀
    WORD = '~='       # 空白分词整词匹配
    REGEX = '/='      # 正则匹配 (re.search)

Node := Tag(op: Op, value: str)                # value='*' 且 op=EQ 表示任意标签
      | Attr(name: str, op: Op | None, value: str | None)  # op=None 表示属性存在性；name='*' 表示任意属性
      | Text(kind: Literal['text', 'owntext'], op: Op, value: str)
      | And(children: tuple[Node, ...])
      | Or(children: tuple[Node, ...])
      | Not(child: Node)
```

**合法性约束（在 AST 构造期校验）**：
* `Tag` 不允许使用 `~=`（分词匹配仅限属性）。
* `Text` 不允许使用 `~=`。
* `op == WORD ('~=')` 时，`value` 不可为空串且不可包含空白字符，否则直接抛出 `LocatorError`。
* `op == REGEX ('/=')` 时，在解析期即调用 `re.compile(value)` 预编译并缓存；非法正则立即抛出 `LocatorError`（而不是等到遍历 DOM 时才崩）。

---

## 3. 字符串查询语法规范（`?` Query DSL）

### 3.1 完整 EBNF 文法

```ebnf
query      := or_expr
or_expr    := and_expr ( ( "||" | "|" ) and_expr )*
and_expr   := unary_expr ( ( "&&" | "&" ) unary_expr )*
unary_expr := "!" unary_expr | "(" or_expr ")" | predicate

predicate  := shorthand
            | "@" ( "*" | attr_key ( oper value )? )
            | key oper value

shorthand  := "#" css_ident
            | "." css_ident
            | "*"
            | tag_word

key        := [A-Za-z_][A-Za-z0-9_:.-]*     (* 覆盖 data_id、xlink:href、v-bind:class 等 *)
attr_key   := key | QUOTED                  (* 支持 @"@click"、@":class" 等前端框架特殊属性名 *)
tag_word   := [A-Za-z][A-Za-z0-9-]*        (* HTML/自定义元素标签名 *)
css_ident  := [A-Za-z0-9_-]+                (* 覆盖 #123、.el-input__inner 等常见类名 *)
oper       := "*=" | "^=" | "$=" | "~=" | "/=" | "="

value      := QUOTED | BARE
QUOTED     := '"' ( '\\' . | [^"\\] )* '"'
            | "'" ( '\\' . | [^'\\] )* "'"
BARE       := [^\s&|()"']+                  (* 遇 空白、&、|、(、)、引号 即结束 *)
```

### 3.2 词法与空白规则

1. **前缀触发**：仅当字符串第 0 个字符为 `?` 时进入本解析器；`?` 之后允许有空白（如 `'? a && b'` 合法）。
2. **空白允许的位置**：`&&`、`||`、`!`、`(`、`)`、`oper` 两侧均可任意加空白。
3. **空白禁止的位置（紧耦合糖）**：`#`、`.`、`@` 与其后的标识符之间**不允许有空白**（`?. btn`、`?@ disabled` 报语法错误），防止阅读歧义。
4. **引号转义**：单双引号内部支持 `\"`、`\'`、`\\`、`\n`、`\t`，其余字符按字面保留。
5. **裸值边界**：
   - `?href*=https://a.com/x?q=1#frag`、?`href*=mailto:a@b.com` 均合法（裸值允许含 `:`、`@`、`.`、`#`、`=`、`?`、`/`）。
   - 若值中包含**空白、括号 `()`、`&`、`|` 或引号**（例如含括号的正则 `?text/="(foo|bar)"`、含空格的值 `?placeholder="搜索 项目名称"`），**必须加引号**；未加引号时解析器会精确报错提示“请加引号”。

### 3.3 谓词与简写一览

| 写法 | 展开为规范 AST | 含义 |
|---|---|---|
| `input` | `Tag(EQ, 'input')` | 标签名简写，位置不限 |
| `*` | `Tag(EQ, '*')` | 任意标签 |
| `#login` | `Attr('id', EQ, 'login')` | `id` 全等 |
| `.el-input__inner` | `Attr('class', WORD, 'el-input__inner')` | `class` 分词匹配（CSS 语义；子串匹配用 `class*=btn`） |
| `type=filter` | `Attr('type', EQ, 'filter')` | 属性全等 |
| `xlink:href^=https://` | `Attr('xlink:href', STARTS, 'https://')` | 带冒号/下划线的属性前缀匹配 |
| `@data-testid` | `Attr('data-testid', None, None)` | 存在该属性（值可为空） |
| `@*` / `!@*` | `Attr('*', None, None)` / `Not(...)` | 存在任意属性 / 没有任何属性 |
| `@tag=x` / `@text=x` | `Attr('tag', EQ, 'x')` | `@` 转义保留键，强制按字面属性名匹配 |
| `@"@click"*=submit` | `Attr('@click', CONTAINS, 'submit')` | 引号转义极端属性名（如 Vue `@click`） |
| `text*=ABC` | `Text('text', CONTAINS, 'ABC')` | 深层文本包含（含子孙） |
| `text/="^\s*登录"` | `Text('text', REGEX, r'^\s*登录')` | 深层文本正则匹配 |
| `owntext=ABC` | `Text('owntext', EQ, 'ABC')` | 仅直属文本节点匹配 |

---

## 4. Python `Q` Builder 规范

专为**变量插值、动态组装、复杂条件复用**设计，编译到完全相同的 AST，彻底免除引号和特殊字符转义烦恼。

### 4.1 两种构造风格（无缝混用）

#### 风格 A：关键字直写（Django 风格，最简短）
```python
from DrissionPage import Q

# 等价于 ?input && type=filter && !id=ad
q = Q('input', type='filter') & ~Q(id='ad')

# 运算符后缀：__contains / __startswith / __endswith / __word / __regex
q = Q('a', text__contains=user_input, href__startswith='https://')
```
* 注：`Q(tag='a')` 与 `Q('a')` 等价；`Q('?a && .btn')`（以 `?` 开头）直接解析字符串为 `Q` 对象。
* 关键字参数中 `tag`、`text`、`owntext` 同样为保留键；含连字符/冒号的属性（如 `data-id`）或同名属性使用风格 B。

#### 风格 B：流式字段代理（覆盖全部特殊属性名与 IDE 自动补全）
```python
# 属性（支持任意特殊属性名：data-testid, xlink:href, tag, @click）
Q.attr('data-testid').exists()
Q.attr('tag').eq('x')
Q.attr('href').regex(r'/item/\d+\.html$')

# 简写与保留字段
Q.tag('div')                      # Q.tag.startswith('h')
Q.id('login')                     # 等价于 #login
Q.cls('btn')                      # 等价于 .btn (WORD 匹配)
Q.text.contains(dynamic_var)      # 深层文本包含（变量含引号/&&/括号也绝对安全）
Q.owntext.eq('基础格式')          # 直属文本节点
```

### 4.2 布尔组合与调试互操作
```python
q = (Q.tag('div') | Q.tag('span')) & Q.cls('btn') & ~Q.attr('disabled').exists()

tab.ele(q)                  # 直接传入 ele / eles / child / next / parent / offset ...
print(repr(q))              # -> Q('?(tag=div || tag=span) && .btn && !@disabled')
print(q.canonical())        # -> '(tag="div" || tag="span") && @class~="btn" && !@disabled'
print(q.explain())          # -> 打印 AST、标准式、Pushdown XPath 与执行策略
```

---

## 5. 语义精确定义

| 表达式 | 匹配定义 | 缺失/大小写语义 |
|---|---|---|
| `Tag(op, v)` | 作用于元素标签名 | **忽略大小写**（HTML 语义）；`value='*'` 恒真 |
| `Attr(n, op, v)` | 作用于 `ele.attrs[n]` | 属性不存在时返回 `False`；因此 `!attr=x` 在**属性缺失时为 `True`** |
| `Attr(n, None)` | `n in ele.attrs` | 区分“不存在”(`!@alt`) 与“存在但为空”(`@alt=""`) |
| `Attr('*', None)` | `len(ele.attrs) > 0` | 是否拥有至少一个属性 |
| `Attr(..., WORD, v)` | 按空白分词后存在一段全等 `v` | 仅限属性；`v` 不可含空白或为空 |
| `Text('text', op, v)` | XPath 路径下为 DOM 后代拼接文本 `string(.)`；本地路径为 `ele.text` | **区分大小写**（正则可通过 `(?i)` 控制） |
| `Text('owntext', op, v)` | 存在至少一个直属文本节点满足 `op(node_text, v)` | **区分大小写**；无直属文本节点时为 `False`，否定后为 `True` |

> **关于 `text` 在 XPath 与本地路径的坦诚边界**：
> 为避免在几千个节点的页面上走 CDP 逐个读取 `.text` 导致灾难性性能退化，纯 XPath 模式下 `text` 直接下推给浏览器原生 XPath `string(.)`；仅当查询包含 `/=`（正则）或走 `offset()` 本地过滤时，才对候选节点读取 `ele.text`（并统一修复旧版 `_check_ele` 在 `and`/`or` 分支混用 `raw_text` 与 `text` 的历史 Bug）。

---

## 6. 编译器与混合执行引擎（核心实现规范）

### 6.1 XPath 1.0 字符串转义与精确编译

1. **安全引号转义 `xpath_literal(s)`**：
   - 无 `"` → `f'"{s}"'`
   - 含 `"` 无 `'` → `f"'{s}'"`
   - 同时含 `"` 与 `'` → `concat("part1", '"', "part2", ...)`（彻底防 XPath 注入与语法崩坏）。

2. **单谓词编译表**（统一编入 `//*[...]` 内部，保证任意布尔嵌套合法）：

| AST 节点 | XPath 1.0 谓词表达 | 关键修正说明 |
|---|---|---|
| `Tag(EQ, '*')` | `true()`（顶层可作为 `//*`） | — |
| `Tag(EQ, v)` | `translate(name(), 'A..Z', 'a..z')="{v.lower()}"` | 兼容 SVG/XML 混合大小写标签 |
| `Tag(CONTAINS, v)` | `contains(translate(name(), 'A..Z', 'a..z'), "{v.lower()}")` | 同上（`^=` / `$=` 同理） |
| `Attr(n, None)` | `@{n}` | 若 `n` 为 `@*` 特殊情况编译为 `@*` |
| `Attr(n, EQ, v)` | `@{n}={lit(v)}` | — |
| `Attr(n, CONTAINS, v)` | `contains(@{n}, {lit(v)})` | — |
| `Attr(n, STARTS, v)` | `starts-with(@{n}, {lit(v)})` | — |
| `Attr(n, ENDS, v)` | `string-length(@{n}) >= {len(v)} and substring(@{n}, string-length(@{n}) - {len(v) - 1}) = {lit(v)}` | 修复 XPath 1.0 无 `ends-with` 与短串越界问题；`v == ""` 时退化为 `@{n}` |
| `Attr(n, WORD, v)` | `contains(concat(" ", normalize-space(@{n}), " "), {lit(" " + v + " ")})` | 标准 CSS 词匹配 |
| `Text('text', ...)` | 将上表中 `@{n}` 替换为 `.` | — |
| `Text('owntext', EQ, v)` | `text()[.={lit(v)}]` | **修复 v1 `/parent::*` 无法参与嵌套的缺陷** |
| `Text('owntext', CONTAINS, v)` | `text()[contains(., {lit(v)})]` | 同上 |
| `Text('owntext', STARTS, v)` | `text()[starts-with(., {lit(v)})]` | 检查**任意**直属文本节点（而非仅首个） |
| `Text('owntext', ENDS, v)` | `text()[string-length(.) >= {len(v)} and substring(., string-length(.) - {len(v) - 1}) = {lit(v)}]` | 同上 |

*(注：若属性名 `n` 含 `@` 等非法 XML QName 字符——如 Vue `@click`——无法直接写 `@n`，则自动视为不可下推节点 `local-only`，交给安全预筛 + 本地 `ele.attrs.get(n)` 精确匹配。)*

### 6.2 混合下推编译（Sound Over-Approximation 规则）

当 AST 包含无法下推到 XPath 1.0 的节点（如 `/=` 正则、或 `@click` 等非标准 QName 属性）时，编译器提取**绝对安全超集（永不漏杀）**的 XPath 预筛表达式 `pushdown(node)`：

```text
pushdown(叶子节点) : 若可编为 XPath -> 返回对应 XPath 片段；否则 -> TRUE_NODE
pushdown(And(xs))  : 过滤掉 TRUE_NODE 后剩余节点做 and 拼接；全为 TRUE_NODE -> TRUE_NODE
pushdown(Or(xs))   : 若任意子项 pushdown 为 TRUE_NODE -> 整体返回 TRUE_NODE；否则 or 拼接
pushdown(Not(x))   : 仅当 x 完全可下推（无任何 local-only 子节点）时返回 not(pushdown(x))；
                     否则必须返回 TRUE_NODE（严禁对超集近似取反！）
```

**执行流程**：
1. 若 `pushdown(ast)` 无本地残留（`pure-xpath`）：直接走现有 XPath 查找通道，**性能 100% 等同原生 XPath**。
2. 若含本地残留（`hybrid`）：用 `//*[pushdown(ast)]` 一次性从 DOM 捞出最小候选集，再按 `ele() / eles()` 语义逐个执行 `ast.match(ele)`，命中 `index` 后立即短路返回（不必读完所有候选元素属性）。

---

## 7. 错误处理与调试体系（WYSIWYG）

### 7.1 `LocatorError`（继承 `ValueError`）

报错统一包含：**出错位置（offset） + `^` 指针行 + 原因 + 修改建议**：

```text
LocatorError: 查询语法错误（位置 14）
  ?tag=input && && type=x
                ^^
原因: '&&' 后缺少条件表达式
建议: 删除多余的 '&&'
```

**内置常见误用（Did-You-Mean）规则表**：

| 用户输入模式 | 精确诊断与提示 |
|---|---|
| `?tag:a` / `?text:ABC` | `无效运算符 ':'；标签名请写 a 或 tag=a，文本包含请写 text*=ABC` |
| `?@@a=1` / `?@\|a=1` | `@@ / @\| 不属于新语法；多条件请用 && 或 \|\| 连接` |
| `?a!=b` | `不支持 != 运算符；否定请统一使用 ! 前缀，如 !a=b` |
| `?div.btn` / `?.btn#id` | `不支持 CSS 式连续简写；每个条件需用 && 连接，如 div && .btn` |
| `?a b`（裸词后跟空格+词） | `位置 3: 'a' 后缺少 &&；若想搜索含空格的文本请写 text*="a b"` |
| `?data_id`（无运算符的带下划线词） | `'data_id' 不是合法标签名；若判断属性存在请加 @ 前缀: @data_id` |
| `?登录`（非 ASCII 裸词） | `'登录' 不是合法标签名；搜索文本请写 text*=登录` |
| `?text/=(a\|b)`（未加引号的特殊字符） | `值中包含括号或 '|' 导致截断；正则或特殊值请用引号包裹: text/="(a\|b)"` |

### 7.2 `explain()` 调试工具与 `NoneElement` 回显

提供公开辅助方法 `DrissionPage.explain_loc(loc)`（以及 `q.explain()`）：

```python
>>> print(explain_loc('?input && .el-input__inner && text/="^\\d+$"'))
```
```text
原始输入: ?input && .el-input__inner && text/="^\d+$"
标准式  : tag="input" && @class~="el-input__inner" && text/="^\d+$"
AST     : And(Tag(EQ, 'input'), Attr('class', WORD, 'el-input__inner'), Text('text', REGEX, '^\\d+$'))
执行模式: hybrid (XPath 预筛 + 本地正则精筛)
预筛XPath: //*[translate(name(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')="input" and contains(concat(" ",normalize-space(@class)," ")," el-input__inner ")]
```

同时，当元素未找到时，`NoneElement` 的提示自动附带 AST 的 `canonical()` 回显：
```text
<NoneElement method=ele(), locator=?buttton, parsed=tag="buttton", index=1, timeout=5>
```
（打错标签名或忘加 `@` 时一眼即破。）

---

## 8. DrissionPage 源码接入清单

保持核心改动高度收敛，集中在以下模块：

| 模块 | 职责与改动内容 |
|---|---|
| `_functions/query_locator.py`（新增） | 词法/语法解析器、`Q` Builder、AST 节点、`explain_loc()`、XPath 编译器与 `ast.match(ele)` 本地求值器 |
| `_functions/locator.py` | 1. `is_str_loc()`：识别 `isinstance(loc, Q)` 或 `loc.startswith('?')`<br>2. `str_to_xpath_loc()` / `get_loc()`：分发 `?` 与 `Q`；`pure-xpath` 返回 `('xpath', xpath)`，`hybrid` 返回 `('query', ast)`<br>3. `locator_to_tuple()`：兼容返回 `('query', ast)` 供相对定位使用 |
| `_elements/base.py` / 查找调度处 | 增加 `by == 'query'` 分支：先用 `ast.pushdown_xpath` 查候选集，再用 `ast.match(ele)` 本地精筛（支持 `index` 短路与 `eles` 收集） |
| `_elements/chromium_element.py` | 1. `_check_ele()`：若收到 `QueryNode` 则直接返回 `ast.match(ele)`；同时顺手修复旧 `loc_data` 中 `and` 用 `raw_text`、`or` 用 `text` 的不一致问题<br>2. `offset()` / `_get_relative_eles()`：定位符校验放行 `?` 与 `Q` |
| `DrissionPage/__init__.py` & `.pyi` | 导出 `Q`、`LocatorError`、`explain_loc`；补全所有 `ele/eles/child/next/...` 参数类型提示 `Union[str, tuple, Q]` |
| `_configs/errors.py` / 语言包 | 录入 `LocatorError` 文案与国际化模板 |

---

## 9. 验收测试矩阵

实现落地必须通过以下 6 类自动化测试：

1. **AST 不变量测试（Property-based / Hypothesis）**：随机生成合法 AST → `canonical()` → 重新 `parse_query()` → 必须得到与原 AST **结构全同**的树。
2. **双前端等价性测试**：任意等价的 `?` 字符串与 `Q` 表达式，编译后必须产生相同的 `AST` 和 `XPath`。
3. **新旧行为等价性测试**：在同一 HTML fixture 上，旧写法（`tag:a@@text():ABC`、`text:基础格式`、`@@tag()=input@@type=filter` 等）与对应新写法在 Chromium 与 Session 模式下返回**完全一致的元素序列**。
4. **混合下推正确性（Soundness）测试**：构造包含 `!(text/="a") && b`、`text/="a" || c` 等反例树，验证 `hybrid` 执行结果与“全量遍历 `//*` 执行 `ast.match()`”结果 100% 相同（零漏杀、零误杀）。
5. **词法与编码地狱测试**：值同时含单双引号 `a'b"c`、`& | ! ( ) ? : = @`、空串 `""`、emoji、中文、非 QName 属性（`@"@click"`）、多文本节点夹杂注释 `<div>a<!--x-->b</div>`。
6. **报错与指针测试**：覆盖所有 Did-You-Mean 规则与语法错误场景，断言 `LocatorError` 的 `offset` 精确指向错误 token，且旧全套回归测试 100% 通过。

---

## 10. 一页速查卡（Cheat Sheet）

```text
── 字符串 DSL（? 前缀）─────────────────────────────────────────────
?input                        标签 input（位置无关；* 表示任意标签）
?#login                       id = login
?.el-input__inner             class 分词匹配 (= class~=el-input__inner)
?type=filter                  属性全等
?type*=fil / ^= / $=          包含 / 开头 / 结尾
?text*=ABC                    深层文本包含（含子孙）
?text/="^\s*登录"             深层文本正则（含 () | 空格需加引号）
?owntext*=ABC                 仅直属文本节点包含
?@data-testid                 存在该属性；?!@data-testid 不存在
?@* / ?!@*                    有任意属性 / 没有任何属性
?@tag=x                       @ 转义保留键（匹配字面属性 tag）
?@"@click"*=submit            引号转义特殊属性名
?input && type=filter         与（顺序随意；别名 &）
?(div || span) && !id=ad      或（别名 |）、非（!）、括号嵌套

── Python Q Builder（动态变量防注入）─────────────────────────────────
Q('input', type='filter')                       # 基础构造
Q('a', text__contains=kw, href__startswith='/') # 关键字后缀
Q.attr('data-testid').exists()                  # 特殊属性名
Q.text.regex(r'\d+') & ~Q.id('ad')              # 流式 + 位运算 (& | ~)
Q.cls('btn') | Q.owntext.eq('确定')              # 简写代理
explain_loc('?...') / q.explain()               # 打印 AST 与下推 XPath
```