class EventDiscarded(Exception):
    def __init__(self, event):
        self.event = event

    def __repr__(self):
        return "Discarded: {0}".format(self.event)

class EventDiscardedOnPurpose(Exception):
    def __init__(self, event):
        self.event = event

    def __repr__(self):
        return "Discarded on purpose: {0}".format(self.event)

class MergeFailed(Exception):
    def __init__(self, req, event):
        self.req = req
        self.event = event

    def __repr__(self):
        return "Merge Failed: {0} {1}".format(self.req, self.event)
