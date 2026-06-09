"""Feature: frame, shadow-root, link, and setter contracts."""
from __future__ import annotations

from feature_cases.browser_interaction_server import browser_interaction_server
from support import assert_equal, assert_in, assert_true, chromium

FEATURE_ID = "frame_shadow_setters"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed frame/shadow contracts skipped by --skip-browser")
    with browser_interaction_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + "/main"), "frame/shadow test page should load")

        frame_ele = tab.ele("#child-frame", timeout=3)
        frame = tab.get_frame("child-frame", timeout=3)
        assert_equal(tab.ele("#frame-child", timeout=3).text, "frame child", "tab should locate iframe inner element directly")
        assert_true(frame, "tab.get_frame() should return the iframe object")
        assert_equal(frame.ele("#frame-child", timeout=3).text, "frame child", "frame object should locate its inner element")
        assert_equal(frame_ele.link, frame.url, "iframe element link should expose frame URL")
        assert_equal(frame.ele("#frame-link").link.split("?")[0], frame.url.rsplit("/", 1)[0] + "/asset.txt", "link property should resolve href")
        assert_equal(tab.ele("#asset-link").src(), "asset-content", "src() should fetch linked file content from link[href]")

        host = tab.ele("#host", timeout=3)
        shadow = host.shadow_root
        assert_true(shadow, "shadow_root should be available after attachment")
        assert_equal(shadow.ele("#shadow-btn", timeout=3).attr("data-role"), "shadow", "shadow root CSS lookup should find inner button")

        primary = tab.ele("#primary")
        primary.set.property("dpProp", "value41")
        primary.set.style("border", "3px solid rgb(1, 2, 3)")
        assert_equal(primary.property("dpProp"), "value41", "set.property() should update DOM property")
        assert_in("3px", primary.style("border-top-width"), "set.style() should update computed style")
        assert_true(primary.timeout >= 0, "element timeout property should be readable")
