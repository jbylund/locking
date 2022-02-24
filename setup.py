from distutils.core import setup

setup(
    name="locking",
    version="1.1.2",
    packages=[
        "locking",
        "locking.filelock",
        "locking.redislock",
        "locking.socketlock",
        "locking.dynamolock",
    ],
)
