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
        self.read_file()

    def read_file(self):
        """Read contents from self.filepath"""
        self.import_config()
        for k in ['parsers', 'layers', 'deducers']:
            v = getattr(self.configs, k)
            setattr(self, k, v if type(v) is list else [v])
        if hasattr(self.configs, 'trace_dir'):
            _trace_dir = self.configs.trace_dir
        else:
            _trace_dir = 'traces'
        self.trace_dir = os.path.join(os.path.dirname(self.filepath),
                                      _trace_dir)

    def import_config(self):
        sys.path.append(self.wpath)
        modname, _ = os.path.splitext(self.filename)
        self.configs = importlib.import_module(modname)
        sys.path.pop()

    def __repr__(self):
        return "Layers:\n{0}\nDeduers:\n{1}".format(self.layers, self.deducers)
