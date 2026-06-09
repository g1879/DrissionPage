# -*- coding: utf-8 -*-
"""Shared local fixtures for core browser feature checks."""
from __future__ import annotations

import time

from support import binary_response, html, json_response, local_server


def core_feature_routes():
    return {
        "/": lambda req: html("<body><h1 id='home'>core fixture</h1></body>", title="core home"),
        "/api": lambda req: json_response({"ok": True, "kind": "core"}),
        "/listener": lambda req: html(
            """
            <button id='again' onclick="fetch('/api?again=1').then(r => r.json()).then(j => window.again = j.kind)">again</button>
            <script>
              window.fetchDone = false;
              fetch('/api?from=listener').then(r => r.json()).then(j => { window.fetchDone = j.kind; });
            </script>
            """,
            title="listener fixture",
        ),
        "/nav": lambda req: html(
            """
            <div id='early'>early content</div>
            <img id='slow-img' src='/slow-resource?delay=2'>
            """,
            title="navigation fixture",
        ),
        "/slow-main": lambda req: (time.sleep(1.5) or html("<body>slow main</body>", title="slow")),
        "/slow-resource": lambda req: (time.sleep(1.5) or binary_response(b"slow", "text/plain; charset=utf-8")),
        "/download-page": lambda req: html(
            "<a id='download-link' href='/download/core.txt' download>download</a>",
            title="download fixture",
        ),
        "/download/core.txt": lambda req: binary_response(
            b"download-body",
            "text/plain; charset=utf-8",
            {"Content-Disposition": "attachment; filename=server-name.txt"},
        ),
        "/page-object": lambda req: html(
            """
            <input id='action-input'>
            <button id='title-button' onclick="document.title='changed-title'; history.pushState({}, '', '#changed');">change</button>
            <iframe id='frame' src='/frame'></iframe>
            """,
            title="page object fixture",
        ),
        "/frame": lambda req: html(
            "<div id='frame-ready' style='width:90px;height:20px'>frame ready</div>",
            title="frame fixture",
        ),
        "/init": lambda req: html("<div id='init-ready'>init</div>", title="init fixture"),
        "/blocked": lambda req: html(
            """
            <script>
              window.blockStatus = 'pending';
              fetch('/blocked-data')
                .then(() => { window.blockStatus = 'loaded'; })
                .catch(() => { window.blockStatus = 'blocked'; });
            </script>
            <div id='blocked-page'>blocked check</div>
            """,
            title="blocked fixture",
        ),
        "/blocked-data": lambda req: json_response({"blocked": False}),
        "/cookies": lambda req: html("<div id='cookie-page'>cookies</div>", title="cookies fixture"),
        "/tab": lambda req: html(
            """
            <button id='alert-button' onclick="alert('tab-alert')">alert</button>
            <div id='tab-ready'>tab ready</div>
            """,
            title="tab fixture",
        ),
        "/elements": lambda req: html(
            """
            <style>
              body { margin: 0; height: 1800px; }
              #box { margin-top: 900px; width: 80px; height: 30px; background: rgb(1, 2, 3); }
            </style>
            <section id='items'>
              <p id='one' class='item' data-kind='keep'>one</p>
              <p id='two' class='item' data-kind='drop'>two</p>
              <p id='three' class='item' data-kind='keep'>three</p>
            </section>
            <label><input id='check' type='checkbox'> check</label>
            <input id='text-input'>
            <select id='choices' multiple>
              <option id='opt-a' value='a'>A</option>
              <option id='opt-b' value='b'>B</option>
            </select>
            <div id='box'>box</div>
            """,
            title="elements fixture",
        ),
    }


def core_feature_server():
    return local_server(core_feature_routes())
