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
from sklearn import metrics

# These are just regular Python variables so that we can easily change all types
# at once in the future, if needed. Otherwise, one could simply inline all these.
Inputs = dataset.Dataset
Outputs = numpy.ndarray

# A named tuple for parameters.
# Specifying types for all parameters is important so that one can do end-to-end
# training from outside. For example, some parameters might have gradients so we
# can use those to optimize them end-to-end.


class Params(params.Params):
    pass


class Hyperparams(hyperparams.Hyperparams):
    pass

class PFSA_CATEGORICAL_FORCASTER(UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """

    """

    __author__ = "UChicago"
    metadata = base.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.d3m_PFSA_CATEGORICAL_FORECASTING",
        "primitive_family": "TIME_SERIES_FORECASTING",
        "python_path": "d3m.primitives.datasmash.PFSA_CATEGORICAL_FORCASTER",
        "source": {
        	'name': 'UChicago',
			'contact': 'mailto:virotaru@uchicago.edu'
		},
        "version": __version__,
        "id": "534c6167-9728-4a03-87aa-abec365931ee",
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
            'classification',
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
        self._END = 100#hyperparam?
        self._NUM = 2#hyperparam?
        self._PARTITION_= None # to compute in train
        self._XgenESeSS = os.path.join(BIN_PATH, 'XgenESeSS_cynet')
        self._cynet = os.path.join(BIN_PATH, 'cynet')
        self._flexroc = os.path.join(BIN_PATH, 'flexroc')
        self._RUNLEN = 0
        self._FITLEN = 0
        self._FLEXWIDTH = 0
        self._DERIVATIVE = 0
        self._ROCTGT = 1 #hyperparam?
        self._OPTIMIZE = 1     
        self._path = 'temp_forcaster'         
        self._data = None
        self._number_quantizations = 1
        self._target_names = []
        self._target_numbers = []
        self._partition = ''
        self._symbols_sorted = None
        self._columns_names = []
 
    def set_training_data(self, *, inputs: Inputs) -> None:  # type: ignore
        print('Datasmash version:',__version__)
        print('Hacky loader\n')
        stri = str(inputs)
        str_list = stri.split('\'')
        for stri in str_list:
            if stri.find('file:///')>=0:
                inputs = stri[8:]
        inputs =  os.path.dirname(os.path.dirname(os.path.abspath(inputs)))
        if not os.path.exists(self._path):
            os.mkdir(self._path)
        allFoldersInDir=os.listdir(inputs)
        print(allFoldersInDir)
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
        self._RUNLEN = (train_vs_test['repeat'].loc['TRAIN'])-1
        self._END = self._RUNLEN/10
        for target in problem_json["inputs"]["data"][0]["targets"]:
            self._target_names.append(target['colIndex'])
        text1 = open(self._DATAFILE, "w") 
        text_file = open(self._NAME_PATH, "w")
        a = os.path.join(inputs, datasetFolderName, data1['dataResources'][0]['resPath'])
        df = pd.read_csv(a)
        symbols = set()
        variable_counter = 0
        for column in data1['dataResources'][0]['columns']:
            if 'index' not in column['role'] and "timeIndicator" not in column['role']:
                if column['colName'] in self._target_names:
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
        self._symbols_sorted = sorted(list(symbols))
        for i in range(1,len(self._symbols_sorted)):
            if i != 1:
                self._partition = self._partition + ' '
            self._partition = self._partition + str((self._symbols_sorted[i-1] + self._symbols_sorted[i])/2)
        return None
                
    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        KEY=' : ' + str(int(self._target_names[0])-2)
        run_name='run' 
        log_File = self._LOG_PATH[:self._LOG_PATH.rfind('.')] + run_name +self._LOG_PATH[self._LOG_PATH.rfind('.'):]
        xgstr=self._XgenESeSS+' -f '+self._DATAFILE+ ' -k "' + KEY+ '" '+str(self._BEG)+' -E '+str(self._END)+ '-n 2 -N '+self._NAME_PATH + ' -T symbolic -m -G 10000 -v 0 -A .5 -q -w '+self._MODEL_PATH+run_name +' -l ' + log_File   
        subprocess.call(xgstr,shell=True)
        return CallResult[None]    
        
    def produce(self, *, inputs: Inputs, iterations: int = None) -> CallResult[Outputs]:
        inputs =  os.path.dirname(os.path.dirname(os.path.abspath(inputs)))
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
        print(data_split)
        train_vs_test = data_split.groupby('type').count()
        print(train_vs_test)
        self._FITLEN = (train_vs_test['repeat'].loc['TEST']) + self._RUNLEN
        self._END = self._RUNLEN/10
        run_name='run' 
        log_File = self._LOG_PATH[:self._LOG_PATH.rfind('.')] + run_name +self._LOG_PATH[self._LOG_PATH.rfind('.'):]
        cystr=self._cynet+' -J '+self._MODEL_PATH+run_name+'model.json'+' -T symbolic '+' -N '+str(self._FITLEN)+' -x '+str(self._FITLEN)+' -l '+log_File+' -w '+self._DATA_PATH+' -U '+str(self._DERIVATIVE)
        subprocess.call(cystr,shell=True)
        header_list = ['-','filename','count_','event']
        str_symbols_sorted = [str(i) for i in self._symbols_sorted]
        header_list.extend(str_symbols_sorted)
        df_log=pd.read_csv(log_File,skip_blank_lines=True, sep="\s+",header=None, names=header_list)
        thresolds = dict()
        df_log.set_index("count_", inplace = True)
        for i in range(len(self._symbols_sorted) - 1):
            df_log['tot_from_' + str(i)] = df_log[[str(i) for i in range(i,len(self._symbols_sorted))]].sum(axis=1)
            for j in range(i,i+1):    #len(self._symbols_sorted)):
                df_log['final_' + str(j)] = df_log[str(j)]/df_log['tot_from_' + str(i)]
                fpr, tpr, thresholds = metrics.roc_curve(df_log['event'], df_log['final_'+str(j)], pos_label=j)
                maxth = 0
                maxaccurasy = 0
                for k in range(len(fpr)):
                    acur = tpr[k]-(fpr[k])
                    if maxaccurasy < acur:
                        maxaccurasy = acur
                        maxth = thresholds[k]
            thresolds[i] = maxth
        prediction = []
        for i in range(self._RUNLEN+2, self._FITLEN+2):
            for j in range(len(self._symbols_sorted)):

                if j == len(self._symbols_sorted)-1:
                    prediction.append(self._symbols_sorted[j])
                elif df_log['final_' + str(j)].loc[i] > thresolds[j]:
                    prediction.append(self._symbols_sorted[j])
                    break

        toReturn = np.array(prediction)
        data_split[self._columns_names[0]] = toReturn
        data_split = data_split.set_index('d3mIndex')
        del data_split['type']	
        del data_split['repeat']
        del data_split['fold']                                   
        return CallResult(data_split)

    def get_params(self) -> Params:
        pass

    def set_params(self, *, params: Params) -> None:
        pass
