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
GATE_SUITE="${DP_TESTS_GATE_SUITE:-stable}"
KNOWN_SUITE="${DP_TESTS_KNOWN_SUITE:-known}"
RUN_KNOWN="${DP_TESTS_RUN_KNOWN:-1}"
RUN_LOCAL_SSR="${DP_TESTS_RUN_LOCAL_SSR:-0}"
LOCAL_SSR_URL="${DP_TEST_SITE_URL:-${DP_LOCAL_FIXTURE_URL:-}}"
COVERAGE_DIR="$REPORT_DIR/coverage"
COVERAGE_RCFILE="${DP_TESTS_COVERAGE_RCFILE:-$REPO_ROOT/.coveragerc}"
COVERAGE_BIN="${DP_TESTS_COVERAGE_BIN:-$PYTHON_BIN -m coverage}"
COVERAGE_ENABLED="${DP_TESTS_COVERAGE:-1}"
BROWSER_GATE_ATTEMPTS="${DP_TESTS_BROWSER_GATE_ATTEMPTS:-2}"

if [[ ! "$BROWSER_GATE_ATTEMPTS" =~ ^[1-9][0-9]*$ ]]; then
  echo "DP_TESTS_BROWSER_GATE_ATTEMPTS must be a positive integer, got: $BROWSER_GATE_ATTEMPTS" >&2
  exit 2
fi

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
  "$REPORT_DIR/pre-browser.md" \
  "$REPORT_DIR/current-stable-no-browser.json" \
  "$REPORT_DIR/current-stable-no-browser.md" \
  "$REPORT_DIR/pre-stable-no-browser.json" \
  "$REPORT_DIR/pre-stable-no-browser.md" \
  "$REPORT_DIR/current-stable-browser.json" \
  "$REPORT_DIR/current-stable-browser.md" \
  "$REPORT_DIR/pre-stable-browser.json" \
  "$REPORT_DIR/pre-stable-browser.md" \
  "$REPORT_DIR/current-known-no-browser.json" \
  "$REPORT_DIR/current-known-no-browser.md" \
  "$REPORT_DIR/pre-known-no-browser.json" \
  "$REPORT_DIR/pre-known-no-browser.md" \
  "$REPORT_DIR/current-known-browser.json" \
  "$REPORT_DIR/current-known-browser.md" \
  "$REPORT_DIR/pre-known-browser.json" \
  "$REPORT_DIR/pre-known-browser.md" \
  "$REPORT_DIR/current-local-ssr.json" \
  "$REPORT_DIR/current-local-ssr.md" \
  "$REPORT_DIR/current-local-ssr-known.json" \
  "$REPORT_DIR/current-local-ssr-known.md"
