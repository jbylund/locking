from getpass import getuser
from os import environ

import boto3

def get_on_ci():
    return "semaphore" == getuser()

def get_boto3_client(service):
    env_var_name = "{}_PORT".format(service.upper())
    env_port = environ.get(env_var_name)
    if env_port:
        return boto3.client(service, endpoint_url="http://localhost:{}".format(env_port))
    return boto3.client(service, region_name='us-east-1')
