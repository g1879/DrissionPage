# 发布验证覆盖矩阵

本矩阵说明 `tests/` 默认批次覆盖的公开行为。覆盖项必须对应可执行测试用例；仅验证函数存在或签名参数，不单独计为完整覆盖。默认批次面向当前仓库源码和当前 PyPI 预发布包，不把历史迁移说明当作当前版本必须保留的 API。

## 核心功能覆盖

来源：<https://www.drissionpage.cn/features/4/>

| 官方范围 | 默认用例 | 覆盖方式 | 状态 |
| --- | --- | --- | --- |
| 新的抓包功能：页面对象内置 `listen`、`start()`、`wait()`、`stop()`、`wait_silent(targets_only=True)` | `feature_listener_basics` | 真实 Chromium 页面触发本地 `fetch()`，先启动监听，再等待目标包，断言 request/response/status/body；随后 `stop()`/`start()` 再次监听 | 已覆盖 |
| 新的页面访问逻辑：`load_mode.none`、`get(timeout)`、`SessionPage.get()` 本地文件 | `feature_navigation_basics` | 本地慢资源页面验证 none 模式不阻塞可用 DOM；慢主文档验证 `timeout` 限时；临时 HTML 文件验证 SessionPage 读取和 DOM 查询 | 已覆盖 |
| 新的下载管理：`set.download_path()`、`set.download_file_name()`、`wait.download_begin()`、任务等待 | `feature_download_management` | 真实浏览器点击本地下载链接，等待 `DownloadMission`，断言重命名文件和文件内容 | 已覆盖 |
| 页面对象：内置动作链、`states`、`wait.doc_loaded()`、`wait.eles_loaded()`、`wait.title_change()`、`wait.url_change()` | `feature_page_object_basics` | 真实页面聚焦输入框并用 `actions.input()` 输入；触发标题和 URL 变化后等待目标状态 | 已覆盖 |
| 页面对象：`ChromiumFrame.rect/states`、frame DOM 查询 | `feature_page_object_basics` | 真实 iframe 获取 frame 对象，断言 frame 存活、几何尺寸和内部元素查询 | 已覆盖；不包含截图 |
| 页面对象：`add_init_js()` / `remove_init_js()`、`set.blocked_urls()` | `feature_page_object_basics` | 新页面验证初始化脚本注入；本地 fetch 被 URL 阻断后页面状态变为 blocked | 已覆盖 |
| cookies 设置：单个 cookie、`clear()`、`remove()` | `feature_cookie_setters` | SessionPage 与真实 Chromium tab 分别写入、删除、清空 cookie，并读取实际 cookie 容器 | 已覆盖 |
| 标签页管理：`new_tab(background)`、`get_tab(index/id)`、Tab 可独立操作和关闭 | `feature_tab_management` | 创建后台标签页，直接查询 DOM，按序号/id 取回，关闭后等待 tab id 消失 | 已覆盖 |
| 标签页行为：Tab 自己处理弹窗、`states.has_alert` | `feature_tab_management` | 真实按钮触发 alert，等待 `states.has_alert`，用 `handle_alert()` 关闭并断言状态恢复 | 已覆盖 |
| 元素相关：`@!` 否定定位、相对定位简化、`parent(locator,index)` | `feature_element_core_behaviors` | 离线 SessionElement 和真实 Chromium 页面均验证否定定位与相邻/父级查询结果 | 已覆盖 |
| 元素相关：`rect`、`states.has_rect`、`states.is_whole_in_viewport`、`wait.has_rect()`、元素相等比较 | `feature_element_core_behaviors` | 真实长页面元素滚动到中央，断言几何、视口状态和同节点句柄相等 | 已覆盖 |
| 元素相关：`input(by_js)`、`check()`、`select.by_option()`、`NoneElement_value()` | `feature_element_core_behaviors` | 真实 input/checkbox/select/missing element 行为断言；`check()` 以行为为准兼容当前源码与预发布参数差异 | 已覆盖 |
| 启动配置：`ChromiumOptions`、`SessionOptions`、`Settings` 当前配置契约 | `feature_options_settings` | options 对象链式调用和状态读取；SessionOptions 路径/重试；Settings 开关设置后恢复 | 已覆盖 |

## 浏览器交互功能覆盖

