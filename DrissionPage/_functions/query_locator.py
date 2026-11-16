# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.

DrissionPage 现代定位层（v1.5 融合版）：
* `?` 前缀字符串 DSL（静态/交互调试）
* `Q` Builder（动态/工程代码）
两者编译到同一棵不可变 AST，共享编译、执行、缓存与报错体系。
规范见 docs/final-syntax.md。
"""
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from re import compile as re_compile, error as re_error, match as re_match

from ..errors import LocatorError
from .settings import Settings as _S

__all__ = ['Q', 'Op', 'QueryError', 'TagNode', 'AttrNode', 'TextNode', 'AndNode', 'OrNode', 'NotNode',
           'parse_query', 'explain_loc', 'xpath_literal']


def _is_en():
    return _S._lang.__name__ == 'English'


def _t(zh, en):
    return en if _is_en() else zh


# ----------------------------------------------------------------AST 模型----------------------------------------------------------------

class Op(Enum):
    EQ = '='            # 全等
    CONTAINS = '*='     # 子串包含
    STARTS = '^='       # 前缀
    ENDS = '$='         # 后缀
    WORD = '~='         # 空白分词整词匹配（仅限属性）
    REGEX = '/='        # 正则匹配（re.search，本地执行）


@lru_cache(maxsize=512)
def _compile_regex(pattern):
    try:
        return re_compile(pattern)
    except re_error as e:
        raise LocatorError(_t(f'无效的正则表达式 {pattern!r}：{e}', f'invalid regex {pattern!r}: {e}'))


def _check_value(op, value, what):
    """构造期合法性校验：WORD 值约束、REGEX 预编译。"""
    if not isinstance(value, str):
        raise LocatorError(_t(f'{what} 的值必须是字符串，而不是 {type(value).__name__}',
                              f'value of {what} must be str, not {type(value).__name__}'))
    if op is Op.WORD:
        if not value or any(c.isspace() for c in value):
            raise LocatorError(_t(f'"{op.value}" 的值不能为空且不可包含空白字符：{value!r}',
                                  f'"{op.value}" value must be non-empty and contain no whitespace: {value!r}'))
    elif op is Op.REGEX:
        _compile_regex(value)


class _Node:
    """AST 节点公共方法：本地求值、格式化与 XPath 编译。"""
    __slots__ = ()

    def match(self, ele):
        return _match_node(self, _EleView(ele))

    def canonical(self):
        return _canon(self)

    def to_query(self):
        return '?' + _query_str(self)

    def xpath(self, relative=False):
        return to_xpath(self, relative)

    def is_pure_xpath(self):
        return is_pure_xpath(self)


@dataclass(frozen=True, repr=False)
class TagNode(_Node):
    op: Op
    value: str

    def __post_init__(self):
        if self.op is Op.WORD:
            raise LocatorError(_t('标签名不支持 "~=" 整词匹配，整词匹配仅限属性', 'tag does not support "~=" word match'))
        _check_value(self.op, self.value, 'tag')

    def __repr__(self):
        return f'Tag({self.op.value}, {self.value!r})'


@dataclass(frozen=True, repr=False)
class AttrNode(_Node):
    name: str
    op: Op = None
    value: str = None

    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise LocatorError(_t('属性名不能为空', 'attribute name must be non-empty'))
        if self.name == '*':
            if self.op is not None:
                raise LocatorError(_t('"@*" 不支持运算符', '"@*" does not take an operator'))
        elif self.op is None:
            if self.value is not None:
                raise LocatorError(_t('属性存在性判断不能带值', 'existence check takes no value'))
        else:
            _check_value(self.op, self.value, f'@{self.name}')

    def __repr__(self):
        return (f'Attr({self.name!r})' if self.op is None
                else f'Attr({self.name!r}, {self.op.value}, {self.value!r})')


@dataclass(frozen=True, repr=False)
class TextNode(_Node):
    kind: str   # 'text' 深层文本 | 'owntext' 直属文本节点
    op: Op
    value: str

    def __post_init__(self):
        if self.kind not in ('text', 'owntext'):
            raise LocatorError(_t(f'文本类型必须是 text 或 owntext，而不是 {self.kind!r}',
                                  f'text kind must be "text" or "owntext", not {self.kind!r}'))
        if self.op is Op.WORD:
            raise LocatorError(_t('文本不支持 "~=" 整词匹配，整词匹配仅限属性', 'text does not support "~=" word match'))
        _check_value(self.op, self.value, self.kind)

    def __repr__(self):
        return f'Text({self.kind!r}, {self.op.value}, {self.value!r})'


@dataclass(frozen=True, repr=False)
class AndNode(_Node):
    children: tuple

    def __post_init__(self):
        if not self.children:
            raise LocatorError(_t('&& 至少需要一个条件', '&& needs at least one condition'))

    def __repr__(self):
        return f'And({", ".join(repr(i) for i in self.children)})'


@dataclass(frozen=True, repr=False)
class OrNode(_Node):
    children: tuple

    def __post_init__(self):
        if not self.children:
            raise LocatorError(_t('|| 至少需要一个条件', '|| needs at least one condition'))

    def __repr__(self):
        return f'Or({", ".join(repr(i) for i in self.children)})'


@dataclass(frozen=True, repr=False)
class NotNode(_Node):
    child: object

    def __repr__(self):
        return f'Not({self.child!r})'


class QueryError(LocatorError):
    """查询 DSL 语法错误，带 offset 与修改建议，继承 LocatorError（ValueError 体系）。"""


# ----------------------------------------------------------------本地求值----------------------------------------------------------------

class _EleView:
    """统一适配 ChromiumElement / ShadowRoot / SessionElement / lxml 元素的只读视图，属性按需懒加载。"""
    __slots__ = ('_ele', '_lx', '_tag', '_attrs', '_deep', '_owns')

    def __init__(self, ele):
        self._ele = ele
        self._lx = None
        self._tag = self._attrs = self._deep = self._owns = None
        inner = getattr(ele, 'inner_ele', None)
        if inner is not None:
            self._lx = inner
        elif hasattr(ele, 'itertext'):
            self._lx = ele

    @property
    def tag(self):
        if self._tag is None:
            self._tag = (self._lx.tag if self._lx is not None else self._ele.tag).lower()
        return self._tag

    @property
    def attrs(self):
        if self._attrs is None:
            self._attrs = dict(self._lx.attrib) if self._lx is not None else dict(self._ele.attrs)
        return self._attrs

    def attr(self, name):
        attrs = self.attrs
        return attrs.get(name, attrs.get(name.lower()))

    @property
    def deep_text(self):
        if self._deep is None:
            self._deep = ''.join(self._lx.itertext()) if self._lx is not None else self._ele.text
        return self._deep

    @property
    def own_texts(self):
        if self._owns is None:
            if self._lx is not None:
                self._owns = [t for t in (self._lx.text, *(c.tail for c in self._lx)) if t]
            else:
                r = self._ele._run_js('var a=[],n=this.childNodes;for(var i=0;i<n.length;i++){'
                                      'if(n[i].nodeType===3){a.push(n[i].textContent)}}return a;')
                self._owns = [t for t in (r or []) if t]
        return self._owns


def _cmp(op, actual, value):
    if op is Op.EQ:
        return actual == value
    if op is Op.CONTAINS:
        return value in actual
    if op is Op.STARTS:
        return actual.startswith(value)
    if op is Op.ENDS:
        return actual.endswith(value)
    return _compile_regex(value).search(actual) is not None


def _match_node(node, view):
    if isinstance(node, TagNode):
        tag = view.tag
        if node.op is Op.EQ:
            return True if node.value == '*' else tag == node.value.lower()
        v = node.value.lower()
        if node.op is Op.CONTAINS:
            return v in tag
        if node.op is Op.STARTS:
            return tag.startswith(v)
        if node.op is Op.ENDS:
            return tag.endswith(v)
        return _compile_regex(node.value).search(tag) is not None

    if isinstance(node, AttrNode):
        if node.name == '*':
            return bool(view.attrs)
        actual = view.attr(node.name)
        if actual is None:
            return False
        if node.op is Op.WORD:
            return node.value in actual.split()
        return _cmp(node.op, actual, node.value)

    if isinstance(node, TextNode):
        if node.kind == 'text':
            return _cmp(node.op, view.deep_text, node.value)
        return any(_cmp(node.op, t, node.value) for t in view.own_texts)

    if isinstance(node, AndNode):
        return all(_match_node(c, view) for c in node.children)

    if isinstance(node, OrNode):
        return any(_match_node(c, view) for c in node.children)

    if isinstance(node, NotNode):
        return not _match_node(node.child, view)

    raise LocatorError(_t(f'未知的查询节点类型：{node!r}', f'unknown query node: {node!r}'))


def match_query(node, ele):
    """对单个元素（ChromiumElement/SessionElement/lxml 元素）执行 AST 本地求值。"""
    return _match_node(node, _EleView(ele))


# ----------------------------------------------------------------XPath 编译----------------------------------------------------------------

_UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_LOWER = 'abcdefghijklmnopqrstuvwxyz'
_QNAME = re_compile(r'[A-Za-z_][A-Za-z0-9_.\-]*(?::[A-Za-z_][A-Za-z0-9_.\-]*)*\Z')


def xpath_literal(s):
    """XPath 1.0 安全字面量：含双引号时换单引号，两者都含时用 concat() 拼接。"""
    if '"' not in s:
        return f'"{s}"'
    if "'" not in s:
        return f"'{s}'"
    segs = s.split('"')
    parts = []
    for i, seg in enumerate(segs):
        if seg:
            parts.append(f'"{seg}"')
        if i < len(segs) - 1:
            parts.append('\'"\'')
    return f'concat({",".join(parts)})'


def _lower_name():
    return f"translate(name(),'{_UPPER}','{_LOWER}')"


def _ends_expr(subject, v):
    lit = xpath_literal(v)
    return f'string-length({subject}) >= {len(v)} and substring({subject}, string-length({subject}) - {len(v) - 1}) = {lit}'


def _leaf_xpath(node):
    """单节点编译为 XPath 1.0 谓词片段；返回 None 表示无法下推（本地执行）。"""
    if isinstance(node, TagNode):
        if node.op is Op.REGEX:
            return None
        if node.value == '*':
            return 'true()'
        t, v = _lower_name(), node.value.lower()
        lit = xpath_literal(v)
        if node.op is Op.EQ:
            return f'{t}={lit}'
        if node.op is Op.CONTAINS:
            return f'contains({t},{lit})'
        if node.op is Op.STARTS:
            return f'starts-with({t},{lit})'
        return _ends_expr(t, v)  # ENDS

    if isinstance(node, AttrNode):
        if node.name == '*':
            return '@*'
        if node.op is Op.REGEX:
            return None
        if ':' in node.name or not _QNAME.match(node.name):
            # 含 ':'（形如命名空间前缀，未声明时任何 XPath 引擎都会报错）或非 QName
            # 属性名（Vue 的 @click、:class 等）都无法作为 @name 下推，交由本地精筛
            return None
        a, v = f'@{node.name}', node.value
        if node.op is None:
            return a
        lit = xpath_literal(v)
        if node.op is Op.EQ:
            return f'{a}={lit}'
        if not v:
            return a    # 空串的包含/前后缀匹配等价于属性存在
        if node.op is Op.CONTAINS:
            return f'contains({a},{lit})'
        if node.op is Op.STARTS:
            return f'starts-with({a},{lit})'
        if node.op is Op.WORD:
            return f'contains(concat(" ",normalize-space({a})," "),{xpath_literal(f" {v} ")})'
        return _ends_expr(a, v)  # ENDS

    if isinstance(node, TextNode):
        if node.op is Op.REGEX:
            return None
        v = node.value
        lit = xpath_literal(v)
        if node.kind == 'text':
            if not v:
                return 'true()'
            if node.op is Op.EQ:
                return f'.={lit}'
            if node.op is Op.CONTAINS:
                return f'contains(.,{lit})'
            if node.op is Op.STARTS:
                return f'starts-with(.,{lit})'
            return _ends_expr('.', v)  # ENDS
        # owntext：检查任意直属文本节点
        if not v:
            return 'text()'
        if node.op is Op.EQ:
            return f'text()[.={lit}]'
        if node.op is Op.CONTAINS:
            return f'text()[contains(.,{lit})]'
        if node.op is Op.STARTS:
            return f'text()[starts-with(.,{lit})]'
        return f'text()[{_ends_expr(".", v)}]'

    return None


@lru_cache(maxsize=512)
def _pushdown(node):
    """返回 (XPath 谓词片段, 是否含本地节点)。片段为 'true()' 表示预筛恒真。
    含本地节点时片段是安全超集（Sound Over-Approximation），绝不漏杀。"""
    if isinstance(node, (AndNode, OrNode, NotNode)):
        if isinstance(node, NotNode):
            frag, local = _pushdown(node.child)
            if local:     # 严禁对超集近似取反
                return 'true()', True
            if frag == 'true()':
                return 'false()', False
            return f'not({frag})', False

        parts, local = [], False
        for c in node.children:
            f, l = _pushdown(c)
            local = local or l
            if f == 'true()':
                if isinstance(node, OrNode):
                    return 'true()', local or True
                continue    # And 中恒真子项直接丢弃
            if isinstance(c, (AndNode, OrNode)):
                f = f'({f})'
            parts.append(f)
        if not parts:
            return 'true()', local
        return f' {"and" if isinstance(node, AndNode) else "or"} '.join(parts), local

    frag = _leaf_xpath(node)
    return (frag if frag is not None else 'true()'), frag is None


def pushdown_fragment(node):
    """下推预筛 XPath 片段（'true()' 表示恒真/需全量捞取）。"""
    return _pushdown(node)[0]


def has_local(node):
    """AST 是否包含无法下推到 XPath 1.0 的本地节点（/= 正则、非 QName 属性名等）。"""
    return _pushdown(node)[1]


@lru_cache(maxsize=512)
def _to_xpath(node, relative):
    frag = _pushdown(node)[0]
    base = './/*' if relative else '//*'
    return base if frag == 'true()' else f'{base}[{frag}]'


def to_xpath(node, relative=False):
    """整棵 AST 的预筛 XPath。pure-xpath 查询即最终执行语句；hybrid 查询为候选集预筛。"""
    return _to_xpath(node, relative)


def is_pure_xpath(node):
    return not has_local(node)


# ----------------------------------------------------------------字符串格式化----------------------------------------------------------------

def _c_lit(v):
    """canonical 格式值：统一双引号，转义 \\ 和 "。"""
    return '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'


