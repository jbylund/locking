import random
import sys
import time

from .utils import get_caller

TIMEOUT_MAX = int(sys.maxsize / 10**9)


class CouldNotLockException(Exception):
    pass


class BaseLock(object):
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
            hex(id(self)),
        )  # do I need to add owner/count?

    def locked(self):
        return self._locked

    def acquire(self, blocking=True, timeout=-1):
        raise NotImplementedError("Child class needs to impement acquire.")

    def check_args(self, blocking, timeout):
        if blocking:
            if timeout < 0:
                if timeout != -1:
                    raise ValueError("Cannot set negative timeout on blocking lock.")
            if TIMEOUT_MAX < timeout:
                raise OverflowError(
                    f"Cannot set a timeout greater than TIMEOUT_MAX ({TIMEOUT_MAX})."
                )
        else:
            if timeout >= 0:
                raise ValueError("Cannot set timeout on non-blocking lock.")

    def _wait(self):
        time.sleep(random.random() * 0.5)

    def __del__(self):
        self.release()

    def _at_fork_reinit(self):
        pass
