# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestFailure, TestCase, TestContext, assert_true, chromium, local_server
from support import function_accepts


def _nav_get(obj, url: str):
    kwargs = {"retry": 0}
    if function_accepts(obj.get, "raise_err"):
        kwargs["raise_err"] = False
    else:
        kwargs["show_errmsg"] = False
    return obj.get(url, **kwargs)


def run(ctx: TestContext) -> None:
    from DrissionPage import SessionPage

    errors: list[str] = []

    def check_nav(res, *, expected_ok=None, expected_status=None, label="nav", url_suffix=None):
        if not hasattr(res, "ok") or not hasattr(res, "status") or not hasattr(res, "url"):
            errors.append(f"{label}: result is not NavResult-like: {res!r}")
            return
        if expected_ok is not None and res.ok is not expected_ok:
            errors.append(f"{label}: expected ok={expected_ok!r}, got {res.ok!r}; result={res!r}")
        if expected_status is not None and res.status != expected_status:
            errors.append(f"{label}: expected status={expected_status!r}, got {res.status!r}; result={res!r}")
        if url_suffix and not (res.url or "").endswith(url_suffix):
            errors.append(f"{label}: expected final url ending {url_suffix!r}, got {res.url!r}")
        try:
            b = bool(res)
            if not isinstance(b, bool):
                errors.append(f"{label}: bool(result) should return bool, got {type(b).__name__}: {b!r}")
        except Exception as e:
            errors.append(f"{label}: bool(result) raised {type(e).__name__}: {e}")

    with local_server() as (base, _server):
        sp = SessionPage()
        check_nav(_nav_get(sp, base + "/ok"), expected_ok=True, expected_status=200, label="SessionPage /ok", url_suffix="/ok")
        check_nav(_nav_get(sp, base + "/missing"), expected_ok=False, expected_status=404, label="SessionPage /missing")
        check_nav(_nav_get(sp, base + "/error"), expected_ok=False, expected_status=500, label="SessionPage /error")
        check_nav(_nav_get(sp, base + "/redirect"), expected_ok=True, expected_status=200, label="SessionPage /redirect", url_suffix="/ok")

        if ctx.skip_browser:
            if errors:
                raise TestFailure("Navigation result mismatches:\n- " + "\n- ".join(errors))
            return

        with chromium(ctx) as browser:
            tab = browser.latest_tab
            check_nav(_nav_get(tab, base + "/ok"), expected_ok=True, expected_status=200, label="ChromiumTab /ok", url_suffix="/ok")
            check_nav(_nav_get(tab, base + "/missing"), expected_ok=False, expected_status=404, label="ChromiumTab /missing", url_suffix="/missing")
            check_nav(_nav_get(tab, base + "/error"), expected_ok=False, expected_status=500, label="ChromiumTab /error", url_suffix="/error")
            check_nav(_nav_get(tab, base + "/redirect"), expected_ok=True, expected_status=200, label="ChromiumTab /redirect", url_suffix="/ok")

    if errors:
        raise TestFailure("Navigation result mismatches:\n- " + "\n- ".join(errors))


TEST_CASE = TestCase(
    name="navigation_result",
    title="get() NavResult status, redirects, errors and alert-on-open",
    requires_browser=False,
    features=("nav_result", "get_raise_err"),
    run=run,
)
