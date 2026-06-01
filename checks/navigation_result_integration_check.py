from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.items import NavigationResult


class Handler(BaseHTTPRequestHandler):
    frame_url = None

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/ok':
            self._send(200, b'<html><title>ok</title><body>ok</body></html>')
        elif path == '/missing':
            self._send(404, b'<html><title>missing</title><body>missing</body></html>')
        elif path == '/error':
            self._send(500, b'<html><title>error</title><body>error</body></html>')
        elif path == '/redirect':
            self.send_response(302)
            self.send_header('Location', '/final')
            self.end_headers()
        elif path == '/final':
            self._send(200, b'<html><title>final</title><body>final</body></html>')
        elif path == '/asset.js':
            self._send(200, b'console.log("asset");', content_type='text/javascript')
        elif path == '/with-assets':
            self._send(200, b'<html><head><script src="/asset.js"></script></head><body>assets</body></html>')
        elif path == '/iframe-host':
            target = Handler.frame_url or '/ok'
            body = f'<html><body><iframe id="frame" src="{target}"></iframe></body></html>'.encode()
            self._send(200, body)
        elif path == '/frame-start':
            self._send(200, b'<html><body>frame start</body></html>')
        elif path == '/frame-final':
            self._send(200, b'<html><body>frame final</body></html>')
        elif path == '/slow':
            time.sleep(2)
            self._send(200, b'<html><body>slow</body></html>')
        else:
            self._send(404, b'unknown')

    def _send(self, status, body, content_type='text/html'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@contextmanager
def server():
    srv = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{srv.server_port}'
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join(timeout=2)


def make_page(tmp_dir):
    co = ChromiumOptions().auto_port().headless()
    co.set_browser_path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    co.set_user_data_path(str(tmp_dir / 'profile'))
    co.set_argument('--no-first-run')
    co.set_argument('--disable-gpu')
    co.set_argument('--no-default-browser-check')
    return ChromiumPage(co)


def assert_status(nav, status):
    assert nav.loaded is True
    assert nav.status in (status, None)
    if nav.status is not None:
        assert nav.from_performance is True


def check_cross_origin_frame(tmp_dir):
    with server() as parent_base, server() as frame_base:
        Handler.frame_url = frame_base + '/frame-start'
        page = make_page(tmp_dir / 'cross_profile')
        try:
            assert page.get(parent_base + '/iframe-host') is True
            frame = page.get_frame(1, timeout=5)
            assert frame.get(frame_base + '/frame-final') is True
            nav = frame.get(frame_base + '/slow', timeout=.5, retry=0, show_errmsg=False, return_info=True)
            assert isinstance(nav, NavigationResult)
            assert nav.loaded is False
            assert nav.final_url is None
            assert nav.status is None
        finally:
            page.quit(force=True, del_data=True)
            Handler.frame_url = None


def main():
    with tempfile.TemporaryDirectory() as tmp, server() as base:
        tmp_dir = Path(tmp)
        page = make_page(tmp_dir / 'main_profile')
        try:
            assert page.get(base + '/ok') is True
            assert page.url_available is True

            nav = page.get(base + '/ok', return_info=True)
            assert isinstance(nav, NavigationResult)
            assert bool(nav) is True
            assert nav.loaded is True
            assert page.url_available is True
            assert nav.final_url.endswith('/ok')
            assert_status(nav, 200)
            if nav.status is not None:
                assert nav.ok is True
                assert nav.http_error is False

            nav = page.get(base + '/missing', return_info=True)
            assert bool(nav) is True
            assert_status(nav, 404)
            if nav.status is not None:
                assert nav.ok is False
                assert nav.http_error is True

            nav = page.get(base + '/error', return_info=True)
            assert bool(nav) is True
            assert_status(nav, 500)
            if nav.status is not None:
                assert nav.http_error is True

            nav = page.get(base + '/redirect', return_info=True)
            assert bool(nav) is True
            assert nav.final_url.endswith('/final')
            assert nav.status in (200, None)

            nav = page.get(base + '/slow', timeout=.5, retry=0, show_errmsg=False, return_info=True)
            assert isinstance(nav, NavigationResult)
            assert nav.loaded is False
            assert bool(nav) is False
            assert nav.final_url is None
            assert page.url_available is False

            original_mode = page._load_mode
            try:
                page._load_mode = 'none'
                nav = page.get(base + '/ok', retry=0, return_info=True)
                assert isinstance(nav, NavigationResult)
                assert nav.loaded is True
                assert bool(nav) is True
                assert nav.status is None
                assert nav.from_performance is False
            finally:
                page._load_mode = original_mode

            page.listen.start(targets=True)
            nav = page.get(base + '/with-assets', return_info=True)
            assert isinstance(nav, NavigationResult)
            assert nav.loaded is True
            assert page.listen.listening is True
            assert page.listen.wait(timeout=3, fit_count=False) is not False
            page.listen.stop()

            page.get(base + '/iframe-host')
            frame = page.get_frame(1, timeout=3)
            assert frame.get(base + '/frame-start') is True
            nav = frame.get(base + '/frame-final', return_info=True)
            assert isinstance(nav, NavigationResult)
            assert nav.loaded is True
            assert nav.final_url.endswith('/frame-final')
            assert_status(nav, 200)

            nav = frame.get(base + '/slow', timeout=.5, retry=0, show_errmsg=False, return_info=True)
            assert isinstance(nav, NavigationResult)
            assert nav.loaded is False
            assert nav.final_url is None
            assert nav.status is None
        finally:
            page.quit(force=True, del_data=True)

        check_cross_origin_frame(tmp_dir)


if __name__ == '__main__':
    main()
