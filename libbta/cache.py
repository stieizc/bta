import os
import pickle


class EventCache:
    def __init__(self, filepath, trace_dir):
        self.filepath = filepath
        self.trace_dir = trace_dir

    def read(self):
        events = None
        if self.up2date():
            with open(self.filepath, 'br') as inbin:
                events = pickle.load(inbin)
        return events

    def update(self, events):
        if not self.up2date():
            with open(self.filepath, 'bw') as outbin:
                pickle.dump(events, outbin)

    def up2date(self):
        if not os.path.isfile(self.filepath):
            return False
        for f in os.listdir(self.trace_dir):
            _file = os.path.join(self.trace_dir, f)
            if os.path.getctime(self.filepath) < os.path.getctime(_file):
                return False
        return True
