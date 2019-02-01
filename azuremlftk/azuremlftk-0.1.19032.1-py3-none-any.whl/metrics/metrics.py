import numpy as np


def _check_calc_input(y_true, y_pred, rm_na=True):
    """
    Check that 'y_true' and 'y_pred' are non-empty and
    have equal length.

    :param y_true: Vector of actual values
    :type y_true: array-like

    :param y_pred: Vector of predicted values
    :type y_pred: array-like

    :param rm_na:
        If rm_na=True, remove entries where y_true=NA and y_pred=NA.
    :type rm_na: boolean

    :return:
        Tuple (y_true, y_pred). if rm_na=True,
        the returned vectors may differ from their input values.
    :rtype: Tuple with 2 entries
    """
    if len(y_true) != len(y_pred):
        raise ValueError(
            'the true values and prediction values do not have equal length.')
    elif len(y_true) == 0:
        raise ValueError(
            'y_true and y_pred are empty.')
    # if there is any non-numeric element in the y_true or y_pred,
    # the ValueError exception will be thrown.
    y_true = np.array(y_true).astype(float)
    y_pred = np.array(y_pred).astype(float)
    if rm_na:
        # remove entries both in y_true and y_pred where at least
        # one element in y_true or y_pred is missing
        y_true_rm_na = y_true[~(np.isnan(y_true) | np.isnan(y_pred))]
        y_pred_rm_na = y_pred[~(np.isnan(y_true) | np.isnan(y_pred))]
        return (y_true_rm_na, y_pred_rm_na)
    else:
        return y_true, y_pred


def calc_mape(y_true, y_pred):
    """
    Calculate MAPE_ (mean absolute percentage error) forecast metric
    using true vs. predicted values.

    .. _MAPE: https://en.wikipedia.org/wiki/Mean_absolute_percentage_error

    :param y_true: Vector of actual values
    :type y_true: Array-like

    :param y_pred: Vector of predicted values
    :type y_pred: array-like

    :return: MAPE_ value
    :rtype: Float
    """
    # Reference: https://en.wikipedia.org/wiki/Mean_absolute_percentage_error
    y_true, y_pred = _check_calc_input(y_true, y_pred)
    if len(y_true) == 0:
        # if there is no entries left after moving na data, return np.nan
        return (np.nan)
    y_true_rm_zero = y_true[y_true != 0]
    y_pred_rm_zero = y_pred[y_true != 0]
    if len(y_true_rm_zero) == 0:
        # if all values are zero, np.nan will be returned.
        return (np.nan)
    ape = np.abs((y_true_rm_zero - y_pred_rm_zero) / y_true_rm_zero) * 100
    mape = np.mean(ape)
    return mape


def calc_mae(y_true, y_pred):
    """
    Calculate MAE_ (mean absolute error) forecast metric
    using true vs. predicted values.

    .. _MAE: https://en.wikipedia.org/wiki/Mean_absolute_error

    :param y_true: Vector of actual values
    :type y_true: Array-like

    :param y_pred: Vector of predicted values
    :type y_pred: array-like

    :return: MAE_ value
    :rtype: Float
    """
    # Reference: https://en.wikipedia.org/wiki/Mean_absolute_error
    y_true, y_pred = _check_calc_input(y_true, y_pred)
    if len(y_true) == 0:
        # if there is no entries left after moving na data, return np.nan
        return(np.nan)
    ae = np.abs(y_true - y_pred)
    mae = np.mean(ae)
    return(mae)


def calc_rmse(y_true, y_pred):
    """
    Calculate RMSE_ (root mean squared error) forecast metric
    using true vs. predicted values.

    .. _RMSE: https://en.wikipedia.org/wiki/Root-mean-square_deviation

    :param y_true: Vector of actual values
    :type y_true: Array-like

    :param y_pred: Vector of predicted values
    :type y_pred: array-like

    :return: RMSE_ value
    :rtype: Float
    """
    # Reference: https://en.wikipedia.org/wiki/Root-mean-square_deviation
    y_true, y_pred = _check_calc_input(y_true, y_pred)
    if len(y_true) == 0:
        # if there is no entries left after moving na data, return np.nan
        return(np.nan)
    se = (y_true - y_pred)**2
    mse = np.mean(se)
    rmse = np.sqrt(mse)
    return(rmse)


