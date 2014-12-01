import unittest

from libbta.analysis import Request

class RequestTestCase(unittest.TestCase):
    def setUp(self):
        self.req = Request('req')

    def test_name(self):
        self.assertEqual(self.req.name, 'req', 'Request Name Failed')

    def test_add_time(self):
        self.req.add_time = 0
        self.assertEqual(self.req.add_time, 0, 'Request add_time failed')

    def test_submit_time(self):
        self.req.submit_time = 0
        self.assertEqual(self.req.submit_time, 0, 'Request submit_time failed')

    def test_finish_time(self):
        self.req.finish_time = 0
        self.assertEqual(self.req.finish_time, 0, 'Request finish_time failed')
