from fta.parser.babeltrace import Babeltrace

from fta.layer.qemu_virtio_layer import QemuVirtioLayer
from fta.layer.qemu_raw_layer import QemuRawLayer
from fta.layer.linux_block_layer import LinuxBlockLayer

config = {
    'parsers': {'babel': Babeltrace},
    'layers': [
        ('guest_blk',
         LinuxBlockLayer,
         ['debian-fstest.kernel']),
        ('qemu_virtio',
         QemuVirtioLayer,
         ['debc.qemu']),
        ('qemu_raw_backend',
         QemuRawLayer,
         ['debc.qemu'])
    ]
}
