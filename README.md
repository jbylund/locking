# locking

![build status](https://jbylund.semaphoreci.com/badges/locking/branches/master.svg?style=semaphore)
[view build logs](https://jbylund.semaphoreci.com/branches/a07cc01d-abee-46d0-8557-64abee8fbfc2)


1. [Overview](#overview)
1. [Examples](#examples)
1. [Installation](#installation)

## <a id='overview'>Overview</a>

These locks provide a similar interface to those in the [threading](https://docs.python.org/3/library/threading.html#threading.Lock) and [multiprocessing](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Lock) modules with a different set of tradeoffs.
These locks are useable by multiple different processes when those processes agree on a naming scheme.
This can be used in order to allow multiple processes running on the same machine to semi-coordinate or in the case of the redis or dynamo backed locks multiple processes running on different machines to coordinate work.
This provides a different type of coordination than multiple workers consuming from a single queue and can allow quickly prototyping a solution where workers attempt to grab a job and take a lock on it, grabbing another job if they fail at getting the lock.
One benefit of this type of solution is that it allows running on spot hardware in the cloud since if a single job is dropped before it is completed the lock will soon expire and another worker will be able to grab that same piece of work.

Much like the locks provided by the threading/multiprocessing modules, these can (and probably should) be used as context managers.

## <a id='examples'>Examples</a>

### SocketLock

`SocketLock` requires no additional third party libs, and should work well on \*nix OS's.

Advantages:
* if a process dies the lock is released ~instantly
* no lockfiles polluting the filesystem

Disadvantages:
* requires all processes to be on the same host OS
* only works on nix-based os's (and maybe not even mac)

```python
from locking import SocketLock
import time

with SocketLock(lockname="uniquename") as mylock:
    # at this point we're holding the lock and can
    # safely perform operations without worrying about
    # other threads/process holding a lock with this name
    # interfering
    time.sleep(1)
```

### FileLock

`FileLock` requires no additional third party libs and _should_ work on most OS's, with the disclaimer that I only have access to \*nix OS's.

```python
from locking import FileLock
import time

with FileLock(lockname="foolock") as mylock:
    time.sleep(1)
```

### RedisLock

`RedisLock` requires [redis](https://github.com/redis/redis-py) and obviously a redis server.
The advantage of `RedisLock` over `SocketLock` or `FileLock` is that you don't need to be on the same host as other processes.
This can be useful if you want one of N hosts to perform some action.

```python
from locking import RedisLock
import time

with RedisLock(lockname="some_process_identifier", hosts=["myredis.com"]):
    time.sleep(1)
```

### DynamoLock

`DynamoLock` doesn't require an always on redis like `RedisLock`, however it does require dynamodb access on AWS.
In theory this should be pretty cheap.

```python
from locking import DynamoLock
import time

with DynamoLock(lockname="some_process_identifier", table="locks", checkpoint_frequency=2, ttl=5):
    time.sleep(1)
```

## <a id='installation'>Installation</a>

### From PyPI

```shell
python -m pip install --upgrade locking
```

### From GitHub

```shell
python -m pip install --upgrade git+https://git@github.com/jbylund/locking.git
```
