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

    def __init__(self, name):
        self.name = name
        self.upper = None
        self.lower = None

    def _add_req(self, req, event, queue):
        req.add_time = event.timestamp
        queue.append(req)
        self.notice_all_deducer(req, 'add')

    def _submit_req(self, req, event, queue):
        req.submit_time = event.timestamp
        queue.append(req)
        self.notice_all_deducer(req, 'submit')

    def _finish_req(self, req, event, queue):
        req.finish_time = event.timestamp
        queue.append(req)
        self.notice_all_deducer(req, 'finish')

    def add_upper_deducer(self, upper):
        self.upper = upper

    def add_lower_deducer(self, lower):
        self.lower = lower

    def notice_all_deducer(self, req, event_type):
        self.notice_upper_deducer(req, event_type)
        self.notice_lower_deducer(req, event_type)

    def notice_upper_deducer(self, req, event_type):
        if self.upper:
            self.notice_layer(self.upper, req, event_type, 'upper')

    def notice_lower_deducer(self, req, event_type):
        if self.lower:
            self.notice_layer(self.lower, req, event_type, 'lower')

    @staticmethod
    def notice_deducer(deducer, req, event_type, layer):
        deducer.deduce(req, event_type, layer)

    def __repr__(self):
        string = self.name
        if self.upper:
            string += ": Upper {1}".format(self.upper.name)
        return string


class BlkLayer(Layer):
    """
    Block Layer
    """
    def __init__(self, name, req_attrs_map):
        super().__init__(name)
        self.req_attrs_map = req_attrs_map

    def gen_req(self, name, event):
        req = BlkRequest(name)
        req.get_event_attrs(event, self.req_attrs_map)
        req.offset = int(req.offset)
        req.length = int(req.length)
        return req


class Deducer:
    """
    Deduce the relationship between requests from lower and upper layers.
    """
    def __init__(self, upper, lower):
        self.upper = upper
        self.lower = lower
        upper.add_lower_deducer(self)
        lower.add_upper_deducer(self)
