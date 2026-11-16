# -*- coding: utf-8 -*-
"""Feature: 现代定位层（`?` DSL + Q Builder + 混合下推引擎）契约测试。

覆盖 docs/final-syntax.md 第 9 节验收矩阵中无需浏览器的部分：
1. AST 不变量（canonical / to_query 往返结构全同）
2. 双前端等价性（? 字符串与 Q 表达式产生相同 AST 与 XPath）
3. 新旧行为等价性（Session 模式同一 HTML fixture）
4. 混合下推正确性（Soundness：hybrid 结果与全量遍历 100% 一致）
5. 词法与编码地狱（引号、emoji、中文、非 QName 属性、注释夹杂文本）
6. 报错与指针（LocatorError 的 offset 与 Did-You-Mean 提示）
"""
from __future__ import annotations

from random import Random

from lxml.html import fromstring

from DrissionPage import Q, LocatorError, explain_loc
from DrissionPage._elements.session_element import make_session_ele
from DrissionPage._functions.locator import get_loc, is_query_loc
from DrissionPage._functions.query_locator import (AndNode, AttrNode, NotNode, Op, OrNode, TagNode, TextNode,
                                                   canonical, is_pure_xpath, parse_query, to_query, to_xpath)

from support import assert_equal, assert_in, assert_true

FEATURE_ID = "query_locator"
REQUIRES_BROWSER = False

HTML = """
<html><body>
<div id="header">
  <input type="filter" class="el-input__inner" placeholder="搜索项目名称"/>
  <input type="text" class="a b"/>
</div>
<a id="l1" href="/item/123.html" class="btn link">登录ABC</a>
<a id="l2" href="/other">text only owntest</a>
<div id="mix">a<!--comment-->b<span>deep</span>tail</div>
<div id="btns"><button class="btn primary" disabled>Btn1</button><button class="btn">Btn2</button></div>
<div data-testid="x" :class="submit-bar" @click="submit()">vue</div>
<p id="quotes">it's "quoted" &amp; (paren)</p>
<p id="emoji">🎉party🎉</p>
</body></html>
"""


def run(ctx):
    test_parse_contracts()
    test_q_builder_contracts()
    test_roundtrip_invariants()
    test_dual_frontend_equivalence()
    test_old_new_equivalence()
    test_session_find_semantics()
    test_hybrid_soundness()
    test_lexical_hell()
    test_errors_and_pointers()
    test_get_loc_dispatch()


def _ids(eles):
    return [e.attr("id") or e.tag for e in eles]


def test_parse_contracts():
    cases = {
        "?input": TagNode(Op.EQ, "input"),
        "?input && type=filter": AndNode((TagNode(Op.EQ, "input"), AttrNode("type", Op.EQ, "filter"))),
        "?#login": AttrNode("id", Op.EQ, "login"),
        "?.el-input__inner": AttrNode("class", Op.WORD, "el-input__inner"),
        "?*": TagNode(Op.EQ, "*"),
        "?@data-testid": AttrNode("data-testid", None, None),
        "?@*": AttrNode("*", None, None),
        "?@tag=x": AttrNode("tag", Op.EQ, "x"),
        '?@"@click"*=submit': AttrNode("@click", Op.CONTAINS, "submit"),
        "?text*=ABC": TextNode("text", Op.CONTAINS, "ABC"),
        "?owntext=ABC": TextNode("owntext", Op.EQ, "ABC"),
        "?xlink:href^=https://": AttrNode("xlink:href", Op.STARTS, "https://"),
        "?href*=https://a.com/x?q=1#frag": AttrNode("href", Op.CONTAINS, "https://a.com/x?q=1#frag"),
        "?(div || span) && !id=ad": AndNode((OrNode((TagNode(Op.EQ, "div"), TagNode(Op.EQ, "span"))),
                                             NotNode(AttrNode("id", Op.EQ, "ad")))),
        "?(a && b) && c": AndNode((AndNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))), TagNode(Op.EQ, "c"))),
        "? a && b": AndNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))),
        "?a & b": AndNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))),
        "?a | b": OrNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))),
        "?(a)": TagNode(Op.EQ, "a"),
        "?(a || b)": OrNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))),
        "?(a && b) || c": OrNode((AndNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))), TagNode(Op.EQ, "c"))),
        "?(a || b) && c": AndNode((OrNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))), TagNode(Op.EQ, "c"))),
        "?(a || b) || c": OrNode((OrNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))), TagNode(Op.EQ, "c"))),
        "?(a && b) && c && d": AndNode((AndNode((TagNode(Op.EQ, "a"), TagNode(Op.EQ, "b"))),
                                        TagNode(Op.EQ, "c"), TagNode(Op.EQ, "d"))),
    }
    for text, expect in cases.items():
        if expect is None:
            continue
        assert_equal(parse_query(text), expect, f"parse {text}")

    # 裸词含 ':' 且非旧语法前缀 → 通用提示（旧前缀提示在 errors 测试中覆盖）
    try:
        parse_query("?mailto:a@b.com")
        raise AssertionError("?mailto:a@b.com should raise")
    except LocatorError as e:
        assert_in("xlink:href", str(e), "colon-word should hint attr-with-value form")

    # 属性省略值 / 空串 / 运算符两侧空白
    assert_equal(parse_query('?type = "filter"'), parse_query("?type=filter"))
    assert_equal(parse_query('?@alt=""'), AttrNode("alt", Op.EQ, ""))
    # 引号转义
    assert_equal(parse_query('''?x="a\\"b"'''), AttrNode("x", Op.EQ, 'a"b'))
    assert_equal(parse_query('''?x='a\\'b' '''), AttrNode("x", Op.EQ, "a'b"))
    assert_equal(parse_query(r'?text/="\d+"'), TextNode("text", Op.REGEX, r"\d+"))
    assert_equal(parse_query('?text/="\\n"'), TextNode("text", Op.REGEX, "\n"))


