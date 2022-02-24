"""Helper to spawn a thread that keeps doing something."""
import random
import sys
import threading


class HeartBeater(threading.Thread):
    """the job of this class is just to keep checking in to keep the lock up to date"""

    def __init__(
        self, interval=25, heartbeat=lambda: True, exit_flag=None, release=lambda: True
    ):
        """Construct the heartbeater thread object."""
        super(HeartBeater, self).__init__()
        assert exit_flag is not None
        self.daemon = True  # daemon thread so that when the parent exits it will disappear (we're going to try to clean it up anyways)
        self.interval = interval  # this is how frequently to check in
        self.heartbeat = heartbeat  # this is the check-in function
        self.exit_flag = exit_flag
        self.jitter = 0.1
        self.release = release

    def get_sleep(self):
        base = (1 - self.jitter) * self.interval
        jitter = self.jitter * random.random() * self.interval
        return base + jitter

    def run(self):
        # keep heartbeating while we can
        while not self.exit_flag.wait(self.get_sleep()):
            try:
                self.heartbeat()
            except Exception as oops:
                print(oops, file=sys.stderr)
        self.release()
