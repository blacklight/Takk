#!/usr/bin/env python

import unittest
import json
import os
import sys

from __armando__ import Armando

###
Armando.initialize()
###

sys.path = [Armando.get_base_dir() + os.sep + 'share' + os.sep + 'Takk'] + sys.path
from rules import Rules

class TestTakkRules(unittest.TestCase):
    def setUp(self):
        self.rules = Rules('conf/app.test.xml')

    def test_pattern_matched(self):
        pattern_id, attributes = self.rules.pattern_match('play some music artist Led Zeppelin')
        self.assertEqual(pattern_id, 'play-music')
        self.assertEqual(attributes['artist'], 'Led Zeppelin')

    def test_pattern_not_matched(self):
        pattern_id, attributes = self.rules.pattern_match('this will never be matched by any of my rules')
        self.assertEqual(pattern_id, None)
        self.assertEqual(len(attributes.keys()), 0)

if __name__ == "__main__":
    unittest.main()

