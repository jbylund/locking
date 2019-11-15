#!/usr/bin/python
# my pid and instance uniquely identify myself
import os
import random
import sys
import threading
import time

from .. import BaseLock, CouldNotLockException
import boto3
from botocore.errorfactory import ClientError

def get_host_id():
    try:
        with open('/etc/hostname') as hostname:
            return hostname.read()
    except:
        return "?"

class HeartBeater(threading.Thread):
    """the job of this class is just to keep checking in to keep the lock up to date"""
    def __init__(self, interval=25, heartbeat=lambda: True, exit_flag=None):
        super(HeartBeater, self).__init__()
        assert exit_flag is not None
        self.daemon = True # daemon thread so that when the parent exits it will disappear (we're going to try to clean it up anyways)
        self.interval = interval # this is how frequently to check in
        self.heartbeat = heartbeat # this is the check-in function
        self.exit_flag = exit_flag
        self.jitter = 0.1

    def get_sleep(self):
        base = (1 - self.jitter) * self.interval
        jitter = self.jitter * random.random() * self.interval
        return base + jitter

    def run(self):
        while not self.exit_flag.wait(self.get_sleep()): # keep heartbeating while we can
            try:
                self.heartbeat()
            except Exception as oops:
                print(oops, file=sys.stderr)


class DynamoLock(BaseLock):
    def __init__(self, lockname, table="locks", checkpoint_frequency=2, ttl=5):
        self.client = boto3.client('dynamodb', region_name='us-east-1')
        self.checkpoint_frequency = checkpoint_frequency
        self.host_id = get_host_id()
        self.lockname = lockname
        self.pid = str(os.getpid())
        self.ttl = ttl
        self.table = table
        self.spin_frequency = 0.5
        self.exit_flag = threading.Event()
        self.heartbeater = HeartBeater(
            heartbeat=self.beat,
            exit_flag=self.exit_flag,
            interval=checkpoint_frequency
        )

    def getitem(self):
        expiry = time.time() + self.ttl
        return {
            "lockname": {
                "S": self.lockname
            },
            "pid": {
                "N": self.pid
            },
            "host": {
                "S": self.host_id
            },
            "expiry": {
                "N": str(expiry)
            }
        }

    def beat(self):
        return self.client.put_item(
            TableName=self.table,
            Item=self.getitem(),
            ConditionExpression='attribute_not_exists(lockname) or attribute_not_exists(expiry) or expiry < :now or (host = :host and pid = :pid)',
            ExpressionAttributeValues={
                ":now": {
                    "N": str(time.time()),
                },
                ":host": {
                    "S": self.host_id
                },
                ":pid": {
                    "N": self.pid
                }
            }
        )

    def __enter__(self, block=True):
        start = time.time()
        while True:
            try:
                self.beat()
                break
            except ClientError as oops:
                if block is False or (block is not True and time.time() - start < block):
                    raise CouldNotLockException()
                time.sleep(
                    self.spin_frequency * 2 *
                    random.random()
                )
        self.heartbeater.start()

    def __exit__(self, errtype, errval, errtb):
        if errtype:
            pass
        try:
            self.client.delete_item(
                TableName=self.table,
                Key={
                    "lockname": {
                        "S": self.lockname
                    }
                },
                ConditionExpression='pid = :pid and host = :host',
                ExpressionAttributeValues={
                    ":pid": {
                        "N": self.pid
                    },
                    ":host": {
                        "S": self.host_id
                    }
                }
            )
        except ClientError as oops:
            pass

def main():
    print("asking for lock at", time.time())
    with DynamoLock("foolock") as foo:
        print("lock acquired at", time.time())
        time.sleep(10)
        a = 1 / 0
        print("releasing lock at", time.time())
    print("lock released at", time.time())


if "__main__" == __name__:
    main()
