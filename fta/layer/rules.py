# For matching req by event
def same_pos(req, event):
    return same_props(req, event, ['offset', 'length'])

def same_id(req, event):
    return req['id'] == event['id']

def same_op_type(req, event):
    return req['ops'][0] == event['ops'][0]

def same_props(req, event, props):
    for p in props:
        if req[p] != event[p]:
            return False
    return True
