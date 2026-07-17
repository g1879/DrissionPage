"""Feature: deterministic edge contracts for small unit helpers."""
from __future__ import annotations

from types import SimpleNamespace

from DrissionPage._units.console import Console
from DrissionPage._units.perm_setter import BrowserPermSetter
from DrissionPage._units.rect import ElementRect, FrameRect, TabRect
from DrissionPage._units.scroller import FrameScroller, PageScroller
from DrissionPage._units.selector import SelectElement
from DrissionPage._units.states import ElementStates, FrameStates, PageStates, ShadowRootStates
from DrissionPage.errors import CDPError, ElementLostError, NoRectError, PageDisconnectedError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "small_unit_edge_contracts"
REQUIRES_BROWSER = False


def _expect_raises(exc_type, func, message):
    try:
        func()
    except exc_type:
        return
    raise AssertionError(message)


def test_permission_methods():
    class Owner:
        def __init__(self):
            self.calls = []

        def _run_cdp(self, method, **kwargs):
            self.calls.append((method, kwargs))

    owner = Owner()
    setter = BrowserPermSetter(owner, "context")
    simple_names = (
        "geolocation", "notifications", "microphone", "background_fetch", "background_sync",
        "persistent_storage", "ambient_light_sensor", "accelerometer", "gyroscope", "magnetometer",
        "screen_wake_lock", "nfc", "display_capture", "payment_handler", "idle_detection",
        "periodic_background_sync", "system_wake_lock", "storage_access", "window_management", "local_fonts",
        "top_level_storage_access", "captured_surface_control", "speaker_selection", "keyboard_lock", "pointer_lock",
        "web_app_installation", "local_network_access", "local_network", "loopback_network",
    )
    for index, name in enumerate(simple_names):
        getattr(setter, name)(allow=index % 2 == 0)
    setter.push(False)
    setter.midi(True, sysex=True)
    setter.midi(False, sysex="ignored")
    setter.camera(True, panTiltZoom=False)
    setter.camera(False, panTiltZoom=None)
    setter.clipboard_read(True, allowWithoutSanitization=True)
    setter.clipboard_read(False, allowWithoutSanitization=None)
    setter.clipboard_write(True, allowWithoutSanitization=False)
    setter.clipboard_write(False, allowWithoutSanitization="ignored")
    setter.fullscreen(False)
    assert_equal(len(owner.calls), len(simple_names) + 10, "every permission method should emit one CDP call")
    assert_true(all(method == "Browser.setPermission" for method, _ in owner.calls),
                "permission methods should use Browser.setPermission")
    assert_true(all(payload["browserContextId"] == "context" for _, payload in owner.calls),
                "context permission calls should preserve browserContextId")
    assert_in(("Browser.setPermission", {
        "permission": {"name": "midi", "sysex": True}, "setting": "granted", "browserContextId": "context",
    }), owner.calls, "midi(sysex=True) should preserve the optional flag")
    assert_in(("Browser.setPermission", {
        "permission": {"name": "fullscreen", "allowWithoutGesture": True},
        "setting": "denied", "browserContextId": "context",
    }), owner.calls, "fullscreen should request gesture-free permission")


class ScrollElement:
    def __init__(self, covered=False):
        self.states = SimpleNamespace(is_covered=covered)
        self.js_calls = []

    def _run_js(self, script):
        self.js_calls.append(script)


class ScrollOwner:
    _type = "ChromiumTab"
    timeout = 0.1

    def __init__(self):
        self.js_calls = []
        self.cdp_calls = 0
        self.element = ScrollElement(covered=True)

    def _run_js(self, script):
        self.js_calls.append(script)

    def _run_cdp(self, method):
        self.cdp_calls += 1
        return {"layoutViewport": {"pageX": 3, "pageY": 4}}

    def _ele(self, locator):
        self.element.locator = locator
        return self.element