_BARE_UNSAFE = set(' \t\r\n\f\v&|()\'"')


def _q_lit(v):
    """DSL 格式值：可安全裸写则裸写，否则加引号。"""
    if v and not any(c in _BARE_UNSAFE for c in v):
        return v
    return _c_lit(v)


def _attr_ref(name):
    """属性名引用（含 @ 前缀）：可裸写则 @name，否则 @"name"（如 Vue 的 @click、:class）。"""
    if _QNAME.match(name):
        return f'@{name}'
    return '@"' + name.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _canon(node):
    if isinstance(node, TagNode):
        return f'tag{node.op.value}{_c_lit(node.value)}'
    if isinstance(node, AttrNode):
        if node.op is None:
            return '@*' if node.name == '*' else _attr_ref(node.name)
        return f'{_attr_ref(node.name)}{node.op.value}{_c_lit(node.value)}'
    if isinstance(node, TextNode):
        return f'{node.kind}{node.op.value}{_c_lit(node.value)}'
    if isinstance(node, AndNode):
        return ' && '.join(_wrap_canon(c) for c in node.children)
    if isinstance(node, OrNode):
        return ' || '.join(_wrap_canon(c) for c in node.children)
    return '!' + _wrap_canon(node.child)


def _wrap_canon(node):
    s = _canon(node)
    return f'({s})' if isinstance(node, (AndNode, OrNode)) else s


