# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""run.py, module for running pipeline."""
import time
import sys
from azureml.core import Run, Experiment
from azureml._restclient.utils import create_session_with_retry


class PipelineRun(Run):
    """
    Represents a run of a pipeline.

    This class can be used to manage, check status and retrieve run details once a pipeline run is submitted.
    Use :func:`azureml.core.Run.get_children` to retrieve the
    :class:`azureml.pipeline.core.StepRun` object which are created by this pipeline run. Other uses include
    retrieving the :class:`azureml.pipeline.core.graph.Graph` object associated with the pipeline run, fetching the
    status of the pipeline run, and waiting for run completion.


    :param experiment: The Experiment object associated with the PipelineRun.
    :type experiment: azureml.core.Experiment
    :param run_id: The run id of the PipelineRun.
    :type run_id: str
    """

    def __init__(self, experiment, run_id, _service_endpoint=None):
        """
        Initialize a Pipeline run.

        :param experiment: The Experiment object associated with the PipelineRun.
        :type experiment: azureml.core.Experiment
        :param run_id: The run id of the PipelineRun.
        :type run_id: str
        :param _service_endpoint: The endpoint to connect to.
        :type _service_endpoint: str
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        self._context = _GraphContext(experiment.name, workspace=experiment.workspace,
                                      service_endpoint=_service_endpoint)
        self._pipeline_run_provider = self._context.workflow_provider.pipeline_run_provider
        self._graph = None
        super().__init__(experiment, run_id)

    #######################################
    # Run methods
    #######################################

    def get_tags(self):
        """
        Get the set of tags for the run.

        :return: The dictionary of tags for the run.
        :rtype: dict
        """
        # Temporary workaround to return an empty set of tags when the tag list is not set
        try:
            return super().get_tags()
        except KeyError:
            return {}

    def _get_status(self):
        """
        Get the current status of the pipeline run.

        :return: The current status of the pipeline run.
        :rtype: str
        """
        return self._pipeline_run_provider.get_status(self._run_id)

    def complete(self):
        """
        Complete for Pipeline run.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Complete is unsupported for Pipeline run.")

    def fail(self):
        """
        Fail for Pipeline run.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Fail is unsupported for Pipeline run.")

    def child_run(self, name=None, run_id=None, outputs=None):
        """
        Child run for Pipeline run.

        :param name: Optional name for the child
        :type name: str
        :param run_id: Optional run_id for the child, otherwise uses default
        :type run_id: str
        :param outputs: Optional outputs directory to track for the child
        :type outputs: str
        :raises: NotImplementedError

        :return: the child run
        :rtype: azureml.core.run.Run
        """
        raise NotImplementedError("Child run is unsupported for Pipeline run.")

    #######################################
    # PipelineRun-specific methods
    #######################################

    def get_graph(self):
        """
        Get the graph of the pipeline run.

        :return: The graph.
        :rtype: azureml.pipeline.core.graph.Graph
        """
        if self._graph is None:
            self._graph = self._context.workflow_provider.graph_provider.create_graph_from_run(self._context,
                                                                                               self._run_id)
        return self._graph

    def get_status(self):
        """
        Get the current status of the pipeline run.

        :return: The run status.
        :rtype: str
        """
        return self._get_status()

    def publish_pipeline(self, name, description, version):
        """
        Publish a pipeline and make it available for rerunning.

        The original pipeline associated with the pipeline_run is used as the base for the published pipeline.

        :param name: Name of the published pipeline.
        :type name: str
        :param description: Description of the published pipeline.
        :type description: str
        :param version: Version of the published pipeline.
        :type version: str

        :return: Created published pipeline.
        :rtype: azureml.pipeline.core.PublishedPipeline
        """
        return self._context.workflow_provider.published_pipeline_provider.create_from_pipeline_run(
            name=name, pipeline_run_id=self._run_id, description=description, version=version)

    def find_step_run(self, name):
        """
        Find a step run in the pipeline by name.

        :param name: Name of the step to find.
        :type name: str

        :return: List of StepRuns with the provided name.
        :rtype: list
        """
        children = self.get_children()
        step_runs = []
        for child in children:
            if name == child._run_dto['name']:
                step_runs.append(child)

        return step_runs

    def get_pipeline_output(self, pipeline_output_name):
        """
        Get the PortDataReference for the given Pipeline output.

        :param pipeline_output_name: Name of the Pipeline output to get.
        :type pipeline_output_name: str

        :return: The PortDataReference representing the Pipeline output data.
        :rtype: azureml.pipeline.core.PortDataReference
        """
        return self._pipeline_run_provider.get_pipeline_output(self._context, self.id, pipeline_output_name)

    def wait_for_completion(self, show_output=True, timeout_seconds=sys.maxsize):
        """
        Wait for the completion of this Pipeline run.

        Returns the status after the wait.

        :param show_output: show_output=True shows the pipeline run status on sys.stdout.
        :type show_output: bool
        :param timeout_seconds: Number of seconds to wait before timing out.
        :type timeout_seconds: int

        :return: The final status.
        :rtype: str
        """
        print('RunId:', self.id)
        print('Link to Portal:', self.get_portal_url())
        status = self._get_status()
        last_status = None
        separator = ''
        time_run = 0
        sleep_period = 5
        while status == 'NotStarted' or status == 'Running' or status == 'Unknown':
            if time_run + sleep_period > timeout_seconds:
                if show_output:
                    print('Timed out of waiting, %sStatus: %s.' % (separator, status), flush=True)
                break
            time_run += sleep_period
            time.sleep(sleep_period)
            status = self._get_status()
            if last_status != status:
                if show_output:
                    print('%sStatus: %s' % (separator, status))
                last_status = status
                separator = ''
            else:
                if show_output:
                    print('.', end='', flush=True)
                separator = '\n'
        print(self.get_details())
        return status

    def cancel(self):
        """Cancel the ongoing run."""
        self._pipeline_run_provider.cancel(self._run_id)

    def get_steps(self):
        """
        Get the step runs for all pipeline steps that have completed or started running.

        :return: List of StepRuns
        :rtype: list
        """
        return self.get_children()

    @staticmethod
    def _from_dto(experiment, run_dto):
        """
        Create a PipelineRun object from the experiment and run dto.

        :param experiment: The experiment object.
        :type experiment: azureml.core.Experiment
        :param run_dto: The run dto object.
        :type run_dto: RunDto

        :return: The PipelineRun object.
        :rtype: PipelineRun
        """
        return PipelineRun(experiment=experiment, run_id=run_dto.run_id)

    @staticmethod
    def get_pipeline_runs(workspace, pipeline_id, _service_endpoint=None):
        """
        Fetch the pipeline runs that were generated from a published pipeline.

        :param workspace: The Workspace associated with the pipeline
        :type workspace: azureml.core.Workspace
        :param pipeline_id: Id of the published pipeline
        :type pipeline_id: str
        :param _service_endpoint: The endpoint to connect to.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.run.PipelineRun`
        :rtype: list
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        context = _GraphContext('placeholder', workspace=workspace, service_endpoint=_service_endpoint)
        pipeline_run_provider = context.workflow_provider.pipeline_run_provider

        run_tuples = pipeline_run_provider.get_runs_by_pipeline_id(pipeline_id)
        pipeline_runs = []
        for (run_id, experiment_name) in run_tuples:
            experiment = Experiment(workspace, experiment_name)
            pipeline_run = PipelineRun(experiment=experiment, run_id=run_id, _service_endpoint=_service_endpoint)
            pipeline_runs.append(pipeline_run)

        return pipeline_runs


class StepRun(Run):
    """
    A run of a step in a pipeline.

    This class can be used to manage, check status, and retrieve run details once the parent pipeline run is submitted
    and the pipeline has submitted the step run. Use :func:`azureml.pipeline.core.StepRun.get_details_with_logs` to
    fetch the run details and logs created by the run. Other uses of this class include fetching outputs generated
    by the step. Use :func:`azureml.pipeline.core.StepRun.get_outputs` to retrieve a dict of the step outputs, or use
    :func:`azureml.pipeline.core.StepRun.get_output` to retrieve the single
    :class:`azureml.pipeline.core.StepRunOutput` object for the output with the provided name. You may also use
    :func:`azureml.pipeline.core.StepRun.get_output_data` to fetch the :class:`azureml.pipeline.core.PortDataReference`
    for the specified step output directly.


    :param experiment: the Experiment object of the step run.
    :type experiment: azureml.core.Experiment
    :param step_run_id: the run id of the step run.
    :type step_run_id: str
    :param pipeline_run_id: the run id of the parent pipeline run.
    :type pipeline_run_id: str
    :param node_id: the id of the node in the graph that represents this step.
    :type node_id: str
    """

    def __init__(self, experiment, step_run_id, pipeline_run_id, node_id, _service_endpoint=None,
                 _is_reused=False, _current_node_id=None):
        """
        Initialize a Step run.

        :param experiment: the Experiment object of the step run.
        :type experiment: azureml.core.Experiment
        :param step_run_id: the run id of the step run.
        :type step_run_id: str
        :param pipeline_run_id: the run id of the parent pipeline run.
        :type pipeline_run_id: str
        :param node_id: the id of the node in the graph that represents this step.
        :type node_id: str
        :param _service_endpoint: The endpoint to connect to.
        :type _service_endpoint: str
        :param _is_reused: Whether this run is a reused previous run.
        :type _is_reused: bool
        :param _current_node_id: For reused node, the node id on the current graph.
        :type _current_node_id: str
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        self._context = _GraphContext(experiment.name, workspace=experiment.workspace,
                                      service_endpoint=_service_endpoint)
        self._pipeline_run_id = pipeline_run_id

        # StepRun may have a different experiment than the PipelineRun if it was reused, check
        experiment_name = \
            self._context.workflow_provider.pipeline_run_provider.get_pipeline_experiment_name(pipeline_run_id)

        if experiment_name != experiment.name:
            experiment = Experiment(experiment.workspace, experiment_name)
            self._context = _GraphContext(experiment.name, workspace=experiment.workspace,
                                          service_endpoint=_service_endpoint)

        self._node_id = node_id
        self._step_run_provider = self._context.workflow_provider.step_run_provider

        super().__init__(experiment, step_run_id)

        self._is_reused = _is_reused
        self._current_node_id = _current_node_id

        self.name = self._run_dto['name']

    #######################################
    # Run methods
    #######################################

    def complete(self):
        """
        Complete for step run.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Complete is unsupported for Step run.")

    def fail(self):
        """
        Fail for step run.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Fail is unsupported for Step run.")

    def child_run(self, name=None, run_id=None, outputs=None):
        """
        Child run for step run.

        :param name: Optional name for the child
        :type name: str
        :param run_id: Optional run_id for the child, otherwise uses default
        :type run_id: str
        :param outputs: Optional outputs directory to track for the child
        :type outputs: str
        :raises: NotImplementedError

        :return: the child run
        :rtype: azureml.core.run.Run
        """
        raise NotImplementedError("Child run is unsupported for Step run.")

    #######################################
    # StepRun-specific methods
    #######################################

    @property
    def pipeline_run_id(self):
        """
        Return the id of the pipeline run corresponding to this step run.

        :return: The PipelineRun id.
        :rtype: str
        """
        return self._pipeline_run_id

    def get_status(self):
        """
        Get the current status of the step run.

        :return: The current status.
        :rtype: str
        """
        return self._step_run_provider.get_status(self._pipeline_run_id, self._node_id)

    def get_job_log(self):
        """
        Dump the current job log for the step run.

        :return: The log string.
        :rtype: str
        """
        return self._step_run_provider.get_job_log(self._pipeline_run_id, self._node_id)

    def get_stdout_log(self):
        """
        Dump the current stdout log for the step run.

        :return: The log string.
        :rtype: str
        """
        return self._step_run_provider.get_stdout_log(self._pipeline_run_id, self._node_id)

    def get_stderr_log(self):
        """
        Dump the current stderr log for the step run.

        :return: The log string.
        :rtype: str
        """
        return self._step_run_provider.get_stderr_log(self._pipeline_run_id, self._node_id)

    def get_outputs(self):
        """
        Get the step outputs.

        :return: A dictionary of StepRunOutputs with the output name as the key.
        :rtype: dict
        """
        return self._step_run_provider.get_outputs(self, self._context, self._pipeline_run_id, self._node_id)

    def get_output(self, name):
        """
        Get the node output with the given name.

        :param name: Name of the output.
        :type name: str

        :return: The StepRunOutput with the given name.
        :rtype: azureml.pipeline.core.StepRunOutput
        """
        return self._step_run_provider.get_output(self, self._context, self._pipeline_run_id, self._node_id, name)

    def get_output_data(self, name):
        """
        Get the output data from a given output.

        :param name: Name of the output.
        :type name: str

        :return: The PortDataReference representing the step output data.
        :rtype: azureml.pipeline.core.PortDataReference
        """
        return self.get_output(name).get_port_data_reference()

    def wait_for_completion(self, show_output=True, timeout_seconds=sys.maxsize):
        """
        Wait for the completion of this pipeline run.

        Returns the status after the wait.

        :param show_output: show_output=True shows the run status on sys.stdout.
        :type show_output: bool
        :param timeout_seconds: Number of seconds to wait before timing out.
        :type timeout_seconds: int

        :return: The final status.
        :rtype: str
        """
        status = self.get_status()
        last_status = None
        separator = ''
        time_run = 0
        sleep_period = 5
        while status == 'NotStarted' or status == "Queued" or status == 'Running' or status == 'Unknown' \
                or status == "PartiallyExecuted":
            if time_run + sleep_period > timeout_seconds:
                if show_output:
                    print('Timed out of waiting, %sstatus:%s.' % (separator, status), flush=True)
                break
            time_run += sleep_period
            time.sleep(sleep_period)
            status = self.get_status()
            if last_status != status:
                if show_output:
                    print('%sstatus:%s' % (separator, status))
                last_status = status
                separator = ''
            else:
                if show_output:
                    print('.', end='', flush=True)
                separator = '\n'
        return status

    def get_details_with_logs(self):
        """
        Return the status details of the run with log file contents.

        :return: Returns the status for the run with log file contents
        :rtype: dict
        """
        from azureml._execution import _commands
        details = self.get_details()
        log_files = details.get("logFiles", {})
        session = create_session_with_retry()

        for log_name in log_files:
            content = _commands._get_content_from_uri(log_files[log_name], session)
            log_files[log_name] = content
        log_files['STDOUT'] = self.get_stdout_log()
        log_files['STDERR'] = self.get_stderr_log()
        log_files['JOBLOG'] = self.get_job_log()
        return details

    @staticmethod
    def _from_dto(experiment, run_dto):
        """
        Create a StepRun object from the experiment and run dto.

        :param experiment: The experiment object.
        :type experiment: Experiment
        :param run_dto: The run dto object.
        :type run_dto: RunDto

        :return: The StepRun object.
        :rtype: StepRun
        """
        run_tags = getattr(run_dto, "tags", {})
        node_id = run_tags.get('azureml.nodeid')
        pipeline_run_id = run_tags.get('azureml.pipeline')
        return StepRun(experiment, step_run_id=run_dto.run_id, pipeline_run_id=pipeline_run_id, node_id=node_id)

    @staticmethod
    def _from_reused_dto(experiment, run_dto):
        """
        Create a StepRun object from the experiment and reused run dto.

        :param experiment: The experiment object.
        :type experiment: Experiment
        :param run_dto: The run dto object.
        :type run_dto: RunDto

        :return: The StepRun object.
        :rtype: StepRun
        """
        run_tags = getattr(run_dto, "tags", {})
        reused_run_id = run_tags.get('azureml.reusedrunid')
        reused_node_id = run_tags.get('azureml.reusednodeid')
        reused_pipeline_run_id = run_tags.get('azureml.reusedpipeline')
        current_node_id = run_tags.get('azureml.nodeid', None)
        return StepRun(experiment, step_run_id=reused_run_id, pipeline_run_id=reused_pipeline_run_id,
                       node_id=reused_node_id, _is_reused=True, _current_node_id=current_node_id)


class StepRunOutput(object):
    """
    Represents an output created by a StepRun in a pipeline.

    Can be used to access the output data of a step. Step run outputs are instantiated by calling
    :func:`azureml.pipeline.core.StepRun.get_output`. Use
    :func:`azureml.pipeline.core.StepRunOutput.get_port_data_reference` to retrieve the
    :class:`azureml.pipeline.core.PortDataReference` which can be used to download the data and can be used as an
    step input in a future pipeline.


    :param context: The graph context object.
    :type context: _GraphContext
    :param pipeline_run_id: The id of the pipeline run which created the output.
    :type pipeline_run_id: str
    :param step_run: The step run object which created the output.
    :type step_run: azureml.pipeline.core.StepRun
    :param name: The name of the output.
    :type name: str
    :param step_output: The step output.
    :type step_output: azureml.pipeline.core.graph.NodeOutput
    """

    def __init__(self, context, pipeline_run_id, step_run, name, step_output):
        """
        Initialize StepRunOutput.

        :param context: The graph context object.
        :type context: _GraphContext
        :param pipeline_run_id: The id of the pipeline run which created the output.
        :type pipeline_run_id: str
        :param step_run: The step run object which created the output.
        :type step_run: azureml.pipeline.core.StepRun
        :param name: The name of the output.
        :type name: str
        :param step_output: The step output.
        :type step_output: azureml.pipeline.core.graph.NodeOutput
        """
        self.step_run = step_run
        self.pipeline_run_id = pipeline_run_id
        self.context = context
        self.name = name
        self.step_output = step_output

    def get_port_data_reference(self):
        """
        Get port data reference produced by the step.

        :return: The port data reference.
        :rtype: azureml.pipeline.core.PortDataReference
        """
        return self.context.workflow_provider.port_data_reference_provider.create_port_data_reference(self)
