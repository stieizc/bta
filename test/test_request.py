import unittest

from fta import Request

class RequestTestCase(unittest.TestCase):
    def setUp(self):
        self.req = Request('req')
        self.req.add_time = 0
        self.req.submit_time = 1
        self.req.finish_time = 2

    def test_name(self):
        self.assertEqual(self.req.name, 'req', 'Request Name Failed')

    def test_add_time(self):
        self.assertEqual(self.req.add_time, 0, 'Request add_time failed')

    def test_submit_time(self):
        self.assertEqual(self.req.submit_time, 1, 'Request submit_time failed')

    def test_finish_time(self):
        self.assertEqual(self.req.finish_time, 2, 'Request finish_time failed')

    def test_print(self):
        #self.assertEqual(str(self.req), 'req: ')
        print()
        print(self.req)
