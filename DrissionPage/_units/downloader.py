# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from os.path import sep
from pathlib import Path
from shutil import move
from time import sleep, perf_counter

from DataRecorder.tools import get_usable_path


class DownloadManager(object):

    def __init__(self, browser):
        self._browser = browser

        t = TabDownloadSettings('browser')
        t.path = self._browser.download_path
        t.rename = None
        t.suffix = None
        t.when_file_exists = 'rename'

        self._missions = {}  # {guid: DownloadMission}
        self._tab_missions = {}  # {tab_id: DownloadMission}
        self._flags = {}  # {tab_id: [bool, DownloadMission]}

        self._running = False

    @property
    def missions(self):
        return self._missions

    def set_path(self, tab, path):
        tid = tab if isinstance(tab, str) else tab.tab_id
        TabDownloadSettings(tid).path = path
        if not self._running or tid == 'browser':
            self._browser._driver.set_callback('Browser.downloadProgress', self._onDownloadProgress)
            self._browser._driver.set_callback('Browser.downloadWillBegin', self._onDownloadWillBegin)
            r = self._browser._run_cdp('Browser.setDownloadBehavior', downloadPath=self._browser._download_path,
                                       behavior='allowAndName', eventsEnabled=True)
            if 'error' in r:
                print('浏览器版本太低无法使用下载管理功能。')
        self._running = True

    def set_rename(self, tab_id, rename=None, suffix=None):
        ts = TabDownloadSettings(tab_id)
        ts.rename = rename
        ts.suffix = suffix

    def set_file_exists(self, tab_id, mode):
        TabDownloadSettings(tab_id).when_file_exists = mode

    def set_flag(self, tab_id, flag):
        self._flags[tab_id] = flag

    def get_flag(self, tab_id):
        return self._flags.get(tab_id, None)

    def get_tab_missions(self, tab_id):
        return self._tab_missions.get(tab_id, [])

    def set_done(self, mission, state, final_path=None):
        if mission.state not in ('canceled', 'skipped'):
            mission.state = state
        mission.final_path = final_path
        if mission.tab_id in self._tab_missions and mission.id in self._tab_missions[mission.tab_id]:
            self._tab_missions[mission.tab_id].remove(mission.id)
        self._missions.pop(mission.id, None)
        mission._is_done = True

    def cancel(self, mission):
        mission.state = 'canceled'
        try:
            self._browser._run_cdp('Browser.cancelDownload', guid=mission.id)
        except:
            pass
        if mission.final_path:
            Path(mission.final_path).unlink(True)

    def skip(self, mission):
        mission.state = 'skipped'
        try:
            self._browser._run_cdp('Browser.cancelDownload', guid=mission.id)
        except:
            pass

    def clear_tab_info(self, tab_id):
        self._tab_missions.pop(tab_id, None)
        self._flags.pop(tab_id, None)
        TabDownloadSettings.TABS.pop(tab_id, None)

    def _onDownloadWillBegin(self, **kwargs):
        guid = kwargs['guid']
        tab_id = self._browser._frames.get(kwargs['frameId'], 'browser')

        settings = TabDownloadSettings(tab_id if tab_id in TabDownloadSettings.TABS else 'browser')
        if settings.rename:
            if settings.suffix is not None:
                name = f'{settings.rename}.{settings.suffix}' if settings.suffix else settings.rename

            else:
                tmp = kwargs['suggestedFilename'].rsplit('.', 1)
                ext_name = tmp[-1] if len(tmp) > 1 else ''
                tmp = settings.rename.rsplit('.', 1)
                ext_rename = tmp[-1] if len(tmp) > 1 else ''
                name = settings.rename if ext_rename == ext_name else f'{settings.rename}.{ext_name}'

            settings.rename = None
            settings.suffix = None

        elif settings.suffix is not None:
            name = kwargs["suggestedFilename"].rsplit(".", 1)[0]
            if settings.suffix:
                name = f'{name}.{settings.suffix}'
            settings.suffix = None

        else:
            name = kwargs['suggestedFilename']

        skip = False
        goal_path = Path(settings.path) / name
        if goal_path.exists():
            if settings.when_file_exists == 'skip':
                skip = True
            elif settings.when_file_exists == 'overwrite':
                goal_path.unlink()

        m = DownloadMission(self, tab_id, guid, settings.path, name, kwargs['url'], self._browser.download_path)
        self._missions[guid] = m

        if self.get_flag(tab_id) is False:  # 取消该任务
            self.cancel(m)
        elif skip:
            self.skip(m)
        else:
            self._tab_missions.setdefault(tab_id, []).append(m)

        if self.get_flag(tab_id) is not None:
            self._flags[tab_id] = m

    def _onDownloadProgress(self, **kwargs):
        if kwargs['guid'] in self._missions:
            mission = self._missions[kwargs['guid']]
            if kwargs['state'] == 'inProgress':
                mission.received_bytes = kwargs['receivedBytes']
                mission.total_bytes = kwargs['totalBytes']

            elif kwargs['state'] == 'completed':
                if mission.state == 'skipped':
                    Path(f'{mission.save_path}{sep}{mission.id}').unlink(True)
                    self.set_done(mission, 'skipped')
                    return
                mission.received_bytes = kwargs['receivedBytes']
                mission.total_bytes = kwargs['totalBytes']
                form_path = f'{mission.save_path}{sep}{mission.id}'
                to_path = str(get_usable_path(f'{mission.path}{sep}{mission.name}'))
                not_moved = True
                for _ in range(10):
                    try:
                        move(form_path, to_path)
                        not_moved = False
                        break
                    except PermissionError:
                        sleep(.5)
                if not_moved:
                    from shutil import copy
                    copy(form_path, to_path)
                self.set_done(mission, 'completed', final_path=to_path)

            else:  # 'canceled'
                self.set_done(mission, 'canceled')


