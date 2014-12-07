import os
import importlib

import libbta

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
    for events in event_queues:
        events.extend(events)
    if len(event_queues) > 1:
        events.sort(key=lambda e: e.timestamp)
    return events