_TAG_BARE = re_compile(r'[A-Za-z][A-Za-z0-9\-]*\Z')


def _query_str(node):
    if isinstance(node, TagNode):
        if node.op is Op.EQ and _TAG_BARE.match(node.value):
            return node.value
        return f'tag{node.op.value}{_q_lit(node.value)}'
    if isinstance(node, AttrNode):
        if node.op is None:
            return '@*' if node.name == '*' else _attr_ref(node.name)
        if node.name == 'class' and node.op is Op.WORD and _CSS_IDENT.fullmatch(node.value):
            return f'.{node.value}'
        if node.name == 'id' and node.op is Op.EQ and _CSS_IDENT.fullmatch(node.value):
            return f'#{node.value}'
        return f'{_attr_ref(node.name)}{node.op.value}{_q_lit(node.value)}'
    if isinstance(node, TextNode):
        return f'{node.kind}{node.op.value}{_q_lit(node.value)}'
    if isinstance(node, AndNode):
        return ' && '.join(_wrap_q(c) for c in node.children)
    if isinstance(node, OrNode):
        return ' || '.join(_wrap_q(c) for c in node.children)
    return '!' + _wrap_q(node.child)


def _wrap_q(node):
    s = _query_str(node)
    return f'({s})' if isinstance(node, (AndNode, OrNode)) else s


