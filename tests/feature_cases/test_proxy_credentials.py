"""Feature: username/password proxy parsing before and after browser startup."""
from __future__ import annotations

from inspect import signature

from DrissionPage import Chromium, ChromiumOptions

from support import assert_equal, assert_in


FEATURE_ID = 'proxy_credentials'


def run(ctx):
    proxy = ChromiumOptions(read_file=False).set_proxy('http://alice:secret@proxy.test:8080')
    assert_equal(proxy.proxy_url, 'http://proxy.test:8080', 'proxy_url should strip credentials')
    assert_equal(proxy.proxy_usr, 'alice', 'proxy username should be parsed')
    assert_equal(proxy.proxy_pwd, 'secret', 'proxy password should be parsed')
    assert_equal(proxy.proxy, 'http://alice:secret@proxy.test:8080', 'original proxy string should be preserved')
    assert_in('--proxy-server=http://proxy.test:8080', proxy.arguments,
              'Chromium should receive credential-free proxy-server argument')

    params = signature(Chromium.new_context).parameters
    assert_in('proxy', params, 'Chromium.new_context() should expose per-context proxy')
    assert_in('proxy_bypass', params, 'Chromium.new_context() should expose proxy_bypass')
