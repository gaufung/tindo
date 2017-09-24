# -*- coding:utf-8 -*-
"""
    tindo

    A micro-framework based on wsgiref

    :copyright: (c) 2017 by Gau Fung
    :license: MIT, see license for more details
"""
import os
import mimetypes
import cgi
import warnings
import types
import StringIO
import traceback
import sys
from threading import Lock
import re
import datetime
import functools
import logging
from uuid import uuid1
from http import RESPONSE_STATUSES, RESPONSE_HEADER_DICT, HEADER_X_POWERED_BY, RE_RESPONSE_STATUS
from http import RedirectError, bad_request, not_found, HttpError
from http import to_str, to_unicode, quote, unquote
from utils import Dict, UTC
from local import Local


ctx = Local()


def route(path, methods=None):
    """
    route decorator
    :param path: the url path
    :param methods: HTTP's Methods, defaults is 'GET'
    :return:
    """
    if methods is None:
        methods = ['GET']

    def _decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__web_route__ = path
        wrapper.__web_method__ = methods
        return wrapper
    return _decorator


def get(path):
    """
     A @get decorator
    :param path: the path
    :return:
    """
    warnings.warn('The method is deprecated, use route instead', stacklevel=2)

    def _decorator(func):
        func.__web_route__ = path
        func.__web_method__ = ['GET']
        return func
    return _decorator


def post(path):
    """
    A @post decorator
    :param path: the path
    :return:
    """
    warnings.warn('The method is deprecated, use route instead', stacklevel=2)

    def _decorator(func):
        func.__web_route__ = path
        func.__web_method__ = ['POST']
        return func
    return _decorator


_re_route = re.compile(r'<([a-zA-Z_]\w*)>')


def _re_char(ch):
    s = ''
    if '0' <= ch <= '9':
        s = s + ch
    elif 'a' <= ch <= 'z':
        s = s + ch
    elif '0' <= ch <= '9':
        s = s + ch
    else:
        s = s + '\\' + ch
    return s


def _build_regex(path):
    """
    build path regex pattern
    '/users/<username>' => '^/user/(?P<username>[^\/]+)$'
    :param path: the path
    :return: regex pattern
    """
    re_list = ['^']
    i = 0
    while i < len(path):
        sub_path = path[i:]
        m = _re_route.match(sub_path)
        if m:
            re_list.append(r'(?P<%s>[^\/]+)' % m.group(1))
            i = i + m.end()
        else:
            re_list.append(_re_char(path[i]))
            i = i+1
    re_list.append('$')
    return ''.join(re_list)


class Route(object):
    """
    A Route object is callable object.
    """

    def __init__(self, func):
        self.path = func.__web_route__
        self.methods = func.__web_method__
        self.route = re.compile(_build_regex(self.path))
        self.func = func

    def match(self, url):
        m = self.route.match(url)
        if m:
            return m.groups()
        return None

    def __call__(self, *args):
        return self.func(*args)

    def __str__(self):
        return '(%s, path=%s)' % (self.methods, self.path)

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
        self.method = ['GET']
        self.is_static = True
        self.route = re.compile('^/static/(.+)$')

    @staticmethod
    def match(url):
        if url.startswith('/static/'):
            return url[1:],
        return None

    def __call__(self, *args, **kwargs):
        file_path = os.path.join(ctx.application.document_root, args[0])
        if not os.path.isfile(file_path):
            raise not_found()
        file_extension = os.path.splitext(file_path)[1]
        ctx.response.content_type = mimetypes.types_map.get(file_extension.lower(), 'application/octet-stream')
        return _static_file_generator(file_path)


def favicon_handler():
    return _static_file_generator('/favicon.ico')


class MultipartFile(object):
    """Multipart file storage get from request input.
    """
    def __init__(self, storage):
        self.filename = to_unicode(storage.filename)
        self.file = storage.file


_SESSIONS_WAREHOUSE = {}

_session_lock = Lock()


