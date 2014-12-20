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

    def _add_req(self, timestamp, queue, req):
        self._handle_req(req, timestamp, queue, 'add')

    def _submit_req(self, timestamp, queue, req):
        self._handle_req(req, timestamp, queue, 'submit')

    def _finish_req(self, timestamp, queue, req):
        self._handle_req(req, timestamp, queue, 'finish')

    def _handle_req(self, req, timestamp, queue, event_type):
        req[event_type + '_time'] = timestamp
        queue.append(req)
        #print("{0}: {1}".format(event_type, str(req)))
        self.notice_all_deducer(req, event_type)

    def add_upper_deducer(self, upper):
        self.upper = upper

    def add_lower_deducer(self, lower):
        self.lower = lower

    def notice_all_deducer(self, req, event_type):
        self.notice_upper_deducer(req, event_type)
        self.notice_lower_deducer(req, event_type)

    # Notice the reverse of layer position here
    def notice_upper_deducer(self, req, event_type):
        if self.upper:
            self.notice(self.upper, req, event_type, 'lower')

    def notice_lower_deducer(self, req, event_type):
        if self.lower:
            self.notice(self.lower, req, event_type, 'upper')

    @staticmethod
    def notice(deducer, req, event_type, layer):
        deducer.deduce(req, event_type, layer)

    @staticmethod
    def fifo_req_out(src, critique, action):
        for req, idx in zip(src, range(len(src))):
            if critique(req):
                del src[idx]
                action(req)
                return True
        return False

    @staticmethod
    def fifo_req_out_warn(src, critique, action, event):
        found = Layer.fifo_req_out(src, critique, action)
        if not found:
            print("Throw event {0}".format(event))

    @staticmethod
    def critique_by_pos(offset, length, req):
        return req.offset == offset and req.length == length

    @staticmethod
    def critique_by_id(_id, req):
        return req['id'] == _id

    def __repr__(self):
        return self.name


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
        self.layers = {'upper': upper, 'lower': lower}
        self.deduce_funcs = {'upper': {}, 'lower': {}}
        upper.add_lower_deducer(self)
        lower.add_upper_deducer(self)

    def deduce(self, req, event_type, layer_to_search):
        deduce_func = self.deduce_funcs[layer_to_search].get(event_type)
        if deduce_func:
            deduce_func(self, req)

    @property
    def upper(self):
        return self.layers['upper']

    @property
    def lower(self):
        return self.layers['lower']
