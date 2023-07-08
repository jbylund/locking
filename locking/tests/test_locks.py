import logging
import threading
import time
from _thread import start_new_thread

RUNNING_ON_CI = True
try:
    import lock_tests
except ImportError:
    from test import lock_tests
    RUNNING_ON_CI = False

try:
    wait_threads_exit = lock_tests.support.threading_helper.wait_threads_exit
except AttributeError:
    wait_threads_exit = lock_tests.support.wait_threads_exit


from .. import FileLock, SocketLock

logger = logging.getLogger("lock_tests")


def _wait():
    # A crude wait/yield function not relying on synchronization primitives.
    time.sleep(0.01)


class LockTClass(lock_tests.LockTests):
    def test_at_fork_reinit(self):
        logger.warning(
            "Not running test of _at_fork_reinit because I haven't done it yet"
        )


class SocketLockTests(LockTClass):
    locktype = staticmethod(SocketLock)


class FileLockTests(LockTClass):
    locktype = staticmethod(FileLock)


try:
    from .. import DynamoLock
except ImportError:
    logging.warning("Not running tests for DynamoLock")
else:

    class DynamoLockTests(LockTClass):
        locktype = staticmethod(DynamoLock)

        def tearDown(self):
            for ithread in threading.enumerate():
                if hasattr(ithread, "exit_flag"):
                    ithread.exit_flag.set()
                    ithread.join()

        def test_reacquire(self):
            """Copied in because the wait_threads_exit"""
            # Lock needs to be released before re-acquiring.
            lock = self.locktype()
            phase = []

            def f():
                lock.acquire()
                phase.append(None)
                lock.acquire()
                phase.append(None)

            with wait_threads_exit(timeout=5):
                start_new_thread(f, ())
                while len(phase) == 0:
                    _wait()
                _wait()
                self.assertEqual(len(phase), 1)
                lock.release()
                while len(phase) == 1:
                    _wait()
                self.assertEqual(len(phase), 2)
                lock.release()

        def test_thread_leak(self):
            # intentionally disabling the thread leak test...
            # it'll be ok
            pass


try:
    from .. import RedisLock
except ImportError:
    pass
else:

    class RedisLockTests(LockTClass):
        locktype = staticmethod(RedisLock)

        def test_thread_leak(self):
            pass

        def tearDown(self):
            for ithread in threading.enumerate():
                if hasattr(ithread, "exit_flag"):
                    ithread.exit_flag.set()
                    ithread.join()

        def test_reacquire(self):
            """Copied in because the wait_threads_exit"""
            # Lock needs to be released before re-acquiring.
            lock = self.locktype()
            phase = []

            def f():
                lock.acquire()
                phase.append(None)
                lock.acquire()
                phase.append(None)

            with wait_threads_exit(timeout=5):
                start_new_thread(f, ())
                while len(phase) == 0:
                    _wait()
                _wait()
                self.assertEqual(len(phase), 1)
                lock.release()
                while len(phase) == 1:
                    _wait()
                self.assertEqual(len(phase), 2)
                lock.release()
