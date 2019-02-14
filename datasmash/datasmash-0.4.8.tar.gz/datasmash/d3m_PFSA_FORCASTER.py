import os, sys
from typing import Dict, Union, Optional
from d3m.container.numpy import ndarray
import pandas as pd
import numpy as np
import subprocess
from d3m.metadata import hyperparams, params
import d3m.metadata.base as metadata_module
from d3m import utils
from datasmash import cylog
from sklearn import linear_model
from d3m.primitive_interfaces.unsupervised_learning import UnsupervisedLearnerPrimitiveBase
from d3m.primitive_interfaces.base import CallResult, DockerContainer
from d3m.types import Data
from datasmash.config import CWD, BIN_PATH
from d3m.container import dataset, numpy
import json
from d3m.container import dataset, numpy
from d3m.metadata import hyperparams, params, base
from datasmash._version import __version__
from d3m.primitive_interfaces.unsupervised_learning import UnsupervisedLearnerPrimitiveBase

# These are just regular Python variables so that we can easily change all types
# at once in the future, if needed. Otherwise, one could simply inline all these.
Inputs = dataset.Dataset
Outputs = numpy.ndarray

# A named tuple for parameters.
# Specifying types for all parameters is important so that one can do end-to-end
# training from outside. For example, some parameters might have gradients so we
# can use those to optimize them end-to-end.


class Params(params.Params):
    quantizer_params: Optional[dict]

class Hyperparams(hyperparams.Hyperparams):
    pass

