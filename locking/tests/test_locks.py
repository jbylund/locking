import unittest

RUNNING_ON_CI = False
try:
    RUNNING_ON_CI = True
    import lock_tests
except ImportError:
    RUNNING_ON_CI = False
    from test import lock_tests

from .. import DynamoLock, FileLock, RedisLock, SocketLock


class SocketLockTests(lock_tests.LockTests):
    locktype = staticmethod(SocketLock)

class FileLockTests(lock_tests.LockTests):
    locktype = staticmethod(FileLock)


if not RUNNING_ON_CI:
    class DynamoLockTests(lock_tests.LockTests):
        locktype = staticmethod(DynamoLock)

        def test_state_after_timeout(self):
            pass # can't differentiate between these things...

class RedisLockTests(lock_tests.LockTests):
    locktype = staticmethod(RedisLock)
