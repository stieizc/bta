from libbta.parser.babeltrace import Babeltrace

from libbta.layer.qemu_virtio_layer import QemuVirtioLayer
from libbta.layer.qemu_raw_layer import QemuRawLayer
from libbta.layer.linux_block_layer import LinuxBlockLayer

config = {
    'parsers': ['babel', Babeltrace],

    'layers': [
        ('guest_blk',
         {'class': LinuxBlockLayer,
          'domains': ['debian-fstest.kernel']}),
        ('qemu_virtio',
         {'class': QemuVirtioLayer,
          'domains': ['debc.qemu']}),
        ('qemu_raw_backend',
         {'class': QemuRawLayer,
          'domains': ['debc.qemu']})
    ]
}
