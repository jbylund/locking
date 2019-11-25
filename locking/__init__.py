"""
xxx
"""

class CouldNotLockException(Exception):
    pass

from .baselock import BaseLock
from .dynamolock import DynamoLock
from .filelock import FileLock
from .redislock import RedisLock
from .socketlock import SocketLock
from .utils import get_caller
