import pickle
import pandas as pd
import numpy as np
from ftk.pipeline import AzureMLForecastPipelineExecutionType
from ftk.operationalization import ScoreContext
from ftk.forecast_data_frame import ForecastDataFrame
from ftk.time_series_data_frame import TimeSeriesDataFrame


def execute_pipeline_operation(pipeline, operation_list):
    """
    .. py:method:: execute_pipeline_operation
    Execute the operations defined in operation_list in sequence on the
    pipeline.

    :param pipeline:
        The pipeline to execute the operations on.
    :type pipeline: AzureMLForecastPipeline

    :param operation_list:
        Each tuple in the list represents a single operation to be executed
        on the pipeline. The first element of the tuple is the operation type,
        e.g ```AzureMLForecastPipelineExecutionType.fit```, and the second element
        of the tuple is the dictionary of the keyword arguments and values to
        be passed into the operation, e.g. ```{'X': sample_tsdf}```, where the
        sample_tsdf is a TimeSeriesDataFrame input for the operation.
    :type operation_list: list of tuples

    :returns:
        (pipeline, last_step_output)
        pipeline: AzureMLForecastPipeline
            The pipeline object after the execution of the operations.
        last_step_output:
            The output of the last step operation.
    :rtype: tuple

    """

    if len(operation_list)>0:
        for i, operation_item in enumerate(operation_list):
            operation_type = operation_item[0]
            operation_args = operation_item[1]
            step_output = pipeline.execute_pipeline_op(
                operation_type, **operation_args)

    return pipeline, step_output


def score_run(score_context, pipeline):
    """
    .. py:method:: score_run
    The score function used in the run() function of the score script.

    :param score_context:
        The ScoreContext object containing the training data, scoring data,
        and scoring mode/pipeline execution type configuration.
    :type score_context: :class:`ftk.operationalization.scorecontext.ScoreContext`

    :param pipeline:
        The pipeline to fit and/or predict on.
    :type pipeline: :class:`ftk.pipeline.AzureMLForecastPipeline`

    :return:
        Prediction result or fitted pipeline, depending on the web service
        scoring mode determined by ScoreContext.pipeline_execution_type.
    :rtype: json str or pickled pipeline
    """
    pipeline_execution_type = score_context.pipeline_execution_type
    training_data_tsdf = score_context.input_training_data_tsdf
    scoring_data_fcdf = score_context.input_scoring_data_fcdf
    fit_params = score_context.fit_params

    if fit_params is None:
        fit_params = {}

    fit_operation_tuple = (AzureMLForecastPipelineExecutionType.fit,
                           {'X': training_data_tsdf, **fit_params})

    predict_operation_tuple = (AzureMLForecastPipelineExecutionType.predict,
                               {'X': scoring_data_fcdf})

    if pipeline_execution_type == 'train_predict':
        operation_list = [fit_operation_tuple, predict_operation_tuple]
    elif pipeline_execution_type == 'train_only':
        operation_list = [fit_operation_tuple]
    elif pipeline_execution_type == 'predict_only':
        operation_list = [predict_operation_tuple]

    pipeline, last_step_output = execute_pipeline_operation(
        pipeline, operation_list)

    if pipeline_execution_type in ['train_predict', 'predict_only']:
        # return prediction json string
        prediction = last_step_output
        return prediction.to_json()

    elif pipeline_execution_type in ['train_only']:
        # return pipeline bytes
        return pickle.dumps(pipeline)


def interpret_as_score_context(input_json):
    """.. py:function:: interpret_as_score_context(input_json)
    Check if the input represents json string or ScoreContext.
    Raises exception if the input is not ScoreContext or its json representation.
    :param input_json: the ScoreContext or JSON string which can be deserialized to ScoreContext.
    :type input_json: ScoreContext or str.
    :returns: ScoreContext with scoring data set.
    :rtype: ScoreContext.
    :raises: Exception.
    """
    if isinstance(input_json, ScoreContext):
        return input_json
    return ScoreContext.construct_from_json(input_json)


def interpret_as_fdf(input_json):
    """.. py:function:: interpret_as_fdf(input_json)
    Check if the input represents json string or ForecastDataFrame.
    Raises exception if the input is not ForecastDataFrame or its json representation.
    :param input_json: the ForecastDataFrame or JSON string which can be deserialized to ForecastDataFrame.
    :type input_json: ForecastDataFrame or str.
    :returns: ScoreContext with scoring data set.
    :rtype: ScoreContext.
    :raises: Exception.
    """
    fdf_data = None
    if isinstance(input_json, ForecastDataFrame):
        fdf_data = input_json
    else:
        fdf_data = ForecastDataFrame.construct_from_json(input_json)
    sc = ScoreContext(input_scoring_data_fcdf=fdf_data, pipeline_execution_type='predict_only')
    return sc


