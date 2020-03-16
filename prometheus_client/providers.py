from threading import Lock


class Value(object):
    """Abstract metrics persistence class."""

    def __init__(self, typ, metric_name, name, labelnames,
                 labelvalues, **kwargs):
        raise NotImplementedError('__init__() must be '
                                  'implemented by %r' % self)

    def inc(self, amount):
        """Increment by value."""
        raise NotImplementedError('inc() must be implemented by %r' % self)

    def set(self, value):
        """Set value."""
        raise NotImplementedError('set() must be implemented by %r' % self)

    def get(self):
        """Get value."""
        raise NotImplementedError('get() must be implemented by %r' % self)


class ValueProvider(Value):
    """The base class that stores the value inside itself."""

    def __init__(self, typ, metric_name, name, labelnames, labelvalues,
                 **kwargs):
        self._value = 0.0
        self._lock = Lock()

    def inc(self, amount):
        with self._lock:
            self._value += amount

    def set(self, value):
        with self._lock:
            self._value = value

    def get(self):
        with self._lock:
            return self._value


class RedisProvider(Value):
    """Metric storage provider in Redis."""

    def __init__(self, typ, metric_name, name, labelnames, labelvalues,
                 **kwargs):
        self._name = self.get_name(typ, metric_name, name, labelnames,
                                   labelvalues, **kwargs)
        self._redis_app = self.get_redis_app()

    def inc(self, amount):
        self._redis_app.incrbyfloat(self._name, amount)

    def set(self, value):
        with self._redis_app.lock(self._name):
            self._redis_app.set(self._name, value)

    def get(self):
        return float(self._redis_app.get(self._name) or 0)

    def get_redis_app(self):
        """Returns a configured instance of Redis"""
        raise NotImplementedError('get_redis_app() must be '
                                  'implemented by %r' % self)

    def get_name(self, typ, metric_name, name, labelnames, labelvalues,
                 **kwargs):
        """
        Collects a unique key for storing data in Redis. If several labels
        coincide, then these metrics will use the common memory space.
        """
        raise NotImplementedError('get_name() must be implemented by %r' % self)


def get_redis_provider(redis_app):
    """Returns a provider using Redis."""

    class Provider(RedisProvider):
        """Metric storage provider in Redis."""

        def get_redis_app(self):
            return redis_app

        def get_name(self, typ, metric_name, name, labelnames, labelvalues,
                     **kwargs):
            label = ''
            if len(labelnames) == len(labelvalues):
                for index in range(len(labelnames)):
                    label += '_' + labelnames[index] + ':' + labelvalues[index]
            return name + label

    return Provider
