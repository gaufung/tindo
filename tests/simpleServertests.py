import sys
sys.path.insert(0, '../')
reload(sys)
import unittest
from simpleserver.simpleserver import Dict, UTC, _RE_RESPONSE_STATUS, _RESPONSE_STATUSES


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

if __name__ == '__main__':
    unittest.main()
