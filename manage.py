import argparse
import sys
import unittest
from example.app import app


def _test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


def _run():
    app.run()

parser = argparse.ArgumentParser(description='tindo')
parser.add_argument('-test', action="store_true", default=False)
parser.add_argument('-app', action="store_true", default=False)
options = parser.parse_args(sys.argv[1:])
if options.test:
    _test()
if options.app:
    _run()

