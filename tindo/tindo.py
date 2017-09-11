# -*- coding:utf-8 -*-
"""
A simple WSGI-compatible web framework
"""
import datetime
import re
import urllib
import threading
import os
import mimetypes
import cgi


class Dict(dict):
    """extend dict but support attribute getter and setter
    """
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("Dict object has no attribute %s" % key)

    def __setattr__(self, key, value):
        self[key] = value


ctx = threading.local()


_TIMEDELTA_ZERO = datetime.timedelta(0)


_RE_TZ = re.compile(r'^([\+\-])([0-9]{1,2})\:([0-9]{1,2})$')


class UTC(datetime.tzinfo):
    """A UTC tzinfo object
    """
    def __init__(self, utc):
        utc = str(utc.strip().upper())
        mt = _RE_TZ.match(utc)
        if mt:
            minus = mt.group(1) == '-'
            h = int(mt.group(2))
            m = int(mt.group(3))
            if minus:
                h, m = (-h), (-m)
            self._utf_offset = datetime.timedelta(hours=h, minutes=m)
            self._tzname = 'UTC%s' % utc
        else:
            raise ValueError('bad utc time zone')

    def utcoffset(self, dt):
        return self._utf_offset

    def dst(self, dt):
        return _TIMEDELTA_ZERO

    def tzname(self, dt):
        return self._tzname

    def __str__(self):
        return 'UTC tzinfo object (%s)' % self._tzname

    __repr__ = __str__

_RE_RESPONSE_STATUS = re.compile(r'^\d\d\d(\[\w\]+)?$')

# all known response status
_RESPONSE_STATUSES = {
    # Informational
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',

    # Successful
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non_Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi Status',
    226: 'IM Used',

    # Redirected
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: 'Temporary Redirect',

    # Client Error
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Accepted',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    418: "I'm a teapot",
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    426: 'Upgrade Required',

    # Server Error
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP version Not Support',
    507: 'Insufficient Storage',
    508: 'Not Extended',
}


_RESPONSE_HEADERS = (
    'Accept-Ranges',
    'Age',
    'Allow',
    'Cache-Control',
    'Connection',
    'Content-Encoding',
    'Content-Language',
    'Content-Length',
    'Content-Location',
    'Content-MD5',
    'Content-Disposition',
    'Content-Range',
    'Content-Type',
    'Date',
    'ETag',
    'Expires',
    'Last-Modified',
    'Link',
    'Location',
    'P3P',
    'Pragma',
    'Proxy-Authenticate',
    'Refresh',
    'Retry-After',
    'Server',
    'Set-Cookie',
    'Strict-Transport-Security',
    'Trailer',
    'Transfer-Encoding',
    'Vary',
    'Via',
    'Warning',
    'WWW-Authenticate',
    'X-Frame-Options',
    'X-XSS-Protection',
    'X-Content-Type-Options',
    'X-Forwarded-Proto',
    'X-Powered-By',
    'X-UA-Compatible',
)


_RESPONSE_HEADER_DICT = dict(zip(
                map(lambda x: x.upper(), _RESPONSE_HEADERS),
                _RESPONSE_HEADERS))


_HEADER_X_POWERED_BY = ('X-Powered-By', 'transwarp/1.0')


class HttpError(Exception):
    def __init__(self, code):
        super(HttpError, self).__init__()
        self.status = '%d %s' % (code, _RESPONSE_STATUSES[code])

    def header(self, name, value):
        if not hasattr(self, '_headers'):
            self._headers = [_HEADER_X_POWERED_BY]
        self._headers.append((name, value))

    @property
    def headers(self):
        if hasattr(self, '_headers'):
            return self._headers
        return []

    def __str__(self):
        return self.status

    __repr__ = __str__


class RedirectError(HttpError):
    def __init__(self, code, location):
        super(RedirectError, self).__init__(code)
        self.location = location

    def __str__(self):
        return '%s, %s' % (self.status, self.location)

    __repr__ = __str__


def badrequest():
    return HttpError(400)


