from fta import Event
from fta import BlkRequest
from fta.request_queue import ReqQueue
from fta.exceptions import EventDiscarded
from fta.utils.trigger import Trigger


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
        super().__init__()
        self.name = name
        self.queues = {}
        self._related = {}

    def accept_req(self, req, event, action, dest):
        """
        Set the timestamp according to action, add it to a queue
        """
        req.add_event(action, event)
        dest.append(req)
        self.trigger(action, req)
        return req

    def relate(self, name, layer):
        self._related[name] = layer

    # To prevent conflict with 'on'. I'm so smart
    def when(self, layer_name, action, f=None):
        layer = self._related.get(layer_name)
        if layer:
            return layer.on(action, f)
        elif f:
            return f
        else:
            return lambda ff: ff

    def link_reqs_in_queue(self, queue, rule, self_type, other_type):
        def find_and_link_with(r):
            _queue = queue(r) if callable(queue) else queue
            for req in _queue:
                _rule = getattr(req, rule)
                if _rule(r):
                    req.link(self_type, r)
                    r.link(other_type, req)
        return find_and_link_with

    def link_with_lower_from(self, queue, rule):
        return self.link_reqs_in_queue(
            queue, rule, self_type='lower', other_type='upper')

    def link_with_upper_from(self, queue, rule):
        return self.link_reqs_in_queue(
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

    def handler_gen_req(self, action, name, dest, attrs=None,
                        discard=None):
        def handler(trace):
            event = Event(trace, attrs)
            if discard and discard(event):
                raise EventDiscarded(event)
            req = BlkRequest(name, event)
            _dest = dest(req) if callable(dest) else dest
            return self.accept_req(req, event, action, _dest)
        return handler

    def handler_mv_req(self, action, dest, src, rule, attrs=None,
                       discard=None):
        def handler(trace):
            event = Event(trace, attrs)
            if discard and discard(event):
                raise EventDiscarded(event)
            _src = src(event) if callable(src) else src
            req = _src.req_out(rule, event)
            _dest = dest(req) if callable(dest) else dest
            return self.accept_req(req, event, action, _dest)
        return handler

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
        if handler:
            return handler(trace)

    def get_queue_req_op(self, name):
        queue = self.queues[name]
        return lambda req: queue[req['ops'][0]]

    @classmethod
    def sec2byte(cls, n):
        return int(n) * cls.SECTOR_SIZE

    def init_queues(self):
        for t in self.EVENT_TYPES:
            self.queues[t] = {'read': ReqQueue(), 'write': ReqQueue()}
