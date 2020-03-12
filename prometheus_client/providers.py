from threading import Lock


class Value(object):
    """Abstract metrics persistence class."""

    def __init__(self, typ, metric_name, name, labelnames, labelvalues, **kwargs):
        raise NotImplementedError('__init__() must be implemented by %r' % self)

    def inc(self, amount):
        """Increment by value."""
        raise NotImplementedError('inc() must be implemented by %r' % self)

    def set(self, value):
        """Set value."""
        raise NotImplementedError('set() must be implemented by %r' % self)

    def get(self):
        """Get value."""
        raise NotImplementedError('get() must be implemented by %r' % self)

    @property
    def lock(self):
        """Provider lock."""
        raise NotImplementedError('lock must be implemented by %r' % self)


class ValueProvider(Value):
    """The base class that stores the value inside itself."""

    def __init__(self, typ, metric_name, name, labelnames, labelvalues, **kwargs):
        self._value = 0.0
        self._lock = Lock()

    def inc(self, amount):
        self._value += amount

    def set(self, value):
        self._value = value

    def get(self):
        return self._value

    @property
    def lock(self):
        return self._lock