def unauthorized():
    return HttpError(401)


def forbidden():
    return HttpError(403)


def notfound():
    return HttpError(404)


def conflict():
    return HttpError(409)


def internalerror():
    return HttpError(500)


def redirect(location):
    return RedirectError(301, location)


def found(location):
    return RedirectError(302, location)


def seeother(location):
    return RedirectError(303, location)


def _to_str(s):
    """Convert to bytes
    :param s: str or unicode
    :return: str
    """
    if isinstance(s, str):
        return s
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return str(s)


def _to_unicode(s, encoding='utf-8'):
    """Convert to unicode
    :param s: str or unicode
    :param encoding: encode type
    :return: unocide
    """
    return s.decode(encoding)


def _quote(s, encoding='utf-8'):
    """
    url quote to str.
    :param s: url
    :param encoding: encoding type
    :return: quote
    """
    if isinstance(s, unicode):
        s = s.encode(encoding)
    return urllib.quote(s)


def _unquote(s, encoding='utf-8'):
    """
    url unquote as unicode
    :param s: unicode
    :param encoding: encoding type
    :return: str type
    """
    return urllib.unquote(s).decode(encoding)


def get(path):
    """
     A @get decorator
    :param path: the path
    :return:
    """
    def _decorator(func):
        func.__web_route__ = path
        func.__web_method__ = 'GET'
        return func
    return _decorator


def post(path):
    """
    A @post decorator
    :param path: the path
    :return:
    """
    def _decorator(func):
        func.__web_route__ = path
        func.__web_method__ = 'POST'
        return func
    return _decorator


_re_route = re.compile(r'(\:[a-zA-Z_]\w*)')


def _build_regex(path):
    """
    build path regex
    :param path: the path
    :return: regex pattern
    """
    re_list = ['^']
    var_list = []
    is_var = False
    for v in _re_route.split(path):
        if is_var:
            var_name = v[1:]
            var_list.append(var_name)
            re_list.append(r'(?P<%s>[^\/]+)' % var_name)
        else:
            s = ''
            for ch in v:
                if '0' <= ch <= '9':
                    s = s + ch
                elif 'A' <= ch <= 'Z':
                    s = s + ch
                elif 'a' <= ch <= 'z':
                    s = s + ch
                else:
                    s = s + '\\' + ch
            re_list.append(s)
        is_var = not is_var
    re_list.append('$')
    return ''.join(re_list)


class Route(object):
    """
    A Route object is callable object.
    """

    def __init__(self, func):
        self.path = func.__web_route__
        self.method = func.__web_route__
        self.is_static = _re_route.search(self.path) is None
        if not self.is_static:
            self.route = re.compile(_build_regex(self.path))
        self.func = func

    def match(self, url):
        m = self.route.match(url)
        if m:
            return m.groups()
        return None

    def __call__(self, *args, **kwargs):
        return self.func(*args)

    def __str__(self):
        if self.is_static:
            return 'Route(static, %s, path=%s)' % (self.method, self.path)
        return 'Route(dynamic, %s, path=%s)' % (self.method, self.path)

    __repr__ = __str__


def _static_file_generator(file_path):
    block_size = 8192
    with open(file_path, 'rb') as f:
        block = f.read(block_size)
        while block:
            yield block
            block = f.read(block_size)


class StaticFileRoute(object):
    def __int__(self):
        self.method = 'GET'
        self.is_static = False
        self.route = re.compile('^/static/(.+)$')

    def match(self, url):
        if url.startswith('/static/'):
            return url[1:],
        return None

    def __call__(self, *args, **kwargs):
        fpath = os.path.join(ctx.application.document_root, args[0])
        if not os.path.isfile(fpath):
            raise notfound()
        fext = os.path.splitext(fpath)[1]
        ctx.response.content_type = mimetypes.types_map.get(fext.lower(), 'application/octet-stream')
        return _static_file_generator(fpath)


def favicon_handler():
    return _static_file_generator('/favicon.ico')


