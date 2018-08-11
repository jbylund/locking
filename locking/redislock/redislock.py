from socket import gethostname
from os import getpid
import redis
import json
import time
import threading
import random

from .. import BaseLock, CouldNotLockException

class HeartBeater(threading.Thread):
    """the job of this class is just to keep checking in to keep the lock up to date"""

    def __init__(self, interval=25, heartbeat=lambda: True, exit_flag=None):
        super(HeartBeater, self).__init__()
        assert exit_flag is not None
        # daemon thread so that when the parent exits it will disappear (we're going to try to clean it up anyways)
        self.daemon = True
        self.interval = interval  # this is how frequently to check in
        self.heartbeat = heartbeat  # this is the check-in function
        self.exit_flag = exit_flag
        self.jitter = 0.1

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
                print >> sys.stderr, oops


class RedisLock(BaseLock):
    """simple lock against redis"""
    def __init__(self, lockname=None, block=False, duration=120, heartbeat_interval=25, conn=None, hosts=None):
        # name="badname", block=True, duration=120, debug=True, heartbeat_interval=25, conn=None, hosts=None):
        super(RedisLock, self).__init__(lockname=lockname, block=block)
        self.hosts = hosts or ['127.0.0.1']
        self.conn = conn or self.get_conn()
        self.exit_flag = threading.Event()
        self.duration = duration
        def heartbeat():
            """the heartbeat function"""
            self.conn.setex(
                self.lockname, self.duration,
                json.dumps(self.get_contents())
            )
        self.heartbeater = HeartBeater(
            heartbeat=heartbeat, exit_flag=self.exit_flag, interval=heartbeat_interval)

    def get_conn(self):
        last_error = None
        app_name = "{}:{}".format(
            gethostname(),
            getpid()
        )
        for host in self.hosts:
            try:
                conn = redis.StrictRedis(host=host, socket_timeout=1.5)
                conn.client_setname(app_name)
                conn.info()
                return conn
            except Exception as oops:
                raise
        msg = 'Could not connect to Redis: last_error={}, hosts={}'.format(last_error, self.hosts)
        raise Exception(msg)

    def get_contents(self):
        """get the contents of the lock (currently the contents are not used)"""
        return {
            'expiry': time.time() + self.duration,
            'host': gethostname(),
            'pid': getpid(),
        }

    def __enter__(self):
        if self.block:
            while not self.conn.setnx(
                self.lockname,
                json.dumps(self.get_contents())
            ):
                time.sleep(random.random() * 10)
        else:
            if not self.conn.setnx(
                self.lockname,
                json.dumps(self.get_contents())
            ):
                if -1 == self.conn.ttl(self.lockname):  # if it doesn't have an expiry
                    self.conn.expire(self.lockname, self.duration)  # set one
                self.disconnect()
                raise CouldNotLockException(
                    """Could not get "{}" lock!""".format(self.lockname))
        self.conn.expire(self.lockname, self.duration)
        self.heartbeater.start()

    def disconnect(self):
        try:
            self.conn.connection_pool.disconnect()
        except Exception as oops:
            print oops

    def __exit__(self, err_type, err_val, err_trace):
        self.exit_flag.set()  # after this it shouldn't heartbeat anymore
        self.conn.delete(self.lockname)  # try to remove the lock from redis
        self.heartbeater.join()  # join the thread...
        self.disconnect()

