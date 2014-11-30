class Event:
    """
    Basic unit of a trace file and an analysis
    """
    def __init__(self, name, timestamp, attrs):
        self.name = name
        self.timestamp = timestamp
        self.attrs = attrs

    def __repr__(self):
        """
        Internal Printing
        """
        return "{0} {1} {2}".format(self.name, self.timestamp, self.attrs)


class BlkEvent(Event):
    """
    Basic unit of block events
    """
    def __init__(self, arg):
        super().__init__()
        self.arg = arg
