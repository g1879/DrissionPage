"""Feature: low-risk compatibility fixes for options, element lists, JS arguments, and POST timeouts."""
from __future__ import annotations

from math import inf, nan
from time import perf_counter, sleep
from types import SimpleNamespace

from requests.adapters import HTTPAdapter

from DrissionPage import SessionOptions
from DrissionPage._elements.chromium_element import ChromiumElement, convert_argument
from DrissionPage._elements.session_element import make_session_ele
from DrissionPage._functions.elements import ChromiumElementsList, SessionElementsList
from DrissionPage._pages.chromium_tab import ChromiumTab

from support import assert_equal, assert_true, local_server

FEATURE_ID = "low_risk_bug_fixes"
FEATURES = (
    "session_options_add_adapter",
    "session_elements_text_nodes",
    "cdp_nonfinite_argument_contract",
    "tab_post_explicit_timeout",
)
REQUIRES_BROWSER = False


def run(ctx):
    _check_session_options_add_adapter()
    _check_element_list_texts()
    _check_cdp_argument_conversion()
    _check_tab_post_timeout_forwarding()
    _check_tab_post_timeout_against_slow_endpoint()


def _check_session_options_add_adapter() -> None:
    options = SessionOptions(read_file=False)
    https_adapter = HTTPAdapter()
    http_adapter = HTTPAdapter()

    assert_true(
        options.add_adapter("https://api.example/", https_adapter) is options,
        "SessionOptions.add_adapter() should be chainable on a new object",
    )
    assert_true(
        options.add_adapter("http://", http_adapter) is options,
        "SessionOptions.add_adapter() should remain chainable for repeated additions",
    )
    assert_equal(
        options.adapters,
        [("https://api.example/", https_adapter), ("http://", http_adapter)],
        "SessionOptions.add_adapter() should preserve insertion order",
    )

    session, _ = options.make_session()
    try:
        assert_true(
            session.adapters["https://api.example/"] is https_adapter,
            "make_session() should mount the configured HTTPS adapter",
        )
        assert_true(
            session.adapters["http://"] is http_adapter,
            "make_session() should mount the configured HTTP adapter",
        )
    finally:
        session.close()


def _check_element_list_texts() -> None:
    element = SimpleNamespace(text="element text")
    mixed = make_session_ele(
        "<div>leading text<span>element text</span>trailing text</div>",
        "xpath://div/node()",
        index=None,
    )

    assert_equal(SessionElementsList(None).texts, [], "empty element-list texts should remain empty")
    assert_equal(
        SessionElementsList(None, [element]).texts,
        ["element text"],
        "element-list texts should preserve existing element behavior",
    )
    assert_true(isinstance(mixed, SessionElementsList), "text-node query should return SessionElementsList")
    assert_equal(
        mixed.texts,
        ["leading text", "element text", "trailing text"],
        "element-list texts should preserve string text nodes",
    )
    assert_true(isinstance(mixed[1:], SessionElementsList), "slicing should preserve SessionElementsList")
    assert_equal(
        mixed[1:].texts,
        ["element text", "trailing text"],
        "sliced element lists should keep mixed text behavior",
    )
    assert_equal(
        ChromiumElementsList(None, [element]).texts,
        ["element text"],
        "ChromiumElementsList should preserve inherited element text behavior",
    )


def _check_cdp_argument_conversion() -> None:
    assert_equal(
        convert_argument(inf),
        {"unserializableValue": "Infinity"},
        "positive infinity should use the CDP unserializable-value field",
    )
    assert_equal(
        convert_argument(-inf),
        {"unserializableValue": "-Infinity"},
        "negative infinity should use the CDP unserializable-value field",
    )
    assert_equal(
        convert_argument(nan),
        {"unserializableValue": "NaN"},
        "NaN should use the CDP unserializable-value field",
    )
    assert_equal(
        convert_argument(-0.0),
        {"unserializableValue": "-0"},
        "negative zero should retain its sign through CDP",
    )

    for value in (0, 1.5, "text", True, {"answer": 42}):
        assert_equal(
            convert_argument(value),
            {"value": value},
            f"ordinary argument should preserve the existing value representation: {value!r}",
        )

    element = object.__new__(ChromiumElement)
    element._obj_id = "remote-object-id"
    assert_equal(
        convert_argument(element),
        {"objectId": "remote-object-id"},
        "element arguments should preserve their existing remote-object representation",
    )

    try:
        convert_argument(["unsupported"])
    except TypeError:
        pass
    else:
        raise AssertionError("unsupported argument types should continue raising TypeError")


