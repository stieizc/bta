class Event:
    """
    Basic unit of a trace file and an analysis
    """
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp
        self.attrs = {}

    def __repr__(self):
        """
        Internal Printing
        """
        return "{0} {1} {2}".format(self.name, self.timestamp, self.attrs)

    def __getitem__(self, key):
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = value


class Request:
    """
    Basic unit of analysis

    Each Request is associated with one or more event, and requests from
    different layers may be connected.
    """

    def __init__(self, name):
        self.name = name
        self.attrs = {}
        self.upper_reqs = []
        self.lower_reqs = []

    def __repr__(self):
        return "{0}: {1} {2}".format(self.name, self.timestamps, self.attrs)

    def __getitem__(self, key):
        return self.attrs[key]

    def get(self, key):
        return self.attrs.get(key)

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def get_event_attrs(self, event, attrs_map):
        for r_attr, e_attr in attrs_map:
            self[r_attr] = event[e_attr]

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
    @property
    def offset(self):
        return self.attrs['offset']

    @offset.setter
    def offset(self, offset):
        self.attrs['offset'] = offset

    @property
    def length(self):
        return self.attrs['length']

    @length.setter
    def length(self, length):
        self.attrs['length'] = length

    @property
    def type(self):
        return self.attrs['type']

    @type.setter
    def type(self, _type):
        self.attrs['type'] = _type

    @property
    def end(self):
        return self.offset + self.length - 1

    def contains(self, req):
        return self.offset <= req.offset and self.end >= req.end
