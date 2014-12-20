import unittest
import os

from libbta.parser import parser_lttng as traceparser

class QemuVirtioLayerTestCase(unittest.TestCase):
    def setUp(self):
        self.tracedir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'traces', 'lttng_example.lttng')
        self.events = traceparser.parse(self.tracedir)

    def test_print(self):
        for e in self.events:
            print(e.name)
