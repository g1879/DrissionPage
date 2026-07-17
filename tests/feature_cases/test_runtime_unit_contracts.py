"""Feature: deterministic click, recording, download, and waiter contracts."""
from __future__ import annotations

from base64 import b64encode
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from types import SimpleNamespace

from DrissionPage._units.clicker import Clicker
from DrissionPage._units.downloader import DownloadManager, DownloadMission, TabDownloadSettings
from DrissionPage._units.screencast import Screencast
from DrissionPage._units.waiter import (
    BaseWaiter,
    BrowserContextWaiter,
    BrowserWaiter,
    ChromiumTabWaiter,
    FrameWaiter,
    get_frame_title,
    get_frame_url,
    wait_mission,
)
from DrissionPage.errors import JavaScriptError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "runtime_unit_contracts"
REQUIRES_BROWSER = False


def _expect_raises(exc_type, func, message):
    try:
        func()
    except exc_type:
        return
    raise AssertionError(message)


class ScreencastOwner:
    def __init__(self, tmp_path):
        self.browser = SimpleNamespace(_chromium_options=SimpleNamespace(tmp_path=tmp_path))
        self.callbacks = []
        self.cdp_calls = []
        self.js_calls = []
        self.blob_ready = True
        self.blob = b64encode(b"recorded-bytes").decode()

    def _set_callback(self, event, callback):
        self.callbacks.append((event, callback))

    def _run_cdp(self, method, **kwargs):
        self.cdp_calls.append((method, kwargs))

    def _run_js(self, script, *args, **kwargs):
        self.js_calls.append((script, args, kwargs))
        if script == "return DrissionPage_Screencast_blob_ok;":
            return self.blob_ready
        if script == "return DrissionPage_Screencast_blob;":
            return self.blob
        return None


def test_screencast_contracts():
    with TemporaryDirectory(prefix="dp-screencast-contracts-") as tmp:
        owner = ScreencastOwner(tmp)
        cast = Screencast(owner)
        _expect_raises(RuntimeError, cast.start, "start() without a save path should fail")

        with NamedTemporaryFile(dir=tmp) as file_obj:
            _expect_raises(ValueError, lambda: cast.set_save_path(file_obj.name),
                           "set_save_path() should reject existing files")

        frames = Path(tmp) / "frames"
        cast.set_mode.frugal_imgs_mode()
        assert_equal(cast._mode, "frugal_imgs", "frugal image mode should update the recording mode")
        cast.start(frames)
        assert_true(frames.is_dir(), "start() should create the output directory")
        assert_in(("Page.startScreencast", {"everyNthFrame": 1, "quality": 100}), owner.cdp_calls,
                  "frugal mode should start CDP screencasting")
        payload = b64encode(b"jpeg-data").decode()
        cast._onScreencastFrame(metadata={"timestamp": 12.5}, data=payload, sessionId=7)
        assert_equal((frames / "12.5.jpg").read_bytes(), b"jpeg-data", "frame callback should decode JPEG bytes")
        assert_equal(owner.cdp_calls[-1], ("Page.screencastFrameAck", {"sessionId": 7}),
                     "frame callback should acknowledge the exact session id")
        assert_equal(cast.stop(), str(frames.resolve()), "image mode stop() should return the output folder")
        assert_equal(owner.callbacks[-1], ("Page.screencastFrame", None), "stop() should unregister frame callback")
        assert_equal(owner.cdp_calls[-1], ("Page.stopScreencast", {}), "stop() should stop CDP screencasting")

        js_dir = Path(tmp) / "js"
        js_cast = Screencast(owner)
        js_cast.set_mode.js_video_mode()
        assert_equal(js_cast._mode, "js_video", "JS video mode should update the recording mode")
        js_cast.start(js_dir)
        js_path = js_cast.stop("capture", suffix="webm")
        assert_equal(Path(js_path).read_bytes(), b"recorded-bytes", "JS recording stop() should write decoded blob bytes")
        assert_true(js_path.endswith("capture.webm"), "stop() should append the requested suffix")
        assert_true(any(call[0] == "mediaRecorder.stop();" for call in owner.js_calls),
                    "JS stop should stop the MediaRecorder")

        mode_probe = Screencast(owner)
        mode_probe.set_mode.video_mode()
        assert_equal(mode_probe._mode, "video", "video_mode should select normal video")
        mode_probe.set_mode.frugal_video_mode()
        assert_equal(mode_probe._mode, "frugal_video", "frugal_video_mode should select frugal video")
        mode_probe.set_mode.imgs_mode()
        assert_equal(mode_probe._mode, "imgs", "imgs_mode should select screenshot sequence mode")


