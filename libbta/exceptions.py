class TraceDiscarded(Exception):
    msg = "No matching request found for trace"
    def __init__(self, trace):
        self.trace = trace

    def __repr__(self):
        return self.msg
