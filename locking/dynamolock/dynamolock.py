#!/usr/bin/python
# my pid and instance uniquely identify myself
import os
import random
import threading
import time

import boto3
from botocore.errorfactory import ClientError

from .. import BaseLock, CouldNotLockException

from .heartbeater import HeartBeater

def get_host_id():
    try:
        with open('/etc/hostname') as hostname:
            return hostname.read()
    except:
        return "?"

class DynamoLock(BaseLock):
    def __init__(self, lockname=None, table="locks", checkpoint_frequency=2, ttl=5):
        super(DynamoLock, self).__init__(lockname=lockname)
        self.client = boto3.client('dynamodb', region_name='us-east-1')
        self.checkpoint_frequency = checkpoint_frequency
        self.host_id = get_host_id()
        self.pid = str(os.getpid())
        self.ttl = ttl
        self.table = table
        self.spin_frequency = 0.5
        self.exit_flag = threading.Event()
        self.heartbeater = None

    def get_heartbeater(self):
        self.exit_flag.clear()
        return HeartBeater(
            heartbeat=self.beat,
            exit_flag=self.exit_flag,
            interval=self.checkpoint_frequency,
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

    def acquire(self, blocking=True, timeout=-1):
        blocking = bool(blocking)
        self.check_args(blocking, timeout)
        start = time.time()
        while True:
            try:
                self.beat()
                self._locked = True
                break
            except ClientError as oops:
                if oops.response['Error']['Code'] == 'ResourceNotFoundException':
                    self._create_table()
                    continue
                if blocking is False:
                    return False
                if timeout < time.time() - start:
                    return False
                time.sleep(
                    self.spin_frequency * 2 *
                    random.random()
                )
        self.heartbeater = self.get_heartbeater()
        self.heartbeater.start()
        return True

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
            pass # it's only a best effort to release the lock
        self.exit_flag.set()
        self.heartbeater.join()
        self._locked = False
