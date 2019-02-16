import json
import logging
from urllib.request import urlopen, Request, HTTPError, URLError
from hashlib import md5
from functools import wraps

EVENT = None
CONTEXT = None
REGISTRY = {}


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def lambda_handler(event, context):
    """Lambda's entry point"""
    global EVENT, CONTEXT
    # allow access to event and context vars from decorators
    EVENT = event
    CONTEXT = context

    request_type = event['RequestType']
    resource_type = event['ResourceType']
    logger.info(f'Received request type "{request_type}" for resource type "{resource_type}"')
    logger.debug(f'Full request: {json.dumps(event)}')

    # default physical resource id to fallback to
    gen_phy_id = md5hash(event['StackId'], event['LogicalResourceId'])
    response = {
        'Status': 'SUCCESS',
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'StackId': event['StackId'],
        'PhysicalResourceId': event.get('PhysicalResourceId', gen_phy_id)
    }

    logger.debug('Registry: %s', REGISTRY)

    try:
        # try to get the resource handler and any additional resource arguments (NoEcho)
        if resource_type in REGISTRY:
            fn, kwargs = REGISTRY[resource_type].get(request_type)
        # if not found, try to fallback to default
        elif 'default' in REGISTRY:
            logger.debug(f'Resource type {resource_type} not in Registry. Using default')
            fn, kwargs = REGISTRY['default'].get(request_type)
        else:
            logger.error(f'No handlers for {request_type} request of {resource_type} type')
            raise ResourceError(f'No handlers for {request_type} request of {resource_type} type')

        response.update(**kwargs)

        # execute handlers
        # TODO: handle incorrect function outputs
        # TODO: add timeout
        logger.info(f'Dispatching function "{fn.__name__}" from "{fn.__module__}"')
        if request_type == 'Create' or request_type == 'Update':
            phy_id, data = fn(event, context)
            if phy_id is not None:
                response.update({'PhysicalResourceId': phy_id})
            if data is not None:
                response.update({'Data': data})
        elif request_type == 'Delete':
            fn(event, context)
    # ResourceError should be raised by handlers to signal error
    except ResourceError as e:
        logger.exception('Failure: ResourceError raised')
        response.update({'Status': 'FAILED', 'Reason': str(e)})
    # general exception handling to avoid custom resource timeout
    except Exception as e:
        logger.exception('Failure: Unexpected exception')
        response.update({
            'Status': 'FAILED',
            'Reason': f'Unexpected {type(e).__name__} exception. Check logs for traceback'
            })
    finally:
        return send_response(event['ResponseURL'], response)


def send_response(url, response):
    """
    send json response back to url
    """
    logger.info(f'Sending callback to {url}')
    data = json.dumps(response)
    encoded_data = data.encode('utf-8')
    logger.debug(f'Callback body: {data}')

    req = Request(
        url,
        data=encoded_data,
        method='PUT',
        headers={
            'Content-Length': len(encoded_data),
            # leaving content-type empty seem to be the desired thing to do as shown in the example:
            # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-cfnresponsemodule
            'Content-Type': ''
        }
    )

    try:
        urlopen(req)
        logger.info('Callback sent successfully')
    except HTTPError as e:
        logger.error(f'Callback failed: {e.code} {e.reason}')
    except URLError as e:
        logger.error(f'Callback failed: {e.reason}')


# decorators

def create(rtype='default', no_echo=False):
    def decorator(f):
        logger.debug(f'register CREATE func {f.__name__} to type {rtype}')

        @wraps
        def wrapper():
            f(EVENT)

        REGISTRY.setdefault(rtype, {})
        REGISTRY[rtype].update({'Create': (f, {'NoEcho': no_echo})})
        return wrapper
    return decorator


def update(rtype='default', no_echo=False):
    def decorator(f):
        logger.debug(f'register UPDATE func {f.__name__} to type {rtype}')

        @wraps
        def wrapper():
            f(EVENT)

        REGISTRY.setdefault(rtype, {})
        REGISTRY[rtype].update({'Update': (f, {'NoEcho': no_echo})})
        return wrapper
    return decorator


def delete(rtype='default'):
    def decorator(f):
        logger.debug(f'register DELETE func {f.__name__} to type {rtype}')

        @wraps
        def wrapper():
            f(EVENT)

        REGISTRY.setdefault(rtype, {})
        REGISTRY[rtype].update({'Delete': (f, {})})
        return wrapper
    return decorator


class ResourceError(Exception):
    pass


def md5hash(arg1, arg2):
    return md5(arg1.encode() + arg2.encode()).hexdigest()
