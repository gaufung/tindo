import sys
sys.path.insert(0, '../')
reload(sys)
import unittest
import sys
from simpleserver.simpleserver import Dict, UTC, _RE_RESPONSE_STATUS, _RESPONSE_STATUSES
from simpleserver.simpleserver import HttpError, RedirectError, badrequest,unauthorized, forbidden
from simpleserver.simpleserver import  notfound, conflict, internalerror, redirect, found, seeother


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

if __name__ == '__main__':
    unittest.main()
