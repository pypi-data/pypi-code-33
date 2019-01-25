from redisCli import *
from numpy import inf

defaultRtIndexCon = {
    'host': 'localhost',
    'port': 15376
}

defaultHistIndexCon = {
    'host': 'localhost',
    'port': 15377
}

class IndexCli  (RedisCli):
    # index classes
    idxClass = [ 'A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'X1','X2', 'ZZ' ]
    # index alias/canonical names
    idxAlias = {
        'A1' : 'idxmktcap',
        'A2' : 'idxprice',
        'A3' : 'idxadjprice',
        'B1' : 'idxpricertn',
        'B2' : 'idxsupplyrtn',
        'B3' : 'idxvolumertn',
        'X1' : 'idxcompositemp',
        'X2' : 'idxcompositempv',
        'ZZ' : 'idxall'
    }

    def __init__(self, host, port):
        super(IndexCli, self).__init__(host, port)

    def connect(self, host=None, port=None):
        return super(IndexCli, self).connect(host, port)
        
    def indices(self, res):
        rsfx = resSuffix[res]
        return [k[:k.rfind(rsfx)] for k in super(IndexCli, self).keys() if k.endswith(rsfx)]

    def count(self, cls, res):
        index = self.idxAlias[cls] if cls in self.idxClass else cls
        return super(IndexCli, self).count(index + resSuffix[res])

    def head(self, cls, res, n, withTimestamp=True):
        index = self.idxAlias[cls] if cls in self.idxClass else cls
        return super(IndexCli, self).head(index + resSuffix[res], n, withTimestamp)

    def tail(self, cls, res, n, withTimestamp=True):
        index = self.idxAlias[cls] if cls in self.idxClass else cls
        return super(IndexCli, self).tail(index + resSuffix[res], n, withTimestamp)

    def minTime(self, cls, res, start=0):
        rsfx = resSuffix[res]
        if isinstance(cls, list):
            index = [(self.idxAlias[nm] if nm in self.idxClass else nm) for nm in cls]
            idxts = map(lambda k: k + rsfx, index)
        else:
            idxts = (self.idxAlias[cls] if cls in self.idxClass else cls) + rsfx
        return datetime.fromtimestamp(super(IndexCli, self).minTime(idxts, start)/1000)

    def maxTime(self, cls, res, end=-1):
        rsfx = resSuffix[res]
        if isinstance(cls, list):
            index = [(self.idxAlias[nm] if nm in self.idxClass else nm) for nm in cls]
            idxts = map(lambda k: k + rsfx, index)
        else:
            idxts = (self.idxAlias[cls] if cls in self.idxClass else cls) + rsfx
        return datetime.fromtimestamp(super(IndexCli, self).maxTime(idxts, end)/1000)

    def getIndex(self, cls, res, start=0, end=-1, verbose=False):
        index = self.idxAlias[cls] if cls in self.idxClass else cls
        rset = self.cli.zrange(
            index + resSuffix[res], start, end, withscores=True)
        if index.find('idxall') == 0:
            ts = np.int64(map(lambda r: r[1], rset))
            df = pd.DataFrame(map(lambda t: json.loads(t[0]), rset))
            for col in df.columns.values:
                df[col] = df[col] - ts
                df[col] = df[col].map(lambda r: round(r, 4))
            df['timestamp'] = ts
            cols = df.columns.tolist()
            df = df[cols[-1:] + cols[:-1]]
        else:
            df = pd.DataFrame(rset)
            df.columns = ['idx', 'timestamp']
            df = df[['timestamp', 'idx']]
            df['timestamp'] = np.int64(df['timestamp'])
            df['idx'] = df['idx'].astype(np.float64) - df['timestamp']
            df['idx'] = df['idx'].apply(lambda x: round(x, 4))
        df['timestamp'] = [datetime.fromtimestamp(
            x/1000) + timedelta(milliseconds=x % 1000) for x in df['timestamp']]
        return df

    def getIndexByTimeRange(self, cls, res, start=-inf, end=+inf, verbose=False):
        index = self.idxAlias[cls] if cls in self.idxClass else cls
        utcstart = '-Inf'
        #tsfmt = '%Y-%m-%d %H:%M' if res == 'minute' else '%Y-%m-%d %H:%M:%S.%f'
        tsfmt = '%Y-%m-%d %H:%M' if res == 'minute' else '%Y-%m-%d %H:%M:%S.%f'
        if isinstance(start, str):
            ts = datetime.strptime(
                start, tsfmt).replace(tzinfo=tz.tzlocal())
            utcstart = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
            # utcstart = utcstart + int(ts.utcoffset().total_seconds())*1000
        elif isinstance(start, pd.Timestamp):
            stime = start.strftime(tsfmt)
            ts = datetime.strptime(
                stime, tsfmt).replace(tzinfo=tz.tzlocal())
            utcstart = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
            # utcstart = utcstart + int(ts.utcoffset().total_seconds())*1000
        elif isinstance(start, datetime):
            utcstart = int(start.strftime('%s'))*1000 + start.microsecond/1000
        elif isinstance(start, float) or isinstance(start, int):
            utcstart = start
        else:
            raise Exception('unsupported data format for ' + start)
        #
        utcend = '+Inf'
        if isinstance(end, str):
            ts = datetime.strptime(
                end, tsfmt).replace(tzinfo=tz.tzlocal())
            utcend = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
            # utcend = utcend + int(ts.utcoffset().total_seconds())*1000
        elif isinstance(end, pd.Timestamp):
            etime = end.strftime(tsfmt)
            ts = datetime.strptime(
                etime, tsfmt).replace(tzinfo=tz.tzlocal())
            utcend = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
            # utcend = utcend + int(ts.utcoffset().total_seconds())*1000
        elif isinstance(end, datetime):
            utcend = int(end.strftime('%s'))*1000 + end.microsecond/1000
        elif isinstance(start, float) or isinstance(start, int):
            utcend = end
        else:
            raise Exception('unsupported data format for ' + end)
        #
        if verbose:
            print 'utcstart ==> ', utcstart
            print 'utcend   ==> ', utcend
        #
        df = pd.DataFrame(self.cli.zrangebyscore(
            index + resSuffix[res], utcstart, utcend, withscores=True))
        df.columns = ['idx', 'timestamp']
        df = df[['timestamp', 'idx']]
        df['timestamp'] = df['timestamp'].astype(np.int64)
        df['idx'] = df['idx'].astype(np.float64) - df['timestamp']
        df['idx'] = df['idx'].apply(lambda x: round(x, 4))
        df['timestamp'] = [datetime.fromtimestamp(
            x/1000) + timedelta(milliseconds=x % 1000) for x in df['timestamp']]
        return df

    def plotIndices(self, clss, res, start=0, end=-1, width=14, height=16, verbose=False):
        if not isinstance(clss, list):
            raise Exception('indices should be a list type')
        indices = [(self.idxAlias[nm] if nm in self.idxClass else nm) for nm in clss]
        #
        fig = plt.figure(figsize=(width, height))
        nplot = len(indices)
        #
        mntime = self.minTime(indices, res, start)
        mxtime = self.maxTime(indices, res, end)
        #
        gs = gridspec.GridSpec(nplot, 1)
        for r in range(nplot):
            ax = fig.add_subplot(gs[r])
            idx = self.getIndex(indices[r], res, start, end)
            title = 'ECI-100:' + clss[r] if clss[r] in self.idxClass else indices[r] 
            ax.set_title(
                res + ': Cryptocurrency Market Indices (' + title + ')', fontsize='20')
            ax.plot(idx['timestamp'], idx['idx'], '--bo')
            ax.set_xlim([mntime, mxtime])
            ax.set_xlabel('Timestamp')
            ax.set_ylabel('Index')
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            ax.grid()
        gs.tight_layout(fig)

    def plotIndicesByTimeRange(self, clss, res, start=-inf, end=+inf, width=14, height=16, verbose=False):
        if not isinstance(clss, list):
            raise Exception('indices should be a list type')
        indices = [(self.idxAlias[nm] if nm in self.idxClass else nm) for nm in clss]
        #
        fig = plt.figure(figsize=(width, height))
        nplot = len(indices)
        #
        mntime = self.minTime(indices, res, 0) if start == -inf else start
        mxtime = self.maxTime(indices, res, -1) if end == +inf else end
        #
        gs = gridspec.GridSpec(nplot, 1)
        for r in range(nplot):
            ax = fig.add_subplot(gs[r])
            idx = self.getIndexByTimeRange(indices[r], res, mntime, mxtime)
            title = 'ECI-100:' + clss[r] if clss[r] in self.idxClass else indices[r] 
            ax.set_title(
                res + ': Cryptocurrency Market Indices (' + title + ')', fontsize='20')
            ax.plot(idx['timestamp'], idx['idx'], '--bo')
            ax.set_xlim([mntime, mxtime])
            ax.set_xlabel('Timestamp')
            ax.set_ylabel('Index')
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            ax.grid()
        gs.tight_layout(fig)

    def plotIndexTimeRangeOverlay(self, clss, res, start=-inf, end=+inf, show_markers=True, verbose=False):
        if not isinstance(clss, list):
            raise Exception('indices should be a list type')
        indices = [(self.idxAlias[nm] if nm in self.idxClass else nm) for nm in clss]
        #
        idxRanges = [self.getIndexByTimeRange(idx, res, start, end, verbose) for idx in indices]
        #
        hplt = host_subplot(111, axes_class=AA.Axes)
        plt.subplots_adjust(right=2, top=2)
        #
        hplt.set_xlim([start, end])

        hplt.set_xlabel('Timestamp')
        hplt.set_ylabel('Index (' + indices[0] + ')')
        #
        p, = hplt.plot(idxRanges[0]['timestamp'], idxRanges[0]['idx'],
                       color=colors[0], marker=markers[0] if show_markers else '', linestyle=linestyles[0],
                       label=indices[0])
        #
        hplt.axis["left"].label.set_color(p.get_color())
        #
        offset = -60
        for ix, nm in enumerate(indices[1:]):
            par = hplt.twinx()
            offset += 60
            new_fixed_axis = par.get_grid_helper().new_fixed_axis
            par.axis["right"] = new_fixed_axis(
                loc="right", axes=par, offset=(offset, 0))
            par.axis["right"].toggle(all=True)
            par.get_yaxis().get_major_formatter().set_useOffset(False)
            par.set_ylabel('Index (' + nm + ')')
            ii = ix + 1
            p, = par.plot(idxRanges[ii]['timestamp'], idxRanges[ii]['idx'],
                          color=colors[ii % ncol], marker=markers[ii % nmrk] if show_markers else '', linestyle=linestyles[ii % nlst],
                          label=nm)
            par.axis["right"].label.set_color(p.get_color())
        #
        hplt.legend()
        #
        plt.title(res + ': Cryptocurrency Market Indices (Overlayed)')
        plt.grid()
        plt.draw()
        plt.show()

    def plotIndexTsEvtBarOverlay(self, cls, start=-inf, end=+inf, show_markers=True, width=14, height=10, verbose=False):
        res = ['timeseries', 'event', 'minute']
        linestyles = [':', '-.', '']
        mkrsizes = [10, 14, 18]
        nmsz = len(mkrsizes)

        idxRanges = [self.getIndexByTimeRange(cls, r, start, end, verbose) for r in res]
        evtratio = idxRanges[1].shape[0]/float(idxRanges[0].shape[0])
        #
        fig = plt.figure(figsize=(width, height))
        gs = gridspec.GridSpec(1, 1)
        ax = fig.add_subplot(gs[0])
        #
        title = 'ECI-100:' + cls if cls in self.idxClass else cls 
        ax.set_title(title + ' : Timeseries vs. Events vs. Bars (' + str(100*evtratio) + '%)', fontsize='20')
        ax.set_xlim([start, end])
        for ii in range(len(idxRanges)):
            ax.plot(idxRanges[ii]['timestamp'], idxRanges[ii]['idx'], color=colors[ii % ncol],
                    marker=markers[ii % nmrk], markersize=mkrsizes[ii % nmsz], linestyle=linestyles[ii % nmsz], label=res[ii] + ' (' + str(idxRanges[ii].shape[0]) + ')')
        # , borderpad=2) # loc='upper center', bbox_to_anchor=(0.5, -0.05),  shadow=True, ncol=2)
        lgnd = ax.legend(fontsize=20)
        for ii in range(len(idxRanges)):
            lgnd.legendHandles[ii]._legmarker.set_markersize(14)
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Index')
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.grid()
        #
        gs.tight_layout(fig)
    
    def level(self, df, col, binsz, op, verbose=True): 
        grp = df.groupby(pd.cut(df[col], np.arange(min(df[col]), max(df[col]), binsz)))
        if op == 'size':
            return grp.size()
        elif op == 'first':
            return grp.first()
        elif op == 'last':
            return grp.last()
        elif op == 'sum':
            return grp.sum()
        elif op == 'mean':
            return grp.agg({'idx':'mean'})
        else:
            raise ValueError('unsupported opertion : ' + op)


if __name__ == '__main__':
    cli = IndexCli('localhost', 15376)
    cli.connect()
    #
    print 'available indices: ', cli.indices('timeseries')
    for res in resSuffix.keys():
        print 'A1 :: ', res, ' :: cnt ==> ', cli.count('A1', res)
    #
    print "cli.idxClass::",cli.idxClass
    print "cli.idxAlias::", cli.idxAlias
    #
    print "cli.count('A1', 'timeseries')::", cli.count('A1', 'timeseries')
    print "cli.count('idxmktcap', 'timeseries')::", cli.count('idxmktcap', 'timeseries')
    #
    #print 'getIndexByTimeRange\n', cli.getIndexByTimeRange('A1', 'event')
    #print 'getIndexByTimeRange\n', cli.getIndexByTimeRange('idxmktcap', 'minute')
