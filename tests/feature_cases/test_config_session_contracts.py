"""Feature: configuration, session option, and session element contracts."""
from __future__ import annotations

from configparser import NoSectionError
from pathlib import Path
from tempfile import TemporaryDirectory

from requests import Session

from DrissionPage import ChromiumOptions, SessionOptions
from DrissionPage._configs.options_manage import OptionsManager
from DrissionPage._elements.none_element import NoneElement
from DrissionPage._elements.session_element import SessionElement, make_session_ele
from DrissionPage._functions.elements import SessionElementsList
from DrissionPage.errors import ElementNotFoundError, LocatorError

from support import assert_equal, assert_false, assert_in, assert_true


FEATURE_ID = "config_session_contracts"
REQUIRES_BROWSER = False


DOCUMENT = """
<html>
  <body>
    <main id="root">
      <section class="group" data-state="ready">
        <article id="first" class="item featured" data-rank="1">
          <h2>Alpha</h2><a href="/alpha">First link</a>
        </article>
        <!-- stable marker -->
        <article id="second" class="item" data-rank="2">
          <h2>Beta</h2><a href="https://example.test/beta">Second link</a>
        </article>
        <p id="tail">Tail <b>bold</b></p>
      </section>
    </main>
  </body>
</html>
"""


def run(ctx):
    with TemporaryDirectory(prefix="dp-config-contracts-") as tmp:
        root = Path(tmp)
        _check_chromium_options(root)
        _check_session_options(root)
        _check_options_manager(root)
    _check_session_elements()
    _check_none_element()


def _check_chromium_options(root: Path) -> None:
    options = ChromiumOptions(read_file=False)
    assert_true(options.set_retry(4, 0.25) is options, "set_retry() should be chainable")
    assert_true(options.clear_arguments() is options, "clear_arguments() should be chainable")
    assert_true(options.set_argument("--contract", "enabled") is options, "set_argument() should be chainable")
    assert_true(options.headless() is options, "headless() should be chainable")
    assert_true(options.set_user("Contract Profile") is options, "set_user() should be chainable")
    assert_true(options.set_timeouts(2, 3, 4) is options, "set_timeouts() should be chainable")
    assert_true(options.set_load_mode("eager") is options, "set_load_mode() should be chainable")
    assert_true(options.set_address("http://localhost:9333") is options, "set_address() should be chainable")
    assert_true(options.set_browser_path(root / "browser") is options, "set_browser_path() should be chainable")
    assert_true(options.set_download_path(root / "downloads") is options, "set_download_path() should be chainable")
    assert_true(options.set_tmp_path(root / "tmp") is options, "set_tmp_path() should be chainable")
    assert_true(options.set_user_data_path(root / "profile") is options, "set_user_data_path() should be chainable")
    assert_true(options.set_cache_path(root / "cache") is options, "set_cache_path() should be chainable")
    assert_true(options.set_pref("contract.nested", {"enabled": True}) is options, "set_pref() should be chainable")
    assert_true(options.set_flag("contract-flag", "on") is options, "set_flag() should be chainable")
    assert_true(options.new_env().existing_only() is options, "environment setters should remain fluent")

    assert_equal(options.retry_times, 4, "retry count should be stored")
    assert_equal(options.retry_interval, 0.25, "retry interval should be stored")
    assert_equal(options.timeouts, {"base": 2, "page_load": 3, "script": 4}, "timeouts should be stored")
    assert_equal(options.load_mode, "eager", "load mode should be stored")
    assert_equal(options.address, "127.0.0.1:9333", "localhost address should be normalized")
    assert_true(options.is_headless, "headless() should update is_headless")
    assert_equal(options.user, "Contract Profile", "profile name should be stored")
    assert_in("--contract=enabled", options.arguments, "argument values should be serialized into the argument")
    assert_in(f"--disk-cache-dir={root / 'cache'}", options.arguments, "cache path should become an argument")
    assert_equal(options.preferences["contract.nested"], {"enabled": True}, "nested preferences should be stored")
    assert_equal(options.flags["contract-flag"], "on", "flag values should be stored")
    assert_true(options.is_existing_only, "existing_only() should update its public state")

    ini_path = root / "chromium.ini"
    saved = options.save(ini_path)
    assert_equal(Path(saved), ini_path.resolve(), "save(path) should return the resolved ini path")
    loaded = ChromiumOptions(ini_path=ini_path)
    assert_equal(loaded.address, options.address, "address should round-trip through ini")
    assert_equal(loaded.browser_path, options.browser_path, "browser path should round-trip through ini")
    assert_equal(loaded.download_path, options.download_path, "download path should round-trip through ini")
    assert_equal(loaded.tmp_path, options.tmp_path, "temporary path should round-trip through ini")
    assert_equal(loaded.timeouts, options.timeouts, "timeouts should round-trip through ini")
    assert_equal((loaded.retry_times, loaded.retry_interval), (4, 0.25), "retry settings should round-trip through ini")
    assert_equal(loaded.load_mode, "eager", "load mode should round-trip through ini")
    assert_in("--contract=enabled", loaded.arguments, "arguments should round-trip through ini")
    assert_equal(loaded.preferences["contract.nested"], {"enabled": True}, "preferences should round-trip through ini")
    assert_equal(loaded.flags["contract-flag"], "on", "flags should round-trip through ini")

    auto = ChromiumOptions(read_file=False).auto_port(scope=root)
    assert_true(auto.is_auto_port, "auto_port(scope) should enable automatic port selection")
    assert_equal(Path(auto.is_auto_port), root, "auto_port(scope) should retain the requested scope")
    assert_equal(auto.address, "", "auto_port() should clear a fixed debugger address")
    assert_true(auto.auto_port(False) is auto, "auto_port(False) should be chainable")
    assert_false(auto.is_auto_port, "auto_port(False) should disable automatic port selection")

    mutable = ChromiumOptions(read_file=False).clear_arguments().clear_prefs().clear_flags()
    mutable.set_argument("--remove-me").set_pref("remove.me", 1).set_flag("remove-me", 1)
    assert_true(mutable.remove_argument("--remove-me") is mutable, "remove_argument() should be chainable")
    assert_true(mutable.remove_pref("remove.me") is mutable, "remove_pref() should be chainable")
    assert_true(mutable.set_flag("remove-me", False) is mutable, "set_flag(False) should be chainable")
    assert_equal((mutable.arguments, mutable.preferences, mutable.flags), ([], {}, {}), "removers should clear values")
    _expect_error(ValueError, lambda: options.set_load_mode("invalid"), "invalid load modes should be rejected")


