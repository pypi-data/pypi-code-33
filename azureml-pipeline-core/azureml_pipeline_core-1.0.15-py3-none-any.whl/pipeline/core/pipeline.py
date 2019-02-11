# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""pipeline.py, module for creating and submitting a pipeline."""
from azureml.pipeline.core._graph_context import _GraphContext
from azureml.pipeline.core.builder import _PipelineGraphBuilder
from azureml.core._experiment_method import experiment_method


def _submit_pipeline(pipeline, workspace, experiment_name, **kwargs):
    """
    Submit a pipeline.

    :param pipeline: pipeline
    :type pipeline: Pipeline
    :param workspace: workspace
    :type workspace: Workspace
    :param experiment_name: experiment name
    :type experiment_name: str
    :param kwargs: kwargs
    :type kwargs: dict

    :return: PipelineRun object
    :rtype: PipelineRun
    """
    continue_on_step_failure = False
    regenerate_outputs = False
    pipeline_params = None
    for key, value in kwargs.items():
        if key == 'continue_on_step_failure':
            continue_on_step_failure = value
        elif key == 'regenerate_outputs':
            regenerate_outputs = value
        elif key == 'pipeline_params':
            pipeline_params = value

    return pipeline.submit(experiment_name, pipeline_parameters=pipeline_params,
                           continue_on_step_failure=continue_on_step_failure,
                           regenerate_outputs=regenerate_outputs)


class Pipeline(object):
    """
    Pipeline represents a collection of steps which can be executed as a workflow.

    A pipeline is created with a list of steps and a workspace. Submit a pipeline using
    :func:`azureml.core.Experiment.submit`. When submit is called,
    a :class:`azureml.pipeline.core.PipelineRun` is created which in turn creates
    :class:`azureml.pipeline.core.StepRun` objects for each step in the workflow.


    :param workspace: The workspace to submit the Pipeline on.
    :type workspace: azureml.core.workspace.Workspace
    :param steps: The list steps to execute as part of a Pipeline.
    :type steps: list
    :param description: The description of the Pipeline.
    :type description: str
    :param default_datastore: The default datastore to use for data connections.
    :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
    :param default_source_directory: The default script directory for steps which execute a script.
    :type default_source_directory: str
    :param resolve_closure: Whether resolve closure or not (automatically bring in dependent steps).
    :type resolve_closure: bool
    """

    @experiment_method(submit_function=_submit_pipeline)
    def __init__(self, workspace, steps, description=None,
                 default_datastore=None, default_source_directory=None, resolve_closure=True,
                 _workflow_provider=None, _service_endpoint=None):
        """
        Initialize Pipeline.

        :param workspace: The workspace to submit the Pipeline on.
        :type workspace: azureml.core.workspace.Workspace
        :param steps: The list steps to execute as part of a Pipeline.
        :type steps: list
        :param description: The description of the Pipeline.
        :type description: str
        :param default_datastore: The default datastore to use for data connections.
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param default_source_directory: The default script directory for steps which execute a script.
        :type default_source_directory: str
        :param resolve_closure: Whether resolve closure or not (automatically bring in dependent steps).
        :type resolve_closure: bool
        :param _workflow_provider: The workflow provider, if None one is created.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :param _service_endpoint: The service endpoint, if None it is determined using the workspace.
        :type _service_endpoint: str
        """
        self._name = description

        self._graph_context = _GraphContext("placeholder", workspace=workspace,
                                            default_source_directory=default_source_directory,
                                            workflow_provider=_workflow_provider,
                                            service_endpoint=_service_endpoint)
        self._graph_builder = _PipelineGraphBuilder(resolve_closure=resolve_closure,
                                                    context=self._graph_context,
                                                    default_datastore=default_datastore)
        if 'aether-dev' in self._graph_context.service_endpoint:
            print('Using dev endpoint:', self._graph_context.service_endpoint)

        self._graph = self._graph_builder.build(self._name, steps, finalize=False)

    def _set_experiment_name(self, name):
        self._graph_context.experiment_name = name
        if self._graph._name is None:
            self._graph._name = name
        if self._name is None:
            self._name = name

    @property
    def graph(self):
        """
        Get the graph associated with the pipeline. Steps and data inputs appear as nodes in the graph.

        :return: The graph.
        :rtype: azureml.pipeline.core.graph.Graph
        """
        return self._graph

    def validate(self):
        """
        Validate a pipeline and identify potential errors, such as unconnected inputs.

        :return: A list of errors in the pipeline.
        :rtype: list
        """
        return self.graph.validate()

    def _finalize(self, regenerate_outputs=False):
        """
        Finalize the graph.

        :param regenerate_outputs: Whether to regenerate step outputs.
        :type regenerate_outputs: bool

        :return: Dictionary of {node_id, (resource_id, is_new_resource)}
        :rtype: dict
        """
        return self.graph.finalize(regenerate_outputs=regenerate_outputs)

    def submit(self, experiment_name, pipeline_parameters=None, continue_on_step_failure=False,
               regenerate_outputs=False):
        """
        Submit a pipeline experiment.

        :param experiment_name: The name of the experiment to submit the pipeline on.
        :type experiment_name: str
        :param pipeline_parameters: Parameters to pipeline execution, dictionary of {name: value}
        :type pipeline_parameters: dict
        :param continue_on_step_failure: Whether to continue pipeline execution if a step fails.
        :type continue_on_step_failure: bool
        :param regenerate_outputs: Whether to force regeneration of all step outputs and disallow data reuse for
            this run.  Subsequent runs may reuse the results of this run.
        :type regenerate_outputs: bool

        :return: The submitted pipeline run.
        :rtype: azureml.pipeline.core.run.PipelineRun
        """
        self._set_experiment_name(experiment_name)

        return self.graph.submit(pipeline_parameters=pipeline_parameters,
                                 continue_on_step_failure=continue_on_step_failure,
                                 regenerate_outputs=regenerate_outputs)

    def publish(self, name=None, description=None, version=None):
        """
        Publish a pipeline and make it available for rerunning.

        :param name: Name of the published pipeline.
        :type name: str
        :param description: Description of the published pipeline.
        :type description: str
        :param version: Version of the published pipeline.
        :type version: str

        :return: Created published pipeline.
        :rtype: azureml.pipeline.core.PublishedPipeline
        """
        return self.graph._save(name=name, description=description, version=version)