class ElementScroll:
    def __init__(self):
        self.calls = 0

    def to_see(self):
        self.calls += 1


class OwnerScroll:
    def __init__(self):
        self.calls = []

    def to_see(self, ele):
        self.calls.append(ele)


class FakeClickOwner:
    def __init__(self):
        self.cdp_calls = []
        self.js_calls = []
        self.scroll = OwnerScroll()
        self.uploads = []
        self.upload_waits = 0
        self.set = SimpleNamespace(upload_files=self.uploads.append)
        self.wait = SimpleNamespace(upload_paths_inputted=self._upload_done)

    def _upload_done(self):
        self.upload_waits += 1

    def _run_cdp(self, method, **kwargs):
        self.cdp_calls.append((method, kwargs))
        if method == "DOM.getNodeForLocation":
            return {"backendNodeId": 99}
        return {}

    def _run_js(self, script, *args, **kwargs):
        self.js_calls.append((script, args, kwargs))
        if "function(){let x" in script:
            return True
        return True


class FakeClickable:
    tag = "button"
    timeout = 0.01
    _backend_id = 99

    def __init__(self):
        self.owner = FakeClickOwner()
        self.scroll = ElementScroll()
        self.js_calls = []
        self.states = SimpleNamespace(
            is_selected=False,
            is_enabled=True,
            is_displayed=True,
            is_in_viewport=True,
            is_covered=False,
        )
        self.rect = SimpleNamespace(
            viewport_corners=((1, 2), (11, 2), (11, 12), (1, 12)),
            viewport_click_point=(6, 7),
            viewport_midpoint=(6, 7),
            viewport_location=(1, 2),
            click_point=(106, 207),
            location=(101, 202),
            size=(10, 10),
        )
        self.wait = SimpleNamespace(has_rect=lambda **kwargs: self.rect.viewport_corners,
                                    clickable=lambda **kwargs: self)
        self.tab = SimpleNamespace(
            _context_id="context-1",
            url="https://example.test/old",
            title="Old title",
            wait=SimpleNamespace(url_change=lambda **kwargs: True, title_change=lambda **kwargs: True),
        )
        tabs = SimpleNamespace(get_newest_tab=lambda context_id: "old-tab")
        browser_wait = SimpleNamespace(_new_tab=lambda context_id, **kwargs: "new-tab")
        browser = SimpleNamespace(_tabs=tabs, wait=browser_wait,
                                  _get_tab=lambda context_id, tid: f"tab:{context_id}:{tid}")
        self.tab.browser = browser

    def _run_js(self, script):
        self.js_calls.append(script)


