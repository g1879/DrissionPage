"""Feature: deterministic collection filtering and action dispatch contracts."""
from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from DrissionPage._elements.none_element import NoneElement
from DrissionPage._functions.elements import ChromiumElementsList, SessionElementsList, get_eles, get_frame
from DrissionPage._functions.keys import Keys
from DrissionPage._units.actions import Actions, location_to_client

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "collection_action_contracts"
REQUIRES_BROWSER = False


class FakeStates:
    def __init__(self, *, displayed=True, checked=False, selected=False, enabled=True, clickable=True, rect=True):
        self.is_displayed = displayed
        self.is_checked = checked
        self.is_selected = selected
        self.is_enabled = enabled
        self.is_clickable = clickable
        self.has_rect = rect


class FakeElement:
    _type = "ChromiumElement"

    def __init__(self, tag, text, *, attrs=None, styles=None, props=None, states=None, link=None):
        self.tag = tag
        self.raw_text = text
        self.text = text.strip()
        self.link = link
        self.states = states or FakeStates()
        self._attrs = attrs or {}
        self._styles = styles or {}
        self._props = props or {}

    def attr(self, name):
        return self._attrs.get(name)

    def style(self, name):
        return self._styles.get(name)

    def property(self, name):
        return self._props.get(name)


class FakeFrame:
    _type = "ChromiumFrame"

    def __bool__(self):
        return True


def _expect_raises(exc_type, func, message):
    try:
        func()
    except exc_type:
        return
    raise AssertionError(message)


def test_element_collections():
    owner = type("Owner", (), {"_none_ele_value": None, "_none_ele_return_value": False})()
    first = FakeElement(
        "div",
        " Alpha ",
        attrs={"role": "item", "id": "first"},
        styles={"color": "red"},
        props={"value": "A"},
        states=FakeStates(displayed=True, checked=True, selected=False, enabled=True, clickable=True, rect=True),
        link="https://example.test/first",
    )
    second = FakeElement(
        "span",
        "Beta",
        attrs={"role": "note", "id": "second"},
        styles={"color": "blue"},
        props={"value": "B"},
        states=FakeStates(displayed=False, checked=False, selected=True, enabled=False, clickable=False, rect=False),
        link="https://example.test/second",
    )
    third = FakeElement("div", "Gamma", attrs={"role": "item", "id": "third"}, states=FakeStates())

    items = SessionElementsList(owner, [first, "raw text", second, third])
    assert_equal(items[0], first, "integer indexing should return the stored element")
    sliced = items[1:3]
    assert_true(isinstance(sliced, SessionElementsList), "slicing should preserve the collection type")
    assert_true(sliced._owner is owner, "slicing should preserve the owner")
    assert_equal(sliced, ["raw text", second], "slicing should preserve values")
    _expect_raises(ValueError, lambda: items["bad"], "non-integer collection indexes should fail")

    element_items = SessionElementsList(owner, [first, second, third])
    assert_equal(element_items.texts, ["Alpha", "Beta", "Gamma"], "texts should expose element text")
    assert_equal(items.get.links(), [first.link, second.link, third.link], "links() should ignore string nodes")
    assert_equal(items.get.texts(), ["Alpha", "raw text", "Beta", "Gamma"], "Getter.texts() should include text nodes")
    assert_equal(items.get.attrs("role"), ["item", "note", "item"], "attrs() should query element attributes")

    assert_equal(list(items.filter.tag("DIV")), [first, third], "tag filter should be case-insensitive")
    assert_equal(list(items.filter.tag("div", equal=False)), [second], "negative tag filter should exclude strings")
    assert_equal(list(items.filter.text("a", fuzzy=True)), [first, "raw text", second, third],
                 "fuzzy text filtering should use raw text")
    assert_equal(list(items.filter.text("Beta", fuzzy=False)), [second], "exact text filtering should match one element")
    assert_equal(list(items.filter.text("Beta", fuzzy=False, contain=False)), [first, "raw text", third],
                 "negative exact text filtering should retain non-matches")
    assert_equal(list(items.filter.attr("role", "item")), [first, third], "attribute filter should return matches")
    assert_equal(list(items.filter.attr("role", "item", equal=False)), [second], "negative attribute filter should work")
    assert_equal(items.filter_one.tag("div"), first, "filter_one.tag() should return the first match")
    assert_equal(items.filter_one(2).tag("div"), third, "filter_one(index) should select the indexed match")
    assert_equal(items.filter_one.text("raw", fuzzy=True), "raw text", "filter_one.text() should support strings")
    assert_equal(items.filter_one.attr("id", "second"), second, "filter_one.attr() should query attributes")
    assert_false(items.filter_one.tag("missing"), "missing filter_one results should be NoneElement-compatible")

    chromium = ChromiumElementsList(owner, [first, "raw text", second, third])
    assert_equal(list(chromium.filter.displayed()), [first, third], "displayed filter should keep displayed elements")
    assert_equal(list(chromium.filter.displayed(False)), [second], "negative displayed filter should work")
    assert_equal(list(chromium.filter.checked()), [first], "checked filter should inspect element states")
    assert_equal(list(chromium.filter.selected()), [second], "selected filter should inspect element states")
    assert_equal(list(chromium.filter.enabled(False)), [second], "enabled(False) should keep disabled elements")
    assert_equal(list(chromium.filter.clickable(False)), [second], "clickable(False) should keep non-clickable elements")
    assert_equal(list(chromium.filter.have_rect(False)), [second], "have_rect(False) should keep rect-less elements")
    assert_equal(list(chromium.filter.style("color", "red")), [first], "style filter should query styles")
    assert_equal(list(chromium.filter.property("value", "B")), [second], "property filter should query properties")
    assert_equal(chromium.filter_one.checked(), first, "filter_one.checked() should return a matching element")
    assert_equal(chromium.filter_one.checked(False), second, "negative state filter_one should work")
    assert_false(chromium.filter_one(9).displayed(), "out-of-range state filter should return NoneElement")

    assert_equal(list(chromium.search(displayed=False)), [second], "search() should apply state predicates")
    assert_equal(list(chromium.search(have_text=True, tag="span")), [first, second, third],
                 "search() uses OR semantics across requested predicates")
    assert_equal(chromium.search_one(selected=True), second, "search_one() should return the first predicate match")
    assert_equal(chromium.search_one(index=2, displayed=True), third, "search_one(index) should select later matches")
    assert_false(chromium.search_one(tag="missing"), "missing search_one result should be NoneElement-compatible")