def test_q_builder_contracts():
    # 风格 A
    assert_equal(Q("input", type="filter").ast,
                 AndNode((TagNode(Op.EQ, "input"), AttrNode("type", Op.EQ, "filter"))))
    assert_equal(Q("a", text__contains="登录", href__startswith="https://").ast,
                 AndNode((TagNode(Op.EQ, "a"), TextNode("text", Op.CONTAINS, "登录"),
                          AttrNode("href", Op.STARTS, "https://"))))
    assert_equal(Q(tag="a").ast, Q("a").ast)

    # 风格 B
    assert_equal(Q.attr("data-testid").exists().ast, AttrNode("data-testid", None, None))
    assert_equal(Q.attr("tag").eq("x").ast, AttrNode("tag", Op.EQ, "x"))
    assert_equal(Q.attr("href").regex(r"/item/\d+").ast, AttrNode("href", Op.REGEX, r"/item/\d+"))
    assert_equal(Q.tag.startswith("h").ast, TagNode(Op.STARTS, "h"))
    assert_equal(Q.id("login").ast, AttrNode("id", Op.EQ, "login"))
    assert_equal(Q.cls("btn").ast, AttrNode("class", Op.WORD, "btn"))
    assert_equal(Q.owntext.eq("基础格式").ast, TextNode("owntext", Op.EQ, "基础格式"))

    # Q('?...') 直接解析字符串
    assert_equal(Q("?a && .btn").ast, parse_query("?a && .btn"))

    # 布尔组合（同类型扁平化）与 repr / canonical
    q = (Q.tag("div") | Q.tag("span")) & Q.cls("btn") & ~Q.attr("disabled").exists()
    assert_equal(q.canonical(), '(tag="div" || tag="span") && @class~="btn" && !@disabled')
    assert_equal(repr(q), 'Q(\'?(div || span) && .btn && !@disabled\')')

    # Word 匹配限制
    for build in (lambda: Q(tag__word="a"), lambda: Q(text__word="a"), lambda: Q.owntext.word("a")):
        try:
            build()
            raise AssertionError("word match on tag/text should raise")
        except LocatorError:
            pass

    # WORD 值含空白 → 构造期报错
    try:
        Q(class__word="a b")
        raise AssertionError("word value with space should raise")
    except LocatorError:
        pass

    # 非法正则 → 构造期报错（而非遍历 DOM 时）
    try:
        Q.text.regex("[unclosed")
        raise AssertionError("bad regex should raise at build time")
    except LocatorError:
        pass

    # explain 输出包含关键行
    text = explain_loc('?input && .el-input__inner && text/="^\\d+$"')
    for key in ("tag=\"input\"", "@class~=\"el-input__inner\"", "hybrid", "//*"):
        assert_in(key, text, "explain output")
    assert_in("pure-xpath", Q("input", type="filter").explain(), "explain pure strategy")


