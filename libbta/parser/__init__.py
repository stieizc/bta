def parse_dir(parsers, directory):
    event_queues = []
    for parser in parsers:
        event_queues.extend(parser.parse_dir(directory))
    return merge_sorted(event_queues, lambda e: e.timestamp)


def merge_sorted(lists, key):
    if len(lists) == 1:
        return lists[0]
    merged = []
    for l in lists:
        merged.extend(l)
    merged.sort(key=key)
    return merged
