class Layer:
    """
    Layers contain requests. There is a hierarchy of layers:

    Layer 0     domain0, domain1
              --------------------
                       |
              --------------------
                       |
    Layer 2         domain0
              --------------------

    Events' host and domain are used for identifying their layers, these
    identifiers must be unique between layers.
    """

    def __init__(self, name, upper=None):
        self.name = name
        self.upper = upper

    def __repr__(self):
        string = self.name
        if self.upper:
            string += ": Upper {1}".format(self.upper.name)
        return string
