# -*- coding:utf-8 -*-
"""
@Author   : jumodada
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class NavigationResult(object):
    url: str
    loaded: bool
    final_url: Optional[str] = None
    status: Optional[int] = None
    from_performance: bool = False

    def __bool__(self):
        return self.loaded

    @property
    def ok(self):
        return self.status is not None and 200 <= self.status <= 299

    @property
    def http_error(self):
        return self.status is not None and self.status >= 400


_JS_STATUS = """
(() => performance.getEntriesByType('navigation').map(entry => entry.responseStatus || 0))()
"""


def make_navigation_result(page, url, loaded):
    frame_info = frame_tree_info(page)
    status = (navigation_status_from_performance(page)
              if loaded and getattr(page, '_load_mode', None) != 'none' else None)
    final_url = (frame_info.get('url') or safe_current_url(page) or url) if loaded else None
    return NavigationResult(url=url,
                            loaded=loaded,
                            final_url=final_url,
                            status=status,
                            from_performance=status is not None)


def frame_tree_info(page):
    if getattr(page, '_type', None) != 'ChromiumFrame':
        return {}

    frame_id = getattr(page, '_frame_id', None)
    target_page = getattr(page, '_target_page', None)
    if not frame_id or target_page is None:
        return {}

    try:
        tree = target_page._run_cdp('Page.getFrameTree').get('frameTree')
    except Exception:
        return {}

    frame = find_frame_info(tree, frame_id)
    return frame or {}


def find_frame_info(node, frame_id):
    if not node:
        return None

    frame = node.get('frame', {})
    if frame.get('id') == frame_id:
        return frame

    for child in node.get('childFrames') or ():
        found = find_frame_info(child, frame_id)
        if found is not None:
            return found
    return None


def navigation_status_from_performance(page):
    try:
        result = page._run_cdp('Runtime.evaluate', expression=_JS_STATUS, returnByValue=True,
                               awaitPromise=True, _timeout=.5)
        entries = result.get('result', {}).get('value')
    except Exception:
        return None

    for item in reversed(entries or []):
        status = _coerce_status(item)
        if status is not None:
            return status
    return None


def safe_current_url(page):
    try:
        return page.url
    except Exception:
        return None


def _coerce_status(value):
    try:
        status = int(value)
    except (TypeError, ValueError):
        return None
    return status if status > 0 else None
