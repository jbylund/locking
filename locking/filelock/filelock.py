import fcntl
import os
import tempfile
import time

from .. import BaseLock, CouldNotLockException

class FileLock(BaseLock):
    @staticmethod
    def get_lockdir():
        try:
            tfdir = '/dev/shm'
            with tempfile.NamedTemporaryFile(dir=tfdir) as tfh:
                pass
            return tfdir
        except:
            return tempfile.gettempdir()

    lockdir = get_lockdir.__func__()
    def __init__(self, lockname=None, block=False):
        super(FileLock, self).__init__(lockname=lockname, block=block)
        self.lockfilename = os.path.join(self.lockdir, lockname)
        self.lockfilehandle = open(self.lockfilename, 'w')

    def __enter__(self):
        flags = fcntl.LOCK_EX
        if self.block:
            pass # whatever
        else:
            flags |= fcntl.LOCK_NB
        try:
            fcntl.flock(self.lockfilehandle, flags)
        except IOError:
            raise CouldNotLockException()
        return self

    def __exit__(self, err_type, err_val, err_tb):
        self.lockfilehandle.close() # I think closing is enough to release?

    def __str__(self):
        return 'FileLock("{}")'.format(self.lockname)

