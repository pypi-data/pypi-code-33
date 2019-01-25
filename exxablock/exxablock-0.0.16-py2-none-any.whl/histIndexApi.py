from common import *


class HistIndexApi  (object):

    def __init__(self, url = 'http://localhost:13456'):
        if url != None:
            self.apiUrl = url

    def convert2UTC(self, res, lts):
        uts = -inf
        tsfmt = '%Y-%m-%d %H:%M:%S' if res == 'minute' else '%Y-%m-%d %H:%M:%S.%f'
        if isinstance(lts, str):
            ts = datetime.strptime(lts, tsfmt).replace(tzinfo=tz.tzlocal())
            uts = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
        elif isinstance(lts, pd.Timestamp):
            stime = lts.strftime(tsfmt)
            ts = datetime.strptime(stime, tsfmt).replace(tzinfo=tz.tzlocal())
            uts = int(ts.strftime('%s'))*1000 + ts.microsecond/1000
        elif isinstance(lts, datetime):
            uts = int(lts.strftime('%s'))*1000 + lts.microsecond/1000
        elif isinstance(lts, float) or isinstance(lts, int):
            uts = lts
        else:
            raise Exception('unsupported data format for ' + lts)
        return uts


    def getIndex(self, cls, res, start=-inf, end=+inf, verbose=False):
        uri = self.apiUrl + '/api/hist/idx?name=' + cls + '&res=' + res
        #
        if start != -inf:
            uri += '&from=' + \
                (start if start in ['today', 'yesterday']
                 else str(self.convert2UTC(res, start)))
        if end != +inf:
            uri += '&to=' + \
                (end if end in ['today', 'tomorrow']
                 else str(self.convert2UTC(res, end)))
        #
        if verbose:
            print(uri)
        #
        jstr = urllib2.urlopen(uri).read()
        j = json.loads(jstr)
        df = pd.DataFrame({'timestamp': [int(x) for x in j['timestamp']], 'idx': [
                          float(x) for x in j['idx']]})
        df = df[['timestamp', 'idx']]
        df['timestamp'] = df['timestamp'].astype(np.int64)
        df['idx'] = df['idx'].astype(np.float64) - df['timestamp']
        df['idx'] = df['idx'].apply(lambda x: round(x, 4))
        df['timestamp'] = [datetime.fromtimestamp(
            x/1000) + timedelta(milliseconds=x % 1000) for x in df['timestamp']]
        return df

    def getIndexAll(self, res, start=-inf, end=+inf, verbose=False):
        uri = self.apiUrl + '/api/hist/idx?name=' + 'idxall' + '&res=' + res
        #
        if start != -inf:
            uri += '&from=' + \
                (start if start in ['today', 'yesterday']
                 else str(self.convert2UTC(res, start)))
        if end != +inf:
            uri += '&to=' + \
                (end if end in ['today', 'tomorrow']
                 else str(self.convert2UTC(res, end)))
        #
        if verbose:
            print(uri)
        #
        jstr = urllib2.urlopen(uri).read()
        jdic = json.loads(jstr)
        jrtn = {}
        for e in jdic:
            df =  pd.DataFrame(jdic[e])
            df = df[['timestamp', 'idx']]
            df['timestamp'] = df['timestamp'].astype(np.int64)
            df['idx'] = df['idx'].astype(np.float64) - df['timestamp']
            df['idx'] = df['idx'].apply(lambda x: round(x, 4))
            df['timestamp'] = [datetime.fromtimestamp(x/1000) + timedelta(milliseconds=x % 1000) for x in df['timestamp']]
            jrtn[e] = df
        return jrtn


    def getIndexByTimeRange(self, cls, res, start=-inf, end=+inf, verbose=False):
        uri = self.apiUrl + '/api/hist/idx?name=' + cls + '&res=' + res
        #
        if start != -inf:
            uri += '&from=' + \
                (start if start in ['today', 'yesterday']
                 else str(self.convert2UTC(res, start)))
        if end != +inf:
            uri += '&to=' + \
                (end if end in ['today', 'tomorrow']
                 else str(self.convert2UTC(res, end)))
        #
        if verbose:
            print(uri)
        #
        jstr = urllib2.urlopen(uri).read()
        j = json.loads(jstr)
        df = pd.DataFrame({'timestamp': [int(x) for x in j['timestamp']], 'idx': [
                          float(x) for x in j['idx']]})
        df = df[['timestamp', 'idx']]
        df['timestamp'] = df['timestamp'].astype(np.int64)
        df['idx'] = df['idx'].astype(np.float64) - df['timestamp']
        df['idx'] = df['idx'].apply(lambda x: round(x, 4))
        df['timestamp'] = [datetime.fromtimestamp(
            x/1000) + timedelta(milliseconds=x % 1000) for x in df['timestamp']]
        return df

    def plotIndexes(self, clss, res, start=-inf, end=+inf, width=14, height=16, verbose=False):
        dfs = [self.getIndex(cls, res, start, end, verbose) for cls in clss]
        #
        mntime = min([df['timestamp'][0] for df in dfs])
        mxtime = max([df['timestamp'][df.shape[0]-1] for df in dfs])
        #
        if verbose:
            print(uri)
        #
        fig = plt.figure(figsize=(width, height))
        nplot = len(clss)
        #

        #
        gs = gridspec.GridSpec(nplot, 1)
        for r in range(nplot):
            ax = fig.add_subplot(gs[r])
            ax.set_title(
                res + ': Cryptocurrency Market Indexes (' + clss[r] + ')', fontsize='20')
            idx = dfs[r]
            ax.plot(idx['timestamp'], idx['idx'], '--bo')
            ax.set_xlim([mntime, mxtime])
            ax.set_xlabel('Timestamp')
            ax.set_ylabel('Index')
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            ax.grid()
        gs.tight_layout(fig)

    def plotIndexOverlay(self, clss, res, start=-inf, end=+inf, show_markers=True, verbose=False):
        dfs = [self.getIndex(cls, res, start, end, verbose) for cls in clss]
        #
        mntime = min([df['timestamp'][0] for df in dfs])
        mxtime = max([df['timestamp'][df.shape[0]-1] for df in dfs])
        #
        hplt = host_subplot(111, axes_class=AA.Axes)
        plt.subplots_adjust(right=2, top=2)
        #
        hplt.set_xlim([mntime, mxtime])

        hplt.set_xlabel('Timestamp')
        hplt.set_ylabel('Index (' + clss[0] + ')')
        #
        p, = hplt.plot(dfs[0]['timestamp'], dfs[0]['idx'],
                       color=colors[0], marker=markers[0] if show_markers else '', linestyle=linestyles[0],
                       label=clss[0])
        #
        hplt.axis["left"].label.set_color(p.get_color())
        #
        offset = -60
        for ix, nm in enumerate(clss[1:]):
            par = hplt.twinx()
            offset += 60
            new_fixed_axis = par.get_grid_helper().new_fixed_axis
            par.axis["right"] = new_fixed_axis(
                loc="right", axes=par, offset=(offset, 0))
            par.axis["right"].toggle(all=True)
            par.get_yaxis().get_major_formatter().set_useOffset(False)
            par.set_ylabel('Index (' + nm + ')')
            ii = ix + 1
            p, = par.plot(dfs[ii]['timestamp'], dfs[ii]['idx'],
                          color=colors[ii % ncol], marker=markers[ii % nmrk] if show_markers else '', linestyle=linestyles[ii % nlst],
                          label=nm)
            par.axis["right"].label.set_color(p.get_color())
        #
        hplt.legend()
        #
        plt.title(res + ': Cryptocurrency Market Indexes (Overlayed)')
        plt.grid()
        plt.draw()
        plt.show()

    def plotIndexTsEvtBarOverlay(self, cls, start=-inf, end=+inf, show_markers=True, width=14, height=10, verbose=False):
        res = ['timeseries', 'event', 'minute']
        linestyles = [':', '-.', '']
        mkrsizes = [10, 14, 18]
        nmsz = len(mkrsizes)
        #
        dfs = [self.getIndex(cls, r, start, end, verbose) for r in res]
        #
        mntime = min([df['timestamp'][0] for df in dfs])
        mxtime = max([df['timestamp'][df.shape[0]-1] for df in dfs])
        #
        evtratio = dfs[1].shape[0]/float(dfs[0].shape[0])
        #
        fig = plt.figure(figsize=(width, height))
        gs = gridspec.GridSpec(1, 1)
        ax = fig.add_subplot(gs[0])
        ax.set_title(cls + ' : Timeseries vs. Events vs. Bars (' +
                     str(100*evtratio) + '%)', fontsize='20')
        ax.set_xlim([mntime, mxtime])
        for ii in range(len(dfs)):
            ax.plot(dfs[ii]['timestamp'], dfs[ii]['idx'], color=colors[ii % ncol],
                    marker=markers[ii % nmrk], markersize=mkrsizes[ii % nmsz], linestyle=linestyles[ii % nmsz], label=res[ii] + ' (' + str(dfs[ii].shape[0]) + ')')
        # , borderpad=2) # loc='upper center', bbox_to_anchor=(0.5, -0.05),  shadow=True, ncol=2)
        lgnd = ax.legend(fontsize=20)
        for ii in range(len(dfs)):
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
    hcli = HistIndexApi()
    # print hcli.getIndex('idxmktcap', 'timeseries', verbose=True)
    print hcli.getIndex('idxmktcap', 'event',  verbose=True)
    print hcli.getIndex('idxmktcap', 'minute', verbose=True)
