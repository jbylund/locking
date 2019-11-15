from .. import SocketLock, FileLock, DynamoLock, RedisLock
import unittest
from test.lock_tests import LockTests

class SocketLockTests(LockTests):
    locktype = staticmethod(SocketLock)

class FileLockTests(LockTests):
    locktype = staticmethod(FileLock)

class DynamoLockTests(LockTests):
    locktype = staticmethod(DynamoLock)

class RedisLockTests(LockTests):
    locktype = staticmethod(RedisLock)
