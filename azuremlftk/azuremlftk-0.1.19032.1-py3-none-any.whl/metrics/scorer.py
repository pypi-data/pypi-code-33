import ftk
from sklearn.metrics import make_scorer

def score_fun_for_fdf(score_fun):
    """
    Wrap the input score function to make it also work with prediction input
    of ForecastDataFrame.

    :param score_fun:
        Score function (or loss function) with signature
        score_func(y, y_pred, **kwargs)
    :type score_fun: callable
    :return:
        The corresponding score function that are compatible with prediction
        input of ForecastDataFrame.
    :rtype: callable
    """
    def score_fun_wrapped(y_true, y_pred):
        if isinstance(y_pred, ftk.ForecastDataFrame):
            if y_pred.pred_point is None:
                raise ValueError('The input ForecastDataFrame does not have '
                                 'point forecasts for evaluation.')
            y_pred = y_pred[y_pred.pred_point]
        return score_fun(y_true, y_pred)
    return score_fun_wrapped


def make_forecast_scorer(score_func, greater_is_better=False, **kwargs):
    """
    This function is a wrapper around sklearn.metrics.make_scorer to make it
    work with predictions stored in ForecastDataFrame.

    .. _sklearn.metrics.make_scorer: http://scikit-learn.org/stable/modules/generated/sklearn.metrics.make_scorer.html

    :param score_func:
        Score function (or loss function) with signature
        score_func(y, y_pred, **kwargs).
        For pre-defined valid score_func, see:
            1) ftk.metrics.metrics.calc_mape, ftk.metrics.metrics.calc_mae,
               ftk.metrics.metrics.calc_rmse, ftk.metrics.metrics.calc_smape
            2) The regression metrics in sklearn.metrics module (http://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics)

    :type callable
    :param greater_is_better:
        Whether score_func is a score function (default), meaning high is good,
        or a loss function, meaning low is good. In the latter case,
        the scorer object will sign-flip the outcome of the score_func.
    :type: boolean
    :param kwargs: additional arguments
        Additional parameters to be passed to score_func.

    :return:
    """
    score_func_wrapped = score_fun_for_fdf(score_func)
    return make_scorer(score_func=score_func_wrapped,
                       greater_is_better=greater_is_better,
                       needs_proba=False, needs_threshold=False, **kwargs)
