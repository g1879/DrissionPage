# DrissionPage Tests

`tests/` 是 DrissionPage 发布验证与回归复现测试套件，用于在同一套测试中对比：

- 当前仓库源码；
- PyPI 当前预发布包（安装在独立虚拟环境中）。

测试内容覆盖公开 API 契约、浏览器集成、网络监听、定位器、导航与 Session 行为、下载、标签页、BrowserContext，以及仍属于当前版本契约的功能页行为。默认用例均使用本地 HTTP、WebSocket 与 SSE 服务；在线冒烟测试必须显式启用。

## 快速开始

在仓库根目录运行：

```bash
./tests/run.sh current --skip-browser
./tests/run.sh pre --skip-browser
./tests/run.sh both
```

`pre` 目标默认使用 `/tmp/dp-tests-pre-venv`。首次运行会安装 PyPI 预发布包；后续默认复用已有虚拟环境。需要更新预发布包时使用：

```bash
./tests/run.sh pre --upgrade-pre
```

列出测试用例：

```bash
python tests/run.py --source current --list-cases
python tests/run.py --source current --list-cases --no-browser-only
python tests/run.py --source current --list-cases --browser-only
```

运行单项测试：

```bash
./tests/run.sh current --case listener_ws_sse
./tests/run.sh pre --case sse_packet
```

默认本地模式为报告模式：测试失败时输出 `[FAIL]` 并写入报告，但退出码保持 `0`。CI 或质量门禁场景应追加 `--fail-on-failures`，使任一失败用例返回非零退出码。

## GitHub Actions 自动化

工作流文件：`.github/workflows/drissionpage-tests.yml`。

触发条件：

- `workflow_dispatch` 手动触发；
- 每日 `03:17 UTC` 定时触发；
- 影响 `DrissionPage/`、`tests/`、工作流文件或 `requirements.txt` 的 push / pull request。

CI 执行入口：

```bash
./tests/ci.sh
```

CI 批次：

1. 当前源码无浏览器测试；
2. PyPI 预发布包无浏览器测试；
3. 当前源码浏览器测试；
4. PyPI 预发布包浏览器测试。

GitHub Actions 安装 Chrome，并设置 `DP_TESTS_REQUIRE_BROWSER=1`。如果浏览器不可用，工作流失败，不降级为仅无浏览器验证。


## SSR 测试站点

`tests/ssr-site/` 是独立的 Astro SSR 项目，用于部署到 Vercel 后作为 DrissionPage 的真实页面测试目标。它提供稳定的 `data-testid`、SSR 时间戳、状态码、重定向、慢响应、POST echo、SSE、表单、iframe、wait、visual、上传下载、Shadow DOM 和 SVG 场景。

本地验证：

```bash
cd tests/ssr-site
npm ci
npm run build
```

Vercel 部署时将项目 Root Directory 设置为 `tests/ssr-site`。该项目使用 Astro Vercel adapter 与 `output: 'server'`，适合验证服务端渲染、API endpoint 与爬取行为。部署后可设置 `DP_SSR_SITE_URL` 并运行可选远端冒烟：

```bash
export DP_SSR_SITE_URL="https://<your-project>.vercel.app"
./tests/run.sh current --include-online --case ssr_site_smoke --fail-on-failures
```

默认 CI 仍使用本地确定性服务；远端 SSR 站点检查必须显式 `--include-online` 才会运行。

## 覆盖率

当前 CLI runner 不依赖 pytest。源码覆盖率使用 `coverage.py`，目标限定为 `DrissionPage/`，配置文件为仓库根目录 `.coveragerc`。CI 只统计当前源码批次；PyPI 预发布包批次用于跨版本行为对比，不计入本仓库覆盖率。

CI 输出：

```text
tests-artifacts/reports/coverage/coverage.txt
tests-artifacts/reports/coverage/coverage.xml
tests-artifacts/reports/coverage/coverage.json
tests-artifacts/reports/coverage/html/
```

如果后续将测试用例改造成 pytest 函数和 fixture，可在现有 `.coveragerc` 基础上接入 `pytest-cov`。当前阶段选择 `coverage.py`，因为它能直接覆盖自定义 CLI runner。

## 环境变量

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `PYTHON_BIN` | `python` | 执行 tests 的 Python 解释器。 |
| `DP_BROWSER_PATH` | 空 | 浏览器可执行文件路径；为空或不可执行时跳过浏览器测试。 |
| `DP_TESTS_REQUIRE_BROWSER` | `0` | 设为 `1` 时，浏览器缺失会导致 CI 失败。 |
| `DP_TESTS_TIMEOUT` | `8` | 单项测试内部超时时间。 |
| `DP_TESTS_REPORT_DIR` | `tests/reports/ci` | CI 报告输出目录。 |
| `DP_TESTS_ARTIFACT_DIR` | `/tmp/dp-tests-artifacts-ci` | 下载文件等运行时产物目录。 |
| `DP_TESTS_PRE_VENV` | `/tmp/dp-tests-pre-venv` | PyPI 预发布包隔离虚拟环境路径。 |
| `DP_TESTS_COVERAGE` | `1` | 是否为当前源码批次生成 coverage.py 报告。 |
| `DP_TESTS_COVERAGE_RCFILE` | `.coveragerc` | coverage.py 配置文件路径。 |
| `DP_TESTS_COVERAGE_BIN` | `python -m coverage` | coverage.py 执行命令。 |
| `DP_SSR_SITE_URL` | 空 | 可选远端 Astro SSR 测试站点 URL；配合 `--include-online --case ssr_site_smoke` 使用。 |

## 报告与产物

本地启动脚本默认生成：

```text
tests/reports/pre-latest.json
tests/reports/pre-latest.md
tests/reports/current-latest.json
tests/reports/current-latest.md
```

这些运行报告由 `.gitignore` 排除。长期维护文档保留在：

- `tests/reports/regression-repros.md`
- `tests/reports/listener-ws-sse-regression-spec.md`

## 目录结构

- `run.sh`：本地启动入口，支持预发布包、当前源码或双目标测试。
- `ci.sh`：CI 入口，编译 tests，列出测试用例，分批运行测试并生成覆盖率报告。
- `run.py`：选择测试目标、隔离导入路径并转发运行参数。
- `runner.py`：批量运行器，负责加载测试用例、执行测试并生成报告。
- `feature_manifest.py`：公开行为与测试用例之间的覆盖关系元数据。
- `COVERAGE.md`：发布验证覆盖矩阵和默认批次排除说明。
- `support.py`：本地服务、浏览器启动、断言和辅助工具。
- `feature_cases/test_*.py`：面向功能行为的测试用例。
- `regression_cases/test_*.py`：面向回归和问题复现的测试用例。
- `.coveragerc`：源码行覆盖率统计配置。

## 范围限制

默认批次不覆盖 iframe 元素截图 / OOPIF 截图、录屏编码、真实代理链路、平台敏感指针事件。此类能力应由独立专项测试验证。
