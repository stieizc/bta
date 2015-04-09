class Event(dict):
    """
    Basic unit of a trace file and an analysis
    """
    def __init__(self, trace, attrs_map=None):
        self.name = trace['name']
        self.timestamp = trace['timestamp']
        self.trace = trace
        if attrs_map:
            self.filter_trace(attrs_map)

    def __repr__(self):
        """
        Internal Printing
        """
        return "{0} {1} {2} {3}".format(
            self.name, self.timestamp, super().__repr__(), self.trace)

    def filter_trace(self, attrs_map):
        for t_attr, attr in attrs_map.items():
            if t_attr == 'additional':
                for k, v in attr:
                    self[k] = v
            elif type(attr) == tuple:
                attr, _map = attr
                self[t_attr] = _map(self.trace[attr])
            else:
                self[t_attr] = self.trace[attr]


class Request(dict):
    """
    Basic unit of analysis

    Each Request is associated with one or more event, and requests from
    different layers may be connected.
    """

    def __init__(self, name, generator):
        self.name = name
        self.related = {'upper': [], 'lower': [], 'merged': []}
        self.events = {}
        self.update(generator)

    def __repr__(self):
        return "{0}:\n{1}".format(
            self.name, "\n".join([str(item) for item in self.events.items()]))

    def add_event(self, name, event):
        self.events[name] = event

    def link(self, _type, req):
        # print("Link {0}\nupper {1}".format(str(self), str(req)))
        self.related[_type].append(req)

    def timestamp(self, name):
        return self.events[name].timestamp


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

    def response_time(self):
        return self.timestamp('finish') - self.timestamp('queue')

    def lower_response_time(self):
        qtime = self.timestamp('queue')
        deltas = [req.timestamp('queue') - qtime
                  for req in self.events['queue']]
        return float(sum(deltas))/len(deltas) \
            if len(deltas) > 0 else float('nan')
