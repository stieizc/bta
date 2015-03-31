class Trigger:
    def __init__(self):
        self._listeners = {}

    def on(self, event, f=None):
        listeners = self._listeners.get(event)
        if not listeners:
            listeners = []
            self._listeners[event] = listeners
        if f:
            listeners.append(f)
        else:
            def fun(ff):
                listeners.append(ff)
                return ff
            return fun

    def trigger(self, event, *args, **kargs):
        listeners = self._listeners.get(event)
        if listeners:
            for f in listeners:
                f(*args, **kargs)
