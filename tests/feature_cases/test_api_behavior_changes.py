"""Feature: other 4.2 API and behavior changes."""
from __future__ import annotations

from inspect import signature
import json
from pathlib import Path
import tempfile
import time

from DrissionPage import Chromium
from DrissionPage._browsers.chromium_context import ChromiumContext
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._functions.settings import Settings
from DrissionPage._pages.chromium_frame import ChromiumFrame
from DrissionPage._pages.chromium_tab import ChromiumTab
from DrissionPage._units.actions import Actions
from DrissionPage._units.clicker import Clicker
from DrissionPage._units.waiter import BaseWaiter, ElementWaiter

from support import assert_equal, assert_false, assert_in, assert_not_in, assert_true, html, local_server, make_browser


FEATURE_ID = 'api_behavior_changes'

BROWSER_PHASE = True

def run(ctx):
    test_api_shape_contracts()
    test_drag_contract_without_browser()
    if ctx.skip_browser:
        ctx.skip_current_browser('browser-backed API behavior checks skipped by --skip-browser')
        return
    test_browser_api_behaviors(ctx.browser_path)


def test_api_shape_contracts():
    browser_new_tab = signature(Chromium.new_tab).parameters
    context_new_tab = signature(ChromiumContext.new_tab).parameters
    assert_in('hidden', browser_new_tab, 'Chromium.new_tab() should expose hidden parameter')
    assert_equal(browser_new_tab['hidden'].default, False, 'Chromium.new_tab(hidden) default should be False')
    assert_equal(context_new_tab['hidden'].default, False, 'ChromiumContext.new_tab(hidden) default should be False')
    assert_not_in('new_context', browser_new_tab, 'Chromium.new_tab() should not expose removed new_context parameter')
    assert_in('as_id', signature(Chromium.get_tab).parameters, 'Chromium.get_tab() should expose as_id parameter')
    assert_false(hasattr(Chromium, 'tabs_count'), 'Chromium.tabs_count should be removed')
    assert_false(hasattr(ChromiumTab, 'reconnect'), 'ChromiumTab.reconnect() should be removed')
    assert_false(hasattr(ChromiumFrame, 'reconnect'), 'ChromiumFrame.reconnect() should be removed')

    assert_in('offset_x', signature(Actions.drag_in).parameters, 'Actions.drag_in() should expose offset_x')
    assert_in('offset_y', signature(Actions.drag_in).parameters, 'Actions.drag_in() should expose offset_y')
    assert_true(hasattr(ChromiumTab, 'new_ele'), 'ChromiumTab should expose new_ele()')
    assert_true(hasattr(ChromiumTab, 'activate'), 'ChromiumTab should expose activate()')

    get_params = signature(ChromiumTab.get).parameters
    assert_in('raise_err', get_params, 'ChromiumTab.get() should expose raise_err')
    assert_not_in('show_errmsg', get_params, 'ChromiumTab.get() should not expose removed show_errmsg')
    assert_in('timeout', signature(BaseWaiter.upload_paths_inputted).parameters,
              'upload_paths_inputted() should expose timeout')
    assert_in('file_exists', signature(Clicker.to_download).parameters,
              'click.to_download() should expose file_exists')
    assert_in('wait_stop', signature(ElementWaiter.clickable).parameters,
              'ElementWaiter.clickable() should use wait_stop parameter')
    assert_not_in('wait_moved', signature(ElementWaiter.clickable).parameters,
                  'ElementWaiter.clickable() should not expose wait_moved')
    assert_in('wait_stop', signature(Clicker.__call__).parameters,
              'element clicker should expose wait_stop parameter')
    assert_in('checked', signature(ChromiumElement.check).parameters,
              'ChromiumElement.check() should use checked parameter')
    assert_not_in('uncheck', signature(ChromiumElement.check).parameters,
                  'ChromiumElement.check() should not expose uncheck parameter')
    assert_true(hasattr(Settings, 'wait_stop_before_click'), 'Settings should expose wait_stop_before_click')
    assert_true(hasattr(Settings, 'set_wait_stop_before_click'), 'Settings should expose set_wait_stop_before_click()')
    assert_true(hasattr(ChromiumElement, 'css_selector'), 'ChromiumElement should expose css_selector')


