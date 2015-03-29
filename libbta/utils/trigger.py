class Trigger:
    def __init__(self):
        self._listeners = {}

    def on(self, event):
        def fun(ff):
            listeners = self._listeners.get(event)
            if listeners:
                listeners.append(ff)
            else:
                self._listeners[event] = [ff]
            return ff
        return fun

    def trigger(self, event, *args, **kargs):
        listeners = self._listeners.get(event)
        if listeners:
            for f in listeners:
                f(*args, **kargs)
