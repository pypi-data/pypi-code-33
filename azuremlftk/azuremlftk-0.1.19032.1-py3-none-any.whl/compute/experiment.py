"""
Script for executing Forecasting Toolkit experiments.
This script is a template that will be used by the
:class::`ftk.compute.aml_compute.AMLBatchAICompute` to be 
experiments to AML Batch AI compute backend.

The script accepts the following arguments.

`--data-folder`: File mount where data for the experiment is stored. 
                This can be an Azure blob store or a file store associated with the
                AML workspace.
`--experiment-name`: Name of the experiment. The data for any run of the script must be
                    available in the `{--data-folder}\{--experiment-name}` location.
`--compute`: Choice of backend - joblib, futures or daskdistributed. This is currently unused.
`--job-type`: Type of job. Choice of - fit, cvsearch, forecasterunion. The choice 
            determines the job type parameter passed to 
            :func::`ftk.compute.experiment.AzureBatchAIComputeE13N.execute_job`            
`--output-folder`: Name of the folder where outputs will be stored. Outputs for a run are stored in
                `{--data-folder}\{--experiment-name}\{--output-folder location}`

"""
#!/usr/bin/python
import argparse
import sys
import io
import os
import importlib
import multiprocessing as mp
import dill as pickle
from joblib import Parallel, delayed

# Conditional import of Python SDK. Compat-mode for old AML envs.
azureml_spec = importlib.util.find_spec("azureml.core")
if azureml_spec is not None:
    from azureml.core.run import Run

from ftk import TimeSeriesDataFrame, ForecastDataFrame
from ftk.factor_types import ComputeJobType
from ftk.verify import Messages
from ftk.exception import ComputeException

class AzureMLForecastE13NArgParser:
    """
    Argument parser class for parsing args passed in to the 
    experiment script.
    """
    _parser = None

    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description='Forecasting Toolkit Experimentation Script Parser')        

    def add_arguments(self):
        """
        Adds arguments to the ArgParser `_parser` instance
        The following arguments are supported currently.

        `--experiment-name`: Name of the experiment. 
        `--compute`: Choice of backend - joblib, futures or daskdistributed
        `--job-type`: Type of job. Choice of - fit, cvsearch, forecasterunion
        `--data-folder`: File mount where data for the experiment is stored.
        `--output-folder`: Name of the folder where outputs will be stored.

        """
        # Experiment name
        self._parser.add_argument('-e', '--experiment-name', 
                                type=str, 
                                dest='experiment_name', 
                                help="Name of the current experiment or run", 
                                required=True)
        # Compute backend
        compute_backends = ['joblib', 'futures', 'daskdistributed']
        self._parser.add_argument('-c','--compute', 
                                choices=compute_backends, 
                                help="Compute backend name", 
                                required=False)
        # Job type
        job_types = ['Fit', 'CVSearch', 'ForecasterUnion']
        self._parser.add_argument('-j','--job-type', 
                                choices=job_types, 
                                dest='job_type',
                                help="Type of job", 
                                required=True)
        # Data folder
        self._parser.add_argument('-d','--data-folder', 
                                type=str, 
                                dest='data_folder', 
                                help='Data folder mounting point',
                                required=True)    
        
        # Output folder name
        self._parser.add_argument('-o','--outputs-folder', 
                                type=str, 
                                dest='output_folder', 
                                help='Output folder name',
                                required=True)    
        return self._parser    
        
