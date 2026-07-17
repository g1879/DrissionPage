"""Feature: deterministic coverage for ChromiumElement helper contracts."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from time import perf_counter

import DrissionPage._elements.chromium_element as chromium_element_module
from DrissionPage._elements.chromium_element import (
    ChromiumElement,
    ChromiumElementsList,
    Pseudo,
    ShadowRoot,
    _check_ele,
    _get_node_by_backend_id,
    _get_node_by_node_id,
    _get_node_by_obj_id,
    _get_node_info,
    _make_ele,
    convert_argument,
    do_find_any,
    do_find_ax,
    do_find_css,
    do_find_sr_any,
    do_find_sr_xpath,
    do_find_xpath,
    find_in_chromium_ele,
    find_by_ax,
    make_chromium_eles,
    make_js_for_find_ele_by_xpath,
    parse_js_result,
    run_js,
    wait_for_ele,
)
from DrissionPage._elements.none_element import NoneElement
from DrissionPage._functions.keys import Keys
from DrissionPage._units.states import ShadowRootStates
from DrissionPage.errors import AlertExistsError, CDPError, ContextLostError, LocatorError, NoRectError, NoResourceError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "chromium_element_extra_contracts"
REQUIRES_BROWSER = False


def run(ctx):
    _check_geometry_and_resource_contracts()
    _check_input_and_drag_contracts()
    _check_shadow_root_contracts()
    _check_find_helper_contracts()
    _check_node_factory_contracts()
    _check_javascript_result_contracts()
    _check_predicate_and_pseudo_contracts()


class ActionLog:
    def __init__(self):
        self.calls = []

    def move_to(self, target, offset_x=None, offset_y=None, duration=None):
        self.calls.append(("move_to", target, offset_x, offset_y, duration))
        return self

    def hold(self, target):
        self.calls.append(("hold", target))
        return self

    def release(self):
        self.calls.append(("release",))
        return self

    def type(self, values):
        self.calls.append(("type", values))
        return self


class FakeOwner:
    def __init__(self, tag="div"):
        self._tab = SimpleNamespace(tab_id="tab-1")
        self.timeout = 0.02
        self.timeouts = SimpleNamespace(script=0.2)
        self.states = SimpleNamespace(has_alert=False)
        self.rect = SimpleNamespace(size=(100, 100))
        self.actions = ActionLog()
        self._none_ele_value = None
        self._none_ele_return_value = False
        self._enabled = set()
        self._Accessibility_enable = lambda: self._enable_domain("Accessibility")
        self._frame_id = "frame-1"
        self._root_oid = "root-object"
        self.tag_name = tag
        self.html = "<div><span>child</span></div>"
        self.js_value = None
        self.calls = []
        self.location_backend_id = 303
        self.raise_focus = False
        self.shadow_info = None

    def _run_cdp(self, method, **kwargs):
        self.calls.append((method, kwargs))
        if method == "DOM.resolveNode":
            source = kwargs.get("nodeId", kwargs.get("backendNodeId"))
            return {"object": {"objectId": f"object-{source}"}}
        if method == "DOM.requestNode":
            return {"nodeId": 44}
        if method == "DOM.describeNode":
            node_id = kwargs.get("nodeId", 44)
            backend_id = kwargs.get("backendNodeId", 55)
            node = {
                "nodeId": node_id,
                "backendNodeId": backend_id,
                "localName": self.tag_name,
                "nodeName": self.tag_name.upper(),
                "nodeValue": "",
            }
            if self.shadow_info:
                node.update(self.shadow_info)
            return {"node": node}
        if method == "DOM.getNodeForLocation":
            return {"backendNodeId": self.location_backend_id}
        if method in {"DOM.focus", "DOM.setFileInputFiles", "DOM.setAttributeValue"}:
            if method == "DOM.focus" and self.raise_focus:
                raise CDPError
            return {}
        if method == "DOM.getOuterHTML":
            return {"outerHTML": self.html}
        if method == "DOM.getAttributes":
            return {"attributes": ["id", "fake"]}
        if method == "DOM.querySelector":
            return {"nodeId": 77}
        if method == "DOM.querySelectorAll":
            return {"nodeIds": [77, 78]}
        if method == "Accessibility.queryAXTree":
            return {"nodes": [{"backendDOMNodeId": 81}, {"backendDOMNodeId": 82}]}
        if method == "Runtime.evaluate":
            return {"result": {"type": "number", "value": 4}}
        if method == "Runtime.callFunctionOn":
            script = kwargs.get("functionDeclaration", "")
            if "this.innerHTML" in script:
                return _cdp_value(self.js_value if self.js_value is not None else self.html)
            if "this.innerText" in script:
                return _cdp_value("text")
            if "this.focus" in script:
                return _cdp_value(None)
            return _cdp_value(self.js_value)
        raise AssertionError(f"unexpected CDP call: {method} {kwargs!r}")


class FakeRect:
    def __init__(self, *, location=(10, 20), midpoint=(30, 40), size=(40, 20)):
        self.location = location
        self.midpoint = midpoint
        self.size = size


class FakeWait:
    def __init__(self):
        self.calls = []

    def clickable(self, **kwargs):
        self.calls.append(kwargs)
        return True


class FakeNodePage(FakeOwner):
    def __init__(self):
        super().__init__()
        self.node_map = {}

    def _run_cdp(self, method, **kwargs):
        if method == "DOM.describeNode":
            key = next((kwargs[k] for k in ("backendNodeId", "nodeId", "objectId") if k in kwargs), None)
            node = self.node_map.get(key)
            if node is not None:
                return {"node": dict(node)}
        return super()._run_cdp(method, **kwargs)


@contextmanager
def _replace(target, **replacements):
    originals = {name: getattr(target, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(target, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(target, name, value)


def _cdp_value(value):
    if value is None:
        return {"result": {"type": "undefined"}}
    if isinstance(value, bool):
        return {"result": {"type": "boolean", "value": value}}
    if isinstance(value, (int, float)):
        return {"result": {"type": "number", "value": value}}
    return {"result": {"type": "string", "value": value}}


def _element(owner=None, *, tag=None, backend_id=101):
    owner = owner or FakeOwner(tag or "div")
    element = ChromiumElement(owner, node_id=1, obj_id="object-1", backend_id=backend_id)
    if tag is not None:
        element._tag = tag
    return element


def _assert_raises(error_type, func, message):
    try:
        func()
    except error_type:
        return
    raise AssertionError(message)


def _last_call(owner, method):
    return next(call for call in reversed(owner.calls) if call[0] == method)


def _check_geometry_and_resource_contracts():
    owner = FakeOwner()
    element = _element(owner)
    element._rect = FakeRect()
    element._states = SimpleNamespace(is_covered=303, has_rect=True)

    covered = element.over(timeout=0)
    assert_true(isinstance(covered, ChromiumElement), "over() should return the covering element")
    element._states = SimpleNamespace(is_covered=False, has_rect=True)
    assert_true(isinstance(element.over(timeout=0), NoneElement), "over() should return NoneElement without coverage")

    assert_true(isinstance(element.offset(timeout=0), ChromiumElement), "offset() should resolve the midpoint node")
    assert_true(isinstance(element.offset(x=2, y=3, timeout=0), ChromiumElement),
                "offset(x, y) should resolve an explicit page coordinate")
    _assert_raises(LocatorError, lambda: element.offset(locator=object(), timeout=0),
                   "offset() should reject non-locator values")

    element._states = SimpleNamespace(is_covered=False, has_rect=((10, 20), (50, 20), (50, 40), (10, 40)))
    for direction in (element.east, element.south, element.west, element.north):
        assert_true(isinstance(direction(2), ChromiumElement), "pixel-relative lookup should resolve an element")
    assert_true(isinstance(element.east(), ChromiumElement), "directional lookup should scan to a matching element")
    element._states = SimpleNamespace(has_rect=False)
    _assert_raises(NoRectError, element.north, "north() should reject elements without geometry")

    with TemporaryDirectory() as directory:
        image = _element(FakeOwner("img"), tag="img")
        image.src = lambda timeout=None: b"image-bytes"
        image.attr = lambda name: "data:image/png;base64,aGVsbG8=" if name == "src" else None
        image.property = lambda name: "https://example.test/image.png" if name == "currentSrc" else None
        saved = image.save(directory, rename=False)
        assert_true(saved.endswith("img.png"), "data-image save should infer the image extension")
        assert_equal(Path(saved).read_bytes(), b"image-bytes", "save() should write binary resource data")

        named = image.save(directory, name="artifact", rename=False)
        assert_true(named.endswith("artifact.jpg"), "save() should add a default suffix to extensionless names")
        empty = _element(FakeOwner("img"), tag="img")
        empty.src = lambda timeout=None: None
        _assert_raises(NoResourceError, lambda: empty.save(directory), "save() should reject unavailable resources")


def _check_input_and_drag_contracts():
    owner = FakeOwner("input")
    element = _element(owner, tag="input")
    element.attr = lambda name: "text" if name == "type" else None
    element._wait = FakeWait()
    typed = []
    with _replace(chromium_element_module,
                  input_text_or_keys=lambda page, values: typed.append((page, values)),
                  system=lambda: "linux"):
        assert_true(element.input("abc", clear=True) is element, "native input should be chainable")
        assert_true(element.clear() is element, "native clear should be chainable")
    assert_equal(typed, [(owner, "abc")], "native text input should route strings to the key helper")
    assert_in(("type", (Keys.CTRL_A, Keys.DEL)), owner.actions.calls,
              "native clear should select and delete through page actions")
    assert_true(element.focus() is element, "focus should be chainable")

    owner.raise_focus = True
    assert_true(element.focus() is element, "focus should fall back to element JavaScript")
    assert_in("function(){this.focus();}",
              [call[1]["functionDeclaration"] for call in owner.calls if call[0] == "Runtime.callFunctionOn"],
              "focus fallback should call this.focus()")
    assert_true(element.hover(4, 5) is element, "hover should remain chainable")

    target = _element(FakeOwner("span"), tag="span", backend_id=202)
    target._rect = FakeRect(midpoint=(80, 90))
    element._rect = FakeRect(midpoint=(30, 40))
    assert_true(element.drag(5, 6, duration=.2) is element, "drag should remain chainable")
    assert_true(element.drag_to(target, duration=.3) is element, "drag_to(element) should use its midpoint")
    _assert_raises(ValueError, lambda: element.drag_to("bad"), "drag_to() should reject unsupported destinations")

    file_element = _element(FakeOwner("input"), tag="input")
    file_element.attr = lambda name: "file" if name == "type" else None
    assert_true(file_element.input("one.txt\ntwo.txt") is file_element, "file input should accept newline paths")
    files = _last_call(file_element.owner, "DOM.setFileInputFiles")[1]["files"]
    assert_equal(files, [str(Path("one.txt").resolve()), str(Path("two.txt").resolve())],
                 "file input should normalize each newline-delimited path")


def _check_shadow_root_contracts():
    owner = FakeOwner()
    parent = _element(owner)
    owner.shadow_info = {"localName": "shadow-root", "nodeId": 44, "backendNodeId": 55}
    owner.js_value = "<html><body><span>inside</span></body></html>"
    shadow = ShadowRoot(parent, obj_id="shadow-object")
    assert_equal((shadow._obj_id, shadow._node_id, shadow._backend_id), ("shadow-object", 44, 55),
                 "ShadowRoot object construction should resolve node and backend identities")
    assert_equal(shadow.tag, "shadow-root", "shadow root should expose its synthetic tag")
    assert_equal(shadow.inner_html, owner.js_value, "shadow root should expose inner HTML")
    assert_equal(shadow.html, f"<shadow_root>{owner.js_value}</shadow_root>",
                 "shadow root html should wrap its inner HTML")
    assert_true(isinstance(shadow.states, ShadowRootStates), "shadow root should expose its state helper")
    assert_true(shadow.states is shadow.states, "shadow root state helper should be cached")
    assert_true(shadow == ShadowRoot(parent, backend_id=55), "shadow roots should compare by backend identity")
    assert_in("<ShadowRoot in", repr(shadow), "shadow root repr should identify its parent")

    calls = []
    marker = object()

    def shadow_find(locator, *args, **kwargs):
        index = kwargs.get("index", 1)
        calls.append(("shadow", locator, index, kwargs.get("relative", False), kwargs.get("timeout")))
        return [marker, "other"] if index is None else marker

    def parent_find(locator, index=1, relative=False, timeout=None, **kwargs):
        calls.append(("parent", locator, index, relative, timeout))
        return [marker, "other"] if index is None else marker

    shadow._ele = shadow_find
    parent._ele = parent_find
    assert_true(shadow.parent(2) is marker, "shadow parent should delegate ancestor-or-self lookup")
    assert_true(shadow.child("tag:span") is marker, "shadow child should delegate relative lookup")
    assert_true(shadow.next("tag:span") is marker, "shadow next should delegate through the host element")
    assert_true(shadow.before("tag:span") is marker, "shadow before should delegate through the host element")
    assert_true(shadow.after("tag:span") is marker, "shadow after should return the requested sibling")
    assert_equal(shadow.children(), [marker, "other"], "shadow children should return all delegated nodes")
    assert_equal(shadow.nexts("tag:span"), [marker, "other"], "shadow nexts should preserve all nodes")
    assert_equal(shadow.befores("tag:span"), [marker, "other"], "shadow befores should preserve all nodes")
    assert_equal(shadow.afters("tag:span"), [marker, "other", marker, "other"],
                 "shadow afters should combine host-next and following nodes")
    assert_true(calls, "shadow traversal should call either the root or host delegate")

    with _replace(chromium_element_module, make_session_ele=lambda *args, **kwargs: "snapshot"):
        assert_equal(shadow.s_ele(), "snapshot", "shadow s_ele() should create a session snapshot")
        assert_equal(shadow.s_eles("tag:span"), "snapshot", "shadow s_eles() should create snapshots after lookup")

    with _replace(chromium_element_module,
                  get_loc=lambda locator: ("ax", "name"),
                  find_by_ax=lambda *args: "ax-result"):
        assert_equal(shadow._find_elements("ignored", .1), "ax-result", "shadow AX lookup should route to find_by_ax")
    with _replace(chromium_element_module,
                  get_loc=lambda locator: ("css selector", ":root > span"),
                  find_by_css=lambda *args: args[2]):
        assert_equal(shadow._find_elements("ignored", .1), " > span", "shadow CSS lookup should strip :root")
    with _replace(chromium_element_module,
                  get_loc=lambda locator: ("xpath", "./span"),
                  find_by_sr_xpath=lambda *args: args[-1]):
        assert_equal(shadow._find_elements("ignored", .1), "./span", "shadow XPath lookup should route to session XPath")
    with _replace(chromium_element_module,
                  get_loc=lambda locator: ("any", "inside"),
                  find_by_sr_any=lambda *args: args[1]):
        assert_equal(shadow._find_elements("ignored", .1), "inside", "shadow text lookup should route to session any")


def _check_find_helper_contracts():
    owner = FakeOwner()
    # The locator dispatcher only needs the small public surface below.
    dispatcher = SimpleNamespace(owner=owner, timeout=.1, css_selector="div#root", _node_id=1, _backend_id=101,
                                 tag="div")
    records = []

    def record(name):
        def call(*args):
            records.append((name, args))
            return name
        return call

    with _replace(chromium_element_module,
                  get_loc=lambda locator: ("xpath", "/span"), find_by_xpath=record("xpath")):
        assert_equal(find_in_chromium_ele(dispatcher, "ignored"), "xpath", "XPath lookup should normalize root paths")
        assert_equal(records[-1][1][1], ". /span".replace(" ", ""), "XPath lookup should become a relative path")
    with _replace(chromium_element_module,
                  get_loc=lambda locator: ("css selector", "> span"), find_by_css=record("css")):
        assert_equal(find_in_chromium_ele(dispatcher, "ignored"), "css", "CSS lookup should route to find_by_css")
        assert_equal(records[-1][1][2], "div#root> span", "direct-child CSS lookup should include the host selector")
    with _replace(chromium_element_module,
                  get_loc=lambda locator: ("ax", "button"), find_by_ax=record("ax")):
        assert_equal(find_in_chromium_ele(dispatcher, "ignored"), "ax", "AX lookup should route to find_by_ax")
    with _replace(chromium_element_module,
                  get_loc=lambda locator: ("any", "label"), find_by_any=record("any")):
        assert_equal(find_in_chromium_ele(dispatcher, "ignored"), "any", "text lookup should route to find_by_any")
    _assert_raises(LocatorError, lambda: find_in_chromium_ele(dispatcher, 3),
                   "locator dispatch should reject non-string/non-tuple values")

    page = FakeOwner()
    enabled_calls = []
    page._enable_domain = lambda name: (enabled_calls.append(name), page._enabled.add(name))
    with _replace(chromium_element_module, wait_for_ele=lambda *args, **kwargs: kwargs):
        result = find_by_ax(page, 1, {"role": "button"}, 1, .1)
    assert_equal(enabled_calls, ["Accessibility"], "AX lookup should enable Accessibility once")
    assert_equal(result["bid"], 1, "AX lookup should preserve its backend node id")

    page._run_cdp = lambda method, **kwargs: {"nodes": []}
    assert_equal(do_find_ax(page, 1, {}, 1), None, "empty AX results should return None")
    page._run_cdp = lambda method, **kwargs: {"nodes": [{"backendDOMNodeId": 81}, {"backendDOMNodeId": 82}]}
    def select_nodes(*args, **kwargs):
        ids = kwargs["_ids"]
        index = kwargs.get("index", 1)
        return ids if index is None else (ids[index - 1] if isinstance(ids, list) else ids)

    with _replace(chromium_element_module, make_chromium_eles=select_nodes):
        assert_equal(do_find_ax(page, 1, {}, 1), 81, "AX index one should use the first backend node")
        assert_equal(do_find_ax(page, 1, {}, 2), 82, "AX positive index should delegate selection")

    css_page = FakeOwner()
    with _replace(chromium_element_module, make_chromium_eles=lambda *args, **kwargs: kwargs["_ids"]):
        assert_equal(do_find_css(css_page, "DOM.querySelector", "span", "nodeId", 1, 1), 77,
                     "CSS index one should wrap the returned node id")
        assert_equal(do_find_css(css_page, "DOM.querySelectorAll", "span", "nodeIds", 1, None), [77, 78],
                     "CSS index none should preserve all node ids")

    class FindElement:
        def __init__(self):
            self.owner = FakeOwner()
            self._obj_id = "obj"

    find_ele = FindElement()
    find_ele.owner._run_cdp = lambda method, **kwargs: _cdp_value("found")
    assert_equal(do_find_xpath(find_ele, "js", "//span", "this", 1), "found",
                 "XPath string results should be returned directly")
    find_ele.owner._run_cdp = lambda method, **kwargs: {"result": {"type": "object", "subtype": "null"}}
    assert_equal(do_find_xpath(find_ele, "js", "//span", "this", 1), None,
                 "XPath null results should return None")
    find_ele.owner._run_cdp = lambda method, **kwargs: {
        "result": {"type": "object", "subtype": "node", "description": "HTMLDivElement", "objectId": "list"}
    }
    with _replace(chromium_element_module, make_chromium_eles=lambda *args, **kwargs: kwargs["_ids"]):
        assert_equal(do_find_xpath(find_ele, "js", "//span", "this", 1), "list",
                     "XPath object results should resolve an element for index one")

    def xpath_properties(method, **kwargs):
        if method == "Runtime.callFunctionOn":
            return {"result": {"type": "object", "subtype": "node", "description": "NodeList(2)",
                                "objectId": "list"}}
        return {"result": [
            {"name": "0", "value": {"type": "object", "objectId": "a"}},
            {"name": "1", "value": {"type": "string", "value": "text"}},
            {"name": "length", "value": {"type": "number", "value": 2}},
        ]}

    find_ele.owner._run_cdp = xpath_properties
    with _replace(chromium_element_module, make_chromium_eles=lambda *args, **kwargs: kwargs["_ids"]):
        assert_equal(do_find_xpath(find_ele, "js", "//span", "this", None), ["a", "text"],
                     "XPath all-results should preserve element and text entries")
        assert_equal(do_find_xpath(find_ele, "js", "//span", "this", -1), "text",
                     "XPath negative indexes should count from the end")

    responses = iter([
        {"result": {"type": "object", "subtype": "null", "description": "The result is not a node set"},
         "exceptionDetails": {"x": 1}},
        _cdp_value("fallback"),
    ])
    find_ele.owner._run_cdp = lambda method, **kwargs: next(responses)
    assert_equal(do_find_xpath(find_ele, "js", "//span", "this", 1), "fallback",
                 "non-node XPath results should retry as scalar XPath")

    with _replace(chromium_element_module,
                  do_find_xpath=lambda *args: None,
                  do_find_css=lambda *args: "css",
                  do_find_sr_xpath=lambda *args: "sr"):
        assert_equal(do_find_any(find_ele, "x", "js", "js1", "xp", "this", "cdp", "css", "arg", 1, 1),
                     "css", "any lookup should fall back from XPath to CSS")
        assert_equal(do_find_sr_any(find_ele, "x", "xp", "cdp", "css", "arg", 1, 1), "sr",
                     "shadow any lookup should fall back to shadow XPath")

    css_item = SimpleNamespace(css_selector="span")
    text_item = "text-node"
    sr = SimpleNamespace(owner=FakeOwner(), _node_id=1)
    with _replace(chromium_element_module,
                  make_session_ele=lambda *args, **kwargs: [css_item, text_item],
                  make_chromium_eles=lambda *args, **kwargs: "resolved"):
        assert_equal(do_find_sr_xpath(sr, "//span", 1), "resolved", "shadow XPath CSS selectors should resolve nodes")
        assert_equal(do_find_sr_xpath(sr, "//span", None), ["resolved", "text-node"],
                     "shadow XPath all results should collect resolved selectors")

    with _replace(chromium_element_module, wait_until=lambda *args, **kwargs: None):
        missing = wait_for_ele(lambda: None, target=owner, timeout=0, index=1)
        all_missing = wait_for_ele(lambda: None, target=owner, timeout=0, index=None)
    assert_true(isinstance(missing, NoneElement), "wait_for_ele should return NoneElement for one missing result")
    assert_true(isinstance(all_missing, ChromiumElementsList), "wait_for_ele should return an empty Chromium list")


def _check_node_factory_contracts():
    page = FakeNodePage()
    page.node_map.update({
        "obj": {"nodeName": "DIV", "nodeId": 1, "backendNodeId": 101, "localName": "div"},
        2: {"nodeName": "#text", "nodeValue": "hello", "nodeId": 2, "backendNodeId": 102, "localName": ""},
        3: {"nodeName": "SPAN", "nodeId": 3, "backendNodeId": 103, "localName": "span"},
    })
    assert_true(isinstance(_get_node_by_obj_id(page, "obj", True), ChromiumElement),
                "object ids should resolve regular elements")
    assert_equal(_get_node_by_node_id(page, 2, False), "hello", "node ids should preserve text when ele_only is false")
    assert_equal(_get_node_by_node_id(page, 2, True), None, "node ids should filter text when ele_only is true")
    assert_true(isinstance(_get_node_by_backend_id(page, 3, True), ChromiumElement),
                "backend ids should resolve regular elements")
    assert_equal(_get_node_info(page, "backendNodeId", 0), False, "empty node ids should return False")
    page._run_cdp = lambda method, **kwargs: {"error": "missing"}
    assert_equal(_get_node_info(page, "nodeId", 4), False, "CDP node errors should return False")

    page = FakeNodePage()
    page.node_map.update({
        1: {"nodeName": "DIV", "nodeId": 1, "backendNodeId": 101, "localName": "div"},
        2: {"nodeName": "#text", "nodeValue": "text", "nodeId": 2, "backendNodeId": 102, "localName": ""},
        3: {"nodeName": "SPAN", "nodeId": 3, "backendNodeId": 103, "localName": "span"},
    })
    all_nodes = make_chromium_eles(page, [1, 2, 3], index=None, id_type="node_id")
    assert_equal(len(all_nodes), 3, "node factory should preserve all entries when ele_only is false")
    assert_equal(len(make_chromium_eles(page, [1, 2, 3], index=None, id_type="node_id", ele_only=True)), 2,
                 "node factory should filter text entries for ele_only")
    assert_true(isinstance(make_chromium_eles(page, [1, 3], index=-1, id_type="node_id"), ChromiumElement),
                "node factory should support negative indexes")
    assert_true(isinstance(_make_ele(page, "obj", {"node": page.node_map[1]}), ChromiumElement),
                "_make_ele should preserve ordinary element types")

    for type_txt in ("9", "7", "2", "1", "3"):
        script = make_js_for_find_ele_by_xpath("//div[@id='a']", type_txt, "this")
        assert_in("document.evaluate", script, "XPath helper should emit an evaluate call")
    assert_in("return e.singleNodeValue", make_js_for_find_ele_by_xpath("//div", "9", "this"),
              "XPath helper should return the first node result")


def _check_javascript_result_contracts():
    owner = FakeOwner()
    element = _element(owner)
    assert_equal(convert_argument(element), {"objectId": "object-1"}, "element arguments should use object ids")
    for value in (1, 1.5, "text", True, {"ok": True}):
        assert_equal(convert_argument(value), {"value": value}, "JSON-compatible arguments should use value payloads")
    _assert_raises(TypeError, lambda: convert_argument([1, 2]), "unsupported argument containers should be rejected")

    page = FakeOwner()
    page.states.has_alert = False
    page._run_cdp = lambda method, **kwargs: _cdp_value(6)
    with TemporaryDirectory() as directory:
        script_path = Path(directory) / "script.js"
        script_path.write_text("6 + 5", encoding="utf-8")
        assert_equal(run_js(page, str(script_path), True, .2), 6,
                     "page expression execution should read JavaScript files")
    page.states.has_alert = True
    _assert_raises(AlertExistsError, lambda: run_js(page, "1", True, .1),
                   "alert state should block JavaScript execution")

    assert_equal(parse_js_result(page, element, {"unserializableValue": "NaN"}, 999), "NaN",
                 "unserializable CDP values should be returned verbatim")
    assert_equal(parse_js_result(page, element, {"type": "object", "subtype": "null"}, 999), None,
                 "null object results should become None")
    assert_equal(parse_js_result(page, element, {"type": "undefined"}, 999), None,
                 "undefined results should become None")
    assert_equal(parse_js_result(page, element, {"type": "function", "description": "function () {}"}, 999),
                 "function () {}", "function results should expose their description")
    assert_equal(parse_js_result(page, element, {"type": "number", "value": 3}, 999), 3,
                 "primitive results should expose their value")
    assert_equal(parse_js_result(page, element, {"type": "object", "subtype": "node", "className": "HTMLDocument",
                                                 "objectId": "document"}, 999)["className"], "HTMLDocument",
                 "document node results should remain CDP dictionaries")

    def object_results(method, **kwargs):
        if method == "Runtime.getProperties":
            return {"result": [
                {"name": "0", "value": {"type": "number", "value": 1}},
                {"name": "1", "value": {"type": "string", "value": "two"}},
            ]}
        if method == "IO.resolveBlob":
            return {"uuid": "blob-uuid"}
        if method == "IO.read":
            return {"data": "blob-data"}
        return _cdp_value('{"ok": true}')

    page._run_cdp = object_results
    assert_equal(parse_js_result(page, element, {"type": "object", "subtype": "array", "objectId": "array"}, 999),
                 [1, "two"], "array object results should recursively decode indexed properties")
    future = perf_counter() + 1
    assert_equal(parse_js_result(page, element, {"type": "object", "className": "Blob", "objectId": "blob"}, future),
                 "blob-data", "blob results should read their IO payload")
    assert_equal(parse_js_result(page, element, {"type": "object", "objectId": "json"}, future), {"ok": True},
                 "object results should JSON-decode serialized values")

    with _replace(chromium_element_module, make_chromium_eles=lambda *args, **kwargs: "resolved"):
        assert_equal(parse_js_result(page, element, {"type": "object", "subtype": "node", "className": "HTMLDivElement",
                                                     "objectId": "element"}, 999), "resolved",
                     "ordinary node results should resolve Chromium elements")
    page.states.has_alert = False
    page._run_cdp = lambda method, **kwargs: (_ for _ in ()).throw(ContextLostError())
    _assert_raises(ContextLostError, lambda: run_js(page, "1", True, .1),
                   "context-loss responses should be surfaced to page callers")


def _check_predicate_and_pseudo_contracts():
    predicate = SimpleNamespace(attrs={"id": "main", "class": "alpha beta"}, tag="div",
                                raw_text="hello world", text="hello world")
    assert_true(_check_ele(predicate, {"and": True, "args": [
        ("id", "=", "main", False), ("class", ":", "alpha", False), ("id", "^", "ma", False),
        ("class", "$", "beta", False), ("tag()", "=", "div", False), ("text()", ":", "hello", False),
    ]}), "AND predicates should support equality, containment, prefix, suffix, tag, and text")
    assert_false(_check_ele(predicate, {"and": True, "args": [("id", "=", "main", True)]}),
                 "denied AND predicates should fail on a matching value")
    assert_true(_check_ele(predicate, {"and": False, "args": [
        ("id", "missing", "=", False), ("class", "alpha", ":", False),
    ]}), "OR predicates should succeed when any condition matches")
    assert_true(_check_ele(SimpleNamespace(attrs={}, tag="div", raw_text="", text=""),
                           {"and": False, "args": [(None, "anything", "=", False)]}),
                "OR predicates should support an attribute-free element condition")

    values = iter(("content", '"after"'))
    fake_element = SimpleNamespace(style=lambda *args: next(values))
    pseudo = Pseudo(fake_element)
    assert_equal(pseudo.before, '"after"', "pseudo.before should fall back through alternate pseudo syntax")
