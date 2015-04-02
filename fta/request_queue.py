from collections import deque
from .exceptions import EventDiscarded


class ReqQueue(deque):
    """
    FIFO queue of requests, sort by add_time
    """
    def req_out(self, critique, event):
        for req, idx in zip(self, range(len(self))):
            if critique(req, event):
                del self[idx]
                return req
        raise EventDiscarded(event)
