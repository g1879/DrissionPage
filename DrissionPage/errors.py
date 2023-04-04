# -*- coding:utf-8 -*-


class BaseError(Exception):
    _info = None

    def __init__(self, ErrorInfo=None):
        super().__init__(self)  # 初始化父类
        self._info = ErrorInfo or self._info

    def __str__(self):
        return self._info


class AlertExistsError(BaseError):
    _info = '存在未处理的提示框。'


class ContextLossError(BaseError):
    _info = '页面被刷新，请操作前尝试等待页面刷新或加载完成。'


class ElementLossError(BaseError):
    _info = '元素对象因刷新已失效。'


class CallMethodError(BaseError):
    _info = '方法调用错误。'


class TabClosedError(BaseError):
    _info = '标签页已关闭。'


class ElementNotFoundError(BaseError):
    _info = '没有找到元素。'


class JavaScriptError(BaseError):
    _info = 'JavaScript运行错误。'


class NoRectError(BaseError):
    _info = '该元素没有位置及大小。'


class BrowserConnectError(BaseError):
    _info = '浏览器连接失败。'


class NoResourceError(BaseError):
    _info = '该元素无可保存的内容或保存失败。'


class CanNotClickError(BaseError):
    _info = '该元素无法滚动到视口或被遮挡，无法点击。'
