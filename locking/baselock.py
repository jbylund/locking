from utils import get_caller

class BaseLock(object):
    def __init__(self, lockname=None, block=True):
        self.lockname = lockname or get_caller()
        self.block = block

    def __enter__(self):
        pass

    def __exit__(self, err_type, err_val, err_tb):
        pass
