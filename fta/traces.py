import os

from fta.cache import Cache
from fta.parser import parse_traces
from fta.reconstructor import Reconstructor


class Traces:
    def __init__(self, config):
        self.config = config
        self.trace_files_per_parser, self.trace_files = \
            self.parser_map_traces(config['trace_dir'], config['parsers'])
        self.cache = Cache(config['cache_dir'])
        self.cache.add('traces', self.trace_files)
        self.cache.chain('timelines', 'traces')
        self.layers = self.gen_layers(config['layers'])

    def load_traces(self):
        traces = self._load('traces')
        if not traces:
            traces = parse_traces(self.trace_files_per_parser)
            self.cache['traces'] = traces
        return traces

    def reconstruct(self):
        timelines = self._load('timelines')
        if not timelines:
            timelines = Reconstructor(self.layers).read(self.load_traces())
            self.cache['timelines'] = timelines
        return timelines

    @staticmethod
    def parser_map_traces(trace_dir, parsers_ext):
        if type(trace_dir) is not list:
            trace_dir = [os.path.join(trace_dir, f) for f
                         in os.listdir(trace_dir)]

        trace_files = []
        parsers = {v: [] for v in parsers_ext.values()}
        for f in trace_dir:
            _, _, ext = f.rpartition('.')
            try:
                parsers[parsers_ext[ext]].append(f)
                trace_files.append(f)
            except KeyError:
                pass
        return (parsers, trace_files)

    def _load(self, name):
        return self.cache[name]

    @staticmethod
    def gen_layers(layerconf):
        layers = []
        upper = None
        for name, _type, domains in layerconf:
            layer = _type(name)
            if upper:
                upper.relate('lower', layer)
                layer.relate('upper', upper)
            upper = layer
            layers.append((layer, domains))
        return layers
