import os
import importlib


def parse_dir(_dir):
    event_queues = []
    for f in os.listdir(_dir):
        _file = os.path.join(_dir, f)
        if not os.path.isfile(_file):
            continue
        _, ext = os.path.splitext(f)
        mod = importlib.import_module('.parser_' + ext[1:], 'libbta.parser')
        event_queues.append(mod.parse(_file))
    return merge_events(event_queues)


def merge_events(event_queues):
    events = []

    for es in event_queues:
        events.extend(es)
    if len(event_queues) > 1:
        events.sort(key=lambda e: e.timestamp)
    #event_queues = [es for es in event_queues if es]
    #while len(event_queues) > 1:
    #    heads = [es[0] for es in event_queues]
    #    idx, min_val = min(enumerate(heads), key=lambda p: p[1].timestamp)
    #    events.append(min_val)
    #    event_queues[idx].popleft()
    #    event_queues = [es for es in event_queues if es]
    #if len(event_queues) == 1:
    #    events.extend(event_queues[0])
    return events
