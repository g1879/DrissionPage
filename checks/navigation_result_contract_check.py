from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from DrissionPage._pages.navigation_result import NavigationResult, _coerce_status
from DrissionPage.items import NavigationResult as ExportedNavigationResult


def main():
    assert ExportedNavigationResult is NavigationResult

    nav = NavigationResult(url='https://example.test', loaded=True, status=204)
    assert bool(nav) is True
    assert nav.ok is True
    assert nav.http_error is False

    nav.status = 404
    assert bool(nav) is True
    assert nav.ok is False
    assert nav.http_error is True

    nav.status = None
    assert nav.ok is False
    assert nav.http_error is False

    failed = NavigationResult(url='https://example.test', loaded=False)
    assert bool(failed) is False

    assert _coerce_status(None) is None
    assert _coerce_status(0) is None
    assert _coerce_status('') is None
    assert _coerce_status('404') == 404


if __name__ == '__main__':
    main()