def _check_session_options(root: Path) -> None:
    options = SessionOptions(read_file=False)
    assert_true(options.set_headers({"X-Contract": "yes", "Accept": "text/plain"}) is options,
                "set_headers() should be chainable")
    assert_true(options.set_a_header("X-Extra", "two") is options, "set_a_header() should be chainable")
    assert_true(options.remove_a_header("accept") is options, "remove_a_header() should be chainable")
    assert_true(options.set_cookies({"token": "abc"}) is options, "set_cookies() should be chainable")
    assert_true(options.set_auth(("user", "pass")) is options, "set_auth() should be chainable")
    assert_true(options.set_params({"page": "1"}) is options, "set_params() should be chainable")
    assert_true(options.set_verify(True) is options, "set_verify() should be chainable")
    assert_true(options.set_cert("cert.pem") is options, "set_cert() should be chainable")
    assert_true(options.set_stream(True) is options, "set_stream() should be chainable")
    assert_true(options.set_trust_env(True) is options, "set_trust_env() should be chainable")
    assert_true(options.set_max_redirects(7) is options, "set_max_redirects() should be chainable")
    assert_true(options.set_proxies("http://proxy.test", "https://proxy.test") is options,
                "set_proxies() should be chainable")
    assert_true(options.set_timeout(8) is options, "set_timeout() should be chainable")
    assert_true(options.set_download_path(root / "session-downloads") is options,
                "set_download_path() should be chainable")
    assert_true(options.set_retry(5, 0.1) is options, "set_retry() should be chainable")

    assert_equal(options.headers, {"x-contract": "yes", "x-extra": "two"},
                 "headers should be normalized case-insensitively")
    assert_equal(options.cookies, [{"name": "token", "value": "abc"}], "cookie mappings should be normalized")
    assert_equal(options.proxies, {"http": "http://proxy.test", "https": "https://proxy.test"},
                 "both proxy schemes should be stored")
    assert_equal((options.timeout, options.retry_times, options.retry_interval), (8, 5, 0.1),
                 "session timing values should be stored")

    session, headers = options.make_session()
    assert_equal(headers["X-Contract"], "yes", "make_session() should return case-insensitive headers")
    assert_equal(session.cookies.get_dict(), {"token": "abc"}, "make_session() should install cookies")
    assert_equal(session.auth, ("user", "pass"), "make_session() should install authentication")
    assert_equal(session.params, {"page": "1"}, "make_session() should install query parameters")
    assert_equal(session.proxies, options.proxies, "make_session() should install proxies")
    assert_true(session.verify and session.stream and session.trust_env, "make_session() should install boolean options")
    assert_equal((session.cert, session.max_redirects), ("cert.pem", 7), "make_session() should install request limits")

    ini_path = root / "session.ini"
    saved = options.save(ini_path)
    assert_equal(Path(saved), ini_path.resolve(), "SessionOptions.save(path) should return the resolved ini path")
    loaded = SessionOptions(ini_path=ini_path)
    expected = options.as_dict()
    assert_equal(loaded.as_dict(), expected, "serializable session options should round-trip through ini")
    assert_equal((loaded.retry_times, loaded.retry_interval), (5, 0.1), "retry settings should round-trip through ini")

    source = Session()
    source.headers["X-Origin"] = "source"
    source.auth = ("origin", "secret")
    source.params = {"from": "session"}
    copied = SessionOptions(read_file=False)
    assert_true(copied.from_session(source) is copied, "from_session() should be chainable")
    assert_equal(copied.headers["X-Origin"], "source", "from_session() should retain session headers")
    assert_equal(copied.auth, source.auth, "from_session() should retain authentication")
    assert_equal(copied.params, source.params, "from_session() should retain query parameters")

    assert_true(options.set_headers(None) is options, "set_headers(None) should be chainable")
    assert_equal(options.headers, {}, "set_headers(None) should reset headers to an empty mapping")
    assert_true(options.set_download_path(None) is options, "set_download_path(None) should be chainable")
    assert_equal(options.download_path, ".", "a missing session download path should fall back to the current directory")


