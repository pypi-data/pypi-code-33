import difflib
import numpy as np
from scipy.stats import linregress


def find_string(choice, options, cutoff=0.3):
    """
    This function find the closest match in a list of string and send warning of error if not found.

    :param choice: the string to match
    :param options: the list of options (in string)
    :param cutoff: float, a number between one and 0, if one the string must match perfectly the options, if 0 all pass
    :return: the closest match or None if nothing is found
    """
    name_found = difflib.get_close_matches(choice, options, cutoff=cutoff)

    if len(name_found) == 0:
        raise ValueError("No match found for {}".format(choice))

    name_found = name_found[0]
    return name_found


def func_logarithm(x, paramfit1, paramfit2, paramfit3):
    """
    This is a function which calculate the log with some free parameters. It is useful to do a logarithmic interpolation
    using the scipy module curve_fit.
    :param x: np.array - data on which is done the interpolation
    :param paramfit1: the first parameter to fit. must be a float.
    :param paramfit2: the second parameter to fit
    :param paramfit3: the third parameter to fit
    """

    return paramfit1 * np.log(paramfit2 * x) + paramfit3


def rsquared(x, y):
    """
    this function return the coefficent of determination (R^2) for two array
    """

    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    return round(r_value**2,4)
