import argparse
import os

from .configparser import ConfigParser
from .types import LayerTypes, DeducerTypes, Parsers


class Config:
    """
    Config for Bta
    """
    def __init__(self):
        self.layermaps = None
        self.deducers = None
        self.argparser = argparse.ArgumentParser(description='Block trace analyser')
        self.argparser.add_argument('-c', '--config', 
                                    default='bta.yaml', help='Configuration file')
        self.parse_args()
        self.generate_events()
        self.generate_layers()

    def parse_args(self):
        self.args = self.argparser.parse_args()
        self.configparser = ConfigParser(self.args.config)
        self.configparser.read_file()

    def generate_events(self):
        _dir = self.configparser.trace_dir
        events = []
        for f in os.listdir(_dir):
            _file = os.path.join(_dir, f)
            if not os.path.isfile(_file):
                continue
            _, ext = os.path.splitext(f)
            events.append(Parsers[ext[1:]](_file))
        self.merge_events(events)

    def generate_layers(self):
        self.layermaps = []
        self.deducers = []
        layers = {}
        for name, attrs in self.configparser.layers.items():
            layer = LayerTypes[attrs['type']](name)
            layers[name] = layer
            self.layermaps.append((layer, attrs['domains']))
        for _type, attrs in self.configparser.deducers.items():
            upper = layers[attrs['upper']]
            lower = layers[attrs['lower']]
            deducer = DeducerTypes[_type](upper, lower)
            self.deducers.append(deducer)

    def merge_events(self, event_queues):
        self.events = []
        for events in event_queues:
            self.events.extend(events)
        if len(event_queues) > 1:
            self.events.sort(key=lambda e: e.timestamp)
