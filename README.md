# locking

![build status](https://jbylund.semaphoreci.com/badges/locking/branches/master.svg?style=semaphore)[view logs](https://jbylund.semaphoreci.com/branches/a07cc01d-abee-46d0-8557-64abee8fbfc2)


1. [Overview](#overview)
1. [Examples](#examples)
1. [Installation](#installation)

## <a id='overview'>Overview</a>

These locks provide a similar interface to those in the threading and multiprocessing modules with a different set of tradeoffs.
These locks are useable by multiple different processes when those processes agree on a naming scheme.
This can be used in order to allow multiple processes running on the same machine to semi-coordinate or in the case of the redis or dynamo backed locks multiple processes running on different machines to coordinate work.
This provides a different type of coordination than multiple workers consuming from a single queue and can allow quickly prototyping a solution where workers attempt to grab a job and take a lock on it, grabbing another job if they fail at getting the lock.
One benefit of this type of solution is that it allows running on spot hardware in the cloud since if a single job is dropped before it is completed the lock will soon expire and another worker will be able to grab that same piece of work.

## <a id='examples'>Examples</a>

### SocketLock

```python
# todo
```

### FileLock

```python
# todo
```

### RedisLock

```python
# todo
```

### DynamoLock

```python
# todo
```

## <a id='installation'>Installation</a>

### From PyPI

```python
# todo
```

### From GitHub

```
python -m pip install --upgrade git+https://git@github.com/jbylund/locking.git
```
