# DrissionPage 预发布回归问题复核记录

记录环境：`/tmp/dp-tests-pre-venv`，历史复核安装包为 `DrissionPage 4.2.0b19`，Chrome：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`。CI 每次运行会安装当前 PyPI 预发布包，实时结果以生成的 JSON/Markdown 报告为准。

本轮明确排除：iframe 截图 / OOPIF 截图。

## 1. `listen.set_res_type.WebSocket/EventSource(only=True)` 无法捕获专属包

专项回归测试设计见：

```text
tests/reports/listener-ws-sse-regression-spec.md
```

命令：

```bash
python tests/run.py \
  --source pre --venv /tmp/dp-tests-pre-venv --no-install \
  --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --case listener_ws_sse
```

实际：

- `set_res_type.WebSocket(only=True)` 超时，未捕获 `WebSocketPacket`；内部 `_res_type={'WebSocket'}`。
- `set_res_type.EventSource(only=True)` 只看到 `DataPacket`，未捕获 `SSEPacket`；内部 `_res_type={'EventSource'}`。

预期：按 4.2 文档，`WebSocket(only=True)` / `EventSource(only=True)` 应捕获 `WebSocketPacket` / `SSEPacket`。

## 2. SessionPage 的 NavResult 在 404/500 下状态为空且 bool() 报错

命令：

```bash
python tests/run.py \
  --source pre --venv /tmp/dp-tests-pre-venv --no-install \
  --skip-browser --case navigation_result --case session_timeout
```

实际：

- `SessionPage.get(/missing)` 返回 `<NavResult url: None, status: None>`。
- `SessionPage.get(/error)` 返回 `<NavResult url: None, status: None>`。
- `bool(result)` 报 `TypeError: __bool__ should return bool, returned NoneType`。
- 慢响应 timeout 应返回可安全取 bool 的结果；`status is None` 时保留 `ok is None` 属于合理的未知状态语义，不再作为问题。

预期：4.2 文档说明 `get()` 返回连接状态信息；已收到 HTTP 响应的 404/500 应保留 `status`，`ok` 应为 `False`；无 HTTP 状态的 timeout 可保留 `status=None`、`ok=None`，但 `bool(NavResult)` 不应抛类型错误。

## 3. XPath 定位被文本内容碰撞污染

命令：

```bash
python tests/run.py \
  --source pre --venv /tmp/dp-tests-pre-venv --no-install \
  --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --case locator_behavior
```

实际：页面中 `<p id="text">//div[@id="target"]</p>` 与真实 `<div id="target">` 同时存在时：

- `tab.ele('//div[@id="target"]')` 返回 `<p id='text'>`。
- `tab.ele('x://div[@id="target"]')` 也返回 `<p id='text'>`。

预期：显式 `x:` XPath 必须优先按 XPath 执行；无前缀自动模式遇到 `//...` 也应识别为 XPath，而不是文本命中。

## 4. 打开即 alert 的页面仍会卡住

命令：

```bash
python tests/run.py \
  --source pre --venv /tmp/dp-tests-pre-venv --no-install \
  --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --case alert_on_open
```

实际：子进程打开 `data:text/html,<script>alert('check-alert')</script>` 超过测试超时未返回；直接执行时可观察到 `Network.disable` 等待 CDP 响应超时。

预期：4.2 修复项写明“打开就弹出 alert 的页面卡住”已修复，应能返回或可处理 alert，不应卡死导航。

## 5. 文档/API 表面不一致：`ChromiumTab.drag_in()` 缺失

命令：

```bash
python tests/run.py \
  --source pre --venv /tmp/dp-tests-pre-venv --no-install \
  --skip-browser --case api_surface
```

实际：`ChromiumTab` 没有 `drag_in`；当前实现只在 `tab.actions.drag_in(..., offset_x=..., offset_y=...)` 上存在偏移参数。

预期：4.2 页面写的是 `ChromiumTab` 对象的 `drag_in()` 增加 `offset_x` / `offset_y`。如果设计实际是 `tab.actions.drag_in()`，文档或公开 API 需要统一。

## 6. `ChromiumTab.post()` 在当前预发布包未返回 Response 对象

命令：

```bash
./tests/run.sh pre \
  --case feature_tab_post_response
```

实际：历史复核的 PyPI 预发布包中，真实本地 POST 请求后，返回对象不是 `requests.Response` 形态，缺少 `status_code`。当前源码 `4.2.0b10` 同一测试用例通过。

预期：4.1 功能页说明 MixTab 和 MixPage 的 `post()` 方法必返回 Response 对象；当前发布验证中，Chromium tab 的 `post()` 应返回可读取 `status_code` 和响应体的 Response 对象。
