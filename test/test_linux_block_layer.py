import unittest, os

from libbta.parser import parser_babeltrace as traceparser
from libbta.layer.linux_block_layer import LinuxBlockLayer

class LinuxBlockLayerTestCase(unittest.TestCase):
    def setUp(self):
        self.infile = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'traces', 'guest.babeltrace')
        self.events = traceparser.parse(self.infile)
        self.layer = LinuxBlockLayer('LinuxBlockLayer')
        for e in self.events:
            self.layer.read_event(e)

    def test_print(self):
        #self.assertEqual(str(self.req), 'req: ')
        print()
        print(self.layer)
