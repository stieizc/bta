import os.path
import sys
import importlib


class Reader:
    def __init__(self, path):
        """Bta configuration parser"""
        self.filepath = os.path.realpath(path)
        self.wpath, self.filename = os.path.split(self.filepath)
        assert os.path.isdir(self.wpath), \
            "{0} is not a directory".format(self.wpath)

    def read(self):
        """Read contents from self.filepath"""
        config = self.import_config()
        for k in ['parsers', 'layers', 'deducers']:
            v = config[k]
            if type(v) is not list:
                config[k] = [v]
        return config

    def import_config(self):
        sys.path.append(self.wpath)
        modname, _ = os.path.splitext(self.filename)
        configmod = importlib.import_module(modname)
        sys.path.pop()
        return configmod.config

    def __repr__(self):
        return "Layers:\n{0}\nDeduers:\n{1}".format(self.layers, self.deducers)
