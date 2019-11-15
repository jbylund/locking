class CouldNotLockException(Exception):
    pass

from .baselock import BaseLock
from .utils import get_caller
from .dynamolock import DynamoLock
from .filelock import FileLock
from .redislock import RedisLock
from .socketlock import SocketLock