def calc_smape(y_true, y_pred):
    """
    Calculate SMAPE_ (symmetric mean absolute percentage error)
    forecast metric using true vs. predicted values.

    .. _SMAPE: https://en.wikipedia.org/wiki/Symmetric_mean_absolute_percentage_error

    :param y_true: Vector of actual values
    :type y_true: Array-like

    :param y_pred: Vector of predicted values
    :type y_pred: array-like

    :return: SMAPE_ value
    :rtype: Float
    """
    # Reference: https://en.wikipedia.org/wiki/Symmetric_mean_absolute_percentage_error

    y_true, y_pred = _check_calc_input(y_true, y_pred)
    if len(y_true) == 0:
        # if there is no entries left after moving na data, return np.nan
        return(np.nan)
    y_true_rm_zero = y_true[~((y_true == 0) & (y_pred == 0))]
    y_pred_rm_zero = y_pred[~((y_true == 0) & (y_pred == 0))]
    if len(y_true_rm_zero) == 0:
        # if there is no entries left after removing zero, np.nan will be returned.
        return(np.nan)
    sape = np.abs((y_true_rm_zero - y_pred_rm_zero)) / (0.5 *
                                                        (np.abs(y_true_rm_zero) + np.abs(y_pred_rm_zero))) * 100
    smape = np.mean(sape)
    return smape


def calc_mase_single_grain(y_true, y_pred, seasonal_freq=None):
    """
    Calculate MASE_ (mean absolute scaled error)
    forecast metric using true vs. predicted values
    for a single grain (i.e. a single time series)

    .. _MASE: https://en.wikipedia.org/wiki/Mean_absolute_scaled_error

    :param y_true: Vector of actual values
    :type y_true: Array-like

    :param y_pred: Vector of predicted values
    :type y_pred: array-like

    :param seasonal_freq:
        Seasonality of the time series if applicable.
        If seasonal_freq=None, the series will be assumed non-seasonal
        and the scale factor for the MASE_ will be calculated from a naive
        forecast. Otherwise, the scale factow will use a seasonal naive
        forecast.
    :type seasonal_freq: Integer

    :return: MASE_ value
    :rtype: float

    """

    # Reference: https://en.wikipedia.org/wiki/Mean_absolute_scaled_error
    y_true, y_pred = _check_calc_input(y_true, y_pred, rm_na=False)

    if seasonal_freq is None:
        # non-seasonal MASE is a special case of seasonal MASE when the seasonal_freq is 1.
        seasonal_freq = 1

    if int(seasonal_freq) != seasonal_freq:
        # the ValueExeption will be thrown will the input seasonal_freq is not numeric value.
        # will round the seasonal_freq if the input seasonal_freq contains fractional part.
        warn('the input seasonal_freq {0} is neither an integer nor a float with value equal to an integer, '
             'will use the rounded value {1} as seasonal_freq instead.'.format(str(seasonal_freq), str(round(seasonal_freq))))
        seasonal_freq = round(seasonal_freq)

    if seasonal_freq < 1:
        raise ValueError(
            'cannot handle the input seasonal_freq with non-positive value {0}.'.format(str(seasonal_freq)))

    if len(y_true) <= seasonal_freq:
        # if the length of the true value is no larger than seasonal_freq, np.nan will be returned
        # since no seasonal naive prediction/error can be calculated.
        return np.nan

    # if any of the actual or predic value is missing, a linear adjusted error sum will be calculated
    # to make sure the denominator and numerator are comparable
    l_origin = len(y_pred)
    y_pred_rm_na = y_pred[~(np.isnan(y_pred) | np.isnan(y_true))]
    y_true_rm_na = y_true[~(np.isnan(y_pred) | np.isnan(y_true))]

    if len(y_pred_rm_na) == 0:
        # if the all the entries have either prediction or actual value missing,
        # then none of the error can be computed, then the numerator cannot be calculated, np.nan will be returned.
        return np.nan

    l_rm_na = len(y_pred_rm_na)

    # the original formula is:
    # err_sum = np.sum(np.abs(y_pred_rm_na - y_true_rm_na)) / l_rm_na * l_origin
    # err_snaive = np.abs(y_true[seasonal_freq:] - y_true[:-seasonal_freq]) / (l_origin - seasonal_freq) * l_origin
    # since the l_origin cancels out during later division, just remove * l_origin when calculating the denominator
    # and numerator to simply the calculation.

    # calculate the numerator
    err_sum = np.sum(np.abs(y_pred_rm_na - y_true_rm_na)) / l_rm_na
    # calculate the denominator
    # pylint: disable=invalid-unary-operand-type
    err_snaive = np.abs(
        y_true[seasonal_freq:] - y_true[:-seasonal_freq]) / (l_origin - seasonal_freq)

    if np.any(np.isnan(err_snaive)):
        # if there is any value missing in any of the (seasonal) naive error, np.nan is returned
        return np.nan

    err_snaive_sum = np.sum(err_snaive)

    if err_snaive_sum == 0:
        # if the denominator is 0, return np.nan
        return np.nan

    return err_sum/err_snaive_sum
