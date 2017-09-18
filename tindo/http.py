# -*- coding:utf-8 -*-
"""
some http errors
"""
import re
import urllib


RE_RESPONSE_STATUS = re.compile(r'^\d\d\d\s.*$')

# all known response status

RESPONSE_STATUSES = {
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


RESPONSE_HEADERS = (
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


RESPONSE_HEADER_DICT = dict(zip(
                map(lambda x: x.upper(), RESPONSE_HEADERS),
                RESPONSE_HEADERS))


HEADER_X_POWERED_BY = ('X-Powered-By', 'tindo/1.0')


class HttpError(Exception):
    def __init__(self, code):
        super(HttpError, self).__init__()
        self.status = '%d %s' % (code, RESPONSE_STATUSES[code])
        self._headers = [HEADER_X_POWERED_BY]

    def header(self, name, value):
        self._headers.append((name, value))

    @property
    def headers(self):
        return self._headers

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


def bad_request():
    raise HttpError(400)


def unauthorized():
    raise HttpError(401)


def forbidden():
    raise HttpError(403)


def not_found():
    raise HttpError(404)


def conflict():
    raise HttpError(409)


def internal_error():
    raise HttpError(500)


def redirect(location):
    raise RedirectError(301, location)


def found(location):
    raise RedirectError(302, location)


def see_other(location):
    raise RedirectError(303, location)


def to_str(s):
    """Convert to bytes
    :param s: str or unicode
    :return: str
    """
    if isinstance(s, str):
        return s
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return str(s)


def to_unicode(s, encoding='utf-8'):
    """Convert to unicode
    :param s: str or unicode
    :param encoding: encode type
    :return: unocide
    """
    return s.decode(encoding)


def quote(s, encoding='utf-8'):
    """
    url quote to str.
    :param s: url
    :param encoding: encoding type
    :return: quote
    """
    if isinstance(s, unicode):
        s = s.encode(encoding)
    return urllib.quote(s)


def unquote(s, encoding='utf-8'):
    """
    url unquote as unicode
    :param s: unicode
    :param encoding: encoding type
    :return: str type
    """
    return urllib.unquote(s).decode(encoding)
