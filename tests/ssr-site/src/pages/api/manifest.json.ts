import type { APIRoute } from 'astro';
import { json } from '../../lib/http';

const cases = [
  { id: 'home', path: '/', selectors: ['[data-testid="home-summary"]', '[data-testid="server-time"]'] },
  { id: 'locators', path: '/cases/locators', selectors: ['[data-testid="xpath-target"]', '[data-testid="aria-save-button"]', '[data-testid="shadow-host"]'] },
  { id: 'navigation', path: '/cases/navigation', selectors: ['[data-testid="status-200"]', '[data-testid="status-404"]', '[data-testid="slow-json"]'] },
  { id: 'network', path: '/cases/network', selectors: ['[data-testid="fetch-json"]', '[data-testid="post-echo"]', '[data-testid="start-sse"]'] },
  { id: 'forms', path: '/cases/forms', selectors: ['[data-testid="profile-form"]', '[data-testid="multi-click"]', '[data-testid="form-output"]'] },
  { id: 'frames', path: '/cases/frames', selectors: ['[data-testid="primary-frame"]'] },
  { id: 'waits', path: '/cases/waits', selectors: ['[data-testid="start-waits"]', '[data-testid="delayed-visible"]', '[data-testid="html-stable-list"]'] },
  { id: 'visual', path: '/cases/visual', selectors: ['[data-testid="visual-target"]', '[data-testid="band-red"]', '[data-testid="dot-top-left"]'] },
  { id: 'upload-download', path: '/cases/upload-download', selectors: ['[data-testid="file-input"]', '[data-testid="download-link"]', '[data-testid="upload-output"]'] },
  { id: 'dynamic', path: '/cases/dynamic?name=drission', selectors: ['[data-testid="dynamic-page"]', '[data-testid="query-name"]'] },
  { id: 'business-dashboard', path: '/cases/business-dashboard', selectors: ['[data-testid="business-root"]', '[data-testid="activity-row"]', '[data-testid="burst-fetch"]'] },
  { id: 'commerce', path: '/cases/commerce', selectors: ['[data-testid="commerce-root"]', '[data-testid="product-card"]', '[data-testid="cart-drawer"]'] },
  { id: 'cloudflare-gate', path: '/cases/cloudflare-gate', selectors: ['[data-testid="cf-challenge"]', '[data-testid="issue-clearance"]', '[data-testid="cf-block-preview"]'] },
  { id: 'marketplace-flow', path: '/scenarios/marketplace', selectors: ['[data-testid="marketplace-root"]', '[data-testid="marketplace-start-flow"]', '[data-testid="marketplace-home-card"]'] },
  { id: 'marketplace-search', path: '/scenarios/marketplace/search?query=耳机', selectors: ['[data-testid="marketplace-search-root"]', '[data-testid="marketplace-result-card"]', '[data-testid="marketplace-load-more"]'] },
  { id: 'marketplace-item-detail', path: '/scenarios/marketplace/item/2', selectors: ['[data-testid="marketplace-item-root"]', '[data-testid="sku-color"]', '[data-testid="add-marketplace-cart"]'] },
  { id: 'marketplace-cart', path: '/scenarios/marketplace/cart', selectors: ['[data-testid="marketplace-cart-root"]', '[data-testid="marketplace-cart-line"]', '[data-testid="marketplace-cart-checkout"]'] },
  { id: 'marketplace-checkout', path: '/scenarios/marketplace/checkout', selectors: ['[data-testid="marketplace-checkout-root"]', '[data-testid="marketplace-address-card"]', '[data-testid="marketplace-submit-order"]'] },
  { id: 'marketplace-order-result', path: '/scenarios/marketplace/order-result?order=TBMOCK-000001', selectors: ['[data-testid="marketplace-order-result"]', '[data-testid="marketplace-result-order-id"]', '[data-testid="marketplace-fulfillment-timeline"]'] },
  { id: 'social-notes-mobile', path: '/scenarios/social-notes', selectors: ['[data-testid="social-mobile-root"]', '[data-testid="social-channel-tabs"]', '[data-testid="social-note-card"]'] },
  { id: 'social-note-detail', path: '/scenarios/social-notes/note/note-002', selectors: ['[data-testid="social-note-detail-root"]', '[data-testid="social-detail-title"]', '[data-testid="social-detail-action-bar"]'] },
  { id: 'social-security-landing', path: '/scenarios/social-notes/security-check?original=/explore/note-404', selectors: ['[data-testid="social-security-root"]', '[data-testid="social-security-original"]', '[data-testid="social-security-actions"]'] },
];