来源：<https://www.drissionpage.cn/features/4.1/>

| 官方范围 | 默认用例 | 覆盖方式 | 状态 |
| --- | --- | --- | --- |
| Chromium 对象：连接浏览器、标签页操作、浏览器操作 | `feature_chromium_tab_management` | 真实启动 Chromium、本地页面、`latest_tab`、`new_tab(background=True)`、`get_tab(id/num)`、`activate()`、`close()`、`close(others=True)` | 已覆盖 |
| `find()` 多定位符匹配 | `feature_find_api` | 离线 SessionElement + 真实 Chromium 页面分别验证 `find(any_one)`、`find(first_ele=False)`、`parent(locator,index)` | 已覆盖 |
| 浏览器页面/元素 `s_ele()`、`s_eles()` timeout 参数 | `feature_find_api` | 真实 Chromium 页面生成 session 快照并查询 DOM | 已覆盖 |
| `console` 属性读取控制台信息 | `feature_console_and_cookie_formats` | 真实页面启动 console listener，执行 `console.log()` 并等待目标事件 | 已覆盖 |
| `cookies()` 的 `as_dict()`、`as_json()`、`as_str()` | `feature_console_and_cookie_formats` | 真实浏览器 cookie 写入后读取 `CookiesList` 三种格式 | 已覆盖 |
| Frame/元素 `set.property()`、`set.style()`、`link`、`get_frame()` | `feature_frame_shadow_setters` | 真实 iframe、真实 DOM property/style 修改、真实 link/src 解析 | 已覆盖 |
| `shadow_root` 等待并查询 shadow DOM | `feature_frame_shadow_setters` | 真实 open shadow-root 内元素查询 | 已覆盖 |
| `scroll()` 方法和 wait title/url 行为 | `feature_scroll_and_waits` | 真实滚动、JS 触发目标 title/url 文本后等待 | 已覆盖 |
| 元素多次点击 | `feature_element_multi_click` | 同一按钮先验证 JS 单击和真实单击基线，再验证 `click.multi(times=2)` 可产生浏览器多击语义：`click` 的 `event.detail=2` 与一次 `dblclick` | 已覆盖；不再强制要求两次 click handler，避免把 CDP clickCount 双击语义误判为缺陷 |
| `post()` 返回 Response 对象 | `feature_tab_post_response` | 真实本地 POST，断言返回对象和请求体 | 已覆盖；当前源码通过，当前预发布复现问题 |
| `ChromiumOptions.new_env()`、`is_headless`、`auto_port(scope)` | `feature_chromium_options_environment` | 真实 options 对象状态和临时 scope 路径断言 | 已覆盖 |

## 默认批次不覆盖的项

| 官方范围 | 原因 |
| --- | --- |
| iframe 元素截图 / OOPIF 截图 | 用户明确排除本轮默认覆盖；截图正确性需要独立图像断言和 OOPIF 专项环境。 |
| 录像 H.265 编码 | 依赖系统媒体编码和浏览器录屏能力，应由媒体专项测试验证。 |
| 真实代理认证链路 | 默认批次不依赖外部代理服务；当前只覆盖代理配置解析和上下文参数。 |
| 动作链真实鼠标 `Actions.click(times)` 指针事件 | headless 指针事件容易受窗口焦点、坐标和平台影响；默认批次以元素点击行为作为稳定发布门槛，动作链指针事件应使用专项可视/有头环境验证。 |
| 历史迁移/已移除 API | 发布验证面向当前源码和当前预发布包；历史页面中已被后续版本替代或删除的 API 不作为“当前必须存在”断言。 |

## 防止假阴的规则

- 默认使用本地 HTTP 服务，不依赖外部网站。
- 浏览器功能必须真实启动 Chromium 并操作 DOM、网络、下载任务或浏览器状态。
- 一个功能点对应一个测试文件；单点失败不应拖垮其它覆盖项。
- 对历史文档中的旧 API，先判断当前版本是否仍是公开契约，再决定纳入、迁移或排除。
- 对同一能力的跨版本参数差异，优先验证当前真实行为；只有明确属于当前公开契约的签名才作为失败条件。
- 对容易受平台影响的能力（截图、录屏、真实代理、指针事件），默认批次不拿不稳定断言凑覆盖率。