def canonical(node):
    """标准式：结构化、全程带引号的规范文本形式。"""
    return _canon(node)


def to_query(node):
    """DSL 式：带 ? 前缀、含简写糖，可用 parse_query 还原为结构相同的 AST。"""
    return '?' + _query_str(node)


def explain_query(node, source=None):
    en = _is_en()
    frag, local = _pushdown(node)
    xp = _to_xpath(node, False)
    if local:
        strategy = 'hybrid (XPath pre-filter + local match)' if en else 'hybrid（XPath 预筛 + 本地精筛）'
        label = 'prefilter' if en else '预筛XPath'
    else:
        strategy = 'pure-xpath' if en else 'pure-xpath（纯 XPath 下推）'
        label = 'xpath' if en else '执行XPath'
    rows = [('original' if en else '原始输入', source if source is not None else to_query(node)),
            ('canonical' if en else '标准式', canonical(node)),
            ('AST', repr(node)),
            ('strategy' if en else '执行模式', strategy),
            (label, xp)]
    width = max(len(k) for k, _ in rows)
    return '\n'.join(f'{k}{" " * (width - len(k) + 1)}: {v}' for k, v in rows)


# ----------------------------------------------------------------解析器----------------------------------------------------------------

_WORD = re_compile(r'[A-Za-z_][A-Za-z0-9_.:\-]*')
_TAG = re_compile(r'[A-Za-z][A-Za-z0-9\-]*\Z')
_CSS_IDENT = re_compile(r'[A-Za-z0-9_\-]+')
_OLD_PREFIX = ('tag:', 'tag=', 't:', 't=', 'text:', 'text=', 'tx:', 'tx=', 'css:', 'css=',
               'xpath:', 'xpath=', 'x:', 'x=', 'c:', 'c=')


