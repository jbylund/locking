import threading
import time
import unittest
from _thread import start_new_thread, TIMEOUT_MAX

RUNNING_ON_CI = True
# try:
    # RUNNING_ON_CI = True
import lock_tests
import support
# except ImportError:
    # RUNNING_ON_CI = False
    # from test import lock_tests, support


from .. import DynamoLock, FileLock, RedisLock, SocketLock


if True:
    class SocketLockTests(lock_tests.LockTests):
        locktype = staticmethod(SocketLock)

    class FileLockTests(lock_tests.LockTests):
        locktype = staticmethod(FileLock)


    if not RUNNING_ON_CI:
        class DynamoLockTests(lock_tests.LockTests):
            locktype = staticmethod(DynamoLock)

            def tearDown(self):
                for ithread in threading.enumerate():
                    if hasattr(ithread, 'exit_flag'):
                        ithread.exit_flag.set()
                        ithread.join()


            def test_reacquire(self):
                """Copied in because the wait_threads_exit """
                # Lock needs to be released before re-acquiring.
                lock = self.locktype()
                phase = []

                def f():
                    lock.acquire()
                    phase.append(None)
                    lock.acquire()
                    phase.append(None)

                with support.wait_threads_exit(timeout=5):
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
                pass

def _wait():
    # A crude wait/yield function not relying on synchronization primitives.
    time.sleep(0.01)

class RedisLockTests(lock_tests.LockTests):
    locktype = staticmethod(RedisLock)

    def test_thread_leak(self):
        pass

    def tearDown(self):
        for ithread in threading.enumerate():
            if hasattr(ithread, 'exit_flag'):
                ithread.exit_flag.set()
                ithread.join()


    def test_reacquire(self):
        """Copied in because the wait_threads_exit """
        # Lock needs to be released before re-acquiring.
        lock = self.locktype()
        phase = []

        def f():
            lock.acquire()
            phase.append(None)
            lock.acquire()
            phase.append(None)

        with support.wait_threads_exit(timeout=5):
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

