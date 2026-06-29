# 测试自动化指南

本文档说明 DrissionPage 测试套件的本地运行、GitHub Actions、私有 fixture 配置和覆盖率上传方式。

## 测试入口

| 路径 | 用途 |
| --- | --- |
| `tests/run.sh` | 本地 shell 入口。 |
| `tests/run.py` | 选择当前源码或预发布包环境。 |
| `tests/runner.py` | 发现用例、过滤分组、执行检查并写入报告。 |
| `tests/support.py` | 本地 HTTP/WebSocket/SSE fixture 和共享断言。 |
| `tests/feature_cases/` | 功能级检查。 |
| `tests/regression_cases/` | 回归和诊断复现用例。 |
| `tests/ssr-site/` | 可选 Astro SSR fixture。 |

## 测试分组

| 分组 | 用途 |
| --- | --- |
| `stable` | 必须通过的 CI 门禁。 |
| `known` | 正在评估的问题复现报告。 |
| `local` | 私有 fixture 或真实网络冒烟检查。 |
| `all` | 手动诊断。 |

## 本地命令

稳定无浏览器门禁：

```bash
./tests/run.sh current --suite stable --skip-browser --no-browser-only --fail-on-failures
```

稳定浏览器门禁：

```bash
./tests/run.sh current --suite stable --browser-only --fail-on-failures
```

预发布包对比：

```bash
./tests/run.sh pre --suite stable --fail-on-failures
./tests/run.sh both --suite stable --fail-on-failures
```

已知问题复现：

```bash
./tests/run.sh current --suite known --skip-browser --no-browser-only
./tests/run.sh current --suite known --browser-only
```

单个用例：

```bash
./tests/run.sh current --case listener_ws_sse --fail-on-failures
```

如果 Chrome 无法自动发现，可使用 `DP_BROWSER_PATH` 或 `--browser-path` 指定路径。

## GitHub Actions

workflow 文件：

```text
.github/workflows/drissionpage-tests.yml
```

工作流步骤：

1. 检出仓库。
2. 安装 Python、Chrome 和 Node。
3. 在依赖较重的步骤前运行 `tests/check_workflow_quality.py`。
4. 安装 Python 依赖和 coverage 工具。
5. 构建 SSR fixture 包。
6. 启动本地 SSR fixture，并把 `DP_LOCAL_FIXTURE_URL` 传给 `tests/ci.sh`。
7. 运行 `tests/ci.sh`，其中本地 SSR 冒烟、Marketplace 全流程和社区笔记移动端流程会计入当前源码 coverage。
8. 配置 `CODECOV_TOKEN` 时上传覆盖率到 Codecov。
9. 在非 pull request 事件中，如果配置了 `DP_PRIVATE_FIXTURE_URL`，执行私有 SSR 冒烟、Marketplace 全流程和社区笔记移动端检查。
10. 上传测试报告和运行时产物。

`stable` 分组失败会导致工作流失败。`known` 分组失败只写入报告，不改变工作流结果。

私有 SSR 冒烟不会在 `pull_request` 事件中运行。每次 workflow 都会写入 `ssr-smoke-eligibility.txt`，用于确认事件类型、secret 是否可用以及本次是否满足运行条件；该文件只包含布尔状态，不包含 URL。

## 仓库密钥

在 GitHub Actions 设置中配置密钥：

| Secret | 用途 |
| --- | --- |
| `CODECOV_TOKEN` | 可选 Codecov 上传 token。 |
| `DP_PRIVATE_FIXTURE_URL` | 可选私有 SSR fixture 基础 URL。 |

不要提交私有 fixture URL。runner 会在生成报告时遮罩并脱敏 `DP_PRIVATE_FIXTURE_URL`。

## 私有 SSR fixture

fixture 包位于 `tests/ssr-site/`。

本地验证：

```bash
cd tests/ssr-site
npm ci
npm run build
npm run dev -- --host 127.0.0.1 --port 4321
```

在仓库根目录另开终端运行 SSR 冒烟：

```bash
DP_PRIVATE_FIXTURE_URL="http://127.0.0.1:4321" \
  ./tests/run.sh current \
    --include-online \
    --browser-path "$DP_BROWSER_PATH" \
    --case ssr_site_smoke \
    --fail-on-failures
```

远端冒烟命令：

```bash
DP_PRIVATE_FIXTURE_URL="$PRIVATE_FIXTURE_URL" \
  ./tests/run.sh current --include-online --case ssr_site_smoke --fail-on-failures
```

Marketplace 完整业务流：

```bash
DP_PRIVATE_FIXTURE_URL="http://127.0.0.1:4321" \
  ./tests/run.sh current \
    --include-online \
    --browser-path "$DP_BROWSER_PATH" \
    --case ssr_marketplace_flow \
    --fail-on-failures
```

社区笔记移动端流程：

```bash
DP_PRIVATE_FIXTURE_URL="http://127.0.0.1:4321" \
  ./tests/run.sh current \
    --include-online \
    --browser-path "$DP_BROWSER_PATH" \
    --case ssr_social_notes_mobile \
    --fail-on-failures
```

如需部署托管版本，使用 `tests/ssr-site` 作为项目根目录，并沿用 package 中定义的安装和构建命令。

## 覆盖率上传

`tests/ci.sh` 会把 coverage XML 写入：

```text
tests-artifacts/reports/coverage/coverage.xml
```

workflow 使用 `codecov/codecov-action@v7` 上传覆盖率。将 `CODECOV_TOKEN` 添加为仓库密钥后运行 workflow。通用 badge 格式：

```md
[![codecov](https://codecov.io/gh/<owner>/<repo>/branch/master/graph/badge.svg)](https://codecov.io/gh/<owner>/<repo>)
```

覆盖率百分比表示已执行当前源码批次的 Python 行覆盖率，与 runner 报告中的功能覆盖摘要不是同一个指标。

## Workflow 质量审核

`tests/check_workflow_quality.py` 是无第三方依赖的守卫脚本，用于检查 workflow 可读性和常见配置风险：

- 禁止使用已知依赖废弃运行时的旧版 action 主版本；
- 禁止使用 `main`、`master`、`HEAD` 等可变 action ref；
- 禁止在 workflow 表达式中使用无效的 `runner.temp`；
- 检查 workflow step 是否有可读名称。

本地运行：

```bash
python tests/check_workflow_quality.py
```

## 提交前检查

```bash
python tests/check_workflow_quality.py
python -m compileall -q tests/run.py tests/runner.py tests/support.py tests/feature_cases tests/regression_cases
cd tests/ssr-site && npm ci && npm run check
cd ../..
git -c core.whitespace=cr-at-eol diff --check
```
