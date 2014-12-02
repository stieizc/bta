import unittest
import os

from libbta.parser import parser_babeltrace as traceparser

class QemuVirtioLayerTestCase(unittest.TestCase):
    def setUp(self):
        self.infile = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'babeltrace_example.txt')
        with open(self.infile) as infile:
            self.linenum = sum(1 for line in infile)
        self.events = traceparser.parse(self.infile)

    def test_events_num(self):
        self.assertEqual(len(self.events), self.linenum,
                         'Event num {0} not equal {1}'.format(len(self.events),
                                                              self.linenum))
