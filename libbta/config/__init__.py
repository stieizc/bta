import argparse
import os

from .configparser import ConfigParser
from .types import LayerTypes, DeducerTypes
from ..parser import parse_dir


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
        self.argparser.add_argument('-a', '--action',
                                    default='', help='Actions')
        self.parse_args()
        self.generate_events()
        self.generate_layers()

    def parse_args(self):
        self.args = self.argparser.parse_args()
        self.configparser = ConfigParser(self.args.config)
        self.configparser.read_file()

    def generate_events(self):
        self.events = parse_dir(self.configparser.trace_dir)

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
