# coding: utf-8

try:
    import httplib
except ImportError:
    import http.client as httplib

import urllib
import time
import hashlib
import json
import itertools
import mimetypes

'''
定义一些系统变量
'''

SYSTEM_GENERATE_VERSION = "taobao-sdk-python-20160927"

P_APP_KEY = "app_key"
P_API = "method"
P_SESSION = "session"
P_ACCESS_TOKEN = "access_token"
P_VERSION = "v"
P_FORMAT = "format"
P_TIMESTAMP = "timestamp"
P_SIGN = "sign"
P_SIGN_METHOD = "sign_method"
P_PARTNER_ID = "partner_id"

P_CODE = 'code'
P_SUB_CODE = 'sub_code'
P_MSG = 'msg'
P_SUB_MSG = 'sub_msg'

N_REST = '/router/rest'
URL_REGEX = 'http://%s/router/rest'


def sign(secret, parameters):
    # ===========================================================================
    # 签名方法
    # @param secret: 签名需要的密钥
    # @param parameters: 支持字典和string两种
    #
    # ===========================================================================
    # 如果parameters 是字典类的话
    if hasattr(parameters, "items"):
        keys = parameters.keys()
        keys.sort()
        parameters = "%s%s%s" % (secret, str().join('%s%s' % (key, parameters[key]) for key in keys), secret)
    # print parameters
    sign_str = hashlib.md5(parameters).hexdigest().upper()
    return sign_str


def mix_str(_str):
    if isinstance(_str, str):
        return _str
    elif isinstance(_str, unicode):
        return _str.encode('utf-8')
    else:
        return str(_str)


class FileItem(object):
    def __init__(self, filename=None, content=None):
        self.filename = filename
        self.content = content


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = "PYTHON_SDK_BOUNDARY"
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, str(value)))
        return self

    def add_file(self, field_name, filename, file_handle, mime_type=None):
        """Add a file to be uploaded."""
        body = file_handle.read()
        if mime_type is None:
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((mix_str(field_name), mix_str(filename), mix_str(mime_type), mix_str(body)))
        return

    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary

        # Add the form fields
        parts.extend(
            [
                part_boundary,
                'Content-Disposition: form-data; name="%s"' % name,
                'Content-Type: text/plain; charset=UTF-8',
                '',
                value,
            ]
            for name, value in self.form_fields
        )

        # Add the files to upload
        parts.extend(
            [
                part_boundary,
                'Content-Disposition: file; name="%s"; filename="%s"' % (field_name, filename),
                'Content-Type: %s' % content_type,
                'Content-Transfer-Encoding: binary',
                '',
                body,
            ]
            for field_name, filename, content_type, body in self.files
        )

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


class TopException(Exception):
    def __init__(self):
        self.error_code = None
        self.message = None
        self.sub_code = None
        self.sub_msg = None
        self.application_host = None
        self.service_host = None

    def parse_error(self, response, json_obj):
        if P_CODE in json_obj["error_response"]:
            self.error_code = json_obj["error_response"][P_CODE]
        if P_MSG in json_obj["error_response"]:
            self.message = json_obj["error_response"][P_MSG]
        if P_SUB_CODE in json_obj["error_response"]:
            self.sub_code = json_obj["error_response"][P_SUB_CODE]
        if P_SUB_MSG in json_obj["error_response"]:
            self.sub_msg = json_obj["error_response"][P_SUB_MSG]
            self.application_host = response.getheader("Application-Host", "")
            self.service_host = response.getheader("Location-Host", "")

    def __str__(self, *args, **kwargs):
        sb = "error_code=" + mix_str(self.error_code) + \
             " message=" + mix_str(self.message) + \
             " sub_code=" + mix_str(self.sub_code) + \
             " sub_msg=" + mix_str(self.sub_msg) + \
             " application_host=" + mix_str(self.application_host) + \
             " service_host=" + mix_str(self.service_host)
        return sb


class RequestException(Exception):
    pass


