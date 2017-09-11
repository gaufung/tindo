import sys
sys.path.insert(0, '../')
reload(sys)
import unittest
import sys
from tindo.tindo import Dict, UTC, _RE_RESPONSE_STATUS, _RESPONSE_STATUSES
from tindo.tindo import HttpError, RedirectError, badrequest,unauthorized, forbidden
from tindo.tindo import notfound, conflict, internalerror, redirect, found, seeother
from tindo.tindo import _to_str, _to_unicode, _quote, _unquote
from tindo.tindo import get, post
from tindo.tindo import _build_regex, Request
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
        for k, _ in _RESPONSE_STATUSES.items():
            self.assertTrue(_RE_RESPONSE_STATUS.match(str(k)))


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
            raise badrequest()
        self.assertEqual(str(sys.exc_value), '400 Bad Request')
        with self.assertRaises(HttpError):
            raise unauthorized()
        self.assertEqual(str(sys.exc_value), '401 Unauthorized')
        with self.assertRaises(HttpError):
            raise forbidden()
        self.assertEqual(str(sys.exc_value), '403 Forbidden')
        with self.assertRaises(HttpError):
            raise internalerror()
        self.assertEqual(str(sys.exc_value), '500 Internal Server Error')
        with self.assertRaises(HttpError):
            raise redirect('http://www.itranswarp.com/')
        self.assertEqual(str(sys.exc_value), '301 Moved Permanently, http://www.itranswarp.com/')
        with self.assertRaises(HttpError):
            raise found('http://www.itranswarp.com/')
        self.assertEqual(str(sys.exc_value), '302 Found, http://www.itranswarp.com/')
        with self.assertRaises(HttpError):
            raise seeother('http://www.itranswarp.com/')
        self.assertEqual(str(sys.exc_value), '303 See Other, http://www.itranswarp.com/')


class TestEncode(unittest.TestCase):
    def testStrUnicode(self):
        self.assertEqual(_to_str('s123'), 's123')
        self.assertEqual(_to_str(u'\u4e2d\u6587'), '\xe4\xb8\xad\xe6\x96\x87')
        self.assertEqual(_to_str(-123), '-123')
        self.assertEqual(_to_unicode('\xe4\xb8\xad\xe6\x96\x87'), u'\u4e2d\u6587')

    def testQuote(self):
        self.assertEqual(_quote('http://example/test?a=1+'), 'http%3A//example/test%3Fa%3D1%2B')
        self.assertEqual(_quote(u'hello world!'), 'hello%20world%21')
        self.assertEqual(_unquote('http%3A//example/test%3Fa%3D1+'), u'http://example/test?a=1+')


@get('/test/:id')
def testget():
    return 'ok'


@post('/post/:id')
def testpost():
    return '200'


class TestMethods(unittest.TestCase):
    def testMethod(self):
        self.assertEqual(testget.__web_route__, '/test/:id')
        self.assertEqual(testget.__web_method__, 'GET')
        self.assertEqual(testpost.__web_route__, '/post/:id')
        self.assertEqual(testpost.__web_method__, 'POST')


class TestBuildRegex(unittest.TestCase):
    def testBuild(self):
        self.assertEqual(_build_regex('/path/to/:file'), '^\\/path\\/to\\/(?P<file>[^\\/]+)$')
        self.assertEqual(_build_regex('/:user/:comments/list'),
                         '^\\/(?P<user>[^\\/]+)\\/(?P<comments>[^\\/]+)\\/list$')
        self.assertEqual(_build_regex(':id-:pid/:w'),
                         '^(?P<id>[^\\/]+)\\-(?P<pid>[^\\/]+)\\/(?P<w>[^\\/]+)$')


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

if __name__ == '__main__':
    unittest.main()
