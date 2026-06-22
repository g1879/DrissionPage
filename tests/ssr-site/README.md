# DrissionPage SSR Fixture

[![DrissionPage tests verification](https://github.com/jumodada/DrissionPage/actions/workflows/drissionpage-tests.yml/badge.svg)](https://github.com/jumodada/DrissionPage/actions/workflows/drissionpage-tests.yml)

`tests/ssr-site/` is an Astro SSR fixture for DrissionPage release verification. It provides stable pages and API endpoints for browser, listener, locator, navigation, iframe, form, wait, screenshot, upload, download, SSE, and SSR behavior checks.

## Fixture contract

- Stable selectors: important nodes use `data-testid`.
- Deterministic behavior: default checks do not depend on third-party websites.
- SSR coverage: pages and API endpoints run with Astro `output: 'server'`.
- Network coverage: JSON, POST echo, status codes, redirects, slow responses, downloads, and SSE.
- Machine-readable inventory: `/api/manifest.json` lists fixture pages, endpoints, expected status codes, and coverage areas.

## Local validation

```bash
cd tests/ssr-site
npm ci
npm run build
npm run preview
```

## Fixture routes

| Path | Purpose |
| --- | --- |
| `/` | Home page, SSR timestamp, fixture index, verification contract. |
| `/cases/locators` | XPath, CSS, text, ARIA, Shadow DOM, and SVG locator targets. |
| `/cases/navigation` | 200/404/500, redirects, and slow response entries. |
| `/cases/network` | Fetch, POST, SSE, and optional WebSocket trigger page. |
| `/cases/forms` | Input, select, checkbox, submit, and multi-click behaviors. |
| `/cases/frames` | Iframe page and frame-internal fetch behavior. |
| `/cases/waits` | Delayed show/hide, text mutation, attribute mutation, and HTML stability. |
| `/cases/visual` | Fixed color bands, green-dot anchors, and long screenshot targets. |
| `/cases/upload-download` | Upload metadata and deterministic download headers/body. |
| `/cases/dynamic?name=drission` | Query parameters, cookies, and SSR timestamp rendering. |
| `/api/health.json` | Health-check JSON endpoint. |
| `/api/manifest.json` | Machine-readable fixture manifest. |
| `/api/echo.json` | GET/POST/PUT/PATCH/DELETE echo endpoint. |
| `/api/status/[code]` | Explicit HTTP status-code endpoint. |
| `/api/redirect?to=/` | Controlled redirect endpoint. |
| `/api/slow.json?delay=750` | Controlled slow-response endpoint. |
| `/api/events` | `text/event-stream` SSE endpoint. |
| `/api/download.txt?name=dp-fixture.txt` | Download endpoint with `Content-Disposition`. |

## Remote smoke check

The remote smoke check is optional. It is skipped unless `--include-online` is passed and `DP_PRIVATE_FIXTURE_URL` is set.

```bash
DP_PRIVATE_FIXTURE_URL="$PRIVATE_FIXTURE_URL" \
  ./tests/run.sh current --include-online --case ssr_site_smoke --fail-on-failures
```

GitHub Actions can run the same check from scheduled or manual workflows by reading `DP_PRIVATE_FIXTURE_URL` from repository secrets. Test reports redact the configured URL and host before writing JSON/Markdown artifacts.

## Reports

Runner reports contain pass/fail/skip and feature coverage summaries:

```text
tests/reports/current-latest.json
tests/reports/current-latest.md
tests/reports/pre-latest.json
tests/reports/pre-latest.md
```

Useful report fields:

```json
summary.passed / summary.failed / summary.skipped / summary.cases_total
summary.feature_coverage_percent
summary.feature_pass_percent
```

## Optional WebSocket fixture

`/cases/network` can trigger an optional WebSocket echo endpoint when `PUBLIC_OPTIONAL_WS_URL` is configured. If unset, the page records a skip message and fetch/SSE coverage remains valid.

## Extension priorities

- `/cases/storage`: cookie, localStorage, sessionStorage, and context isolation fixtures.
- `/cases/shadow-nested`: nested shadow roots and slot distribution fixtures.
- `/cases/iframe-nested`: nested iframe fixtures covering same-origin and cross-host structures.
