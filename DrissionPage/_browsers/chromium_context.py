# -*- coding:utf-8 -*-
from .._functions.settings import Settings as _S
from .._units.setter import BrowserContextSetter
from .._units.waiter import BrowserContextWaiter


class ChromiumContext(object):
    def __init__(self, browser, context_id):
        self._browser = browser
        self._context_id = context_id
        self._set = None
        self._wait = None
        self._default_context = context_id == browser._browser_id

    @property
    def browser(self):
        return self._browser

    @property
    def tab_ids(self):
        return self.browser._tab_ids(self._context_id)

    @property
    def latest_tab(self):
        ids = self.tab_ids
        return self.new_tab() if not ids else self.browser._get_tab(self._context_id,
                                                                    id_or_num=ids[0], as_id=not _S.singleton_tab_obj)

    @property
    def set(self):
        if self._set is None:
            self._set = BrowserContextSetter(self)
        return self._set

    @property
    def wait(self):
        if self._wait is None:
            self._wait = BrowserContextWaiter(self)
        return self._wait

    def cookies(self, all_info=False):
        return self.browser._cookies(all_info=all_info, context_id=self._context_id)

    def new_tab(self, url=None, new_window=False, background=False, hidden=False):
        return self._browser._new_tab(url=url, new_window=new_window, background=background,
                                      hidden=hidden, context_id=self._context_id, is_browser=False)

    def get_tab(self, id_or_num=None, title=None, url=None, tab_type='page', as_id=False):
        return self.browser._get_tab(self._context_id, id_or_num=id_or_num, title=title,
                                     url=url, tab_type=tab_type, as_id=as_id)

    def get_tabs(self, title=None, url=None, tab_type='page'):
        return self._browser._get_tabs(self._context_id, title=title, url=url, tab_type=tab_type, as_id=False)

    def close(self):
        if not self._default_context:
            self._browser._run_cdp('Target.disposeBrowserContext', browserContextId=self._context_id)
            self._browser._tabs.remove_context(self._context_id)

    def _run_cdp(self, cmd, _ignore=None, **cmd_args):
        return self.browser._run_cdp(cmd, _ignore=_ignore, **cmd_args)
