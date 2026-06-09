"""Feature: recommended Chromium() entry and Page-object migration surface."""
from __future__ import annotations

import DrissionPage as dp
from DrissionPage import Chromium

from support import assert_false, assert_true, version_tuple


FEATURE_ID = 'recommended_chromium_entry'


def run(ctx):
    assert_true(version_tuple() >= (4, 2, 0), f'expected DrissionPage current 4.2+ release target, got {dp.__version__}')
    assert_true(hasattr(dp, 'Chromium'), 'Chromium should be exported as recommended browser entry point')
    assert_true(hasattr(dp, 'ChromiumPage'), 'ChromiumPage should remain importable for compatibility')
    assert_false(hasattr(dp, 'WebPage'), 'WebPage should not remain exported in the current public entry surface')
    assert_true(callable(Chromium), 'Chromium should be callable as the recommended entry object')
