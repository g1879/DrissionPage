"""Feature: built-in network listener contracts."""
from __future__ import annotations

from feature_cases.core_feature_server import core_feature_server
from support import assert_equal, assert_true, chromium, wait_for_packet

FEATURE_ID = "listener_basics"
REQUIRES_BROWSER = True


def run(ctx):
    if ctx.skip_browser:
        ctx.skip_current_browser("browser-backed listener contracts skipped by --skip-browser")
    with core_feature_server() as base, chromium(ctx) as browser:
        tab = browser.latest_tab

        tab.listen.start("/api")
        try:
            assert_true(tab.get(base + "/listener"), "listener page should load")
            packet = wait_for_packet(
                tab,
                lambda p: "/api?from=listener" in getattr(p, "url", ""),
                timeout=ctx.timeout,
                desc="listener fetch packet",
            )
            assert_equal(packet.request.method, "GET", "listener should expose request method")
            assert_equal(packet.response.status, 200, "listener should expose response status")
            assert_equal(packet.response.body["kind"], "core", "listener should expose parsed response body")
            assert_true(tab.listen.wait_silent(timeout=ctx.timeout, targets_only=True), "wait_silent(targets_only=True) should observe target quietness")
        finally:
            tab.listen.stop()

        tab.listen.start("/api?again=1")
        try:
            tab("#again").click(by_js=True)
            restarted = wait_for_packet(
                tab,
                lambda p: "/api?again=1" in getattr(p, "url", ""),
                timeout=ctx.timeout,
                desc="listener packet after restart",
            )
            assert_equal(restarted.response.body["kind"], "core", "listener should work after stop/start")
        finally:
            tab.listen.stop()
