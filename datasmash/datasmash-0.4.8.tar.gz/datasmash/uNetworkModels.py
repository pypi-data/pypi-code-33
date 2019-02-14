import numpy as np
import pandas as pd
import random
import json


class uNetworkModels:
    """
    Utilities for storing and manipulating XPFSA models
    inferred by XGenESeSS
    @author zed.uchicago.edu
    Attributes:
        jsonFile (string): path to json file containing models
    """

    def __init__(self,
                 jsonFILE):
        with open(jsonFILE) as data_file:
            self._models = json.load(data_file)


    @property
    def models(self):
         return self._models

    @property
    def df(self):
         return self._df


    def append(self,pydict):
        """
        append models
        @author zed.uchicago.edu
        """
        self._models.update(pydict)


    def select(self,var="gamma",n=None,
               reverse=False, store=None,
               high=None,low=None,equal=None,inplace=False):
        """
        Utilities for storing and manipulating XPFSA models
        inferred by XGenESeSS
        @author zed.uchicago.edu
        Selects the N top models as ranked by var specified value
        (in reverse order if reverse is True)
        Inputs -
            var (string): model parameter to rank by
            n (int): number of models to return
            reverse (boolean): return in ascending order (True)
                or descending (False) order
            store (string): name of file to store selection json
            high (float): higher cutoff
            low (float): lower cutoff
            inplace (bool): update models if true
        Output -
            (dictionary): top n models as ranked by var
                         in ascending/descending order
        """

        #assert var in self._models.keys(), "Error: Model parameter specified not valid"
        if equal is not None:
            out={key:value
                 for (key,value) in self._models.items() if value[var]==equal }
        else:
            this_dict={value[var]:key
                       for (key,value) in self._models.items() }

            if low is not None:
                this_dict={key:this_dict[key] for key in this_dict.keys() if key >= low }
            if high is not None:
                this_dict={key:this_dict[key] for key in this_dict.keys() if key <= high }

            if n is None:
                n=len(this_dict)
            if n > len(this_dict):
                n=len(this_dict)

            out = {this_dict[k]:self._models[this_dict[k]]
                   for k in sorted(this_dict.keys(),
                                   reverse=reverse)[0:n]}
        if dict:
            if inplace:
                self._models=out
            if store is not None:
                with open(store, 'w') as outfile:
                    json.dump(out, outfile)
        else:
            warnings.warn("Selection creates empty model dict")

        return out


    def setVarname(self):
        """
        Utilities for storing and manipulating XPFSA models
        inferred by XGenESeSS
        @author zed.uchicago.edu
        Extracts the varname for src and tgt of
        each model and stores under src_var and tgt_var
        keys of each model;
        No I/O
        """

        VARNAME='var'
        f=lambda x: x[-1] if len(x)%2==1  else VARNAME

        for key,value in self._models.items():
            self._models[key]['src_var']=f(value['src'].replace('#',' ').split())
            self._models[key]['tgt_var']=f(value['tgt'].replace('#',' ').split())

        return


    def augmentDistance(self):
        """
        Utilities for storing and manipulating XPFSA models
        inferred by XGenESeSS
        @author zed.uchicago.edu
        Calculates the distance between all models and stores
        them under the
        distance key of each model;
        No I/O
        """

        f=lambda x: x[:-1] if len(x)%2==1  else x

        for key,value in self._models.items():
            src=[float(i) for i in f(value['src'].replace('#',' ').split())]
            tgt=[float(i) for i in f(value['tgt'].replace('#',' ').split())]

            dist = haversine((np.mean(src[0:2]),np.mean(src[2:])),
                           (np.mean(tgt[0:2]),np.mean(tgt[2:])),
                           miles=True)
            self._models[key]['distance'] = dist

        return


    def to_json(self,outFile):
        """
        Utilities for storing and manipulating XPFSA models
        inferred by XGenESeSS
        @author zed.uchicago.edu
        Writes out updated models json to file
        Input -
            outFile (string): name of outfile to write json to
        Output -
            No output
        """

        with open(outFile, 'w') as outfile:
            json.dump(self._models, outfile)

        return


    def setDataFrame(self,scatter=None):
        """
        Generate dataframe representation of models
        @author zed.uchicago.edu
        Input -
            scatter (string) : prefix of filename to plot 3X3 regression
            matrix between delay, distance and coefficiecient of causality
        Output -
            Pandas.DataFrame with columns
            ['latsrc','lonsrc','lattgt',
             'lontgtt','gamma','delay','distance']
        """

        latsrc=[]
        lonsrc=[]
        lattgt=[]
        lontgt=[]
        gamma=[]
        delay=[]
        distance=[]
        src_var=[]
        tgt_var=[]

        NUM=None
        f=lambda x: x[:-1] if len(x)%2==1  else x

        for key,value in self._models.items():
            src=[float(i) for i in f(value['src'].replace('#',' ').split())]
            tgt=[float(i) for i in f(value['tgt'].replace('#',' ').split())]
            if NUM is None:
                NUM=len(src)/2
            latsrc.append(np.mean(src[0:NUM]))
            lonsrc.append(np.mean(src[NUM:]))
            lattgt.append(np.mean(tgt[0:NUM]))
            lontgt.append(np.mean(tgt[NUM:]))
            gamma.append(value['gamma'])
            delay.append(value['delay'])
            distance.append(value['distance'])
            src_var.append(value['src_var'])
            tgt_var.append(value['tgt_var'])

        self._df = pd.DataFrame({'latsrc':latsrc,
                                 'lonsrc':lonsrc,
                                 'lattgt':lattgt,
                                 'lontgt':lontgt,
                                 'gamma':gamma,
                                 'delay':delay,
                                 'distance':distance,
                                 'src':src_var,
                                 'tgt':tgt_var})

        if scatter is not None:
            sns.set_style('darkgrid')
            fig=plt.figure(figsize=(12,12))
            fig.subplots_adjust(hspace=0.25)
            fig.subplots_adjust(wspace=.25)
            ax = plt.subplot2grid((3,3), (0,0), colspan=1,rowspan=1)
            sns.distplot(self._df.gamma,ax=ax,kde=True,color='#9b59b6');
            ax = plt.subplot2grid((3,3), (0,1), colspan=1,rowspan=1)
            sns.regplot(ax=ax,x="gamma", y="distance", data=self._df);
            ax = plt.subplot2grid((3,3), (0,2), colspan=1,rowspan=1)
            sns.regplot(ax=ax,x="gamma", y="delay", data=self._df);

            ax = plt.subplot2grid((3,3), (1,0), colspan=1,rowspan=1)
            sns.regplot(ax=ax,x="distance", y="gamma", data=self._df);
            ax = plt.subplot2grid((3,3), (1,1), colspan=1,rowspan=1)
            sns.distplot(self._df.distance,ax=ax,kde=True,color='#9b59b6');
            ax = plt.subplot2grid((3,3), (1,2), colspan=1,rowspan=1)
            sns.regplot(ax=ax,x="distance", y="delay", data=self._df);

            ax = plt.subplot2grid((3,3), (2,0), colspan=1,rowspan=1)
            sns.regplot(ax=ax,x="delay", y="gamma", data=self._df);
            ax = plt.subplot2grid((3,3), (2,1), colspan=1,rowspan=1)
            sns.regplot(ax=ax,x="delay", y="distance", data=self._df);
            ax = plt.subplot2grid((3,3), (2,2), colspan=1,rowspan=1)
            sns.distplot(self._df.delay,ax=ax,kde=True,color='#9b59b6');

            plt.savefig(scatter+'.pdf',dpi=300,bbox_inches='tight',transparent=False)


        return self._df


    def iNet(self,init=0):
        """
        Utilities for storing and manipulating XPFSA models
        inferred by XGenESeSS
        @author zed.uchicago.edu
        Calculates the distance between all models and stores
        them under the
        distance key of each model;
        No I/O
        """

        pass


def to_json(pydict,outFile):
    """
        Writes dictionary json to file
        @author zed.uchicago.edu
        Input -
            pydict (dict): ditionary to store
            outFile (string): name of outfile to write json to
        Output -
            No output
    """

    with open(outFile, 'w') as outfile:
        json.dump(pydict, outfile)

    return
