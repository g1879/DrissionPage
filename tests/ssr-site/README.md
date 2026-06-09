# DrissionPage SSR Test Site

[![DrissionPage tests verification](https://github.com/jumodada/DrissionPage/actions/workflows/drissionpage-tests.yml/badge.svg)](https://github.com/jumodada/DrissionPage/actions/workflows/drissionpage-tests.yml)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

`tests/ssr-site/` 是专供 DrissionPage 自动化验证使用的 Astro SSR 测试站点。项目可作为 Vercel 独立项目部署，部署后由 DrissionPage 抓取页面、监听网络请求、验证状态码、表单、iframe、SSE 和 SSR 动态内容。

## 设计目标

- 页面结构稳定：关键节点均提供 `data-testid`。
- 行为可重复：默认不依赖外部网站。
- SSR 可验证：根配置使用 `output: 'server'` 与 Vercel adapter。
- 网络测试完整：提供 JSON、POST echo、状态码、重定向、慢响应、SSE endpoint。
- Vercel 友好：项目根目录设为 `tests/ssr-site` 即可部署。
- 闭环可机器读取：`/api/manifest.json` 暴露页面、接口、预期状态码和覆盖领域。

## Vercel 配置

| 配置项 | 推荐值 |
| --- | --- |
| Framework Preset | `Astro` |
| Root Directory | `tests/ssr-site` |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | 留空，使用 Vercel/Astro adapter 默认值 |
| Node.js Version | `22.x` |

本项目 `package.json` 声明 `node >=22.12.0`，Vercel 项目里请优先选择 Node 22。

## 本地运行

```bash
cd tests/ssr-site
npm ci
npm run dev
npm run build
```

## 主要测试入口

| 路径 | 用途 |
| --- | --- |
| `/` | 首页、SSR 时间戳、用例索引、验证说明。 |
| `/cases/locators` | XPath/CSS/文本/ARIA/Shadow DOM/SVG 定位。 |
| `/cases/navigation` | 200/404/500、跳转、慢响应入口。 |
| `/cases/network` | fetch、POST、SSE、可选 WebSocket 触发页。 |
| `/cases/forms` | 输入、select、checkbox、提交、多击。 |
| `/cases/frames` | iframe 页面与 frame 内 fetch。 |
| `/cases/waits` | 定时显示/隐藏、文本/属性变化、HTML 稳定性。 |
| `/cases/visual` | 固定色带、绿点锚点、长元素截图夹具。 |
| `/cases/upload-download` | 文件上传 metadata、下载响应头和文件名。 |
| `/cases/dynamic?name=drission` | 查询参数、cookie、SSR 时间戳。 |
| `/api/health.json` | 健康检查 JSON。 |
| `/api/manifest.json` | 机器可读测试清单。 |
| `/api/echo.json` | GET/POST/PUT/PATCH/DELETE echo。 |
| `/api/status/[code]` | 指定 HTTP 状态码。 |
| `/api/redirect?to=/` | 可控重定向。 |
| `/api/slow.json?delay=750` | 可控慢响应。 |
| `/api/events` | `text/event-stream` SSE。 |
| `/api/download.txt?name=dp-fixture.txt` | 带 `Content-Disposition` 的下载文件。 |

## DrissionPage 远端冒烟闭环

部署到 Vercel 后，把部署 URL 传给测试 runner：

```bash
export DP_SSR_SITE_URL="https://<your-project>.vercel.app"
./tests/run.sh current --include-online --case ssr_site_smoke --fail-on-failures
```

该用例默认不会运行，必须同时满足：

1. 传入 `--include-online`；
2. 设置 `DP_SSR_SITE_URL`；
3. 浏览器测试未被 `--skip-browser` 禁用。

验证范围：

- `SessionPage` 读取 `/api/health.json`、`/api/manifest.json`、`/api/status/404` 和 SSR 动态页面；
- `Chromium` 打开首页、定位页面、网络页面、iframe 页面、wait 页面、visual 页面和 upload/download 页面；
- 页面 listener 捕获 `/api/echo.json?from=fetch-json`；
- iframe 子页面元素可读取；
- wait fixture 的显示/隐藏/文本/属性变化可观察；
- visual fixture 的色带和绿点锚点存在；
- upload/download fixture 的 file input、下载链接和下载响应头存在。

测试通过率和覆盖率由 DrissionPage runner 生成：

```text
tests/reports/current-latest.json
tests/reports/current-latest.md
```

GitHub Actions 会把 CI 报告上传为 `drissionpage-tests-reports` artifact；README 顶部的 Actions badge 反映最近一次工作流状态。若需要在 README 中展示更细的通过率，可从 JSON 报告读取：

```json
summary.passed / summary.failed / summary.skipped / summary.cases_total
summary.feature_coverage_percent
summary.feature_pass_percent
```

## WebSocket 说明

Vercel Serverless Functions 不适合作为通用 WebSocket 服务端。`/cases/network` 支持读取 `PUBLIC_TEST_WS_URL`，在需要测试 WebSocket 监听时可配置独立 WS echo 服务；未配置时页面会明确记录跳过，不影响 fetch 与 SSE 测试。

## 已补充的专项夹具

- `/cases/waits`：定时显示/隐藏元素，用于 `wait.ele_displayed()`、`wait.ele_hidden()`、`wait.html_stable()`。
- `/cases/visual`：固定色块/绿点页面，供截图专项做像素断言。
- `/cases/upload-download`：小文件上传、下载响应头和文件名场景。

## 继续扩展建议

优先补充以下稳定用例：

- `/cases/storage`：cookie、localStorage、sessionStorage、跨 context 隔离验证。
- `/cases/shadow-nested`：嵌套 shadow root 和 slot 分发。
- `/cases/iframe-nested`：多层 iframe，区分同源和跨 host。
