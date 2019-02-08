import inspect
from aiohttp.web_request import Request, BaseRequest

def find_request():
    """
    Finds the aiohttp post processed request object from the stack
    """
    request = None
    frames = inspect.stack()
    for frame in [frames[i].frame for i in range(len(frames)-1, 0, -1)]:
        if ('request' in frame.f_locals.keys()
                and type(frame.f_locals.get('request')) == Request
                and type(frame.f_locals.get('request')) != BaseRequest
           ):
            request = frame.f_locals.get('request')
            break
    return request
