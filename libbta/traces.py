import os

from libbta.cache import Cache
from libbta.parser import TraceParser
from libbta.reconstructor import Reconstructor


class Traces:
    def __init__(self, config):
        self.config = config
        self.parsers, self.trace_files = \
            self.parser_map_traces(config['trace_dir'], config['parsers'])
        self.cache = Cache(config['cache_dir'])
        self.cache.add('traces', self.trace_files)
        self.cache.chain('requests', 'traces')
        self.layers = self.gen_layers(config['layers'])

    def load_traces(self):
        traces = self._load('traces')
        if not traces:
            traces = self.parse_traces()
            self.cache['traces'] = traces
        return traces

    def load_requests(self):
        requests = self._load('requests')
        if not requests:
            requests = Reconstructor(self.layers).read(self.load_traces())
            self.cache['requests'] = requests
        return requests

    def parse_traces(self):
        return TraceParser(self.parsers).parse()

    @staticmethod
    def parser_map_traces(trace_dir, parsers_ext):
        if type(trace_dir) is not list:
            trace_dir = [os.path.join(trace_dir, f) for f
                         in os.listdir(trace_dir)]

        trace_files = []
        parsers = {v: [] for v in parsers_ext.itervalues()}
        for f in trace_dir:
            _, ext = os.path.splitext(f)
            try:
                parsers[parsers_ext[ext]].append(f)
                trace_files.append(f)
            except KeyError:
                pass
        return (parsers, trace_files)

    def _load(self, name):
        return self.cache[name]

    @staticmethod
    def gen_layers(self, layerconf):
        layers = []
        upper = None
        for name, attrs in self.configs.layers:
            layer = attrs['class'](name)
            if upper:
                upper.relate('lower', layer)
                layer.relate('upper', upper)
            upper = layer
            layers.append((layer, attrs['domains']))
        return layers
