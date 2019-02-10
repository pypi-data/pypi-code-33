import inspect
import types
import socket
import threading
import msgpack

class _ProvidedApi:
    def __init__(self, argSpec, fun):
        self.name = fun.__name__
        self.fun = fun
        self.args = argSpec.args
        self.varargs = argSpec.varargs
        self.varkw = argSpec.keywords
        self.defaults = argSpec.defaults

    def call(self, *args, **kw):
        return self.fun(*args, **kw)

class ServiceProvider:
    apis = {}
    def __init__(self, name):
        self.name = name
    
    def export(self, fun, name=None):
        if(type(fun) != types.FunctionType):
            raise TypeError('{!r} is not a function'.format(fun))
        if name == None:
            name = fun.__name__
        self.apis[name] = _ProvidedApi(inspect.getargspec(fun), fun)

    def _make_response(self, conn, request_id, success, result):
        if success:
            pass
            # print('INFO: success call')
        else:
            pass
            # print('ERROR: fail call')
        response = {
            "request_id": request_id,
            "success": success,
            "result": result
        }
        data = msgpack.packb(response)
        conn.send(len(data).to_bytes(8, byteorder="big"))
        conn.send(data)
        conn.close()

    def _process(self, conn):
        dataSize = int.from_bytes(conn.recv(8), byteorder='big')
        try:
            data = msgpack.unpackb(conn.recv(dataSize), raw=False, use_list=False)
            request_id = data.get("request_id", None)
            name = data.get("name", None)
            args = data.get("args", ())
            kw = data.get("kw", {})
            if request_id == None or name == None:
                raise Exception("Require \'name\' and \'request_id\'")
        except:
            # print('ERROR: Wrong request format')
            conn.close()
            return
        api = self.apis.get(name)
        if(api == None):
            self._make_response(conn, request_id, False, "{} not defined".format(name))
            return
        try:
            self._make_response(conn, request_id, True, api.call(*args, **kw))
        except Exception as e:
            self._make_response(conn, request_id, False, str(e))


    def _startRpc(self, ip, port):
        server = socket.socket()
        server.bind((ip, port))
        server.listen(5)
        while True:
            conn, addr = server.accept()
            # print("INFO: receive connection from {}".format(addr))
            threading.Thread(target=ServiceProvider._process, args=(self, conn)).start()


    def start(self, ip='localhost', port=8080):
        # print("INFO: server started at {}:{}".format(ip, port))
        threading.Thread(target=ServiceProvider._startRpc, args=(self, ip, port)).start()