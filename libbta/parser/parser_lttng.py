import babeltrace
import sys


def parse(traces_path):
    # a trace collection holds one to many traces
    col = babeltrace.TraceCollection()

    # add the trace provided by the user
    # (LTTng traces always have the 'ctf' format)
    if col.add_traces_recursive(traces_path, 'ctf') is None:
        raise RuntimeError('Cannot add trace')

    # iterate events
    for event in col.events:
        print("{0} {1}".format(event.name, event.timestamp))
        for f, v in event.items():
            print("{0} {1}".format(f, v))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        msg = 'Usage: python {} TRACEPATH'.format(sys.argv[0])
        raise ValueError(msg)

    parse(sys.argv[1])