def test_scroller_edges():
    owner = ScrollOwner()
    scroll = PageScroller(owner)
    assert_true(scroll.to_bottom() is owner, "to_bottom should return the owner")
    assert_true(scroll.to_half() is owner, "to_half should return the owner")
    assert_true(scroll.to_rightmost() is owner, "to_rightmost should return the owner")
    assert_true(scroll.to_leftmost() is owner, "to_leftmost should return the owner")
    assert_true(scroll.up(8) is owner, "up should return the owner")
    assert_true(scroll.right(9) is owner, "right should return the owner")
    assert_equal(owner.js_calls, [
        "window.scrollTo(document.documentElement.scrollLeft, document.documentElement.scrollHeight);",
        "window.scrollTo(document.documentElement.scrollLeft, document.documentElement.scrollHeight/2);",
        "window.scrollTo(document.documentElement.scrollWidth, document.documentElement.scrollTop);",
        "window.scrollTo(0, document.documentElement.scrollTop);",
        "window.scrollBy(0, -8);",
        "window.scrollBy(9, 0);",
    ], "page scroll helpers should emit exact JS")
    scroll._wait_complete = True
    assert_true(scroll.to_location(1, 2) is owner, "wait-complete scroll should still return the owner")
    assert_true(owner.cdp_calls >= 2, "wait-complete scrolling should poll layout metrics")
    scroll.to_see("#covered", center=None)
    assert_equal(owner.element.locator, "#covered", "to_see should resolve the locator")
    assert_equal(len(owner.element.js_calls), 2, "covered elements should receive native and centering scroll JS")

    doc = ScrollOwner()
    doc._type = "ChromiumElement"
    frame = SimpleNamespace(doc_ele=doc)
    frame_scroll = FrameScroller(frame)
    assert_equal((frame_scroll._t1, frame_scroll._t2), ("this.documentElement", "this.documentElement"),
                 "FrameScroller should target the frame document element")
    assert_true(frame_scroll.to_see("#frame", center=False) is doc,
                "FrameScroller returns the document element owner used by PageScroller")


class Option:
    def __init__(self, text, value, selected=False):
        self.text = text
        self.value = value
        self.states = SimpleNamespace(is_selected=selected)
        self.js_calls = []

    def attr(self, name):
        return self.value if name == "value" else None

    def _run_js(self, script):
        self.js_calls.append(script)
        if script == "this.selected=true;":
            self.states.is_selected = True
        elif script == "this.selected=false;":
            self.states.is_selected = False


class SelectOwner:
    tag = "select"
    timeout = 0

    def __init__(self, *, multiple=True):
        self.multiple = multiple
        self.items = [Option("One", "1"), Option("Two", "2", selected=True), Option("Three", "3")]
        self.js_calls = []

    def attr(self, name):
        return "" if self.multiple else None

    def eles(self, locator, timeout=None):
        if locator == "missing":
            return []
        if locator == "xpath://option":
            return [self.items[0], 1, self.items[1], self.items[2]]
        return list(self.items)

    def _run_js(self, script):
        self.js_calls.append(script)
        if script == "return this.options[this.selectedIndex];":
            return self.items[1]


def test_selector_edges():
    _expect_raises(TypeError, lambda: SelectElement(SimpleNamespace(tag="div")),
                   "SelectElement should reject non-select elements")
    owner = SelectOwner(multiple=True)
    select = SelectElement(owner)
    assert_true(select.is_multi, "multiple attribute should enable multi-select")
    assert_equal(select.options, owner.items, "options should filter non-element sentinels")
    assert_equal(select.selected_option, owner.items[1], "selected_option should return JS-selected option")
    assert_equal(select.selected_options, [owner.items[1]], "selected_options should filter selected states")
    assert_true(select.all() is owner, "all() should select every option")
    assert_true(all(item.states.is_selected for item in owner.items), "all() should select each option")
    assert_true(select.invert() is owner, "invert() should return the select element")
    assert_true(all(not item.states.is_selected for item in owner.items), "invert() should toggle each option")
    assert_true(select.by_text(["One", "Three"]) is owner, "by_text(list) should select multiple options")
    assert_true(select.by_value("2") is owner, "by_value should select matching option values")
    assert_true(select.by_index((-1, 1)) is owner, "by_index should support positive and negative indices")
    assert_true(select.by_locator("tag:option") is owner, "by_locator should select resolved options")
    assert_true(select.cancel_by_text("One") is owner, "cancel_by_text should deselect matches")
    assert_true(select.cancel_by_value("2") is owner, "cancel_by_value should deselect value matches")
    assert_true(select.cancel_by_index(1) is owner, "cancel_by_index should deselect indexed options")
    assert_true(select.cancel_by_locator("tag:option") is owner, "cancel_by_locator should deselect resolved options")
    assert_true(select.by_option(owner.items[0]) is owner, "by_option should select an option object")
    assert_true(select.cancel_by_option(owner.items[0]) is owner, "cancel_by_option should deselect an option object")
    assert_true(select.clear() is owner, "clear() should deselect all multi-select options")
    _expect_raises(RuntimeError, lambda: select.by_locator("missing", timeout=0),
                   "missing option locators should fail")
    _expect_raises(RuntimeError, lambda: select.by_text("Missing", timeout=0),
                   "missing option text should fail")
    _expect_raises(RuntimeError, lambda: select.by_index(99, timeout=0),
                   "out-of-range option index should fail")
    assert_true(owner.js_calls, "selection changes should dispatch change events")

    single_owner = SelectOwner(multiple=False)
    single = SelectElement(single_owner)
    assert_false(single.is_multi, "missing multiple attribute should indicate single select")
    _expect_raises(TypeError, single.all, "all() should reject single-select elements")
    _expect_raises(TypeError, single.invert, "invert() should reject single-select elements")
    _expect_raises(TypeError, single.clear, "clear() should reject single-select elements")
    _expect_raises(TypeError, lambda: single(["One", "Two"]),
                   "single select should reject a list of conditions")
    assert_true(single("One") is single_owner, "calling SelectElement should select by text")


