"""Shared helpers for optional DrissionPage SSR test-site checks."""
from __future__ import annotations

import os
from urllib.parse import urljoin

TEST_SITE_URL_ENV = 'DP_TEST_SITE_URL'
LEGACY_FIXTURE_URL_ENV = 'DP_PRIVATE_FIXTURE_URL'


def test_site_base_url() -> str:
    """Return the configured shared test-site URL, preserving legacy env fallback."""
    return (
        os.environ.get(TEST_SITE_URL_ENV)
        or os.environ.get(LEGACY_FIXTURE_URL_ENV)
        or ''
    ).strip().rstrip('/')


def test_site_url(path: str = '') -> str:
    """Build an absolute URL for the shared DrissionPage test-site."""
    base = test_site_base_url()
    if not base:
        return ''
    if not path:
        return base
    return urljoin(base + '/', path.lstrip('/'))


def required_url_message(label: str) -> str:
    """Return a clear skip reason for missing shared test-site configuration."""
    return f'{label} requires {TEST_SITE_URL_ENV} or legacy {LEGACY_FIXTURE_URL_ENV}'
