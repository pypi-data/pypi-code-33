#!/usr/bin/python

import subprocess
import os
import sys
from scipy.stats import linregress
from sklearn.metrics import accuracy_score
from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import roc_curve
from sklearn import metrics
import pandas as pd
import numpy as np

"""
cynet output postprocess utilities
author: zed.uchicago.edu
year: 2018

"""

TODO="match qpred \
    + match sig beg to end \
    +"


__version__ = '0.3.14'


class cylog:
    """
    Inputs:

    FILE: output log from cynet
    DATA_PATH: path to file where target variable datafile is
    TH: threshold value
    PARTITION: partition used in analysis
    COLNUM: column number for positive class (start from zero prob pred col)
    BEG: out of sample start index for cynet log
    END: out of sample end index for cynet log
    DERIVATIVE: True if detrending is used in quantization

    Ouputs:


    """
    def __init__(self,
                 FILE,
                 DATA_PATH="./",
                 TH=None,
                 PARTITION=None,
                 COLNUM=1,
                 BEG=0,
                 END=-1,
                 DERIVATIVE=False,
                 DEQUANTIZER='MEAN',
                 TARGET=0,
                 DEBAG = False):
        
        self.TARGET=TARGET
        self.DEBAG = DEBAG
        self.FILE = FILE
        self.DATA_PATH = DATA_PATH
        self.TH = TH
        self.BEG = BEG
        self.END = END
        self.DERIVATIVE = DERIVATIVE
        self.DEQUANTIZER = DEQUANTIZER
        
        self.PARTITION = None
        if PARTITION is not None:
            self.PARTITION=[float(i) 
                            for i in PARTITION.split()]


        self.dfilename = None
        self.data = None
        self.event = None
        self.prob = None
        self.pred = None

        self.partition_map = None
        self.init_val = None

        self.slope = None
        self.intercept = None
        self.r_value = None
        self.p_value = None
        self.std_err = None
        self.historicprediction = None
        self.continuous_signal = None
        self.continuous_signal_pred = None        
        self.log_log_data =None
        self.shift= None
        self.fit()
        self.historicProb1=None

    def fit(self): 
        """
        read the output log from
        cynet
        """
        assert sum(1 for line in open(self.FILE))>1, "EMPTY CYLOG"
        df=pd.read_csv(self.FILE,skip_blank_lines=True,
                       sep="\s+",header=None,
                       names=['-','filename','count_','event','prob0','prob1'])
        df.set_index('count_', inplace=True)
        self.log_log_data = df
        self.dfilename=os.path.join(self.DATA_PATH,df.filename.values[0])
        #self.shift=int(df['count_'].iloc[0])
        #print(self.BEG-shift+1)
        #print(self.END-shift)
        self.event=pd.to_numeric(df['event'].loc[self.BEG+1:self.END])
        self.prob=pd.to_numeric(df['prob1'].loc[self.BEG+1:self.END])
        self.getQuantizedPredictions()
        self.getData()
        self.getPartitionDict()
        if (self.DEBAG):
            print('df is', df)
            print('beg         ',self.BEG)
            print('END         ',self.END)
            print('self.event',self.event)
            print('self.prob',self.prob)
        self.cevent=np.cumsum(self.event)
        self.cpred=np.cumsum(self.pred)
        self.quantized_results=pd.DataFrame.from_dict({'observed':self.cevent,'predicted':self.cpred})
        if (self.DEBAG):
            print('self.cevent',self.cevent)
            print('self.cpred',self.cpred)
        if(self.DERIVATIVE):
            self.exv = explained_variance_score(self.cevent,self.cpred)
            self.mse = mean_squared_error(self.cevent,self.cpred)
        else:
            self.exv = explained_variance_score(self.event,self.pred)
            self.mse = mean_squared_error(self.event,self.pred)


    def getQuantizedPredictions(self):
        """
        map to symbols from
        symbol prediction probability
        using threshold
        determined for a
        specific TPR/FPR pair
        """
        self.pred=(self.prob>self.TH).astype(int)
    def getData(self):
        """
        BEG is almost always at 0
        END is just before BEG in reading cynet log.
        Also must read the continuous observed
        signal for comparison
        """
        if os.path.exists(self.dfilename) and os.path.isfile(self.dfilename):
            arr = pd.read_csv(self.dfilename,sep="\s+",
                              header=None).transpose()
            self.data = arr.iloc[0:self.BEG]
            self.continuous_signal = arr.iloc[self.BEG:]
            self.init_val = arr.iloc[self.BEG].values[0]
           
    def getPartitionDict(self):
        """
        mapping parition to median
        continuous values
        BEG is almost always at 0
        END is just before BEG in reading cynet log.
        Also must read the continuous observed
        signal for comparison
        """
        if (self.DEQUANTIZER=='MEDIAN'):

            if self.DERIVATIVE:
                arr=self.data.diff().dropna()
                M=[arr[arr[0]<self.PARTITION[0]].median()]
            ind=0
            while ind < len(self.PARTITION)-1:
                M=np.append(M,arr[arr[0].between(self.PARTITION[ind],
                                                 self.PARTITION[ind+1])].median())
                ind=ind+1
                
            M=np.append(M,arr[arr[0]>self.PARTITION[-1]].mean())
        elif (self.DEQUANTIZER=='MEAN'):

            if self.DERIVATIVE:
                arr=self.data.diff().dropna()
                M=[arr[arr[0]<self.PARTITION[0]].mean()]
            ind=0
            while ind < len(self.PARTITION)-1:
                M=np.append(M,arr[arr[0].between(self.PARTITION[ind],
                                                 self.PARTITION[ind+1])].mean())
                ind=ind+1            
            M=np.append(M,arr[arr[0]>self.PARTITION[-1]].mean())
        self.partition_map=M

        
    def d2a(self):
        """
        map symbol stream 
        to continuous signal
        """
        self.continuous_signal_pred = [self.partition_map[i] for i in self.pred]
       # if self.DERIVATIVE:
           # self.continuous_signal_pred \
             #   = np.cumsum(self.continuous_signal_pred)+self.init_val

    def print_AUC(self):
        fpr, tpr, thresholds = roc_curve(self.event, self.prob)
        #fpr, tpr, thresholds = roc_curve(self.event, np.random.rand(150,1))

        precision, recall, thresholds1 = metrics.precision_recall_curve(self.event, self.prob)
        #print('thresholds is',thresholds1)
        #print('precision is',precision)
        print('auc',metrics.auc(fpr, tpr))
        top_20 =  sorted(sorted(range(len(list(self.prob))), key=lambda i: list(self.prob)[i])[-5:])
        #print('Top 20 by Pr value', top_20)
        #print(self.event[[x+self.BEG for x in top_20]])
     
    def getCorr(self):
        """
        get correlation between observed and predicted events
        """
        self.slope,self.intercept,self.r_value,self.p_value,self.std_err \
            = linregress(self.event,self.pred)
       
        
    def viz(self,LEN=None):
        """
        plot observed and predicted continuous signals
        """
        self.d2a()
        if LEN is None:
            LEN=len(self.continuous_signal_pred)+1
        sig=self.continuous_signal[0].values[1:LEN]

        #print len(sig[:-self.BEG]),len(self.continuous_signal_pred[self.BEG:LEN+self.BEG])
        return pd.DataFrame.from_dict({'obs':sig[:-self.BEG],
                                       'pred':self.continuous_signal_pred[self.BEG:LEN+self.BEG]})


    def print_summary(self,QPREDFILE='qpred.csv'):
        """
        summary of prediction
        """
        print("---- zCast summary ")

        print("correlation of obs vs quatized:",  self.r_value)
        print("p-value of obs vs quantized:   ",  self.p_value)
        print("accuracy obs vs quantized:     ",  self.acc)
        print("explained variance score:      ",  self.exv)
        print("mean squared error             ",  self.mse)
        print("correlation of integrated obs vs quantized:")
        print(self.quantized_results.corr())
        #pd.DataFrame.from_dict({'obs':self.event,'prd':self.pred}).to_csv(QPREDFILE,index=None,sep=" ")

