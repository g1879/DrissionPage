from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
from threading import Thread
from time import perf_counter, sleep
import unittest
import warnings

from DrissionPage import Chromium, ChromiumOptions
from DrissionPage.errors import WaitTimeoutError


warnings.filterwarnings('ignore', category=ResourceWarning)


class QuietThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        error = sys.exc_info()[1]
        if isinstance(error, (BrokenPipeError, ConnectionResetError, OSError)):
            return
        super().handle_error(request, client_address)


class SSEHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    child_base = None

    def do_GET(self):
        path = self.path.split('?', 1)[0]

        pages = {
            '/page-basic': """
                <!doctype html><meta charset="utf-8">
                <script>
                window.basic = new EventSource('/sse-basic');
                window.hitApi = () => fetch('/api').then(r => r.json());
                </script>
                basic
            """,
            '/page-filter': """
                <!doctype html><meta charset="utf-8">
                <script>
                window.target = new EventSource('/sse-target');
                window.ignore = new EventSource('/sse-ignore');
                </script>
                filter
            """,
            '/page-multi': """
                <!doctype html><meta charset="utf-8">
                <script>
                window.alpha = new EventSource('/sse-alpha');
                window.beta = new EventSource('/sse-beta');
                </script>
                multi
            """,
            '/page-regex': """
                <!doctype html><meta charset="utf-8">
                <script>
                window.regex = new EventSource('/sse-regex-42');
                window.hitApi = () => fetch('/api').then(r => r.json());
                </script>
                regex
            """,
            '/page-restart-a': """
                <!doctype html><meta charset="utf-8">
                <script>window.restartA = new EventSource('/sse-restart-a');</script>
                restart-a
            """,
            '/page-restart-b': """
                <!doctype html><meta charset="utf-8">
                <script>window.restartB = new EventSource('/sse-restart-b');</script>
                restart-b
            """,
            '/page-delayed': """
                <!doctype html><meta charset="utf-8">
                <script>window.delayed = new EventSource('/sse-delayed');</script>
                delayed
            """,
            '/page-missing-stream': """
                <!doctype html><meta charset="utf-8">
                <script>window.missing = new EventSource('/sse-missing');</script>
                missing-stream
            """,
        }

        if path in pages:
            self._send_html(pages[path])
            return

        if path == '/page-iframe':
            self._send_html(f"""
                <!doctype html><meta charset="utf-8">
                <iframe src="{self.child_base}/iframe-child"></iframe>
                iframe
            """)
            return

        if path == '/iframe-child':
            self._send_html("""
                <!doctype html><meta charset="utf-8">
                <script>window.iframeSSE = new EventSource('/sse-iframe');</script>
                child
            """)
            return

        if path == '/api':
            body = json.dumps({'ok': True, 'text': '普通请求'}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        streams = {
            '/sse-basic': (
                ('event: greet\nid: 1\ndata: 你好\n\n', 0.05),
                ('data: world\n\n', 0.05),
                ('event: done\nid: 2\ndata: 再见\n\n', 0.05),
            ),
            '/sse-target': (
                ('event: target\nid: t1\ndata: target-1\n\n', 0.05),
                ('event: target\nid: t2\ndata: target-2\n\n', 0.05),
            ),
            '/sse-ignore': (
                ('event: ignore\nid: i1\ndata: ignore-1\n\n', 0.05),
                ('event: ignore\nid: i2\ndata: ignore-2\n\n', 0.05),
            ),
            '/sse-alpha': (('event: alpha\nid: a1\ndata: alpha-1\n\n', 0.05),),
            '/sse-beta': (('event: beta\nid: b1\ndata: beta-1\n\n', 0.05),),
            '/sse-regex-42': (('event: regex\nid: r1\ndata: regex-ok\n\n', 0.05),),
            '/sse-restart-a': (('event: restart\nid: old\ndata: restart-a\n\n', 0.05),),
            '/sse-restart-b': (('event: restart\nid: new\ndata: restart-b\n\n', 0.05),),
            '/sse-delayed': (
                ('event: delayed\nid: d1\ndata: delayed-1\n\n', 1.0),
                ('event: delayed\nid: d2\ndata: delayed-2\n\n', 0.05),
            ),
            '/sse-iframe': (('event: iframe\nid: f1\ndata: iframe-ok\n\n', 0.05),),
        }

        if path in streams:
            self._send_sse(streams[path])
            return

        self.send_response(404)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _send_html(self, html):
        body = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_sse(self, chunks):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        try:
            for chunk, delay_after in chunks:
                self.wfile.write(chunk.encode('utf-8'))
                self.wfile.flush()
                sleep(delay_after)

            end = perf_counter() + 1.5
            while perf_counter() < end:
                self.wfile.write(b': keepalive\n\n')
                self.wfile.flush()
                sleep(0.5)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def log_message(self, *_):
        pass


@contextmanager
def local_server(handler=SSEHandler):
    server = QuietThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown()
        server.server_close()


@contextmanager
def make_tab():
    co = ChromiumOptions(read_file=False)
    co.auto_port()
    co.headless(True)
    co.set_load_mode('normal')
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-gpu')
    browser = Chromium(addr_or_opts=co)
    try:
        yield browser.latest_tab
    finally:
        browser.quit()


class TestListenerSSE(unittest.TestCase):
    def test_wait_sse_receives_event_fields_utf8_and_raw_data(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-basic')
            self.assertTrue(page.get(base + '/page-basic'))

            first = page.listen.wait_sse(timeout=5)
            second = page.listen.wait_sse(timeout=5)

            self.assertEqual(first.url, base + '/sse-basic')
            self.assertEqual(first.eventName, 'greet')
            self.assertEqual(first.eventId, '1')
            self.assertEqual(first.data, '你好')
            self.assertEqual(second.eventName, 'message')
            self.assertEqual(second.data, 'world')
            self.assertEqual(first.requestId, second.requestId)
            self.assertIsInstance(first.timestamp, float)
            self.assertEqual(first.raw_data['data'], '你好')
            self.assertIsNone(first.not_a_cdp_field)
            self.assertIn('SSEMessage', repr(first))

    def test_wait_sse_count_returns_ordered_message_list(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-basic')
            self.assertTrue(page.get(base + '/page-basic'))

            messages = page.listen.wait_sse(count=3, timeout=5)

            self.assertEqual([m.data for m in messages], ['你好', 'world', '再见'])
            self.assertEqual([m.eventName for m in messages], ['greet', 'message', 'done'])

    def test_sse_steps_returns_gap_batches(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-basic')
            self.assertTrue(page.get(base + '/page-basic'))

            batch = next(page.listen.sse_steps(count=2, timeout=5, gap=2))

            self.assertEqual([m.data for m in batch], ['你好', 'world'])

    def test_start_sse_filters_single_target(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-target')
            self.assertTrue(page.get(base + '/page-filter'))

            messages = page.listen.wait_sse(count=2, timeout=5)

            self.assertEqual([m.data for m in messages], ['target-1', 'target-2'])
            self.assertTrue(all('/sse-target' in m.url for m in messages))
            self.assertTrue(all(m.eventName == 'target' for m in messages))

    def test_start_sse_accepts_multiple_targets(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse(('/sse-alpha', '/sse-beta'))
            self.assertTrue(page.get(base + '/page-multi'))

            messages = page.listen.wait_sse(count=2, timeout=5)

            self.assertEqual({m.data for m in messages}, {'alpha-1', 'beta-1'})
            self.assertEqual({m.eventName for m in messages}, {'alpha', 'beta'})

    def test_start_sse_targets_true_captures_all_event_sources(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse(True)
            self.assertTrue(page.get(base + '/page-filter'))

            messages = page.listen.wait_sse(count=4, timeout=5)

            self.assertEqual(
                {m.data for m in messages},
                {'target-1', 'target-2', 'ignore-1', 'ignore-2'},
            )

    def test_start_sse_accepts_regex_target(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse(r'/sse-regex-\d+', is_regex=True)
            self.assertTrue(page.get(base + '/page-regex'))

            message = page.listen.wait_sse(timeout=5)

            self.assertEqual(message.data, 'regex-ok')
            self.assertEqual(message.eventId, 'r1')

    def test_start_sse_restarts_and_clears_previous_queue(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-restart-a')
            self.assertTrue(page.get(base + '/page-restart-a'))
            page.listen.wait_sse(timeout=5)

            page.listen.start_sse('/sse-restart-b')
            self.assertTrue(page.get(base + '/page-restart-b'))
            message = page.listen.wait_sse(timeout=5)

            self.assertEqual(message.data, 'restart-b')
            self.assertFalse(page.listen.wait_sse(timeout=0.3))

    def test_wait_sse_fit_count_false_returns_partial_messages(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-delayed')
            self.assertTrue(page.get(base + '/page-delayed'))

            messages = page.listen.wait_sse(count=2, timeout=0.4, fit_count=False)

            self.assertEqual([m.data for m in messages], ['delayed-1'])

    def test_wait_sse_timeout_returns_false_when_no_message_arrives(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-missing')
            self.assertTrue(page.get(base + '/page-missing-stream'))

            self.assertFalse(page.listen.wait_sse(timeout=0.5))

    def test_wait_sse_raise_err_raises_wait_timeout_error(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-missing')
            self.assertTrue(page.get(base + '/page-missing-stream'))

            with self.assertRaises(WaitTimeoutError):
                page.listen.wait_sse(timeout=0.5, raise_err=True)

    def test_wait_sse_requires_sse_mode(self):
        with local_server() as base, make_tab() as page:
            page.listen.start('/api')
            self.assertTrue(page.get(base + '/page-basic'))

            with self.assertRaises(RuntimeError):
                page.listen.wait_sse(timeout=0.2)

    def test_pause_clear_makes_wait_sse_unavailable_until_restarted(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse('/sse-basic')
            page.listen.pause(clear=True)
            self.assertTrue(page.get(base + '/page-basic'))

            with self.assertRaises(RuntimeError):
                page.listen.wait_sse(timeout=0.2)

            page.listen.start_sse('/sse-basic')
            self.assertTrue(page.get(base + '/page-basic'))
            self.assertEqual(page.listen.wait_sse(timeout=5).data, '你好')

    def test_normal_listener_still_returns_datapacket_after_sse(self):
        with local_server() as base, make_tab() as page:
            page.listen.start_sse(r'/sse-regex-\d+', is_regex=True)
            self.assertTrue(page.get(base + '/page-regex'))
            self.assertEqual(page.listen.wait_sse(timeout=5).data, 'regex-ok')

            page.listen.stop()
            page.listen.start('/api')
            page.run_js('return window.hitApi();')
            packet = page.listen.wait(timeout=5)

            self.assertEqual(packet.url, base + '/api')
            self.assertEqual(packet.response.body, {'ok': True, 'text': '普通请求'})

    def test_tab_listener_captures_cross_origin_iframe_sse(self):
        with local_server() as child_base:
            class ParentHandler(SSEHandler):
                pass

            ParentHandler.child_base = child_base

            with local_server(ParentHandler) as parent_base, make_tab() as page:
                page.listen.start_sse('/sse-iframe')
                self.assertTrue(page.get(parent_base + '/page-iframe'))

                message = page.listen.wait_sse(timeout=5)

                self.assertEqual(message.data, 'iframe-ok')
                self.assertEqual(message.eventName, 'iframe')
                self.assertTrue(message.url.startswith(child_base))


if __name__ == '__main__':
    unittest.main(verbosity=2, warnings='ignore')