def test_drag_contract_without_browser():
    class FakeRect:
        viewport_location = (10, 20)
        viewport_midpoint = (50, 60)

    class FakeElement:
        rect = FakeRect()

    class FakeOwner:
        def __init__(self):
            self.cdp_calls = []

        def __call__(self, loc):
            assert_equal(loc, '#drop', 'drag_in() should resolve target through owner')
            return FakeElement()

        def _run_cdp(self, method, **kwargs):
            self.cdp_calls.append((method, kwargs))

    owner = FakeOwner()
    actions = Actions(owner)
    assert_true(actions.drag_in('#drop', text='payload', offset_x=3, offset_y=4) is actions,
                'drag_in() should be chainable')
    assert_equal(len(owner.cdp_calls), 2, 'drag_in() should dispatch dragEnter and drop')
    for event, (method, kwargs) in zip(('dragEnter', 'drop'), owner.cdp_calls):
        assert_equal(method, 'Input.dispatchDragEvent', 'drag_in() should use CDP drag event')
        assert_equal(kwargs['type'], event, f'drag_in() should send {event}')
        assert_equal((kwargs['x'], kwargs['y']), (13, 24), 'offsets should apply to viewport_location')
        assert_equal(kwargs['data']['items'][0]['data'], 'payload', 'text payload should be sent')


def test_browser_api_behaviors(executable):
    routes = {
        '/': lambda req: html(
            """
            <body>
              <div id="parent-ready">Parent Ready</div>
              <button id="stable-button">Stable Button</button>
              <form id="upload-form">
                <input id="upload" type="file">
                <input id="upload-click" type="file">
              </form>
            </body>
            """,
            title='api behavior page',
        ),
        '/hidden': lambda req: html("<body><div id='hidden-ready'>Hidden Ready</div></body>", title='hidden tab'),
    }
    with local_server(routes) as base, make_browser(executable) as browser:
        tab = browser.latest_tab
        assert_true(tab.get(base + '/'), 'api behavior page should load')

        assert_true(tab('#stable-button').wait.clickable(timeout=5),
                    'wait.clickable(wait_stop default) should return bool for stable clickable element')
        css_selector = tab('#parent-ready').css_selector
        assert_true(css_selector, 'element.css_selector should expose renamed css selector path')
        assert_in('div[id="parent-ready"]', css_selector,
                  'element.css_selector should include the target element identity')

        created = tab.new_ele('<section id="created-by-new-ele">Created</section>')
        assert_equal(created.attr('id'), 'created-by-new-ele', 'new_ele() should create element from HTML')
        assert_true(tab('#created-by-new-ele', timeout=5), 'new_ele() result should be attached to the page')

        tab.activate()
        assert_equal(browser.latest_tab.tab_id, tab.tab_id, 'activate() should make the tab active')

        tab.console.start()
        tab.console.clear()
        tab.run_js("console.log('dp-console', {answer: 42});")
        console_data = None
        console_payload = ''
        deadline = time.time() + 5
        while time.time() < deadline:
            item = tab.console.wait(timeout=1)
            if not item:
                continue
            payload = json.dumps(item.data, ensure_ascii=False, default=str)
            if 'dp-console' in payload:
                console_data = item
                console_payload = payload
                break
        assert_true(console_data, 'console listener should receive the emitted console log')
        assert_true(console_data.data, 'console data should expose raw payload')
        assert_true(console_data.args or console_data.text,
                    'console data should expose arguments or rendered log text')
        assert_in('dp-console', console_payload, 'console data should include emitted log content')
        tab.console.stop()

        with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.txt', delete=False) as file_obj:
            file_obj.write('upload-body')
            upload_path = file_obj.name
        try:
            tab('#upload').input(upload_path)
            assert_equal(tab.run_js("return document.querySelector('#upload').files[0].name;"),
                         Path(upload_path).name, 'direct file input should set selected file')
            assert_true(tab.wait.upload_paths_inputted(timeout=5),
                        'upload_paths_inputted(timeout) should return after direct input')

            tab.set.upload_files(upload_path)
            tab('#upload-click').click(timeout=5)
            assert_true(tab.wait.upload_paths_inputted(timeout=5),
                        'upload_paths_inputted(timeout) should wait for intercepted chooser upload')
            assert_equal(tab.run_js("return document.querySelector('#upload-click').files[0].name;"),
                         Path(upload_path).name, 'set.upload_files() should fill clicked file chooser')
        finally:
            Path(upload_path).unlink(missing_ok=True)

        hidden = browser.new_tab(hidden=True)
        assert_true(hidden.get(base + '/hidden'), 'hidden tab should navigate')
        assert_equal(hidden('#hidden-ready', timeout=5).text, 'Hidden Ready', 'hidden tab DOM should be readable')
        hidden_id = browser.get_tab(id_or_num=hidden.tab_id, as_id=True)
        assert_equal(hidden_id, hidden.tab_id, 'get_tab(as_id=True) should return the tab id')
