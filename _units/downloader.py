# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from os.path import sep
from pathlib import Path
from shutil import move
from time import sleep, perf_counter

from DataRecorder.tools import get_usable_path

from .._functions.settings import Settings as _S


class DownloadManager(object):

    def __init__(self, browser):
        self._browser = browser

        t = TabDownloadSettings('browser')
        t.path = self._browser.download_path
        t.rename = None
        t.suffix = None
        t.when_file_exists = 'rename'

        self._missions = {}  # {guid: DownloadMission}
        self._tab_missions = {}  # {tab_id: [DownloadMission, ...]}
        self._flags = {}  # {tab_id: [bool, DownloadMission]}
        self._waiting_tab = set()  # click.to_download()专用
        self._tmp_path = '.'
        self._page_id = None

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
            self._tmp_path = self._browser._download_path
            if 'error' in r:
                print(_S._lang.NOT_SUPPORT_DOWNLOAD)
        self._running = True

    @staticmethod
    def set_rename(tab_id, rename=None, suffix=None):
        ts = TabDownloadSettings(tab_id)
        ts.rename = rename
        ts.suffix = suffix

    @staticmethod
    def set_file_exists(tab_id, mode):
        TabDownloadSettings(tab_id).when_file_exists = mode

    def set_flag(self, tab_id, flag):
        self._flags[tab_id] = flag

    def get_flag(self, tab_id):
        return self._flags.get(tab_id, None)

    def get_tab_missions(self, tab_id):
        return self._tab_missions.get(tab_id, set())

    def set_done(self, mission, state, final_path=None):
        if mission.state not in ('canceled', 'skipped'):
            mission.state = state
        mission.final_path = final_path
        if mission.tab_id in self._tab_missions and mission in self._tab_missions[mission.tab_id]:
            self._tab_missions[mission.tab_id].discard(mission)
        if (mission.from_tab and mission.from_tab in self._tab_missions
                and mission in self._tab_missions[mission.from_tab]):
            self._tab_missions[mission.from_tab].discard(mission)
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
        self._waiting_tab.discard(tab_id)

    def _onDownloadWillBegin(self, **kwargs):
        guid = kwargs['guid']
        tab_id = self._browser._frames.get(kwargs['frameId'], 'browser')
        tab = 'browser' if tab_id in ('browser', self._page_id) or self.get_flag('browser') is not None else tab_id
        opener = self._browser._relation.get(tab_id, None)
        from_tab = None
        if opener and opener in self._waiting_tab:
            tab = from_tab = opener

        settings = TabDownloadSettings(tab)
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
        overwrite = None  # 存在且重命名
        goal_path = Path(settings.path) / name
        if goal_path.exists():
            if settings.when_file_exists == 'skip':
                skip = True
            elif settings.when_file_exists == 'overwrite':
                overwrite = True  # 存在且覆盖
        else:  # 不存在
            overwrite = False

        m = DownloadMission(self, tab_id, guid, settings.path, name, kwargs['url'], self._tmp_path, overwrite)
        if from_tab:
            m.from_tab = from_tab
            self._tab_missions.setdefault(from_tab, set()).add(m)
        self._missions[guid] = m

        if self.get_flag('browser') is False or self.get_flag(tab) is False:  # 取消该任务
            self.cancel(m)
        elif skip:
            self.skip(m)
        else:
            self._tab_missions.setdefault(tab_id, set()).add(m)

        if self.get_flag('browser') is not None:
            self._flags['browser'] = m
        elif self.get_flag(tab) is not None:
            self._flags[tab] = m

    def _onDownloadProgress(self, **kwargs):
        if kwargs['guid'] in self._missions:
            mission = self._missions[kwargs['guid']]
            if kwargs['state'] == 'inProgress':
                mission.received_bytes = kwargs['receivedBytes']
                mission.total_bytes = kwargs['totalBytes']

            elif kwargs['state'] == 'completed':
                if mission.state == 'skipped':
                    Path(f'{mission.tmp_path}{sep}{mission.id}').unlink(True)
                    self.set_done(mission, 'skipped')
                    return
                mission.received_bytes = kwargs['receivedBytes']
                mission.total_bytes = kwargs['totalBytes']
                form_path = f'{mission.tmp_path}{sep}{mission.id}'
                if mission._overwrite is None:
                    to_path = str(get_usable_path(f'{mission.folder}{sep}{mission.name}'))
                else:
                    to_path = f'{mission.folder}{sep}{mission.name}'
                Path(mission.folder).mkdir(parents=True, exist_ok=True)
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
        self.path = '' if tab_id == 'browser' else self.TABS['browser'].path
        self.when_file_exists = 'rename' if tab_id == 'browser' else self.TABS['browser'].when_file_exists

        TabDownloadSettings.TABS[tab_id] = self


class DownloadMission(object):
    def __init__(self, mgr, tab_id, _id, folder, name, url, tmp_path, overwrite):
        self._mgr = mgr
        self.url = url
        self.tab_id = tab_id
        self.from_tab = None
        self.id = _id
        self.folder = folder
        self.name = name
        self.state = 'running'
        self.total_bytes = None
        self.received_bytes = 0
        self.final_path = None
        self.tmp_path = tmp_path
        self._overwrite = overwrite
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
            print(f'url: {self.url}')
            end_time = perf_counter()
            while self.name is None and perf_counter() < end_time:
                sleep(0.01)
            print(f'{_S._lang.FILE_NAME}: {self.name or _S._lang.UNKNOWN}')
            print(f'{_S._lang.FOLDER_PATH}: {self.folder}')

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
                print('\r100% ', end='')
                if self._overwrite is None:
                    print(f'{_S._lang.COMPLETED_AND_RENAME} {self.final_path}')
                elif self._overwrite is False:
                    print(f'{_S._lang.DOWNLOAD_COMPLETED} {self.final_path}')
                else:
                    print(f'{_S._lang.OVERWROTE} {self.final_path}')
            elif self.state == 'canceled':
                print(_S._lang.DOWNLOAD_CANCELED)
            elif self.state == 'skipped':
                print(f'{_S._lang.SKIPPED} {self.folder}{sep}{self.name}')
            print()

        return self.final_path if self.final_path else False
