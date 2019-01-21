from indexCli import *


class IndexCache  (IndexCli):

    def __init__(self, host='localhost', port=15377, res='event'):
        super(IndexCache, self).__init__(host, port)


if __name__ == '__main__':
    host = 'localhost'
    cache = IndexCache(host, 15377)
    cache.connect()
    for res in ['timeseries', 'event', 'minute']:
        print '######', res, '######'
        print 'available indices: ', cache.indices(res)
        print 'nrows: ', cache.count('idxmktcap', res)
    #
    print "index::", cache.getIndex('idxmktcap', 'event')
    #
    print "minTime(['A1', 'A2'], 'timeseries')::", cache.minTime(['A1', 'A2'], 'timeseries')
    print "minTime(['idxmktcap', 'idxprice'], 'timeseries')::", cache.minTime(['idxmktcap', 'idxprice'], 'timeseries')
    print "maxTime(['A1', 'A2'], 'timeseries')::", cache.maxTime(['A1', 'A2'], 'timeseries')
    print "maxTime(['idxmktcap', 'idxprice'], 'timeseries')::", cache.maxTime(['idxmktcap', 'idxprice'], 'timeseries')
    #
    print "getIndexByTimeRange('A1', 'minute')::\n", cache.getIndexByTimeRange('A1', 'minute')
    print "getIndexByTimeRange('idxmktcap', 'minute')::\n", cache.getIndexByTimeRange('idxmktcap', 'minute')
    #print 'getIndexByTimeRange\n', cache.getIndexByTimeRange('idxmktcap', 'minute', 
    #        cache.minTime('idxmktcap', 'timeseries'),
    #        cache.minTime('idxmktcap', 'timeseries') + timedelta(minutes=5), True)
    #
