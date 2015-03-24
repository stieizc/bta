import sys

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
        self._handle_req(timestamp, queue, 'add', req)

    def _submit_req(self, timestamp, queue, req):
        self._handle_req(timestamp, queue, 'submit', req)

    def _finish_req(self, timestamp, queue, req):
        self._handle_req(timestamp, queue, 'finish', req)

    def _handle_req(self, timestamp, queue, event_type, req):
        """
        Set the timestamp according to event_type, add it to a queue, and
        notice upper and lower deducer with request and event_type
        """
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

    def __repr__(self):
        return self.name


class BlkLayer(Layer):
    """
    Block Layer
    """
    SECTOR_SIZE = 512

    def __init__(self, name):
        super().__init__(name)
        self.event_handlers = {
                'add': self.add_request,
                'submit': self.fifo_mv_request,
                'finish': self.fifo_mv_request}

    def read_event(self, event):
        """
        Read a event, pass it to *a* proper handler, if any. So a event only
        gets handled once.

        info is a object passed as argument to standard handlers. If it has a
        handler field, then that handler is called instead.

        Directly needed entries of info are:
        'type': see 'handler'

        Optional entries:
        'handler': if has one, use it as the handler name; otherwise use
                   info['type'] as handler name
        """
        info = self.event_info_map.get(event.name, None)
        if info:
            handler_name = info.get('handler', None)
            if not handler_name:
                handler_name = info['type']
            handler = self.event_handlers[handler_name]
            handler(event, info)

    def add_request(self, event, info):
        """
        Generate a request from event, add it to queue.

        Needed entries of info are:
        'name': name of the request
        'type': type of the event. Standard types are 'add', 'submit' and
                'finish'

        Optional entries:
        'queue': name of the queue in req_queue. Default: 'type'

        Return the request in the end.
        """
        req = self.gen_req(event, info)
        queue = self.req_queue[info.get('queue', info['type'])]
        self._handle_req(event.timestamp, queue, info['type'], req)
        return req

    def fifo_mv_request(self, event, info, warn=True):
        """
        Move one request from one queue to another, and set timestamp according
        to type. See Layer._handle_req.

        Needed entries of info are:
        'type': type of the event. Standard types are 'add', 'submit' and
                'finish'
        'src': name of the source request queue
        'rule': rule to find the request, a function that takes (req, event) as
                it's arguments, and return True if the req is needed

        If found a request, return the request in the end; else return None.
        """
        src = self.req_queue[info['src']]
        req = src.req_out(info['rule'], event)
        if req:
            queue = self.req_queue[info.get('queue', info['type'])]
            self._handle_req(event.timestamp, queue, info['type'], req)
        elif warn:
            print('Throw: ' + str(event), file=sys.stderr)
        return req

    @classmethod
    def gen_req(cls, event, info):
        req = BlkRequest(info['name'])
        req.read_event(event, cls.req_attrs_map)
        cls.offset_length_to_byte(req)
        return req

    @staticmethod
    def rule_by_pos(offset, length, req):
        return req.offset == offset and req.length == length

    @classmethod
    def offset_length_to_byte(cls, req):
        req['offset'] *= cls.SECTOR_SIZE
        req['length'] *= cls.SECTOR_SIZE

    def add_rwbs_flag(rwbs, action):
        return rwbs | BlkRequest.RWBS_FLAG[action]
