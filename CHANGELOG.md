# 更新日志

DrissionPage 版本变更、兼容性影响和迁移提示。

## 快速导航

- [中文更新日志](#中文更新日志)
- [English Changelog](#english-changelog)
- [历史功能说明](#历史功能说明)

---

<a id="中文更新日志"></a>

# 中文更新日志

## [5.0.0b0] - 2026-07-06

### 发布说明

5.0.0b0 是测试版兼容性断点版本。由于测试版期间新增能力较多，且底层实现进行了较大规模重构，项目不再继续发布 4.2 正式版，直接进入 5.0 测试线。

本版本彻底删除 `ChromiumPage`。越来越多新功能与旧 `ChromiumPage` 抽象存在冲突，继续保留会增加维护成本并限制后续能力扩展。升级到 5.0.0b0 时，请重点检查浏览器入口、标签页管理、定位符行为和 Edge 启动方式。

### 破坏性变更

- 彻底删除 `ChromiumPage`。
  - 新代码应使用 `Chromium` 作为浏览器入口，并通过 `browser.latest_tab`、`browser.new_tab()` 等方式获取标签页。
- `ChromiumOptions.set_browser_path()` 删除 `edge` 参数。
  - 需要使用 Edge 时，改用 `ChromiumOptions.use_edge()`。
- 定位符行为调整。
  - 定位符仅以 `.` 或 `#` 开头时，按 CSS 选择器匹配。
  - 后接 `=`、`:`、`^`、`$` 时，才按 DrissionPage 定位符逻辑处理。

### 新增

- `ChromiumOptions.use_edge()`：用于显式启用 Microsoft Edge。
- 适配 `<object>` 元素。

### 恢复

- `get_tabs()` 补回 `as_id` 参数，可直接返回 tab id 列表。

### 行为调整

- `tab_ids` 属性忽略插件标签页，避免扩展页污染普通页面标签列表。
- `get_tab()` 的 `id_or_num` 参数为数字时，后续 `title`、`url`、`tab_type` 三个条件参数现在会参与筛选。

### 修复

- 修复监听 WebSocket 时某些情况下获取不到数据包的问题。
- 修复控制手机 Edge 创建 tab 时卡住的问题。

### 迁移示例

#### `ChromiumPage` 迁移

旧写法：

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://example.com')
```

新写法：

```python
from DrissionPage import Chromium

browser = Chromium()
tab = browser.latest_tab
tab.get('https://example.com')
```

#### Edge 启动方式迁移

旧写法：

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions().set_browser_path(edge=True)
```

新写法：

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions().use_edge()
```

#### 定位符兼容性

如果旧代码依赖 `.name` 或 `#id` 的 DrissionPage 定位符解析，请重新确认语义。5.0.0b0 中，单独以 `.` 或 `#` 开头的定位符会优先按 CSS 选择器处理。

---

<a id="english-changelog"></a>

# English Changelog

## [5.0.0b0] - 2026-07-06

### Release Notes

5.0.0b0 is a beta release with intentional compatibility breaks. The 4.2 beta line introduced many new capabilities and significant low-level refactoring, so the project moves directly to the 5.0 beta line instead of publishing a 4.2 stable release.

`ChromiumPage` has been removed completely. More new features conflict with the old `ChromiumPage` abstraction, so keeping it would increase maintenance cost and limit future development.

### Breaking Changes

- Removed `ChromiumPage` completely.
  - Use `Chromium` as the browser entry point and operate tabs through `browser.latest_tab`, `browser.new_tab()`, and related APIs.
- Removed the `edge` parameter from `ChromiumOptions.set_browser_path()`.
  - Use `ChromiumOptions.use_edge()` to launch Microsoft Edge.
- Locator behavior changed.
  - Locators that only start with `.` or `#` are treated as CSS selectors.
  - DrissionPage locator logic is used only when followed by `=`, `:`, `^`, or `$`.

### Added

- Added `ChromiumOptions.use_edge()`.
- Added support for `<object>` elements.

### Restored

- Restored the `as_id` parameter for `get_tabs()`.

### Changed

- `tab_ids` now ignores extension/plugin tabs.
- `get_tab()` now applies `title`, `url`, and `tab_type` filters when `id_or_num` is numeric.

### Fixed

- Fixed cases where WebSocket listener packets could not be captured.
- Fixed a hang when creating tabs while controlling mobile Edge.

### Migration Examples

#### Replace `ChromiumPage`

Before:

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://example.com')
```

After:

```python
from DrissionPage import Chromium

browser = Chromium()
tab = browser.latest_tab
tab.get('https://example.com')
```

#### Use Edge

Before:

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions().set_browser_path(edge=True)
```

After:

```python
from DrissionPage import ChromiumOptions

co = ChromiumOptions().use_edge()
```

#### Locator Compatibility

If older code depends on DrissionPage parsing for `.name` or `#id`, review the behavior. In 5.0.0b0, locators that only start with `.` or `#` are treated as CSS selectors.

---

<a id="历史功能说明"></a>

# 历史功能说明 / Historical Feature Notes

- [4.2 功能说明 / 4.2 feature notes](http://drissionpage.cn/features/4.2)
- [4.1 功能说明 / 4.1 feature notes](http://drissionpage.cn/features/4.1)
- [4.0 功能说明 / 4.0 feature notes](http://drissionpage.cn/features/4)
- [3.x 功能说明 / 3.x feature notes](http://drissionpage.cn/features/3)