class MultipartFile(object):
    """Multipart file storage get from request input.
    """
    def __init__(self, storage):
        self.filename = _to_unicode(storage.filename)
        self.file = storage.file


class Request(object):
    """
     Request object for obtaining all http request information.
    """
    def __init__(self, environ):
        self._environ = environ

    def _parse_input(self):
        def _convert(item):
            if isinstance(item, list):
                return [_to_unicode(i.value) for i in item]
            if item.filename:
                return MultipartFile(item)
            return _to_unicode(item.value)
        fs = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ, keep_blank_values=True)
        inputs = dict()
        for key in fs:
            inputs[key] = _convert(fs[key])
        return inputs

    def _get_raw_input(self):
        """
        Get raw input as dict containing values as unicode, list or MultipartFile.
        :return:
        """
        if not hasattr(self, '_raw_input'):
            self._raw_input = self._parse_input()
        return self._raw_input

    def __getitem__(self, key):
        """
        Get input parameter value. If the specified key has multiple value, the first one is returned.
        If the specified key is not exist, then raise KeyError.
        """
        r = self._get_raw_input()[key]
        if isinstance(r, list):
            return r[0]
        return r

    def get(self, key, default=None):
        """
        The same as request[key], but return default value if key is not found.
        :param key:
        :param default:
        :return:
        """
        r = self._get_raw_input().get(key, default)
        if isinstance(r, list):
            return r[0]
        return r

    def gets(self, key):
        """
        Get multiple values for specified key.
        :param key:
        :return:
        """
        r = self._get_raw_input()[key]
        if isinstance(r, list):
            return r[:]
        return [r]

    def input(self, **kw):
        """
        Get input as dict from request, fill dict using provided default value if key not exist.

        i = ctx.request.input(role='guest')
        i.role ==> 'guest'
        :param kw:
        :return:
        """
        copy = Dict(**kw)
        raw = self._get_raw_input()
        for k, v in raw.iteritems():
            copy[k] = v[0] if isinstance(v, list) else v
        return copy

    def get_body(self):
        """
        Get raw data from HTTP POST and return as str.
        :return:
        """
        fp = self._environ['wsgi.input']
        return fp.read()

    @property
    def remote_addr(self):
        """
        Get remote addr. Return '0.0.0.0' if cannot get remote_addr.
        """
        return self._environ.get('REMOTE_ADDR', '0.0.0.0')

    @property
    def document_root(self):
        """
        Get raw document_root as str. Return '' if no document_root.
        """
        return self._environ.get('DOCUMENT_ROOT', '')

    @property
    def query_string(self):
        """
        Get raw query string as str. Return '' if no query string.
        """
        return self._environ.get('QUERY_STRING', '')

    @property
    def environ(self):
        """
        Get raw environ as dict, both key, value are str.
        """
        return self._environ

    @property
    def request_method(self):
        """
        Get request method. The valid returned values are 'GET', 'POST', 'HEAD'.
        """
        return self._environ['REQUEST_METHOD']

    @property
    def path_info(self):
        """
        Get request path as str.
        """
        return urllib.unquote(self._environ.get('PATH_INFO', ''))

    @property
    def host(self):
        """
        Get request host as str. Default to '' if cannot get host..
        """
        return self._environ.get('HTTP_HOST', '')

    def _get_headers(self):
        if not hasattr(self, '_headers'):
            hdrs = {}
            for k, v in self._environ.iteritems():
                if k.startswith('HTTP_'):
                    # convert 'HTTP_ACCEPT_ENCODING' to 'ACCEPT-ENCODING'
                    hdrs[k[5:].replace('_', '-').upper()] = v.decode('utf-8')
            self._headers = hdrs
        return self._headers

    @property
    def headers(self):
        """
        Get all HTTP headers with key as str and value as unicode. The header names are 'XXX-XXX' uppercase.
        """
        return dict(**self._get_headers())

    def header(self, header, default=None):
        """
        Get header from request as unicode, return None if not exist, or default if specified.
        The header name is case-insensitive such as 'USER-AGENT' or u'content-Type'.
        """
        return self._get_headers().get(header.upper(), default)

    def _get_cookies(self):
        if not hasattr(self, '_cookies'):
            cookies = {}
            cookie_str = self._environ.get('HTTP_COOKIE')
            if cookie_str:
                for c in cookie_str.split(';'):
                    pos = c.find('=')
                    if pos>0:
                        cookies[c[:pos].strip()] = _unquote(c[pos+1:])
            self._cookies = cookies
        return self._cookies

    @property
    def cookies(self):
        """
        Return all cookies as dict. The cookie name is str and values is unicode.
        """
        return Dict(**self._get_cookies())

    def cookie(self, name, default=None):
        """
        Return specified cookie value as unicode. Default to None if cookie not exists.
        """
        return self._get_cookies().get(name, default)


