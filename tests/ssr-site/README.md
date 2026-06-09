# DrissionPage SSR Fixture

`tests/ssr-site/` 是用于 DrissionPage 冒烟检查的 Astro SSR fixture。它提供确定性的页面和 API 端点，用于定位器、导航、监听、iframe、表单、等待、视觉、上传、下载、SSE、大 DOM、复杂业务流和 Cloudflare-like 拦截页场景。

## 契约

- 稳定选择器使用 `data-testid`。
- 默认检查不依赖第三方网站。
- 页面和 API 端点使用 Astro `output: 'server'` 运行。
- `/api/manifest.json` 暴露 fixture 清单，便于自动化检查。
- 报告会脱敏 `DP_PRIVATE_FIXTURE_URL` 及其 host。

## 本地验证

```bash
cd tests/ssr-site
npm ci
npm run build
npm run dev -- --host 127.0.0.1 --port 4321
```

## 路由

| 路径 | 用途 |
| --- | --- |
| `/` | 首页、SSR 时间戳和 fixture 索引。 |
| `/cases/locators` | XPath、CSS、文本、ARIA、Shadow DOM 和 SVG 目标。 |
| `/cases/navigation` | 状态码、重定向和慢响应。 |
| `/cases/network` | Fetch、POST、SSE 和可选 WebSocket 触发页面。 |
| `/cases/forms` | 输入框、下拉框、复选框、提交和多击行为。 |
| `/cases/frames` | iframe 页面和 frame 内部 fetch 行为。 |
| `/cases/waits` | 延迟显示、文本变化、属性变化和 HTML 稳定性。 |
| `/cases/visual` | 色带、绿色锚点和长截图目标。 |
| `/cases/upload-download` | 上传元数据和确定性下载响应。 |
| `/cases/business-dashboard` | 大列表、筛选、批量选择、加载更多和突发请求。 |
| `/cases/commerce` | 商品列表、筛选排序、懒加载、推荐、购物车和结算弹窗。 |
| `/cases/cloudflare-gate` | 模拟托管挑战、`cf_clearance`、WAF 403 和 429 限流响应。 |
| `/cases/dynamic?name=drission` | 查询参数、cookie 和 SSR 渲染。 |
| `/api/health.json` | 健康检查 JSON 端点。 |
| `/api/manifest.json` | 机器可读 fixture 清单。 |
| `/api/echo.json` | 方法和 payload 回显端点。 |
| `/api/status/[code]` | 显式 HTTP 状态码端点。 |
| `/api/redirect?to=/` | 可控重定向端点。 |
| `/api/slow.json?delay=750` | 可控慢响应端点。 |
| `/api/events` | `text/event-stream` SSE 端点。 |
| `/api/download.txt?name=dp-fixture.txt` | 带 `Content-Disposition` 的下载端点。 |
| `/api/activity-batch.json?offset=0&count=3` | 确定性批量活动 JSON。 |
| `/api/commerce/products.json?offset=0&count=3` | 确定性商品列表 JSON。 |
| `/api/commerce/cart.json` | 购物车 POST 回显。 |
| `/api/commerce/checkout.json` | 结算 POST 回显。 |
| `/api/cf/protected.json` | 需要 `cf_clearance` 的受保护 JSON；支持 403/429 模式。 |
| `/cdn-cgi/challenge-platform/fixture-clearance` | 设置合成 `cf_clearance` cookie。 |

## 远端冒烟检查

```bash
DP_PRIVATE_FIXTURE_URL="$PRIVATE_FIXTURE_URL" \
  ./tests/run.sh current --include-online --case ssr_site_smoke --fail-on-failures
```

只有同时提供 `--include-online` 和 `DP_PRIVATE_FIXTURE_URL` 时，该命令才会执行检查。

## 可选 WebSocket 端点

配置 `PUBLIC_OPTIONAL_WS_URL` 后，`/cases/network` 可以触发可选 WebSocket 回显端点。未配置时，页面会记录跳过状态，fetch 和 SSE 检查仍然有效。
