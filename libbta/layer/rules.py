# For matching req by trace
def same_pos(req, trace):
    return same_props(req, trace, ['offset', 'length'])

def same_id(req, trace):
    return req['id'] == trace['id'] \

def same_props(req, trace, props):
    for p in props:
        if req[p] != trace[p]:
            return False
    return True