class _Parser:
    def __init__(self, text):
        self.s = text    # 完整字符串（含开头的 ?）
        self.n = len(text)
        self.i = 1

    def parse(self):
        self._ws()
        if self._at_end():
            self._err(1, _t('查询不能为空', 'empty query'), _t('例如 ?input && type=filter', 'e.g. ?input && type=filter'))
        node = self._or()
        self._ws()
        if not self._at_end():
            self._leftover()
        return node

    # ----------基础工具----------
    def _err(self, pos, reason, tip=None, tok=None):
        tok = tok if tok is not None else (self.s[pos] if pos < self.n else '')
        lines = [_t(f'查询语法错误（位置 {pos}）', f'query syntax error (offset {pos})'),
                 f'  {self.s.replace(chr(10), " ")}',
                 f'  {" " * pos}{"^" * max(1, len(tok))}',
                 f'{_t("原因", "reason")}: {reason}']
        if tip:
            lines.append(f'{_t("建议", "tip")}: {tip}')
        raise QueryError('\n'.join(lines))

    def _ws(self):
        while self.i < self.n and self.s[self.i].isspace():
            self.i += 1

    def _at_end(self):
        return self.i >= self.n

    def _ch(self, k=0):
        p = self.i + k
        return self.s[p] if p < self.n else ''

    def _take(self, tok):
        if self.s.startswith(tok, self.i):
            self.i += len(tok)
            return True
        return False

    # ----------布尔层----------
    def _or(self):
        parts = [self._and()]
        while True:
            save = self.i
            self._ws()
            if self._take('||'):
                op = '||'
            elif self._ch() == '|' and self._ch(1) != '|':
                self.i += 1
                op = '|'
            else:
                self.i = save
                return OrNode(tuple(parts)) if len(parts) > 1 else parts[0]
            self._ws()
            if self._at_end() or self._ch() in ')&|':
                self._err(self.i, _t(f"'{op}' 后缺少条件表达式", f"missing condition after '{op}'"),
                          _t(f"删除多余的 '{op}'", f"remove extra '{op}'"), tok=op)
            parts.append(self._and())

    def _and(self):
        parts = [self._unary()]
        while True:
            save = self.i
            self._ws()
            if self._take('&&'):
                op = '&&'
            elif self._ch() == '&' and self._ch(1) not in '&=':
                self.i += 1
                op = '&'
            else:
                self.i = save
                return AndNode(tuple(parts)) if len(parts) > 1 else parts[0]
            self._ws()
            if self._at_end() or self._ch() in ')&|':
                self._err(self.i, _t(f"'{op}' 后缺少条件表达式", f"missing condition after '{op}'"),
                          _t(f"删除多余的 '{op}' 或补充条件", f"remove extra '{op}' or add a condition"), tok=op)
            parts.append(self._unary())

    def _unary(self):
        c = self._ch()
        if c == '!':
            pos = self.i
            self.i += 1
            self._ws()
            if self._at_end() or self._ch() in ')&|':
                self._err(pos, _t("'!' 后缺少条件表达式", "missing condition after '!'"),
                          _t("'!' 需作用于一个条件，如 !id=ad", "'!' must precede a condition, e.g. !id=ad"), tok='!')
            return NotNode(self._unary())
        if c == '(':
            pos = self.i
            self.i += 1
            self._ws()
            if self._ch() == ')':
                self._err(pos, _t('空括号 "()" 内缺少条件', 'empty "()" has no condition'))
            node = self._or()
            self._ws()
            if self._ch() != ')':
                self._err(self.i, _t('括号不匹配，缺少 ")"', 'unbalanced parenthesis, missing ")"'), tok=')')
            self.i += 1
            return node
        return self._pred()

    # ----------谓词层----------
    def _pred(self):
        c, pos = self._ch(), self.i
        if not c or c in ')&|':
            self._err(pos, _t('缺少条件表达式', 'missing condition'))
        if c == '#':
            self.i += 1
            self._tight('#')
            return AttrNode('id', Op.EQ, self._css_ident('#'))
        if c == '.':
            self.i += 1
            self._tight('.')
            return AttrNode('class', Op.WORD, self._css_ident('.'))
        if c == '*':
            self.i += 1
            return TagNode(Op.EQ, '*')
        if c == '@':
            self.i += 1
            return self._attr_pred(pos)
        if c in '\'"':
            self._err(pos, _t('条件不能以引号开头', 'a condition cannot start with a quote'),
                      _t('引号只能用于包裹值或 @ 后的属性名', 'quotes only wrap values or attr names after @'))
        if c in '=!~^$/':
            self._err(pos, _t(f"意外字符 '{c}'", f"unexpected character '{c}'"),
                      _t('条件应以标签名、#id、.class、@属性 或 ! / ( 开头',
                         'a condition starts with a tag, #id, .class, @attr, ! or ('))
        m = _WORD.match(self.s, self.i)
        if not m:
            self._bad_start(pos, c)
        word = m.group()
        self.i = m.end()
        save = self.i
        self._ws()
        if self._ch() == '!' and self._ch(1) == '=':
            self._err(self.i, _t('不支持 != 运算符', "'!=' is not supported"),
                      _t('否定请统一使用 ! 前缀，如 !a=b', "use the '!' prefix for negation, e.g. !a=b"), tok='!=')
        op = self._oper()
        if op is None:
            self.i = save
            return self._word_as_tag(word, pos)
        value = self._value()
        return self._make_word_node(word, op, value, pos)

    def _make_word_node(self, word, op, value, pos):
        if word == 'tag':
            if op is Op.WORD:
                self._err(pos, _t('标签名不支持 "~=" 整词匹配', 'tag does not support "~=" word match'),
                          _t('直接写 tag=div 即可', 'just write tag=div'), tok=word)
            return TagNode(op, value)
        if word in ('text', 'owntext'):
            if op is Op.WORD:
                self._err(pos, _t('文本不支持 "~=" 整词匹配', 'text does not support "~=" word match'),
                          _t('用 text*=xxx 实现包含匹配', 'use text*=xxx for contains'), tok=word)
            return TextNode(word, op, value)
        return AttrNode(word, op, value)

    def _word_as_tag(self, word, pos):
        if _TAG.match(word):
            return TagNode(Op.EQ, word)
        if ':' in word:
            tip = (_t(f'旧语法 {word} 不属于新引擎；标签名请直接写，文本包含请写 text*=',
                      f'legacy syntax does not apply here; write the tag name directly, or text*= for text')
                   if word.startswith(_OLD_PREFIX) else
                   _t('属性名中的 ":" 需与值连用，如 xlink:href^=https://',
                      'attr names with ":" need a value, e.g. xlink:href^=https://'))
            self._err(pos, _t(f"无效运算符 ':'（'{word}' 不是合法标签名）",
                              f"invalid operator ':' ('{word}' is not a valid tag name)"), tip, tok=word)
        if '_' in word:
            self._err(pos, _t(f"'{word}' 不是合法标签名", f"'{word}' is not a valid tag name"),
                      _t(f'若判断属性是否存在请加 @ 前缀：@{word}',
                         f'to test attribute existence, prefix with @: @{word}'), tok=word)
        if '.' in word:
            self._err(pos, _t('不支持 CSS 式连续简写', 'CSS-style chained shorthands are not supported'),
                      _t('每个条件需用 && 连接，如 div && .btn', 'join conditions with &&, e.g. div && .btn'), tok=word)
        self._err(pos, _t(f"'{word}' 不是合法标签名", f"'{word}' is not a valid tag name"),
                  _t(f'若是文本请写 text*={word}', f'for text search write text*={word}'), tok=word)

    def _bad_start(self, pos, c):
        if not c.isascii() and c.isalnum():
            m = re_match(r'[^\s&|()]+', self.s[pos:])
            w = m.group() if m else c
            self._err(pos, _t(f"'{w}' 不是合法标签名", f"'{w}' is not a valid tag name"),
                      _t(f'搜索文本请写 text*={w}', f'to search text write text*={w}'), tok=w)
        self._err(pos, _t(f"意外字符 '{c}'", f"unexpected character '{c}'"))

    def _tight(self, sym):
        if self._at_end() or self._ch().isspace():
            self._err(self.i, _t(f"'{sym}' 后不能有空格", f"no whitespace allowed after '{sym}'"),
                      _t(f'名称须紧跟 {sym}，如 {sym}btn', f'the name must follow {sym} directly'), tok=sym)

    def _css_ident(self, sym):
        m = _CSS_IDENT.match(self.s, self.i)
        if not m:
            self._err(self.i, _t(f"'{sym}' 后缺少有效名称", f"invalid name after '{sym}'"),
                      _t('名称可含字母、数字、_ 和 -', 'names may contain letters, digits, _ and -'))
        self.i = m.end()
        return m.group()

    def _attr_pred(self, pos):
        c = self._ch()
        if c == '*':
            self.i += 1
            return AttrNode('*', None, None)
        if not c:
            self._err(self.i, _t("'@' 后缺少属性名", 'missing attribute name after @'))
        if c.isspace():
            self._err(self.i, _t("'@' 后不能有空格", "no whitespace allowed after '@'"),
                      _t('属性名须紧跟 @，如 @data-testid', 'attr name must follow @ directly'), tok='@')
        if c in '@|':
            self._err(pos, _t("'@@' / '@|' 不属于新语法", "'@@' / '@|' do not exist in the new syntax"),
                      _t('多条件请用 && 或 || 连接，如 a=1 && b=2', 'join conditions with && or ||'), tok=f'@{c}')
        if c in '\'"':
            name = self._quoted()
        else:
            m = _WORD.match(self.s, self.i)
            if not m:
                self._err(self.i, _t(f"无效的属性名起始字符 '{c}'", f"invalid attribute name start '{c}'"))
            name = m.group()
            self.i = m.end()
        save = self.i
        self._ws()
        if self._ch() == '!' and self._ch(1) == '=':
            self._err(self.i, _t('不支持 != 运算符', "'!=' is not supported"),
                      _t('否定请统一使用 ! 前缀，如 !@alt', "use the '!' prefix, e.g. !@alt"), tok='!=')
        op = self._oper()
        if op is None:
            self.i = save
            return AttrNode(name, None, None)
        return AttrNode(name, op, self._value())

    def _oper(self):
        for tok, op in (('*=', Op.CONTAINS), ('^=', Op.STARTS), ('$=', Op.ENDS),
                        ('~=', Op.WORD), ('/=', Op.REGEX), ('=', Op.EQ)):
            if self._take(tok):
                return op
        return None

    def _value(self):
        self._ws()
        c = self._ch()
        if not c or c == ')':
            self._err(self.i, _t('缺少匹配值', 'missing value'),
                      _t('如 type=filter；空值请用引号：alt=""', 'e.g. type=filter; quote empty values: alt=""'))
        if c in '\'"':
            return self._quoted()
        j = self.i
        while j < self.n and not self.s[j].isspace() and self.s[j] not in _BARE_UNSAFE:
            j += 1
        if j == self.i:
            self._err(self.i, _t(f"值不能以特殊字符 '{c}' 开头", f"value cannot start with special character '{c}'"),
                      _t('正则或含 () | & 空白的值请用引号包裹，如 text/="(a|b)"',
                         'quote values containing () | & or spaces, e.g. text/="(a|b)"'))
        v = self.s[self.i:j]
        self.i = j
        return v

    def _quoted(self):
        q, start = self.s[self.i], self.i
        self.i += 1
        buf = []
        while self.i < self.n:
            c = self.s[self.i]
            if c == '\\':
                if self.i + 1 >= self.n:
                    self._err(self.i, _t('转义符 \\ 后缺少字符', 'dangling escape character \\'))
                nxt = self.s[self.i + 1]
                buf.append({'n': '\n', 't': '\t', '\\': '\\', '"': '"', "'": "'"}.get(nxt, '\\' + nxt))
                self.i += 2
            elif c == q:
                self.i += 1
                return ''.join(buf)
            else:
                buf.append(c)
                self.i += 1
        self._err(start, _t('引号未闭合', 'unterminated quote'), _t(f'补上结尾的 {q}', f'close with {q}'), tok=q)

    def _leftover(self):
        pos = self.i
        c = self._ch()
        m = re_match(r'[^\s&|()]+', self.s[pos:])
        tok = m.group() if m else c
        if c in '#.':
            self._err(pos, _t('不支持 CSS 式连续简写', 'CSS-style chained shorthands are not supported'),
                      _t('每个条件需用 && 连接，如 div && .btn && #id',
                         'join conditions with &&, e.g. div && .btn && #id'), tok=tok)
        if c.isalnum() or c in '_!@*(':
            self._err(pos, _t('相邻条件之间缺少 &&', "adjacent conditions are missing '&&'"),
                      _t('若想搜索含空格的文本请写 text*="a b"',
                         'to match text containing spaces write text*="a b"'), tok=tok)
        self._err(pos, _t(f'无法解析的剩余内容：{tok}', f'unparseable remainder: {tok}'), tok=tok)


