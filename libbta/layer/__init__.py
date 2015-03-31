import sys
from collections import deque

from libbta import BlkRequest
from libbta import ReqQueue
from libbta.utils.trigger import Trigger


class Layer(Trigger):
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
        self.queues = {}
        self._related = {}

    def accept_req(self, req, action, timestamp):
        """
        Set the timestamp according to action, add it to a queue
        """
        req.timestamps[action] = timestamp
        self.get_queue(req, action).append(req)
        self.trigger(action, req)

    def relate(self, name, layer):
        self._related[name] = layer

    # To prevent conflict with 'on'. I'm so smart
    def when(self, layer_name, action):
        layer = self._related.get(layer_name)
        if layer:
            return layer.on(action)
        else:
            return lambda f: f

    @staticmethod
    def link_reqs_in_queue(queue, rule, self_type, other_type):
        def find_and_link_with(r):
            for req in queue:
                if rule(req, r):
                    req.link(self_type, r)
                    r.link(other_type, req)
        return find_and_link_with

    @classmethod
    def link_reqs_with_lower(cls, queue, rule):
        return cls.link_reqs_in_queue(
            queue, rule, self_type='lower', other_type='upper')

    @classmethod
    def link_reqs_with_upper(cls, queue, rule):
        return cls.link_reqs_in_queue(
            queue, rule, self_type='upper', other_type='lower')

    def __repr__(self):
        return self.name


class BlkLayer(Layer):
    """
    Block Layer
    """
    SECTOR_SIZE = 512
    EVENT_TYPES = ['queue', 'submit', 'finish']

    def __init__(self, name):
        super().__init__(name)
        self.init_queues()

    def read_trace(self, trace):
        """
        Read a trace, pass it to *a* proper handler, if any. So a trace only
        gets handled once.

        info is a object passed as argument to standard handlers. If it has a
        handler field, then that handler is called instead.

        Directly needed entries of info are:
        'type': see 'handler'

        Optional entries:
        'handler': if has one, use it as the handler name; otherwise use
                   info['type'] as handler name
        """
        handler = self.trace_handlers.get(trace.name)
        if callable(handler):
            handler(trace)
        elif type(handler) == tuple:
            self.handle_trace(trace, handler)

    def handle_trace(trace, info):
        action, detail = info
        if action == 'queue':
            self.queue_request(trace, *info)
        else:
            self.handle_request_fifo(trace, action, info)

    def queue_request(self, trace, name, attrs_map):
        req = trace.map2dict(BlkRequest(name), attrs_map)
        self.accept_req(req, 'queue', trace.timestamp)
        return req

    def handle_request_fifo(self, trace, action, info):
        """
        Move one request from one queue to another, and set timestamp according
        to type.
        """
        req = self.fifo_req_out(trace, *info)
        if req:
            self.accept_req(req, action, trace.timestamp)
        else:
            print('Throw: ' + str(event), file=sys.stderr)
        return req

    def fifo_req_out(self, trace, src, rule, attrs_map):
        if attrs_map:
            event = trace.map2dict({}, attrs_map)
        else:
            event = trace
        src = self.get_queue(event, src)
        return src.req_out(rule, event)

    @classmethod
    def sec2byte(cls, n):
        return int(n) * cls.SECTOR_SIZE

    def init_queues(self):
        for t in self.EVENT_TYPES:
            self.queues[t] = {'read': ReqQueue(), 'write': ReqQueue()}

    def get_queue(self, req, action):
        return self.queues[action][req.op_type]
