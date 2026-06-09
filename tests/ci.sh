#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="${DP_TESTS_REPORT_DIR:-$REPO_ROOT/tests/reports/ci}"
ARTIFACT_DIR="${DP_TESTS_ARTIFACT_DIR:-/tmp/dp-tests-artifacts-ci}"
PRE_VENV="${DP_TESTS_PRE_VENV:-/tmp/dp-tests-pre-venv}"
PYTHON_BIN="${PYTHON_BIN:-python}"
BROWSER_PATH="${DP_BROWSER_PATH:-}"
TIMEOUT="${DP_TESTS_TIMEOUT:-8}"
REQUIRE_BROWSER="${DP_TESTS_REQUIRE_BROWSER:-0}"
COVERAGE_DIR="$REPORT_DIR/coverage"
COVERAGE_RCFILE="${DP_TESTS_COVERAGE_RCFILE:-$REPO_ROOT/.coveragerc}"
COVERAGE_BIN="${DP_TESTS_COVERAGE_BIN:-$PYTHON_BIN -m coverage}"
COVERAGE_ENABLED="${DP_TESTS_COVERAGE:-1}"

cd "$REPO_ROOT"
mkdir -p "$REPORT_DIR" "$ARTIFACT_DIR"
rm -f \
  "$REPORT_DIR/environment.txt" \
  "$REPORT_DIR/cases.txt" \
  "$REPORT_DIR/current-no-browser.json" \
  "$REPORT_DIR/current-no-browser.md" \
  "$REPORT_DIR/pre-no-browser.json" \
  "$REPORT_DIR/pre-no-browser.md" \
  "$REPORT_DIR/current-browser.json" \
  "$REPORT_DIR/current-browser.md" \
  "$REPORT_DIR/pre-browser.json" \
  "$REPORT_DIR/pre-browser.md"
rm -rf "$COVERAGE_DIR"
mkdir -p "$COVERAGE_DIR"
if [[ "$COVERAGE_ENABLED" == "1" ]]; then
  rm -f "$REPO_ROOT/.coverage" "$REPO_ROOT"/.coverage.*
fi

overall_rc=0

run_step() {
  local label="$1"
  shift
  echo
  echo "=== $label ==="
  if "$@"; then
    echo "=== $label: passed ==="
  else
    local rc=$?
    echo "=== $label: failed rc=$rc ==="
    overall_rc=1
  fi
}

run_step "compile Python test suite" \
  "$PYTHON_BIN" -m compileall -q \
    "$SCRIPT_DIR/run.py" \
    "$SCRIPT_DIR/runner.py" \
    "$SCRIPT_DIR/support.py" \
    "$SCRIPT_DIR/feature_cases" \
    "$SCRIPT_DIR/regression_cases"

write_environment() {
  {
    echo "generated_at_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "repo_root=$REPO_ROOT"
    echo "script_dir=$SCRIPT_DIR"
    echo "python_bin=$PYTHON_BIN"
    "$PYTHON_BIN" - <<'PY'
import platform
import sys
print(f"python_executable={sys.executable}")
print(f"python_version={sys.version.replace(chr(10), ' ')}")
print(f"platform={platform.platform()}")
PY
    echo "browser_path=${BROWSER_PATH:-}"
    echo "browser_executable=$([[ -n "$BROWSER_PATH" && -x "$BROWSER_PATH" ]] && echo true || echo false)"
    echo "timeout=$TIMEOUT"
    echo "require_browser=$REQUIRE_BROWSER"
    echo "coverage_enabled=$COVERAGE_ENABLED"
    echo "coverage_rcfile=$COVERAGE_RCFILE"
    echo "coverage_dir=$COVERAGE_DIR"
    echo "report_dir=$REPORT_DIR"
    echo "artifact_dir=$ARTIFACT_DIR"
    echo "pre_venv=$PRE_VENV"
  } > "$REPORT_DIR/environment.txt"
}

run_step "write environment metadata" write_environment

list_cases() {
  "$PYTHON_BIN" "$SCRIPT_DIR/run.py" \
    --source current \
    --list-cases | tee "$REPORT_DIR/cases.txt"
}

run_step "list cases" list_cases

run_case_batch() {
  local label="$1"
  local source="$2"
  local report_name="$3"
  shift 3
  local common_args=(
    --timeout "$TIMEOUT"
    --artifacts-dir "$ARTIFACT_DIR/$report_name"
    --report-json "$REPORT_DIR/$report_name.json"
    --report-md "$REPORT_DIR/$report_name.md"
    --fail-on-failures
  )
  local cmd=()
  if [[ "$source" == "current" ]]; then
    local launcher=("$PYTHON_BIN")
    if [[ "$COVERAGE_ENABLED" == "1" ]]; then
      launcher=($COVERAGE_BIN run --rcfile "$COVERAGE_RCFILE" --parallel-mode)
    fi
    cmd=(
      env "PYTHONPATH=$SCRIPT_DIR:$REPO_ROOT:${PYTHONPATH:-}"
      "${launcher[@]}" "$SCRIPT_DIR/runner.py"
      "${common_args[@]}"
    )
  else
    cmd=(
      "$PYTHON_BIN" "$SCRIPT_DIR/run.py"
      --source pre
      --venv "$PRE_VENV"
      "${common_args[@]}"
    )
  fi
  cmd+=("$@")
  run_step "$label" "${cmd[@]}"
}

run_case_batch "current no-browser cases" current current-no-browser --skip-browser --no-browser-only
run_case_batch "pre-release no-browser cases" pre pre-no-browser --skip-browser --no-browser-only

if [[ -n "$BROWSER_PATH" && -x "$BROWSER_PATH" ]]; then
  run_case_batch "current browser cases" current current-browser --browser-path "$BROWSER_PATH" --browser-only
  run_case_batch "pre-release browser cases" pre pre-browser --browser-path "$BROWSER_PATH" --browser-only
else
  echo
  echo "Browser cases skipped: DP_BROWSER_PATH is unset or not executable."
  if [[ "$REQUIRE_BROWSER" == "1" ]]; then
    overall_rc=1
  fi
fi

write_coverage_reports() {
  if [[ "$COVERAGE_ENABLED" != "1" ]]; then
    echo "Coverage disabled by DP_TESTS_COVERAGE=$COVERAGE_ENABLED"
    return 0
  fi
  (
    cd "$REPO_ROOT"
    $COVERAGE_BIN combine --rcfile "$COVERAGE_RCFILE"
    $COVERAGE_BIN report --rcfile "$COVERAGE_RCFILE" > "$COVERAGE_DIR/coverage.txt"
    $COVERAGE_BIN xml --rcfile "$COVERAGE_RCFILE" -o "$COVERAGE_DIR/coverage.xml"
    $COVERAGE_BIN json --rcfile "$COVERAGE_RCFILE" -o "$COVERAGE_DIR/coverage.json"
    $COVERAGE_BIN html --rcfile "$COVERAGE_RCFILE" -d "$COVERAGE_DIR/html"
  )
}

run_step "write coverage reports" write_coverage_reports

exit "$overall_rc"