def interpret_as_tsdf(input_json, sample_fcdf):
    """.. py:function:: interpret_as_tsdf(input_json, sample_fcdf)
    Check if the input represents json string or TimeSeriesDataFrame.
    Raises exception if the input is not TimeSeriesDataFrame or its json representation.
    :param input_json: the TimeSeriesDataFrame or JSON string which can be deserialized to TimeSeriesDataFrame.
    :type input_json: TimeSeriesDataFrame or str.
    :param sample_fcdf: the ForecastDataFrame carrying all metadata to reconstfuct ForecastDataFrame from input_json.
    :type sample_fcdf: ForecastDataFrame.
    :returns: ScoreContext with scoring data set.
    :rtype: ScoreContext.
    :raises: Exception.
    """
    tsdf_data = None
    if isinstance(input_json, TimeSeriesDataFrame):
        tsdf_data = input_json
    else:
        tsdf_data = TimeSeriesDataFrame.construct_from_json(input_json)
    if sample_fcdf.pred_dist not in list(tsdf_data.columns.values):
        tsdf_data[sample_fcdf.pred_dist] = np.zeros(len(tsdf_data),)
    if sample_fcdf.pred_point not in list(tsdf_data.columns.values):
        tsdf_data[sample_fcdf.pred_point] = np.zeros(len(tsdf_data),)
    fcdf_predict = ForecastDataFrame(tsdf_data,
                                     pred_point = sample_fcdf.pred_point,
                                     pred_dist = sample_fcdf.pred_dist)
    return interpret_as_fdf(fcdf_predict)


def interpret_as_df(input_json, sample_fcdf):
    """.. py:function:: interpret_as_df(input_json, sample_fcdf)
    Check if the input represents json string or DataFrame.
    Raises Exception if the input is not pandas DataFrame or its json representation.
    :param input_json: the pandas.DataFrame or JSON string which can be deserialized to pandas.DataFrame.
    :type input_json: pandas.DataFrame or str.
    :param sample_fcdf: the ForecastDataFrame carrying all metadata to reconstfuct ForecastDataFrame from input_json.
    :type sample_fcdf: ForecastDataFrame.
    :returns: ScoreContext with scoring data set.
    :rtype: ScoreContext.
    :raises: Exception.
    """
    pd_data = None
    if isinstance(input_json, pd.DataFrame):
        pd_data = input_json
    else:
        pd_data = pd.read_json(input_json, orient='split')
    tsdf_data = TimeSeriesDataFrame(pd_data, 
                                    grain_colnames = sample_fcdf.grain_colnames, 
                                    time_colname = sample_fcdf.time_colname, 
                                    ts_value_colname = sample_fcdf.ts_value_colname, 
                                    group_colnames = sample_fcdf.group_colnames)
    return interpret_as_tsdf(tsdf_data, sample_fcdf)

def run_impl(input_info_json_str, pipeline, json_meta_params=''):
    """.. py:function:: run_impl(input_info_json_str, json_meta_params)
    Run the scoring on input_info_json_str. input_info_json_str may represent ScoreContext,
    ForecastDataFrame, TimeSeriesDataFrame or pandas.DataFrame serialized or not serialized to JSON
    string. If input_info_json_str represents TimeSeriesDataFrame or pandas.DataFrame, the json_meta_params is required.
    json_meta_params is the sample ForecastDataFrame serialized to JSON string. Sample ForecastDataFrame that sets
    the input schema. The service being created will attempt to interpret the input according to this it if the
    service is called with 'unannotated' data type, such as a pandas.DataFrame.
    :param input_info_json_str: ScoreContext, ForecastDataFrame, TimeSeriesDataFrame or pandas.DataFrame in serialized or deserialized form.
    :type input_info_json_str:  ScoreContext, ForecastDataFrame, TimeSeriesDataFrame, pandas.DataFrame or str.
    :param pipeline:
        The pipeline to fit and/or predict on.
    :type pipeline: :class:`ftk.pipeline.AzureMLForecastPipeline`
    :param json_meta_params: sample ForecastDataFrame.
    :type json_meta_params: str.
    :returns: The ForecastDataFrame with forecast serialized to JSON format.
    :rtype: str.
    """
    score_context = None 
    fcdf_meta = None
    if json_meta_params != '':
        fcdf_meta = ForecastDataFrame.construct_from_json(json_meta_params)
    
    score_context = None
    try:
        score_context = interpret_as_score_context(input_info_json_str)
    except:
        pass
    
    if score_context is None:
        try:
            score_context = interpret_as_fdf(input_info_json_str)
        except:
            pass
    
    if  score_context is None and  not fcdf_meta is None: 
        try:
            score_context = interpret_as_tsdf(input_info_json_str, fcdf_meta)
        except:
            pass
        
        if score_context is None:
            try:
                score_context = interpret_as_df(input_info_json_str, fcdf_meta)
            except:
                pass
    
    if score_context is None:
        raise NameError("The input string format was not recognized.")
    # score_run
    result = score_run(score_context=score_context, pipeline=pipeline)
    return result
