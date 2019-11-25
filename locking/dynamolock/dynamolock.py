#!/usr/bin/python
# my pid and instance uniquely identify myself
import os
import random
import string
import threading
import time

import boto3
from botocore.errorfactory import ClientError

from .. import BaseLock, CouldNotLockException

from .heartbeater import HeartBeater


def get_host_id():
    try:
        with open('/etc/hostname') as hostname:
            return hostname.read().strip()
    except Exception:
        return "?"


def randstr():
    return "".join(random.choice(string.ascii_lowercase) for _ in range(16))


def pack(local_shape):
    pass


def unpack(aws_shape):
    return {
        key: val_dict.popitem()[1]
        for key, val_dict in aws_shape.items()
    }


class DynamoLock(BaseLock):
    def __init__(self, lockname=None, table="locks", checkpoint_frequency=2, ttl=5):
        # lockname = lockname or randstr()
        super(DynamoLock, self).__init__(lockname=lockname)
        self.client = boto3.client('dynamodb', region_name='us-east-1')
        self.checkpoint_frequency = checkpoint_frequency
        self.host_id = get_host_id()
        self.pid = str(os.getpid())  # this is weird, but boto3 wants to get the values as strings, even if they're ints
        self.lockid = str(random.randint(10**16, 10**20))
        self.ttl = ttl
        self.table = table
        self.spin_frequency = 0.5
        self.exit_flag = threading.Event()
        self.heartbeater = None

    def get_heartbeater(self):
        host_id = self.host_id
        lockid = self.lockid
        pid = self.pid

        def heartbeat():
            try:
                self.client.put_item(
                    TableName=self.table,
                    Item=self.getitem(),
                    ReturnValues="ALL_OLD",
                    ConditionExpression=" OR ".join([
                        "attribute_not_exists(lockname)",
                        "attribute_not_exists(expiry)",
                        "expiry < :now",
                        "(host = :host AND pid = :pid AND ( attribute_not_exists(lockid) OR lockid = :lockid ) )",
                    ]),
                    ExpressionAttributeValues={
                        ":host": {"S": host_id},
                        ":lockid": {"N": lockid},
                        ":now": {"N": str(time.time()), },
                        ":pid": {"N": pid},
                    }
                )
            except ClientError as oops:
                print(oops)

        def release():
            self.exit_flag.clear()
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

        return HeartBeater(
            exit_flag=self.exit_flag,
            heartbeat=heartbeat,
            interval=self.checkpoint_frequency,
            release=release,
        )

    def getitem(self):
        expiry = time.time() + self.ttl
        return {
            "expiry": {"N": str(expiry)},
            "host": {"S": self.host_id},
            "lockid": {"N": self.lockid},
            "lockname": {"S": self.lockname},
            "pid": {"N": self.pid},
        }

    def beat(self):
        response = self.client.put_item(
            TableName=self.table,
            Item=self.getitem(),
            ReturnValues="ALL_OLD",
            ConditionExpression=" OR ".join([
                "attribute_not_exists(lockname)",
                "attribute_not_exists(expiry)",
                "expiry < :now",
                "(host = :host AND pid = :pid AND ( attribute_not_exists(lockid) OR lockid = :lockid ) )",
            ]),
            ExpressionAttributeValues={
                ":host": {"S": self.host_id},
                ":lockid": {"N": self.lockid},
                ":now": {"N": str(time.time()), },
                ":pid": {"N": self.pid},
            }
        )
        return response

    def acquire(self, blocking=True, timeout=-1):
        blocking = bool(blocking)
        self.check_args(blocking, timeout)
        start = time.time()
        while True:
            if not self._locked:
                try:
                    retval = self.beat()
                    self._locked = True
                    self.heartbeater = self.get_heartbeater()
                    self.heartbeater.start()
                    return True
                except ClientError as oops:
                    if oops.response['Error']['Code'] == 'ResourceNotFoundException':
                        self._create_table()
                        continue
            if blocking is False:
                return False
            if 0 < timeout:
                if timeout < time.time() - start:
                    return False
            self._wait()

    def _create_table(self):
        response = self.client.create_table(
            AttributeDefinitions=[
                {
                    "AttributeName": "lockname",
                    "AttributeType": "S",
                },
            ],
            TableName=self.table,
            KeySchema=[
                {
                    "AttributeName": "lockname",
                    "KeyType": "HASH",
                },
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 25,
                "WriteCapacityUnits": 25,
            },
        )

    def release(self):
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
        except ClientError:  # what can happen here?
            pass  # it's only a best effort to release the lock
        self.exit_flag.set()
        if self.heartbeater:
            self.heartbeater.join()
        self._locked = False
