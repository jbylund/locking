"""
xxx
"""
from .custom_exceptions import CouldNotLockException
from .baselock import BaseLock
from .filelock import FileLock
from .socketlock import SocketLock
from .utils import get_caller

outgoing = [
    BaseLock,
    CouldNotLockException,
    FileLock,
    get_caller,
    SocketLock,
]

try:
    from .redislock import RedisLock
except ImportError:
    pass
else:
    outgoing.append(RedisLock)

try:
    from .dynamolock import DynamoLock
except ImportError:
    # no boto3
    pass
else:
    outgoing.append(DynamoLock)
