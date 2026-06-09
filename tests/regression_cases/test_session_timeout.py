# -*- coding: utf-8 -*-
from __future__ import annotations

import time

from support import TestCase, TestContext, assert_true, local_server


def run(ctx: TestContext) -> None:
    from DrissionPage import SessionPage

    with local_server() as (base, _server):
        page = SessionPage()
        start = time.perf_counter()
        res = page.get(base + "/slow?delay=2", timeout=0.25, retry=0, raise_err=False)
        elapsed = time.perf_counter() - start
        assert_true(elapsed < 1.5, "SessionPage.get(timeout=...) should not wait for full slow response", elapsed=elapsed)
        assert_true(hasattr(res, "ok"), "timeout result should still be NavResult-like")
        status = getattr(res, "status", None)
        assert_true(status is None or isinstance(status, str),
                    "timeout without HTTP response should keep unknown status or expose a transport error string",
                    status=status, elapsed=elapsed)
        if status is None:
            assert_true(res.ok is None, "timeout without status should keep ok=None unknown semantics", status=status)
        else:
            assert_true(res.ok is False, "timeout transport error should not be successful", status=status)
        assert_true(bool(res) is False, "timeout navigation result should be falsey without raising", status=status)


TEST_CASE = TestCase(
    name="session_timeout",
    title="SessionPage timeout contract on slow local endpoint",
    requires_browser=False,
    features=("session_timeout",),
    run=run,
)
