from functools import wraps
from threading import Lock


def singleton(cls):
    cls._instance = None
    original_new = cls.__new__
    original_init = cls.__init__
    lock = Lock()

    @wraps(original_new)
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with lock:
                if cls._instance is None:
                    cls._instance = original_new(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not hasattr(self, '_initialized'):
            with lock:
                if not hasattr(self, '_initialized'):
                    original_init(self, *args, **kwargs)
                    self._initialized = True

    cls.__new__ = __new__
    cls.__init__ = __init__

    def __copy__(self):
        return cls._instance

    def __deepcopy__(self, memo):
        return cls._instance

    cls.__copy__ = __copy__
    cls.__deepcopy__ = __deepcopy__

    return cls
