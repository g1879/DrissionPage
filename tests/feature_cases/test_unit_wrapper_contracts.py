"""Feature: deterministic unit-wrapper behavior contracts."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from DrissionPage._units.console import Console, ConsoleData
from DrissionPage._units.cookies_setter import BrowserCookiesSetter, ChromiumTabCookiesSetter, CookiesSetter
from DrissionPage._units.perm_setter import BrowserPermSetter
from DrissionPage._units.rect import ElementRect, TabRect
from DrissionPage._units.scroller import ElementScroller, PageScroller
from DrissionPage._units.selector import SelectElement
from DrissionPage._units.setter import (
    BaseSetter,
    ChromiumBaseSetter,
    ChromiumElementSetter,
    PageScrollSetter,
    SessionPageSetter,
)
from DrissionPage._units.states import BrowserStates, ElementStates, PageStates
from DrissionPage._units.waiter import BaseWaiter, ElementWaiter

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "unit_wrapper_contracts"
REQUIRES_BROWSER = False


def run(ctx):
    _check_state_properties()
    _check_rect_properties()
    _check_scroller_contracts()
    _check_permission_and_cookie_payloads()
    _check_console_contracts()
    _check_select_contracts()
    _check_waiter_contracts()
    _check_setter_contracts()


def _check_state_properties():
    class StateOwner:
        def __init__(self):
            self.calls = []

        def _run_cdp(self, method, **kwargs):
            self.calls.append((method, kwargs))
            if method == "DOM.describeNode":
                return {"node": {"nodeId": 9}}
            if method == "DOM.getNodeForLocation":
                return {"backendNodeId": 41}
            if method == "Page.getLayoutMetrics":
                return {}
            raise AssertionError(f"unexpected CDP call: {method}")

    class StateElement:
        _backend_id = 41

        def __init__(self):
            self.owner = StateOwner()
            self.rect = SimpleNamespace(corners=((1, 2), (3, 2), (3, 4), (1, 4)), click_point=(2, 3))

        def _run_js(self, script):
            return {
                "return this.selected;": True,
                "return this.checked;": False,
                "return this.disabled;": False,
            }[script]

        def style(self, name):
            return {"visibility": "visible", "display": "block", "pointer-events": "auto"}[name]

        def property(self, name):
            assert_equal(name, "hidden", "is_displayed should query the hidden property")
            return False

    ele = StateElement()
    states = ElementStates(ele)
    assert_true(states.is_selected, "is_selected should expose the selected JS property")
    assert_false(states.is_checked, "is_checked should expose the checked JS property")
    assert_true(states.is_displayed, "visible element should report displayed")
    assert_true(states.is_enabled, "non-disabled element should report enabled")
    assert_true(states.is_alive, "described DOM node should report alive")
    assert_false(states.is_covered, "hit-testing the same backend node should report not covered")
    assert_equal(states.has_rect, ele.rect.corners, "has_rect should return the available corner coordinates")
    assert_true(states.is_clickable, "rectangular visible enabled element should report clickable")
    assert_in(("DOM.describeNode", {"backendNodeId": 41}), ele.owner.calls,
              "is_alive should identify the element by backend node id")
    assert_in(("DOM.getNodeForLocation", {"x": 2, "y": 3}), ele.owner.calls,
              "is_covered should hit-test the integer click point")

    driver = SimpleNamespace(is_running=True)
    browser = SimpleNamespace(_driver=driver, _is_headless=True, _is_exists=False, _incognito=True, _guest=False)
    browser_states = BrowserStates(browser)
    assert_true(browser_states.is_alive, "browser state should mirror driver liveness")
    assert_true(browser_states.is_headless, "browser state should mirror headless mode")
    assert_false(browser_states.is_existed, "browser state should mirror existing-process ownership")
    assert_true(browser_states.is_incognito, "browser state should mirror incognito mode")
    assert_false(browser_states.is_guest, "browser state should mirror guest mode")

    page_owner = StateOwner()
    page_owner._is_loading = False
    page_owner._ready_state = "complete"
    page_owner._has_alert = True
    page_owner.browser = SimpleNamespace(states=browser_states)
    page_states = PageStates(page_owner)
    assert_true(page_states.is_alive, "successful layout metrics query should report a live page")
    assert_false(page_states.is_loading, "page state should mirror loading state")
    assert_equal(page_states.ready_state, "complete", "page state should expose readyState")
    assert_true(page_states.has_alert, "page state should expose alert state")
    assert_true(page_states.is_headless, "page state should delegate browser headless state")
    assert_false(page_states.is_existed, "page state should delegate browser existence state")
    assert_true(page_states.is_incognito, "page state should delegate browser context mode")


def _check_rect_properties():
    class ElementOwner:
        def __init__(self):
            self.calls = []
            self.rect = SimpleNamespace(viewport_location=(100, 200))

        def _run_cdp(self, method, **kwargs):
            self.calls.append((method, kwargs))
            assert_equal(method, "DOM.getBoxModel", "element rect should use DOM.getBoxModel")
            return {"model": {
                "border": [10, 20, 110, 20, 110, 70, 10, 70],
                "padding": [12, 22, 108, 22, 108, 68, 12, 68],
            }}

        def _run_cdp_loaded(self, method):
            assert_equal(method, "Page.getLayoutMetrics", "page coordinates should use layout metrics")
            return {"visualViewport": {"pageX": 5, "pageY": 7}}

        def _run_js(self, script):
            assert_equal(script, "return window.devicePixelRatio;", "screen coordinates should query pixel ratio")
            return 2

    owner = ElementOwner()
    element = SimpleNamespace(
        owner=owner,
        _backend_id=71,
        _node_id=72,
        _obj_id="object-73",
        _run_js=lambda script: "4 9",
    )
    rect = ElementRect(element)
    assert_equal(rect.viewport_corners, ((10, 20), (110, 20), (110, 70), (10, 70)),
                 "viewport_corners should preserve the box-model quad")
    assert_equal(rect.corners, [(15, 27), (115, 27), (115, 77), (15, 77)],
                 "corners should include page scroll offsets")
    assert_equal(rect.size, (100, 50), "size should derive width and height from the border quad")
    assert_equal(rect.viewport_location, (10, 20), "viewport_location should expose top-left border coordinates")
    assert_equal(rect.viewport_midpoint, (60, 45), "viewport_midpoint should expose the border center")
    assert_equal(rect.viewport_click_point, (60, 25), "click point should use horizontal center and padding offset")
    assert_equal(rect.location, (15, 27), "location should translate viewport coordinates to page coordinates")
    assert_equal(rect.midpoint, (65, 52), "midpoint should translate viewport coordinates to page coordinates")
    assert_equal(rect.click_point, (65, 32), "click point should translate viewport coordinates to page coordinates")
    assert_equal(rect.screen_location, (220, 440), "screen_location should include browser chrome and pixel ratio")
    assert_equal(rect.scroll_position, (4, 9), "element scroll_position should parse integer JS coordinates")
    assert_in(("DOM.getBoxModel", {"backendNodeId": 71, "nodeId": 72, "objectId": "object-73"}), owner.calls,
              "size should pass every available node identity to DOM.getBoxModel")

    class Browser:
        def __init__(self):
            self.calls = []

        def _run_cdp(self, method, **kwargs):
            self.calls.append((method, kwargs))
            return {"bounds": {"windowState": "normal", "left": 10, "top": 20, "width": 816, "height": 607}}

    browser = Browser()
    tab_owner = SimpleNamespace(tab_id="tab-9", browser=browser)
    tab_owner._run_js = lambda script: "800 600"
    tab_owner._run_cdp_loaded = lambda method: {
        "contentSize": {"width": 1200, "height": 900},
        "layoutViewport": {"pageX": 3, "pageY": 4},
        "visualViewport": {"clientWidth": 780, "clientHeight": 580, "pageX": 30, "pageY": 40},
    }
    tab_rect = TabRect(tab_owner)
    assert_equal(tab_rect.window_state, "normal", "window_state should expose CDP window state")
    assert_equal(tab_rect.window_location, (17, 20), "window_location should account for normal window border")
    assert_equal(tab_rect.window_size, (800, 600), "window_size should remove normal browser chrome")
    assert_equal(tab_rect.viewport_location, (17, 20), "viewport_location should combine window and viewport sizes")
    assert_equal(tab_rect.page_location, (14, 16), "page_location should subtract layout scroll offsets")
    assert_equal(tab_rect.size, (1200, 900), "tab size should expose content dimensions")
    assert_equal(tab_rect.viewport_size, (780, 580), "viewport_size should expose visual viewport dimensions")
    assert_equal(tab_rect.viewport_size_with_scrollbar, (800, 600),
                 "viewport_size_with_scrollbar should parse window inner dimensions")
    assert_equal(tab_rect.scroll_position, (30, 40), "tab scroll_position should expose visual viewport offsets")
    assert_in(("Browser.getWindowForTarget", {"targetId": "tab-9"}), browser.calls,
              "tab rect should request the window for its exact target id")


def _check_scroller_contracts():
    class PageOwner:
        _type = "ChromiumTab"

        def __init__(self):
            self.js_calls = []
            self.target = None

        def _run_js(self, script):
            self.js_calls.append(script)

        def _ele(self, locator):
            self.target = ScrollElement()
            self.target.locator = locator
            return self.target

    class ScrollElement:
        def __init__(self):
            self.js_calls = []
            self.states = SimpleNamespace(is_covered=False)

        def _run_js(self, script):
            self.js_calls.append(script)

    owner = PageOwner()
    scroll = PageScroller(owner)
    assert_true(scroll.to_top() is owner, "page scroll operations should return the owner")
    assert_true(scroll.to_location(11, 22) is owner, "to_location should be chainable through the owner")
    assert_true(scroll.left(5) is owner, "directional scroll should return the owner")
    assert_true(scroll(7) is owner, "calling a scroller should delegate to down()")
    assert_equal(owner.js_calls, [
        "window.scrollTo(document.documentElement.scrollLeft, 0);",
        "window.scrollTo(11, 22);",
        "window.scrollBy(-5, 0);",
        "window.scrollBy(0, 7);",
    ], "page scroller should emit exact window/documentElement JS payloads")
    assert_true(scroll.to_see("#target", center=False) is owner, "to_see should return the page owner")
    assert_equal(owner.target.locator, "#target", "to_see should resolve the requested locator")
    assert_equal(owner.target.js_calls, ["this.scrollIntoViewIfNeeded(false);"],
                 "center=False should only request the native visibility scroll")

    class ParentScroll:
        def __init__(self):
            self.calls = []

        def to_see(self, element, center=None):
            self.calls.append((element, center))

    parent_scroll = ParentScroll()
    parent = SimpleNamespace(scroll=parent_scroll)
    element = SimpleNamespace(owner=parent)
    element_scroll = ElementScroller(element)
    assert_true(element_scroll.to_see(center=False) is element, "element to_see should return the element")
    assert_true(element_scroll.to_center() is element, "element to_center should return the element")
    assert_equal(parent_scroll.calls, [(element, False), (element, True)],
                 "element scroller should delegate visibility scrolling to its owning page")

    scroll_setter = PageScrollSetter(scroll)
    scroll_setter.wait_complete(True)
    assert_true(scroll._wait_complete, "wait_complete(True) should enable scroll completion waits")
    scroll_setter.smooth(False)
    assert_false(scroll._wait_complete, "smooth(False) should disable completion waits")
    assert_equal(owner.js_calls[-1], 'document.documentElement.style.setProperty("scroll-behavior","auto");',
                 "smooth(False) should emit the exact auto-scroll CSS payload")


def _check_permission_and_cookie_payloads():
    class CdpOwner:
        def __init__(self, **attrs):
            self.calls = []
            for name, value in attrs.items():
                setattr(self, name, value)

        def _run_cdp(self, method, **kwargs):
            self.calls.append((method, kwargs))

    default_owner = CdpOwner()
    default_perm = BrowserPermSetter(default_owner, None)
    default_perm.geolocation(False)
    default_perm.push()
    assert_equal(default_owner.calls, [
        ("Browser.setPermission", {"permission": {"name": "geolocation"}, "setting": "denied"}),
        ("Browser.setPermission", {"permission": {"name": "push", "userVisibleOnly": True}, "setting": "granted"}),
    ], "default-context permissions should omit browserContextId and map booleans to CDP settings")

    context_owner = CdpOwner()
    context_perm = BrowserPermSetter(context_owner, "context-3")
    context_perm.camera(panTiltZoom=True)
    context_perm.clipboard_read(False, allowWithoutSanitization=False)
    context_perm.fullscreen()
    assert_equal(context_owner.calls, [
        ("Browser.setPermission", {
            "permission": {"name": "camera", "panTiltZoom": True},
            "setting": "granted",
            "browserContextId": "context-3",
        }),
        ("Browser.setPermission", {
            "permission": {"name": "clipboard-read", "allowWithoutSanitization": False},
            "setting": "denied",
            "browserContextId": "context-3",
        }),
        ("Browser.setPermission", {
            "permission": {"name": "fullscreen", "allowWithoutGesture": True},
            "setting": "granted",
            "browserContextId": "context-3",
        }),
    ], "context permissions should preserve optional flags and context isolation")

    default_cookies = CdpOwner(_default_context=True, _context_id="ignored")
    BrowserCookiesSetter(default_cookies).clear()
    assert_equal(default_cookies.calls, [("Storage.clearCookies", {})],
                 "default-context cookie clearing should omit browserContextId")
    context_cookies = CdpOwner(_default_context=False, _context_id="context-4")
    BrowserCookiesSetter(context_cookies).clear()
    assert_equal(context_cookies.calls, [("Storage.clearCookies", {"browserContextId": "context-4"})],
                 "non-default cookie clearing should target the exact browser context")

    tab_owner = CdpOwner(url="https://example.test/path")
    cookie_setter = CookiesSetter(tab_owner)
    cookie_setter.remove("sid")
    cookie_setter.remove("scoped", domain=".example.test", path="/account")
    cookie_setter.clear()
    assert_equal(tab_owner.calls, [
        ("Network.deleteCookies", {"name": "sid", "url": "https://example.test/path"}),
        ("Network.deleteCookies", {"name": "scoped", "domain": ".example.test", "path": "/account"}),
        ("Network.clearBrowserCookies", {}),
    ], "tab cookie removal should preserve URL/domain/path payload boundaries")

    class SessionCookies:
        def __init__(self):
            self.calls = []

        def set(self, name, value):
            self.calls.append(("set", name, value))

        def clear(self):
            self.calls.append(("clear",))

    session_cookies = SessionCookies()
    session_tab = CdpOwner(_d_mode=False, _messenger_running=False,
                           _session=True, session=SimpleNamespace(cookies=session_cookies))
    mixed_setter = ChromiumTabCookiesSetter(session_tab)
    mixed_setter.remove("session-id")
    mixed_setter.clear()
    assert_equal(session_cookies.calls, [("set", "session-id", None), ("clear",)],
                 "session-mode tab cookie operations should use the requests cookie jar")


def _check_console_contracts():
    class ConsoleOwner:
        def __init__(self):
            self.callbacks = {}
            self.cdp_calls = []
            self._messenger_running = True

        def _set_callback(self, event, callback):
            self.callbacks[event] = callback

        def _run_cdp(self, method):
            self.cdp_calls.append(method)

    owner = ConsoleOwner()
    console = Console(owner)
    assert_equal(console.messages, [], "messages should be empty before console listening starts")
    console.start()
    assert_true(console.listening, "start should mark console listening active")
    assert_equal(owner.cdp_calls, ["Log.enable", "Runtime.enable"],
                 "start should enable both CDP console domains")
    owner.callbacks["Log.entryAdded"](entry={"text": "log-entry", "level": "info"})
    first = console.wait(timeout=0.01)
    assert_true(isinstance(first, ConsoleData), "wait should return ConsoleData for queued events")
    assert_equal(first.text, "log-entry", "ConsoleData attributes should delegate to raw event fields")
    assert_equal(first.data, {"text": "log-entry", "level": "info"},
                 "ConsoleData.data should preserve the raw event payload")
    owner.callbacks["Runtime.consoleAPICalled"](type="log", args=[{"value": 42}])
    drained = console.messages
    assert_equal(len(drained), 1, "messages should drain all currently queued console events")
    assert_equal(drained[0].args, [{"value": 42}], "runtime console arguments should remain available")
    assert_equal(console.messages, [], "messages should be destructive after draining")
    console.clear()
    assert_equal(console.messages, [], "clear should replace the pending event queue")
    console.stop()
    assert_false(console.listening, "stop should mark console listening inactive")
    assert_equal(owner.callbacks["Log.entryAdded"], None, "stop should unregister Log.entryAdded callback")
    assert_equal(owner.callbacks["Runtime.consoleAPICalled"], None,
                 "stop should unregister Runtime.consoleAPICalled callback")
    assert_equal(owner.cdp_calls[-2:], ["Log.disable", "Runtime.disable"],
                 "stop should disable both CDP console domains")


def _check_select_contracts():
    class Option:
        def __init__(self, text, value, selected=False):
            self.text = text
            self.value = value
            self.states = SimpleNamespace(is_selected=selected)
            self.js_calls = []

        def attr(self, name):
            assert_equal(name, "value", "value selection should query the option value attribute")
            return self.value

        def _run_js(self, script):
            self.js_calls.append(script)
            if script == "this.selected=true;":
                self.states.is_selected = True
            elif script == "this.selected=false;":
                self.states.is_selected = False

    class Select:
        tag = "select"
        timeout = 0.01

        def __init__(self):
            self.items = [Option("One", "1"), Option("Two", "2", selected=True)]
            self.js_calls = []

        def attr(self, name):
            assert_equal(name, "multiple", "is_multi should query the multiple attribute")
            return ""

        def eles(self, locator, timeout=None):
            assert_in(locator, ("xpath://option", "tag:option"), "select should only enumerate option elements")
            return [self.items[0], 0, self.items[1]] if locator == "xpath://option" else list(self.items)

        def _run_js(self, script):
            self.js_calls.append(script)
            if script == "return this.options[this.selectedIndex];":
                return self.items[1]

    element = Select()
    selector = SelectElement(element)
    assert_true(selector.is_multi, "multiple attribute should expose multi-select semantics")
    assert_equal(selector.options, element.items, "options should filter non-element sentinels")
    assert_equal(selector.selected_option, element.items[1], "selected_option should return the JS selectedIndex option")
    assert_equal(selector.selected_options, [element.items[1]], "selected_options should filter by option state")
    assert_true(selector.by_text(["One", "Two"], timeout=0.01) is element,
                "by_text should return the select element for chaining")
    assert_true(all(item.states.is_selected for item in element.items),
                "by_text should select every matching option in a multi-select")
    assert_equal(element.js_calls.count('this.dispatchEvent(new CustomEvent("change", {bubbles: true}));'), 2,
                 "each selected option should dispatch a bubbling change event")
    assert_true(selector.cancel_by_index(-1, timeout=0.01) is element,
                "negative index cancellation should return the select element")
    assert_false(element.items[1].states.is_selected, "index -1 should address the last option")
    assert_true(selector.invert() is element, "invert should return the select element")
    assert_false(element.items[0].states.is_selected, "invert should clear selected options")
    assert_true(element.items[1].states.is_selected, "invert should select unselected options")
    assert_true(selector.clear() is element, "clear should return the select element")
    assert_false(any(item.states.is_selected for item in element.items), "clear should deselect all options")


def _check_waiter_contracts():
    class LocatedElement:
        def __init__(self):
            self.wait = SimpleNamespace(
                deleted=lambda timeout, raise_err=None: "deleted-result",
                displayed=lambda timeout, raise_err=None: self,
                hidden=lambda timeout, raise_err=None: self,
            )

    class WaitOwner:
        timeout = 0.01
        _messenger_running = True
        _upload_list = []
        _target_id = "target-8"

        def __init__(self):
            self._is_loading = False
            self.cdp_calls = []
            self.element = LocatedElement()

        def _ele(self, locator, **kwargs):
            return None if locator == "#missing" else self.element

        def _run_cdp(self, method, **kwargs):
            self.cdp_calls.append((method, kwargs))
            return {"targetInfo": {"url": "https://example.test/changed", "title": "Ready title"}}

    owner = WaitOwner()
    waiter = BaseWaiter(owner)
    assert_true(waiter.eles_loaded(["#one", "#two"], timeout=0.01),
                "eles_loaded should succeed when every locator resolves")
    assert_true(waiter.eles_loaded(["#missing", "#two"], timeout=0.01, any_one=True),
                "eles_loaded(any_one=True) should succeed when one locator resolves")
    assert_true(waiter.url_change("changed", timeout=0.01) is owner,
                "url_change should return the owner when target URL contains the text")
    assert_true(waiter.title_change("not present", exclude=True, timeout=0.01) is owner,
                "title_change(exclude=True) should return the owner when text is absent")
    assert_in(("Target.getTargetInfo", {"targetId": "target-8"}), owner.cdp_calls,
              "URL/title waits should query the exact target id")
    assert_true(waiter.doc_loaded(timeout=0.01), "doc_loaded should succeed when loading is false")
    owner._is_loading = True
    assert_true(waiter.load_start(timeout=0.01), "load_start should succeed when loading is true")
    assert_true(waiter.upload_paths_inputted(timeout=0.01),
                "upload_paths_inputted should succeed when the pending path list is empty")
    assert_true(waiter.ele_deleted("#missing", timeout=0.01),
                "ele_deleted should immediately succeed for an absent element")
    assert_true(waiter.ele_displayed("#one", timeout=0.01) is owner.element,
                "ele_displayed should return the located element")

    element = SimpleNamespace(
        timeout=0.01,
        states=SimpleNamespace(
            is_alive=False,
            is_displayed=True,
            is_covered=False,
            is_enabled=False,
            is_clickable=True,
            has_rect=((1, 1), (2, 1), (2, 2), (1, 2)),
        ),
    )
    element_waiter = ElementWaiter(element)
    assert_true(element_waiter.deleted(timeout=0.01), "deleted should return a boolean success result")
    assert_true(element_waiter.displayed(timeout=0.01) is element,
                "displayed should return the element when its state already matches")
    assert_true(element_waiter.not_covered(timeout=0.01) is element,
                "not_covered should return the element when hit testing is clear")
    assert_true(element_waiter.disabled(timeout=0.01) is element,
                "disabled should return the element when enabled state is false")
    assert_true(element_waiter.clickable(wait_stop=False, timeout=0.01) is element,
                "clickable(wait_stop=False) should return without movement polling")
    assert_equal(element_waiter.has_rect(timeout=0.01), element.states.has_rect,
                 "has_rect should preserve non-boolean rectangle data")


def _check_setter_contracts():
    base_owner = SimpleNamespace(
        _none_ele_return_value=False,
        _none_ele_value=None,
        retry_times=0,
        retry_interval=0,
        _download_path=None,
    )
    base = BaseSetter(base_owner)
    base.NoneElement_value("missing", on_off=True)
    base.retry_times(4)
    base.retry_interval(0.25)
    base.download_path(None)
    assert_equal((base_owner._none_ele_return_value, base_owner._none_ele_value), (True, "missing"),
                 "NoneElement_value should update both enable flag and fallback value")
    assert_equal((base_owner.retry_times, base_owner.retry_interval), (4, 0.25),
                 "retry setters should update the owner's retry policy")
    assert_equal(base_owner._download_path, str(Path(".").resolve()),
                 "download_path(None) should resolve to the current directory")

    class Session:
        def __init__(self):
            self.proxies = None
            self.auth = None
            self.hooks = None
            self.params = None
            self.verify = None
            self.cert = None
            self.stream = None
            self.trust_env = None
            self.max_redirects = None
            self.mount_calls = []

        def mount(self, url, adapter):
            self.mount_calls.append((url, adapter))

    session_owner = SimpleNamespace(
        _cookies_setter=None,
        _downloader=None,
        _timeout=0,
        _encoding=None,
        response=SimpleNamespace(encoding=None),
        _headers={},
        session=Session(),
    )
    session_setter = SessionPageSetter(session_owner)
    session_setter.timeout(3)
    session_setter.encoding("utf-8")
    session_setter.headers({"X-Test": "one"})
    session_setter.header("x-extra", "two")
    session_setter.user_agent("Unit-UA")
    session_setter.proxies("http://proxy", "https://proxy")
    session_setter.auth(("user", "pass"))
    session_setter.verify(False)
    session_setter.add_adapter("mock://", "adapter")
    assert_equal(session_owner._timeout, 3, "session timeout setter should update the owner timeout")
    assert_equal((session_owner._encoding, session_owner.response.encoding), ("utf-8", "utf-8"),
                 "encoding should update both owner default and current response")
    assert_equal(session_owner._headers["x-test"], "one", "headers should be case-insensitive and formatted")
    assert_equal(session_owner._headers["X-Extra"], "two", "header should update one case-insensitive entry")
    assert_equal(session_owner._headers["user-agent"], "Unit-UA", "user_agent should update the request header")
    assert_equal(session_owner.session.proxies, {"http": "http://proxy", "https": "https://proxy"},
                 "proxies should preserve separate HTTP and HTTPS values")
    assert_equal(session_owner.session.auth, ("user", "pass"), "auth should pass through to the requests session")
    assert_false(session_owner.session.verify, "verify(False) should update the requests session")
    assert_equal(session_owner.session.mount_calls, [("mock://", "adapter")],
                 "add_adapter should mount the exact prefix and adapter")

    class WaitProbe:
        def __init__(self):
            self.calls = 0

        def doc_loaded(self):
            self.calls += 1

    class ChromiumOwner:
        def __init__(self):
            self.calls = []
            self.enabled = []
            self.disabled = []
            self.callbacks = []
            self.timeouts = SimpleNamespace(base=1, page_load=2, script=3)
            self.wait = WaitProbe()
            self._frame_id = "frame-5"
            self._upload_list = []
            self._onFileChooserOpened = object()
            self._alert = SimpleNamespace(auto=False)
            self.scroll = SimpleNamespace(_wait_complete=False)

        def _enable_domain(self, domain):
            self.enabled.append(domain)

        def _disable_domain(self, domain):
            self.disabled.append(domain)

        def _set_callback(self, event, callback):
            self.callbacks.append((event, callback))

        def _run_cdp(self, method, **kwargs):
            self.calls.append((method, kwargs))
            if method == "Storage.getStorageKeyForFrame":
                return {"storageKey": "storage-key-5"}
            return {}

    chromium_owner = ChromiumOwner()
    chromium_setter = ChromiumBaseSetter(chromium_owner)
    chromium_setter.timeouts(base=4, page_load=5, script=6)
    assert_equal((chromium_owner.timeouts.base, chromium_owner.timeouts.page_load, chromium_owner.timeouts.script),
                 (4, 5, 6), "timeouts should update only the requested timeout fields")
    chromium_setter.headers({"X-One": "1"})
    chromium_setter.user_agent("Agent-UA", platform="UnitOS")
    chromium_setter.blocked_urls("https://blocked.test/*")
    assert_in(("Network.setExtraHTTPHeaders", {"headers": {"X-One": "1"}}), chromium_owner.calls,
              "headers should preserve the exact Network.setExtraHTTPHeaders payload")
    assert_in(("Emulation.setUserAgentOverride", {"userAgent": "Agent-UA", "platform": "UnitOS"}),
              chromium_owner.calls, "user_agent should preserve optional platform payload")
    assert_in(("Network.setBlockedURLs", {"urls": ("https://blocked.test/*",)}), chromium_owner.calls,
              "a single blocked URL should be normalized to a tuple payload")

    chromium_owner.calls.clear()
    chromium_setter.local_storage("theme", "dark")
    assert_equal(chromium_owner.calls, [
        ("Storage.getStorageKeyForFrame", {"frameId": "frame-5"}),
        ("DOMStorage.setDOMStorageItem", {
            "storageId": {"storageKey": "storage-key-5", "isLocalStorage": True},
            "key": "theme",
            "value": "dark",
        }),
    ], "local_storage should address the frame storage key and local-storage namespace")
    assert_equal((chromium_owner.enabled[-1], chromium_owner.disabled[-1]), ("DOMStorage", "DOMStorage"),
                 "storage updates should enable and then disable the DOMStorage domain")

    chromium_owner.calls.clear()
    chromium_setter.session_storage("token", False)
    assert_equal(chromium_owner.calls, [
        ("Storage.getStorageKeyForFrame", {"frameId": "frame-5"}),
        ("DOMStorage.removeDOMStorageItem", {
            "storageId": {"storageKey": "storage-key-5", "isLocalStorage": False},
            "key": "token",
        }),
    ], "session_storage(False) should remove from the session-storage namespace")
    assert_equal(chromium_owner.wait.calls, 4, "each storage update should wait before and after the CDP mutation")

    chromium_setter.upload_files("first.txt\nsecond.txt")
    expected_paths = [str(Path("first.txt").resolve()), str(Path("second.txt").resolve())]
    assert_equal(chromium_owner._upload_list, expected_paths,
                 "upload_files should normalize newline-separated paths to absolute strings")
    assert_equal(chromium_owner.callbacks[0][0], "Page.fileChooserOpened",
                 "the first upload should install the file chooser callback")
    assert_in(("Page.setInterceptFileChooserDialog", {"enabled": True}), chromium_owner.calls,
              "the first upload should enable file chooser interception")
    chromium_setter.auto_handle_alert(False)
    assert_equal(chromium_owner._alert.auto, "close", "auto_handle_alert(False) should configure automatic close")

    class ElementOwner:
        def __init__(self):
            self.calls = []

        def _run_cdp(self, method, **kwargs):
            self.calls.append((method, kwargs))

    element_owner = ElementOwner()
    js_calls = []
    element = SimpleNamespace(owner=element_owner, _node_id=19, _run_js=js_calls.append)
    element_setter = ChromiumElementSetter(element)
    element_setter.attr("data-count", 7)
    element_setter.property("title", 'a"b')
    element_setter.style("backgroundColor", "red")
    assert_equal(element_owner.calls, [
        ("DOM.setAttributeValue", {"nodeId": 19, "name": "data-count", "value": "7"}),
    ], "element attr should send a string value and exact node id")
    assert_equal(js_calls, ['this.title="a\\"b";', 'this.style.backgroundColor="red";'],
                 "element property/style setters should emit exact escaped JS assignments")
