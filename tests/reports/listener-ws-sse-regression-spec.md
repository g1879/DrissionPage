# Listener WS/SSE 专属数据包问题复核报告

本文记录 `listener_ws_sse` 测试复现到的 Listener 问题，面向修复 PR 和作者沟通。复核目标是确认问题是否违反 4.2 文档契约，并给出可验证的验收标准。

复核环境：

- DrissionPage：历史复核为 `4.2.0b19`；自动化 CI 以当前 PyPI 预发布包和当前源码实时结果为准
- 测试目标：PyPI 预发布包 `pre` 与当前源码 `current`
- 浏览器：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- 测试服务：tests 内置本地 HTTP / WebSocket / SSE 服务，不依赖外网

复核命令：

```bash
./tests/run.sh pre --case listener_ws_sse \
  --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
./tests/run.sh current --case listener_ws_sse \
  --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

## 相关文档契约

4.2 功能页说明 Listener 新增 `listen.set_method()` 与 `listen.set_res_type()`，并新增专属数据包：

- `WebSocketPacket`：监听到 ws 请求产生的专属数据包，包含 `is_sent`、`connect_info`、`payload`、`timestamp`。
- `SSEPacket`：监听到 sse 请求产生的专属数据包，包含 `timestamp`、`name`、`id`、`data`、`connect_info`。

因此，当用户在连接创建前设置：

```python
tab.listen.set_res_type.WebSocket(only=True)
tab.listen.set_res_type.EventSource(only=True)
```

`listen.wait()` 应能获得对应的专属数据包，而不是超时或只获得连接阶段的普通 `DataPacket`。

## 总体结论

本轮复核确认两个明确问题、一个语义待确认点、一个回归保护点：

1. `WebSocket(only=True)` 捕获不到 `WebSocketPacket`：**明确问题**。
2. `EventSource(only=True)` 捕获不到 `SSEPacket`：**明确问题**。
3. `EventSource(only=True)` 下先返回握手 `DataPacket`：**语义待确认/建议修复**。
4. WS/SSE 模式后恢复普通 HTTP `DataPacket`：**当前通过，不是已复现问题，应作为回归保护**。

## 问题 1：`WebSocket(only=True)` 未返回 `WebSocketPacket`

### 复现场景

在页面创建 WebSocket 连接前启动 Listener，并只监听 `WebSocket` 资源类型：

```python
tab.listen.set_res_type.WebSocket(only=True)
tab.listen.start('/ws')
tab.get(base + '/page/listener?mode=ws')
packet = wait_for_packet(tab, lambda p: p.type == 'WebSocketPacket')
```

### 预期行为

- 能捕获到 `WebSocketPacket`。
- `packet.resourceType == 'WebSocket'`。
- `packet.connect_info` 不为空，因为监听早于连接建立。
- `packet.payload` 或等价数据字段可读取 WebSocket frame 内容。

### 实际行为

`pre` 与 `current` 结果一致：

```text
No WebSocketPacket before timeout; seen=[]; internal _res_type={'WebSocket'}
```

这说明公开 API 设置已经进入内部状态，但专属 WebSocket 事件没有被正确捕获或入队。

### 影响

用户按 4.2 文档使用 `set_res_type.WebSocket(only=True)` 时，无法获得文档承诺的 `WebSocketPacket`，WS 监听能力不可用。

## 问题 2：`EventSource(only=True)` 未返回 `SSEPacket`

### 复现场景

在页面创建 `EventSource` 连接前启动 Listener，并只监听 `EventSource` 资源类型：

```python
tab.listen.set_res_type.EventSource(only=True)
tab.listen.start('/events')
tab.get(base + '/page/listener?mode=sse')
packet = wait_for_packet(tab, lambda p: p.type == 'SSEPacket')
```

### 预期行为

- 能捕获到 `SSEPacket`。
- `packet.resourceType == 'EventSource'`。
- `packet.name`、`packet.id`、`packet.data` 与服务端发送的 SSE 消息一致。
- `packet.connect_info` 在监听早于连接建立时可用。

### 实际行为

`pre` 与 `current` 结果一致：

```text
No SSEPacket before timeout; seen=['DataPacket']; internal _res_type={'EventSource'}
```

精确复核脚本还观察到首个包为：

```text
DataPacket(resourceType='EventSource', url='/events')
```

但没有出现 `SSEPacket`。

### 影响

用户按 4.2 文档监听 SSE 时，无法获得 `SSEPacket.name/id/data`，只能看到连接阶段的普通 `DataPacket`。这与“监听到的 sse 请求产生的专属数据包”描述不一致。

## 语义待确认：SSE 握手 `DataPacket` 是否应默认进入业务队列

### 背景

SSE 与 WebSocket 建连都会经过 HTTP 层，因此底层能捕获连接/握手请求是合理的。问题在于：当用户显式设置 `EventSource(only=True)` 时，`listen.wait()` 的主要语义应是返回 SSE 消息包，而不是先返回连接握手包。

### 建议语义

- 握手/连接阶段的 HTTP 信息保留为 `connect_info`。
- `EventSource(only=True)` 默认返回 `SSEPacket`。
- 握手 `DataPacket` 不默认混入专属消息队列，除非未来提供显式调试开关。

### 验收行为

```python
tab.listen.set_res_type.EventSource(only=True)
tab.listen.start('/events')
tab.get(base + '/page/listener?mode=sse')
packet = tab.listen.wait(timeout=ctx.timeout)
assert packet.type == 'SSEPacket'
assert packet.connect_info is not None
```

该点不是文档逐字规定，但它是 `SSEPacket` 作为“专属数据包”时更一致的公开 API 语义。

## 回归保护：专属模式后普通 HTTP 监听仍应可用

本项本轮复核通过，不作为本轮缺陷项。保留它是为了防止修复 WS/SSE 时破坏普通 HTTP 监听。

### 覆盖场景

```python
tab.listen.set_res_type.all()
tab.listen.set_method.all()
tab.listen.start('/json')
tab.get(base + '/page/listener?mode=fetch')
packet = wait_for_packet(tab, lambda p: p.type == 'DataPacket')
```

### 当前结果

- `set_res_type.all()` 后可以正常捕获 `Fetch` 类型的 `DataPacket`。
- `packet.response.status == 200`。
- URL 为 `/json?from=listener`。

### 回归要求

修复 WS/SSE 后，该场景必须继续通过，确保专属回调、过滤器状态、`stop()` / `start()` 清理逻辑不会污染普通 HTTP 监听。

## 可能原因判断

从复现结果看，内部状态保存的是文档形式的资源类型：

```text
_res_type={'WebSocket'}
_res_type={'EventSource'}
```

但专属回调判断疑似使用了全大写形式，例如 `WEBSOCKET` / `EVENTSOURCE`。这会导致：

- 用户设置已生效；
- 但 WebSocket / SSE 专属事件没有按资源类型命中；
- SSE 连接阶段仍可能通过普通 HTTP 路径产生 `DataPacket`。

## 修复验收标准

- `set_res_type.WebSocket(only=True)` 能稳定返回 `WebSocketPacket`。
- `set_res_type.EventSource(only=True)` 能稳定返回 `SSEPacket`。
- 连接创建前开始监听时，专属包的 `connect_info` 可用。
- SSE 的 `name/id/data` 与服务端发送消息一致。
- WS 的 `payload` / `is_sent` 等字段可读取。
- SSE / WS 连接握手信息不应破坏专属包队列语义。
- `set_res_type.all()`、`remove_WebSocket()`、`remove_EventSource()`、`stop()` / `start()` 后普通 HTTP `DataPacket` 行为保持兼容。
