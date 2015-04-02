import os.path
import pickle


class Cache:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        self.caches = {}

    def add(self, name, deps=[]):
        deps = deps if type(deps) is list else [deps]
        if name in self.caches:
            self.caches[name]['deps'].extend(deps)
        else:
            self.caches[name] = {'file': self.get_cache_name(name),
                                 'deps': deps, 'data': None}

    def chain(self, name, other_names):
        other_names = other_names if type(other_names) is list \
            else [other_names]
        self.add(name, [self.caches[n]['file'] for n in other_names])

    def __getitem__(self, name):
        cache = self.caches[name]
        if self._is_latest(cache):
            if not cache['data']:
                with open(cache['file'], 'br') as inbin:
                    cache['data'] = pickle.load(inbin)
        else:
            cache['data'] = None;
        return cache['data']

    def __setitem__(self, name, data):
        cache = self.caches[name]
        with open(cache['file'], 'bw') as outbin:
            pickle.dump(data, outbin)
            cache['data'] = data

    def is_latest(self, name):
        cache = self.caches[name]
        return self._is_latest(cache)

    def get_cache_name(self, name):
        return os.path.join(self.cache_dir, name)

    def _is_latest(self, cache):
        if not os.path.exists(cache['file']):
            return False
        ctime = os.path.getctime(cache['file'])
        for f in cache['deps']:
            if ctime < os.path.getctime(f):
                return False
        return True