class TabDownloadSettings(object):
    TABS = {}

    def __new__(cls, tab_id):
        """
        :param tab_id: tab id
        """
        if tab_id in cls.TABS:
            return cls.TABS[tab_id]
        return object.__new__(cls)

    def __init__(self, tab_id):
        if hasattr(self, '_created'):
            return
        self._created = True
        self.tab_id = tab_id
        self.rename = None
        self.suffix = None
        self.path = ''
        self.when_file_exists = 'rename'

        TabDownloadSettings.TABS[tab_id] = self


class DownloadMission(object):
    def __init__(self, mgr, tab_id, _id, path, name, url, save_path):
        self._mgr = mgr
        self.url = url
        self.tab_id = tab_id
        self.id = _id
        self.path = path
        self.name = name
        self.state = 'running'
        self.total_bytes = None
        self.received_bytes = 0
        self.final_path = None
        self.save_path = save_path
        self._is_done = False

    def __repr__(self):
        return f'<DownloadMission {id(self)} {self.rate}>'

    @property
    def rate(self):
        return round((self.received_bytes / self.total_bytes) * 100, 2) if self.total_bytes else None

    @property
    def is_done(self):
        return self._is_done

    def cancel(self):
        self._mgr.cancel(self)

    def wait(self, show=True, timeout=None, cancel_if_timeout=True):
        if show:
            print(f'url：{self.url}')
            end_time = perf_counter()
            while self.name is None and perf_counter() < end_time:
                sleep(0.01)
            print(f'文件名：{self.name}')
            print(f'目标路径：{self.path}')

        if timeout is None:
            while not self.is_done:
                if show:
                    print(f'\r{self.rate}% ', end='')
                sleep(.2)

        else:
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                if show:
                    print(f'\r{self.rate}% ', end='')
                sleep(.2)

            if not self.is_done and cancel_if_timeout:
                self.cancel()

        if show:
            if self.state == 'completed':
                print(f'下载完成 {self.final_path}')
            elif self.state == 'canceled':
                print(f'下载取消')
            elif self.state == 'skipped':
                print(f'已跳过')
            print()

        return self.final_path if self.final_path else False
