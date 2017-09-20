# -*- coding:utf-8 -*-
import unittest
import time
from threading import Thread
from tindo import Local


class TestLocal(unittest.TestCase):
    def testSingle(self):
        local = Local()
        local.name = 'gaofeng'
        local.age = 12
        self.assertEqual(local.name, 'gaofeng')
        self.assertEqual(local.age, 12)
        del local.name
        with self.assertRaises(AttributeError):
            local.name

    def modify(self, ctx):
        time.sleep(1)
        ctx.name = 'subThread'

    def testMultiThread(self):
        ctx = Local()
        ctx.name = 'main'
        t = Thread(target=self.modify, args=(ctx,))
        t.start()
        t.join()
        self.assertEqual(ctx.name, 'main')


if __name__ == '__main__':
    unittest.main()