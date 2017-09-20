import unittest
import datetime
import sys
from tindo import Dict, UTC
from tindo import HttpError, RedirectError, bad_request, unauthorized, forbidden, RE_RESPONSE_STATUS
from tindo import internal_error, redirect, found, see_other
from tindo import to_str, to_unicode, quote, unquote, RESPONSE_STATUSES
from tindo import get, post, Request, Response, route
from tindo.tindo import _build_regex, _load_module
from StringIO import StringIO


class TestDict(unittest.TestCase):

    def testDict(self):
        d1 = Dict()
        d1.x = 100
        self.assertTrue(d1['x'], 100)
        d1['y'] = 200
        self.assertTrue(d1.y, 200)
        with self.assertRaises(AttributeError):
            print(d1.empty)


class TestUTC(unittest.TestCase):
    def testUtc(self):
        tz0 = UTC('+00:00')
        self.assertTrue(tz0.tzname(None), 'UTC+00:00')
        tz8 = UTC('+08:00')
        self.assertTrue(tz8.tzname(None), 'UTC+08:00')
        tz5 = UTC('-05:30')
        self.assertTrue(tz5.tzname(None), 'UTC-05:30')
        with self.assertRaises(ValueError):
            tzNone = UTC('az:08')


class TestReponseStatus(unittest.TestCase):
    def testMath(self):
        for k, _ in RESPONSE_STATUSES.items():
            self.assertTrue(RE_RESPONSE_STATUS.match(str(k)+' '+_))


class TestHttpError(unittest.TestCase):
    def test404Error(self):
        e = HttpError(404)
        self.assertEqual(e.status, '404 Not Found')

    def testRedirectError(self):
        e = RedirectError(302, 'http://www.apple.com/')
        self.assertEqual(e.status, '302 Found')
        self.assertEqual(e.location, 'http://www.apple.com/')

    def testRaiseError(self):
        with self.assertRaises(HttpError):
            bad_request()
        self.assertEqual(str(sys.exc_value), '400 Bad Request')
        with self.assertRaises(HttpError):
            unauthorized()
        self.assertEqual(str(sys.exc_value), '401 Unauthorized')
        with self.assertRaises(HttpError):
            forbidden()
        self.assertEqual(str(sys.exc_value), '403 Forbidden')
        with self.assertRaises(HttpError):
            internal_error()
        self.assertEqual(str(sys.exc_value), '500 Internal Server Error')
        with self.assertRaises(HttpError):
            redirect('http://www.itranswarp.com/')
        self.assertEqual(str(sys.exc_value), '301 Moved Permanently, http://www.itranswarp.com/')
        with self.assertRaises(HttpError):
            found('http://www.itranswarp.com/')
        self.assertEqual(str(sys.exc_value), '302 Found, http://www.itranswarp.com/')
        with self.assertRaises(HttpError):
            see_other('http://www.itranswarp.com/')
        self.assertEqual(str(sys.exc_value), '303 See Other, http://www.itranswarp.com/')


class TestEncode(unittest.TestCase):
    def testStrUnicode(self):
        self.assertEqual(to_str('s123'), 's123')
        self.assertEqual(to_str(u'\u4e2d\u6587'), '\xe4\xb8\xad\xe6\x96\x87')
        self.assertEqual(to_str(-123), '-123')
        self.assertEqual(to_unicode('\xe4\xb8\xad\xe6\x96\x87'), u'\u4e2d\u6587')

    def testQuote(self):
        self.assertEqual(quote('http://example/test?a=1+'), 'http%3A//example/test%3Fa%3D1%2B')
        self.assertEqual(quote(u'hello world!'), 'hello%20world%21')
        self.assertEqual(unquote('http%3A//example/test%3Fa%3D1+'), u'http://example/test?a=1+')


@get('/test/:id')
def testget():
    return 'ok'


@post('/post/:id')
def testpost():
    return '200'


class TestMethods(unittest.TestCase):
    def testMethod(self):
        self.assertEqual(testget.__web_route__, '/test/:id')
        self.assertEqual(testget.__web_method__, ['GET'])
        self.assertEqual(testpost.__web_route__, '/post/:id')
        self.assertEqual(testpost.__web_method__, ['POST'])


class TestBuildRegex(unittest.TestCase):
    def testBuild(self):
        self.assertEqual(_build_regex('/path/to/<file>'), '^\\/path\\/to\\/(?P<file>[^\\/]+)$')
        self.assertEqual(_build_regex('/path/to/<name>/<comment>'),
                                      '^\\/path\\/to\\/(?P<name>[^\\/]+)\\/(?P<comment>[^\\/]+)$')


