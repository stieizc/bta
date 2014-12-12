import babeltrace
import sys

from libbta import Event


def parse(traces_path):
    # a trace collection holds one to many traces
    col = babeltrace.TraceCollection()

    # add the trace provided by the user
    # (LTTng traces always have the 'ctf' format)
    if col.add_traces_recursive(traces_path, 'ctf') is None:
        raise RuntimeError('Cannot add trace')

    events = []
    # iterate events
    for e in col.events:
        event = Event(e.name, e.timestamp)
        event.attrs.update(e)
        events.append(event)

    return events
