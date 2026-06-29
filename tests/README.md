# DrissionPage 测试套件

`tests/` 提供 DrissionPage 的自动化验证套件。测试对象包括当前源码，以及按需安装到独立虚拟环境中的最新预发布包。

默认测试使用本地 HTTP、WebSocket、SSE 和本地 SSR fixture。外部网络或私有 fixture 检查均为显式启用项，不作为 pull request 的必要条件。

## 测试分组

| 分组 | 用途 | CI 行为 |
| --- | --- | --- |
| `stable` | 稳定、确定、预期通过的兼容性和回归检查。 | 必须通过。 |
| `known` | 已确认或仍在评估的问题复现用例。 | 默认只生成报告。 |
| `local` | 私有 fixture 或真实网络冒烟检查。 | 显式启用。 |
| `all` | 全量诊断运行。 | 仅供手动使用。 |

## 快速开始

在仓库根目录运行：

```bash
./tests/run.sh current --suite stable --skip-browser --no-browser-only --fail-on-failures
./tests/run.sh current --suite stable --browser-only --fail-on-failures
```

对比最新预发布包：

```bash
./tests/run.sh pre --suite stable --fail-on-failures
./tests/run.sh both --suite stable --fail-on-failures
```

列出可用用例：

```bash
python tests/run.py --source current --list-cases --suite stable
python tests/run.py --source current --list-cases --suite known
python tests/run.py --source current --list-cases --suite local
python tests/run.py --source current --list-cases --suite all
```

运行单个用例：

```bash
./tests/run.sh current --case listener_ws_sse --fail-on-failures
```

运行已知问题复现用例，但不让命令失败：

```bash
./tests/run.sh current --suite known --skip-browser --no-browser-only
./tests/run.sh current --suite known --browser-only
```

## 报告
本地报告默认写入 `tests/reports/`，也可以通过参数指定报告路径。CI 报告会作为 workflow artifact 上传，并被 git 忽略。

## SSR fixture

`tests/ssr-site/` 是用于浏览器冒烟检查的 Astro SSR fixture，覆盖复杂业务流、动态页面和 Cloudflare-like 拦截页模拟。fixture URL 通过 `DP_PRIVATE_FIXTURE_URL` 提供；测试报告会脱敏该 URL 和 host。

主要业务场景：

- `/scenarios/marketplace`：合成电商全流程，覆盖浏览、搜索筛选、商品详情、SKU、购物车、结算和订单结果。
- `/cases/business-dashboard`：大列表、筛选、批量选择、加载更多和突发请求。
- `/cases/cloudflare-gate`：托管挑战、clearance cookie、403 和 429 响应模拟。

```bash 
cd tests/ssr-site
npm ci
npm run build
npm run dev -- --host 127.0.0.1 --port 4321
```

在仓库根目录运行：

```bash
DP_PRIVATE_FIXTURE_URL="http://127.0.0.1:4321" \
  ./tests/run.sh current --include-online --case ssr_site_smoke --fail-on-failures
```

运行 Marketplace 完整业务流：

```bash
DP_PRIVATE_FIXTURE_URL="http://127.0.0.1:4321" \
  ./tests/run.sh current --include-online --case ssr_marketplace_flow --fail-on-failures
```
