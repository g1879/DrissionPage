"""Optional SSR marketplace full-flow checks."""
from __future__ import annotations

import os
import time
from urllib.parse import urljoin

from DrissionPage import SessionPage

from support import assert_equal, assert_in, assert_nav_result, assert_true, make_browser


FEATURE_ID = 'ssr_marketplace_flow'
FEATURES = ('ssr_marketplace_flow',)
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
        ctx.skip('SSR marketplace flow requires --include-online')
        return
    base = site_url()
    if not base:
        ctx.skip(f'SSR marketplace flow requires {PRIVATE_FIXTURE_URL_ENV}')
        return

    session_page = SessionPage()
    search = session_page.get(site_url('/api/marketplace/search.json?query=耳机&count=4&delay=1'), timeout=20)
    assert_nav_result(search, status=200, ok=True, label='marketplace search endpoint')
    search_json = search.Response.json()
    assert_true(search_json['ok'] is True, 'marketplace search endpoint should report ok=true')
    assert_equal(search_json['query'], '耳机', 'marketplace search should echo query')
    assert_equal(search_json['count'], 4, 'marketplace search should return requested item count')
    assert_equal(len(search_json['items']), 4, 'marketplace search item list should match count')
    assert_true(search_json['summary']['total'] >= 100, 'marketplace summary should expose large deterministic catalog')

    if ctx.skip_browser:
        ctx.skip_current_browser('SSR marketplace browser flow skipped by --skip-browser')
        return

    with make_browser(ctx.browser_path, page_load_timeout=20) as browser:
        tab = browser.latest_tab

        home = tab.get(site_url('/scenarios/marketplace'))
        assert_nav_result(home, status=200, ok=True, label='marketplace home navigation')
        assert_true(tab('[data-testid="marketplace-root"]', timeout=10), 'marketplace home should expose root')
        assert_true(tab('[data-testid="marketplace-start-flow"]', timeout=10), 'marketplace home should expose flow entry')
        assert_true(tab.run_js('return document.querySelectorAll("[data-testid=marketplace-home-card]").length >= 12'),
                    'marketplace home should render a product feed')

        listing = tab.get(site_url('/scenarios/marketplace/search?query=耳机'))
        assert_nav_result(listing, status=200, ok=True, label='marketplace listing navigation')
        assert_true(tab('[data-testid="marketplace-search-root"]', timeout=10), 'marketplace listing should expose root')
        assert_true(tab.run_js('return document.querySelectorAll("[data-testid=marketplace-result-card]").length > 0'),
                    'marketplace listing should render result cards')

        tab.run_js(
            "document.querySelector('[data-testid=\"marketplace-query\"]').value = '';"
            "document.querySelector('[data-testid=\"marketplace-category\"]').value = 'digital';"
            "document.querySelector('[data-testid=\"marketplace-sort\"]').value = 'sales-desc';"
        )
        tab.listen.start('/api/marketplace/search.json')
        try:
            tab('[data-testid="marketplace-apply-filter"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/marketplace/search.json' in packet.url,
                        'listener should capture marketplace filter request')
            assert_equal(packet.response.status, 200, 'marketplace filter endpoint should return 200')
            assert_equal(packet.response.body['category'], 'digital', 'marketplace filter should send selected category')
            assert_equal(packet.response.body['sort'], 'sales-desc', 'marketplace filter should send selected sort')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="marketplace-search-output"]', 'loaded=24')

        tab.listen.start('/api/marketplace/search.json')
        try:
            tab('[data-testid="marketplace-load-more"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and 'offset=24' in packet.url,
                        'listener should capture marketplace load-more offset')
            assert_equal(packet.response.status, 200, 'marketplace load-more endpoint should return 200')
            assert_true(packet.response.body['count'] > 0, 'marketplace load-more should append remaining digital items')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="marketplace-search-output"]', 'next=')
        assert_true(tab.run_js('return document.querySelectorAll("[data-testid=marketplace-result-card][data-category=digital]").length >= 24'),
                    'marketplace listing should contain digital result cards after filtering')

        detail = tab.get(site_url('/scenarios/marketplace/item/2'))
        assert_nav_result(detail, status=200, ok=True, label='marketplace item navigation')
        assert_equal(tab('[data-testid="marketplace-item-root"]', timeout=10).attr('data-id'), '2',
                     'marketplace item page should expose selected item id')
        tab.run_js(
            "document.querySelector('[data-testid=\"sku-color\"]').value = '曜石黑';"
            "document.querySelector('[data-testid=\"sku-spec\"]').value = '升级款';"
            "document.querySelector('[data-testid=\"sku-quantity\"]').value = '2';"
        )
        tab.listen.start('/api/marketplace/cart.json')
        try:
            tab('[data-testid="add-marketplace-cart"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/marketplace/cart.json' in packet.url,
                        'listener should capture marketplace cart POST')
            assert_equal(packet.response.status, 200, 'marketplace cart endpoint should return 200')
            assert_equal(packet.response.body['cartCount'], 2, 'marketplace cart should receive selected quantity')
            assert_equal(packet.response.body['line']['id'], 2, 'marketplace cart should receive selected item id')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="marketplace-item-output"]', 'cart=2')
        assert_in('marketplace_cart_count=2', tab.run_js('return document.cookie'),
                  'marketplace cart cookie should be visible to browser flow')

        cart = tab.get(site_url('/scenarios/marketplace/cart'))
        assert_nav_result(cart, status=200, ok=True, label='marketplace cart navigation')
        assert_equal(tab('[data-testid="marketplace-cart-root"]', timeout=10).attr('data-id'), '2',
                     'marketplace cart should restore item id from cookie')
        assert_equal(tab('[data-testid="marketplace-cart-quantity"]', timeout=10).value, '2',
                     'marketplace cart should restore quantity from cookie')
        tab('[data-testid="marketplace-cart-qty-plus"]', timeout=10).click(by_js=True)
        wait_text_contains(tab, '[data-testid="marketplace-cart-output"]', 'quantity=3')
        checkout_href = tab('[data-testid="marketplace-cart-checkout"]', timeout=10).attr('href')
        assert_in('/scenarios/marketplace/checkout?item=2&qty=3', checkout_href,
                  'marketplace cart checkout link should include selected item and quantity')

        checkout = tab.get(site_url(checkout_href))
        assert_nav_result(checkout, status=200, ok=True, label='marketplace checkout navigation')
        assert_equal(tab('[data-testid="marketplace-checkout-root"]', timeout=10).attr('data-quantity'), '3',
                     'marketplace checkout should receive quantity from cart link')
        tab.run_js(
            "document.querySelectorAll('[data-testid=\"marketplace-address-radio\"]')[1].checked = true;"
            "document.querySelector('[data-testid=\"marketplace-payment-select\"]').value = 'mock-card';"
            "document.querySelector('[data-testid=\"marketplace-invoice-select\"]').value = 'company';"
            "document.querySelector('[data-testid=\"marketplace-buyer-note\"]').value = '自动化测试备注';"
        )
        tab.listen.start('/api/marketplace/checkout.json')
        try:
            tab('[data-testid="marketplace-submit-order"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/marketplace/checkout.json' in packet.url,
                        'listener should capture marketplace checkout POST')
            assert_equal(packet.response.status, 200, 'marketplace checkout endpoint should return 200')
            assert_equal(packet.response.body['status'], 'created', 'marketplace checkout should create an order')
            assert_equal(packet.response.body['itemCount'], 3, 'marketplace checkout should submit selected quantity')
            assert_equal(packet.response.body['payment'], 'mock-card', 'marketplace checkout should submit selected payment')
            order_id = packet.response.body['orderId']
            next_url = packet.response.body['nextUrl']
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="marketplace-checkout-output"]', 'status=created')
        assert_in(order_id, tab('[data-testid="marketplace-order-result-link"]', timeout=10).attr('href'),
                  'marketplace checkout result link should include created order id')

        result = tab.get(site_url(next_url))
        assert_nav_result(result, status=200, ok=True, label='marketplace order result navigation')
        assert_equal(tab('[data-testid="marketplace-order-result"]', timeout=10).attr('data-order'), order_id,
                     'marketplace result page should expose created order id')
        assert_equal(tab('[data-testid="marketplace-result-status"]', timeout=10).text, 'created',
                     'marketplace result page should expose created status')
        assert_equal(tab.run_js('return document.querySelectorAll("[data-testid=marketplace-timeline-step]").length'), 4,
                     'marketplace result page should render deterministic fulfillment timeline')
