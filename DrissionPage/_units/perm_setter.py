# -*- coding:utf-8 -*-
class BrowserPermSetter(object):
    def __init__(self, owner, context_id):
        self._owner = owner
        self._context_id = context_id

    def _set_perm(self, data, allow):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission=data,
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission=data, setting=allow)

    def geolocation(self, allow=True):
        self._set_perm({'name': 'geolocation'}, allow)

    def notifications(self, allow=True):
        self._set_perm({'name': 'notifications'}, allow)

    def push(self, allow=True):
        self._set_perm({'name': 'push', 'userVisibleOnly': True}, allow)

    def midi(self, allow=True, sysex=None):
        data = {'name': 'midi', 'sysex': sysex} if isinstance(sysex, bool) else {'name': 'midi'}
        self._set_perm(data, allow)

    def camera(self, allow=True, panTiltZoom=None):
        data = {'name': 'camera', 'panTiltZoom': panTiltZoom} if isinstance(panTiltZoom, bool) else {'name': 'camera'}
        self._set_perm(data, allow)

    def microphone(self, allow=True):
        self._set_perm({'name': 'microphone'}, allow)

    def background_fetch(self, allow=True):
        self._set_perm({'name': 'background-fetch'}, allow)

    def background_sync(self, allow=True):
        self._set_perm({'name': 'background-sync'}, allow)

    def persistent_storage(self, allow=True):
        self._set_perm({'name': 'persistent-storage'}, allow)

    def ambient_light_sensor(self, allow=True):
        self._set_perm({'name': 'ambient-light-sensor'}, allow)

    def accelerometer(self, allow=True):
        self._set_perm({'name': 'accelerometer'}, allow)

    def gyroscope(self, allow=True):
        self._set_perm({'name': 'gyroscope'}, allow)

    def magnetometer(self, allow=True):
        self._set_perm({'name': 'magnetometer'}, allow)

    def screen_wake_lock(self, allow=True):
        self._set_perm({'name': 'screen-wake-lock'}, allow)

    def nfc(self, allow=True):
        self._set_perm({'name': 'nfc'}, allow)

    def display_capture(self, allow=True):
        self._set_perm({'name': 'display-capture'}, allow)

    def clipboard_read(self, allow=True, allowWithoutSanitization=None):
        data = ({'name': 'clipboard-read', 'allowWithoutSanitization': allowWithoutSanitization}
                if isinstance(allowWithoutSanitization, bool) else {'name': 'clipboard-read'})
        self._set_perm(data, allow)

    def clipboard_write(self, allow=True, allowWithoutSanitization=None):
        data = ({'name': 'clipboard-write', 'allowWithoutSanitization': allowWithoutSanitization}
                if isinstance(allowWithoutSanitization, bool) else {'name': 'clipboard-write'})
        self._set_perm(data, allow)

    def payment_handler(self, allow=True):
        self._set_perm({'name': 'payment-handler'}, allow)

    def idle_detection(self, allow=True):
        self._set_perm({'name': 'idle-detection'}, allow)

    def periodic_background_sync(self, allow=True):
        self._set_perm({'name': 'periodic-background-sync'}, allow)

    def system_wake_lock(self, allow=True):
        self._set_perm({'name': 'system-wake-lock'}, allow)

    def storage_access(self, allow=True):
        self._set_perm({'name': 'storage-access'}, allow)

    def window_management(self, allow=True):
        self._set_perm({'name': 'window-management'}, allow)

    def local_fonts(self, allow=True):
        self._set_perm({'name': 'local-fonts'}, allow)

    def top_level_storage_access(self, allow=True):
        self._set_perm({'name': 'top-level-storage-access'}, allow)

    def captured_surface_control(self, allow=True):
        self._set_perm({'name': 'captured-surface-control'}, allow)

    def speaker_selection(self, allow=True):
        self._set_perm({'name': 'speaker-selection'}, allow)

    def keyboard_lock(self, allow=True):
        self._set_perm({'name': 'keyboard-lock'}, allow)

    def pointer_lock(self, allow=True):
        self._set_perm({'name': 'pointer-lock'}, allow)

    def fullscreen(self, allow=True):
        self._set_perm({'name': 'fullscreen', 'allowWithoutGesture': True}, allow)

    def web_app_installation(self, allow=True):
        self._set_perm({'name': 'web-app-installation'}, allow)

    def local_network_access(self, allow=True):
        self._set_perm({'name': 'local-network-access'}, allow)

    def local_network(self, allow=True):
        self._set_perm({'name': 'local-network'}, allow)

    def loopback_network(self, allow=True):
        self._set_perm({'name': 'loopback-network'}, allow)
