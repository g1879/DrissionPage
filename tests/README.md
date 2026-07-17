# DrissionPage 测试

以下命令均在仓库根目录执行。

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 测试当前源码

先运行不需要浏览器的稳定测试：

```bash
python tests/run.py --source current --suite stable --skip-browser --no-browser-only --fail-on-failures
```

再运行真实 Chromium 测试：

```bash
python tests/run.py --source current --suite stable --browser-only --browser-path "<Chrome 可执行文件路径>" --fail-on-failures
```

常见 Chrome 路径：

- Windows：`C:\Program Files\Google\Chrome\Application\chrome.exe`
- macOS：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Linux：`/usr/bin/google-chrome`

macOS/Linux 也可以使用 shell 入口；macOS 会自动发现默认 Chrome：

```bash
./tests/run.sh current --suite stable --browser-only --fail-on-failures
```

## 复现已知问题

`known` 用例预期可能显示 `[FAIL]`，默认只生成报告，不会让命令失败：

```bash
python tests/run.py --source current --suite known --skip-browser --no-browser-only

python tests/run.py --source current --suite known --browser-only --browser-path "<Chrome 可执行文件路径>"
```

运行单个用例：

```bash
python tests/run.py --source current --case listener_ws_sse --browser-path "<Chrome 可执行文件路径>"
```

## 测试分组

| 分组 | 用途 |
| --- | --- |
| `stable` | 必须通过的主测试。 |
| `known` | 已知问题复现，默认只报告。 |
| `local` | 需要外部网络或独立 test-site 的专项测试。 |
| `all` | 手动运行全部测试。 |
