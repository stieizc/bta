import glob
import os.path


class Parser:
    """
    Can only have classmethods and staticmethods
    """
    @classmethod
    def parse_files(cls, files):
        return [cls.parse(f) for f in files]