def test_element_lookup_helpers():
    class LookupOwner:
        def __init__(self):
            self.calls = []
            self._none_ele_value = None
            self._none_ele_return_value = False

        def _ele(self, loc, **kwargs):
            self.calls.append((loc, kwargs))
            if loc in ("#one", ("css selector", "#one")):
                return "first-result"
            if loc == "frame-name":
                return FakeFrame()
            if isinstance(loc, str) and loc.startswith("xpath://*"):
                return FakeFrame()
            if isinstance(loc, tuple) and loc == ("css selector", "iframe"):
                return FakeFrame()
            if loc == "@|tag():iframe@|tag():frame":
                return FakeFrame()
            return NoneElement(self, "_ele", args={"loc": loc})

    owner = LookupOwner()
    results = get_eles(["#one", "#missing"], owner, timeout=0)
    assert_equal(results["#one"], "first-result", "get_eles() should store successful results")
    assert_false(results["#missing"], "get_eles() should preserve missing NoneElement-compatible results")
    any_result = get_eles(["#one", "#missing"], owner, any_one=True, timeout=0)
    assert_equal(any_result["#one"], "first-result", "any_one lookup should stop after the first success")
    tuple_result = get_eles(("css selector", "#one"), owner, timeout=0)
    assert_equal(tuple_result[("css selector", "#one")], "first-result", "selenium locator tuple should be one locator")

    assert_true(isinstance(get_frame(owner, "frame-name"), FakeFrame), "frame name should build a frame locator")
    assert_true(isinstance(get_frame(owner, ("css selector", "iframe")), FakeFrame), "tuple frame locator should work")
    assert_true(isinstance(get_frame(owner, 1), FakeFrame), "integer frame locator should use the indexed frame query")
    frame = FakeFrame()
    assert_true(get_frame(owner, frame) is frame, "existing ChromiumFrame should pass through")
    missing = get_frame(owner, "#missing")
    assert_false(missing, "missing frame should remain NoneElement-compatible")
    assert_equal(missing.method, "get_frame()", "missing frame should identify the public helper")
    _expect_raises(ValueError, lambda: get_frame(owner, object()), "unsupported frame locators should fail")

    class WrongOwner(LookupOwner):
        def _ele(self, loc, **kwargs):
            return FakeElement("div", "not a frame")

    _expect_raises(Exception, lambda: get_frame(WrongOwner(), "#frame"), "non-frame matches should fail")


class FakeRect:
    midpoint = (100, 120)
    location = (90, 110)
    viewport_midpoint = (50, 60)
    viewport_location = (40, 50)


class FakeActionElement:
    _type = "ChromiumElement"
    rect = FakeRect()


class FakeScroll:
    def __init__(self):
        self.seen = []
        self.locations = []

    def to_see(self, ele):
        self.seen.append(ele)

    def to_location(self, x, y):
        self.locations.append((x, y))


class FakeActionOwner:
    def __init__(self):
        self.cdp_calls = []
        self.js_calls = []
        self.wait_calls = []
        self.scroll = FakeScroll()
        self.element = FakeActionElement()
        self.in_viewport = True

    def __call__(self, locator):
        return self.element

    def _run_cdp(self, method, **kwargs):
        self.cdp_calls.append((method, kwargs))

    def _run_js(self, script, *args):
        self.js_calls.append((script, args))
        if "clientWidth" in script:
            return 800
        if "clientHeight" in script:
            return 600
        if "scrollLeft" in script and script.strip().startswith("return"):
            return 5
        if "scrollTop" in script and script.strip().startswith("return"):
            return 7
        if "function(){let x" in script:
            return self.in_viewport
        return True

    def wait(self, *, second, scope=None):
        self.wait_calls.append((second, scope))


