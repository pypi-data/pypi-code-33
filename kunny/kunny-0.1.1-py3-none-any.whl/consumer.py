import socket
import msgpack
import functools
import uuid

class ServiceConsumer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
    
    def require(self, funcName=None, providerName=None):
        def decorator(fun):
            if funcName == None:
                name = fun.__name__
            else:
                name = funcName
            @functools.wraps(fun)
            def wrapper(*args, **argkw):
                request = {
                    "request_id": uuid.uuid4().hex,
                    "name": name,
                    "args": args,
                    "kw": argkw                   
                }
                client = socket.socket()
                client.connect((self.ip, self.port))
                data = msgpack.packb(request)
                client.send(len(data).to_bytes(8, byteorder="big"))
                client.send(data)
                length = int.from_bytes(client.recv(8), byteorder="big")
                response = msgpack.unpackb(client.recv(length), raw=False, use_list=False)
                client.close()
                if response.get('success', False):
                    if 'result' in response:
                        return response.get('result')
                    else:
                        raise Exception('Did not receive result')
                raise Exception(response.get('result', 'Did not receive result'))
            return wrapper
        return decorator
