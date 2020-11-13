import fcntl
import os
import tempfile
import time

from .. import BaseLock


class FileLock(BaseLock):
    @staticmethod
    def get_lockdir():
        try:
            tfdir = "/dev/shm"
            with tempfile.NamedTemporaryFile(dir=tfdir):
                pass
            return tfdir
        except Exception:
            return tempfile.gettempdir()

    lockdir = get_lockdir.__func__()

    def __init__(self, lockname=None, block=False):
        super(FileLock, self).__init__(lockname=lockname, block=block)
        self.lockname = "_".join(self.lockname.split("/"))
        self._lock_file = os.path.join(self.lockdir, self.lockname)
        self._lock_file_fd = None

    def acquire(self, blocking=True, timeout=-1):
        blocking = bool(blocking)
        self.check_args(blocking, timeout)
        ask_time = time.time()
        while True:
            open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
            fd = os.open(self._lock_file, open_mode)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self._lock_file_fd = fd
                self._locked = True
                return True
            except (IOError, OSError):
                os.close(fd)
                # did not get the lock this attempt
                if not blocking:
                    return False
                if 0 <= timeout:
                    wait_time = time.time() - ask_time
                    if timeout < wait_time:
                        return False
                self._wait()

    def release(self):
        fd = self._lock_file_fd
        if fd is None:
            return
        self._lock_file_fd = None
        fcntl.flock(fd, fcntl.LOCK_UN)
        self._locked = False
        os.close(fd)

    if True:

        def __del__(self):
            self.release()