class XmRequest(object):
    def __init__(self, method='POST', url='gw.api.taobao.com'):
        self.method = method
        self.url = url
        self.body = None
        self.headers = None

    def set_body(self, b):
        self.body = b

    def set_headers(self, h):
        self.headers = h

    def get_body(self):
        return self.body

    def get_headers(self):
        return self.headers


def set_request_header(form):
    header = {
        'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        "Cache-Control": "no-cache",
        "Connection": "Keep-Alive",
    }
    if form:
        header['Content-type'] = form.get_content_type()
    return header


class BaseApi():
    def __init__(self, app_info, env="default"):
        # 初始化基类
        # 开放属性会被转化为请求参数 都 设置为私有属性 __xxx
        if env == "default":
            self.__domain = "gw.api.taobao.com"
        else:
            self.__domain = "gw.api.tbsandbox.com"

        self.__http_method = "POST"

        self.__app_key = app_info.appkey
        self.__secret = app_info.secret

        self.__sys_params = {
            P_APP_KEY: self.__app_key,
            P_TIMESTAMP: str(long(time.time() * 1000)),
            P_VERSION: '2.0',
            P_FORMAT: 'json',
            P_SIGN_METHOD: "md5",
            P_PARTNER_ID: SYSTEM_GENERATE_VERSION,
        }

        self.__translate_map = {}
        self.__multipart_params = None

    def set_api(self, method):
        self.__sys_params[P_API] = method

    def set_translate_params(self, tm):
        self.__translate_map = tm

    def set_multipart_params(self, mp):
        self.__multipart_params = mp

    def __check_request(self):
        pass

    def __get_api_params(self):
        """将对象的属性转化为 请求参数 私有参数不转化"""
        params = self.__dict__
        ps = {}
        # 查询翻译字典来规避一些关键字属性
        translate_parameter = self.__translate_map
        for key, value in params.iteritems():

            if key.startswith("_"):
                continue
            if key in translate_parameter:
                ps[translate_parameter[key]] = params[key]

            else:
                ps[key] = params[key]
        return ps

    def __set_sign(self):
        sign_params = self.__sys_params.copy()
        customize_params = self.__get_api_params()
        sign_params.update(customize_params)
        self.__sys_params[P_SIGN] = sign(self.__secret, sign_params)

    def __get_request_params(self):
        customize_params = self.__get_api_params()
        self.__set_sign()
        customize_params.update(self.__sys_params)
        return customize_params

    def _format_multipart_params(self, m_params):

        form = MultiPartForm()
        for key, value in self.__get_request_params():
            form.add_field(key, value)

        for key in m_params:
            file_item = getattr(self, key)
            if file_item and isinstance(file_item, FileItem):
                form.add_file(key, file_item.filename, file_item.content)
        return form

    def __make_request(self):
        xm_request = XmRequest(self.__http_method, self.__domain)
        m_params = self.__multipart_params

        self.__request_params = self.__get_request_params()
        if m_params:
            form = self._format_multipart_params(m_params)
            body = str(form)
            xm_request.set_headers(set_request_header(form))
            xm_request.set_body(body)
        else:
            body = urllib.urlencode(self.__request_params)
            xm_request.set_headers(set_request_header(None))
            xm_request.set_body(body)
        return xm_request

    def get_response(self, auth=None, timeout=30):
        if auth is not None:
            self.__sys_params[P_SESSION] = auth

        req = self.__make_request()

        url = N_REST + "?" + urllib.urlencode(self.__request_params)
        connection = httplib.HTTPConnection(self.__domain, 80, False, timeout)
        connection.connect()

        connection.request(self.__http_method, url, body=req.get_body(), headers=req.get_headers())
        response = connection.getresponse()

        if response.status is not 200:
            raise RequestException('invalid http status ' + str(response.status) + ',detail body:' + response.read())
        result = response.read()

        json_obj = json.loads(result)
        if 'error_response' in json_obj:
            error = TopException()
            error.parse_error(response, json_obj)
            raise error

        return json_obj

