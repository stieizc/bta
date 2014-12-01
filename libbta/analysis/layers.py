from collections import deque


class Layer:
    """
    Layers contain requests. There is a hierarchy of layers:

    Layer 0     domain0, domain1
              --------------------
                       |
              --------------------
                       |
    Layer 2         domain0
              --------------------

    Events' host and domain are used for identifying their layers, these
    identifiers must be unique between layers.
    """

    def __init__(self, name, upper):
        self.name = name
        self.upper = upper


class QemuVirtioLayer(Layer):
    """Layer for Qemu's Virtio"""
    def __init__(self, name, upper):
        super().__init__(name, upper)
        self.added_reqs = deque()
        self.submitted_reqs = deque()
        self.issued_reqs = self.submitted_reqs


LayerTypes = {
    'qemu_virtio': QemuVirtioLayer
}