@lru_cache(maxsize=256)
def parse_query(text):
    """解析 `?` 前缀查询字符串为不可变 AST（lru_cache 缓存）。"""
    if not isinstance(text, str) or not text.startswith('?'):
        raise LocatorError(_t(f'查询字符串须以 "?" 开头：{text!r}', f'query string must start with "?": {text!r}'))
    return _Parser(text).parse()


# ----------------------------------------------------------------Q Builder----------------------------------------------------------------

_SUFFIX_OPS = {'eq': Op.EQ, 'contains': Op.CONTAINS, 'startswith': Op.STARTS,
               'endswith': Op.ENDS, 'word': Op.WORD, 'regex': Op.REGEX}


def _kw_to_node(key, value):
    base, d, suf = key.partition('__')
    op = _SUFFIX_OPS[suf] if (d and suf in _SUFFIX_OPS) else (Op.EQ if not d else None)
    if op is None:
        raise LocatorError(_t(f'不支持的匹配后缀 "{suf}"，可用：__contains / __startswith / __endswith / __word / __regex',
                              f'unsupported suffix "{suf}"; use __contains/__startswith/__endswith/__word/__regex'))
    if base == 'tag':
        return TagNode(op, value)
    if base in ('text', 'owntext'):
        return TextNode(base, op, value)
    return AttrNode(base, op, value)