def test_actions_dispatch():
    owner = FakeActionOwner()
    actions = Actions(owner)

    assert_true(actions.move(10, 20, duration=0) is actions, "move() should be chainable")
    method, payload = owner.cdp_calls[-1]
    assert_equal(method, "Input.dispatchMouseEvent", "move() should dispatch a mouse event")
    assert_equal((payload["type"], payload["x"], payload["y"]), ("mouseMoved", 10, 20),
                 "move() should update the cursor location")
    assert_true(actions.move_to((20, 30), offset_x=5, offset_y=7, duration=0) is actions,
                "move_to(tuple) should be chainable")
    assert_equal((actions.curr_x, actions.curr_y), (20, 30), "document coordinates should map through current scroll")
    owner.in_viewport = False
    actions.move_to("#target", duration=0)
    assert_equal(owner.scroll.seen[-1], owner.element, "element move_to() should scroll the element into view")
    assert_equal((actions.curr_x, actions.curr_y), owner.element.rect.viewport_midpoint,
                 "element move_to() should use the viewport midpoint by default")
    owner.in_viewport = True

    assert_true(actions.click(times=2) is actions, "click() should be chainable")
    assert_equal(owner.wait_calls[-1], (0.05, None), "click() should use the owner wait helper")
    assert_equal(owner.cdp_calls[-2][1]["button"], "left", "click() should press the left button")
    assert_equal(owner.cdp_calls[-2][1]["clickCount"], 2, "click(times) should pass clickCount")
    actions.r_click().m_click().hold().release().r_hold().r_release().m_hold().m_release()
    buttons = [payload.get("button") for method, payload in owner.cdp_calls if payload.get("type") in {"mousePressed", "mouseReleased"}]
    assert_in("right", buttons, "right-click helpers should dispatch right button events")
    assert_in("middle", buttons, "middle-click helpers should dispatch middle button events")
    assert_true(actions.scroll(delta_y=120, delta_x=3) is actions, "scroll() should be chainable")
    assert_equal(owner.cdp_calls[-1][1]["type"], "mouseWheel", "scroll() should dispatch a wheel event")
    original_move = actions.move
    directional = []

    def record_move(offset_x=0, offset_y=0, duration=.5):
        directional.append((offset_x, offset_y, duration))
        return actions

    actions.move = record_move
    try:
        actions.up(1).down(2).left(3).right(4)
    finally:
        actions.move = original_move
    assert_equal(directional, [(0, -1, .5), (0, 2, .5), (-3, 0, .5), (4, 0, .5)],
                 "direction helpers should delegate signed offsets to move()")

    actions.key_down(Keys.CONTROL).key_down("a").key_up("a").key_up(Keys.CONTROL)
    assert_equal(actions.modifier, 0, "modifier key_up() should restore modifier state")
    key_events = [payload for method, payload in owner.cdp_calls if method == "Input.dispatchKeyEvent"]
    assert_true(key_events, "key helpers should dispatch key events")
    _expect_raises(ValueError, lambda: actions.key_down("definitely-not-a-key"), "unknown named keys should fail")
    assert_true(actions.type((Keys.SHIFT, "ab"), interval=0) is actions, "type() should be chainable")
    assert_equal(actions.modifier, 0, "type() should release temporary modifiers")
    before = len(owner.cdp_calls)
    actions.input("hello")
    assert_true(len(owner.cdp_calls) > before, "input() should dispatch text input")

    actions.drag_in("#drop", text="payload", title="title", offset_x=2, offset_y=3)
    drag_calls = owner.cdp_calls[-2:]
    assert_equal([payload["type"] for _, payload in drag_calls], ["dragEnter", "drop"],
                 "drag_in() should dispatch enter then drop")
    assert_equal((drag_calls[0][1]["x"], drag_calls[0][1]["y"]), (42, 53),
                 "drag offsets should be based on viewport location")
    assert_equal(drag_calls[0][1]["data"]["items"][0]["title"], "title",
                 "drag title should be preserved")
    with NamedTemporaryFile() as file_obj:
        actions.drag_in("#drop", files=file_obj.name)
        file_data = owner.cdp_calls[-2][1]["data"]
        assert_equal(file_data["files"], [str(Path(file_obj.name).resolve())], "file drag should resolve paths")
    _expect_raises(ValueError, lambda: actions.drag_in("#drop"), "drag_in() requires files or text")
    assert_equal(location_to_client(owner, 25, 37), (20, 30), "location_to_client() should subtract document scroll")


def run(ctx):
    test_element_collections()
    test_element_lookup_helpers()
    test_actions_dispatch()