def _check_options_manager(root: Path) -> None:
    manager = OptionsManager(False)
    assert_false(manager.file_exists, "OptionsManager(False) should start without a backing file")
    assert_equal(manager.get_value("timeouts", "base"), 10, "default numeric values should be parsed")
    assert_equal(manager.get_value("paths", "download_path"), "", "plain strings should remain strings")
    assert_equal(manager.get_value("timeouts", "missing"), None, "missing options should return None")
    assert_true(manager.set_item("others", "contract", {"items": [1, 2]}) is manager,
                "set_item() should be chainable")
    assert_equal(manager.get_value("others", "contract"), {"items": [1, 2]}, "structured values should be parsed")
    assert_true(manager.remove_item("others", "contract") is manager, "remove_item() should be chainable")
    assert_equal(manager.get_value("others", "contract"), None, "removed values should fall back to None")
    _expect_error(NoSectionError, lambda: manager.get_value("missing", "item"),
                  "missing sections should preserve configparser's error")

    manager.set_item("others", "contract", {"items": [1, 2]})
    manager_dir = root / "manager"
    manager_dir.mkdir()
    saved = manager.save(manager_dir)
    assert_equal(Path(saved), (manager_dir / "config.ini").resolve(),
                 "saving to a directory should create config.ini")
    reloaded = OptionsManager(saved)
    assert_true(reloaded.file_exists, "a saved manager should report an existing file")
    assert_equal(reloaded.get_value("others", "contract"), {"items": [1, 2]},
                 "OptionsManager values should round-trip through ini")
    assert_equal(reloaded.others["contract"], {"items": [1, 2]}, "section attribute access should return parsed values")