def test_clicker_contracts():
    ele = FakeClickable()
    click = Clicker(ele)
    assert_true(click.left(timeout=0) is ele, "simulated left click should return the element")
    assert_equal(ele.scroll.calls, 1, "simulated click should scroll the element into view")
    mouse_calls = [call for call in ele.owner.cdp_calls if call[0] == "Input.dispatchMouseEvent"]
    assert_equal([call[1]["type"] for call in mouse_calls[-2:]], ["mousePressed", "mouseReleased"],
                 "simulated click should press then release")
    assert_true(click.right() is ele, "right click should return the element")
    assert_true(click.at(offset_x=2, offset_y=3, button="middle", count=2) is ele,
                "offset click should return the element")
    assert_true(click.multi(3) is ele, "multi() should delegate the click count")
    assert_equal(mouse_calls[-1][1]["type"], "mouseReleased", "mouse event history should remain valid")

    assert_equal(click.middle(get_tab=True), "tab:context-1:new-tab", "middle click should return the new tab")
    assert_true(click.middle(get_tab=False) is None, "middle(get_tab=False) should not resolve a tab")
    assert_equal(click.for_new_tab(timeout=0.01), "tab:context-1:new-tab", "for_new_tab should return the opened tab")
    assert_true(click.for_url_change(timeout=0.01), "for_url_change should return a boolean success")
    assert_true(click.for_title_change(timeout=0.01), "for_title_change should return a boolean success")
    assert_true(click.for_url_change(text="new", exclude=False, timeout=0.01),
                "explicit URL wait arguments should pass through")
    click.to_upload(["a.txt", "b.txt"], by_js=True)
    assert_equal(ele.owner.uploads, [["a.txt", "b.txt"]], "to_upload should configure exact upload paths")
    assert_equal(ele.owner.upload_waits, 1, "to_upload should wait for file chooser completion")

    js_ele = FakeClickable()
    assert_true(Clicker(js_ele).left(by_js=True) is js_ele, "JS click should return the element")
    assert_equal(js_ele.js_calls, ["this.click();"], "JS click should call native click()")

    class FallbackJsElement(FakeClickable):
        def _run_js(self, script):
            self.js_calls.append(script)
            if script == "this.click();":
                raise JavaScriptError("native click failed")

    fallback = FallbackJsElement()
    assert_true(Clicker(fallback).left(by_js=True) is fallback, "JS fallback click should return the element")
    assert_true(fallback.js_calls[-1].startswith("function(){this.dispatchEvent"),
                "JS click failure should dispatch a MouseEvent fallback")

    class SelectApi:
        is_multi = True

        def __init__(self):
            self.selected = []
            self.canceled = []

        def by_option(self, option):
            self.selected.append(option)

        def cancel_by_option(self, option):
            self.canceled.append(option)

    select_api = SelectApi()
    select = SimpleNamespace(select=select_api)

    class Option:
        tag = "option"

        def __init__(self, selected):
            self.states = SimpleNamespace(is_selected=selected)

        def parent(self, locator):
            assert_equal(locator, "t:select", "option click should locate its select parent")
            return select

    unselected = Option(False)
    selected = Option(True)
    assert_true(Clicker(unselected).left() is unselected, "unselected option click should return the option")
    assert_true(Clicker(selected).left() is selected, "selected multi-option click should return the option")
    assert_equal(select_api.selected, [unselected], "unselected option should be selected")
    assert_equal(select_api.canceled, [selected], "selected multi-option should be canceled")


class FakeDownloadBrowser:
    def __init__(self, path):
        self.download_path = str(path)
        self._download_path = str(path)
        self._context_id = "default-context"
        self._messenger_running = True
        self.callbacks = []
        self.cdp_calls = []
        self._tabs = SimpleNamespace(
            get_context_id=lambda frame_id: "child-context",
            frame_ids={"frame-1": "tab-1"},
            openers={},
        )

    def _set_callback(self, event, callback):
        self.callbacks.append((event, callback))

    def _run_cdp(self, method, **kwargs):
        self.cdp_calls.append((method, kwargs))
        if method == "Target.getBrowserContexts":
            return {"browserContextIds": ["child-context"]}
        return {}