def _q_of(node):
    q = Q.__new__(Q)
    q._ast = node
    q._src = None
    return q


class _Field:
    """流式字段代理：Q.tag / Q.text / Q.owntext / Q.id / Q.cls / Q.attr(name)。"""
    def __init__(self, kind, name=None, default_op=Op.EQ):
        self._kind = kind
        self._name = name
        self._default_op = default_op

    def _node(self, op, value):
        if self._kind == 'tag':
            return TagNode(op, value)
        if self._kind == 'text':
            return TextNode(self._name, op, value)
        return AttrNode(self._name, op, value)

    def __call__(self, value):
        return _q_of(self._node(self._default_op, value))

    def eq(self, value):
        return _q_of(self._node(Op.EQ, value))

    def contains(self, value):
        return _q_of(self._node(Op.CONTAINS, value))

    def startswith(self, value):
        return _q_of(self._node(Op.STARTS, value))

    def endswith(self, value):
        return _q_of(self._node(Op.ENDS, value))

    def regex(self, pattern):
        return _q_of(self._node(Op.REGEX, pattern))

    def word(self, value):
        return _q_of(self._node(Op.WORD, value))


class _TagField(_Field):
    def __init__(self):
        super().__init__('tag')

    def word(self, value):
        raise LocatorError(_t('标签名不支持 "~=" 整词匹配', 'tag does not support "~=" word match'))