def _check_session_elements() -> None:
    root = make_session_ele(DOCUMENT)
    assert_true(isinstance(root, SessionElement), "inline HTML should produce a SessionElement")
    assert_equal(root.tag, "html", "the document root should be the html element")

    first = make_session_ele(DOCUMENT, "#first")
    assert_equal((first.tag, first.attr("id"), first.attr("data-rank")), ("article", "first", "1"),
                 "id locators should expose tags and attributes")
    assert_in("Alpha", first.text, "element text should include descendant text")
    assert_in("First link", first.raw_text, "raw_text should include descendant text")
    assert_in("class=\"item featured\"", first.html, "html should serialize attributes")
    assert_in("<h2>Alpha</h2>", first.inner_html, "inner_html should serialize descendants")
    assert_in("article", first.xpath, "xpath should identify the element")
    assert_in("article", first.css_selector, "css_selector should identify the element")

    css_items = make_session_ele(DOCUMENT, ("css selector", "article.item"), index=None)
    xpath_items = make_session_ele(DOCUMENT, ("xpath", "//article"), index=None)
    assert_true(isinstance(css_items, SessionElementsList), "index=None should return SessionElementsList")
    assert_equal([item.attr("id") for item in css_items], ["first", "second"],
                 "CSS list lookup should preserve document order")
    assert_equal([item.attr("id") for item in xpath_items], ["first", "second"],
                 "XPath list lookup should preserve document order")
    assert_equal(make_session_ele(DOCUMENT, "css:article.item", index=-1).attr("id"), "second",
                 "negative indexes should select from the end")
    assert_equal(make_session_ele(DOCUMENT, "text:Beta").tag, "h2", "explicit text lookup should find text hosts")
    assert_equal(make_session_ele(DOCUMENT, "tag:article", index=None), xpath_items,
                 "tag lookup should return the same articles as XPath")
    assert_equal(list(make_session_ele(DOCUMENT, "xpath://article/@id", index=None)), ["first", "second"],
                 "XPath attribute lists should preserve scalar results")
    assert_equal(make_session_ele(DOCUMENT, "xpath:count(//article)"), 2.0,
                 "scalar XPath expressions should return their scalar result")

    section = make_session_ele(DOCUMENT, "css:section.group")
    second = section(("xpath", "./article"), index=2)
    assert_equal(second.attr("id"), "second", "SessionElement.__call__ should support XPath tuple locators")
    assert_equal(section.child(("xpath", "./article"), index=1), first,
                 "child() should support explicit XPath tuple locators")
    assert_equal([item.attr("id") for item in section.children(("xpath", "./article"))], ["first", "second"],
                 "children() should support explicit XPath tuple locators")
    assert_equal(first.parent(("xpath", "//section")).attr("class"), "group",
                 "parent() should support explicit XPath tuple locators")
    assert_equal(first.next().attr("id"), "second", "next() should find the next element sibling")
    assert_equal(second.prev().attr("id"), "first", "prev() should find the previous element sibling")
    assert_equal([item.attr("id") for item in first.nexts()], ["second", "tail"],
                 "nexts() should return later element siblings")
    assert_equal(section.child_count, 3, "child_count should count element children")
    assert_equal(len(section.comments), 1, "comments should expose comment nodes")

    missing = make_session_ele(DOCUMENT, "css:.missing", method="contract_lookup")
    assert_true(isinstance(missing, NoneElement), "missing indexed lookups should return NoneElement")
    assert_false(missing, "NoneElement should be false-like")
    assert_equal(missing, None, "NoneElement should compare equal to None")
    assert_equal(missing.method, "contract_lookup", "NoneElement should preserve method metadata")
    assert_equal(missing.args["locator"], "css:.missing", "NoneElement should preserve locator metadata")
    assert_equal(make_session_ele(DOCUMENT, "css:.missing", index=None), [],
                 "missing list lookups should return an empty collection")

    _expect_error(LocatorError, lambda: make_session_ele(DOCUMENT, "xpath:???"),
                  "invalid XPath should raise LocatorError")
    _expect_error(LocatorError, lambda: make_session_ele(DOCUMENT, "css:???"),
                  "invalid CSS should raise LocatorError")
    _expect_error(ValueError, lambda: make_session_ele(DOCUMENT, "ax:@name=Alpha"),
                  "SessionElement should reject unsupported accessibility locators")
    _expect_error(LocatorError, lambda: make_session_ele(DOCUMENT, object()),
                  "unsupported locator types should raise LocatorError")


def _check_none_element() -> None:
    plain = NoneElement(method="missing", args={"locator": "#none"})
    assert_false(plain, "a plain NoneElement should be false-like")
    assert_equal(plain, None, "a plain NoneElement should compare equal to None")
    assert_in("method=missing", repr(plain), "repr should include method metadata")
    _expect_error(ElementNotFoundError, lambda: plain.text,
                  "accessing a value on a plain NoneElement should raise ElementNotFoundError")
    _expect_error(ElementNotFoundError, lambda: plain(),
                  "calling a plain NoneElement should raise ElementNotFoundError")

    class FallbackOwner:
        _none_ele_value = "fallback"
        _none_ele_return_value = True

    fallback = NoneElement(FallbackOwner(), method="missing", args={"locator": "#none"})
    assert_equal(fallback.text, "fallback", "configured NoneElement values should provide a safe fallback")
    assert_equal(fallback.attr, "fallback", "configured NoneElement methods should provide the fallback value")
    assert_true(fallback.ele("#nested") is fallback, "configured NoneElement traversal should remain chainable")
    assert_true(fallback() is fallback, "configured NoneElement calls should remain chainable")
    _expect_error(ElementNotFoundError, lambda: fallback.unknown,
                  "unsupported fallback attributes should still raise ElementNotFoundError")


def _expect_error(error_type, action, message: str) -> None:
    try:
        action()
    except error_type:
        return
    except Exception as exc:
        raise AssertionError(f"{message}: expected {error_type.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"{message}: expected {error_type.__name__}")