def test_roundtrip_invariants():
    corpus = [
        "?input", "?#a1", "?.b_2-c", "?*", "?@x", "?@*", "?@tag=x", '?@"@click"',
        "?tag=div", "?tag*=di", "?text=x", "?owntext^=x", "?a=1", "?a*=1", "?a^=1", "?a$=1", "?a~=1",
        '?text/="\\d+"', "?x:y=1", "?x-y=1", "?x_y=1",
        "?a && b", "?a || b", "?!a", "?(a || b) && !c=1", "?a && (b || c)",
        "?(a && b) || (c && d)", "?(a && b) && c", "?!(a || b)",
        '?v="a b"', "?v=\"it's\"", '?v="\\n\\t\\\\\\\\"',
        "?href*=https://a.com/x?q=1#frag", "?placeholder=搜索项目名称",
        "?text*=🎉中文", '?@"v-bind:class"*=x',
    ]
    for text in corpus:
        ast = parse_query(text)
        assert_equal(parse_query("?" + ast.canonical()), ast, f"canonical roundtrip of {text}")
        assert_equal(parse_query(ast.to_query()), ast, f"to_query roundtrip of {text}")

    # 随机生成 AST（确定性种子），验证 canonical 往返结构全同
    rng = Random(20260101)
    leaves = [
        lambda: TagNode(Op.EQ, rng.choice(["div", "input", "a"])),
        lambda: TagNode(rng.choice([Op.CONTAINS, Op.STARTS, Op.ENDS]), rng.choice(["d", "in", "pa"])),
        lambda: AttrNode(rng.choice(["id", "class", "type", "data-x"]), Op.EQ, rng.choice(["x", "y z", 'a"b'])),
        lambda: AttrNode(rng.choice(["id", "class"]), None, None),
        lambda: AttrNode("class", Op.WORD, rng.choice(["btn", "card"])),
        lambda: AttrNode("href", Op.REGEX, rng.choice([r"\d+", "a|b"])),
        lambda: TextNode(rng.choice(["text", "owntext"]), rng.choice([Op.EQ, Op.CONTAINS]), rng.choice(["登", "a b"])),
    ]

    def gen(depth):
        if depth == 0 or rng.random() < 0.4:
            return rng.choice(leaves)()
        r = rng.random()
        if r < 0.15:
            return NotNode(gen(depth - 1))
        cls = AndNode if r < 0.6 else OrNode
        return cls(tuple(gen(depth - 1) for _ in range(rng.randint(2, 3))))

    for i in range(300):
        ast = gen(3)
        assert_equal(parse_query("?" + ast.canonical()), ast, f"random canonical roundtrip #{i}")
        assert_equal(parse_query(ast.to_query()), ast, f"random to_query roundtrip #{i}")


def test_dual_frontend_equivalence():
    pairs = [
        ("?input && type=filter && !id=ad", lambda: Q("input", type="filter") & ~Q(id="ad")),
        ("?(div || span) && .btn && !@disabled",
         lambda: (Q.tag("div") | Q.tag("span")) & Q.cls("btn") & ~Q.attr("disabled").exists()),
        (r'?text/="\d+"', lambda: Q.text.regex(r"\d+")),
        ('?owntext="基础格式"', lambda: Q.owntext.eq("基础格式")),
        ("?a && b && c", lambda: Q.tag("a") & Q.tag("b") & Q.tag("c")),
        ("?a || b || c", lambda: Q.tag("a") | Q.tag("b") | Q.tag("c")),
        ("?!@alt && x^=y", lambda: ~Q.attr("alt").exists() & Q.attr("x").startswith("y")),
        ('?@href$=".html"', lambda: Q.attr("href").endswith(".html")),
        ("?tag^=h && .btn", lambda: Q.tag.startswith("h") & Q.cls("btn")),
    ]
    for text, build in pairs:
        q = build()
        assert_equal(parse_query(text), q.ast, f"dual-frontend AST of {text}")
        assert_equal(to_xpath(parse_query(text)), q.xpath(), f"dual-frontend XPath of {text}")


def test_old_new_equivalence():
    pairs = [
        ("tag:a@@text():ABC", "?a && text*=ABC"),
        ("text:基础格式", '?text*=基础格式'),
        ("@@tag()=input@@type=filter", "?input && type=filter"),
        ("tag:input@type=filter", "?input && type=filter"),
 ("t:input", "?input"),
        ("#:main", "?#main"),
        (".:btn", "?class~=btn"),
        ("@type=filter", "?type=filter"),
        ("@@class:btn@@tag()=button", "?button && .btn"),
        ("text=Btn1", "?owntext=Btn1"),
        ("@!disabled", "?!@disabled"),
    ]
    for old, new in pairs:
        got_old = _ids(make_session_ele(HTML, old, index=None))
        got_new = _ids(make_session_ele(HTML, new, index=None))
        assert_equal(got_new, got_old, f"old {old!r} vs new {new!r}")

    # 单个元素与 index 语义一致
    assert_equal(make_session_ele(HTML, "@@tag()=input@@type=filter").attr("placeholder"),
                 make_session_ele(HTML, "?input && type=filter").attr("placeholder"))
    assert_equal(_ids(make_session_ele(HTML, "css:button", index=None)),
                 _ids(make_session_ele(HTML, "?button", index=None)))


