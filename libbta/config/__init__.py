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