class TestRequest(unittest.TestCase):
    def testGetItem(self):
        r = Request({'REQUEST_METHOD':'POST', 'wsgi.input': StringIO('a=1&b=M%20M&c=ABC&c=XYZ&e=')})
        self.assertEqual(r['a'], u'1')
        self.assertEqual(r['c'], u'ABC')
        with self.assertRaises(KeyError):
            r['empty']

        r = Request({'REQUEST_METHOD': 'POST', 'wsgi.input': StringIO('a=1&b=M%20M&c=ABC&c=XYZ&e=')})
        self.assertEqual(r.get('a'), u'1')
        self.assertEqual(r.gets('c'), [u'ABC', u'XYZ'])
        with self.assertRaises(KeyError):
            r.gets('empty')

    def testInputItem(self):
        r = Request({'REQUEST_METHOD': 'POST', 'wsgi.input': StringIO('a=1&b=M%20M&c=ABC&c=XYZ&e=')})
        i = r.input(x=2017)
        self.assertEqual(i.x, 2017)
        self.assertEqual(i.a, u'1')
        self.assertEqual(i.b, u'M M')
        self.assertEqual(i.c, u'ABC')
        self.assertEqual(i.get('d', u'2008'), '2008')

    def testBody(self):
        r = Request({'REQUEST_METHOD': 'POST', 'wsgi.input': StringIO('<xml><raw/>')})
        self.assertEqual(r.get_body(), '<xml><raw/>')

    def testRemote_Addr(self):
        r = Request({'REMOTE_ADDR': '192.168.0.100'})
        self.assertEqual(r.remote_addr, '192.168.0.100')

    def testDocumentRoot(self):
        r = Request({'DOCUMENT_ROOT': '/srv/path/to/doc'})
        self.assertEqual(r.document_root, '/srv/path/to/doc')

    def testQueryString(self):
        r = Request({'QUERY_STRING': 'a=1&c=2'})
        self.assertEqual(r.query_string, 'a=1&c=2')
        r = Request({})
        self.assertEqual(r.query_string, '')

    def testRequestMethod(self):
        r = Request({'REQUEST_METHOD': 'GET'})
        self.assertEqual(r.request_method, 'GET')
        r = Request({'REQUEST_METHOD': 'POST'})
        self.assertEqual(r.request_method, 'POST')

    def testPathInfo(self):
        r = Request({'PATH_INFO': '/test/a%20b.html'})
        self.assertEqual(r.path_info, '/test/a b.html')

    def testHost(self):
        r = Request({'HTTP_HOST': 'localhost:8080'})
        self.assertEqual(r.host, 'localhost:8080')

    def testHeader(self):
        r = Request({'HTTP_USER_AGENT': 'Mozilla/5.0', 'HTTP_ACCEPT': 'text/html'})
        H = r.headers
        self.assertEqual(H['ACCEPT'], 'text/html')
        self.assertEqual(H['USER-AGENT'], 'Mozilla/5.0')

    def testCookies(self):
        r = Request({'HTTP_COOKIE': 'A=123; url=http%3A%2F%2Fwww.example.com%2F'})
        self.assertEqual(r.cookies['A'], '123')
        self.assertEqual(r.cookies['url'], u'http://www.example.com/')


class TestResponse(unittest.TestCase):
    def testHeaders(self):
        r = Response()
        self.assertEqual(r.headers, [('Content-Type', 'text/html; charset=utf-8'), ('X-Powered-By', 'tindo/1.0')])
        r.set_cookie('s1', 'ok', 3600)
        self.assertEqual(r.headers,
                         [('Content-Type', 'text/html; charset=utf-8'),
                          ('Set-Cookie', 's1=ok; Max-Age=3600; Path=/; HttpOnly'),
                          ('X-Powered-By', 'tindo/1.0')])
        self.assertEqual(r.header('content-type'), 'text/html; charset=utf-8')
        self.assertEqual(r.header('CONTENT-type'), 'text/html; charset=utf-8')
        r.unset_header('content-type')
        self.assertEqual(r.header('content-type'), None)
        r.set_header('content-type', 'image/png')
        self.assertEqual(r.header('content-type'), 'image/png')

    def testContent(self):
        r = Response()
        self.assertEqual(r.content_type, 'text/html; charset=utf-8')
        r.content_type = 'text/json'
        self.assertEqual(r.content_type, 'text/json')

        r.content_length = 100
        self.assertEqual(r.content_length, '100')
        r.content_length = '1024'
        self.assertEqual(r.content_length, '1024')

    def testCookies(self):
        r = Response()
        r.set_cookie('company', 'Abc, Inc.', max_age=3600)
        self.assertEqual(r._cookies, {'company': 'company=Abc%2C%20Inc.; Max-Age=3600; Path=/; HttpOnly'})
        r.set_cookie('company', r'Example="Limited"', expires=1342274794.123, path='/sub/')
        self.assertEqual(r._cookies,
                         {'company': 'company=Example%3D%22Limited%22; Expires=Sat, 14-Jul-2012 14:06:34 GMT; Path=/sub/; HttpOnly'})
        dt = datetime.datetime(2012, 7, 14, 22, 6, 34, tzinfo=UTC('+8:00'))
        r.set_cookie('company', 'Expires', expires=dt)
        self.assertEqual(r._cookies, {'company': 'company=Expires; Expires=Sat, 14-Jul-2012 14:06:34 GMT; Path=/; HttpOnly'})
        r.unset_cookie('company')
        self.assertEqual(r._cookies, {})

    def testStatus(self):
        r = Response()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.status, '200 OK')
        r.status = 404
        self.assertEqual(r.status, '404 Not Found')
        with self.assertRaises(ValueError):
            r.status = 1000
        r.status = '500 ERROR'
        self.assertEqual(r.status, '500 ERROR')


class TestLoadModule(unittest.TestCase):
    def testModule(self):
        m = _load_module('xml')
        self.assertEqual(m.__name__, 'xml')
        m = _load_module('xml.sax')
        self.assertEqual(m.__name__, 'xml.sax')
        m = _load_module('xml.sax.handler')
        self.assertEqual(m.__name__, 'xml.sax.handler')


@route('/')
def index():
    pass


@route('/home', methods=['GET', 'POST'])
def home():
    pass


class TestRoute(unittest.TestCase):
    def testRouteDecorator(self):
        self.assertEqual(index.__web_route__, '/')
        self.assertEqual(index.__web_method__, ['GET'])
        self.assertEqual(home.__web_route__, '/home')
        self.assertEqual(home.__web_method__, ['GET', 'POST'])


if __name__ == '__main__':
    unittest.main()
