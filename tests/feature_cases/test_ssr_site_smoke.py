"""Optional Astro SSR fixture smoke checks."""
from __future__ import annotations

import os
import tempfile
import time
from urllib.parse import urljoin

from DrissionPage import SessionPage

from support import assert_equal, assert_in, assert_nav_result, assert_true, make_browser


FEATURE_ID = 'ssr_site_smoke'
FEATURES = ('ssr_site_smoke',)
BROWSER_PHASE = True
PRIVATE_FIXTURE_URL_ENV = 'DP_PRIVATE_FIXTURE_URL'


def site_url(path: str = '') -> str:
    base = (os.environ.get(PRIVATE_FIXTURE_URL_ENV) or '').strip().rstrip('/')
    if not base:
        return ''
    if not path:
        return base
    return urljoin(base + '/', path.lstrip('/'))


def wait_text_contains(tab, selector: str, expected: str, *, timeout: float = 10.0, interval: float = 0.1) -> str:
    deadline = time.time() + timeout
    last = ''
    while time.time() < deadline:
        last = tab(selector, timeout=2).text
        if expected in last:
            return last
        time.sleep(interval)
    assert_in(expected, last, f'{selector} should include expected text')
    return last


def run(ctx):
    if not ctx.include_online:
        ctx.skip('SSR site smoke requires --include-online')
        return
    base = site_url()
    if not base:
        ctx.skip(f'SSR fixture smoke requires {PRIVATE_FIXTURE_URL_ENV}')
        return

    session_page = SessionPage()
    health = session_page.get(site_url('/api/health.json'), timeout=20)
    assert_nav_result(health, status=200, ok=True, label='SSR health endpoint')
    health_json = health.Response.json()
    assert_true(health_json['ok'] is True, 'health endpoint should report ok=true')
    assert_equal(health_json['service'], 'drissionpage-ssr-test-site', 'health endpoint service mismatch')

    manifest = session_page.get(site_url('/api/manifest.json'), timeout=20)
    assert_nav_result(manifest, status=200, ok=True, label='SSR manifest endpoint')
    manifest_json = manifest.Response.json()
    assert_true(manifest_json['ok'] is True, 'manifest should report ok=true')
    case_ids = {item['id'] for item in manifest_json['cases']}
    for required in (
        'home',
        'locators',
        'network',
        'forms',
        'frames',
        'waits',
        'visual',
        'upload-download',
        'dynamic',
        'business-dashboard',
        'commerce',
        'cloudflare-gate',
        'marketplace-flow',
        'marketplace-search',
        'marketplace-item-detail',
        'marketplace-cart',
        'marketplace-checkout',
        'marketplace-order-result',
    ):
        assert_in(required, case_ids, 'manifest should include expected fixture case')

    missing = session_page.get(site_url('/api/status/404'), timeout=20, retry=0, raise_err=False)
    assert_nav_result(missing, status=404, ok=False, label='SSR explicit 404 endpoint')

    dynamic = session_page.get(site_url('/cases/dynamic?name=session-smoke'), timeout=20)
    assert_nav_result(dynamic, status=200, ok=True, label='SSR dynamic page')
    assert_in('session-smoke', session_page.html, 'SSR dynamic page should include query value')

    download = session_page.get(site_url('/api/download.txt?name=session-fixture.txt'), timeout=20)
    assert_nav_result(download, status=200, ok=True, label='SSR download endpoint')
    assert_in('attachment;', download.headers.get('content-disposition', ''),
              'download endpoint should expose attachment content-disposition')
    assert_in('session-fixture.txt', download.Response.text, 'download body should include requested filename')

    activity_batch = session_page.get(site_url('/api/activity-batch.json?offset=0&count=5&delay=1'), timeout=20)
    assert_nav_result(activity_batch, status=200, ok=True, label='SSR activity batch endpoint')
    activity_json = activity_batch.Response.json()
    assert_equal(activity_json['count'], 5, 'activity batch should return requested count')
    assert_equal(activity_json['items'][0]['title'], 'Activity 001',
                 'activity batch should return deterministic item titles')
    assert_equal(activity_json['items'][0]['amount'], 1013,
                 'activity batch should return deterministic business values')

    activity_limit = session_page.get(site_url('/api/activity-batch.json?offset=120&count=80&delay=1'), timeout=20)
    assert_nav_result(activity_limit, status=200, ok=True, label='SSR activity batch limit endpoint')
    activity_limit_json = activity_limit.Response.json()
    assert_equal(activity_limit_json['count'], 50, 'activity batch should cap large requested counts')
    assert_equal(activity_limit_json['nextOffset'], 170, 'activity batch should advance nextOffset after capped count')
    assert_equal(activity_limit_json['items'][-1]['title'], 'Activity 170',
                 'activity batch should keep deterministic high-offset item titles')

    commerce_products = session_page.get(site_url('/api/commerce/products.json?offset=0&count=4&delay=1'), timeout=20)
    assert_nav_result(commerce_products, status=200, ok=True, label='SSR commerce products endpoint')
    commerce_json = commerce_products.Response.json()
    assert_equal(commerce_json['count'], 4, 'commerce products endpoint should return requested count')
    assert_equal(commerce_json['items'][0]['sku'], 'SKU-0001',
                 'commerce products endpoint should return deterministic sku values')
    assert_equal(commerce_json['summary']['total'], 4, 'commerce products endpoint should expose summary total')

    cf_blocked = session_page.get(site_url('/api/cf/protected.json'), timeout=20, retry=0, raise_err=False)
    assert_nav_result(cf_blocked, status=403, ok=False, label='SSR Cloudflare-like protected endpoint without clearance')
    cf_blocked_json = cf_blocked.Response.json()
    assert_equal(cf_blocked_json['reason'], 'challenge_required',
                 'Cloudflare-like protected endpoint should require clearance first')

    cf_clearance = session_page.get(site_url('/cdn-cgi/challenge-platform/fixture-clearance'), timeout=20)
    assert_nav_result(cf_clearance, status=200, ok=True, label='SSR Cloudflare-like clearance endpoint')
    assert_in('cf_clearance=fixture-pass', cf_clearance.headers.get('set-cookie', ''),
              'Cloudflare-like clearance endpoint should set cf_clearance cookie')

    cf_protected = session_page.get(site_url('/api/cf/protected.json'), timeout=20)
    assert_nav_result(cf_protected, status=200, ok=True, label='SSR Cloudflare-like protected endpoint with clearance')
    assert_equal(cf_protected.Response.json()['clearance'], 'accepted',
                 'Cloudflare-like protected endpoint should accept fixture clearance cookie')

    cf_rate = session_page.get(site_url('/api/cf/protected.json?mode=rate-limit'), timeout=20, retry=0, raise_err=False)
    assert_nav_result(cf_rate, status=429, ok=False, label='SSR Cloudflare-like rate-limit endpoint')
    assert_equal(cf_rate.headers.get('retry-after'), '3',
                 'Cloudflare-like rate-limit endpoint should expose Retry-After')

    if ctx.skip_browser:
        ctx.skip_current_browser('SSR browser smoke skipped by --skip-browser')
        return

    with make_browser(ctx.browser_path, page_load_timeout=20) as browser:
        tab = browser.latest_tab

        home = tab.get(site_url('/'))
        assert_nav_result(home, status=200, ok=True, label='SSR home Chromium navigation')
        assert_equal(tab('[data-testid="site-name"]', timeout=10).text, 'DrissionPage SSR Test Site',
                     'home should expose stable site-name test id')
        assert_true(tab('[data-testid="api-manifest"]', timeout=10), 'home should link manifest endpoint')

        locators = tab.get(site_url('/cases/locators'))
        assert_nav_result(locators, status=200, ok=True, label='SSR locators page')
        assert_equal(tab('x://div[@id="target"]', timeout=10).attr('data-testid'), 'xpath-target',
                     'explicit XPath should find locator target')
        assert_equal(tab('ax:@name=Save Now@role=button', timeout=10).attr('data-testid'), 'aria-save-button',
                     'AX locator should find accessible button')

        network = tab.get(site_url('/cases/network'))
        assert_nav_result(network, status=200, ok=True, label='SSR network page')
        tab.listen.start('/api/echo.json')
        try:
            tab('[data-testid="fetch-json"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/echo.json?from=fetch-json' in packet.url,
                        'listener should capture SSR fixture fetch packet')
            assert_equal(packet.response.status, 200, 'SSR fixture fetch should return 200')
            assert_equal(packet.response.body['query']['from'], 'fetch-json',
                         'SSR fixture fetch should expose query in JSON body')
        finally:
            tab.listen.stop()
        deadline = time.time() + 10
        while time.time() < deadline and 'fetch-json status=200' not in tab('[data-testid="network-log"]').text:
            time.sleep(0.2)
        assert_in('fetch-json status=200', tab('[data-testid="network-log"]').text,
                  'network page should render fetch result in log')

        forms = tab.get(site_url('/cases/forms'))
        assert_nav_result(forms, status=200, ok=True, label='SSR forms page')
        tab.run_js(
            "const name = document.querySelector('[data-testid=\"name-input\"]');"
            "const mode = document.querySelector('[data-testid=\"mode-select\"]');"
            "const agree = document.querySelector('[data-testid=\"agree-checkbox\"]');"
            "name.value = 'business-user';"
            "name.dispatchEvent(new Event('input', { bubbles: true }));"
            "mode.value = 'beta';"
            "mode.dispatchEvent(new Event('change', { bubbles: true }));"
            "agree.checked = true;"
            "agree.dispatchEvent(new Event('change', { bubbles: true }));"
        )
        tab.listen.start('/api/echo.json')
        try:
            tab('[data-testid="submit-button"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and packet.response.status == 200, 'listener should capture form POST echo packet')
            assert_equal(packet.response.body['method'], 'POST', 'form echo should use POST')
            assert_equal(packet.response.body['body']['name'], 'business-user',
                         'form echo should include edited input value')
            assert_equal(packet.response.body['body']['mode'], 'beta',
                         'form echo should include selected mode')
        finally:
            tab.listen.stop()
        form_output = wait_text_contains(tab, '[data-testid="form-output"]', 'business-user')
        assert_in('beta', form_output, 'form output should include selected mode')

        frames = tab.get(site_url('/cases/frames'))
        assert_nav_result(frames, status=200, ok=True, label='SSR frames page')
        frame = tab.get_frame(1, timeout=10)
        assert_equal(frame('[data-testid="inside-frame"]', timeout=10).text, 'inside frame: primary',
                     'frame child should expose stable inside-frame text')
        tab.listen.start('/api/echo.json')
        try:
            frame('[data-testid="frame-fetch"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/echo.json?from=iframe' in packet.url,
                        'listener should capture fetch triggered inside iframe')
            assert_equal(packet.response.body['query']['from'], 'iframe',
                         'iframe fetch should expose query in JSON body')
        finally:
            tab.listen.stop()
        wait_text_contains(frame, '[data-testid="frame-output"]', 'iframe')

        waits = tab.get(site_url('/cases/waits'))
        assert_nav_result(waits, status=200, ok=True, label='SSR waits page')
        tab('[data-testid="start-waits"]', timeout=10).click(by_js=True)
        deadline = time.time() + 10
        while time.time() < deadline and tab('[data-testid="delayed-visible"]', timeout=2).attr('hidden') is not None:
            time.sleep(0.1)
        assert_true(tab('[data-testid="delayed-visible"]', timeout=2).attr('hidden') is None,
                    'wait fixture delayed-visible should become visible')
        deadline = time.time() + 10
        while time.time() < deadline and tab('[data-testid="text-target"]', timeout=2).text != 'text-ready':
            time.sleep(0.1)
        assert_equal(tab('[data-testid="text-target"]', timeout=2).text, 'text-ready',
                     'wait fixture text target should become ready')
        assert_equal(tab('[data-testid="attr-target"]', timeout=2).attr('data-state'), 'ready',
                     'wait fixture attr target should become ready')
        tab('[data-testid="stabilize-html"]', timeout=10).click(by_js=True)
        deadline = time.time() + 10
        while time.time() < deadline and tab('[data-testid="html-stable-list"]', timeout=2).attr('data-stable') != 'true':
            time.sleep(0.1)
        assert_equal(tab('[data-testid="html-stable-list"]', timeout=2).attr('data-stable'), 'true',
                     'wait fixture html-stable-list should mark stable')

        visual = tab.get(site_url('/cases/visual'))
        assert_nav_result(visual, status=200, ok=True, label='SSR visual page')
        assert_true(tab('[data-testid="visual-target"]', timeout=10), 'visual target should exist')
        assert_equal(tab('[data-testid="band-red"]', timeout=10).text, 'red band',
                     'visual fixture should expose red band')
        assert_true(tab('[data-testid="dot-top-left"]', timeout=10), 'visual fixture should expose green dot anchors')
        assert_true(tab('[data-testid="long-visual-target"]', timeout=10), 'visual fixture should expose long target')

        upload_download = tab.get(site_url('/cases/upload-download'))
        assert_nav_result(upload_download, status=200, ok=True, label='SSR upload/download page')
        assert_true(tab('[data-testid="file-input"]', timeout=10), 'upload fixture should expose file input')
        assert_in('/api/download.txt?name=dp-fixture.txt', tab('[data-testid="download-link"]', timeout=10).attr('href'),
                  'upload/download fixture should expose deterministic download link')
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as tmp:
            tmp.write('upload smoke')
            upload_path = tmp.name
        try:
            tab('[data-testid="file-input"]', timeout=10).input(upload_path)
            tab('[data-testid="upload-submit"]', timeout=10).click(by_js=True)
            deadline = time.time() + 10
            while time.time() < deadline and 'upload' not in tab('[data-testid="upload-output"]', timeout=2).text:
                time.sleep(0.1)
            assert_in('.txt', tab('[data-testid="upload-output"]', timeout=2).text,
                      'upload fixture should render uploaded file metadata')
        finally:
            try:
                os.unlink(upload_path)
            except OSError:
                pass

        business = tab.get(site_url('/cases/business-dashboard'))
        assert_nav_result(business, status=200, ok=True, label='SSR business dashboard page')
        assert_equal(tab('[data-testid="business-root"]', timeout=10).attr('data-total'), '120',
                     'business dashboard should expose large deterministic list total')
        assert_equal(tab.run_js('return document.querySelectorAll("[data-testid=activity-row]").length'), 120,
                     'business dashboard should render 120 initial rows')
        assert_equal(tab('[data-testid="summary-blocked"]', timeout=10).attr('data-count'), '12',
                     'business dashboard should expose deterministic blocked summary')

        tab.run_js(
            "const input = document.querySelector('[data-testid=\"business-search\"]');"
            "input.value = 'Activity 042';"
            "input.dispatchEvent(new Event('input', { bubbles: true }));"
        )
        wait_text_contains(tab, '[data-testid="business-output"]', 'visible=1')

        tab.run_js(
            "const select = document.querySelector('[data-testid=\"status-filter\"]');"
            "select.value = 'pending';"
            "select.dispatchEvent(new Event('change', { bubbles: true }));"
        )
        wait_text_contains(tab, '[data-testid="business-output"]', 'visible=0')

        tab.run_js(
            "const input = document.querySelector('[data-testid=\"business-search\"]');"
            "const select = document.querySelector('[data-testid=\"status-filter\"]');"
            "input.value = '';"
            "input.dispatchEvent(new Event('input', { bubbles: true }));"
            "select.value = 'blocked';"
            "select.dispatchEvent(new Event('change', { bubbles: true }));"
        )
        wait_text_contains(tab, '[data-testid="business-output"]', 'visible=12')

        tab('[data-testid="select-visible"]', timeout=10).click(by_js=True)
        wait_text_contains(tab, '[data-testid="business-output"]', 'selected=12')

        tab.listen.start('/api/activity-batch.json')
        try:
            tab('[data-testid="load-more"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/activity-batch.json?offset=120&count=8' in packet.url,
                        'listener should capture activity load-more packet')
            assert_equal(packet.response.status, 200, 'activity load-more should return 200')
            assert_equal(packet.response.body['count'], 8, 'activity load-more should return 8 items')
        finally:
            tab.listen.stop()

        wait_text_contains(tab, '[data-testid="business-output"]', 'total=128')
        assert_equal(tab.run_js('return document.querySelectorAll("[data-testid=activity-row]").length'), 128,
                     'business dashboard should contain appended rows')

        tab('[data-testid="burst-fetch"]', timeout=10).click(by_js=True)
        wait_text_contains(tab, '[data-testid="business-output"]', 'burst=6; items=18')

        commerce = tab.get(site_url('/cases/commerce'))
        assert_nav_result(commerce, status=200, ok=True, label='SSR commerce workflow page')
        assert_equal(tab('[data-testid="commerce-root"]', timeout=10).attr('data-total'), '60',
                     'commerce page should expose deterministic initial product total')
        assert_equal(tab.run_js('return document.querySelectorAll("[data-testid=product-card]").length'), 60,
                     'commerce page should render 60 initial product cards')
        assert_equal(tab('[data-testid="commerce-summary-electronics"]', timeout=10).attr('data-count'), '15',
                     'commerce page should expose deterministic category summary')

        tab.run_js(
            "const category = document.querySelector('[data-testid=\"commerce-category\"]');"
            "category.value = 'electronics';"
            "category.dispatchEvent(new Event('change', { bubbles: true }));"
        )
        wait_text_contains(tab, '[data-testid="commerce-output"]', 'visible=15')

        tab.run_js(
            "const input = document.querySelector('[data-testid=\"commerce-search\"]');"
            "const category = document.querySelector('[data-testid=\"commerce-category\"]');"
            "category.value = 'all';"
            "category.dispatchEvent(new Event('change', { bubbles: true }));"
            "input.value = 'Fixture Product 012';"
            "input.dispatchEvent(new Event('input', { bubbles: true }));"
        )
        wait_text_contains(tab, '[data-testid="commerce-output"]', 'visible=1')

        tab.run_js(
            "const input = document.querySelector('[data-testid=\"commerce-search\"]');"
            "const sort = document.querySelector('[data-testid=\"commerce-sort\"]');"
            "input.value = '';"
            "input.dispatchEvent(new Event('input', { bubbles: true }));"
            "sort.value = 'price-desc';"
            "sort.dispatchEvent(new Event('change', { bubbles: true }));"
        )
        wait_text_contains(tab, '[data-testid="commerce-output"]', 'visible=60')

        tab.listen.start('/api/commerce/cart.json')
        try:
            tab.run_js(
                "const card = Array.from(document.querySelectorAll('[data-testid=\"product-card\"]'))"
                ".find((item) => item.dataset.stock !== 'sold_out');"
                "card.querySelector('[data-testid=\"product-variant\"]').value = "
                "card.querySelector('[data-testid=\"product-variant\"] option:last-child').value;"
                "card.querySelector('[data-testid=\"add-to-cart\"]').click();"
            )
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/commerce/cart.json' in packet.url,
                        'listener should capture commerce cart POST packet')
            assert_equal(packet.response.status, 200, 'commerce cart endpoint should return 200')
            assert_equal(packet.response.body['ok'], True, 'commerce cart endpoint should report ok=true')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="cart-output"]', 'cart=1')

        tab.listen.start('/api/commerce/products.json')
        try:
            tab('[data-testid="commerce-load-more"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/commerce/products.json?offset=60&count=20' in packet.url,
                        'listener should capture commerce load-more packet')
            assert_equal(packet.response.body['count'], 20, 'commerce load-more should return 20 products')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="commerce-output"]', 'total=80')
        assert_equal(tab.run_js('return document.querySelectorAll("[data-testid=product-card]").length'), 80,
                     'commerce page should append lazy-loaded products')

        tab('[data-testid="commerce-recommend"]', timeout=10).click(by_js=True)
        wait_text_contains(tab, '[data-testid="recommendations"]', 'recommendations=4')

        tab('[data-testid="open-checkout"]', timeout=10).click(by_js=True)
        assert_true(tab.run_js('return document.querySelector("[data-testid=checkout-dialog]").open === true'),
                    'commerce checkout dialog should open')
        tab.run_js(
            "document.querySelector('[data-testid=\"checkout-email\"]').value = 'qa-buyer@example.test';"
            "document.querySelector('[data-testid=\"checkout-address\"]').value = '99 Fixture Avenue';"
        )
        tab.listen.start('/api/commerce/checkout.json')
        try:
            tab('[data-testid="checkout-submit"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/commerce/checkout.json' in packet.url,
                        'listener should capture commerce checkout POST packet')
            assert_equal(packet.response.status, 200, 'commerce checkout endpoint should return 200')
            assert_equal(packet.response.body['status'], 'reserved',
                         'commerce checkout should reserve deterministic order')
            assert_equal(packet.response.body['itemCount'], 1,
                         'commerce checkout should include current cart item count')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="checkout-output"]', 'status=reserved')

        cf_page = tab.get(site_url('/cases/cloudflare-gate'))
        assert_nav_result(cf_page, status=200, ok=True, label='SSR Cloudflare-like gate page')
        assert_in('Checking your browser', tab('[data-testid="cf-challenge-title"]', timeout=10).text,
                  'Cloudflare-like page should expose challenge title')
        assert_equal(tab('[data-testid="cf-challenge"]', timeout=10).attr('data-cf-ray'), '79f4c2d4b8b9dp01-SJC',
                     'Cloudflare-like page should expose deterministic Ray ID')

        tab.listen.start('/cdn-cgi/challenge-platform/fixture-clearance')
        try:
            tab('[data-testid="issue-clearance"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/cdn-cgi/challenge-platform/fixture-clearance' in packet.url,
                        'listener should capture Cloudflare-like clearance request')
            assert_equal(packet.response.status, 200, 'Cloudflare-like clearance endpoint should return 200')
            assert_equal(packet.response.body['clearance'], 'issued',
                         'Cloudflare-like clearance endpoint should issue fixture clearance')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="cf-output"]', 'clearance=issued')
        assert_in('cf_clearance=fixture-pass', tab.run_js('return document.cookie'),
                  'Cloudflare-like browser flow should set cf_clearance cookie')

        tab.listen.start('/api/cf/protected.json')
        try:
            tab('[data-testid="fetch-protected"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/cf/protected.json' in packet.url,
                        'listener should capture Cloudflare-like protected request')
            assert_equal(packet.response.status, 200, 'protected request should pass after clearance')
            assert_equal(packet.response.body['clearance'], 'accepted',
                         'protected request should accept fixture clearance')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="cf-output"]', 'protected=200')

        tab.listen.start('/api/cf/protected.json?mode=blocked')
        try:
            tab('[data-testid="fetch-blocked"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and 'mode=blocked' in packet.url,
                        'listener should capture Cloudflare-like blocked request')
            assert_equal(packet.response.status, 403, 'blocked request should return 403')
            assert_equal(packet.response.body['code'], 1020,
                         'blocked request should expose synthetic Cloudflare code 1020')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="cf-output"]', 'blocked=403')

        tab.listen.start('/api/cf/protected.json?mode=rate-limit')
        try:
            tab('[data-testid="fetch-rate-limit"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and 'mode=rate-limit' in packet.url,
                        'listener should capture Cloudflare-like rate-limit request')
            assert_equal(packet.response.status, 429, 'rate-limit request should return 429')
            assert_equal(packet.response.headers.get('retry-after'), '3',
                         'rate-limit request should expose Retry-After header')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="cf-output"]', 'rate=429')
