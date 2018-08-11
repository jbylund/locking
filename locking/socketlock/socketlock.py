import socket
import time
import random

from .. import BaseLock, CouldNotLockException

class SocketLock(BaseLock):

    def __init__(self, lockname=None, block=True):
        super(SocketLock, self).__init__(lockname=lockname, block=block)
        self.socket_name = chr(0) + self.lockname
        self._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    def __enter__(self):
        ask_time = time.time()
        while True:
            wait_time = time.time() - ask_time
            try:
                self._lock_socket.bind(self.socket_name)
                break
            except Exception as oops:
                if self.block is True:
                    pass
                elif self.block is False or wait_time > self.block:
                    raise CouldNotLockException()
                time.sleep(random.random() * 0.005)

    def __exit__(self, a, b, c):
        self._lock_socket = None
        del self._lock_socket
