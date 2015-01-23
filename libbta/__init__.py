from collections import deque


class Event(dict):
    """
    Basic unit of a trace file and an analysis
    """
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp

    def __repr__(self):
        """
        Internal Printing
        """
        return "{0} {1} {2}".format(self.name, self.timestamp,
                                    super().__repr__())


class Request(dict):
    """
    Basic unit of analysis

    Each Request is associated with one or more event, and requests from
    different layers may be connected.
    """

    def __init__(self, name):
        self.name = name
        self.upper_reqs = []
        self.lower_reqs = []
        self.merged_reqs = []

    def __repr__(self):
        return "{0}: {1} {2}".format(self.name, self.timestamps,
                                     super().__repr__())

    def read_event(self, event, attrs_map):
        for new_attr, attr_map in attrs_map.items():
            attr, _type = attr_map
            if _type and _type != str:
                self[new_attr] = _type(event[attr])
            else:
                self[new_attr] = event[attr]

    def add_upper_req(self, req):
        #print("Link {0}\nupper {1}".format(str(self), str(req)))
        self.upper_reqs.append(req)

    def add_lower_req(self, req):
        #print("Link {0}\nlower {1}".format(str(self), str(req)))
        self.lower_reqs.append(req)

    @property
    def timestamps(self):
        """Get timestamps"""
        return {k: self.get(k) for k in ['add_time', 'submit_time',
                                         'finish_time']}

    @property
    def add_time(self):
        """Request add_time or none"""
        return self['add_time']

    @add_time.setter
    def add_time(self, timestamp):
        self['add_time'] = timestamp

    @property
    def submit_time(self):
        """Request is submitted for handling"""
        return self['submit_time']

    @submit_time.setter
    def submit_time(self, timestamp):
        self['submit_time'] = timestamp

    @property
    def finish_time(self):
        """Request has been handled"""
        return self['finish_time']

    @finish_time.setter
    def finish_time(self, timestamp):
        self['finish_time'] = timestamp


class BlkRequest(Request):
    """
    Request for Block Service
    """
    RWBS_FLAG = {'write': 1 << 0, 'discard': 1 << 1, 'read' : 1 << 2,
                 'rahead': 1 << 3, 'barrier': 1 << 4, 'sync': 1 << 5,
                 'meta': 1 << 6, 'secure': 1 << 7, 'flush': 1 << 8,
                 'fua': 1 << 9}

    @property
    def rwbs(self):
        return self['rwbs']

    @rwbs.setter
    def rwbs(self, rwbs):
        self['rwbs'] = rwbs

    @staticmethod
    def _op_type(rwbs):
        return 7 & rwbs

    @property
    def op_type(self):
        return self._op_type(self.rwbs)

    def op_type_same(self, req):
        return  self.op_type == req.op_type

    def op_type_equal(self, rwbs):
        return  self.op_type == self._op_type(rwbs)

    @property
    def offset(self):
        return self['offset']

    @offset.setter
    def offset(self, offset):
        self['offset'] = offset

    @property
    def length(self):
        return self['length']

    @length.setter
    def length(self, length):
        self['length'] = length

    @property
    def end(self):
        return self.offset + self.length - 1

    def contains(self, req):
        return self.offset <= req.offset and self.end >= req.end

    def overlaps(self, req):
        return self.offset <= req.end and req.offset <= self.end


class ReqQueue(deque):
    """
    FIFO queue of requests, sort by add_time
    """
    def req_out(self, critique, event):
        for req, idx in zip(self, range(len(self))):
            if critique(req, event):
                del self[idx]
                return req
        return None