def test_session_find_semantics():
    # deep text 与 owntext 的层级差异
    deep = _ids(make_session_ele(HTML, "?text*=deep", index=None))
    own = _ids(make_session_ele(HTML, "?owntext*=deep", index=None))
    assert_in("mix", deep, "deep text should match ancestor")
    assert_in("span", deep, "deep text should match node itself")
    assert_true("mix" not in own and "span" in own, f"owntext only direct nodes: {own}")

    # 注释夹杂的多文本节点
    assert_true(make_session_ele(HTML, "?owntext=b", index=None), "owntext=b should hit #mix")
    assert_true(make_session_ele(HTML, "?text*=ab", index=None), "text*=ab should hit #mix")

    # 正则 hybrid
    assert_equal(_ids(make_session_ele(HTML, r'?a && href/="/item/\d+\.html$"', index=None)), ["l1"])

    # 非 QName 属性走本地精筛（lxml 会丢弃 '@click'、'v-bind:class' 这类属性名，用 ':class' 覆盖 session 路径）
    assert_equal(_ids(make_session_ele(HTML, '?@":class"*=submit', index=None)), ["div"])

    # index 语义：1 基、负数从后数、越界返回 NoneElement
    assert_equal(make_session_ele(HTML, "?button && .btn", index=2).text, "Btn2")
    assert_equal(make_session_ele(HTML, "?button && .btn", index=-1).text, "Btn2")
    assert_true(make_session_ele(HTML, "?button && .btn", index=9) == None, "index out of range")
    # NoneElement 回显 parsed 标准式
    ne = make_session_ele(HTML, "?buttton", index=1)
    assert_in('parsed=tag="buttton"', repr(ne), "NoneElement repr should include parsed canonical")

    # 属性缺失语义：!attr=x 在属性缺失时为 True
    nos = _ids(make_session_ele(HTML, "?a && !target=_blank", index=None))
    assert_equal(nos, ["l1", "l2"], "!attr should treat missing attr as no-match")
    # 存在性 vs 存在但为空
    assert_true(not list(make_session_ele(HTML, '?@alt=""', index=None)), "no element has alt=\"\"")


def test_hybrid_soundness():
    root = fromstring(HTML)
    all_eles = root.xpath(".//*")   # 与引擎 session 路径同域（.//* 不含上下文元素自身，与旧语法一致）
    queries = [
        '?!(text/="deep") && @class~=btn',
        '?text/="deep" || @id=mix',
        '?owntext/="^[ab]$"',
        r'?href/="\d+" && tag=a',
        '?!@* && text*=vue',
        '?(@id^=l || @id$=x) && !@disabled',
        '?!(@id/= "^l\\d") && tag=a',
        '?text/="paren" && !@class',
        r'?@href/="123" || @placeholder/="搜索"',
    ]
    for text in queries:
        ast = parse_query(text)
        hybrid = [e for e in root.xpath(ast.xpath(relative=True)) if ast.match(e)]
        brute = [e for e in all_eles if ast.match(e)]
        assert_equal(hybrid, brute, f"soundness of {text} (zero missed / zero extra)")

    # 下推规则：Not 含本地节点时必须退化为 true()（严禁对超集取反）
    frag = parse_query('?!(@id/= "^l\\d") && tag=a')
    assert_equal(to_xpath(frag), '//*[name()="a"]'.replace('name()="a"',
                   'translate(name(),\'ABCDEFGHIJKLMNOPQRSTUVWXYZ\',\'abcdefghijklmnopqrstuvwxyz\')="a"'),
                 "not-with-local must collapse to tag-only prefilter")
    # Or 含本地节点时整体 true()
    assert_equal(to_xpath(parse_query('?text/="a" || c=1')), "//*", "or-with-local must be true()")


