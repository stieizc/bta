import unittest

from libbta.sorter import Sorter


class SorterTestCase(unittest.TestCase):
    def setUp(self):
        self.args = [('qemu_virtio_req', 'qemu_virtio', {'host': 'debc',
                      'domain': 'qemu', 'type': 'virtio'}),
                     ('qemu_raw_req', 'qemu_virtio', {'host': 'debc',
                      'domain': 'qemu', 'type': 'raw'})]
        self.sorter = Sorter(self.args)

    def test_name(self):
        for layer, arg in zip(self.sorter.layers, self.args):
            self.assertEqual(layer.name, arg[0], 'Layer Name Failed')

    def test_id(self):
        for _id, arg in zip(self.sorter.ids, self.args):
            self.assertEqual(_id, arg[2], 'Layer Identifier Failed')
