import unittest, os

from fta.config.configparser import ConfigParser


class ConfigReaderTestCase(unittest.TestCase):
    def setUp(self):
        self.conffile = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'bta.yaml')
        self.parser = ConfigParser(self.conffile)

    def test_print(self):
        print()
        print(self.parser)