def test_lexical_hell():
    # 值同时含单双引号（DSL 需加引号转义；Q Builder 天然免转义；HTML 侧用实体编码构造）
    q = Q.attr("v").eq('a"b\'c')
    hole = '<div v="a&quot;b&#39;c">x</div><div v="no">y</div>'
    got = make_session_ele(hole, '?@v="a\\"b\'c"', index=None)
    assert_equal(len(got), 1, "single+double quote value via DSL")
    assert_equal(make_session_ele(hole, q, index=None)[0].text, "x")

    # 特殊字符集合
    for v in ["&", "|", "(", ")", "!", "?", ":", "=", "@", "#", "", "🎉", "中文 中文"]:
        html = f"<div data-x='HOLE'>mark</div>"
        ast_q = Q.attr("data-x").eq(v)
        got = make_session_ele(html, ast_q, index=None)
        assert_equal(len(got), 0 if v != "HOLE" else 1, f"attr value {v!r}")

    # emoji 与中文文本（text 为深层文本：祖先元素同样命中）
    assert_equal(_ids(make_session_ele(HTML, "?owntext*=🎉", index=None)), ["emoji"])
    assert_in("emoji", _ids(make_session_ele(HTML, "?text*=🎉", index=None)), "deep text matches leaf")
    assert_in("l1", _ids(make_session_ele(HTML, "?text*=登录", index=None)), "chinese text")

    # 空串文本包含 → 恒真（每个元素都有文本内容）
    assert_true(len(make_session_ele(HTML, '?text*=""', index=None)) > 0, "contains empty string matches all")

    # 裸值允许的字符：://?#@=
    assert_equal(len(make_session_ele('<a href="https://a.com/x?q=1#f">t</a>',
                                      "?href*=https://a.com/x?q=1#f", index=None)), 1)

    # 未加引号的特殊值 → 精确报错提示加引号
    try:
        parse_query("?text/=(a|b)")
        raise AssertionError("unquoted paren value should raise")
    except LocatorError as e:
        assert_in("引号", str(e), "quote hint")


def test_errors_and_pointers():
    import re as _re
    cases = [
        ("?tag:a", "无效运算符"),
        ("?@@a=1", "不属于新语法"),
        ("?a!=b", "不支持 !="),
        ("?div.btn", "CSS 式连续简写"),
        ("?.btn#id", "CSS 式连续简写"),
        ("?a b", "缺少 &&"),
        ("?data_id", "@"),
        ("?登录", "text*="),
        ("?text/=(a|b)", "引号"),
        ("?input && && type=x", "缺少条件"),
        ("?", "不能为空"),
        ("?(a && b", '")"'),
        ("?. btn", "不能有空格"),
        ("?@ disabled", "不能有空格"),
        ("?a=", "缺少匹配值"),
        ('?x="unclosed', "未闭合"),
        ("?tag~=div", '"~="'),
    ]
    for text, needle in cases:
        try:
            parse_query(text)
            raise AssertionError(f"{text!r} should raise LocatorError")
        except LocatorError as e:
            msg = str(e)
            assert_in(needle, msg, f"error message of {text!r}")
            assert_true(_re.search(r"(位置|offset) \d+", msg), f"offset in error of {text!r}")
            assert_in("^", msg, f"caret pointer in error of {text!r}")

    # 指针位置精确：'?' 后第 3 个字符处
    msg = str(_raise_of("?a b"))
    assert_in("(位置 3", msg.replace("（", "(").replace("）", ")"), "pointer offset of '?a b'")


def _raise_of(text):
    try:
        parse_query(text)
        raise AssertionError(f"{text!r} should raise")
    except LocatorError as e:
        return e


def test_get_loc_dispatch():
    # pure-xpath 查询 → ('xpath', ...)
    mode, loc = get_loc("?input && type=filter")
    assert_equal(mode, "xpath", "pure query dispatch")
    assert_true(loc.startswith("//*[") or loc == "//*", "pure query xpath")
    # hybrid 查询 → ('query', ast)
    mode, loc = get_loc("?text/='\\d+'")
    assert_equal(mode, "query", "hybrid query dispatch")
    assert_equal(loc, parse_query("?text/='\\d+'"), "hybrid query carries ast")
    # Q 对象同样分发
    assert_equal(get_loc(Q("input"))[0], "xpath")
    assert_equal(get_loc(Q.text.regex(r"\d"))[0], "query")
    # 识别函数
    assert_true(is_query_loc("?a") and is_query_loc(Q("a")), "is_query_loc")
    assert_true(not is_query_loc("tag:div"), "old syntax is not query loc")
    # 旧语法不受影响
    assert_equal(get_loc("tag:div"), ("xpath", '//*[name()="div"]'))
    # 保留键与 @ 转义
    assert_equal(parse_query("?@tag=x"), AttrNode("tag", Op.EQ, "x"), "@ escapes reserved key")
    # 纯字符串不会被误判为查询
    assert_equal(get_loc("div")[0], "any", "plain text still any mode")


# 确保 to_query / canonical / to_xpath 模块级函数可导入使用
_ = (to_query, canonical)
