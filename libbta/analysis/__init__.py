from libbta import Event


class Request:
    """
    Basic unit of analysis

    Each Request is associated with one or more event, and requests from
    different layers may be connected.
    """

    add_time = 0
    submit_time = 1
    finish_time = 2

    def __init__(self, name):
        self.name = name
        self.timestamps = {}

    @property
    def add_time(self):
        """Request add_time or none"""
        return self.timestamps.get(Request.add_time)

    @add_time.setter
    def add_time(self, timestamp):
        self.timestamps[Request.add_time] = timestamp

    @property
    def submit_time(self):
        """Request is submitted for handling"""
        return self.timestamps.get(Request.submit_time)

    @submit_time.setter
    def submit_time(self, timestamp):
        self.timestamps[Request.submit_time] = timestamp

    @property
    def finish_time(self):
        """Request has been handled"""
        return self.timestamps.get(Request.finish_time)

    @finish_time.setter
    def finish_time(self, timestamp):
        self.timestamps[Request.finish_time] = timestamp
