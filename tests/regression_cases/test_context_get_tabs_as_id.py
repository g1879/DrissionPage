# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestCase, TestContext, assert_in, assert_true, chromium


def run(ctx: TestContext) -> None:
    with chromium(ctx) as browser:
        context = browser.new_context()
        try:
            tab = context.new_tab("about:blank")
            tab_ids = context.get_tabs(as_id=True)
            assert_in(tab.tab_id, tab_ids, "context.get_tabs(as_id=True) should include created tab id")
            assert_true(all(isinstance(tab_id, str) for tab_id in tab_ids), "as_id=True should return tab id strings", tab_ids=tab_ids)

            tabs = context.get_tabs()
            assert_true(
                any(getattr(item, "tab_id", None) == tab.tab_id for item in tabs),
                "context.get_tabs() default should still return tab objects",
                tab_id=tab.tab_id,
                tabs=tabs,
            )
        finally:
            context.close()


TEST_CASE = TestCase(
    name="context_get_tabs_as_id",
    title="BrowserContext.get_tabs(as_id=True) runtime contract",
    requires_browser=True,
    features=("context_get_tabs_as_id",),
    run=run,
)