class _TextField(_Field):
    def __init__(self, kind):
        super().__init__('text', name=kind)

    def word(self, value):
        raise LocatorError(_t('文本不支持 "~=" 整词匹配', 'text does not support "~=" word match'))


class _AttrField(_Field):
    def __init__(self, name):
        super().__init__('attr', name=name)

    def exists(self):
        return _q_of(AttrNode(self._name, None, None))


class _ClsField(_AttrField):
    def __init__(self):
        super().__init__('class')
        self._default_op = Op.WORD


class Q:
    """查询构建器：Q('input', type='filter') & ~Q.id('ad')。

    * 风格 A：关键字直写，后缀 __contains/__startswith/__endswith/__word/__regex 选择运算符
    * 风格 B：Q.tag / Q.text / Q.owntext / Q.id / Q.cls / Q.attr(name) 流式代理
    * Q('?a && .btn') 直接解析查询字符串
    * 支持 & | ~ 布尔组合，与 `?` 字符串编译到同一棵 AST
    """
    __slots__ = ('_ast', '_src')

    tag = _TagField()
    text = _TextField('text')
    owntext = _TextField('owntext')
    id = _AttrField('id')
    cls = _ClsField()

    def __init__(self, tag=None, **kwargs):
        if isinstance(tag, str) and tag.startswith('?'):
            if kwargs:
                raise LocatorError(_t('Q("?...") 字符串形式不接受额外的关键字参数',
                                      'Q("?...") string form takes no extra keyword arguments'))
            self._ast = parse_query(tag)
            self._src = tag
            return
        children = []
        if tag is not None:
            children.append(TagNode(Op.EQ, tag))
        children.extend(_kw_to_node(k, v) for k, v in kwargs.items())
        if not children:
            raise LocatorError(_t('Q() 至少需要一个条件，如 Q("input", type="filter")',
                                  'Q() needs at least one condition, e.g. Q("input", type="filter")'))
        self._ast = children[0] if len(children) == 1 else AndNode(tuple(children))
        self._src = None

    @classmethod
    def attr(cls, name):
        """支持任意特殊属性名的流式代理：Q.attr('data-testid').exists()。"""
        return _AttrField(name)

    @property
    def ast(self):
        return self._ast

    # ----------布尔组合----------
    def _combine(self, other, cls):
        if not isinstance(other, Q):
            raise LocatorError(_t(f'运算符两侧都必须是 Q 对象，而不是 {type(other).__name__}',
                                  f'both operands must be Q objects, not {type(other).__name__}'))
        children = []
        for side in (self._ast, other._ast):
            children.extend(side.children if isinstance(side, cls) else (side,))  # 同类型提升为扁平结构
        return _q_of(cls(tuple(children)))

    def __and__(self, other):
        return self._combine(other, AndNode)

    def __or__(self, other):
        return self._combine(other, OrNode)

    def __rand__(self, other):
        return self._combine(other, AndNode)

    def __ror__(self, other):
        return self._combine(other, OrNode)

    def __invert__(self):
        return _q_of(NotNode(self._ast))

    # ----------求值与调试----------
    def match(self, ele):
        return _match_node(self._ast, _EleView(ele))

    def canonical(self):
        return canonical(self._ast)

    def to_query(self):
        return to_query(self._ast)

    def xpath(self, relative=False):
        return to_xpath(self._ast, relative)

    def is_pure_xpath(self):
        return is_pure_xpath(self._ast)

    def explain(self):
        return explain_query(self._ast, self._src)

    def __repr__(self):
        return f'Q({to_query(self._ast)!r})'

    def __eq__(self, other):
        return isinstance(other, Q) and self._ast == other._ast

    def __hash__(self):
        return hash(('Q', self._ast))


def explain_loc(loc):
    """调试工具：打印 `?` 字符串或 Q 对象的标准式、AST、执行策略与 XPath。"""
    if isinstance(loc, Q):
        return loc.explain()
    return explain_query(parse_query(loc), loc if isinstance(loc, str) else None)
