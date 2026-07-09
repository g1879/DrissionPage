# DrissionPage

DrissionPage is a Python browser automation library built around Chromium-based browsers and HTTP session workflows.

It is designed for concise code, practical automation, web testing, data collection, and browser debugging without WebDriver.

- Website: <https://drissionpage.cn>
- GitHub: <https://github.com/g1879/DrissionPage>
- Gitee: <https://gitee.com/g1879/DrissionPage>
- Changelog: [CHANGELOG.md](./CHANGELOG.md)
- Chinese README: [README.md](./README.md)

## Quick Links

### Upgrade and Release Notes

- [Version Notice](#version-notice)
- [Migration to 5.0.0b0](#migration-to-500b0)
- [Historical Feature Notes](#historical-feature-notes)
- [Full Changelog](./CHANGELOG.md#english-changelog)
- [中文 README](./README.md)

### Project Guide

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Highlights](#highlights)
- [Runtime Requirements](#runtime-requirements)
- [Terms](#terms)

## Version Notice

The current beta line is **5.0.0b0**.

The project moved directly from the 4.2 beta line to the 5.0 beta line because the beta branch introduced many new features and significant low-level refactoring.

`ChromiumPage` has been removed in 5.0.0b0. Please review the compatibility notes before upgrading.

See [CHANGELOG.md](./CHANGELOG.md) for the full release notes.

## Historical Feature Notes

- [4.2 feature notes](http://drissionpage.cn/features/4.2)
- [4.1 feature notes](http://drissionpage.cn/features/4.1)
- [4.0 feature notes](http://drissionpage.cn/features/4)
- [3.x feature notes](http://drissionpage.cn/features/3)

## Installation

```bash
pip install DrissionPage
```

For pre-release versions:

```bash
pip install --pre --upgrade DrissionPage
```

## Basic Usage

```python
from DrissionPage import Chromium

browser = Chromium()
tab = browser.latest_tab
tab.get('https://example.com')
print(tab.title)
```

Session mode:

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('https://example.com')
print(page.title)
```

## Migration to 5.0.0b0

### Replace `ChromiumPage`

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

### Use Edge

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

### Locator Changes

In 5.0.0b0, locators that only start with `.` or `#` are treated as CSS selectors. DrissionPage locator logic is used only when the prefix is followed by `=`, `:`, `^`, or `$`.

Review selectors such as `.class-name` and `#element-id` when upgrading from older beta versions.

## Highlights

- No WebDriver dependency.
- No browser-driver version matching.
- Fast Chromium control through DevTools Protocol.
- Direct multi-tab operations without switching global state.
- Easier iframe handling.
- Integrated waits and retries.
- Built-in download helpers.
- Session and browser workflows in one project.
- Useful APIs for testing, data collection, and debugging.

## Runtime Requirements

- Operating systems: Windows, Linux, macOS.
- Python: 3.6+.
- Browsers: Chromium-based browsers, including Chrome and Edge; Electron applications are also supported.

## Legal and Ethical Use

Use DrissionPage only for lawful, authorized, and ethical automation tasks.

Do not use this project for attacks, harassment, unauthorized data collection, or activities that violate local laws, website terms, or robots rules.

## Terms

Individuals may use and distribute the source code for learning and lawful non-commercial purposes. Commercial use requires authorization from the copyright holder.

Users are responsible for all consequences of their own use. The copyright holder is not liable for disputes, risks, or losses caused by using DrissionPage.
