from getpass import getuser
from os import environ

import boto3


def get_on_ci():
    return "semaphore" == getuser()


def get_boto3_client(service):
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
        raise AssertionError("You cannot talk to real services from ci!")
    return boto3.client(service, region_name="us-east-1")
