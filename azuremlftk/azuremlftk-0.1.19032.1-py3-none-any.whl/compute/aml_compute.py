import os
import io
import json
from datetime import datetime
import tempfile
import dill as pickle
import shutil
import importlib
from random import *
from warnings import warn

# Conditional import of AML Python SDK.
azureml_spec = importlib.util.find_spec("azureml.core")
if azureml_spec is not None:
    import azureml.core
    from azureml.core import (Workspace, 
                            Experiment, 
                            Run,                             
                            ScriptRunConfig)    
    from azureml.core.runconfig import RunConfiguration
    from azureml.core.conda_dependencies import CondaDependencies
else:
     warn("Azure ML Python SDK was not found in the current environment. \
            The `aml_compute` module will not be useable.", RuntimeWarning)

from ftk.factor_types import ComputeJobType
from ftk.exception import (ComputeException,
                           JobTypeNotSupportedException)
from ftk.verify import Messages
from ftk.constants import *
from .compute_base import (ComputeStrategyMixin, ComputeBase)
    
# pylint: disable=no-member
class AMLBatchAICompute(ComputeBase):
    """
    .. py:class:: AMLBatchAICompute
    
    Provides capabilities to execute Forecasting jobs on Azure Batch AI
    backend using Azure Machine Learning's experimentation stack. 

    :param workspace:     
        An Azure Machine Learning workspace object        
    :type workspace: :class:`azureml.core.workspace.Workspace`
    
    :param run_config: 
        An Azure Machine Learning run configuration object        
    :type run_config: :class:`azureml.core.runconfig.RunConfiguration`
    
    :param experiment_name: 
        Name of the experiment. If the parameter is not specified an experiment name prefix `amlpfexpt`
        is auto-generated. An experiment can either indicate a single run
        of the experiment or be a static value that indicates a set of runs. 
        Executing with the same name will over-write remove AML artifacts that were 
        generated during a previous run. Although this will not impact the current run, previous
        run artifacts from the local system may become unavailable.
    :type experiment_name: str

    :param experiment_script: 
        Optional parameter that is a path to the experiment script to execute.
        If not specified, a template experiment is used to run standard job types supported in this package. 
        If a custom script is provided then it is expected that the user will handle all
        results output from the script. The job results are available on this object's
        `job_results` property and the errors on the `errors` property.
        script 
    :type experiment_script: str

    :param conda_dependencies: 
        Optional parameter that is a path to the conda dependencies yml file that will be used to create
        an linux image for the Azure Batch AI contrainers to use.
        If not specified, a template yml is used. When specified an absolute path mst be provided.
    :type conda_dependencies: str

    """

    _workspace = None
    _experiment = None    
    _run_config = None
    _custom_experiment = True
    _aml_conda_dependencies = None

    def __init__(self, 
                workspace,
                run_config, 
                experiment_name=None, 
                experiment_script=None, 
                conda_dependencies=None):
        
        super().__init__()

        # AML Workspace object
        self._workspace = workspace
        
        # AML RunConfiguration object
        self._run_config = run_config

        # Experiment name - If none specified an experiment with prefix
        # 'amlpfext' is generated
        if experiment_name is not None:
            self._experiment_name = experiment_name
        else:
            date_now = datetime.now()            
            self._experiment_name = 'amlpf_expt_{}'.format(datetime.strftime(date_now, "%y%m%d%H%M%S"))

        # Name of the experiment script
        if experiment_script is None:
            self._experiment_script = AMLCOMPUTE_EXPERIMENT_TEMPLATE_NAME
            self._custom_experiment = False       
        else:
            self._experiment_script = experiment_script
            self._custom_experiment = True

        # Conda dependencies to setup. The environment to execute
        # script is system managed. If no conda dependencies is specified we will
        # use stock ./requirements_E13N.yml otherwise user specified config is used.
        if conda_dependencies is None:
            self._conda_dependencies = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                                    AMLCOMPUTE_CONDA_REQUIREMENTS_TEMPLATE)            
        else:
            self._conda_dependencies = conda_dependencies

        # Initialize the AML CondaDependencies using either user-supplied
        # or our own template inited yml.
        self._aml_conda_dependencies = CondaDependencies(conda_dependencies_file_path=self._conda_dependencies)
    
    @property
    def workspace(self):
        """
        Get workspace object. Expected to be of type 
        :class:`azureml.core.workspace.Workspace`
        """
        return self._workspace

    @workspace.setter        
    def workspace(self, val):
        """
        Set workspace object. Expected to be of type 
        :class:`azureml.core.workspace.Workspace`
        """
        self._workspace = val

    @property        
    def experiment(self):
        """
        Get experiment object. Expected to be of type 
        :class:`azureml.core.experiment.Experiment`
        """
        return self._experiment
    
    @property
    def run_config(self):
        """
        Get run configuration object. 
        
        Expected to be of type 
        :class:`azureml.core.runconfig.RunConfiguration`
        """
        return self._run_config

    @run_config.setter
    def run_config(self, val):
        """
        Set run configuration object.
        
        :param val: Value to set.
        :type val: :class:`azureml.core.runconfig.RunConfiguration`

        """
        self._run_config = val

    @property
    def experiment_script(self):
        """
        Get experiment script name
        """
        return self._experiment_script
    
    @experiment_script.setter
    def experiment_script(self, val):
        """
        Set experiment script name.

        :param val: Value to set.
        :type val: str

        """
        self.experiment_script = val   
    
    @ComputeBase.job_results.setter
    def job_results(self, val):
        """
        Set the job results. 

        :param val: Value to set.
        :type val: list

        """
        if self._job_results is None:
            self._job_results = list()
        self._job_results.append(val)
    
    @ComputeBase.jobs.setter
    def jobs(self, val):
        """
        Set the jobs

        :param val: Value to set.
        :type val: list, None.

        """
        self._jobs = val
    
    @ComputeBase.summary.setter
    def summary(self, val):
        """
        Set the summary. 

        :param val: Value to set.
        :type val: list.

        """
        if self._summary is None:
            self._summary = list()
        self._summary.append(val)

    @ComputeBase.errors.setter
    def errors(self, val):
        """
        Set the errors.

        :param val: Value to set.
        :type val: list.
        """
        if self._errors is None:
            self._errors = list()
        self._errors.append(val)    
    
    @ComputeBase.scheduler.setter
    def scheduler(self, val):
        """
        Scheduler object. None required for this backend as 
        AML experimentation service handles the job scheduling.
        """       
        self._scheduler = None

    def state(self):
        """
        State of the compute backend. The following checks are to be made before
        jobs can be submitted:

        1. Validate the workspace is of type ::class:`~azureml.core.workspace.Workspace`
        2. Validate `self.experiment` is of type ::class:`~azureml.core.experiment.Project`
        3. Validate `self._run_config` is of type ::class:`~azureml.core.runconfig.RunConfiguration`        

        """

        if azureml_spec is None:
            raise ComputeException('Could not import some or all modules of Azure ML Python SDK. \
                        Ensure the current environment has AML Python SDK installed.')

        if self._workspace is None or not isinstance(self._workspace, azureml.core.workspace.Workspace):
            raise ComputeException('Workspace object must be of type {}. \
                                    The actual object is of type {}'
                                    .format(type(azureml.core.workspace.Workspace).__name__,
                                    type(self._workspace).__name__))
        
        if self._run_config is None or not isinstance(self._run_config, azureml.core.runconfig.RunConfiguration):
            raise ComputeException('Run configuration must be of type {} \
                                    The actual object is of type {}'
                                    .format(type(azureml.core.runconfig.RunConfiguration).__name__,
                                    type(self._run_config).__name__))
        
        return True

    def execute_job(self, func, data, data_map_func, job_type, *args, **kwargs):
        """
        Execute a job using Azure Batch AI compute backend.
        
        :param func:
            Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data:
            Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type func: Callable.
        :param args:
            List of arguments to be passed to the func.
        :type args: list.
        :param kwargs:
            Keyword arguments to be passed to the func.
        :type args: dict.

        :returns: self.
        :rtype: object.

        :raises TypeError: If callable func and data_map_func are not passed.
        :raises JobTypeNotSupportedException: If job type is not supported.
        """       

        # Validate state of this object
        self.state()        

        # Validate input params
        if not callable(func):
            raise TypeError(Messages.PARAM_MUST_BE_CALLABLE.format(FUNC_PARAM_NAME))

        if data_map_func is not None and not callable(data_map_func):
            raise TypeError(Messages.PARAM_MUST_BE_CALLABLE.format(DATA_MAP_FUNC_PARAM_NAME))
    
        if job_type is None or not isinstance(job_type, ComputeJobType):
            raise JobTypeNotSupportedException(str(job_type))                        
        
        # Create a directory for the experiment under temp directory.
        # Note: We just create it for a cleaner experiment run experience.
        _src_dir = os.path.join(tempfile.gettempdir(), self._experiment_name)        
        if os.path.exists(_src_dir):
            shutil.rmtree(_src_dir, ignore_errors=True)
        os.makedirs(_src_dir)

        # Fetch default datastore for the workspace
        _default_data_store = self._workspace.get_default_datastore()

        # Serialize all parameter objects passed to this function.
        print('Serializing FUNC...')
        self._serialize(func, FUNC_PARAM_NAME, _src_dir) 

        if data_map_func is not None:
            print('Serializing DATA_MAP_FUNC...')
            self._serialize(data_map_func, DATA_MAP_FUNC_PARAM_NAME, _src_dir)

        print('Serializing DATA_PARAM_NAME...')
        self._serialize(data, DATA_PARAM_NAME, _src_dir)

        print('Serializing ARGS_PARAM_NAME...')
        self._serialize(args, ARGS_PARAM_NAME, _src_dir)

        print('Serializing KEYWORD_ARGS_PARAM_NAME...')
        self._serialize(kwargs, KEYWORD_ARGS_PARAM_NAME, _src_dir)

        # Upload all serialized objects to the default data store (on the Azure cloud)
        # The experiment script will pick these objects from there during execution.
        _default_data_store.upload(src_dir = _src_dir, 
                    target_path = self._experiment_name, 
                    overwrite = True, 
                    show_progress = True)

        # Remove the serialized files from experiment directory, 
        # the data for our script is uploaded already.
        for root, dirs, files in os.walk(_src_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        
        # Copy experiment script to the project directory.
        # For experiments that use template script, the experiment_script is the name 
        # of the script in the current sub-package. We simply copy it to the
        # experiment directory
        if not self._custom_experiment:
            _experiment_script_path = os.path.abspath(os.path.join(
                                        os.path.dirname(os.path.realpath(__file__)), 
                                        AMLCOMPUTE_EXPERIMENT_TEMPLATE_NAME))        
            shutil.copy(_experiment_script_path, _src_dir)

        # For custom experiments, the experiment_script is the full path.
        # Copy the script to experiment directory. Then reset the self._experiment_script to 
        # just be the name of the script.
        else:
            shutil.copy(self._experiment_script, _src_dir)
            self._experiment_script = os.path.split(self._experiment_script)

        # Setup system managed environment by specifying our conda
        self._run_config.prepare_environment = True
        self._run_config.environment.python.user_managed_dependencies = False        
        self._run_config.environment.python.conda_dependencies = self._aml_conda_dependencies
        
        # Compute the arguments list for Run
        _script_params = {
            "--experiment-name": self._experiment_name,
            "--job-type": job_type.name,            
            "--outputs-folder": AMLCOMPUTE_OUTPUT_LOC_NAME,
            "--data-folder": str(_default_data_store.as_mount())
        }        

        # Run submit needs a list, so we reformat the dict
        _args_list = list(sum(_script_params.items(), tuple()))

        # Execute the job. Note that the logic that splits the work items 
        # is embedded in the experiment script.
        if job_type is ComputeJobType.CVSearch or job_type is ComputeJobType.Custom:

            try:

                # Submit the experiment
                print('Submitting experiment....')
                # Create an AML Experiment for this run.                
                _script_config = ScriptRunConfig(source_directory=_src_dir, 
                                        script=self._experiment_script,
                                        run_config=self._run_config, 
                                        arguments = _args_list)
                self._experiment = Experiment(workspace=self._workspace, name=self._experiment_name)
                _run = self._experiment.submit(config=_script_config)

                # Blocking call that waits until the experiment is complete
                print('Waiting for completion...')
                _run.wait_for_completion(show_output=True)
                _run.complete()                
        
                # Once experiment is complete the outputs are expected
                # to be a in a relative location in the same data store - {data store path}/{experiment_name}/outputs
                # There are two expected output files - job_results.pkl and errors.pkl
                # We check and download whichever is available.
                _out_dir_name = '{}_{}'.format(self._experiment_name, AMLCOMPUTE_OUTPUT_LOC_NAME)
                _default_data_store.download(target_path=_src_dir, 
                                            prefix=_out_dir_name,
                                            show_progress=True)

                # If job results is available deserialize. This indicates our experiment 
                # ran without any errors. Unwrap results and set it to the self.job_results
                _out_dir = os.path.join(_src_dir, _out_dir_name)
                _job_results_file = os.path.join(_out_dir, '{}.pkl'.format(AMLCOMPUTE_OUTPUT_JOB_RESULTS))
                print('Checking if job results file {} exists'.format(_job_results_file))
                if os.path.exists(_job_results_file):
                    self.job_results = self._deserialize(_job_results_file)
                
                # If errors is available deserialize. This indicates our experiment 
                # failed. Unwrap and set the errors to the self.errors
                _error_file = os.path.join(_out_dir, '{}.pkl'.format(AMLCOMPUTE_OUTPUT_ERRORS))
                print('Checking if error file {} exists'.format(_error_file))
                if os.path.exists(_error_file):
                    self.errors = self._deserialize(_error_file)                
                
            except Exception as exc:
                self.errors = exc
        else:
            raise JobTypeNotSupportedException(Messages.JOB_TYPE_NOT_SUPPORTED.format(str(job_type)))

        # Cleanup local and remote resources
        # if everything was successful.
        try:
            if self.errors is None and os.path.exists(_src_dir):
                shutil.rmtree(_src_dir, ignore_errors=True)            
        except Exception as clean_exc:
            self.errors = clean_exc

        return self

    def execute_task_job(self, func, job_type, tasks, *func_args, **func_kwargs):        
        raise ComputeException(Messages.EXECUTE_TASK_JOB_NOT_SUPPORTED)           
    
    def _serialize(self, obj, target_file_name, target_path):        
        """
        Serialize the object `obj` passed in to the location `target_location` as the
        `target_file_name.pkl` file.
        """        
        target_file = '{}/{}.pkl'.format(target_path, target_file_name)     
        with open(target_file, 'wb') as output:
            pickle.dump(obj, output, -1)

    def _deserialize(self, file_path):        
        """
        Deserialize the pkl file back to an AMLPF object.
        """
        with open(file_path, 'rb') as _object:
            return pickle.load(_object)

    # pylint: enable=no-member