# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestCase, TestContext, assert_equal, assert_true, chromium, local_server, wait_for_packet


def run(ctx: TestContext) -> None:
    # This check intentionally avoids screenshot APIs. It only covers iframe element access and waits.
    with local_server() as (base, _server), chromium(ctx) as browser:
        tab = browser.latest_tab
        tab.get(base + "/page/iframe-parent")
        frame = tab.get_frame("t:iframe")
        assert_true(frame, "same-origin iframe should be obtainable")
        assert_equal(frame.ele("#inside").text, "inside frame", "iframe element lookup mismatch")
        old_title = frame.title
        old_url = frame.url
        frame.ele("#swap").click()
        changed_url = frame.wait.url_change(old_url, timeout=ctx.timeout)
        assert_true(changed_url is not False, "iframe wait.url_change() should detect child navigation")
        changed_title = frame.wait.title_change(old_title, timeout=ctx.timeout)
        assert_true(changed_title is not False, "iframe wait.title_change() should detect child navigation")
        assert_equal(frame.title, "child-title-2", "iframe title after navigation mismatch")
        assert_true(frame.url.endswith("/page/iframe-child-2"), "iframe url after navigation mismatch", url=frame.url)

        # Direct lookup from tab into iframe content is a 4.2 non-screenshot cross-frame behavior.
        tab.get(base + "/page/iframe-parent")
        inside = tab.ele("#inside")
        assert_true(inside and inside.text == "inside frame", "tab should directly locate iframe inner element in 4.2")

        # Cross-host iframe listener: parent uses 127.0.0.1, child uses localhost, no screenshots involved.
        from DrissionPage.items import DataPacket
        port = base.rsplit(":", 1)[1]
        child = f"http://localhost:{port}/page/iframe-fetch-child"
        tab.listen.set_res_type.Fetch(only=True)
        tab.listen.start("/json?from=iframe")
        tab.get(base + "/page/iframe-parent?child=" + child)
        packet = wait_for_packet(tab, lambda p: isinstance(p, DataPacket) and "/json?from=iframe" in p.url, timeout=ctx.timeout, desc="cross-host iframe fetch DataPacket")
        assert_equal(packet.response.status, 200, "cross-host iframe listener packet status mismatch")
        tab.listen.stop()


TEST_CASE = TestCase(
    name="iframe_non_screenshot",
    title="Iframe direct element access and waits without screenshot scenarios",
    requires_browser=True,
    features=("cross_origin_iframe_element", "cross_origin_iframe_listener", "iframe_waits"),
    run=run,
)
