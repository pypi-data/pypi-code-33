import pickle
from ftk.pipeline import AzureMLForecastPipelineExecutionType
from ftk.operationalization.dnnscorecontext import DnnScoreContext
from ftk.constants import PIPELINE_PREDICT_OPERATION
import json

def execute_pipeline_operation(pipeline, operation_list):
    """
    Execute the operations defined in operation_list in sequence on the
    pipeline.

    :param pipeline: AzureMLForecastPipeline
        The pipeline that the operations are executed on.
    :param operation_list: List of tuples.
        Each tuple in the list represents a single operation to be executed
        on the pipeline. The first element of the tuple is the operation type,
        e.g AzureMLForecastPipelineExecutionType.fit, and the second element
        of the tuple is the dictionary of the keyword arguments and values to
        be passed into the operation, e.g {'X': sample_tsdf}, where the
        sample_tsdf is a TimeSeriesDataFrame input for the operation.

    :returns:
    (pipeline, last_step_output)
        pipeline: AzureMLForecastPipeline
            the pipeline object after the execution of the operations.
        last_step_output:
            The output of the last steps operation. If the last operation has
            no output, then it will be None.

    """

    if len(operation_list)>0:
        for i, operation_item in enumerate(operation_list):
            operation_type = operation_item[0]
            operation_args = operation_item[1]
            step_output = pipeline.execute_pipeline_op(
                operation_type, **operation_args)

    return pipeline, step_output


def score_run(dnn_score_context, pipeline):
    """
    score function in run() function of score script.
    """
    pipeline_execution_type = dnn_score_context.pipeline_execution_type
    scoring_data = dnn_score_context.input_scoring_data

    if pipeline_execution_type == PIPELINE_PREDICT_OPERATION:
        operation_list = [
            (AzureMLForecastPipelineExecutionType.predict,
             {'X': scoring_data})]

    pipeline, last_step_output = execute_pipeline_operation(
        pipeline, operation_list)

    if pipeline_execution_type in [PIPELINE_PREDICT_OPERATION]:
        # return prediction json string
        prediction = last_step_output.tolist()
        return json.dumps(prediction)


