from indexCli import *


class HistIndexCli  (IndexCli):

    def __init__(self, host, port):
        super(HistIndexCli, self).__init__(host, port)


if __name__ == '__main__':
    cli = HistIndexCli('localhost', 15377)
    cli.connect()
    for res in ['timeseries', 'event', 'minute']:
        print '######', res, '######'
        print 'available indices: ', cli.indices(res)
        print 'nrows: ', cli.count('idxmktcap', res)
    #
    print cli.getIndex('idxmktcap', 'minute')
    #
    print cli.minTime(['idxmktcap', 'idxprice'], 'timeseries')
    print cli.maxTime('idxmktcap', 'timeseries')
    #
    print 'getIndexByTimeRange\n', cli.getIndexByTimeRange('idxmktcap', 'minute')
    print 'getIndexByTimeRange\n', cli.getIndexByTimeRange('idxmktcap', 'minute', 
            cli.minTime('idxmktcap', 'timeseries'),
            cli.minTime('idxmktcap', 'timeseries') + timedelta(minutes=5), True)
