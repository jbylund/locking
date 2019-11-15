"""Lock implementation using posix virtual sockets."""
import socket
import time
import random
import errno

from .. import BaseLock

TIMEOUT_MAX = BaseLock.TIMEOUT_MAX


class SocketLock(BaseLock):
    """Lock implementation using posix virtual sockets."""

    def __init__(self, lockname=None):
        """Create a socket lock in the unlocked state."""
        super(SocketLock, self).__init__(lockname=lockname)
        self.socket_name = chr(0) + self.lockname
        self._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    def acquire(self, blocking=True, timeout=-1):
        """Attempt to acquire the lock, returning True on success, False on failure."""
        blocking = bool(blocking)
        if blocking:
            if timeout < 0:
                if timeout != -1:
                    raise ValueError("Cannot set negative timeout on blocking lock.")
            if TIMEOUT_MAX < timeout:
                raise OverflowError("Cannot set a timeout greater than TIMEOUT_MAX ({}).".format(TIMEOUT_MAX))
        else:
            if timeout >= 0:
                raise ValueError("Cannot set timeout on non-blocking lock.")
        ask_time = time.time()
        while True:
            try:
                self._lock_socket.bind(self.socket_name)
                self._locked = True
                return True
            except OSError as oops:
                # TODO: handle case where you get bad file descriptor
                # means you need to replace the socket and try again
                if oops.errno == errno.EBADFD:
                    self._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                elif oops.errno == errno.EINVAL:  # someone else has the lock
                    if blocking is False:
                        return False
                    else:
                        if timeout < 0:
                            # blocking is True no timeout
                            pass
                        else:
                            # blocking is True, finite timeout
                            wait_time = time.time() - ask_time
                            if timeout < wait_time:
                                return False
                    time.sleep(random.random() * 0.005)
                else:
                    raise

    def release(self):
        """Release the lock."""
        if not self._locked:
            raise AssertionError("Cannot release an open lock.")
        self._lock_socket.shutdown(socket.SHUT_WR)
        self._lock_socket.close()
        # there is a race condition right here...
        # if another thread acquires the lock before we make a new one
        self._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._locked = False
