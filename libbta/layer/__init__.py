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
        if type(action) == tuple:
            action, queue = action
            if callable(queue):
                queue = queue(req)
        else:
            queue = self.get_queue(action, req)
        queue.append(req)
        self.trigger(action, req)

    def relate(self, name, layer):
        self._related[name] = layer

    # To prevent conflict with 'on'. I'm so smart
    def when(self, layer_name, action, f=None):
        layer = self._related.get(layer_name)
        if layer:
            return layer.on(action, f)
        else if f:
            return f
        else:
            return lambda ff: ff

    def link_reqs_in_queue(self, action, rule, self_type, other_type):
        def find_and_link_with(r):
            queue = self.get_queue(action, r)
            for req in queue:
                rule = getattr(req, rule)
                if rule(r):
                    req.link(self_type, r)
                    r.link(other_type, req)
        return find_and_link_with

    def link_reqs_with_lower(self, action, rule):
        return self.link_reqs_in_queue(
            action, rule, self_type='lower', other_type='upper')

    def link_reqs_with_upper(self, action, rule):
        return self.link_reqs_in_queue(
            action, rule, self_type='upper', other_type='lower')

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
        try:
            if action == 'queue':
                self.queue_request(trace, *info)
            else:
                self.queue_req_mv(trace, action, info)
        except 

    def queue_request(self, trace, name, attrs_map):
        req = trace.map2dict(BlkRequest(name), attrs_map)
        self.accept_req(req, 'queue', trace.timestamp)
        return req

    def queue_req_mv(self, trace, action, info):
        """
        Move one request from one queue to another, and set timestamp according
        to type.
        """
        req = self.queue_req_out(trace, *info)
        self.accept_req(req, action, trace.timestamp)
        return req

    def queue_req_out(self, trace, src, rule, attrs_map=None):
        if attrs_map:
            event = trace.gen_set_event(attrs_map)
        else:
            event = trace
        if callable(src):
            src = src(event)
        elif type(src) == str:
            src = self.get_queue(src, event)
        return src.req_out(rule, event)

    @classmethod
    def sec2byte(cls, n):
        return int(n) * cls.SECTOR_SIZE

    def init_queues(self):
        for t in self.EVENT_TYPES:
            self.queues[t] = {'read': ReqQueue(), 'write': ReqQueue()}

    def get_queue(self, action, event):
        return self.get_queue_by_event_op(action, event)

    def get_queue_by_event_op(self, action, event):
        # Note event could be generate from trace or just a request
        return self.get_queue_by_op(action, event['ops'][0])

    def get_queue_by_op(self, action, op_type):
        return self.queues[action][op_type]

    def use_default_lower_linker(self):
        self.when('lower', 'queue',
                  self.link_reqs_with_lower('submit', 'overlaps'))