def test_download_contracts():
    old_tabs = dict(TabDownloadSettings.TABS)
    TabDownloadSettings.TABS.clear()
    try:
        with TemporaryDirectory(prefix="dp-download-contracts-") as tmp:
            root = Path(tmp)
            browser = FakeDownloadBrowser(root)
            manager = DownloadManager(browser)
            manager.set_path("browser", root)
            assert_true(manager._running, "set_path() should enable download management")
            assert_equal([event for event, _ in browser.callbacks],
                         ["Browser.downloadProgress", "Browser.downloadWillBegin"],
                         "set_path() should register both browser download callbacks")
            assert_in(("Browser.setDownloadBehavior", {
                "downloadPath": str(root), "behavior": "allowAndName", "eventsEnabled": True,
            }), browser.cdp_calls, "default context should configure browser download behavior")
            assert_in(("Browser.setDownloadBehavior", {
                "downloadPath": str(root), "behavior": "allowAndName", "eventsEnabled": True,
                "browserContextId": "child-context",
            }), browser.cdp_calls, "created contexts should receive download behavior")

            manager.set_rename("tab-1", "renamed", "txt")
            manager.set_file_exists("tab-1", "overwrite")
            manager.set_flag("tab-1", True)
            assert_true(manager.get_flag("tab-1"), "download flags should round-trip")
            manager._tmp_path = str(root / "tmp")
            Path(manager._tmp_path).mkdir()
            manager._onDownloadWillBegin(
                guid="guid-1", frameId="frame-1", suggestedFilename="original.bin", url="https://example.test/file"
            )
            mission = manager.missions["guid-1"]
            assert_equal((mission.name, mission.tab_id, mission._context_id), ("renamed.txt", "tab-1", "child-context"),
                         "download begin should apply tab rename/suffix and context ownership")
            assert_true(mission in manager.get_tab_missions("tab-1"), "download begin should index the tab mission")
            manager._onDownloadProgress(guid="guid-1", state="inProgress", receivedBytes=4, totalBytes=10)
            assert_equal(mission.rate, 40.0, "in-progress events should update download rate")
            (Path(manager._tmp_path) / "guid-1").write_bytes(b"downloaded")
            manager._onDownloadProgress(guid="guid-1", state="completed", receivedBytes=10, totalBytes=10)
            assert_true(mission.is_done, "completed download should mark the mission done")
            assert_equal(Path(mission.final_path).read_bytes(), b"downloaded", "completed download should move the file")
            assert_equal(mission.wait(show=False, timeout=0), mission.final_path,
                         "completed mission wait should return the final path")
            assert_in("100.0", repr(mission), "mission repr should include its completion rate")

            cancel_path = root / "cancel.tmp"
            cancel_path.write_text("cancel", encoding="utf-8")
            cancel_mission = DownloadMission(manager, "other-context", "tab-2", "guid-cancel", str(root),
                                              "cancel.txt", "https://example.test/cancel", str(root), "rename")
            cancel_mission.final_path = cancel_path
            manager._missions[cancel_mission.id] = cancel_mission
            cancel_mission.cancel()
            assert_equal(cancel_mission.state, "canceled", "cancel() should update mission state")
            assert_false(cancel_path.exists(), "cancel() should remove an existing final path")
            assert_equal(browser.cdp_calls[-1][1]["browserContextId"], "other-context",
                         "cancel() should target non-default context downloads")

            skip_tmp = root / "guid-skip"
            skip_tmp.write_text("skip", encoding="utf-8")
            skip_mission = DownloadMission(manager, "default-context", "tab-3", "guid-skip", str(root),
                                            "skip.txt", "https://example.test/skip", str(root), "skip")
            manager._missions[skip_mission.id] = skip_mission
            manager._tab_missions["tab-3"] = {skip_mission}
            manager.skip(skip_mission)
            assert_true(skip_mission.is_done, "skip() should finish the mission")
            assert_equal(skip_mission.state, "skipped", "skip() should preserve skipped state")
            assert_false(skip_tmp.exists(), "skip() should remove the temporary guid file")

            manager.set_flag("tab-3", True)
            manager._waiting_tab.add("tab-3")
            manager.clear_tab_info("tab-3")
            assert_true(manager.get_flag("tab-3") is None, "clear_tab_info() should remove flags")
            assert_false("tab-3" in TabDownloadSettings.TABS, "clear_tab_info() should remove tab settings")
    finally:
        TabDownloadSettings.TABS.clear()
        TabDownloadSettings.TABS.update(old_tabs)


