from getpass import getuser
from os import environ, getpid
import functools

import boto3


def get_on_ci():
    return "semaphore" == getuser()

def get_boto3_client(service):
    return _get_boto3_client(getpid(), service)

@functools.lru_cache()
def _get_boto3_client(pid, service):
    env_var_name = f"{service.upper()}_PORT"
    env_port = environ.get(env_var_name)
    if env_port:
        return boto3.client(
            service,
            endpoint_url=f"http://localhost:{env_port}",
            region_name="us-east-1",
            verify=False,
        )
    if get_on_ci():
        raise AssertionError(f"Cannot talk to real services as {getuser()}!")
    return boto3.client(service, region_name="us-east-1")
