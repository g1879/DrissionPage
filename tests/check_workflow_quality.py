#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static quality checks for GitHub Actions workflows.

This guard uses only the Python standard library so it can run before project
dependencies are installed. It catches known-invalid contexts, old Node 20
action pins, mutable action refs, and basic readability issues before GitHub
Actions rejects the workflow or emits runtime deprecation errors.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"

# These major versions are known to run on Node.js 20 in this project context.
# Keep the blocklist narrow and explicit so the check remains easy to review.
DISALLOWED_ACTIONS = {
    "actions/checkout": {"v1", "v2", "v3", "v4", "v5"},
    "actions/setup-python": {"v1", "v2", "v3", "v4", "v5"},
    "actions/setup-node": {"v1", "v2", "v3", "v4", "v5"},
    "actions/upload-artifact": {"v1", "v2", "v3", "v4", "v5", "v6"},
    "codecov/codecov-action": {"v1", "v2", "v3", "v4", "v5", "v6"},
}

ACTION_RE = re.compile(r"^\s*uses:\s*['\"]?(?P<uses>[^'\"\s#]+)")
ACTION_VALUE_RE = re.compile(r"^(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(?P<ref>[^\s#]+)$")
STEP_NAME_RE = re.compile(r"^\s*-\s+name:\s*.+")
STEP_START_RE = re.compile(r"^\s*-\s+(name:|uses:|run:)\s*")

# runner.temp caused a real parse failure when used in job-level env. For this
# project, use stable /tmp paths instead of runner context in workflow strings.
FORBIDDEN_CONTEXT_SNIPPETS = ("${{ runner.temp }}", "runner.temp")


def _major_ref(ref: str) -> str:
    match = re.match(r"v\d+", ref)
    return match.group(0) if match else ref


def _check_action_ref(path: Path, line_no: int, uses: str, errors: list[str]) -> None:
    match = ACTION_VALUE_RE.match(uses)
    if not match:
        errors.append(f"{path}:{line_no}: invalid or unpinned action reference: {uses!r}")
        return

    repo = match.group("repo")
    ref = match.group("ref")
    if ref in {"main", "master", "HEAD"}:
        errors.append(f"{path}:{line_no}: mutable action ref is not allowed: {uses}")

    major = _major_ref(ref)
    if major in DISALLOWED_ACTIONS.get(repo, set()):
        errors.append(
            f"{path}:{line_no}: deprecated/blocked Node 20 action runtime: {uses}. "
            "Use a Node 24 compatible major version."
        )


def _check_step_names(path: Path, lines: list[str], errors: list[str]) -> None:
    """Require each visible step to have a name for workflow readability."""
    current_step_line: int | None = None
    current_step_has_name = False

    for line_no, line in enumerate(lines, start=1):
        if STEP_START_RE.match(line):
            if current_step_line is not None and not current_step_has_name:
                errors.append(f"{path}:{current_step_line}: workflow step is missing a readable name")
            current_step_line = line_no
            current_step_has_name = bool(STEP_NAME_RE.match(line))
            continue
        if current_step_line is not None and re.match(r"^\s+name:\s*.+", line):
            current_step_has_name = True

    if current_step_line is not None and not current_step_has_name:
        errors.append(f"{path}:{current_step_line}: workflow step is missing a readable name")


def check_workflow(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []

    if not text.strip():
        return [f"{path}: workflow file is empty"]
    if "\t" in text:
        errors.append(f"{path}: tabs are not allowed in workflow YAML indentation")
    if not re.search(r"(?m)^name:\s*\S", text):
        errors.append(f"{path}: workflow is missing top-level name")
    if not re.search(r"(?m)^jobs:\s*$", text):
        errors.append(f"{path}: workflow is missing top-level jobs")

    for line_no, line in enumerate(lines, start=1):
        for snippet in FORBIDDEN_CONTEXT_SNIPPETS:
            if snippet in line:
                errors.append(f"{path}:{line_no}: forbidden workflow context snippet: {snippet}")
        action_match = ACTION_RE.match(line)
        if action_match:
            _check_action_ref(path, line_no, action_match.group("uses"), errors)

    _check_step_names(path, lines, errors)
    return errors


def main() -> int:
    workflow_paths = sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml"))
    if not workflow_paths:
        print("No workflow files found.")
        return 0

    errors: list[str] = []
    for path in workflow_paths:
        errors.extend(check_workflow(path))

    if errors:
        print("Workflow quality audit failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Workflow quality audit passed for {len(workflow_paths)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
