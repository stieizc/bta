class Request:
    """
    Basic unit of analysis

    Each Request is associated with one or more event, and requests from
    different layers may be connected.
    """

    def __init__(self, name, attrs={}):
        self.name = name
        self.attrs = attrs
        self.timestamps = {}

    def __repr__(self):
        return "{0}: {1} {2}".format(self.name, self.timestamps, self.attrs)

    def get(self, attr_name):
        return self.attrs[attr_name]

    @property
    def add_time(self):
        """Request add_time or none"""
        return self.timestamps.get('add_time')

    @add_time.setter
    def add_time(self, timestamp):
        self.timestamps['add_time'] = timestamp

    @property
    def submit_time(self):
        """Request is submitted for handling"""
        return self.timestamps.get('submit_time')

    @submit_time.setter
    def submit_time(self, timestamp):
        self.timestamps['submit_time'] = timestamp

    @property
    def finish_time(self):
        """Request has been handled"""
        return self.timestamps.get('finish_time')

    @finish_time.setter
    def finish_time(self, timestamp):
        self.timestamps['finish_time'] = timestamp


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
