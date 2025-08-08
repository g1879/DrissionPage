# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from locale import getlocale

from ..version import __version__


def get_txt_class(lang=None):
    languages = {
        'zh_cn': Texts,
        'cn': Texts,
        'en': English,
    }
    if lang is None:
        locale = str(getlocale()[0]).lower()
        if locale.startswith('zh') or 'chinese' in locale:
            lang = 'zh_cn'
        elif locale.startswith('en') or 'english' in locale:
            lang = 'en'
        else:
            lang = 'zh_cn'
    else:
        lang = lang.lower()
    lang = languages.get(lang, None)
    if lang is None:
        raise ValueError(f'lang must be one of {languages.keys()}')
    return lang


class Texts(object):
    # --------- 参数名 ---------
    VERSION = '版本'
    INFO = '详情'
    METHOD = '方法'
    ARGS = '参数'
    ARG = '参数'
    BROWSER_VER = '浏览器版本'
    PATH = '路径'
    VALUE = '值'
    ALLOW_VAL = '允许值'
    CURR_VAL = '当前值'
    ALLOW_TYPE = '允许类型'
    CURR_TYPE = '当前类型'
    TIP = '提示'
    ADDRESS = '地址'
    LOCATOR = '定位符'
    ALL_TABS = '所有标签页'

    # --------- 异常默认文本 ---------
    ELEMENTNOTFOUNDERROR = '没有找到元素。'
    ALERTEXISTSERROR = '存在未处理的提示框。'
    CONTEXTLOSTERROR = '页面被刷新，请操作前尝试等待页面刷新或加载完成。'
    ELEMENTLOSTERROR = '元素对象已失效。可能是页面整体刷新，或js局部刷新把元素替换或去除了。'
    CDPERROR = '方法调用错误。'
    PAGEDISCONNECTEDERROR = '与页面的连接已断开。'
    JAVASCRIPTERROR = 'JavaScript运行错误。'
    NORECTERROR = '该元素没有位置及大小。'
    BROWSERCONNECTERROR = '浏览器连接失败。'
    NORESOURCEERROR = '该元素无可保存的内容或保存失败。'
    CANNOTCLICKERROR = '该元素无法滚动到视口或被遮挡，无法点击。'
    GETDOCUMENTERROR = '获取文档失败。'
    WAITTIMEOUTERROR = '等待失败。'
    INCORRECTURLERROR = '无效的url。'
    LOCATORERROR = '定位符格式不正确。',
    STORAGEERROR = '无法操作当前存储数据。'
    COOKIEFORMATERROR = 'cookie格式不正确。'
    TARGETNOTFOUNDERROR = '找不到指定页面。'

    # --------- 异常信息 ---------
    NO_AVAILABLE_PORT_FOUND = '未找到可用端口。'
    WIN_SYS_ONLY = '该方法只能在Windows系统使用。'
    NEED_LIB_ = '请先安装{}。'
    INVALID_URL = '无效的url，也许要加上"http://"？'
    INVALID_HEADER_NAME = '无效的header项名。'
    NOT_A_FUNCTION = '传入的js无法解析成函数。'
    METHOD_NOT_FOUND = '没有找到对应功能，方法错误或你的浏览器太旧。'
    NO_RESPONSE = '超时，可能是浏览器卡了。'
    UNKNOWN_ERR = '出现未知错误。'
    FEEDBACK = ('出现这个错误可能意味着程序有bug，请把错误信息和重现方法告知作者，谢谢。\n'
                '报告网站: https://gitee.com/g1879/DrissionPage/issues')
    INI_NOT_FOUND = 'ini文件不存在。'
    EXT_NOT_FOUND = '插件路径不存在。'
    WAITING_FAILED_ = '等待{}失败（等待{}秒）。'
    GET_OBJ_FAILED = '获取对象失败。'
    INCORRECT_VAL_ = '{}参数值错误。'
    INCORRECT_TYPE_ = '{}参数类型错误。'
    CONNECT_ERR = '连接异常。'
    BROWSER_CONNECT_ERR1_ = '浏览器连接失败，请检查{}端口是否浏览器，且已添加"--remote-debugging-port={}"启动项。'
    BROWSER_CONNECT_ERR2 = '浏览器连接失败，请确认浏览器已启动。'
    BROWSER_EXE_NOT_FOUND = '无法找到浏览器可执行文件路径，请手动配置。'
    BROWSER_NOT_FOUND = '未找到浏览器。'
    BROWSER_NOT_EXIST = '浏览器未开启或已关闭。'
    BROWSER_DISCONNECTED = '浏览器已关闭或链接已断开。'
    BROWSER_NOT_FOR_CONTROL = '浏览器版本太旧或此浏览器不支持接管。'
    UNSUPPORTED_CSS_SYNTAX = '此css selector语法不受支持，请换成xpath。'
    UNSUPPORTED_ARG_TYPE_ = '不支持参数{}的类型: {}。'
    UPGRADE_WS = '请升级websocket-client库。'
    INI_NOT_SET = 'ini_path未设置。'
    INVALID_XPATH_ = '无效的xpath语句: {}'
    INVALID_CSS_ = '无效的css selector语句: {}'
    INDEX_FORMAT = '序号必须是数字或切片。'
    LOC_NOT_FOR_FRAME = '该定位符不是指向frame元素。'
    NEED_DOWNLOAD_PATH = '此功能需显式设置下载路径。'
    GET_WINDOW_SIZE_FAILED = '获取窗口信息失败。'
    SET_FAILED_ = '{}设置失败。'
    NOT_LISTENING = '监听未启动或已停止。'
    NOT_BLOB = '该链接非blob类型。'
    CANNOT_INPUT_FILE = '该输入框无法接管，请改用对<input>元素输入路径的方法设置。'
    NO_SUCH_KEY_ = '没有这个按键: {}'
    NO_NEW_TAB = '没有等到新标签页。'
    NO_SUCH_TAB = '没有找到指定标签页。'
    NEED_DOMAIN = '需设置domain或url值。如设置url值，需以http开头。'
    NEED_DOMAIN2 = 'cookie必须带有"domain"或"url"字段。'
    NEED_ARG_ = '{}必须设置。'
    SAVE_PATH_MUST_BE_FOLDER = 'save_path必须为文件夹。'
    GET_PDF_FAILED = '保存失败，可能浏览器版本不支持。'
    GET_BLOB_FAILED = '无法获取该资源。'
    NO_SRC_ATTR = '元素没有src值或该值为空。'
    D_MODE_ONLY = 'url、domain、path参数只有d模式下有效。'
    S_MODE_ONLY = '以下参数在s模式下才会生效:'
    STATUS_CODE_ = '状态码: {}'
    TAB_OBJ_EXISTS = '该标签页已有非MixTab版本，如需多对象共用标签页请设置Settings.set_singleton_tab_obj(False)。'
    ONLY_ENGLISH = '转换成视频仅支持英文路径和文件名。'
    SELECT_ONLY = 'select方法只能在<select>元素使用。'
    MULTI_SELECT_ONLY = '只能在多选菜单执行此操作。'
    OPTION_NOT_FOUND = '没有找到指定选项。'
    STR_FOR_SINGLE_SELECT = '单选列表只能传入str格式。'
    JS_RUNTIME_ERR = 'js运行环境出错。'
    TIMEOUT_ = '{}超时（等待{}秒）'
    JS_RESULT_ERR = 'js结果解析错误。'
    S_MODE_GET_FAILED = 's模式访问失败，请设置go=False，自行构造连接参数进行访问。'
    ZERO_PAGE_SIZE = '页面大小为0，请尝试等待页面加载完成。'
    CONTENT_IS_EMPTY = '返回内容为空。'
    FIND_ELE_ERR = '查找元素异常。'
    SYMBOL_CONFLICT = '@@和@|不能同时出现在一个定位语句中。'
    INVALID_LOC = '无法识别的定位符。'
    LOC_LEN = '定位符长度必须为2。'
    INCORRECT_SIGN_ = '符号不正确: {}'
    DOMAIN_NOT_SET = '未设置域名，请设置cookie的domain参数或先访问一个网站。'

    # --------- 参数内容 ---------
    ELE_DISPLAYED = '元素显示'
    ELE_LOADED = '元素加载'
    PAGE_LOADED = '页面加载'
    NEW_TAB = '新标签页'
    DATA_PACKET = '数据包'
    ELE_HIDDEN_DEL = '元素隐藏或被删除'
    ELE_DEL = '元素被删除'
    ELE_HAS_RECT = '元素拥有大小及位置'
    ELE_HIDDEN = '元素隐藏'
    ELE_CLICKABLE = '元素可点击'
    ELE_COVERED = '元素被覆盖'
    ELE_NOT_COVERED = '元素不被覆盖'
    ELE_AVAILABLE = '元素可用'
    ELE_NOT_AVAILABLE = '元素不可用'
    ELE_STOP_MOVING = '元素停止运动'
    ELE_STATE_CHANGED_ = '等待元素状态改变失败（等待{}秒）。'
    RUN_BY_ADMIN = '尝试用管理员权限运行。'
    BROWSER_CONNECT_ERR_INFO = ('\n1、用户文件夹没有和已打开的浏览器冲突\n'
                                '2、如为无界面系统，请添加\'--headless=new\'启动参数\n'
                                '3、如果是Linux系统，尝试添加\'--no-sandbox\'启动参数\n'
                                '可使用ChromiumOptions设置端口和用户文件夹路径。')
    # ALLOW
    LOC_OR_IND = '定位符（str或长度为2的tuple）或序号'
    STR_ONLY = 'str格式且不支持xpath和css形式'
    LOC_FORMAT = 'str或长度为2的tuple'
    ELE_OR_LOC = '定位符（str或长度为2的tuple）或元素'
    FRAME_LOC_FORMAT = '定位符、iframe序号、id、name、ChromiumFrame对象'
    SET_DOWNLOAD_PATH = '使用set.download_path()方法、配置对象或ini文件均可。'
    SET_WINDOW_NORMAL = '浏览器全屏或最小化状态时请先调用set.window.normal()恢复正常状态。'
    HTML_ELE_TYPE = '元素、页面对象或html文本'
    ELE_LOC_FORMAT = '(x, y)格式坐标，或ChromiumElement对象'
    IP_OR_OPTIONS = 'ip:port格式字符串或ChromiumOptions类型'

    TAB_OR_ID = '标签页对象或id'
    RUN_JS = '执行js'
    PAGE_CONNECT = '页面连接'
    NEW_ELE_INFO = 'str格式的html文本，或tuple格式(tag, {name: value})。'
    DICT_TO_NEW_ELE = '此网页不支持html格式新建元素，请用dict传入html_or_info参数。'

    # --------- print ---------
    RETRY = '重试'
    OPTIONS_HAVE_SAVED = '配置已保存到文件'
    AUTO_LOAD_TIP = '以后程序可自动从文件加载配置'
    STOP_RECORDING = '停止录制'
    START_RECORD = '开始录制'
    CHOOSE_RECORD_TARGET = '请手动选择要录制的目标。'
    UNSUPPORTED_USER_PROXY = '你似乎在设置使用账号密码的代理，暂时不支持这种代理，可自行用插件实现需求。'
    UNSUPPORTED_SOCKS_PROXY = '你似乎在设置使用socks代理，暂时不支持这种代理，可自行用插件实现需求。'
    NOT_SUPPORT_DOWNLOAD = '浏览器版本太低无法使用下载管理功能。'
    FILE_NAME = '文件名'
    FOLDER_PATH = '目录路径'
    UNKNOWN = '未知'
    DOWNLOAD_COMPLETED = '下载完成'
    COMPLETED_AND_RENAME = '完成并重命名'
    OVERWROTE = '已覆盖'
    DOWNLOAD_CANCELED = '下载取消'
    SKIPPED = '已跳过'

    @classmethod
    def get(cls, item):
        return getattr(cls, item, item) if isinstance(item, str) and item.isupper() else item

    @classmethod
    def join(cls, *args, **kwargs):
        kwargs['VERSION'] = __version__
        main = ('\n' + args[0].format(*[i for i in args[1:]])) if args else ''
        msg = ('\n' + '\n'.join([f'{cls.get(k)}: {v}' for k, v in kwargs.items()]))
        return f'{main}{msg}'


