from collections import deque


class Trace(dict):
    """
    Basic unit of a trace file and an analysis
    """
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp
        self.event = None

    def __repr__(self):
        """
        Internal Printing
        """
        return "{0} {1} {2} {3}".format(
            self.name, self.timestamp, self.event,
            super().__repr__())

    def gen_set_event(self, attrs_map):
        event = self.map2dict({}, attrs_map)
        self.event = event
        return event

    def map2dict(self, target, attrs_map):
        for target_attr, attr in attrs_map.iteritems():
            if target_attr == 'addtional':
                # attr will be additional key-value pair
                for k, v in attr:
                    target[k] = v
            else:
                if type(attr) == tuple:
                    attr, _map = attr
                    target[target_attr] = _map(self[attr])
                else:
                    target[target_attr] = self[attr]
        return target


class Request(dict):
    """
    Basic unit of analysis

    Each Request is associated with one or more event, and requests from
    different layers may be connected.
    """

    def __init__(self, name):
        self.name = name
        self.related = {'upper': [], 'lower': [], 'merged': []}
        self.timestamps = {}

    def __repr__(self):
        return "{0}: {1} {2}".format(self.name, self.timestamps,
                                     super().__repr__())

    def link(self, _type, req):
        # print("Link {0}\nupper {1}".format(str(self), str(req)))
        self.related[_type].append(req)


class BlkRequest(Request):
    """
    Request for Block Service
    """

    def __init__(self, name):
        super().__init__(name)

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
    def op_type(self):
        return self['ops'][0]

    @property
    def end(self):
        return self['offset'] + self['length'] - 1

    def contains(self, req):
        return self['offset'] <= req['offset'] and self['end'] >= req['end']

    def overlaps(self, req):
        return self['offset'] <= req['end'] and req['offset'] <= self['end']


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
