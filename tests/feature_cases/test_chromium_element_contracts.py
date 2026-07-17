"""Feature: deterministic ChromiumElement public contracts without a browser."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from DrissionPage._elements.chromium_element import ChromiumElement, Pseudo
from DrissionPage._elements.session_element import SessionElement
from DrissionPage._functions.elements import ChromiumElementsList, SessionElementsList
from DrissionPage._units.clicker import Clicker
from DrissionPage._units.rect import ElementRect
from DrissionPage._units.scroller import ElementScroller
from DrissionPage._units.selector import SelectElement
from DrissionPage._units.setter import ChromiumElementSetter
from DrissionPage._units.states import ElementStates
from DrissionPage._units.waiter import ElementWaiter
from DrissionPage.errors import AlertExistsError, ElementLostError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "chromium_element_contracts"
REQUIRES_BROWSER = False


def run(ctx):
    _check_construction_and_identity()
    _check_content_and_attribute_contracts()
    _check_session_snapshot_contracts()
    _check_accessor_and_setter_wiring()
    _check_traversal_delegation()
    _check_element_actions_and_resources()
    _check_javascript_payloads()


class FakeStates:
    def __init__(self, *, checked=False, has_alert=False):
        self.is_checked = checked
        self.has_alert = has_alert


class FakeRect:
    midpoint = (12, 18)
    location = (10, 15)
    size = (40, 20)


class FakeActions:
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


class FakeDriver:
    def __init__(self, owner):
        self.owner = owner
        self.calls = []

    def run(self, method, **kwargs):
        self.calls.append((method, kwargs))

        if method == "DOM.resolveNode":
            source = kwargs.get("nodeId", kwargs.get("backendNodeId"))
            return {"object": {"objectId": f"object-for-{source}"}}
        if method == "DOM.requestNode":
            return {"nodeId": self.owner.request_node_id}
        if method == "DOM.describeNode":
            return {"node": {
                "nodeId": kwargs.get("nodeId", self.owner.request_node_id),
                "backendNodeId": kwargs.get("backendNodeId", self.owner.describe_backend_id),
                "localName": self.owner.local_name,
            }}
        if method == "DOM.getAttributes":
            if self.owner.lose_attributes_once:
                self.owner.lose_attributes_once = False
                raise ElementLostError
            flattened = [item for pair in self.owner.attributes.items() for item in pair]
            return {"attributes": flattened}
        if method == "DOM.getOuterHTML":
            html = self.owner.document_html if kwargs.get("objectId") == "document-object" else self.owner.element_html
            return {"outerHTML": html}
        if method in {"DOM.setAttributeValue", "DOM.focus", "DOM.setFileInputFiles"}:
            return {}
        if method == "Runtime.evaluate":
            return _cdp_value(11)
        if method == "Runtime.callFunctionOn":
            return self._run_javascript(kwargs["functionDeclaration"])
        raise AssertionError(f"unexpected CDP call: {method} {kwargs!r}")

    def _run_javascript(self, script):
        if "return this.ownerDocument;" in script:
            return {"result": {
                "type": "object",
                "subtype": "node",
                "className": "HTMLDocument",
                "objectId": "document-object",
            }}
        if "return path.substr(1);" in script:
            return _cdp_value("html>body>div:nth-child(1)")
        if "return path;" in script:
            return _cdp_value("/html/body/div")
        if "return this.innerHTML;" in script:
            return _cdp_value(self.owner.inner_html)
        if "return this.innerText;" in script:
            return _cdp_value(self.owner.raw_text)
        if "return this.baseURI;" in script:
            return _cdp_value(self.owner.base_uri)
        if "return this.value;" in script:
            return _cdp_value(self.owner.value)
        if "return this.encoded;" in script:
            return _cdp_value("A &amp; B")
        if "return this.broken;" in script:
            raise RuntimeError("simulated unavailable property")
        if "getComputedStyle" in script:
            if '"::before"' in script:
                return _cdp_value('"before-value"')
            if '"::after"' in script:
                return _cdp_value('"after-value"')
            return _cdp_value("grid")
        if "this.complete &&" in script:
            return _cdp_value(True)
        if "return 7;" in script:
            return _cdp_value(7)
        return _cdp_value(None)


class FakeOwner:
    def __init__(self, *, local_name="div", attributes=None):
        self._tab = SimpleNamespace(tab_id="tab-1")
        self.timeout = 0.02
        self.timeouts = SimpleNamespace(script=0.25)
        self.states = FakeStates()
        self.rect = SimpleNamespace(size=(1280, 720))
        self.actions = FakeActions()
        self.wait = SimpleNamespace(doc_loaded=lambda: True)
        self._none_ele_value = None
        self._none_ele_return_value = False
        self.local_name = local_name
        self.request_node_id = 31
        self.describe_backend_id = 41
        self.lose_attributes_once = False
        self.base_uri = "https://example.test/base/page/"
        self.value = "field-value"
        self.raw_text = "Hello world\nline"
        self.inner_html = "Hello <span id='child'>world</span><br>line"
        self.element_html = (
            "<div id='main' href='../next' src='img.png' data-label='A &amp; B'>"
            f"{self.inner_html}</div>"
        )
        self.document_html = f"<html><body>{self.element_html}</body></html>"
        self.attributes = attributes or {
            "id": "main",
            "href": "../next",
            "src": "img.png",
            "data-label": "A & B",
        }
        self._driver = FakeDriver(self)

    @property
    def calls(self):
        return self._driver.calls

    @property
    def html(self):
        return self.document_html

    @property
    def url(self):
        return self.base_uri

    def _run_cdp(self, method, **kwargs):
        return self._driver.run(method, **kwargs)


class FakeClick:
    def __init__(self):
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1


def _cdp_value(value):
    if value is None:
        result = {"type": "undefined"}
    elif isinstance(value, bool):
        result = {"type": "boolean", "value": value}
    elif isinstance(value, (int, float)):
        result = {"type": "number", "value": value}
    else:
        result = {"type": "string", "value": value}
    return {"result": result}


def _element(owner=None, *, node_id=1, obj_id="object-1", backend_id=101):
    return ChromiumElement(owner or FakeOwner(), node_id=node_id, obj_id=obj_id, backend_id=backend_id)


def _assert_raises(error_type, func, message):
    try:
        func()
    except error_type:
        return
    raise AssertionError(message)


def _last_call(owner, method):
    return next(call for call in reversed(owner.calls) if call[0] == method)


def _check_construction_and_identity():
    owner = FakeOwner()
    direct = _element(owner)
    assert_true(direct.owner is owner, "element construction should preserve its owner")
    assert_true(direct.tab is owner._tab, "element construction should expose the owner's tab")
    assert_equal((direct._node_id, direct._obj_id, direct._backend_id), (1, "object-1", 101),
                 "complete DOM identities should be retained")
    assert_equal(owner.calls, [], "complete DOM identities should not require a CDP lookup")

    by_node = ChromiumElement(owner, node_id=7)
    assert_equal((by_node._node_id, by_node._obj_id, by_node._backend_id),
                 (7, "object-for-7", owner.describe_backend_id),
                 "node-id construction should resolve object and backend identities")
    assert_in(("DOM.resolveNode", {"nodeId": 7}), owner.calls,
              "node-id construction should resolve the exact node")
    assert_in(("DOM.describeNode", {"nodeId": 7}), owner.calls,
              "node-id construction should describe the exact node")

    by_object = ChromiumElement(owner, obj_id="remote-object")
    assert_equal((by_object._node_id, by_object._obj_id, by_object._backend_id),
                 (owner.request_node_id, "remote-object", owner.describe_backend_id),
                 "object-id construction should request the node and backend identities")
    by_backend = ChromiumElement(owner, backend_id=88)
    assert_equal((by_backend._node_id, by_backend._obj_id, by_backend._backend_id),
                 (owner.request_node_id, "object-for-88", 88),
                 "backend-id construction should resolve the object and node identities")
    _assert_raises(ElementLostError, lambda: ChromiumElement(owner),
                   "construction without a DOM identity should fail as a lost element")

    same = _element(FakeOwner(), backend_id=101)
    different = _element(FakeOwner(), backend_id=102)
    assert_true(direct == same, "elements for the same backend node should compare equal")
    assert_false(direct == different, "elements for different backend nodes should not compare equal")
    assert_false(direct == object(), "an unrelated object should not compare equal to an element")


def _check_content_and_attribute_contracts():
    owner = FakeOwner()
    element = _element(owner)
    assert_equal(element.tag, "div", "tag should expose the lower-case DOM local name")
    first_tag_calls = len([call for call in owner.calls if call[0] == "DOM.describeNode"])
    assert_equal(element.tag, "div", "tag should remain stable on repeated access")
    assert_equal(len([call for call in owner.calls if call[0] == "DOM.describeNode"]), first_tag_calls,
                 "repeated tag access should use the resolved value")
    assert_equal(element.html, owner.element_html, "html should expose outerHTML")
    assert_equal(element.inner_html, owner.inner_html, "inner_html should expose the DOM innerHTML value")
    assert_equal(element.text, "Hello world\nline", "text should format a snapshot of outerHTML")
    assert_equal(element.raw_text, owner.raw_text, "raw_text should expose innerText")
    assert_equal(element.attrs, owner.attributes, "attrs should pair CDP attribute names and values")
    assert_equal(element.attr("href"), "https://example.test/base/next",
                 "href should resolve against the DOM base URI")
    assert_equal(element.attr("src"), "https://example.test/base/page/img.png",
                 "src should resolve against the DOM base URI")
    assert_equal(element.link, "https://example.test/base/next", "link should prefer href")
    assert_equal(element.attr("text"), element.text, "text pseudo-attribute should expose formatted text")
    assert_equal(element.attr("innerText"), owner.raw_text, "innerText pseudo-attribute should expose raw text")
    assert_equal(element.attr("outerHTML"), owner.element_html,
                 "outerHTML pseudo-attribute should expose element HTML")
    assert_equal(element.attr("innerHTML"), owner.inner_html,
                 "innerHTML pseudo-attribute should expose inner HTML")
    assert_equal(element.attr("data-label"), "A & B", "ordinary attributes should retain their value")
    assert_equal(element.property("encoded"), "A & B", "string properties should decode HTML entities")
    assert_equal(element.property("broken"), None, "unavailable properties should return None")
    assert_equal(element.style("display"), "grid", "style should expose computed property values")
    assert_equal(element.value, owner.value, "value should delegate to the DOM property")
    assert_true("<ChromiumElement div " in repr(element), "repr should identify the element type and tag")
    assert_in("id='main'", repr(element), "repr should include public attributes")

    owner.attributes["href"] = "javascript:void(0)"
    assert_equal(element.attr("href"), "javascript:void(0)",
                 "non-navigation JavaScript hrefs should remain unchanged")
    owner.attributes["href"] = ""
    assert_equal(element.link, "https://example.test/base/page/img.png",
                 "link should fall back to src when href is empty")

    recovering_owner = FakeOwner()
    recovering_owner.lose_attributes_once = True
    recovering = _element(recovering_owner, node_id=2, obj_id="stale-object", backend_id=202)
    assert_equal(recovering.attrs, recovering_owner.attributes,
                 "attrs should refresh identities after an element-lost response")
    assert_equal((recovering._node_id, recovering._obj_id),
                 (recovering_owner.request_node_id, "object-for-202"),
                 "attribute recovery should retain refreshed DOM identities")


def _check_session_snapshot_contracts():
    owner = FakeOwner()
    element = _element(owner)
    snapshot = element.s_ele()
    assert_true(isinstance(snapshot, SessionElement), "s_ele() should return a session snapshot element")
    assert_true(snapshot.owner is owner, "session snapshots should retain the page owner")
    assert_equal((snapshot.tag, snapshot.attr("id"), snapshot.text), ("div", "main", "Hello world\nline"),
                 "session snapshots should preserve tag, attributes, and formatted text")

    original_ele = element.ele
    element.ele = lambda locator, index=1, timeout=None: original_ele if index == 1 else None
    child = element.s_ele("tag:span")
    children = element.s_eles("tag:span")
    assert_equal((child.tag, child.attr("id"), child.text), ("span", "child", "world"),
                 "s_ele(locator) should query within the current element snapshot")
    assert_true(isinstance(children, SessionElementsList), "s_eles() should return a session element list")
    assert_equal([item.attr("id") for item in children], ["child"],
                 "s_eles(locator) should return all matching snapshot elements")
    owner_document_calls = [call for call in owner.calls
                            if call[0] == "Runtime.callFunctionOn"
                            and "ownerDocument" in call[1]["functionDeclaration"]]
    assert_equal(len(owner_document_calls), 1, "session snapshots should reuse the resolved owner document")


def _check_accessor_and_setter_wiring():
    owner = FakeOwner()
    element = _element(owner)
    accessors = (
        (element.set, ChromiumElementSetter, "set"),
        (element.states, ElementStates, "states"),
        (element.pseudo, Pseudo, "pseudo"),
        (element.rect, ElementRect, "rect"),
        (element.scroll, ElementScroller, "scroll"),
        (element.click, Clicker, "click"),
        (element.wait, ElementWaiter, "wait"),
    )
    for accessor, expected_type, name in accessors:
        assert_true(isinstance(accessor, expected_type), f"{name} should expose its specialized helper")
        assert_true(accessor is getattr(element, name), f"{name} should preserve helper state between accesses")

    assert_equal(element.pseudo.before, '"before-value"', "pseudo.before should query computed content")
    assert_equal(element.pseudo.after, '"after-value"', "pseudo.after should query computed content")
    assert_false(element.select, "non-select elements should not expose a selector helper")
    select = _element(FakeOwner(local_name="select"))
    assert_true(isinstance(select.select, SelectElement), "select elements should expose a selector helper")
    assert_true(select.select is select.select, "selector helper state should be preserved")

    assert_equal(element.set.attr("role", "button"), None, "attribute setter should be command-like")
    assert_in(("DOM.setAttributeValue", {"nodeId": 1, "name": "role", "value": "button"}), owner.calls,
              "attribute setter should target the element's exact node id")
    assert_equal(element.set.property("title", 'a"b'), None, "property setter should be command-like")
    assert_equal(element.set.style("backgroundColor", "red"), None, "style setter should be command-like")
    assert_equal(element.set.innerHTML("<b>new</b>"), None, "innerHTML setter should be command-like")
    assert_equal(element.set.value("new value"), None, "value setter should be command-like")
    scripts = [call[1]["functionDeclaration"] for call in owner.calls if call[0] == "Runtime.callFunctionOn"]
    assert_in('function(){this.title="a\\"b";}', scripts,
              "property setter should escape quotes in its JavaScript payload")
    assert_in('function(){this.style.backgroundColor="red";}', scripts,
              "style setter should target the requested style property")


def _check_traversal_delegation():
    owner = FakeOwner()
    element = _element(owner)
    marker = object()
    calls = []

    def find(locator, timeout, index=1, relative=False, raise_err=None):
        calls.append((locator, timeout, index, relative, raise_err))
        return [marker, "text", "   "] if index is None else marker

    element._find_elements = find
    assert_true(element("tag:child", index=2, timeout=0.1) is marker,
                "calling an element should delegate to ele()")
    assert_true(element.parent(2, timeout=0.2) is marker, "parent should return the delegated result")
    assert_true(element.child(2, timeout=0.3) is marker, "child(index) should return the delegated result")
    assert_true(element.prev(2, timeout=0.4) is marker, "prev(index) should return the delegated result")
    assert_true(element.next(3, timeout=0.5) is marker, "next(index) should return the delegated result")
    assert_true(element.before(4, timeout=0.6) is marker, "before(index) should return the delegated result")
    assert_true(element.after(5, timeout=0.7) is marker, "after(index) should return the delegated result")

    collections = (
        element.children(timeout=0.8, ele_only=False),
        element.prevs(timeout=0.9, ele_only=False),
        element.nexts(timeout=1.0, ele_only=False),
        element.befores(timeout=1.1, ele_only=False),
        element.afters(timeout=1.2, ele_only=False),
    )
    for collection in collections:
        assert_true(isinstance(collection, ChromiumElementsList),
                    "multi-element traversal should preserve Chromium collection helpers")
        assert_true(collection._owner is owner, "traversal collections should retain their owner")
        assert_equal(collection, [marker, "text"], "traversal should discard whitespace-only text nodes")

    assert_equal(calls[:7], [
        ("tag:child", 0.1, 2, False, None),
        ("xpath:./ancestor::*[2]", 0.2, 1, True, False),
        ("xpath:./*", 0.3, 2, True, False),
        ("xpath:./preceding-sibling::*", 0.4, -2, True, False),
        ("xpath:./following-sibling::*", 0.5, 3, True, False),
        ("xpath:./preceding::*", 0.6, -4, True, False),
        ("xpath:./following::*", 0.7, 5, True, False),
    ], "single-element traversal should delegate normalized relative queries")


def _check_element_actions_and_resources():
    owner = FakeOwner(local_name="input", attributes={"type": "text"})
    element = _element(owner)
    assert_true(element.input([1, "x"], clear=True, by_js=True) is element,
                "JavaScript input should remain chainable")
    scripts = [call[1]["functionDeclaration"] for call in owner.calls if call[0] == "Runtime.callFunctionOn"]
    assert_in("function(){this.value='';}", scripts, "JavaScript clear should empty the value")
    assert_in('function(){this.value="1x";}', scripts, "JavaScript input should normalize list values to text")
    assert_true(element.remove_attr("disabled") is element, "remove_attr should remain chainable")
    assert_in('function(){this.removeAttribute("disabled");}',
              [call[1]["functionDeclaration"] for call in owner.calls if call[0] == "Runtime.callFunctionOn"],
              "remove_attr should emit a scoped DOM mutation")

    click = FakeClick()
    element._states = FakeStates(checked=False)
    element._clicker = click
    assert_true(element.check(True) is element, "check should remain chainable")
    assert_equal(click.calls, 1, "check should click only when the requested state differs")
    element._states = FakeStates(checked=True)
    assert_true(element.check(False, by_js=True) is element, "JavaScript uncheck should remain chainable")
    assert_in('function(){this.checked=false;this.dispatchEvent(new Event("change", {bubbles: true}));}',
              [call[1]["functionDeclaration"] for call in owner.calls if call[0] == "Runtime.callFunctionOn"],
              "JavaScript uncheck should update state and dispatch change")

    assert_true(element.focus() is element, "focus should remain chainable")
    assert_in(("DOM.focus", {"backendNodeId": 101}), owner.calls,
              "focus should identify the exact backend node")
    assert_true(element.hover(offset_x=2, offset_y=3) is element, "hover should remain chainable")
    assert_equal(owner.actions.calls[-1], ("move_to", element, 2, 3, 0.1),
                 "hover should delegate its offsets to page actions")

    file_owner = FakeOwner(local_name="input", attributes={"type": "file"})
    file_element = _element(file_owner)
    assert_true(file_element.input(("relative-upload.txt", Path("/tmp/absolute-upload.txt"))) is file_element,
                "file input should remain chainable")
    file_call = _last_call(file_owner, "DOM.setFileInputFiles")
    assert_equal(file_call[1], {
        "files": [str(Path("relative-upload.txt").resolve()), str(Path("/tmp/absolute-upload.txt").resolve())],
        "backendNodeId": 101,
    }, "file input should send normalized absolute paths for the exact element")

    image_owner = FakeOwner(local_name="img", attributes={
        "src": "data:image/png;base64,aGVsbG8=",
    })
    image = _element(image_owner)
    assert_equal(image.src(timeout=0), b"hello", "data-image src should decode to bytes by default")
    assert_equal(image.src(timeout=0, base64_to_bytes=False), "aGVsbG8=",
                 "data-image src should expose base64 text when requested")


def _check_javascript_payloads():
    owner = FakeOwner()
    element = _element(owner)
    argument_element = _element(FakeOwner(), obj_id="argument-object", backend_id=202)
    assert_equal(element.run_js("return 7;", argument_element, 3, "text", {"ok": True}, timeout=0.4), 7,
                 "run_js should return the decoded CDP value")
    method, payload = _last_call(owner, "Runtime.callFunctionOn")
    assert_equal(method, "Runtime.callFunctionOn", "run_js should call the element-scoped runtime method")
    assert_equal(payload, {
        "functionDeclaration": "function(){return 7;}",
        "objectId": "object-1",
        "arguments": [
            {"objectId": "argument-object"},
            {"value": 3},
            {"value": "text"},
            {"value": {"ok": True}},
        ],
        "returnByValue": False,
        "awaitPromise": True,
        "userGesture": True,
        "_timeout": 0.4,
        "_ignore": AlertExistsError,
    }, "run_js should preserve object identities and supported argument payloads")

    assert_equal(element.run_js("6 + 5", as_expr=True, timeout=0.3), 11,
                 "expression mode should return the evaluated value")
    _, expression_payload = _last_call(owner, "Runtime.evaluate")
    assert_equal({key: expression_payload[key] for key in (
        "expression", "returnByValue", "awaitPromise", "userGesture", "_timeout"
    )}, {
        "expression": "6 + 5",
        "returnByValue": False,
        "awaitPromise": True,
        "userGesture": True,
        "_timeout": 0.3,
    }, "expression mode should send a bounded Runtime.evaluate payload")
    assert_equal(element.run_async_js("return 7;"), None, "async JavaScript dispatch should be command-like")
    _, async_payload = _last_call(owner, "Runtime.callFunctionOn")
    assert_equal(async_payload["_timeout"], 0, "async JavaScript dispatch should use a non-blocking timeout")
