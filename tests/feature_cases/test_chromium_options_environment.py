"""Feature: ChromiumOptions new environment contracts."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from DrissionPage import ChromiumOptions
from support import assert_equal, assert_true

FEATURE_ID = "chromium_options_environment"
REQUIRES_BROWSER = False


def run(ctx):
    co = ChromiumOptions(read_file=False)
    assert_true(co.new_env() is co, "ChromiumOptions.new_env() should be chainable")
    assert_true(getattr(co, "_new_env", False), "new_env() should persist the new environment option")
    assert_true(hasattr(co, "is_headless"), "ChromiumOptions.is_headless should exist")

    with TemporaryDirectory() as tmp:
        auto = ChromiumOptions(read_file=False).auto_port(scope=tmp)
        assert_true(auto.is_auto_port, "auto_port(scope=...) should enable auto-port mode")
        assert_equal(Path(auto._auto_port).resolve(), Path(tmp).resolve(), "auto_port(scope) should persist the scope path")