def test_console_edges():
    class Owner:
        _messenger_running = True

        def __init__(self):
            self.callbacks = []
            self.cdp = []

        def _set_callback(self, event, callback):
            self.callbacks.append((event, callback))

        def _run_cdp(self, method):
            self.cdp.append(method)

    owner = Owner()
    console = Console(owner)
    _expect_raises(RuntimeError, lambda: console.wait(timeout=0), "wait() should require start()")
    console.start()
    console.start()
    assert_equal(owner.cdp[:2], ["Log.enable", "Runtime.enable"], "domains should be enabled only once")
    console._onEntryAdded(entry={"text": "one"})
    generator = console.steps(timeout=None)
    assert_equal(next(generator).text, "one", "steps(None) should yield queued console data")
    generator.close()
    console._onConsoleAPICalled(type="log", args=[{"value": 2}])
    generator = console.steps(timeout=1)
    assert_equal(next(generator).args, [{"value": 2}], "timed steps should yield queued console data")
    generator.close()
    owner._messenger_running = False
    assert_false(console.wait(timeout=0), "wait() should stop when the messenger is disconnected")
    console.stop()
    console.stop()


def test_rect_and_state_edges():
    class DiffOwner:
        _is_diff_domain = True
        rect = SimpleNamespace(viewport_location=(10, 20), screen_location=(100, 200))

        def _run_cdp(self, method, **kwargs):
            return {"model": {
                "border": [1, 2, 11, 2, 11, 12, 1, 12],
                "padding": [2, 3, 10, 3, 10, 11, 2, 11],
            }}

        def _run_js(self, script):
            return 2

        def _run_cdp_loaded(self, method):
            return {"visualViewport": {"pageX": 5, "pageY": 7}}

    element = SimpleNamespace(owner=DiffOwner(), _backend_id=1, _node_id=2, _obj_id="3",
                              _run_js=lambda script: "4 5")
    rect = ElementRect(element)
    assert_equal(rect.screen_location, (102, 204), "diff-domain screen location should use parent screen origin")
    assert_equal(rect.screen_midpoint, (112, 214), "diff-domain screen midpoint should use parent screen origin")
    assert_equal(rect.screen_click_point, (112, 212), "diff-domain click point should use parent screen origin")

    class WindowBrowser:
        def __init__(self, state):
            self.state = state

        def _run_cdp(self, method, **kwargs):
            return {"bounds": {"windowState": self.state, "left": 5, "top": 6, "width": 100, "height": 80}}

    for state, expected_location, expected_size in (
        ("fullscreen", (0, 0), (100, 80)),
        ("maximized", (0, 0), (84, 64)),
    ):
        owner = SimpleNamespace(tab_id="tab", browser=WindowBrowser(state),
                                _run_js=lambda script: "84 64",
                                _run_cdp_loaded=lambda method: {
                                    "contentSize": {"width": 1, "height": 2},
                                    "layoutViewport": {"pageX": 0, "pageY": 0},
                                    "visualViewport": {"clientWidth": 3, "clientHeight": 4, "pageX": 0, "pageY": 0},
                                })
        tab_rect = TabRect(owner)
        assert_equal(tab_rect.window_location, expected_location, f"{state} window location mismatch")
        assert_equal(tab_rect.window_size, expected_size, f"{state} window size mismatch")

    frame_ele_rect = SimpleNamespace(location=(1, 2), viewport_location=(3, 4), screen_location=(5, 6),
                                     size=(7, 8), corners=((1, 1),), viewport_corners=((2, 2),))
    frame = SimpleNamespace(
        frame_ele=SimpleNamespace(rect=frame_ele_rect),
        doc_ele=SimpleNamespace(_run_js=lambda script: {
            "return this.body.scrollWidth": 90,
            "return this.body.scrollHeight": 100,
            'return this.documentElement.scrollLeft.toString() + " " + this.documentElement.scrollTop.toString();': "11 12",
        }[script]),
    )
    frame_rect = FrameRect(frame)
    assert_equal((frame_rect.location, frame_rect.viewport_location, frame_rect.screen_location),
                 ((1, 2), (3, 4), (5, 6)), "FrameRect should delegate frame element coordinates")
    assert_equal((frame_rect.size, frame_rect.viewport_size, frame_rect.corners, frame_rect.viewport_corners,
                  frame_rect.scroll_position),
                 ((90, 100), (7, 8), ((1, 1),), ((2, 2),), (11, 12)),
                 "FrameRect should expose document and viewport geometry")

    class LostOwner:
        def _run_cdp(self, method, **kwargs):
            if method == "DOM.describeNode":
                raise ElementLostError
            if method == "DOM.getNodeForLocation":
                raise CDPError
            return {}

        def _run_js(self, script):
            return True

    class LostRect:
        click_point = (0, 1)
        location = (1, 2)
        size = (3, 4)

        @property
        def corners(self):
            raise NoRectError

    lost_ele = SimpleNamespace(owner=LostOwner(), _backend_id=1, rect=LostRect(),
                               _run_js=lambda script: False,
                               style=lambda name: "visible", property=lambda name: False)
    states = ElementStates(lost_ele)
    assert_false(states.is_alive, "lost element should not be alive")
    assert_false(states.is_in_viewport, "zero-x click point should be outside viewport")
    assert_false(states.is_covered, "CDP hit-test failure should report not covered")
    assert_false(states.has_rect, "NoRectError should report no rectangle")
    shadow = ShadowRootStates(lost_ele)
    assert_true(shadow.is_enabled, "shadow root enabled state should invert disabled JS")
    assert_false(shadow.is_alive, "lost shadow root should not be alive")

    page = SimpleNamespace(_is_loading=False, _ready_state="complete", _has_alert=False,
                           _run_cdp=lambda method: (_ for _ in ()).throw(PageDisconnectedError()))
    page_states = PageStates(page)
    assert_false(page_states.is_alive, "disconnected page should not be alive")

    frame_state_owner = SimpleNamespace(
        _is_loading=True,
        _ready_state="interactive",
        _has_alert=True,
        _frame_ele=SimpleNamespace(_backend_id=9),
        _target_page=SimpleNamespace(_run_cdp=lambda method, **kwargs: {"node": {"frameId": "frame"}}),
        frame_ele=SimpleNamespace(style=lambda name: "visible", _run_js=lambda script: False),
    )
    frame_states = FrameStates(frame_state_owner)
    assert_true(frame_states.is_loading, "FrameStates should expose loading state")
    assert_true(frame_states.is_alive, "frame node with frameId should be alive")
    assert_equal(frame_states.ready_state, "interactive", "FrameStates should expose ready state")
    assert_true(frame_states.is_displayed, "visible frame element should report displayed")
    assert_true(frame_states.has_alert, "FrameStates should expose alert state")
    frame_state_owner._target_page = SimpleNamespace(
        _run_cdp=lambda method, **kwargs: (_ for _ in ()).throw(PageDisconnectedError())
    )
    assert_false(frame_states.is_alive, "disconnected frame should not be alive")


def run(ctx):
    test_permission_methods()
    test_scroller_edges()
    test_selector_edges()
    test_console_edges()
    test_rect_and_state_edges()