UTC_O = UTC('+00:00')


class Response(object):
    """
    The Response from the web server
    """
    def __init__(self):
        self._status = '200 OK'
        self._headers = {'CONTENT-TYPE': 'text/html; charset=utf-8'}

    @property
    def headers(self):
        L = [(_RESPONSE_HEADER_DICT.get(k, k), v) for k, v in self._headers.iteritems()]
        if hasattr(self, '_cookies'):
            for v in self._cookies.itervalues():
                L.append(('Set-Cookie', v))
        L.append(_HEADER_X_POWERED_BY)
        return L

    def header(self, name):
        key = name.upper()
        if key not in _RESPONSE_HEADER_DICT:
            key = name
        return self._headers.get(key)

    def unset_header(self, name):
        key = name.upper()
        if key not in _RESPONSE_HEADER_DICT:
            key = name
        if key in self._headers:
            del self._headers[key]

    def set_header(self, name, value):
        key = name.upper()
        if key not in _RESPONSE_HEADER_DICT:
            key = name
        self._headers[key] = _to_str(value)

    @property
    def content_type(self):
        return self._headers['CONTENT-TYPE']

    @content_type.setter
    def content_type(self, value):
        if value:
            self.set_header('CONTENT-TYPE', value)
        else:
            self.unset_header('CONTENT-TYPE')

    @property
    def content_length(self):
        return self.header('CONTENT-LENGTH')

    @content_length.setter
    def content_length(self, value):
        self.set_header('CONTENT-LENGTH', str(value))

    def delete_cookie(self, name):
        self.set_cookie(name, '__deleted__', expires=0)

    def set_cookie(self, name, value, max_age=None,
                    expires=None, path='/', domain=None,
                    secure=False, http_only=True):
        if not hasattr(self, '_cookies'):
            self._cookies = {}
        L = ['%s=%s' % (_quote(name), _quote(value))]
        if expires is not None:
            if isinstance(expires, (float, int, long)):
                L.append('Expires=%s' % datetime.datetime.fromtimestamp(expires, UTC_O)
                         .strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
            if isinstance(expires, (datetime.date, datetime.datetime)):
                L.append('Expires=%s' % expires.astimezone(UTC_O).strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
        elif isinstance(max_age, (int, long)):
            L.append('Max-Age=%d' % max_age)
        L.append('Path=%s' % path)
        if domain:
            L.append('Domain=%s' % domain)
        if secure:
            L.append('Secure')
        if http_only:
            L.append('HttpOnly')
        self._cookies[name] = '; '.join(L)

    def unset_cookie(self, name):
        if hasattr(self, '_cookies'):
            if name in self._cookies:
                del self._cookies[name]

    @property
    def status_code(self):
        return int(self._status[:3])

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if isinstance(value, (int, long)):
            if 100 <= value <= 999:
                st = _RESPONSE_STATUSES.get(value, '')
                if st:
                    self._status = '%s %s' % (value, st)
                else:
                    self._status = str(value)
            else:
                raise ValueError('Bad Response code: %d' % value)
        elif isinstance(value, basestring):
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            if _RE_RESPONSE_STATUS.match(value):
                self._status = value
            else:
                raise ValueError('Bad response code: %s' % value)
        else:
            raise TypeError('Bad type of response code.')






