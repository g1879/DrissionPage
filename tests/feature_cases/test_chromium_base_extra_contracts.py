"""Feature: deterministic Chromium base, tab, and frame edge contracts."""
from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace

import DrissionPage._pages.chromium_base as chromium_base_module
import DrissionPage._pages.chromium_frame as chromium_frame_module
import DrissionPage._pages.chromium_tab as chromium_tab_module
from DrissionPage._pages.chromium_base import Alert, ChromiumBase, Timeout
from DrissionPage._pages.chromium_frame import ChromiumFrame
from DrissionPage._pages.chromium_tab import ChromiumTab
from DrissionPage._pages.session_page import SessionPage
from DrissionPage.errors import ContextLostError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "chromium_base_extra_contracts"
REQUIRES_BROWSER = False


def run(ctx):
    test_base_protocol_and_lazy_accessors()
    test_base_storage_cache_alert_and_download_contracts()
    test_base_lookup_and_element_helpers()
    test_tab_cookie_conversion_mode_and_cleanup()
    test_frame_accessors_and_detach_bookkeeping()


@contextmanager
def _patched(target, **replacements):
    originals = {name: getattr(target, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(target, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(target, name, value)


@contextmanager
def _preserved_dict(mapping):
    original = dict(mapping)
    try:
        yield
    finally:
        mapping.clear()
        mapping.update(original)


class _WaitProbe:
    def __init__(self, owner=None, loaded=True):
        self.owner = owner
        self.loaded = loaded
        self.calls = []

    def doc_loaded(self):
        self.calls.append(("doc_loaded",))

    def load_start(self):
        self.calls.append(("load_start",))

    def eles_loaded(self, locator, timeout=None):
        self.calls.append(("eles_loaded", locator, timeout))
        return self.loaded


class _Widget:
    def __init__(self, owner):
        self.owner = owner
        self.loaded_calls = 0

    def doc_loaded(self):
        self.loaded_calls += 1


def _base_page():
    page = object.__new__(ChromiumBase)
    page._browser = SimpleNamespace()
    page._driver = object()
    page._target_id = "target-extra"
    page._frame_id = "frame-extra"
    page._context_id = "context-extra"
    page._default_context = True
    page._timeouts = Timeout(base=4, page_load=8, script=12)
    page._load_mode = "normal"
    page._root_oid = "root-object"
    page._wait = _WaitProbe(page)
    page._init_jss = []
    page._session = None
    page._upload_list = ["pending.txt"]
    page._messenger_running = True
    page._ready_state = "complete"
    page._is_loading = False
    page._none_ele_value = None
    page._none_ele_return_value = False
    page._nav_result = SimpleNamespace()
    return page


def test_base_protocol_and_lazy_accessors():
    page = _base_page()
    cdp_calls = []

    def run_cdp(command, **kwargs):
        cdp_calls.append((command, kwargs))
        if command == "Target.getTargetInfo":
            return {"targetInfo": {"title": "Extra title", "url": "https://extra.test/"}}
        if command == "DOM.getOuterHTML":
            return {"outerHTML": "<html>extra</html>"}
        if command == "Runtime.evaluate" and kwargs.get("expression") == "navigator.userAgent;":
            return {"result": {"value": "extra-agent"}}
        if command == "Runtime.evaluate" and kwargs.get("expression") == "document.readyState;":
            return {"result": {"value": "complete"}}
        return {"ok": command}

    page._run_func = run_cdp
    assert_equal(page.run_cdp("Runtime.evaluate", expression="1"), {"ok": "Runtime.evaluate"},
                 "run_cdp should return the raw command payload")
    assert_equal(cdp_calls[-1], ("Runtime.evaluate", {"expression": "1", "_user": True}),
                 "run_cdp should mark user commands while preserving command arguments")
    assert_equal(page.run_cdp_loaded("Page.enable"), {"ok": "Page.enable"},
                 "run_cdp_loaded should return the loaded command payload")
    assert_equal(cdp_calls[-1], ("Page.enable", {"_ignore": None, "_user": True, "_timeout": None}),
                 "run_cdp_loaded should route ignore, user, and timeout flags")

    js_calls = []

    def fake_run_js(owner, script, as_expr, timeout, args):
        js_calls.append((owner, script, as_expr, timeout, args))
        return f"js:{script}"

    with _patched(chromium_base_module, run_js=fake_run_js):
        assert_equal(page.run_js("return 1;", "arg", as_expr=True, timeout=2), "js:return 1;",
                     "run_js should return the helper result")
        assert_equal(page.run_js_loaded("return 2;", 3), "js:return 2;",
                     "run_js_loaded should return the helper result")
        assert_equal(page._run_js_loaded("return 3;", as_expr=True), "js:return 3;",
                     "_run_js_loaded should use the configured script timeout")
        assert_equal(page.run_async_js("return 4;", "async"), None,
                     "run_async_js should preserve its fire-and-forget return contract")
    assert_equal(
        [(script, as_expr, timeout, args) for _, script, as_expr, timeout, args in js_calls],
        [("return 1;", True, 2, ("arg",)),
         ("return 2;", False, 12, (3,)),
         ("return 3;", True, 12, ()),
         ("return 4;", False, 0, ("async",))],
        "JavaScript wrappers should route expression mode, timeout, and positional arguments",
    )

    assert_equal((page.title, page.url, page._browser_url, page.html, page.user_agent),
                 ("Extra title", "https://extra.test/", "https://extra.test/", "<html>extra</html>",
                  "extra-agent"),
                 "base properties should route through the target and runtime CDP methods")
    page._run_js_loaded = lambda script, **kwargs: "active-element"
    assert_equal(page.active_ele, "active-element", "active_ele should use loaded JavaScript")
    page._ele = lambda locator, **kwargs: SimpleNamespace(text='{"extra": true}')
    assert_equal(page.json, {"extra": True}, "json should decode valid preformatted JSON")
    page._ele = lambda locator, **kwargs: SimpleNamespace(text="not-json")
    assert_equal(page.json, None, "json should return None for malformed preformatted content")

    page._session = None
    page._create_session = lambda: setattr(page, "_session", "created-session")
    assert_equal(page.session, "created-session", "session should lazily create a missing request session")

    page._run_func = lambda *args, **kwargs: (_ for _ in ()).throw(ContextLostError("context"))
    assert_equal(page._js_ready_state, None, "context loss should produce an absent ready state")
    page._run_func = lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError())
    assert_equal(page._js_ready_state, "timeout", "ready-state timeout should use its public sentinel")

    page._wait = None
    page._set = None
    page._screencast = None
    page._actions = None
    page._listener = None
    page._states = None
    page._scroll = None
    page._rect = None
    page._console = None
    with _patched(
        chromium_base_module,
        BaseWaiter=_Widget,
        ChromiumBaseSetter=_Widget,
        Screencast=_Widget,
        Actions=_Widget,
        Listener=_Widget,
        PageStates=_Widget,
        PageScroller=_Widget,
        TabRect=_Widget,
        Console=_Widget,
    ):
        wait = page.wait
        assert_true(page.wait is wait, "wait should cache a single base waiter")
        assert_true(page.set is page._set, "set should cache its owner-bound setter")
        assert_true(page.screencast is page._screencast, "screencast should cache its owner-bound wrapper")
        actions = page.actions
        scroll = page.scroll
        assert_true(actions is page._actions and scroll is page._scroll,
                    "actions and scroll should cache their owner-bound wrappers")
        assert_true(page.listen is page._listener, "listen should cache its owner-bound listener")
        assert_true(page.states is page._states, "states should cache its owner-bound state wrapper")
        assert_true(page.rect is page._rect, "rect should cache its owner-bound rectangle wrapper")
        assert_true(page.console is page._console, "console should cache its owner-bound console wrapper")
        assert_equal(wait.loaded_calls, 2, "actions and scroll should wait for document readiness")


def test_base_storage_cache_alert_and_download_contracts():
    page = _base_page()
    page._run_js_loaded = lambda script, **kwargs: (script, kwargs)
    assert_equal(page.session_storage(), ("sessionStorage", {"as_expr": True}),
                 "session_storage without an item should evaluate the storage object")
    assert_equal(page.local_storage("theme"), ('localStorage.getItem("theme")', {"as_expr": True}),
                 "local_storage should generate an item lookup expression")

    cdp_calls = []
    loaded_calls = []
    domain_calls = []
    page._run_func = lambda command, **kwargs: cdp_calls.append((command, kwargs)) or (
        {"storageKey": "storage-extra"} if command == "Storage.getStorageKeyForFrame" else {}
    )
    page._run_cdp_loaded = lambda command, **kwargs: loaded_calls.append((command, kwargs)) or {}
    page._enable_domain = lambda domain: domain_calls.append(("enable", domain))
    page._disable_domain = lambda domain: domain_calls.append(("disable", domain))
    page.clear_cache()
    assert_equal(loaded_calls[0], ("Storage.clearDataForOrigin", {"origin": "*", "storageTypes": "all"}),
                 "clear_cache should clear all origin data when every category is selected")
    assert_in(("DOMStorage.clear", {"storageId": {"storageKey": "storage-extra", "isLocalStorage": False}}),
              cdp_calls, "clear_cache should clear session storage for the active frame")
    assert_in(("DOMStorage.clear", {"storageId": {"storageKey": "storage-extra", "isLocalStorage": True}}),
              cdp_calls, "clear_cache should clear local storage for the active frame")
    assert_in(("Network.clearBrowserCache", {}), loaded_calls,
              "clear_cache should clear browser cache after storage cleanup")
    assert_in(("Network.clearBrowserCookies", {}), loaded_calls,
              "clear_cache should clear browser cookies after storage cleanup")
    assert_equal(domain_calls, [("enable", "DOMStorage"), ("disable", "DOMStorage")],
                 "storage cleanup should bracket DOMStorage with enable and disable calls")

    cdp_calls.clear()
    loaded_calls.clear()
    domain_calls.clear()
    page.clear_cache(session_storage=False, local_storage=False, cache=False, cookies=True)
    assert_equal(loaded_calls, [("Network.clearBrowserCookies", {})],
                 "partial cache cleanup should only invoke selected CDP categories")
    assert_equal(domain_calls, [], "partial cache cleanup should not enable DOMStorage when storage is disabled")

    page._init_jss = ["one", "two"]
    page.remove_init_js()
    assert_equal(page._init_jss, [], "remove_init_js without an id should clear every local script id")
    assert_equal(
        cdp_calls[-2:],
        [("Page.removeScriptToEvaluateOnNewDocument", {"identifier": "one"}),
         ("Page.removeScriptToEvaluateOnNewDocument", {"identifier": "two"})],
        "remove_init_js should remove every selected protocol script",
    )

    page._alert = Alert()
    page._has_alert = False
    page._run_func = lambda command, **kwargs: cdp_calls.append((command, kwargs))
    page._alert.activated = True
    page._alert.text = "Prompt?"
    page._alert.type = "prompt"
    assert_equal(page._handle_alert(True, send="yes", timeout=0), "Prompt?",
                 "active prompt handling should return the prompt text")
    assert_in(("Page.handleJavaScriptDialog", {"accept": True, "_timeout": 0, "promptText": "yes"}), cdp_calls,
              "prompt handling should route accept, prompt text, and non-waiting timeout")
    assert_equal(page._handle_alert("inspect", timeout=0), "Prompt?",
                 "non-boolean alert handling should return text without accepting")
    assert_equal(page._handle_alert(next_one=True), None, "next_one alert setup should be non-blocking")
    assert_equal((page._alert.handle_next, page._alert.next_text), (True, None),
                 "next_one should store the next alert policy")
    page._alert.auto = "close"
    page._on_alert_open(message="Closed", type="alert", defaultPrompt=None)
    assert_equal((page._alert.text, page._alert.type, page._has_alert), ("Closed", "alert", True),
                 "alert-open events should update alert metadata and active state")
    page._on_alert_close(result=True, userInput="")
    assert_equal((page._alert.response_accept, page._alert.response_text, page._has_alert), (True, "", False),
                 "alert-close events should preserve response metadata and clear active state")

    download_calls = []

    class DownloadElement:
        _obj_id = "download-object"

        class Click:
            def to_download(self, **kwargs):
                download_calls.append(kwargs)
                return "mission"

        click = Click()

    page.new_ele = lambda info: download_calls.append(("new_ele", info)) or DownloadElement()
    result = page._download_by_browser(
        "https://extra.test/report", save_path="/tmp/downloads", rename="report", suffix=".pdf",
        timeout=2, file_exists="overwrite",
    )
    assert_equal(result, "mission", "browser download helper should return the click download mission")
    assert_equal(download_calls[0], ("new_ele", ("a", {
        "href": "https://extra.test/report", "target": "_blank", "download": "report.pdf",
    })), "browser download helper should create a temporary link with a normalized filename")
    assert_equal(download_calls[1], {
        "save_path": "/tmp/downloads", "rename": "report", "suffix": ".pdf", "timeout": 2,
        "by_js": True, "new_tab": True, "file_exists": "overwrite",
    }, "browser download helper should route mission options exactly")
    assert_equal(cdp_calls[-1], ("Runtime.callFunctionOn", {
        "functionDeclaration": "function(){arguments[0].remove();}",
        "arguments": [{"objectId": "download-object"}], "userGesture": True,
        "_timeout": 0, "_ignore": True,
    }), "browser download helper should remove the temporary link after clicking")


def test_base_lookup_and_element_helpers():
    page = _base_page()
    lookup_calls = []
    page._ele = lambda locator, **kwargs: lookup_calls.append((locator, kwargs)) or f"ele:{locator}"
    assert_equal(page("#item", index=2, timeout=1), "ele:#item", "base calls should use ele() lookup")
    assert_equal(page.ele("#item", index=3, timeout=2), "ele:#item", "ele should retain index and timeout")
    assert_equal(page.eles(".item", timeout=4), "ele:.item", "eles should request an index-less lookup")
    assert_equal(lookup_calls[-1], (".item", {"timeout": 4, "index": None}),
                 "eles should pass an explicit None index to the lookup")

    page._wait = _WaitProbe(page, loaded=False)
    missing = page.s_ele("#missing", index=2, timeout=3)
    assert_equal(missing.args, {"locator": "#missing", "index": 2, "timeout": 3},
                 "missing session-element lookups should preserve locator metadata")
    assert_equal(type(page.s_eles(".missing")).__name__, "SessionElementsList",
                 "missing session-element collections should preserve their empty collection type")

    sentinel = object()
    page._wait.loaded = True
    with _patched(chromium_base_module, make_session_ele=lambda *args, **kwargs: sentinel):
        assert_true(page.s_ele("#item") is sentinel, "loaded session-element lookup should use the session wrapper")
        assert_true(page.s_eles(".item") is sentinel, "loaded session-element collections should use the session wrapper")


def test_tab_cookie_conversion_mode_and_cleanup():
    tab = object.__new__(ChromiumTab)
    tab._target_id = "tab-extra"
    tab._context_id = "context-extra"
    tab._default_context = True
    tab._timeouts = Timeout(base=3, page_load=7, script=9)
    tab._wait = _WaitProbe(tab)
    tab._headers = {}
    tab._session = object()
    tab._response = None
    tab._messenger_running = True
    cdp_calls = []
    tab._run_func = lambda command, **kwargs: cdp_calls.append((command, kwargs)) or (
        {"result": {"value": "tab-agent"}} if command == "Runtime.evaluate" else
        {"cookies": [{"name": "sid", "value": "abc", "domain": "extra.test"}]}
    )
    session_cookie_calls = []
    with _patched(chromium_tab_module, set_session_cookies=lambda session, cookies: session_cookie_calls.append((session, cookies))):
        tab.cookies_to_session()
    assert_equal(tab._headers, {"User-Agent": "tab-agent"},
                 "cookies_to_session should copy the browser user agent into session headers")
    assert_equal(len(session_cookie_calls), 1, "cookies_to_session should transfer browser cookies once")
    assert_equal(session_cookie_calls[0][1].as_dict(), {"sid": "abc"},
                 "cookies_to_session should preserve transferred cookie values")

    browser_cookie_calls = []
    with _patched(
        chromium_tab_module,
        SessionPage=SessionPage,
        set_tab_cookies=lambda owner, cookies: browser_cookie_calls.append((owner, cookies)),
    ), _patched(SessionPage, cookies=lambda owner, *args: ["session-cookie"]):
        tab.cookies_to_browser()
    assert_equal(browser_cookie_calls, [(tab, ["session-cookie"])],
                 "cookies_to_browser should transfer session cookies through the tab helper")

    mode_cookie_calls = []
    tab._d_mode = True
    tab._mode_obj = SimpleNamespace()
    tab._response = SimpleNamespace(url="https://session.extra/")
    tab.cookies_to_session = lambda: mode_cookie_calls.append("cookies-to-session")
    tab.change_mode("s", go=False, copy_cookies=True)
    assert_false(tab._d_mode, "change_mode('s') should switch a tab into session mode")
    assert_equal(tab._url, "https://session.extra/", "session-mode transition should preserve response URL")
    assert_equal(mode_cookie_calls, ["cookies-to-session"],
                 "session-mode transition should copy cookies when requested")

    browser_calls = []
    close_tab = object.__new__(ChromiumTab)
    close_tab._target_id = "tab-close-extra"
    close_tab._browser = SimpleNamespace(
        _close_tab=lambda value: browser_calls.append(("close", value)),
        close_tabs=lambda value, **kwargs: browser_calls.append(("others", value, kwargs)),
    )
    close_tab._session = None
    close_tab._response = None
    close_tab.close(session=True)
    close_tab.close(others=True, session=True)
    assert_equal(browser_calls, [("close", close_tab), ("others", "tab-close-extra", {"others": True})],
                 "tab close should remain safe when no session or response resource exists")

    with _preserved_dict(ChromiumTab._TABS):
        ChromiumTab._TABS["tab-close-extra"] = close_tab
        close_tab._disconnect_flag = True
        close_tab._on_disconnect()
        assert_true("tab-close-extra" in ChromiumTab._TABS,
                    "disconnect during an intentional reconnect should preserve the singleton tab")
        close_tab._disconnect_flag = False
        close_tab._on_disconnect()
        assert_false("tab-close-extra" in ChromiumTab._TABS,
                     "ordinary disconnect should evict the singleton tab")


def test_frame_accessors_and_detach_bookkeeping():
    frame = object.__new__(ChromiumFrame)
    frame._scroll = None
    frame._set = None
    frame._states = None
    frame._wait = None
    frame._rect = None
    frame._listener = None
    frame._is_diff_domain = False
    frame._target_id = "frame-extra"
    frame._frame_id = "frame-extra-id"
    frame._tab = SimpleNamespace(tab_id="tab-extra")
    frame._browser = SimpleNamespace(_tabs=SimpleNamespace(remove_frame=lambda frame_id: None))
    frame._stop_messenger = lambda: None

    with _patched(
        chromium_frame_module,
        FrameScroller=_Widget,
        ChromiumFrameSetter=_Widget,
        FrameStates=_Widget,
        FrameWaiter=_Widget,
        FrameRect=_Widget,
        FrameListener=_Widget,
    ):
        wait = frame.wait
        assert_true(frame.wait is wait, "frame wait should cache a single frame waiter")
        assert_true(frame.scroll is frame._scroll, "frame scroll should cache its wrapper")
        assert_true(frame.set is frame._set, "frame set should cache its wrapper")
        assert_true(frame.states is frame._states, "frame states should cache its wrapper")
        assert_true(frame.rect is frame._rect, "frame rect should cache its wrapper")
        assert_true(frame.listen is frame._listener, "frame listener should cache its wrapper")
        assert_equal(wait.loaded_calls, 1, "frame scroll should wait for document readiness")

    frame._is_diff_domain = True
    frame._run_func = lambda command, **kwargs: {"result": {"value": "interactive"}}
    assert_equal(frame._js_ready_state, "interactive",
                 "cross-domain frame ready state should use the base runtime evaluator")

    navigated = []
    frame._is_diff_domain = False
    frame._stop_messenger = lambda: navigated.append("stopped")
    frame._onFrameNavigated(frame={"id": "frame-extra"})
    assert_equal(navigated, ["stopped"],
                 "same-domain navigation of the target frame should stop its stale messenger")

    removed = []
    frame._browser = SimpleNamespace(_tabs=SimpleNamespace(remove_frame=removed.append))
    frame._stop_messenger = lambda: removed.append("stop")
    with _preserved_dict(ChromiumFrame._Frames):
        ChromiumFrame._Frames["frame-extra-id"] = frame
        frame._onFrameDetached(frameId="other-frame", reason="remove")
        assert_equal(removed, [], "detachment for another frame should not mutate this frame's bookkeeping")
        frame._onFrameDetached(frameId="frame-extra-id", reason="remove")
        assert_equal(removed, ["frame-extra-id", "stop"],
                     "removed frames should unregister their frame id and stop their messenger")
        assert_false("frame-extra-id" in ChromiumFrame._Frames,
                     "removed frames should leave the singleton frame cache")
        frame._onFrameDetached(frameId="frame-extra-id", reason="ignored")
        assert_equal(removed, ["frame-extra-id", "stop"],
                     "unknown detach reasons should be ignored safely")
