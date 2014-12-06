from ..layer.qemu_virtio_layer import QemuVirtioLayer
from ..layer.qemu_raw_layer import QemuRawLayer

LayerTypes = {
    'qemu_virtio': QemuVirtioLayer,
    'qemu_raw': QemuRawLayer
}

from ..layer.deducers import VirtioRawDeducer

DeducerTypes = {
    'virtio_raw': VirtioRawDeducer
}

from ..parser.parser_babeltrace import parse as ParseBabeltrace

Parsers = {
    'babeltrace': ParseBabeltrace
}