class English(Texts):
    # --------- 参数名 ---------
    VERSION = 'Version'
    INFO = 'Information'
    METHOD = 'Method'
    ARGS = 'Arguments'
    ARG = 'Argument'
    BROWSER_VER = 'Browser Version'
    PATH = 'Path'
    VALUE = 'Value'
    ALLOW_VAL = 'Allow Value'
    CURR_VAL = 'Current Value'
    ALLOW_TYPE = 'Allow Type'
    CURR_TYPE = 'Current Type'
    TIP = 'Tip'
    ADDRESS = 'Address'
    LOCATOR = 'Locator'
    ALL_TABS = 'All Tabs'

    # --------- 异常默认文本 ---------
    ELEMENTNOTFOUNDERROR = 'No element found.'
    ALERTEXISTSERROR = 'An unprocessed dialog box exists.'
    CONTEXTLOSTERROR = 'The page is refreshed. Please wait until the page is refreshed or loaded.'
    ELEMENTLOSTERROR = ('The element object is invalid. This may be an overall refresh of the page, or a partial js '
                        'refresh to replace or remove elements.')
    CDPERROR = 'Method call error.'
    PAGEDISCONNECTEDERROR = 'The connection to the page has been disconnected.'
    JAVASCRIPTERROR = 'JavaScript running error.'
    NORECTERROR = 'This element has no location or size.'
    BROWSERCONNECTERROR = 'The browser connection fails.'
    NORESOURCEERROR = 'The element has no saved content or failed to save.'
    CANNOTCLICKERROR = 'The element does not scroll to the viewport or is blocked and cannot be clicked.'
    GETDOCUMENTERROR = 'Failed to obtain the document. Procedure'
    WAITTIMEOUTERROR = 'Wait for failure.'
    INCORRECTURLERROR = 'Invalid url.'
    LOCATORERROR = 'Invalid locator format.',
    STORAGEERROR = 'Cannot manipulate the currently stored data.'
    COOKIEFORMATERROR = 'The cookie format is incorrect.'
    TARGETNOTFOUNDERROR = 'The specified page cannot be found.'

    # --------- 异常信息 ---------
    NO_AVAILABLE_PORT_FOUND = 'No available port found.'
    WIN_SYS_ONLY = 'This method can be used only on Windows.'
    NEED_LIB_ = 'Please install {} first.'
    INVALID_URL = 'Invalid url, maybe add "http://"?'
    INVALID_HEADER_NAME = 'Invalid header name.'
    NOT_A_FUNCTION = 'The passed js cannot be parsed into a function.'
    METHOD_NOT_FOUND = 'The function is not found, the method is wrong or your browser is too old.'
    NO_RESPONSE = 'Time out. Maybe the browser is stuck.'
    UNKNOWN_ERR = 'An unknown error occurred.'
    FEEDBACK = ('This error may mean that there is a bug in the program, please inform the author of the error '
                'message and how to reproduce it, thank you.\n'
                'Report url: https://gitee.com/g1879/DrissionPage/issues')
    INI_NOT_FOUND = 'The ini file does not exist.'
    EXT_NOT_FOUND = 'The plug-in path does not exist.'
    WAITING_FAILED_ = 'Wait for {} failed ({} seconds).'
    GET_OBJ_FAILED = 'Failed to obtain the object. Procedure'
    INCORRECT_VAL_ = 'The {} parameter value is incorrect.'
    INCORRECT_TYPE_ = 'The {} parameter type is incorrect.'
    CONNECT_ERR = 'The connection is abnormal.'
    BROWSER_CONNECT_ERR1_ = ('Browser connect failed, check whether the port {} is a browser and '
                             '"--remote-debugging-port={}" startup item is added.')
    BROWSER_CONNECT_ERR2 = 'The browser connection failed. Please ensure that the browser is started.'
    BROWSER_EXE_NOT_FOUND = 'The browser executable file path cannot be found. Please configure it manually.'
    BROWSER_NOT_FOUND = 'Browser not found.'
    BROWSER_NOT_EXIST = 'The browser is not started or closed.'
    BROWSER_DISCONNECTED = 'The browser is closed or the link is broken.'
    BROWSER_NOT_FOR_CONTROL = 'The browser version is too old or this browser does not support takeover.'
    UNSUPPORTED_CSS_SYNTAX = 'This css selector syntax is not supported, please replace it with xpath.'
    UNSUPPORTED_ARG_TYPE_ = 'The type of parameter {} is not supported: {}.'
    UPGRADE_WS = 'Upgrade the websocket-client library.'
    INI_NOT_SET = 'ini_path is not set.'
    INVALID_XPATH_ = 'Invalid xpath statement: {}'
    INVALID_CSS_ = 'Invalid css selector statement: {}'
    INDEX_FORMAT = 'The serial number must be a number or slice.'
    LOC_NOT_FOR_FRAME = 'This locator does not point to the frame element.'
    NEED_DOWNLOAD_PATH = 'You need to explicitly set the download path for this function.'
    GET_WINDOW_SIZE_FAILED = 'Failed to obtain window information. Procedure'
    SET_FAILED_ = 'The argument {} setting failed.'
    NOT_LISTENING = 'Listening is not started or stopped.'
    NOT_BLOB = 'The link is not of blob type.'
    CANNOT_INPUT_FILE = 'This input field cannot handle. Instead, set the input path to the <input> element.'
    NO_SUCH_KEY_ = 'There is no button: {}'
    NO_NEW_TAB = 'Failed to wait for new tab.'
    NO_SUCH_TAB = 'The specified tab was not found.'
    NEED_DOMAIN = 'You need to set a domain or url value. If the url value is set, it must start with http.'
    NEED_DOMAIN2 = 'The cookie must have a "domain" or "url" field.'
    NEED_ARG_ = '{} must be set.'
    SAVE_PATH_MUST_BE_FOLDER = 'save_path must be a folder.'
    GET_PDF_FAILED = 'The save fails because the browser version may not support it.'
    GET_BLOB_FAILED = 'The resource cannot be retrieved.'
    NO_SRC_ATTR = 'The element does not have a src value or the value is empty.'
    D_MODE_ONLY = 'The url, domain, and path parameters are valid only in d mode.'
    S_MODE_ONLY = 'The following parameters take effect only in s mode:'
    STATUS_CODE_ = 'Status Code: {}'
    TAB_OBJ_EXISTS = ('There is already a non-mixtab version of this tab. If multiple objects are common, '
                      'use Settings.set_singleton_tab_obj(False).')
    ONLY_ENGLISH = 'Only English path and file name are supported when converting to video.'
    SELECT_ONLY = 'The select method can only be used on <select> elements.'
    MULTI_SELECT_ONLY = 'You can only do this from the multiple select element.'
    OPTION_NOT_FOUND = 'The specified option was not found.'
    STR_FOR_SINGLE_SELECT = 'Single-choice select element can only be passed in str format.'
    JS_RUNTIME_ERR = 'The js runtime environment is faulty.'
    TIMEOUT_ = 'Wait for {} timeout ({} seconds).'
    JS_RESULT_ERR = 'js result parsing error.'
    S_MODE_GET_FAILED = 'S mode access fails, please set go=False and construct connection parameters for access.'
    ZERO_PAGE_SIZE = 'The page size is 0, please try to wait for the page to load.'
    CONTENT_IS_EMPTY = 'The returned content is empty.'
    FIND_ELE_ERR = 'Find element exceptions.'
    SYMBOL_CONFLICT = '"@@" and "@|" cannot appear in the same location statement.'
    INVALID_LOC = 'Unrecognized locator.'
    LOC_LEN = 'The length of the locator must be 2.'
    INCORRECT_SIGN_ = 'Incorrect symbol: {}'
    DOMAIN_NOT_SET = 'No domain name is set, please set the domain parameter of the cookie or visit a website first.'

    # --------- 参数内容 ---------
    ELE_DISPLAYED = 'element display'
    ELE_LOADED = 'element loaded'
    PAGE_LOADED = 'page loaded'
    NEW_TAB = 'new tab'
    DATA_PACKET = 'data packet'
    ELE_HIDDEN_DEL = 'element is hidden or deleted'
    ELE_DEL = 'element be deleted'
    ELE_HAS_RECT = 'element has size and position'
    ELE_HIDDEN = 'element hidden'
    ELE_CLICKABLE = 'element clickable'
    ELE_COVERED = 'element is covered'
    ELE_NOT_COVERED = 'element is not covered'
    ELE_AVAILABLE = 'element available'
    ELE_NOT_AVAILABLE = 'element not available'
    ELE_STOP_MOVING = 'element stop moving'
    ELE_STATE_CHANGED_ = 'Failed to wait for element state change ({} seconds).'
    RUN_BY_ADMIN = 'Try to run with administrator rights.'
    BROWSER_CONNECT_ERR_INFO = ('\n1, the user folder does not conflict with the open browser \n'
                                '2, if no interface system, please add \'--headless=new\' startup parameter \n'
                                '3, if the system is Linux, try adding \'--no-sandbox\' boot parameter \n'
                                'The port and user folder paths can be set using ChromiumOptions.')
    # ALLOW
    LOC_OR_IND = 'A locator (str or tuple of length 2) or serial number.'
    STR_ONLY = 'Str format and not support xpath or css selector.'
    LOC_FORMAT = 'str or tuple of length 2'
    ELE_OR_LOC = 'A locator (str or tuple of length 2) or element.'
    FRAME_LOC_FORMAT = 'locator, iframe serial number, id, name, ChromiumFrame object'
    SET_DOWNLOAD_PATH = 'Use the set.download_path() method, configuration object, or ini file.'
    SET_WINDOW_NORMAL = ('When the browser is in full screen or minimized state, call set.window.normal() '
                         'first to restore the normal state.')
    HTML_ELE_TYPE = 'Element, Tab object, or html text'
    ELE_LOC_FORMAT = '(x, y) format coordinates, or ChromiumElement objects'
    IP_OR_OPTIONS = 'ip:port format character string or ChromiumOptions type'

    TAB_OR_ID = 'Tab object or tab id'
    RUN_JS = 'run js'
    PAGE_CONNECT = 'Page connection'
    NEW_ELE_INFO = 'html text, or tuple format: (tag, {name: value}).'
    DICT_TO_NEW_ELE = ('This page does not support new elements in html format. Please pass the html_or_info '
                       'parameter with dict.')

    # --------- print ---------
    RETRY = 'Retry'
    OPTIONS_HAVE_SAVED = 'The configuration is saved to a file'
    AUTO_LOAD_TIP = 'Later the program can automatically load the configuration from the file'
    STOP_RECORDING = 'Stop recording.'
    START_RECORD = 'Start recording.'
    CHOOSE_RECORD_TARGET = 'Manually select the target you want to record.'
    UNSUPPORTED_USER_PROXY = ('You seem to be setting up a proxy that uses the account password, which is not '
                              'supported for the time being, and can be implemented by the plug-in itself.')
    UNSUPPORTED_SOCKS_PROXY = ('You seem to be setting up the use of socks proxy, this proxy is not supported for the '
                               'time being, you can use your own plug-in to achieve the requirements.')
    NOT_SUPPORT_DOWNLOAD = 'The browser version is too low to use the download management function.'
    FILE_NAME = 'File Name'
    FOLDER_PATH = 'Folder Path'
    UNKNOWN = 'Unknown'
    DOWNLOAD_COMPLETED = 'Complete'
    COMPLETED_AND_RENAME = 'Renamed'
    OVERWROTE = 'Overwrote'
    DOWNLOAD_CANCELED = 'Canceled'
    SKIPPED = 'Skipped'