class AzureBatchAIComputeE13N:        
    """
    Facade class that distributes jobs to the forecasting toolkit compute backends.

    :param run: AML Python SDK run object

    :param experiment_name: Name of the experiment
    :type experiment_name: str.

    :param job_type: Job type. One of :class:`ftk.factor_types.ComputeJobType` enun str
    :type job_type: str

    :param data_folder: Mount path of the data location
    :type data_folder: str

    :param output_folder: Name of the output foder. Outputs will be pushed to 
                        a relative path under the data mount location
    :type output_folder: str

    """
    __run = None
    _experiment_name = None
    _data_folder = None
    _output_folder = None

    def __init__(self, 
                    run, 
                    experiment_name, 
                    job_type, 
                    data_folder, 
                    output_folder):
        self.__run = run        
        self._experiment_name = experiment_name        
        self._job_type = job_type
        self._data_folder = data_folder
        self._output_folder = output_folder

    def execute_job(self, job_type):

        try:

            print('Deserializing all input data...')        
            func = self._deserialize('func')
            data_map_func = self._deserialize('data_map_func')
            data = self._deserialize('data')
            kwargs = self._deserialize('kwargs')
            print('All inputs deserialized successfully.')  

            if ComputeJobType[job_type] is ComputeJobType.CVSearch:
                print('Job type is CVSearch. Starting cross-validation job...')
                _job_results, _errors = self._process_cvsearch_job(func, data, data_map_func, **kwargs)
                print('Cross-validation job is completed.')

                if _job_results is not None:
                    print('Serializing job results...')
                    self._serialize('job_results', _job_results)
                
                if _errors is not None:
                    print('Serializing errors...')
                    self._serialize('errors', _errors)
            else:
                print('Job type {} is not supported currently'.format(job_type))
        except:
            print("Unexpected error encountered:", sys.exc_info()[0])            
            self._serialize('errors', sys.exc_info()[0])
        return self 

    def _deserialize(self, obj_name):
        file_name = '{}/{}.pkl'.format(self._data_folder, obj_name)
        with open(file_name, 'rb') as _object:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
            return pickle.load(_object) 

    def _serialize(self, obj_name, obj):
        target_file = '{}/{}.pkl'.format(self._output_folder, obj_name)        
        with open(target_file, 'wb') as output:
            pickle.dump(obj, output, -1) 
        
    def _process_cvsearch_job(self, func, data, data_map_func, **kwargs):
        """
        Execute cross-validation search jobs using joblib. This is essentially a 
        "blocking" API and no futures are created/returned. 

       :param func: Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data: Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func: Function that takes in the data and splits it into 
        chunks appropriately for processing. 
        :type data_map_func: Callable.
        :param args: List of arguments to be passed to the func.
        :type args: list.
        :param kwargs: Keyword arguments to be passed to the func.
        :type args: dict.
        :returns: self.
        :rtype: object.

        :raises ComputeException: Raised if input parameters are invalid.
        """        
        _errors = None
        if func is None:
            raise ComputeException(Messages.FUNC_PARAM_NOT_SPECIFIED)

        if data is None:
            raise ComputeException(Messages.DATA_PARAM_NOT_SPECIFIED)

        try:
            # TODO: Jobs must be dynamic
            _job_results = Parallel(n_jobs=mp.cpu_count(),                                         
                                    verbose=10)(delayed(func)
                    (data, parameters, train, test, **kwargs)
                    for parameters, (train, test) in data_map_func(data, **kwargs))

        except TypeError as typ_err:
            _errors = typ_err
        except Exception as exc:
            _errors = exc

        return _job_results, _errors       
        
if __name__ == '__main__':   

    # Initialize the `AzureMLForecastE13NArgParser` arg parser.
    amlfp_arg_parser = AzureMLForecastE13NArgParser()
    parser = amlfp_arg_parser.add_arguments()
    args = parser.parse_args()    
        
    # Get the current submitted run object
    run = Run.get_submitted_run()    
    
    # Fetch all parameters
    experiment_name = args.experiment_name    
    job_type = args.job_type
    data_folder = os.path.join(args.data_folder, args.experiment_name)
    output_folder = os.path.join(args.data_folder, '{}_{}'.format(args.experiment_name, args.output_folder))    

    # Make outputs dir if not present        
    os.makedirs(output_folder, exist_ok=True)

    print("Experiment name: {}".format(experiment_name))
    print("Job type: {}".format(job_type))
    print("Data folder: {}".format(data_folder))
    print("Output folder: {}".format(output_folder))
    
    # Execute experiment
    print('Starting experiment execution...')
    amlfp_batchai_compute = AzureBatchAIComputeE13N(run, 
                                                    experiment_name, 
                                                    job_type,
                                                    data_folder,                                                     
                                                    output_folder)        
    compute_executor = amlfp_batchai_compute.execute_job(args.job_type)    

    print('Experiment completed.')    