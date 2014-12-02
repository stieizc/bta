class Event:
    """
    Basic unit of a trace file and an analysis
    """
    def __init__(self, name, timestamp, attrs = {}):
        self.name = name
        self.timestamp = timestamp
        self.attrs = attrs

    def __repr__(self):
        """
        Internal Printing
        """
        return "{0} {1} {2}".format(self.name, self.timestamp, self.attrs)

    def get(self, attr_name):
        return self.attrs[attr_name]

    def get_int(self, attr_name):
        """
        Convert attr to int before return
        """
        return int(self.attrs[attr_name])

    def get_float(self, attr_name):
        """
        Convert attr to float before return
        """
        return int(self.attrs[attr_name])
