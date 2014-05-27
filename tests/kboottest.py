#!/usr/bin/env python

#
# kboottest.py
#
# Automatically run "does-it-boot" tests on a range of platforms
#

#
# Usage:
#   <change into a kernel source directory>
#   nice ionice <path_to>/kboottest.py
#   make mrproper    ;-)
#
# Note that this test suite is VERY talkative
#

import importlib
import unittest

class TestKbootSuite(unittest.TestCase):
    def setUp(self):
	pass

    def tearDown(self):
	pass

    def verdict(self):
        testname = str(self).split()[0]
        board = testname[5:] + "_verdict"
        print('')
        verdict = importlib.import_module(board)
        verdict.run()

    def test_versatile(self):
	self.verdict()

    def test_versatile_dt(self):
	self.verdict()

#    def test_versatile_fiq(self):
#	self.verdict()

if __name__ == '__main__':
    unittest.main()
