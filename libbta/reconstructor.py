class Reconstructor:
    """
    From a list of traces, reconstruct requests for different layers.

    Events happens in different layers, and are associated with requests on
    each layer. Each request has multiple traces, e.g. issued, pended,
    finished.  Since we have one series of traces, but multiple levels of
    layers, We have to deduce wich trace is associated with each layer.

    Further more, since requests in different layers are linked (layer1 issued
    a request, layer2 received it and issued another), the relationship between
    different requests from different layers have to be deduced, too.

    In essence, "deducing" here means guessing, based on some assumptions on
    how the layers work, so the Sorter may well make mistakes. The better we
    know how the different layers interacts, the fewer mistakes we may make.
    But we may not know every detail of the layers, and even if we know them,
    they may be hard to program. Moreover, the tracer may decide not to trace
    those details, in consideration of impact on performance, or difficulties
    in implementing the trace. To make matters worth, "noise events" can be
    traced, and they do cause problems.

    Here's some of the Sorters assumption:
    0. A layer may have 0 or 1 upper layer, and 0 or 1 lower layer
    1. When lower layer issued a request, it is either not associted with upper
    layer, or associated with one or more "submitted" requests from upper layer
    """

    def __init__(self, layers):
        self.layers = layers
        self.ids = []

    def __repr__(self):
        string = '\n'.join([str(l) for l in self.layers])
        return string

    def read(self, traces):
        for trace in traces:
            self.dispatch(trace)
        for layer, _ in self.layers:
            print(layer)

    def dispatch(self, trace):
        for layer, domains in self.layers:
            if trace['domain'] in domains:
                layer.read_trace(trace)
