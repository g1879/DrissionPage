# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestCase, TestContext, TestFailure, assert_equal, assert_true, function_accepts


def run(ctx: TestContext) -> None:
    import inspect
    import DrissionPage
    from DrissionPage import Chromium, ChromiumOptions
    from DrissionPage._functions.settings import Settings
    from DrissionPage._pages.chromium_tab import ChromiumTab
    from DrissionPage._elements.chromium_element import ChromiumElement
    from DrissionPage._units.actions import Actions
    from DrissionPage._units.clicker import Clicker
    from DrissionPage._units.waiter import ChromiumTabWaiter, ElementWaiter

    errors: list[str] = []

    def check(condition, message: str) -> None:
        if not condition:
            errors.append(message)

    def accepts(obj, param: str, label: str) -> None:
        check(function_accepts(obj, param), f"{label} should accept `{param}`")

    check(callable(Chromium), "Chromium entrypoint should be callable")
    check(hasattr(DrissionPage, "ChromiumPage"), "ChromiumPage should remain import-compatible during transition")

    co = ChromiumOptions(read_file=False)
    check(hasattr(co, "remove_test_type"), "ChromiumOptions.remove_test_type() missing")
    if hasattr(co, "remove_test_type"):
        check(co.remove_test_type() is co, "remove_test_type() should be chainable")
    check(hasattr(co, "disable_pdf_preview"), "ChromiumOptions.disable_pdf_preview() missing")
    if hasattr(co, "disable_pdf_preview"):
        check(co.disable_pdf_preview() is co, "disable_pdf_preview() should be chainable")
    accepts(co.set_browser_path, "edge", "set_browser_path")
    accepts(co.set_proxy, "proxy", "set_proxy")
    co.set_proxy("http://user:pass@127.0.0.1:8080")
    check(co.proxy_url == "http://127.0.0.1:8080", f"proxy_url should strip credentials, got {co.proxy_url!r}")
    check(co.proxy == "http://user:pass@127.0.0.1:8080", f"proxy should preserve original auth proxy string, got {co.proxy!r}")
    check(co.proxy_usr == "user", f"proxy username should be parsed, got {co.proxy_usr!r}")
    check(co.proxy_pwd == "pass", f"proxy password should be parsed, got {co.proxy_pwd!r}")
    co.auto_port().set_user_data_path(ctx.artifacts_dir / "user-data")
    check(co.is_auto_port, "auto_port should remain enabled after set_user_data_path")

    check(hasattr(Settings, "wait_stop_before_click"), "Settings.wait_stop_before_click missing")
    check(hasattr(Settings, "set_wait_stop_before_click"), "Settings.set_wait_stop_before_click missing")

    check(hasattr(ChromiumTab, "activate"), "ChromiumTab.activate() missing")
    check(hasattr(ChromiumTab, "new_ele"), "ChromiumTab.new_ele() missing")
    check(hasattr(ChromiumTab, "drag_in"), "Docs say ChromiumTab.drag_in(offset_x/offset_y) exists, but ChromiumTab.drag_in is missing")
    if hasattr(ChromiumTab, "drag_in"):
        accepts(ChromiumTab.drag_in, "offset_x", "ChromiumTab.drag_in")
        accepts(ChromiumTab.drag_in, "offset_y", "ChromiumTab.drag_in")
    # The actual implementation currently lives on tab.actions; verify offsets there too.
    accepts(Actions.drag_in, "offset_x", "Actions.drag_in")
    accepts(Actions.drag_in, "offset_y", "Actions.drag_in")
    accepts(ChromiumTab.get, "raise_err", "ChromiumTab.get")
    accepts(ChromiumTabWaiter.upload_paths_inputted, "timeout", "wait.upload_paths_inputted")

    check(hasattr(ChromiumElement, "css_selector"), "ChromiumElement.css_selector missing")
    accepts(ChromiumElement.check, "checked", "ChromiumElement.check")
    accepts(Clicker.__call__, "wait_stop", "Element.click")
    sig = inspect.signature(Clicker.__call__)
    check(sig.parameters.get("wait_stop") is not None and sig.parameters["wait_stop"].default is False,
          f"Element.click(wait_stop) should default to False, got {sig.parameters.get('wait_stop')}")
    accepts(Clicker.to_download, "file_exists", "click.to_download")
    accepts(ElementWaiter.clickable, "wait_stop", "wait.clickable")

    if errors:
        raise TestFailure("API surface mismatches:\n- " + "\n- ".join(errors))


TEST_CASE = TestCase(
    name="api_surface",
    title="4.2 API surface and option compatibility",
    requires_browser=False,
    features=(
        "chromium_entrypoint", "proxy_auth", "remove_test_type", "edge_path", "user_data_logic",
        "disable_pdf_preview", "show_trail", "drag_in_offsets", "new_ele", "upload_timeout", "click_defaults",
        "download_file_exists", "wait_clickable_wait_stop", "settings_wait_stop", "actions_key_tuple",
    ),
    run=run,
)
