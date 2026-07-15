# -*- coding: utf-8 -*-
"""Shared local fixtures for browser interaction feature checks."""
from __future__ import annotations

from support import html, json_response, local_server


def browser_interaction_routes():
    return {
        "/main": lambda req: html(
            """
            <style>
              body { margin: 0; height: 2200px; }
              #fixed { position: fixed; top: 0; left: 0; right: 0; height: 32px; background: rgba(0,0,0,.1); }
              #clicker { position: absolute; top: 120px; left: 40px; width: 120px; height: 40px; }
              #moving { position: absolute; top: 420px; left: 20px; width: 120px; height: 30px; background: #def; }
              #scroll-target { margin-top: 1400px; height: 80px; background: #dfd; }
            </style>
            <div id='fixed'>fixed</div>
            <link id='asset-link' rel='stylesheet' href='/asset.txt'>
            <button id='primary'>primary</button>
            <button id='secondary'>secondary</button>
            <input id='text-input'>
            <button id='clicker'
                    onclick='window.clickCount=(window.clickCount||0)+1; window.clickDetails=(window.clickDetails||[]).concat(event.detail);'
                    ondblclick='window.doubleClickCount=(window.doubleClickCount||0)+1; window.doubleClickDetails=(window.doubleClickDetails||[]).concat(event.detail);'>click me</button>
            <select id='chooser'><option value='a'>A</option><option value='b'>B</option></select>
            <div id='scroll-target'>scroll target</div>
            <div id='moving'>moving</div>
            <div id='host'></div>
            <iframe id='child-frame' src='/frame'></iframe>
            <script>
              document.cookie = 'client_cookie=browser; path=/';
              window.clickCount = 0;
              window.doubleClickCount = 0;
              window.clickDetails = [];
              window.doubleClickDetails = [];
              const host = document.querySelector('#host');
              const shadow = host.attachShadow({mode:'open'});
              shadow.innerHTML = '<button id="shadow-btn" data-role="shadow">Shadow Button</button>';
              setTimeout(() => { document.body.setAttribute('data-late', 'ready'); }, 120);
            </script>
            """,
            title="browser interaction main",
        ),
        "/frame": lambda req: html(
            """
            <a id='frame-link' href='/asset.txt'>frame asset</a>
            <div id='frame-child'>frame child</div>
            <script>document.body.setAttribute('data-frame-ready', 'yes');</script>
            """,
            title="browser interaction frame",
        ),
        "/asset.txt": lambda req: (200, "text/plain; charset=utf-8", "asset-content", {}),
        "/post": lambda req: json_response({
            "method": "POST",
            "body": getattr(req, "_cached_body", None)
            or req.rfile.read(int(req.headers.get("Content-Length") or 0)).decode("utf-8", "replace"),
        }),
    }


def browser_interaction_server():
    return local_server(browser_interaction_routes())
