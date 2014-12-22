from libbta.config.types import *

Layers = [('guest_blk',
           {'class': LinuxBlockLayer,
            'domains': ['debian-fstest.kernel']}),
          ('qemu_virtio',
           {'class': QemuVirtioLayer,
            'domains': ['debc.qemu']}),
          ('qemu_raw_backend',
           {'class': QemuRawLayer,
            'domains': ['debc.qemu']})]

Deducers = [(VirtioRawDeducer,
            {'upper': 'qemu_virtio',
             'lower': 'qemu_raw_backend'}),
            (FifoDeducer,
            {'upper': 'guest_blk',
             'lower': 'qemu_virtio'})]
