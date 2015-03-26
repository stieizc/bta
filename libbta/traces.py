import os

from libbta.cache import Cache
from libbta.parse import TraceParser


class Traces:
    def __init__(self, trace_dir, cache_dir, parsers_ext):
        self.trace_files = [os.path.join(trace_dir, f) for f
                            in os.listdir(trace_dir)] \
            if type(trace_dir) is list else trace_dir
        self.group_files_ext()
        self.cache = Cache(cache_dir)
        self.cache.add('events', self.trace_files)
        self.cache.chain('requests', 'events')
        self.parsers_ext = parsers_ext

    def load(self):
        events = self.cache['events']
        events = events if events else self.parse()

    def parse(self):
        return TraceParser(self.parsers_ext, self.trace_files_ext)

    def group_files_ext(self):
        files_ext = {}
        for ext in self.parsers_ext:
            files_ext[ext] = []
        for f in self.trace_files:
            _, ext = os.path.splitext(f)
            try:
                files_ext[ext].append(f)
            except KeyError:
                pass
        self.trace_files_ext = files_ext
