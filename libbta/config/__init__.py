from .reader import Reader


class Config:
    """
    Config for Bta
    """
    def __init__(self, conf):
        self.conf = conf

    def read(self, default={}):
        default.update(self.parse_args(self.conf))
        return default

    def parse_args(self, conf):
        return Reader(conf).read()

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
