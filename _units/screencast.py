# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from base64 import b64decode
from os.path import sep
from pathlib import Path
from random import randint
from shutil import rmtree
from tempfile import gettempdir
from threading import Thread
from time import sleep, time

from .._functions.settings import Settings as _S


class Screencast(object):
    def __init__(self, owner):
        self._owner = owner
        self._path = None
        self._tmp_path = None
        self._running = False
        self._enable = False
        self._mode = 'video'

    @property
    def set_mode(self):
        return ScreencastMode(self)

    def start(self, save_path=None):
        self.set_save_path(save_path)
        if self._path is None:
            raise RuntimeError(_S._lang.join(_S._lang.NEED_ARG_, 'save_path'))

        if self._mode in ('frugal_video', 'video'):
            if self._owner.browser._chromium_options.tmp_path:
                self._tmp_path = Path(
                    self._owner.browser._chromium_options.tmp_path) / f'screencast_tmp_{time()}_{randint(0, 100)}'
            else:
                self._tmp_path = Path(gettempdir()) / 'DrissionPage' / f'screencast_tmp_{time()}_{randint(0, 100)}'
            self._tmp_path.mkdir(parents=True, exist_ok=True)

        if self._mode.startswith('frugal'):
            self._owner.driver.set_callback('Page.screencastFrame', self._onScreencastFrame)
            self._owner._run_cdp('Page.startScreencast', everyNthFrame=1, quality=100)

        elif not self._mode.startswith('js'):
            self._running = True
            self._enable = True
            Thread(target=self._run).start()

        else:  # js模式
            js = '''
            async function () {
                stream = await navigator.mediaDevices.getDisplayMedia({video: true, audio: true})
                mime = MediaRecorder.isTypeSupported("video/webm; codecs=vp9")
                               ? "video/webm; codecs=vp9"
                               : "video/webm"
                mediaRecorder = new MediaRecorder(stream, {mimeType: mime})
                DrissionPage_Screencast_chunks = [];
                mediaRecorder.addEventListener('dataavailable', function(e) {
                    DrissionPage_Screencast_blob_ok = false;
                    DrissionPage_Screencast_chunks.push(e.data);
                    DrissionPage_Screencast_blob_ok = true;
                })
                mediaRecorder.start()

                mediaRecorder.addEventListener('stop', function(){
                    while(DrissionPage_Screencast_blob_ok==false){}
                    DrissionPage_Screencast_blob = new Blob(DrissionPage_Screencast_chunks, 
                                                            {type: DrissionPage_Screencast_chunks[0].type});
                })
              }
            '''
            print(_S._lang.CHOOSE_RECORD_TARGET)
            self._owner._run_js('var DrissionPage_Screencast_blob;var DrissionPage_Screencast_blob_ok=false;')
            self._owner._run_js(js)
        print(_S._lang.START_RECORD)

    def stop(self, video_name=None, suffix='mp4', coding='mp4v'):
        video_name = f'{time()}.{suffix}' if not video_name else video_name
        if not video_name.endswith(f'.{suffix}'):
            video_name = f'{video_name}.{suffix}'
        path = f'{self._path}{sep}{video_name}'

        if self._mode.startswith('js'):
            self._owner._run_js('mediaRecorder.stop();', as_expr=True)
            while not self._owner._run_js('return DrissionPage_Screencast_blob_ok;'):
                sleep(.05)
            with open(path, 'wb') as f:
                f.write(b64decode(self._owner._run_js('return DrissionPage_Screencast_blob;')))
            self._owner._run_js('DrissionPage_Screencast_blob_ok = false;'
                                'DrissionPage_Screencast_chunks = [];'
                                'DrissionPage_Screencast_blob = null', as_expr=True)
            print(_S._lang.STOP_RECORDING)
            return path

        if self._mode.startswith('frugal'):
            self._owner.driver.set_callback('Page.screencastFrame', None)
            self._owner._run_cdp('Page.stopScreencast')
        else:
            self._enable = False
            while self._running:
                sleep(.01)

        if self._mode.endswith('imgs'):
            print(_S._lang.STOP_RECORDING)
            return str(Path(self._path).absolute())

        if not str(self._path).isascii():
            raise ValueError(_S._lang.join(_S._lang.ONLY_ENGLISH, CURR_VAL=self._path))

        try:
            from cv2 import VideoWriter, imread, VideoWriter_fourcc
            from numpy import fromfile, uint8
        except (ImportError, ModuleNotFoundError):
            raise EnvironmentError(_S._lang.join(_S._lang.NEED_LIB_, 'cv2, numpy',
                                                 TIP='pip install opencv-python\npip install numpy'))

        pic_list = Path(self._tmp_path or self._path).glob('*.jpg')
        img = imread(str(next(pic_list)))
        imgInfo = img.shape
        size = (imgInfo[1], imgInfo[0])

        videoWrite = VideoWriter(path, VideoWriter_fourcc(*coding.upper()), 5, size)

        for i in pic_list:
            img = imread(str(i))
            videoWrite.write(img)

        rmtree(self._tmp_path)
        self._tmp_path = None
        print(_S._lang.STOP_RECORDING)
        return f'{self._path}{sep}{video_name}'

    def set_save_path(self, save_path=None):
        if save_path:
            save_path = Path(save_path)
            if save_path.exists() and save_path.is_file():
                raise ValueError(_S._lang.join(_S._lang.SAVE_PATH_MUST_BE_FOLDER))
            save_path.mkdir(parents=True, exist_ok=True)
            self._path = save_path

    def _run(self):
        self._running = True
        path = self._tmp_path or self._path
        while self._enable:
            self._owner.get_screenshot(path=path, name=f'{time()}.jpg')
            sleep(.04)
        self._running = False

    def _onScreencastFrame(self, **kwargs):
        path = self._tmp_path or self._path
        with open(f'{path}{sep}{kwargs["metadata"]["timestamp"]}.jpg', 'wb') as f:
            f.write(b64decode(kwargs['data']))
        self._owner._run_cdp('Page.screencastFrameAck', sessionId=kwargs['sessionId'])


class ScreencastMode(object):
    def __init__(self, screencast):
        self._screencast = screencast

    def video_mode(self):
        self._screencast._mode = 'video'

    def frugal_video_mode(self):
        self._screencast._mode = 'frugal_video'

    def js_video_mode(self):
        self._screencast._mode = 'js_video'

    def frugal_imgs_mode(self):
        self._screencast._mode = 'frugal_imgs'

    def imgs_mode(self):
        self._screencast._mode = 'imgs'