def _get_session(session_id):
    """
    get session from the runtime memory, which store as dictionary.
    Using lock to make thread-safe.
    :param session_id: the session id assigned to each request.
    :return: a Dict
    """
    with _session_lock:
        if session_id not in _SESSIONS_WAREHOUSE:
            _SESSIONS_WAREHOUSE[session_id] = Dict()
        return _SESSIONS_WAREHOUSE[session_id]


class Request(object):
    """Request object for obtaining all http request information.
    """
    def __init__(self, environ):
        self._environ = environ

    def _parse_input(self):
        def _convert(item):
            if isinstance(item, list):
                return [to_unicode(i.value) for i in item]
            if item.filename:
                return MultipartFile(item)
            return to_unicode(item.value)
        fs = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ, keep_blank_values=True)
        inputs = dict()
        for key in fs:
            inputs[key] = _convert(fs[key])
        return inputs

    def _get_raw_input(self):
        """Get raw input as dict containing values as unicode, list or MultipartFile.
        :return:
        """
        if not hasattr(self, '_raw_input'):
            self._raw_input = self._parse_input()
        return self._raw_input

    def __getitem__(self, key):
        """Get input parameter value. If the specified key has multiple value, the first one is returned.
        If the specified key is not exist, then raise KeyError.
        """
        r = self._get_raw_input()[key]
        if isinstance(r, list):
            return r[0]
        return r

    def get(self, key, default=None):
        """The same as request[key], but return default value if key is not found.
        :param key:
        :param default:
        :return:
        """
        r = self._get_raw_input().get(key, default)
        if isinstance(r, list):
            return r[0]
        return r

    def gets(self, key):
        """Get multiple values for specified key.
        :param key:
        :return:
        """
        r = self._get_raw_input()[key]
        if isinstance(r, list):
            return r[:]
        return [r]

    def input(self, **kw):
        """Get input as dict from request, fill dict using provided default value if key not exist.
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
        """Get raw data from HTTP POST and return as str.
        :return:
        """
        fp = self._environ['wsgi.input']
        return fp.read()

    @property
    def remote_addr(self):
        """Get remote addr Return '0.0.0.0' if cannot get remote_addr.
        """
        return self._environ.get('REMOTE_ADDR', '0.0.0.0')

    @property
    def document_root(self):
        """Get raw document_root as str. Return '' if no document_root.
        """
        return self._environ.get('DOCUMENT_ROOT', '')

    @property
    def query_string(self):
        """Get raw query string as str. Return '' if no query string.
        """
        return self._environ.get('QUERY_STRING', '')

    @property
    def environ(self):
        """Get raw environ as dict, both key, value are str.
        """
        return self._environ

    @property
    def request_method(self):
        """Get request method. The valid returned values are 'GET', 'POST', 'HEAD'.
        """
        return self._environ['REQUEST_METHOD']

    @property
    def path_info(self):
        """Get request path as str.
        """
        return unquote(self._environ.get('PATH_INFO', ''))

    @property
    def host(self):
        """Get request host as str. Default to '' if cannot get host..
        """
        return self._environ.get('HTTP_HOST', '')

    def _get_headers(self):
        if not hasattr(self, '_headers'):
            headers = {}
            for k, v in self._environ.iteritems():
                if k.startswith('HTTP_'):
                    # convert 'HTTP_ACCEPT_ENCODING' to 'ACCEPT-ENCODING'
                    headers[k[5:].replace('_', '-').upper()] = v.decode('utf-8')
            self._headers = headers
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
        """
        HTTP_COOKIE: theme=light; sessionToken=abc123; value=10
        :return:
        """
        if not hasattr(self, '_cookies'):
            cookies = {}
            cookie_str = self._environ.get('HTTP_COOKIE')
            if cookie_str:
                for c in cookie_str.split(';'):
                    pos = c.find('=')
                    if pos > 0:
                        cookies[c[:pos].strip()] = unquote(c[pos+1:])
            self._cookies = cookies
        return self._cookies

    @property
    def cookies(self):
        """Return all cookies as dict. The cookie name is str and values is unicode.
        """
        return Dict(**self._get_cookies())

    def cookie(self, name, default=None):
        """Return specified cookie value as unicode. Default to None if cookie not exists.
        """
        return self._get_cookies().get(name, default)

    @property
    def session(self):
        sessionid = self.cookie('sessionid')
        if sessionid is not None:
            return _get_session(sessionid)


UTC_0 = UTC('+00:00')


class Response(object):
    """
    The Response from the web server
    """
    def __init__(self):
        self._status = '200 OK'
        self._headers = {'CONTENT-TYPE': 'text/html; charset=utf-8'}

    @property
    def headers(self):
        _headers = [(RESPONSE_HEADER_DICT.get(k, k), v) for k, v in self._headers.iteritems()]
        if hasattr(self, '_cookies'):
            for v in self._cookies.itervalues():
                _headers.append(('Set-Cookie', v))
        _headers.append(HEADER_X_POWERED_BY)
        return _headers

    def header(self, name):
        key = name.upper()
        if key not in RESPONSE_HEADER_DICT:
            key = name
        return self._headers.get(key)

    def unset_header(self, name):
        key = name.upper()
        if key not in RESPONSE_HEADER_DICT:
            key = name
        if key in self._headers:
            del self._headers[key]

    def set_header(self, name, value):
        key = name.upper()
        if key not in RESPONSE_HEADER_DICT:
            key = name
        self._headers[key] = to_str(value)

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
                   expires=None, path='/', domain='localhost:9000',
                   secure=False, http_only=True):
        if not hasattr(self, '_cookies'):
            self._cookies = {}
        cookies = ['%s=%s' % (quote(name), quote(value))]
        if expires is not None:
            if isinstance(expires, (float, int, long)):
                cookies.append('Expires=%s' % datetime.datetime.fromtimestamp(expires, UTC_0)
                         .strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
            if isinstance(expires, (datetime.date, datetime.datetime)):
                cookies.append('Expires=%s' % expires.astimezone(UTC_0).strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
        elif isinstance(max_age, (int, long)):
            cookies.append('Max-Age=%d' % max_age)
        cookies.append('Path=%s' % path)
        if domain:
            cookies.append('Domain=%s' % domain)
        if secure:
            cookies.append('Secure')
        if http_only:
            cookies.append('HttpOnly')
        self._cookies[name] = '; '.join(cookies)

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
                st = RESPONSE_STATUSES.get(value, '')
                if st:
                    self._status = '%s %s' % (value, st)
                else:
                    self._status = str(value)
            else:
                raise ValueError('Bad Response code: %d' % value)
        elif isinstance(value, basestring):
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            if RE_RESPONSE_STATUS.match(value):
                self._status = value
            else:
                raise ValueError('Bad response code: %s' % value)
        else:
            raise TypeError('Bad type of response code.')

    @property
    def session(self):
        if ctx.request.session is None:
            sessionid = str(uuid1())
            self.set_cookie('sessionid', sessionid)
        else:
            sessionid = ctx.request.cookie('sessionid')
            self.set_cookie('sessionid', sessionid)
        return _get_session(sessionid)


class Template(object):
    def __init__(self, template_name, **kw):
        self.template_name = template_name
        self.model = dict(**kw)


class TemplateEngine(object):
    def __call__(self, path, model):
        return '<!-- override this method to render template -->'


class Jinja2TemplateEngine(TemplateEngine):
    def __init__(self, templ_dir, **kw):
        from jinja2 import Environment, FileSystemLoader
        if 'autoescape' not in kw:
            kw['autoescape'] = True
        self._env = Environment(loader=FileSystemLoader(templ_dir), **kw)

    def add_filter(self, name, fn_filter):
        self._env.filters[name] = fn_filter

    def __call__(self, path, model):
        return self._env.get_template(path).render(**model).encode('utf-8')


def view(path):
    """
    A view decorator that render a view by dict.
    :param path: path
    :return:
    """
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kw):
            r = func(*args, **kw)
            if isinstance(r, dict):
                logging.info('Return Template')
                return Template(path, **r)
            raise ValueError('Expect return a dict when using @view() decorator.')
        return _wrapper
    return _decorator


def _load_module(module_name):
    last_dot = module_name.rfind('.')
    if last_dot == (-1):
        return __import__(module_name, globals(), locals())
    from_module = module_name[:last_dot]
    import_module = module_name[last_dot+1:]
    m = __import__(from_module, globals(), locals(), [import_module])
    return getattr(m, import_module)


class Tindo(object):
    def __init__(self, document_root, template_engine=None, debug=True, **kw):
        self._running = False
        self._document_root = document_root
        self._debug = debug

        self._template_engine = Jinja2TemplateEngine(
            os.path.join(self._document_root, 'templates')) if template_engine is None else None

        self._get_dynamic = []
        self._post_dynamic = []
        self._get_dynamic.append(StaticFileRoute())

    def _check_not_running(self):
        if self._running:
            raise RuntimeError('Cannot modify the tindo when running')

    @property
    def template_engine(self):
        return self._template_engine

    @template_engine.setter
    def template_engine(self, engine):
        self._check_not_running()
        self._template_engine = engine

    def add_module(self, mod):
        self._check_not_running()
        m = mod if isinstance(mod, types.ModuleType) else _load_module(mod)
        logging.info('Add module: %s' % m.__name__)
        for name in dir(m):
            fn = getattr(m, name)
            if callable(fn) and hasattr(fn, '__web_route__') and hasattr(fn, '__web_method__'):
                self.add_url(fn)

    def add_url(self, func):
        self._check_not_running()
        r = Route(func)
        if 'GET' in r.methods:
            self._get_dynamic.append(r)
        if 'POST' in r.methods:
            self._post_dynamic.append(r)
        logging.info('Add route: %s' % str(r))

    def run(self, port=9000, host='127.0.0.1'):
        from werkzeug.serving import run_simple
        logging.info('application (%s) will start at %s:%s' % (self._document_root, host, port))
        run_simple(host, port, self)

    def __call__(self, environ, start_response):
        """
        WSGI protocol, a callable instance
        :param environ: wsgi environ
        :param start_response: wsgi start_response
        :return:
        """
        return self._wsgi_app(environ, start_response, self._debug)

    def _dispatch_request(self):
        """
        make response of route
        :return:
        """
        request_method = ctx.request.request_method
        path_info = ctx.request.path_info
        if request_method == 'GET':
            for fn in self._get_dynamic:
                args = fn.match(path_info)
                if args is not None:
                    return fn(*args)
            raise not_found()
        if request_method == 'POST':
            for fn in self._post_dynamic:
                args = fn.match(path_info)
                if args is not None:
                    return fn(*args)
            raise not_found()
        bad_request()

    def _wsgi_app(self, environ, start_response, debug=True):
        self._running = True
        _application = Dict(document_root=self._document_root)

        ctx.application = _application
        ctx.request = Request(environ)
        response = ctx.response = Response()
        try:
            r = self._dispatch_request()
            if isinstance(r, Template):
                r = self._template_engine(r.template_name, r.model)
            if isinstance(r, unicode):
                r = r.encode('utf-8')
            if r is None:
                r = []
            start_response(response.status, response.headers)
            return r
        except RedirectError, e:
            response.set_header('location', e.location)
            start_response(e.status, response.headers)
            return []
        except HttpError, e:
            start_response(e.status, response.headers)
            return ['<html><body><h1>', e.status, '</h1></body></html>']
        except Exception, e:
            logging.exception(e)
            if not debug:
                start_response('500 Internal Server Error', [])
                return ['<html><body><h1>500 Internal Server Error</h1></body></html>']
            exc_type, exc_value, exc_traceback = sys.exc_info()
            fp = StringIO()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=fp)
            stacks = fp.getvalue()
            fp.close()
            start_response('500 Internal Server Error', [])
            return [
                r'''<html><body><h1>
                500 Internal Server Error</h1>
                <div style="font-family:Monaco, Menlo, Consolas, 'Courier New', monospace;">
                <pre>''',
                stacks.replace('<', '&lt;').replace('>', '&gt;'),
                '</pre></div></body></html>']
        finally:
            del ctx.application
            del ctx.request
            del ctx.response
