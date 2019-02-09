from threading import Thread
import socket

IPv4_IP = socket.gethostbyname(socket.gethostname())

class Connection:
    def __init__(self, conn, addr):
        self.conn = conn
        self.host = addr[0]
        self.port = addr[1]

class Conns:
    def __init__(self):
        self.by_index = []
        self.by_port = {}
        self.by_conn = {}

class TCP:
    def __init__(self, host:str='localhost', port:int=8080, QueueSize:int=10):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_at = f'{host}:{port}'
        self.connections = Conns()
        self.host = host
        self.port = port
        self.onDataDict = {}
        self.onDataMain = None
        self.onConnection = None
        self.onDisconnect = None
        self.QueueSize = QueueSize
        self.type = None
        self.StopHandler = False
    
    def Err(self, _error:str, _exception:str):
        raise(f'Intonet: {_error}\nException: {_exception}')

    def Server(self):
        self.type = 'server'
        try:
            self.sock.bind((self.host, self.port))
        except Exception as e:
            self.Err(f'Can\'t bind a server at {self.conn_at}', e)
        
        while True:
            self.sock.listen(self.QueueSize)
            self.lastConn, self.lastAddr = self.sock.accept()
            self.connections.by_index.append(Connection(self.lastConn, self.lastAddr))
            self.connections.by_port[self.lastAddr[1]] = Connection(self.lastConn, self.lastAddr)
            self.connections.by_conn[self.lastConn] = Connection(self.lastConn, self.lastAddr)
            if self.onConnection != None:
                self.onConnection(self.lastConn)
    
    def Client(self, handler=None, onStartup=None):
        self.type = 'client'
        try:
            self.sock.connect((self.host, self.port))
        except Exception as e:
            self.Err(f'Can\'t connect to a server at {self.conn_at}', e)
        if onStartup:
            onStartup()
        if handler:
            while True:
                if not self.StopHandler:
                    handler()
                else:
                    break
    
    def GetData(self, conn=None, buffer:int=1024):
        if self.type == 'server':
            if conn != None:
                return conn.recv(buffer).decode('utf-8')
            else:
                self.Err('Conn argument is None', None)
        elif self.type == 'client':
            return self.sock.recv(buffer).decode('utf-8')
        else:
            self.Err('Can\'t send data because TCP type is not setted yet (server/client)', None)
    
    def onData(self, func, value:str=None):
        if value != None:
            self.onDataDict[value] = func
        else:
            self.onDataMain = func

    def send(self, data:str, conn=None, DataType:str='string'):
        if self.type == 'server':
            if DataType == 'string':
                conn.send(data.encode('utf-8'))
            elif DataType == 'bytes':
                conn.send(data)
            else:
                self.Err(f'"{DataType}" is invalid DataType', None)
        elif self.type == 'client':
            if DataType == 'string':
                self.sock.send(data.encode('utf-8'))
            elif DataType == 'bytes':
                self.sock.send(data)
            else:
                self.Err(f'"{DataType}" is invalid DataType', None)
        else:
            self.Err('Can\'t send data because TCP type is not setted yet (server/client)', None)
    
    def sendToAll(self, data:str, DataType:str='string'):
        for x in self.connections.by_conn:
            self.send(data, conn=x)

    def close(self):
        self.sock.close()
    
    def FuncBasicConnectionHandler(self, conn):
        while True:
            if not self.StopHandler:
                try:
                    data = self.GetData(conn)
                except:
                    if self.onDisconnect != None:
                        self.onDisconnect(conn)
                    break
                if data:
                    if data in self.onDataDict:
                        self.onDataDict[data](conn)
                    elif self.onDataMain != None:
                        self.onDataMain(conn, data)
            else:
                break
    
    def BasicConnectionHandler(self, conn):
        Thread(target=self.FuncBasicConnectionHandler, args=(conn,)).start()

    def ConnectionHandler(self, conn, func):
        Thread(target=func, args=(conn,)).start()
    
    def Handler(self, func):
        Thread(target=func).start()