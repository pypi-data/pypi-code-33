import logging

logger = logging.getLogger(__name__)

def exists(context):
    return False

def deploy(context):
    resource = context.v1.resource

def endpoint(context):
    endpoint = {
        'url': '42.42.42.42',
        'user': 'scotty',
        'password': '***********',
    }
    return endpoint

def clean(context):
    pass