rm -f "$REPORT_DIR"/*-attempt-*.json "$REPORT_DIR"/*-attempt-*.md
rm -rf "$COVERAGE_DIR"
mkdir -p "$COVERAGE_DIR"
if [[ "$COVERAGE_ENABLED" == "1" ]]; then
  rm -f "$REPO_ROOT/.coverage" "$REPO_ROOT"/.coverage.*
fi

overall_rc=0
failed_steps=()
flaky_steps=()

mark_failed() {
  failed_steps+=("$1")
  overall_rc=1
}

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
    mark_failed "$label"
  fi
}

run_step "compile Python test suite" \
  "$PYTHON_BIN" -m compileall -q \
    "$SCRIPT_DIR/run.py" \
    "$SCRIPT_DIR/runner.py" \
    "$SCRIPT_DIR/support.py" \
    "$SCRIPT_DIR/check_runner_quality.py" \
    "$SCRIPT_DIR/feature_cases" \
    "$SCRIPT_DIR/regression_cases"

run_step "validate test runner semantics" \
  env "PYTHONPATH=$SCRIPT_DIR:$REPO_ROOT:${PYTHONPATH:-}" \
  "$PYTHON_BIN" "$SCRIPT_DIR/check_runner_quality.py"

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
    echo "browser_gate_attempts=$BROWSER_GATE_ATTEMPTS"
    echo "gate_suite=$GATE_SUITE"
    echo "known_suite=$KNOWN_SUITE"
    echo "run_known=$RUN_KNOWN"
    echo "run_local_ssr=$RUN_LOCAL_SSR"
    echo "local_ssr_configured=$([[ -n "$LOCAL_SSR_URL" ]] && echo true || echo false)"
    echo "github_event_name=${GITHUB_EVENT_NAME:-}"
    echo "private_fixture_configured=${HAS_PRIVATE_FIXTURE:-unknown}"
    echo "private_fixture_smoke_enabled=${RUN_PRIVATE_FIXTURE:-unknown}"
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
    --suite all \
    --list-cases | tee "$REPORT_DIR/cases.txt"
}

run_step "list cases" list_cases

execute_case_batch() {
  local source="$1"
  local report_name="$2"
  shift 2
  local common_args=(
    --timeout "$TIMEOUT"
    --artifacts-dir "$ARTIFACT_DIR/$report_name"
    --report-json "$REPORT_DIR/$report_name.json"
    --report-md "$REPORT_DIR/$report_name.md"
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
  "${cmd[@]}"
}

run_case_batch() {
  local label="$1"
  local source="$2"
  local report_name="$3"
  shift 3
  run_step "$label" execute_case_batch "$source" "$report_name" "$@"
}

run_report_case_batch() {
  local label="$1"
  local source="$2"
  local report_name="$3"
  shift 3
  echo
  echo "=== $label ==="
  if execute_case_batch "$source" "$report_name" "$@"; then
    echo "=== $label: reported ==="
  else
    local rc=$?
    echo "=== $label: report generation failed rc=$rc ==="
    mark_failed "$label"
  fi
}

promote_attempt_report() {
  local attempt_name="$1"
  local report_name="$2"
  local extension
  for extension in json md; do
    if [[ -f "$REPORT_DIR/$attempt_name.$extension" ]]; then
      cp "$REPORT_DIR/$attempt_name.$extension" "$REPORT_DIR/$report_name.$extension"
    fi
  done
}

run_browser_gate_with_retry() {
  local label="$1"
  local source="$2"
  local report_name="$3"
  shift 3
  local attempt attempt_name rc
  for ((attempt = 1; attempt <= BROWSER_GATE_ATTEMPTS; attempt++)); do
    attempt_name="$report_name-attempt-$attempt"
    echo
    echo "=== $label (attempt $attempt/$BROWSER_GATE_ATTEMPTS) ==="
    if execute_case_batch "$source" "$attempt_name" "$@"; then
      promote_attempt_report "$attempt_name" "$report_name"
      if ((attempt > 1)); then
        flaky_steps+=("$label (passed on attempt $attempt/$BROWSER_GATE_ATTEMPTS)")
      fi
      echo "=== $label: passed on attempt $attempt/$BROWSER_GATE_ATTEMPTS ==="
      return 0
    else
      rc=$?
      echo "=== $label: attempt $attempt/$BROWSER_GATE_ATTEMPTS failed rc=$rc ==="
    fi
  done
  promote_attempt_report "$attempt_name" "$report_name"
  mark_failed "$label (failed after $BROWSER_GATE_ATTEMPTS attempts)"
  return 0
}

run_case_batch "current stable no-browser gate" current current-stable-no-browser \
  --suite "$GATE_SUITE" --skip-browser --no-browser-only --fail-on-failures
run_case_batch "pre-release stable no-browser gate" pre pre-stable-no-browser \
  --suite "$GATE_SUITE" --skip-browser --no-browser-only --fail-on-failures

if [[ -n "$BROWSER_PATH" && -x "$BROWSER_PATH" ]]; then
  run_browser_gate_with_retry "current stable browser gate" current current-stable-browser \
    --suite "$GATE_SUITE" --browser-path "$BROWSER_PATH" --browser-only --fail-on-failures
  run_browser_gate_with_retry "pre-release stable browser gate" pre pre-stable-browser \
    --suite "$GATE_SUITE" --browser-path "$BROWSER_PATH" --browser-only --fail-on-failures

  if [[ "$RUN_KNOWN" == "1" ]]; then
    run_report_case_batch "current known-issue repros (report-only)" current current-known-browser \
      --suite "$KNOWN_SUITE" --browser-path "$BROWSER_PATH" --browser-only
    run_report_case_batch "pre-release known-issue repros (report-only)" pre pre-known-browser \
      --suite "$KNOWN_SUITE" --browser-path "$BROWSER_PATH" --browser-only
  fi

  if [[ "$RUN_LOCAL_SSR" == "1" && -n "$LOCAL_SSR_URL" ]]; then
    export DP_TEST_SITE_URL="$LOCAL_SSR_URL"
    export DP_PRIVATE_FIXTURE_URL="$LOCAL_SSR_URL"
    run_case_batch "current local SSR business scenarios gate" current current-local-ssr \
      --suite local --browser-path "$BROWSER_PATH" --include-online \
      --case ssr_marketplace_flow \
      --case ssr_social_notes_mobile \
      --fail-on-failures
    run_report_case_batch "current local SSR full smoke known issue (report-only)" current current-local-ssr-known \
      --suite local --browser-path "$BROWSER_PATH" --include-online \
      --case ssr_site_smoke
  fi
else
  echo
  echo "Browser cases skipped: DP_BROWSER_PATH is unset or not executable."
  if [[ "$REQUIRE_BROWSER" == "1" ]]; then
    mark_failed "browser availability"
  fi
fi

if [[ "$RUN_KNOWN" == "1" ]]; then
  run_report_case_batch "current known-issue no-browser repros (report-only)" current current-known-no-browser \
    --suite "$KNOWN_SUITE" --skip-browser --no-browser-only
  run_report_case_batch "pre-release known-issue no-browser repros (report-only)" pre pre-known-no-browser \
    --suite "$KNOWN_SUITE" --skip-browser --no-browser-only
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

echo
echo "=== CI summary ==="
if ((${#flaky_steps[@]})); then
  echo "Flaky gates:"
  printf '  - %s\n' "${flaky_steps[@]}"
fi
if ((${#failed_steps[@]})); then
  echo "Failed gates:"
  printf '  - %s\n' "${failed_steps[@]}"
else
  echo "All required gates passed."
fi

exit "$overall_rc"
