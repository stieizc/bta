class Event(dict):
    """
    Basic unit of a trace file and an analysis
    """
    def __init__(self, trace, attrs_map=None):
        self.trace = trace
        if attrs_map:
            self.filter_trace(attrs_map)

    def __repr__(self):
        """
        Internal Printing
        """
        return "{0} {1}".format(super().__repr__(), self.event)

    def filter_trace(self, attrs_map):
        for t_attr, attr in attrs_map.items():
            if type(attr) == tuple:
                attr, _map = attr
                self[t_attr] = _map(self.trace[attr])
            else:
                self[t_attr] = self.trace[attr]


class Request:
    """
    Basic unit of analysis

    Each Request is associated with one or more event, and requests from
    different layers may be connected.
    """

    def __init__(self, name, generator):
        self.name = name
        self.related = {'upper': [], 'lower': [], 'merged': []}
        self.events = {}
        self.generator = generator

    def __repr__(self):
        return "{0}: {1}\n{2}".format(
            self.name, super().__repr__(), "\n".join(self.events))

    def __getitem__(self, item):
        return self.generator[item]

    def add_event(self, name, event):
        self.events[name] = event

    def link(self, _type, req):
        # print("Link {0}\nupper {1}".format(str(self), str(req)))
        self.related[_type].append(req)


class BlkRequest(Request):
    """
    Request for Block Service
    """

    @staticmethod
    def endof(_dict):
        return _dict['offset'] + _dict['length'] - 1

    def contains(self, _dict):
        return self['offset'] <= _dict['offset'] and \
            self.endof(self) >= self.endof(_dict)

    def overlaps(self, _dict):
        return self['offset'] <= self.endof(_dict) and \
            _dict['offset'] <= self.endof(self)
