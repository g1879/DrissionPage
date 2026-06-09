#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_BROWSER="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MODE="${1:-}"
shift || true

usage() {
  cat <<'EOF'
Usage:
  ./tests/run.sh [pre|current|both] [options]

Modes:
  pre      Test the PyPI pre-release package in /tmp/dp-tests-pre-venv.
  current  Test the current checkout source code.
  both     Run pre first, then current.

If mode is omitted, an interactive selector is shown.
The first pre run installs DrissionPage when the venv is missing; later runs reuse it.

Common options forwarded to tests/run.py:
  --suite stable     Run the stable CI gate cases only (default).
  --suite known      Run isolated known-issue repro cases; report-only unless --fail-on-failures is added.
  --suite local      Run opt-in local/online smoke cases.
  --suite all        Run every case.
  --skip-browser
  --include-online
  --fail-on-failures
  --upgrade-pre
  --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  --case listener_ws_sse

Default behavior is the stable suite in report-only mode: failed cases print as
[FAIL] and exit 0. Use --fail-on-failures to return non-zero when any selected
case fails. Explicit --case runs search all suites unless --suite is provided.
EOF
}

if [[ "${MODE}" == "-h" || "${MODE}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ -z "${MODE}" ]]; then
  echo "选择测试目标："
  echo "  1) pre     PyPI 预发布包测试（独立 venv）"
  echo "  2) current 当前源码测试（当前 checkout）"
  echo "  3) both    两者都跑"
  printf "请输入 1/2/3 [默认 1]: "
  read -r choice
  case "${choice:-1}" in
    1|pre) MODE="pre" ;;
    2|current) MODE="current" ;;
    3|both) MODE="both" ;;
    *) echo "未知选择: $choice" >&2; exit 2 ;;
  esac
fi

case "$MODE" in
  1|p|pre) MODE="pre" ;;
  2|c|current) MODE="current" ;;
  3|b|both) MODE="both" ;;
  *) echo "未知模式: $MODE" >&2; usage >&2; exit 2 ;;
esac

has_arg() {
  local name="$1"
  shift
  for arg in "$@"; do
    [[ "$arg" == "$name" || "$arg" == "$name="* ]] && return 0
  done
  return 1
}

run_one() {
  local source="$1"
  shift
  local report_prefix="$source"
  local cmd=(python "$SCRIPT_DIR/run.py" --source "$source" --no-install)
  if [[ "$source" == "pre" ]]; then
    cmd=(python "$SCRIPT_DIR/run.py" --source pre --venv /tmp/dp-tests-pre-venv)
  fi
  if ! has_arg "--browser-path" "$@" && [[ -x "$DEFAULT_BROWSER" ]]; then
    cmd+=(--browser-path "$DEFAULT_BROWSER")
  fi
  if ! has_arg "--report-json" "$@"; then
    cmd+=(--report-json "$SCRIPT_DIR/reports/${report_prefix}-latest.json")
  fi
  if ! has_arg "--report-md" "$@"; then
    cmd+=(--report-md "$SCRIPT_DIR/reports/${report_prefix}-latest.md")
  fi
  cmd+=("$@")
  echo
  echo "=== DrissionPage tests: $source ==="
  (cd "$REPO_ROOT" && "${cmd[@]}")
}

if [[ "$MODE" == "both" ]]; then
  run_one pre "$@"
  pre_rc=$?
  run_one current "$@"
  current_rc=$?
  if [[ $pre_rc -ne 0 || $current_rc -ne 0 ]]; then
    exit 1
  fi
else
  run_one "$MODE" "$@"
fi
