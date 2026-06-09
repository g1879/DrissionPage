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

CI 执行本地确定性测试、浏览器测试、coverage 统计，并上传测试报告 artifact。定时任务和手动任务可通过仓库 Secret `DP_PRIVATE_FIXTURE_URL` 运行可选 SSR fixture 冒烟；pull request 不运行该远端检查。

## SSR fixture 测试站点

`tests/ssr-site/` 是独立 Astro SSR fixture，提供稳定的 `data-testid`、SSR 时间戳、状态码、重定向、慢响应、POST echo、SSE、表单、iframe、wait、visual、上传下载、Shadow DOM 和 SVG 场景。

本地验证：

```bash
cd tests/ssr-site
npm ci
npm run build
```

可选远端冒烟：

```bash
DP_PRIVATE_FIXTURE_URL="$PRIVATE_FIXTURE_URL" \
  ./tests/run.sh current --include-online --case ssr_site_smoke --fail-on-failures
```

该用例默认跳过，必须同时设置 `--include-online` 和 `DP_PRIVATE_FIXTURE_URL`。测试报告会对该环境变量中的 URL 和 host 做脱敏处理。

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
| `DP_PRIVATE_FIXTURE_URL` | 空 | 可选 SSR fixture URL；配合 `--include-online --case ssr_site_smoke` 使用。 |
