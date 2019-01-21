from socketIO_client_nexus import SocketIO, BaseNamespace
import sys

#
# Analytic classes
# A - - price and price returns:
# * price, return, cumulative return
# B - - moments:
# * mean, var, skew, and kurtosis
#  C - - similarity matrix measures:
# * colinear, covariance, and correlation matrices
# D - - intraday volatility estimation:
# * Average True Range(ATR), Parkinson(PK), Garman-Klass(GK), and Rogers-Satchell(RS)
anlClass = ['A1', 'B1', 'C1', 'C2', 'C3', 'D1']

anlAlias = {
    'A1': 'anlrtns',
    'B1': 'anlcmnt',
    'C1': 'anlcolm',
    'C2': 'anlcovm',
    'C3': 'anlcorm',
    'D1': 'anlatr',   
}

alias2Class = {
    'anlrtns' : 'A1',
    'anlcmnt' : 'B1',
    'anlcolm' : 'C1',
    'anlcovm' : 'C2',
    'anlcorm' : 'C3',
    'anlatr'  : 'D1',
}

resSuffix = {
    'timeseries': 'ts',
    'event': 'evt',
    'minute': 'min'
}


class AnalyticBaseNamespace(BaseNamespace):
    def __init__(self, io, path):
        super(AnalyticBaseNamespace, self).__init__(io, path)


# define Socket.io channel handler class
class AnalyticNamespace(AnalyticBaseNamespace):
    def on_admin(self, *args):  # administration news channel
        print('on_admin :: ' + ''.join(args))

    def on_update(self, *args):  # analytic value push channel
        print('on_update :: ' + ''.join(args))

    def on_reconnect(self):
        print('on_reconnect')

    def on_disconnect(self):
        print('on_disconnect')


class RealtimeAnalyticFeed(object):
    host = None
    port = None
    socketIO = None
    anlChnl = None

    def __init__(self, host='analytic-rt.exxablock.io', port=80):
        self.host = host
        self.port = port
        #print ('connecting ExxaBlock Socket.io server at ' + host + ':' + str(port))
        #self.socketIO = SocketIO(host, port)
        #print ('connected to ExxaBlock Socket.io server')

    def connect(self, cls, res, handler=AnalyticNamespace):
        self.socketIO = SocketIO(self.host, self.port)
        #
        if not res in resSuffix.keys():
            raise Exception('unknown data resolution :' + res)
        #
        if not cls in anlClass:
            if not cls in anlAlias.values():
                raise Exception('unknown analytic name :' + cls)
            else:
                schnl = '/' + cls + resSuffix[res]
        else:
            schnl = '/' + anlAlias[cls] + resSuffix[res]
        #
        self.anlChnl = self.socketIO.define(handler, schnl)
        print ('connected to an analytic channel ' + schnl)

    def disconnect(self, path=''):
        self.socketIO.disconnect(path)

    def wait(self, **kw):
        self.socketIO.wait(kw)


if __name__ == '__main__':
    rtfeed = RealtimeAnalyticFeed('localhost', '23456')
    rtfeed.connect('anlrtns', 'timeseries')
    rtfeed.wait()
    #

    class AltAnalyticNamespace(BaseNamespace):
        msgcnt = 1

        def on_admin(self, *args):  # administration news channel
            print('on_admin  :: ' + ''.join(args))

        def on_update(self, *args):  # analytic value push channel
            print('on_update :: ' + str(self.msgcnt) + ' :: ' + ''.join(args))
            self.msgcnt += 1

        def on_reconnect(self):
            print('on_reconnect')

        def on_disconnect(self):
            print('on_disconnect')

    rtfeed.connect('anlrtns', 'timeseries', AltAnalyticNamespace)
    rtfeed.wait()
