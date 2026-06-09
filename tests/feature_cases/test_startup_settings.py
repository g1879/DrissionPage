"""Feature: Chromium startup settings added or changed in 4.2."""
from __future__ import annotations

from DrissionPage import ChromiumOptions

from support import assert_equal, assert_in, assert_not_in, assert_true


FEATURE_ID = 'startup_settings'


def run(ctx):
    co = ChromiumOptions(read_file=False)
    assert_in('--disable-site-isolation-trials', co.arguments,
              '4.2 default startup args should include cross-origin iframe support')
    assert_in('--test-type', co.arguments, '4.2 default startup args should include --test-type')
    assert_true(co.remove_test_type() is co, 'remove_test_type() should be chainable')
    assert_not_in('--disable-site-isolation-trials', co.arguments, 'remove_test_type() should remove site isolation flag')
    assert_not_in('--test-type', co.arguments, 'remove_test_type() should remove test type flag')

    edge = ChromiumOptions(read_file=False).set_browser_path(edge=True)
    assert_equal(edge.browser_path, 'msedge', 'set_browser_path(edge=True) should select Edge executable name')
    explicit = ChromiumOptions(read_file=False).set_browser_path('/custom/chrome', edge=True)
    assert_equal(explicit.browser_path, '/custom/chrome', 'explicit browser path should win over edge=True')

    pdf = ChromiumOptions(read_file=False)
    assert_true(pdf.disable_pdf_preview() is pdf, 'disable_pdf_preview() should be chainable')
    assert_true(pdf._prefs.get('plugins.always_open_pdf_externally'),
                'disable_pdf_preview() should set Chrome PDF external-open pref')
    pdf.disable_pdf_preview(False)
    assert_not_in('plugins.always_open_pdf_externally', pdf._prefs,
                  'disable_pdf_preview(False) should remove PDF external-open pref')

    system_user = ChromiumOptions(read_file=False).use_system_user_path(True, old_ver=True)
    assert_true(system_user.system_user_path, 'use_system_user_path(True) should enable system profile mode')
    assert_true(system_user._old_browser, 'use_system_user_path(old_ver=True) should retain old browser mode flag')

    user_data = ChromiumOptions(read_file=False).set_user_data_path('/tmp/dp-user').auto_port()
    assert_equal(user_data.user_data_path, '/tmp/dp-user',
                 'set_user_data_path() should remain compatible with auto_port()')
    assert_true(user_data.is_auto_port, 'auto_port() should remain enabled after set_user_data_path()')
