from .. import BaseLock

class DynamoLock(BaseLock):
    def __enter__(self):
        pass

    def __exit__(self, err_type, err_val, err_tb):
        pass
