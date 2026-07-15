# 已知问题复现用例

`known` 分组保留已确认或仍在评估的问题复现检查。CI 中默认只生成报告；只有显式添加 `--fail-on-failures` 时才作为失败门禁。

最近复核：2026-07-15，当前源码 `5.0.0b0`，macOS Google Chrome `149.0.7827.198`（headless），本地 HTTP/WebSocket/SSE fixture。失败用例已经从 `stable` 主门禁隔离，但仍由 `known` 套件持续执行并输出 traceback，不能删除或改成无条件跳过。

## 运行命令

列出用例：

```bash
python tests/run.py --source current --list-cases --suite known
```

以报告模式运行全部已知问题用例：

```bash
./tests/run.sh current --suite known --skip-browser --no-browser-only
./tests/run.sh current --suite known --browser-only
```

将单个用例作为失败门禁运行：

```bash
./tests/run.sh current --case listener_ws_sse --fail-on-failures
```

## 当前用例

### 当前源码确认失败

| 用例 | 范围 | 2026-07-15 实测现象 |
| --- | --- | --- |
| `feature_recommended_chromium_entry` | 根导出兼容 | `from DrissionPage import ChromiumPage` 失败。 |
| `feature_startup_settings` | 启动参数兼容 | `ChromiumOptions.set_browser_path(edge=True)` 不接受 `edge` 参数。 |
| `api_surface` | 公开 API 契约 | 同时复现上述两个兼容缺口、`ChromiumTab.drag_in()` 缺失和 `Element.click(wait_stop)` 默认值差异。 |
| `feature_element_locators` | AX 定位 | 真实 Chrome 报 `Accessibility has not been enabled`。 |
| `locator_behavior` | AX/定位回归矩阵 | 与 `feature_element_locators` 独立复现相同 AX domain 生命周期问题。 |
| `feature_element_core_behaviors` | 相对父元素定位 | `parent("#items")` 生成无效 XPath。 |
| `feature_find_api` | SessionElement 相对定位 | `parent(".card")` 生成无效 XPath。 |
| `feature_regression_basics` | 数字开头 id 与监听回归 | 当前最先失败于 `#123abc` 无法定位。 |
| `locator_explicit_syntax` | 显式定位符语义 | `//missing` 未命中后误走文本兜底，返回文本所在元素。 |
| `feature_listener_upgrade` | 监听 API | `Listener.set_targets` 缺失，测试在 API 形状检查阶段失败。 |
| `listener_ws_sse` | WebSocket/SSE 数据包 | `WebSocketPacket` 和 `SSEPacket` 缺少 `connect_info`。 |
| `feature_cross_origin_iframe_listener` | iframe 监听覆盖 | tab listener 未捕获跨 host iframe 内触发的 fetch。 |
| `feature_tab_post_response` | `ChromiumTab.post()` 返回值 | session mode 返回对象不符合 `requests.Response` 契约。 |
| `alert_on_open` | 导航与弹窗 | 子进程实测超过 8 秒仍未返回，由测试自身超时终止。 |
| `feature_ssr_site_smoke` | 独立 SSR 全场景 | 真实 Astro fixture 在 locators 页面复现 AX domain 未启用；CI 暂时 report-only，后续场景尚未执行到。 |

### 当前源码已通过但继续观察

以下用例在本次 current + Chrome 单次运行通过，但尚未完成 pre-release、Linux headless 和重复稳定性矩阵，因此暂不移回 `stable`：

| 用例 | 当前状态 | 保留原因 |
| --- | --- | --- |
| `feature_tab_management` | 通过 | 旧问题曾涉及 tab id 形状，等待 CI/预发布对比。 |
| `feature_chromium_tab_management` | 通过 | 与上项共享底层路径，等待 CI/预发布对比。 |
| `context_get_tabs_as_id` | 通过 | 当前源码已支持，预发布包和 Linux CI 尚未复核。 |
| `iframe_non_screenshot` | 通过 | 保留用于 Chromium/OOPIF 环境差异对比。 |

## 移入稳定分组的条件

只有同时满足以下条件，才应将用例从 `known` 移入 `stable`：

1. 底层行为或测试契约已经明确并修复；
2. 本地添加 `--fail-on-failures` 后通过；
3. 当前源码和预发布包差异已被有意处理；
4. 在 Linux headless CI 和至少一次本地重复运行中稳定通过；
5. 从 `KNOWN_ISSUE_CASES` 删除后，`stable` 的纯 Python 与浏览器门禁均通过。

`feature_ssr_site_smoke` 仍归类为 `local`，因为它需要独立 fixture；恢复时还需把 `tests/ci.sh` 和远端 fixture workflow 中对应 report-only 步骤重新并入失败门禁。
