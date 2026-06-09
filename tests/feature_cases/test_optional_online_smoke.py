"""Optional live-internet smoke checks for real public test/reference sites."""
from __future__ import annotations

import time

from DrissionPage import SessionPage

from support import assert_equal, assert_in, assert_nav_result, make_browser


FEATURE_ID = 'optional_online_smoke'

REQUIRES_BROWSER = True

def run(ctx):
    if not ctx.include_online:
        ctx.skip('online smoke checks require --include-online')
        return
    if ctx.skip_browser:
        ctx.skip('online Chromium checks skipped by --skip-browser')
        return

    session_page = SessionPage()
    example = session_page.get('https://example.com/', timeout=20)
    assert_nav_result(example, status=200, ok=True, label='SessionPage example.com navigation')
    assert_in('Example Domain', session_page.html, 'SessionPage should read example.com HTML')

    httpbingo_get = session_page.get('https://httpbingo.org/get?dp=tests_cli', timeout=20)
    assert_nav_result(httpbingo_get, status=200, ok=True, label='SessionPage httpbingo /get navigation')
    httpbingo_json = httpbingo_get.Response.json()
    assert_equal(httpbingo_json['args']['dp'], ['tests_cli'], 'SessionPage should read httpbingo JSON body')
    assert_in('https://httpbingo.org/get', httpbingo_json['url'],
              'SessionPage should expose requested httpbingo URL')

    fake_api = session_page.get('https://jsonplaceholder.typicode.com/todos/1', timeout=20)
    assert_nav_result(fake_api, status=200, ok=True, label='SessionPage JSONPlaceholder navigation')
    fake_api_json = fake_api.Response.json()
    assert_equal(fake_api_json['id'], 1, 'SessionPage should read JSONPlaceholder JSON body')
    assert_equal(fake_api_json['completed'], False, 'SessionPage should preserve JSON boolean values')

    with make_browser(ctx.browser_path, page_load_timeout=20) as browser:
        tab = browser.latest_tab

        example = tab.get('https://example.com/')
        assert_nav_result(example, status=200, ok=True, label='Chromium example.com navigation')
        assert_equal(tab('x://h1', timeout=10).text, 'Example Domain',
                     'Chromium should locate example.com heading')

        httpbingo_html = tab.get('https://httpbingo.org/html')
        assert_nav_result(httpbingo_html, status=200, ok=True, label='Chromium httpbingo /html navigation')
        assert_in('Herman Melville', tab.html, 'Chromium should read httpbingo HTML body')

        redirected = tab.get('https://httpbingo.org/redirect-to?url=https%3A%2F%2Fexample.com%2F')
        assert_nav_result(redirected, status=200, ok=True, label='Chromium httpbingo redirect navigation')
        assert_in('example.com', redirected.url, 'Chromium should expose final redirected URL')
        assert_equal(tab('x://h1', timeout=10).text, 'Example Domain',
                     'Chromium should read final page after online redirect')

        selenium_form = tab.get('https://www.selenium.dev/selenium/web/web-form.html')
        assert_nav_result(selenium_form, status=200, ok=True, label='Chromium Selenium web-form navigation')
        input_ele = tab('[name="my-text"]', timeout=10)
        input_ele.input('drissionpage online smoke')
        input_value = tab.run_js('return document.querySelector("[name=\\"my-text\\"]").value;')
        assert_equal(input_value, 'drissionpage online smoke',
                     'Chromium should input text on Selenium public test form')
        tab('button', timeout=10).click()
        deadline = time.time() + 10
        while time.time() < deadline and 'submitted-form' not in tab.url:
            time.sleep(0.2)
        assert_in('submitted-form', tab.url, 'Chromium should submit Selenium public test form')
