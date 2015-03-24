import argparse
import os

from .reader import Reader
from ..parser import parse_dir
from ..cache import EventCache


class Config:
    """
    Config for Bta
    """
    def __init__(self):
        self.layermaps = None
        self.deducers = None
        self.argparser = argparse.ArgumentParser(description='Block trace analyser')
        self.argparser.add_argument('-c', '--config',
                                    default='config.py', help='Configuration file')
        self.argparser.add_argument('--event_cache', 
                                    default='.event.cache', help='Events cache')
        self.argparser.add_argument('-a', '--action',
                                    default='', help='Actions')
        self.parse_args()
        self.generate_events()
        self.generate_layers()

    def parse_args(self):
        self.args = self.argparser.parse_args()
        self.configs = Reader(self.args.config)
        self.event_cache = EventCache(self.args.event_cache,
                                      self.configs.trace_dir)

    def generate_events(self):
        self.events = self.event_cache.read()
        if not self.events:
            self.events = parse_dir(self.configs.parsers, self.configs.trace_dir)
            self.event_cache.update(self.events)

    def generate_layers(self):
        self.layermaps = []
        self.deducers = []
        layers = {}
        for name, attrs in self.configs.layers:
            layer = attrs['class'](name)
            layers[name] = layer
            self.layermaps.append((layer, attrs['domains']))
        for deducer_class, attrs in self.configs.deducers:
            upper = layers[attrs['upper']]
            lower = layers[attrs['lower']]
            deducer = deducer_class(upper, lower)
            self.deducers.append(deducer)
