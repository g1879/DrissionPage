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
];

const endpoints = [
  { id: 'health', path: '/api/health.json', method: 'GET', expectedStatus: 200 },
  { id: 'echo-get', path: '/api/echo.json?from=manifest', method: 'GET', expectedStatus: 200 },
  { id: 'status-404', path: '/api/status/404', method: 'GET', expectedStatus: 404 },
  { id: 'redirect', path: '/api/redirect?to=/', method: 'GET', expectedStatus: 302 },
  { id: 'slow', path: '/api/slow.json?delay=100', method: 'GET', expectedStatus: 200 },
  { id: 'sse', path: '/api/events?count=1&interval=10', method: 'GET', expectedStatus: 200 },
  { id: 'download', path: '/api/download.txt?name=dp-fixture.txt', method: 'GET', expectedStatus: 200 },
];

export const GET: APIRoute = () => json({
  ok: true,
  service: 'drissionpage-ssr-test-site',
  version: '0.1.0',
  generatedAt: new Date().toISOString(),
  cases,
  endpoints,
  coverage: {
    areas: ['SSR', 'locators', 'navigation', 'status-codes', 'redirects', 'slow-response', 'fetch', 'POST', 'SSE', 'forms', 'iframes', 'waits', 'visual-screenshot', 'upload', 'download', 'shadow-dom', 'svg'],
    websocket: 'optional private WebSocket endpoint',
  },
});
