"""Optional SSR social notes mobile-flow checks."""
from __future__ import annotations

import os
import time
from urllib.parse import urljoin

from DrissionPage import SessionPage

from support import assert_equal, assert_in, assert_nav_result, assert_true, make_browser


FEATURE_ID = 'ssr_social_notes_mobile'
FEATURES = ('ssr_social_notes_mobile',)
BROWSER_PHASE = True
PRIVATE_FIXTURE_URL_ENV = 'DP_PRIVATE_FIXTURE_URL'
MOBILE_UA = (
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 '
    'Mobile/15E148 Safari/604.1'
)


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


def apply_mobile_profile(tab) -> None:
    """Use a deterministic mobile profile before opening the SSR H5 page."""
    tab.set.user_agent(MOBILE_UA, platform='iPhone')
    tab.run_cdp('Emulation.setDeviceMetricsOverride',
                width=390, height=844, deviceScaleFactor=3, mobile=True)
    tab.run_cdp('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=5)
    tab.run_cdp('Page.addScriptToEvaluateOnNewDocument', source="""
        Object.defineProperty(Navigator.prototype, 'maxTouchPoints', {
          get: () => 5,
          configurable: true
        });
    """)


def run(ctx):
    if not ctx.include_online:
        ctx.skip('SSR social notes mobile flow requires --include-online')
        return
    base = site_url()
    if not base:
        ctx.skip(f'SSR social notes mobile flow requires {PRIVATE_FIXTURE_URL_ENV}')
        return

    session_page = SessionPage()
    feed = session_page.get(site_url('/api/social-notes/feed.json?channel=food&count=5&delay=1'), timeout=20)
    assert_nav_result(feed, status=200, ok=True, label='social notes feed endpoint')
    feed_json = feed.Response.json()
    assert_true(feed_json['ok'] is True, 'social feed endpoint should report ok=true')
    assert_equal(feed_json['channel'], 'food', 'social feed endpoint should echo channel')
    assert_equal(feed_json['count'], 5, 'social feed endpoint should return requested count')
    assert_equal(len(feed_json['items']), 5, 'social feed items should match count')

    comments = session_page.get(site_url('/api/social-notes/comments.json?noteId=note-002'), timeout=20)
    assert_nav_result(comments, status=200, ok=True, label='social comments endpoint')
    assert_equal(len(comments.Response.json()['comments']), 4, 'social comments endpoint should return deterministic comments')

    if ctx.skip_browser:
        ctx.skip_current_browser('SSR social notes browser flow skipped by --skip-browser')
        return

    with make_browser(ctx.browser_path, page_load_timeout=20) as browser:
        try:
            browser.set.window.size(390, 844)
        except Exception:
            pass
        tab = browser.latest_tab
        apply_mobile_profile(tab)

        home = tab.get(site_url('/scenarios/social-notes'))
        assert_nav_result(home, status=200, ok=True, label='social notes mobile navigation')
        mobile_metrics = tab.run_js(
            'return {ua: navigator.userAgent, width: innerWidth, height: innerHeight, '
            'dpr: devicePixelRatio, touch: navigator.maxTouchPoints};'
        )
        assert_in('Mobile', mobile_metrics['ua'], 'social mobile check should use mobile UA')
        assert_true(320 <= mobile_metrics['width'] <= 430,
                    'social mobile viewport should stay in phone-width range',
                    metrics=mobile_metrics)
        assert_true(mobile_metrics['touch'] >= 1,
                    'social mobile profile should expose touch points',
                    metrics=mobile_metrics)
        assert_true(tab('[data-testid="social-mobile-root"]', timeout=10), 'social mobile page should expose root')
        assert_true(tab('[data-testid="social-mobile-app-bar"]', timeout=10), 'social mobile page should expose top app bar')
        assert_true(tab('[data-testid="social-bottom-open-app"]', timeout=10), 'social mobile page should expose bottom app bar')
        assert_true(tab.run_js('return document.querySelectorAll("[data-testid=social-note-card]").length >= 12'),
                    'social mobile page should render waterfall cards')
        tab('[data-testid="social-open-app-top"]', timeout=10).click(by_js=True)
        wait_text_contains(tab, '[data-testid="social-app-open-output"]', 'source=top')

        tab.listen.start('/api/social-notes/feed.json')
        try:
            tab.run_js(
                'document.querySelector("[data-testid=social-search-input]").value = "早餐";'
                'document.querySelector("[data-testid=social-search-form]").dispatchEvent('
                'new Event("submit", { bubbles: true, cancelable: true }));'
            )
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/social-notes/feed.json' in packet.url,
                        'listener should capture social search feed request')
            assert_equal(packet.response.status, 200, 'social search endpoint should return 200')
            assert_equal(packet.response.body['query'], '早餐', 'social search should submit typed query')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="social-feed-output"]', 'query=早餐')
        tab.run_js('document.querySelector("[data-testid=social-search-input]").value = "";')

        tab.listen.start('/api/social-notes/feed.json')
        try:
            tab.run_js(
                "Array.from(document.querySelectorAll('[data-testid=\"social-channel-tab\"]'))"
                ".find((item) => item.dataset.channel === 'food').click();"
            )
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/social-notes/feed.json' in packet.url,
                        'listener should capture social channel feed request')
            assert_equal(packet.response.status, 200, 'social channel feed endpoint should return 200')
            assert_equal(packet.response.body['channel'], 'food', 'social channel request should use selected channel')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="social-feed-output"]', 'channel=food')

        tab.listen.start('/api/social-notes/feed.json')
        try:
            tab('[data-testid="social-load-more"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and 'offset=18' in packet.url,
                        'listener should capture social load-more offset')
            assert_equal(packet.response.status, 200, 'social load-more endpoint should return 200')
            assert_true(packet.response.body['count'] > 0, 'social load-more should append remaining cards')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="social-feed-output"]', 'next=')

        tab.run_js('document.querySelector("[data-testid=social-note-card]").click();')
        wait_text_contains(tab, '[data-testid="social-action-output"]', 'action=open')
        wait_text_contains(tab, '[data-testid="social-comment-output"]', 'comments=4')
        active_note = tab.run_js('return document.querySelector("[data-testid=social-action-output]").textContent.match(/note=([^;]+)/)[1];')
        assert_true(active_note.startswith('note-'), 'social detail sheet should expose active note id')

        tab.listen.start('/api/social-notes/actions.json')
        try:
            tab('[data-testid="social-like-note"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/social-notes/actions.json' in packet.url,
                        'listener should capture social like action')
            assert_equal(packet.response.status, 200, 'social action endpoint should return 200')
            assert_equal(packet.response.body['action'], 'like', 'social action should submit like')
            assert_equal(packet.response.body['enabled'], True, 'social action should enable like')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="social-action-output"]', 'liked=true')

        for selector, expected_action, expected_state in (
            ('[data-testid="social-collect-note"]', 'collect', 'collected=true'),
            ('[data-testid="social-follow-author"]', 'follow', 'followed=true'),
            ('[data-testid="social-share-note"]', 'share', 'shared=true'),
        ):
            tab.listen.start('/api/social-notes/actions.json')
            try:
                tab(selector, timeout=10).click(by_js=True)
                packet = tab.listen.wait(timeout=10)
                assert_true(packet and '/api/social-notes/actions.json' in packet.url,
                            f'listener should capture social {expected_action} action')
                assert_equal(packet.response.status, 200,
                             f'social {expected_action} endpoint should return 200')
                assert_equal(packet.response.body['action'], expected_action,
                             f'social action should submit {expected_action}')
            finally:
                tab.listen.stop()
            wait_text_contains(tab, '[data-testid="social-action-output"]', expected_state)

        tab.run_js('document.querySelector("[data-testid=social-comment-input]").value = "移动端评论测试";')
        tab.listen.start('/api/social-notes/comments.json')
        try:
            tab('[data-testid="social-comment-submit"]', timeout=10).click(by_js=True)
            packet = tab.listen.wait(timeout=10)
            assert_true(packet and '/api/social-notes/comments.json' in packet.url,
                        'listener should capture social comment POST')
            assert_equal(packet.response.status, 200, 'social comment endpoint should return 200')
            assert_equal(packet.response.body['comment']['text'], '移动端评论测试',
                         'social comment endpoint should receive typed comment')
        finally:
            tab.listen.stop()
        wait_text_contains(tab, '[data-testid="social-comment-output"]', 'status=posted')

        detail = tab.get(site_url('/scenarios/social-notes/note/note-002'))
        assert_nav_result(detail, status=200, ok=True, label='social note detail navigation')
        assert_equal(tab('[data-testid="social-note-detail-root"]', timeout=10).attr('data-note-id'), 'note-002',
                     'social note detail should expose requested note id')
        assert_equal(tab.run_js('return document.querySelectorAll("[data-testid=social-detail-comment]").length'), 4,
                     'social note detail should render deterministic comments')

        security = tab.get(site_url('/scenarios/social-notes/security-check?original=/explore/note-404'))
        assert_nav_result(security, status=200, ok=True, label='social security landing navigation')
        assert_equal(tab('[data-testid="social-security-root"]', timeout=10).attr('data-original-url'), '/explore/note-404',
                     'social security landing should preserve original URL')
        assert_in('无法查看', tab('[data-testid="social-security-title"]', timeout=10).text,
                  'social security landing should expose unavailable state')
