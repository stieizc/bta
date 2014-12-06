import yaml
import os

try:
    from yaml import Cloader as Loader
except ImportError:
    from yaml import Loader


class ConfigParser:
    def __init__(self, path):
        """Bta configuration parser"""
        self.layers = {}
        self.deducers = []
        self.filepath = path
        _dir = os.path.join(os.path.dirname(os.path.realpath(path)), 'traces')
        self.trace_dir = _dir

        self.read_file()

    def read_file(self):
        """Read contents from self.filepath"""
        with open(self.filepath, 'r') as config_file:
            section = yaml.load(config_file, Loader=Loader)
            self.layers = section['Layers']
            self.deducers = section['Deducers']
            general = section.get('General')
            if general:
                _dir = general.get('TraceDir')
                if _dir:
                    self.trace_dir = _dir

    def __repr__(self):
        return "Layers:\n{0}\nDeduers:\n{1}".format(self.layers, self.deducers)