const endpoints = [
  { id: 'health', path: '/api/health.json', method: 'GET', expectedStatus: 200 },
  { id: 'echo-get', path: '/api/echo.json?from=manifest', method: 'GET', expectedStatus: 200 },
  { id: 'status-404', path: '/api/status/404', method: 'GET', expectedStatus: 404 },
  { id: 'redirect', path: '/api/redirect?to=/', method: 'GET', expectedStatus: 302 },
  { id: 'slow', path: '/api/slow.json?delay=100', method: 'GET', expectedStatus: 200 },
  { id: 'sse', path: '/api/events?count=1&interval=10', method: 'GET', expectedStatus: 200 },
  { id: 'download', path: '/api/download.txt?name=dp-fixture.txt', method: 'GET', expectedStatus: 200 },
  { id: 'activity-batch', path: '/api/activity-batch.json?offset=0&count=3', method: 'GET', expectedStatus: 200 },
  { id: 'commerce-products', path: '/api/commerce/products.json?offset=0&count=3', method: 'GET', expectedStatus: 200 },
  { id: 'marketplace-search', path: '/api/marketplace/search.json?query=耳机&count=3', method: 'GET', expectedStatus: 200 },
  { id: 'marketplace-cart', path: '/api/marketplace/cart.json', method: 'POST', expectedStatus: 200 },
  { id: 'marketplace-checkout', path: '/api/marketplace/checkout.json', method: 'POST', expectedStatus: 200 },
  { id: 'social-notes-feed', path: '/api/social-notes/feed.json?channel=food&count=3', method: 'GET', expectedStatus: 200 },
  { id: 'social-notes-actions', path: '/api/social-notes/actions.json', method: 'POST', expectedStatus: 200 },
  { id: 'social-notes-comments', path: '/api/social-notes/comments.json?noteId=note-002', method: 'GET', expectedStatus: 200 },
  { id: 'cf-protected-blocked', path: '/api/cf/protected.json', method: 'GET', expectedStatus: 403 },
  { id: 'cf-clearance', path: '/cdn-cgi/challenge-platform/fixture-clearance', method: 'GET', expectedStatus: 200 },
];

export const GET: APIRoute = () => json({
  ok: true,
  service: 'drissionpage-ssr-test-site',
  version: '0.1.0',
  generatedAt: new Date().toISOString(),
  cases,
  endpoints,
  coverage: {
    areas: ['SSR', 'locators', 'navigation', 'status-codes', 'redirects', 'slow-response', 'fetch', 'POST', 'SSE', 'forms', 'iframes', 'waits', 'visual-screenshot', 'upload', 'download', 'shadow-dom', 'svg', 'business-dashboard', 'large-dom', 'batch-network', 'commerce-facets', 'cart-checkout', 'modal-flow', 'marketplace-home', 'marketplace-search', 'marketplace-item-detail', 'marketplace-cart', 'marketplace-checkout', 'marketplace-order-result', 'social-notes-mobile', 'social-notes-waterfall', 'social-note-detail', 'social-actions', 'social-comments', 'social-security-landing', 'cloudflare-challenge', 'waf-block', 'rate-limit'],
    websocket: 'optional private WebSocket endpoint',
  },
});