class PFSA_FORCASTER(UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """

    """

    __author__ = "UChicago"
    metadata = base.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.d3m_XG1",
        "primitive_family": "TIME_SERIES_FORECASTING",
        "python_path": "d3m.primitives.datasmash.PFSA_FORCASTER",
        "source": {
        	'name': 'UChicago',
			'contact': 'mailto:virotaru@uchicago.edu'
		},
        "version": __version__,
        "id": "e79460bd-17f9-47bf-ae3d-5503c268c07e",
        "description": "This time series forecasting primitive quantises the data, compute the pfsa of quantized data,  forcasts the quantized time series and maps the quantized forcast to the original range",
        'installation': [
            {'type': base.PrimitiveInstallationType.PIP,
             'package': 'datasmash',
             'version': __version__
            }
        ],
        "keywords": [
            'time',
            'series',
            'data smashing',
            'data-smashing',
            'data_smashing',
            'datasmashing',
            'forecasting',
            'parameter-free',
            'hyperparameter-free'
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed)


        assert os.path.isfile(os.path.join(BIN_PATH, 'XgenESeSS')), "invalid bin path."
        self._training_inputs = None
        self._fitted = False
        self._partitions = False
        self._OPTIMIZE = 1
        self._ROCTGT = 1
        self._DATAFILE = './temp_forcaster/data.dat' # to create in set train
        self._NAME_PATH = './temp_forcaster/name.dat' # to create in set train
        self._DATA_PATH = './temp_forcaster/' # to create in set train
        self._LOG_PATH = './temp_forcaster/_log.log'
        self._MODEL_PATH = './temp_forcaster/'
        self._BEG = 0#hyperparam?
        self._END = 0#hyperparam?
        self._NUM = 5#hyperparam?
        self._PARTITION_= None # to compute in train
        self._XgenESeSS = os.path.join(BIN_PATH, 'XgenESeSS_FOR')
        self._cynet = os.path.join(BIN_PATH, 'cynet')
        self._RUNLEN = 0
        self._FITLEN = 0
        self._FLEXWIDTH = 0
        self._DERIVATIVE = 1
        self._ROCTGT = 1 #hyperparam?
        self._OPTIMIZE = 1
        self._TARGET = 0       
        self._path = 'temp_forcaster'         
        self._data = None
        self._number_quantizations = 15
        self._target_index = []
        self._target_numbers = []
        self._columns_names = []
        self._target_names = []       

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:  # type: ignore
        print('Datasmash version:',__version__)
        if not os.path.exists(self._path):
            os.mkdir(self._path)
        allFoldersInDir=os.listdir(inputs)
        if len([a for a in allFoldersInDir if a.find('problem') != -1])!=0 and \
            len([a for a in allFoldersInDir if a.find('dataset') != -1])!=0:
            allFoldersInDir=os.listdir(inputs)
            dataSetPath=inputs
            problemFolderName=[a for a in allFoldersInDir if a.find('problem') != -1][0]
            datasetFolderName=[a for a in allFoldersInDir if a.find('dataset') != -1][0]
            data=os.path.join(dataSetPath, datasetFolderName, 'datasetDoc.json')
            problem=os.path.join(dataSetPath, problemFolderName, 'problemDoc.json')
        with open(data) as f:
            data1 = json.load(f)
        with open(problem) as f:
            problem_json = json.load(f)
        split_file = os.path.join(dataSetPath, problemFolderName, problem_json["inputs"]["dataSplits"]["splitsFile"])
        data_split = pd.read_csv(split_file)
        train_vs_test = data_split.groupby('type').count()
        self._FITLEN = (train_vs_test['d3mIndex'].loc['TRAIN'])-1
        self._END = int(self._FITLEN*0.1)
        for target in problem_json["inputs"]["data"][0]["targets"]:
            self._target_index.append(target['colIndex'])
            self._target_names.append(target['colName'])
        text1 = open(self._DATAFILE, "w") 
        text_file = open(self._NAME_PATH, "w")
        a = os.path.join(inputs, datasetFolderName, data1['dataResources'][0]['resPath'])
        df = pd.read_csv(a)
        symbols = set()
        variable_counter = 0
        print("                 ",self._target_index)
        for column in data1['dataResources'][0]['columns']:
            if 'index' not in column['role'] and "timeIndicator" not in column['role']:
                if column['colName'] in self._target_index:
                    self._target_numbers.append(variable_counter)
                self._columns_names.append(str(column['colName']))                
                name = column['colName'] + '.dat'  
                text_file.write(name+'\n') 
                b=df[column['colName']]
                symbols.update(b)
                towrite = ' '.join([str(i) for i in list(b)])+'\n'
                with open('./temp_forcaster/' + name, "w") as text2:
                    text2.write(towrite)
                text1.write(towrite)
                variable_counter = variable_counter + 1
        text1.close()
        text_file.close()
        diff = df[self._target_names[0]].diff()
        self._partitions = list(np.linspace(diff.mean() + diff.std(), diff.mean() - diff.std(), self._number_quantizations))    
        return None
                
    def fit(self, *, timeout: float = None, iterations: int = None, outputs: Outputs) -> CallResult[None]:
        KEY=' : ' + str(int(self._target_index[0])-2)
        for i in range(len(self._partitions)):
            PARTITION = self._partitions[i]
            run_name='T_'+str(self._TARGET)+'P_'+str(PARTITION)[0:5]+'R_'+ str(0) 
            log_File = self._LOG_PATH[:self._LOG_PATH.rfind('.')] + run_name +self._LOG_PATH[self._LOG_PATH.rfind('.'):]
            xgstr=self._XgenESeSS+' -f '+self._DATAFILE+' -L '+str(self._FITLEN)+' -k "'+KEY+'" -B '+str(self._BEG)+' -E '+str(self._END)+' -n '+str(self._NUM)+' -p '+str(PARTITION)[0:5]+' -u '+str(self._DERIVATIVE)+' -S -m -g 0.01 -G 5000 -v 0 -w '+self._MODEL_PATH+run_name+' -N '+self._NAME_PATH 
            subprocess.call(xgstr,shell=True)

        return CallResult[None]

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        VERBOSE = False
        if not os.path.exists(self._path):
            os.mkdir(self._path)
        allFoldersInDir=os.listdir(inputs)
        if len([a for a in allFoldersInDir if a.find('problem') != -1])!=0 and \
            len([a for a in allFoldersInDir if a.find('dataset') != -1])!=0:
            allFoldersInDir=os.listdir(inputs)
            dataSetPath=inputs
            problemFolderName=[a for a in allFoldersInDir if a.find('problem') != -1][0]
            datasetFolderName=[a for a in allFoldersInDir if a.find('dataset') != -1][0]
            data=os.path.join(dataSetPath, datasetFolderName, 'datasetDoc.json')
            problem=os.path.join(dataSetPath, problemFolderName, 'problemDoc.json')
        with open(problem) as f:
            problem_json = json.load(f)
        split_file = os.path.join(dataSetPath, problemFolderName, problem_json["inputs"]["dataSplits"]["splitsFile"])
        data_split = pd.read_csv(split_file)
        train_vs_test = data_split.groupby('type').count()
        self._RUNLEN = (train_vs_test['d3mIndex'].loc['TEST']) + self._FITLEN
        cont_past = pd.DataFrame()
        cont_forcast = pd.DataFrame()
        results = pd.DataFrame()
        toPrint = pd.DataFrame()
        data = pd.DataFrame()
        file_Name = pd.read_csv(self._NAME_PATH, sep=" ", header = None)[0].loc[self._TARGET]
        data[self._TARGET] = (pd.read_csv(os.path.join(os.path.dirname(self._NAME_PATH),file_Name), sep=" ", header = None).T)[0]
        for i in range(len(self._partitions)):
            PARTITION = self._partitions[i]
            run_name='T_'+str(self._TARGET)+'P_'+str(PARTITION)[0:5]+'R_'+ str(0) 
            log_File = self._LOG_PATH[:self._LOG_PATH.rfind('.')] + run_name +self._LOG_PATH[self._LOG_PATH.rfind('.'):]
            cystr=self._cynet+' -J '+self._MODEL_PATH+run_name+'model.json'+' -T continuous -p '+str(PARTITION)[0:5]+' -N '+str(self._RUNLEN)+' -x '+str(self._RUNLEN)+' -l '+log_File+' -w '+self._DATA_PATH+' -U '+str(self._DERIVATIVE)
            print(cystr)
            subprocess.call(cystr,shell=True)
            if sum(1 for line in open(log_File) if len(line)>10)==0:
                print('__________________Empty log_File:',log_File)
                continue
            print('CALLED SUBPROCESS')
            df_log=pd.read_csv(log_File,skip_blank_lines=True, sep="\s+",header=None, names=['-','filename','count_','event','prob0','prob1'])
            EXV = 0
            for th in np.linspace( max(df_log['prob1'].mean()-3*df_log['prob1'].std(), 0), min(df_log['prob1'].mean()+3*df_log['prob1'].std(), 1) ,num=(6*df_log['prob1'].std()/0.1)*20+1):
                    W=cylog(FILE=log_File,
                               DATA_PATH=self._DATA_PATH,
                               TH=th,BEG=int(self._FITLEN/2),END=self._FITLEN,
                               PARTITION=str(PARTITION),
                               DERIVATIVE=self._DERIVATIVE,
                               TARGET=self._TARGET)
                    if EXV<W.exv:
                        EXV=W.exv
                        TH=th
                        
            W=cylog(FILE=log_File,
                           DATA_PATH=self._DATA_PATH,
                           TH=TH,BEG=self._FITLEN,END=self._RUNLEN,
                           PARTITION=str(PARTITION),
                           DERIVATIVE=self._DERIVATIVE,
                           TARGET=self._TARGET,
                           DEBAG=False)

            W.d2a()
            if True:
                cont_forcast[str(PARTITION)]=W.continuous_signal_pred
                past_data=(W.log_log_data['prob1'].loc[self._END-self._BEG+10:self._FITLEN]>W.TH).astype(int)
                if VERBOSE:
                    print("MAping dict is", W.partition_map)
                toAdd=[W.partition_map[i] for i in past_data]
                cont_past[str(PARTITION)] = toAdd
        clf = linear_model.LinearRegression()
        temp2=data[self._TARGET].astype(float).diff().loc[1:]
        clf.fit(cont_past, temp2.loc[self._END-self._BEG+10:self._FITLEN])
        _pred = clf.predict(cont_forcast)
        _pred[0]=_pred[0]+data[self._TARGET].loc[self._FITLEN]
        results[0]=_pred.cumsum()
        toPrint['actual']=data[self._TARGET][self._FITLEN:self._RUNLEN].reset_index(drop=True)
        return results.mean(axis=1)


    def get_params(self) -> Params:
        
        return Params(
                    quantizer_params=self.__dict__)


    def set_params(self, *, params: Params) -> None:
        self.__dict__ = params['quantizer_params']