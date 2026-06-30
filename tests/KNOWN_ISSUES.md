# 已知问题复现用例

`known` 分组保留已确认或仍在评估的问题复现检查。CI 中默认只生成报告；只有显式添加 `--fail-on-failures` 时才作为失败门禁。

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

| 用例 | 范围 | 当前现象 |
| --- | --- | --- |
| `api_surface` | 公开 API 契约 | `ChromiumTab.drag_in()` 缺失；`Element.click(wait_stop)` 默认值与断言契约不一致。 |
| `listener_ws_sse` | WebSocket/SSE 数据包 | WebSocket-only 模式未产生 `WebSocketPacket`；`SSEPacket` 缺少 `connect_info`。 |
| `feature_listener_upgrade` | 监听状态恢复 | HTTP 数据包恢复场景可能返回 `False`，而不是 `DataPacket`。 |
| `feature_regression_basics` | 监听重启 | 重启监听后等待 fetch 数据包时可能返回 `False`。 |
| `feature_cross_origin_iframe_listener` | iframe 监听覆盖 | tab 级 listener 未捕获跨 host iframe 内触发的 fetch。 |
| `feature_tab_management` | 标签页查询 | `browser.get_tab(0)` 可能把 dict 传到需要 tab id 的路径。 |
| `feature_chromium_tab_management` | Chromium 标签页查询 | 与 `feature_tab_management` 相同的 tab id 形状问题。 |
| `feature_tab_post_response` | `ChromiumTab.post()` 返回值 | 返回对象不符合断言中的 `requests.Response` 类契约。 |
| `alert_on_open` | 导航与弹窗 | 初始加载阶段触发 `alert()` 的页面可能导致导航挂起。 |
| `iframe_non_screenshot` | iframe 访问与等待 | 当前源码本地可通过；保留用于预发布包和环境差异对比。 |

## 移入稳定分组的条件

只有同时满足以下条件，才应将用例从 `known` 移入 `stable`：

1. 底层行为或测试契约已经明确并修复；
2. 本地添加 `--fail-on-failures` 后通过；
3. 当前源码和预发布包差异已被有意处理；
4. 在 headless CI 中表现稳定、可复现。
