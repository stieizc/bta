import unittest, os

from fta.parser import parser_babeltrace as traceparser
from fta.layer.qemu_raw_layer import QemuRawLayer

class QemuRawLayerTestCase(unittest.TestCase):
    def setUp(self):
        self.infile = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'babeltrace_example.txt')
        self.events = traceparser.parse(self.infile)
        self.layer = QemuRawLayer('QemuRawLayer')
        for e in self.events:
            self.layer.read_event(e)

    def test_print(self):
        #self.assertEqual(str(self.req), 'req: ')
        print()
        print(self.layer)