def test_waiter_contracts():
    class Tabs:
        def __init__(self):
            self.values = ["old", "new"]
            self.index = 0

        def get_newest_tab(self, context_id):
            value = self.values[min(self.index, len(self.values) - 1)]
            self.index += 1
            return value

    tabs = Tabs()
    context_owner = SimpleNamespace(_context_id="context-2", _browser=SimpleNamespace(_tabs=tabs, timeout=0.01))
    assert_equal(BrowserContextWaiter(context_owner).new_tab(timeout=0.01), "new",
                 "new_tab() should return a changed newest tab id")

    class Mission:
        def __init__(self):
            self.canceled = 0

        def cancel(self):
            self.canceled += 1

    mission = Mission()
    dl_mgr = SimpleNamespace(_running=True, _missions={}, set_flag=lambda tid, flag: None,
                             get_flag=lambda tid: mission)
    browser = SimpleNamespace(_dl_mgr=dl_mgr, _messenger_running=True, timeout=0.01)
    assert_true(BrowserWaiter(browser).downloads_done(timeout=0.01),
                "downloads_done() should succeed when no missions remain")
    assert_true(wait_mission(browser, "browser", 0.01) is mission,
                "wait_mission() should return a non-boolean mission flag")

    class ElementWait:
        def hidden(self, timeout, raise_err=None):
            return "hidden"

    owner = SimpleNamespace(
        timeout=0.01,
        _messenger_running=True,
        _upload_list=["pending"],
        _is_loading=False,
        _target_id="target",
        _ele=lambda locator, **kwargs: SimpleNamespace(wait=ElementWait()),
        _run_cdp=lambda method, **kwargs: {"targetInfo": {"url": "https://example.test/a", "title": "A"}},
    )
    base = BaseWaiter(owner)
    assert_equal(base.ele_hidden("#one", timeout=0.01), "hidden", "ele_hidden() should delegate remaining timeout")
    owner._upload_list = []
    assert_true(base.upload_paths_inputted(timeout=0.01), "empty upload list should complete immediately")
    assert_false(base.url_change("missing", timeout=0), "unmatched URL change should return False")
    assert_false(base.title_change("A", exclude=True, timeout=0), "exclude wait should fail while text remains present")

    tab_dl = SimpleNamespace(_running=True, get_tab_missions=lambda tab_id: set())
    tab_owner = SimpleNamespace(
        browser=SimpleNamespace(_dl_mgr=tab_dl), tab_id="tab", states=SimpleNamespace(has_alert=False)
    )
    tab_waiter = ChromiumTabWaiter(tab_owner)
    assert_true(tab_waiter.downloads_done(timeout=None) is tab_owner,
                "downloads_done(timeout=None) should return once the tab has no missions")
    assert_true(tab_waiter.alert_closed(timeout=0) is tab_owner,
                "alert_closed(timeout=0) should return when no alert is open")

    frame = SimpleNamespace(
        timeout=0.01,
        frame_ele=SimpleNamespace(timeout=0.01),
        _frame_id="child",
        run_js=lambda script: "Frame title",
        _run_cdp=lambda method: {"frameTree": {"frame": {"id": "root", "url": "root"},
                                                     "childFrames": [{"frame": {"id": "child", "url": "child-url"}}]}},
    )
    assert_equal(get_frame_title(frame), "Frame title", "get_frame_title() should return document.title")
    assert_equal(get_frame_url(frame), "child-url", "get_frame_url() should locate the matching child frame")
    frame_waiter = FrameWaiter(frame)
    assert_true(frame_waiter.title_change("Frame", timeout=0.01) is frame,
                "FrameWaiter should use frame title for title_change")
    assert_true(frame_waiter.url_change("child", timeout=0.01) is frame,
                "FrameWaiter should use frame tree URL for url_change")


def run(ctx):
    test_screencast_contracts()
    test_clicker_contracts()
    test_download_contracts()
    test_waiter_contracts()
