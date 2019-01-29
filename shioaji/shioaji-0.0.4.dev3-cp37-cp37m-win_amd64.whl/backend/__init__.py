from shioaji.backend.http import HttpApi
try:
    from shioaji.backend.socket import Wrapper
except:
    Wrapper = None


def get_backends():
    apis = {
        'http': HttpApi,
        'socket': Wrapper,
    }
    return apis
