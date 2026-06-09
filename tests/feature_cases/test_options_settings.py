"""Feature: startup option and Settings contracts."""
from __future__ import annotations

from tempfile import TemporaryDirectory

from DrissionPage import ChromiumOptions, SessionOptions
from DrissionPage._functions.settings import Settings

from support import assert_equal, assert_false, assert_in, assert_true

FEATURE_ID = "options_settings"
REQUIRES_BROWSER = False


def run(ctx):
    with TemporaryDirectory(prefix="dp-options-") as tmp:
        co = ChromiumOptions(read_file=False)
        assert_true(co.set_flag("temporary-unexpire-flags", "1") is co, "set_flag() should be chainable")
        assert_equal(co.flags.get("temporary-unexpire-flags"), "1", "set_flag() should persist flag value")
        co.set_flag("temporary-unexpire-flags", False)
        assert_false("temporary-unexpire-flags" in co.flags, "set_flag(flag, False) should remove the flag")
        assert_true(co.clear_flags_in_file() is co, "clear_flags_in_file() should be chainable")
        assert_true(getattr(co, "clear_file_flags", False), "clear_flags_in_file() should record clear intent")

        co.ignore_certificate_errors().incognito().set_retry(4, 0.2).set_tmp_path(tmp).set_load_mode("none")
        assert_in("--ignore-certificate-errors", co.arguments, "ignore_certificate_errors() should add Chrome argument")
        assert_in("--incognito", co.arguments, "incognito() should add Chrome incognito argument")
        assert_equal((co.retry_times, co.retry_interval), (4, 0.2), "set_retry() should update retry settings")
        assert_equal(co.tmp_path, tmp, "set_tmp_path() should persist tmp path")
        assert_equal(co.load_mode, "none", "set_load_mode('none') should persist load mode")

        co.set_browser_path("/tmp/chrome").set_local_port(9333).set_download_path(tmp).set_user_data_path(tmp).set_cache_path(tmp)
        assert_equal(co.browser_path, "/tmp/chrome", "set_browser_path() should persist browser path")
        assert_equal(co.address, "127.0.0.1:9333", "set_local_port() should persist debugger address")
        assert_equal(co.download_path, tmp, "set_download_path() should persist download path")
        assert_equal(co.user_data_path, tmp, "set_user_data_path() should persist user data path")
        assert_true(any(arg.startswith("--disk-cache-dir=") for arg in co.arguments), "set_cache_path() should add disk-cache argument")

    so = SessionOptions(read_file=False)
    so.set_download_path("/tmp/dp-session-downloads").set_retry(5, 0.1)
    assert_equal(so.download_path, "/tmp/dp-session-downloads", "SessionOptions.set_download_path() should persist path")
    assert_equal((so.retry_times, so.retry_interval), (5, 0.1), "SessionOptions.set_retry() should update retry settings")

    old_singleton = Settings.singleton_tab_obj
    old_raise = Settings.raise_when_ele_not_found
    try:
        Settings.set_singleton_tab_obj(False)
        Settings.set_raise_when_ele_not_found(False)
        assert_false(Settings.singleton_tab_obj, "Settings.set_singleton_tab_obj(False) should update setting")
        assert_false(Settings.raise_when_ele_not_found, "Settings.set_raise_when_ele_not_found(False) should update setting")
    finally:
        Settings.set_singleton_tab_obj(old_singleton)
        Settings.set_raise_when_ele_not_found(old_raise)
