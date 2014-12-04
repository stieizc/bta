from libbta import BlkRequest


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

    def __init__(self, name, upper=None):
        self.name = name
        self.upper = upper

    def __repr__(self):
        string = self.name
        if self.upper:
            string += ": Upper {1}".format(self.upper.name)
        return string


class BlkLayer(Layer):
    """
    Block Layer
    """
    def __init__(self, name, req_attrs_map, upper=None):
        super().__init__(name, upper)
        self.req_attrs_map = req_attrs_map

    def gen_req(self, name, event):
        req = BlkRequest(name)
        req.get_event_attrs(event, self.req_attrs_map)
        req.offset = int(req.offset)
        req.length = int(req.length)
        req.add_time = event.timestamp
        return req
