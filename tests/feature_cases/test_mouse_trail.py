"""Feature: show mouse trail setter behavior."""
from __future__ import annotations

from DrissionPage._units.setter import ChromiumBaseSetter

from support import assert_equal, assert_in, assert_true


FEATURE_ID = 'mouse_trail'


class FakeOwner:
    def __init__(self):
        self.js_calls = []

    def run_js(self, js):
        self.js_calls.append(js)


def run(ctx):
    owner = FakeOwner()
    setter = ChromiumBaseSetter(owner)
    assert_true(setter.show_trail(True) is setter, 'show_trail(True) should be chainable')
    setter.show_trail(False)
    assert_equal(len(owner.js_calls), 3, 'show_trail should inject once then enable and disable')
    assert_in('window.MouseTrail', owner.js_calls[0], 'show_trail should inject MouseTrail JS')
    assert_equal(owner.js_calls[1], 'MouseTrail.enable(); ', 'show_trail(True) should enable trail')
    assert_equal(owner.js_calls[2], 'MouseTrail.disable();', 'show_trail(False) should disable trail')
