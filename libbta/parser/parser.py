import glob
import os.path


class Parser:
    def __init__(self, exts):
        if type(exts) is not list:
            exts = [exts]
        self.exts = exts

    def parse_dir(self, directory):
        return [self.parse(_file) for ext in self.exts
                for _file in self.iter_files(directory)]

    def iter_files(self, directory):
        for ext in self.exts:
            for _file in self.iter_file_with_ext(directory, ext):
                print(_file)
                yield _file

    @staticmethod
    def iter_file_with_ext(directory, ext):
        return glob.glob(os.path.join(directory, '*.{}'.format(ext)))
