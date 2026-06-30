# 测试覆盖矩阵

本文档说明 `tests/` 提供的自动化覆盖范围。`stable` 分组作为 CI 门禁；诊断用例和 fixture 专项检查单独跟踪，避免环境相关场景影响发布验证结果。

## 稳定覆盖

| 范围 | 用例 | 验证内容 |
| --- | --- | --- |
| 导航与加载行为 | `feature_navigation_basics`, `feature_navigation_result`, `navigation_result`, `session_timeout` | 使用本地页面覆盖成功访问、重定向、HTTP 错误、超时、本地文件和加载模式。 |
| 基础监听能力 | `feature_listener_basics` | 使用本地 fetch 请求验证 `listen.start()`、`wait()`、`stop()`、响应状态/正文和监听重启。 |
| 下载能力 | `feature_download_management`, `download_browser`, `feature_browser_download` | 浏览器下载和浏览器主动下载 API 写入确定性文件，并校验文件内容。 |
| 页面对象 API | `feature_page_object_basics`, `feature_options_settings`, `feature_api_behavior_changes` | 使用本地页面检查动作链、状态、等待、阻止 URL、初始化脚本、选项和设置。 |
| 元素与定位器 | `feature_element_core_behaviors`, `feature_element_locators`, `locator_behavior`, `feature_find_api`, `feature_element_multi_click` | 验证 XPath/CSS/text/AX 定位、相对定位、元素状态、输入/选择/勾选、快照和多击行为。 |
| Frame 与 Shadow DOM | `feature_cross_origin_iframe_elements`, `feature_frame_shadow_setters` | 覆盖同源和跨 host frame 访问、frame setter、链接解析和 open shadow-root 查询。 |
| 浏览器上下文与 cookie | `feature_browser_contexts`, `context_isolation`, `feature_cookie_setters`, `feature_console_and_cookie_formats` | 在 Chromium 中验证上下文隔离、cookie、console 事件和 cookie 输出格式。 |
| 浏览器与标签页冒烟 | `feature_chromium_options_environment`, `console_and_tabs`, `feature_permissions` | 覆盖浏览器启动选项、权限、隐藏标签页、激活和 console payload。 |

## 诊断覆盖

`known` 分组保留已确认或仍在评估的问题复现用例。这些用例默认只生成报告，除非显式添加 `--fail-on-failures`。

| 范围 | 用例 |
| --- | --- |
| 公开 API 契约核查 | `api_surface` |
| WebSocket/SSE 监听数据包 | `listener_ws_sse`, `feature_listener_upgrade` |
| iframe 内触发的监听数据包 | `feature_cross_origin_iframe_listener`, `iframe_non_screenshot` |
| 监听重启回归 | `feature_regression_basics` |
| 标签页管理回归 | `feature_tab_management`, `feature_chromium_tab_management` |
| Chromium tab POST 返回值 | `feature_tab_post_response` |
| 初始导航期间出现 alert | `alert_on_open` |

当前复现命令和分诊说明见 `tests/KNOWN_ISSUES.md`。

## 专项验证

部分能力需要专用环境或视觉断言，不纳入 `stable` 门禁：

| 范围 | 验证方式 |
| --- | --- |
| iframe/OOPIF 截图 | 使用专门截图套件，结合像素断言、默认 Chromium 模式和强制 OOPIF 模式。 |
| 媒体录制与编码支持 | 使用平台相关的浏览器媒体能力验证。 |
| 真实代理认证 | 使用外部代理基础设施或受控集成环境。 |
| 底层指针事件时序 | 使用有头浏览器或视觉交互专项验证。 |
| SSR fixture 冒烟 | CI checkout 并启动独立 `DrissionPage-test-site`，计入 coverage；远端共享/私有 fixture 使用 `local` 分组和 `DP_TEST_SITE_URL`（兼容旧的 `DP_PRIVATE_FIXTURE_URL`）。 |
| SSR Marketplace 全流程 | `feature_ssr_marketplace_flow` 使用合成电商站点覆盖首页、搜索、详情、购物车、结算和订单结果。 |
| SSR 社区笔记移动端 | `feature_ssr_social_notes_mobile` 使用合成移动 H5 场景覆盖移动 UA/视口、瀑布流、搜索、详情弹层、点赞收藏、关注、评论和安全落地页。 |

SSR fixture 额外覆盖商品筛选/排序/购物车/结算弹窗、Marketplace 浏览到下单完整链路、社区笔记移动端互动、活动大列表、突发请求、Cloudflare-like 托管挑战、`cf_clearance`、WAF 403 和 429 限流响应。

## 质量策略

- 优先使用本地确定性 fixture，避免依赖第三方网站。
- 浏览器行为必须在 Chromium 中真实执行，不能只验证 API 形状。
- `stable` 门禁用例应保持确定、可复现、可定位。
- 已知缺陷应保持可复现，但默认不影响公开 CI。
- 修改公开 API 时，应同步增加运行时检查和类型 stub 检查。
