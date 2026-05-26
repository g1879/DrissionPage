# -*- coding:utf-8 -*-
class BrowserPermSetter(object):
    def __init__(self, owner, context_id):
        self._owner = owner
        self._context_id = context_id

    def geolocation(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'geolocation'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'geolocation'}, setting=allow)

    def notifications(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'notifications'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'notifications'}, setting=allow)

    def push(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'push', 'userVisibleOnly': True},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'push', 'userVisibleOnly': True},
                                 setting=allow)

    def midi(self, allow=True, sysex=None):
        allow = 'granted' if allow else 'denied'
        if isinstance(sysex, bool):
            data = {'name': 'midi', 'sysex': sysex}
        else:
            data = {'name': 'midi'}

        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission=data, setting=allow,
                                 browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission=data, setting=allow)

    def camera(self, allow=True, panTiltZoom=None):
        allow = 'granted' if allow else 'denied'
        if isinstance(panTiltZoom, bool):
            data = {'name': 'camera', 'panTiltZoom': panTiltZoom}
        else:
            data = {'name': 'camera'}

        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission=data, setting=allow,
                                 browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission=data, setting=allow)

    def microphone(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'microphone'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'microphone'}, setting=allow)

    def background_fetch(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'background-fetch'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'background-fetch'}, setting=allow)

    def background_sync(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'background-sync'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'background-sync'}, setting=allow)

    def persistent_storage(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'persistent-storage'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'persistent-storage'}, setting=allow)

    def ambient_light_sensor(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'ambient-light-sensor'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'ambient-light-sensor'}, setting=allow)

    def accelerometer(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'accelerometer'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'accelerometer'}, setting=allow)

    def gyroscope(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'gyroscope'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'gyroscope'}, setting=allow)

    def magnetometer(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'magnetometer'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'magnetometer'}, setting=allow)

    def screen_wake_lock(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'screen-wake-lock'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'screen-wake-lock'}, setting=allow)

    def nfc(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'nfc'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'nfc'}, setting=allow)

    def display_capture(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'display-capture'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'display-capture'}, setting=allow)

    def clipboard_read(self, allow=True, allowWithoutSanitization=None):
        allow = 'granted' if allow else 'denied'
        if isinstance(allowWithoutSanitization, bool):
            data = {'name': 'clipboard-read', 'allowWithoutSanitization': allowWithoutSanitization}
        else:
            data = {'name': 'clipboard-read'}

        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission=data,
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission=data, setting=allow)

    def clipboard_write(self, allow=True, allowWithoutSanitization=None):
        allow = 'granted' if allow else 'denied'
        if isinstance(allowWithoutSanitization, bool):
            data = {'name': 'clipboard-write', 'allowWithoutSanitization': allowWithoutSanitization}
        else:
            data = {'name': 'clipboard-write'}

        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission=data, setting=allow,
                                 browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission=data, setting=allow)

    def payment_handler(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'payment-handler'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'payment-handler'}, setting=allow)

    def idle_detection(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'idle-detection'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'idle-detection'}, setting=allow)

    def periodic_background_sync(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'periodic-background-sync'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'periodic-background-sync'},
                                 setting=allow)

    def system_wake_lock(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'system-wake-lock'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'system-wake-lock'}, setting=allow)

    def storage_access(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'storage-access'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'storage-access'}, setting=allow)

    def window_management(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'window-management'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'window-management'}, setting=allow)

    def local_fonts(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'local-fonts'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'local-fonts'}, setting=allow)

    def top_level_storage_access(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'top-level-storage-access'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'top-level-storage-access'},
                                 setting=allow)

    def captured_surface_control(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'captured-surface-control'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'captured-surface-control'},
                                 setting=allow)

    def speaker_selection(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'speaker-selection'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'speaker-selection'}, setting=allow)

    def keyboard_lock(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'keyboard-lock'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'keyboard-lock'}, setting=allow)

    def pointer_lock(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'pointer-lock'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'pointer-lock'}, setting=allow)

    def fullscreen(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', setting=allow, browserContextId=self._context_id,
                                 permission={'name': 'fullscreen', 'allowWithoutGesture': True})
        else:
            self._owner._run_cdp('Browser.setPermission', setting=allow,
                                 permission={'name': 'fullscreen', 'allowWithoutGesture': True})

    def web_app_installation(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'web-app-installation'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'web-app-installation'}, setting=allow)

    def local_network_access(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'local-network-access'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'local-network-access'}, setting=allow)

    def local_network(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'local-network'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'local-network'}, setting=allow)

    def loopback_network(self, allow=True):
        allow = 'granted' if allow else 'denied'
        if self._context_id:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'loopback-network'},
                                 setting=allow, browserContextId=self._context_id)
        else:
            self._owner._run_cdp('Browser.setPermission', permission={'name': 'loopback-network'}, setting=allow)
