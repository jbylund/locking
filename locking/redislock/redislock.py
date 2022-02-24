import json
import threading
import time
from os import environ, getpid
from socket import gethostname

import redis

from .. import BaseLock
from ..heartbeater import HeartBeater


class RedisLock(BaseLock):
    """simple lock against redis"""

    def __init__(
        self, lockname=None, block=False, duration=5, heartbeat_interval=2, hosts=None
    ):
        super(RedisLock, self).__init__(lockname=lockname, block=block)
        self.hosts = hosts or ["127.0.0.1"]
        self.exit_flag = threading.Event()
        self.duration = duration * 1000
        self.heartbeat_interval = heartbeat_interval
        self.heartbeater = None
        self._locked = False
        self.conn = self.get_conn()

    def get_heartbeater(self):
        sub_conn = self.conn

        def heartbeat():
            sub_conn.set(
                self.lockname,
                json.dumps(self.get_contents()),
                px=self.duration,
                xx=True,
            )

        def release():
            self.exit_flag.clear()
            sub_conn.delete(self.lockname)

        return HeartBeater(
            heartbeat=heartbeat,
            exit_flag=self.exit_flag,
            interval=self.heartbeat_interval,
            release=release,
        )

    def get_conn(self, app_name="master"):
        last_error = None
        app_name = f"{gethostname()}:{getpid()}:{app_name}"
        for host in self.hosts:
            conn = redis.StrictRedis(
                host=host,
                port=int(environ.get("REDIS_PORT", 6379)),
                socket_timeout=1.5,
            )
            conn.client_setname(app_name)
            conn.info()
            return conn
        msg = f"Could not connect to Redis: last_error={last_error}, hosts={self.hosts}"
        raise Exception(msg)

    def get_contents(self):
        """get the contents of the lock (currently the contents are not used)"""
        return {
            "expiry": time.time() + self.duration,
            "host": gethostname(),
            "pid": getpid(),
        }

    def acquire(self, blocking=True, timeout=-1):
        blocking = bool(blocking)
        self.check_args(blocking, timeout)
        ask_time = time.time()
        while True:
            try:
                got_lock = bool(
                    self.conn.set(
                        self.lockname,
                        json.dumps(self.get_contents()),
                        nx=True,
                        px=self.duration,
                    )
                )
                if got_lock:
                    self.heartbeater = self.get_heartbeater()
                    self.heartbeater.start()
                    self._locked = True
                    return True
                else:
                    # check if we need to timeout and how long we've waited
                    # set a ttl if it doesn't have one...
                    if -1 == self.conn.ttl(
                        self.lockname
                    ):  # if it doesn't have an expiry
                        self.conn.expire(self.lockname, self.duration)  # set one
                    if blocking is False:
                        return False
                    if timeout < 0:
                        pass
                    else:
                        wait_time = time.time() - ask_time
                        if timeout < wait_time:
                            return False
                    self._wait()
            except Exception:
                raise
        return False

    def disconnect(self):
        try:
            self.conn.connection_pool.disconnect()
        except Exception as oops:
            print(oops)

    def release(self):
        self.exit_flag.set()  # after this it shouldn't heartbeat anymore
        if self.heartbeater is not None:
            self.heartbeater.join()  # join the thread...
            self.heartbeater = None
        self._locked = False