def _check_tab_post_timeout_forwarding() -> None:
    explicit_calls = []
    explicit_tab = _make_fake_tab(explicit_calls)
    marker = explicit_tab.post(
        "https://example.test/post",
        retry=2,
        interval=0.1,
        timeout=3,
        raise_err=True,
        data="payload",
    )
    assert_equal(marker, "posted", "ChromiumTab.post() should preserve the delegated return value")
    assert_equal(explicit_calls[-1]["timeout"], 3, "ChromiumTab.post() should forward explicit timeout")
    assert_equal(explicit_calls[-1]["data"], "payload", "ChromiumTab.post() should preserve request kwargs")
    assert_equal(explicit_calls[-1]["retry"], 2, "ChromiumTab.post() should preserve retry")
    assert_equal(explicit_calls[-1]["interval"], 0.1, "ChromiumTab.post() should preserve interval")
    assert_true(explicit_calls[-1]["raise_err"] is True, "ChromiumTab.post() should preserve raise_err")

    default_calls = []
    _make_fake_tab(default_calls).post("https://example.test/post")
    assert_equal(default_calls[-1]["timeout"], 5, "ChromiumTab.post() should preserve page-load timeout default")

    zero_calls = []
    _make_fake_tab(zero_calls).post("https://example.test/post", timeout=0)
    assert_equal(zero_calls[-1]["timeout"], 0, "ChromiumTab.post() should preserve an explicit zero timeout")

    d_mode_calls = []
    d_mode_tab = _make_fake_tab(d_mode_calls, d_mode=True)
    d_mode_tab.post("https://example.test/post", timeout=4)
    assert_true(d_mode_calls[0] == "cookies", "d mode POST should continue copying browser cookies")
    assert_equal(d_mode_calls[-1]["timeout"], 4, "d mode POST should forward explicit timeout")


def _check_tab_post_timeout_against_slow_endpoint() -> None:
    def slow_post(_request):
        sleep(1)
        return 200, "text/plain; charset=utf-8", "slow", {}

    with local_server({"/slow-post": slow_post}) as base:
        tab = object.__new__(ChromiumTab)
        tab._d_mode = False
        tab._session = None
        tab._timeouts = SimpleNamespace(page_load=5)
        tab._mode_obj = SimpleNamespace(post=lambda **kwargs: ChromiumTab._s_connect(tab, mode="post", **kwargs))
        tab._url = None
        tab._response = None
        tab._headers = {}
        tab._encoding = None
        tab.retry_times = 0
        tab.retry_interval = 0
        tab._session_options = SessionOptions(read_file=False)

        start = perf_counter()
        result = tab.post(base + "/slow-post", timeout=0.1, retry=0)
        elapsed = perf_counter() - start
        try:
            assert_true(elapsed < 0.8, "ChromiumTab.post(timeout=...) should stop before the slow response")
            assert_true(bool(result) is False, "timed-out ChromiumTab.post() should return a falsey NavResult")
        finally:
            tab._session.close()


def _make_fake_tab(calls, d_mode=False):
    def post(**kwargs):
        calls.append(kwargs)
        return "posted"

    tab = object.__new__(ChromiumTab)
    tab._d_mode = d_mode
    tab._session = object()
    tab._timeouts = SimpleNamespace(page_load=5)
    tab._mode_obj = SimpleNamespace(post=post)
    tab.cookies_to_session = lambda: calls.append("cookies")
    return tab
