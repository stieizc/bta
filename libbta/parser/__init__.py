class TraceParser(dict):
    def __init__(self, parsers_ext, files_ext):
        event_queues = []
        for ext, parser in extmap.items():
            files = files_ext.get(ext)
            if files:
                event_queues.extend(parser.parse_files(files))
        return merge_sorted(event_queues, lambda e: e.timestamp)


def merge_sorted(lists, key):
    if len(lists) == 1:
        return lists[0]
    merged = []
    for l in lists:
        merged.extend(l)
    merged.sort(key=key)
    return merged
