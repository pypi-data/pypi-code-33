from redisCli import *

defaultRtAnalyticCon = {
    'host': 'localhost',
    'port': 15386
}

defaultHistAnalyticCon = {
    'host': 'localhost',
    'port': 15387
}

class AnalyticCli  (RedisCli):
    # analytic classes
    anlClass = ['A1', 'B1', 'C1', 'C2', 'C3', 'D1']

    anlAlias = {
        'A1': 'anlrtns',
        'B1': 'anlcmnt',
        'C1': 'anlcolm',
        'C2': 'anlcovm',
        'C3': 'anlcorm',
        'D1': 'anlatr',
    }

    cols = {
        'A1': ['timestamp', 'symbol', 'rtn', 'crtn'],
        'B1': ['timestamp', 'symbol', 'mean', 'var', 'skew', 'kurt'],
        'C1': 'symbols',
        'C2': 'symbols',
        'C3': 'symbols'
    }

    def __init__(self, host, port):
        super(AnalyticCli, self).__init__(host, port)

    def connect(self, host=None, port=None):
        return super(AnalyticCli, self).connect(host, port)

    def analytics(self, res):
        rsfx = resSuffix[res]
        return [k[:k.rfind(rsfx)] for k in super(AnalyticCli, self).keys() if k.endswith(rsfx)]

    def count(self, cls, res):
        anlytc = self.anlAlias[cls] if cls in self.anlClass else cls
        return super(AnalyticCli, self).count(anlytc + resSuffix[res])

    def head(self, cls, res, n, withTimestamp=True):
        anlytc = self.anlAlias[cls] if cls in self.anlClass else cls
        return super(AnalyticCli, self).head(cls + resSuffix[res], n, withTimestamp)

    def tail(self, cls, res, n, withTimestamp=True):
        anlytc = self.NLAlias[cls] if cls in self.anlClass else cls
        return super(AnalyticCli, self).tail(anlytc + resSuffix[res], n, withTimestamp)

    def minTime(self, cls, res, start=0):
        rsfx = resSuffix[res]
        if isinstance(cls, list):
            anlytc = [(self.anlAlias[nm] if nm in self.anlClass else nm)
                      for nm in cls]
            anlts = map(lambda k: k + rsfx, anlytc)
        else:
            anlts = (self.anlAlias[cls]
                     if cls in self.anlClass else cls) + rsfx
        return datetime.fromtimestamp(super(AnalyticCli, self).minTime(anlts, start)/1000)

    def maxTime(self, cls, res, end=-1):
        rsfx = resSuffix[res]
        if isinstance(cls, list):
            anlytc = [(self.anlAlias[nm] if nm in self.anlClass else nm)
                      for nm in cls]
            anlts = map(lambda k: k + rsfx, anlytc)
        else:
            anlts = (self.anlAlias[cls]
                     if cls in self.anlClass else cls) + rsfx
        return datetime.fromtimestamp(super(AnalyticCli, self).maxTime(anlts, end)/1000)

    def getAnalytic(self, cls, res, sym='all', n=0, bres=0):
        if bres != 0 and (not bres in barRes):
            print 'Unsupported bar resolution:', bres
            print 'Please choose one of ', barRes
            return
        #
        st = 0
        ed = -1  # all range if n == 0
        if n > 0:
            ed = int(math.ceil(n / 100.0)) if sym == 'all' else n - 1
            if bres != 0:
                ed *= int(bres/15000)
        elif n < 0:
            st = -int(math.ceil(abs(n) / 100.0)) if sym == 'all' else n
            if bres != 0:
                st *= int(bres/15000)
        #
        prd = self.anlAlias[cls] if cls in self.anlClass else cls
        tsdata = self.cli.zrange(prd + resSuffix[res], st, ed, withscores=True)
        rdf = None
        if cls in ['A1', 'B1']:
            for ts in tsdata:
                cobj = cbor.loads(ts[0])
                val = cobj['value']
                df = pd.DataFrame(val)
                lts = pd.to_datetime(cobj['timestamp'], unit='ms')
                df['timestamp'] = lts
                rdf = df if rdf is None else rdf.append(df, sort=False)
            rdf = rdf[self.cols[cls]]  # column reordering
            # symbol filtering
            rdf = rdf if sym == 'all' else rdf.loc[rdf['symbol'] == sym]
            if n != 0:  # range filtering
                rdf = rdf.tail(abs(n)) if n < 0 else rdf.head(n)
            rdf.index = range(rdf.shape[0])
        elif cls in ['C1', 'C2', 'C3']:
            for ts in tsdata:
                cobj = cbor.loads(ts[0])
                val = cobj['value']
                syms = val['symbol']
                mtrx = val['mtrx']
                df = pd.DataFrame(mtrx)
                df.columns = syms
                lts = pd.to_datetime(cobj['timestamp'], unit='ms')
                df['timestamp'] = lts
                df['symbol'] = syms
                cols = ['timestamp', 'symbol'] + syms
                df = df[cols]  # column reordering
                # symbol filtering
                if sym != 'all':   # return vectors
                    df = df.loc[df['symbol'] == sym]
                rdf = df if rdf is None else rdf.append(df, sort=False)
            if n != 0:  # range filtering
                rdf = rdf.tail(abs(n)) if n < 0 else rdf.head(n)
            rdf.index = range(rdf.shape[0])
        elif cls in ['D1']:
            for ts in tsdata:
                cobj = cbor.loads(ts[0])
                val = cobj['value']
                if bres == 0:
                    for r in sorted([int(v) for v in val.keys()]):
                        rvec = val[str(r)]
                        df = pd.DataFrame(rvec)
                        if sym != 'all': # symbol filtering
                            df = df.loc[df['symbol'] == sym]
                        df['window'] = r
                        df = df[['window', 'btimestamp', 'symbol', 'tr', 'atr', 'close']]
                        rdf = df if rdf is None else rdf.append(df, sort=False)
                else:
                    rvec = val[str(bres)]
                    df = pd.DataFrame(rvec)
                    if sym != 'all': # symbol filtering
                        df = df.loc[df['symbol'] == sym]
                    df['window'] = bres
                    df = df[['window', 'btimestamp', 'symbol', 'tr', 'atr', 'close']]
                    rdf = df if rdf is None else rdf.append(df, sort=False)
            # group by 'window', 'btimestamp' and 'symbol'
            rdf = rdf.groupby(['window', 'symbol', 'btimestamp'], sort=False).last().reset_index()
            if n != 0:  # range filtering
                rdf = rdf.tail(abs(n)) if n < 0 else rdf.head(n)
            # convert numbers to timestamps
            rdf['btimestamp'] = pd.to_datetime(rdf['btimestamp'], unit='ms')
            # put row indices
            rdf.index = range(rdf.shape[0])
        else:
            print 'unknown class ', cls
            return
        #
        return rdf

    def getAnalyticByTimeRange(self, cls, res, sym='all', start='-Inf', end='+Inf', bres=0):
        if bres != 0 and (not bres in barRes):
            print 'Unsupported bar resolution:', bres
            print 'Please choose one of ', barRes
            return
        #
        utcstart, utcend = self.timeRange2Offsets(res, start, end)
        tsdata = self.cli.zrangebyscore(self.anlAlias[cls] + resSuffix[res], utcstart, utcend, withscores=True)
        #
        rdf = None
        if cls in ['A1', 'B1']:
            for ts in tsdata:
                cobj = cbor.loads(ts[0])
                rtns = cobj['value']
                df = pd.DataFrame(rtns)
                lts = pd.to_datetime(cobj['timestamp'], unit='ms')
                df['timestamp'] = lts
                rdf = df if rdf is None else rdf.append(df)
            rdf = rdf[self.cols[cls]]  # column reordering
            # symbol filtering
            rdf = rdf if sym == 'all' else rdf.loc[rdf['symbol'] == sym]
            rdf.index = range(rdf.shape[0])
        elif cls in ['C1', 'C2', 'C3']:
            for ts in tsdata:
                cobj = cbor.loads(ts[0])
                val = cobj['value']
                syms = val['symbol']
                mtrx = val['mtrx']
                df = pd.DataFrame(mtrx)
                df.columns = syms
                lts = pd.to_datetime(cobj['timestamp'], unit='ms')
                df['timestamp'] = lts
                df['symbol'] = syms
                cols = ['timestamp', 'symbol'] + syms
                df = df[cols]  # column reordering
                # symbol filtering
                if sym != 'all':   # return vectors
                    df = df.loc[df['symbol'] == sym]
                rdf = df if rdf is None else rdf.append(df, sort=False)
            rdf.index = range(rdf.shape[0])
        elif cls in ['D1']:
            for ts in tsdata:
                cobj = cbor.loads(ts[0])
                val = cobj['value']
                if bres == 0:
                    for r in sorted([int(v) for v in val.keys()]):
                        rvec = val[str(r)]
                        df = pd.DataFrame(rvec)
                        if sym != 'all': # symbol filtering
                            df = df.loc[df['symbol'] == sym]
                        df['window'] = r
                        df = df[['window', 'btimestamp', 'symbol', 'tr', 'atr', 'close']]
                        rdf = df if rdf is None else rdf.append(df, sort=False)
                else:
                    rvec = val[str(bres)]
                    df = pd.DataFrame(rvec)
                    if sym != 'all': # symbol filtering
                        df = df.loc[df['symbol'] == sym]
                    df['window'] = bres
                    df = df[['window', 'btimestamp', 'symbol', 'tr', 'atr', 'close']]
                    rdf = df if rdf is None else rdf.append(df, sort=False)
            # group by 'window', 'btimestamp' and 'symbol'
            rdf = rdf.groupby(['window', 'symbol', 'btimestamp'], sort=False).last().reset_index()
            # convert numbers to timestamps
            rdf['btimestamp'] = pd.to_datetime(rdf['btimestamp'], unit='ms')
            # put row indices
            rdf.index = range(rdf.shape[0])
        else:
            print 'unknown class ', cls
            return
        #
        return rdf

    def plotAnalyticTsEvtBarOverlay(self, cls, sym, col, start='-Inf', end='+Inf', show_markers=True, width=14, height=10):
        linestyles = [':', '-.', '']
        mkrsizes = [10, 14, 18]
        nmsz = len(mkrsizes)
        #
        anlRanges = [self.getAnalyticByTimeRange(cls, r, sym, start, end) for r in res]
        evtratio = anlRanges[1].shape[0]/float(anlRanges[0].shape[0])
        #
        fig = plt.figure(figsize=(width, height))
        gs = gridspec.GridSpec(1, 1)
        ax = fig.add_subplot(gs[0])
        #
        title = 'ECA-100:' + cls if cls in self.anlClass else cls
        ax.set_title(title + ' : ' + sym + ' : Timeseries vs. Events vs. Bars (' +
                     str(100*evtratio) + '%)', fontsize='20')
        #ax.set_xlim([start, end])
        #
        for ii in range(len(anlRanges)):
            ax.plot(anlRanges[ii]['timestamp'], anlRanges[ii][col],
                    marker=markers[ii % nmrk], markersize=mkrsizes[ii % nmsz], linestyle=linestyles[ii % nmsz], label=res[ii] + ' (' + str(anlRanges[ii].shape[0]) + ')')
        # , borderpad=2) # loc='upper center', bbox_to_anchor=(0.5, -0.05),  shadow=True, ncol=2)
        lgnd = ax.legend(fontsize=20)
        for ii in range(len(anlRanges)):
            lgnd.legendHandles[ii]._legmarker.set_markersize(14)
        ax.set_xlabel('Timestamp')
        ax.set_ylabel(col)
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.grid()
        #
        gs.tight_layout(fig)


