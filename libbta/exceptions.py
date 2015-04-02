class EventDiscarded(Exception):
    def __init__(self, event):
        self.event = event

class MergeFailed(Exception):
    def __init__(self, req, event):
        self.req = req
        self.event = event
