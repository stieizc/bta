from . import Deducer


def _deduce_lower_add(self, lower_req):
    """
    When a req is added to lower, find reqs contained by lower_req, set links
    between them
    """
    for upper_req in self.upper.submitted_reqs:
        if upper_req.type == lower_req.type and lower_req.contains(upper_req):
            upper_req.add_lower_req(lower_req)

def _deduce_upper_finish(self, upper_req):
    """
    When a req is finished in upper, find reqs linked in lower_layer, set them
    as finished
    """
    for lower_req in upper_req.lower_reqs:
        self.layers['lower'].finish_request(lower_req, upper_req.finish_time)

class VirtioRawDeducer(Deducer):
    """
    Deducer for block request, when upper and lower layers both are block
    layers.

    Get a request, find its offset and length. See if the requested layer has
    some issued request whose range contain / are contained in this range.

    Upper layers' request is contained by lower layers' requests
    """
    def __init__(self, upper, lower):
        super().__init__(upper, lower)
        self.deduce_funcs['lower'] = {'add': _deduce_lower_add}
        self.deduce_funcs['upper'] = {'finish': _deduce_upper_finish}