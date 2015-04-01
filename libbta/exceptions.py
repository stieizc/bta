class EventDiscarded(Exception):
    def __init__(self, event):
        self.event = event
