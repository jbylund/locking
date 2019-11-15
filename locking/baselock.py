import sys

from .utils import get_caller
from . import CouldNotLockException

class BaseLock(object):

    TIMEOUT_MAX = int(sys.maxsize / 10**9)

    def __init__(self, lockname=None, block=True):
        self.lockname = lockname or get_caller()
        self.block = block
        self._locked = False

    def __enter__(self):
        if self.acquire() is False:
            raise CouldNotLockException

    def __exit__(self, err_type, err_val, err_tb):
        self.release()

    def __repr__(self):
        return "<%s %s.%s object at %s>" % (
            "locked" if self._locked else "unlocked",
            self.__class__.__module__,
            self.__class__.__qualname__,
            hex(id(self))
        ) # do I need to add owner/count?

    def locked(self):
        return self._locked

    def acquire(self, blocking=True, timeout=-1):
        raise NotImplementedError("Child class needs to impement acquire.")