if __name__ == '__main__':
    cli = AnalyticCli('localhost', 15386)
    cli.connect()
    #
    print 'available analytics: ', cli.analytics('timeseries')
    for res in resSuffix.keys():
        print 'A1 :: ', res, ' :: cnt ==> ', cli.count('A1', res)
    #
    print "cli.anlClass::", cli.anlClass
    print "cli.anlAlias::", cli.anlAlias
    #
    print "cli.count('A1', 'timeseries')::", cli.count('A1', 'timeseries')
    print "cli.count('anlrtns', 'timeseries')::", cli.count('anlrtns', 'timeseries')

    #
    for cls in ['A1', 'B1', 'C1', 'C2', 'C3']:
        #print "cli.getAnalytic('" + cls + "', 'event', 'ETH', -5)\n", cli.getAnalytic('cls, event', 'ETH', -5)
        #print "cli.getAnalytic('" + cls + "', 'event', 'all', -5)\n", cli.getAnalytic('cls, event', 'all', -5)
        #print "cli.getAnalytic('" + cls + "', 'event', 'all', -5)\n", cli.getAnalytic('cls, event', 'all', -5)
        #print "cli.getAnalytic('" + cls + "', 'event', 'BTC', -5)\n", cli.getAnalytic('cls, event', 'BTC', -5)
        print "cli.getAnalyticByTimeRange(" + cls + ", 'event', " + "'all', 3)\n", cli.getAnalyticByTimeRange(
            cls, 'event', 'all', 3)
        print "cli.getAnalyticByTimeRange(" + cls + ", 'event', " + "'all', -3)\n", cli.getAnalyticByTimeRange(
            cls, 'event', 'all', -3)
        print "cli.getAnalyticByTimeRange(" + cls + ", 'event', " + "'ETH', 3)\n", cli.getAnalyticByTimeRange(
            cls, 'event', 'ETH', 3)
        print "cli.getAnalyticByTimeRange(" + cls + ", 'event', " + "'ETH', -3)\n", cli.getAnalyticByTimeRange(
            cls, 'event', 'ETH', -3)