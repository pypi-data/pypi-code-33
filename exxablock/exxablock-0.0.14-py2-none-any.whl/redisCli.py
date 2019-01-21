from common import *


resSuffix = {
    'timeseries': 'ts',
    'event': 'evt',
    'minute': 'min'
}

class RedisCli(object):
    host = None
    port = None
    cli = None

    def __init__(self, host='localhost', port=None):
        self.host = host
        self.port = port

    def connect(self, host=None, port=None):
        if host != None:
            self.host = host
        if port != None:
            self.port = port            
        self.cli = redis.Redis(self.host, self.port, db=0) # redis.StrictRedis(self.host, self.port, db=0)
        return self.cli

    def keys(self):
        if self.cli == None:
            raise ValueError('Not connected to server. run connect() first')
        return self.cli.keys()

    def count(self, key):
        if self.cli == None:
            raise ValueError('Not connected to server. run connect() first')
        return self.cli.zcard(key)

    def head(self, key, n, withTimestamp=True):
        if self.cli == None:
            raise ValueError('Not connected to server. run connect() first')
        return self.cli.zrange(key, 0, n, withscores=withTimestamp)

    def tail(self, key, n, withTimestamp=True):
        if self.cli == None:
            raise ValueError('Not connected to server. run connect() first')
        return self.cli.zrevrange(key, 0, n, withscores=withTimestamp)

    def minTime(self, key, start=0):
        if self.cli == None:
            raise ValueError('Not connected to server. run connect() first')
        if isinstance(key, list):
            pipe = self.cli.pipeline()
            for nm in key:
                pipe.zrange(nm, start, start, withscores=True)
            return min([row[0][1] for row in pipe.execute()])
        else:
            return self.cli.zrange(key, start, start, withscores=True)[0][1]

    def maxTime(self, key, end=-1):
        if self.cli == None:
            raise ValueError('Not connected to server. run connect() first')
        if isinstance(key, list):
            pipe = self.cli.pipeline()
            for nm in key:
                pipe.zrange(nm, end, end, withscores=True)
            return max([row[0][1] for row in pipe.execute()])
        else:
            return self.cli.zrange(key, end, end, withscores=True)[0][1]

    def timeRange2Offsets(self, res, start='-Inf', end='+Inf'):
        # tsfmt = '%Y-%m-%d %H:%M' if res == 'minute' else '%Y-%m-%d %H:%M:%S.%f'
        tsfmt = '%Y-%m-%d %H:%M' if res == 'minute' else '%Y-%m-%d %H:%M:%S.%f'
        if start == '-Inf':
            utcstart = start
        elif isinstance(start, str):
            ts = datetime.strptime(start, tsfmt).replace(tzinfo=tz.tzlocal())
            utcstart = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
            # utcstart = utcstart + int(ts.utcoffset().total_seconds())*1000
        elif isinstance(start, pd.Timestamp):
            stime = start.strftime(tsfmt)
            ts = datetime.strptime(stime, tsfmt).replace(tzinfo=tz.tzlocal())
            utcstart = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
            # utcstart = utcstart + int(ts.utcoffset().total_seconds())*1000
        elif isinstance(start, datetime):
            utcstart = int(start.strftime('%s'))*1000 + start.microsecond/1000
        elif isinstance(start, float) or isinstance(start, int):
            utcstart = start
        else:
            raise Exception('unsupported data format for ' + start)
        #
        if end == '+Inf':
            utcend = end
        elif isinstance(end, str):
            ts = datetime.strptime(end, tsfmt).replace(tzinfo=tz.tzlocal())
            utcend = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
            # utcend = utcend + int(ts.utcoffset().total_seconds())*1000
        elif isinstance(end, pd.Timestamp):
            etime = end.strftime(tsfmt)
            ts = datetime.strptime(etime, tsfmt).replace(tzinfo=tz.tzlocal())
            utcend = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
            # utcend = utcend + int(ts.utcoffset().total_seconds())*1000
        elif isinstance(end, datetime):
            utcend = int(end.strftime('%s'))*1000 + end.microsecond/1000
        elif isinstance(start, float) or isinstance(start, int):
            utcend = end
        else:
            raise Exception('unsupported data format for ' + end)
        return utcstart, utcend

if __name__ == '__main__':
    cli = RedisCli('localhost', 15376) 
    cli.connect()
    keys = cli.keys()
    print 'available keys : ', keys
    for ky in keys:
        print '\t' + ky + ' :: ' + \
            ' nrows: ' + str(cli.count(ky)) + \
            ', minTime:' + str(cli.minTime(ky)) + \
            ', maxTime:' + str(cli.maxTime(ky))
