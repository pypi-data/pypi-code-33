import warnings
import functools


def deprecated(extra_info=None):
    """
    deprecator's wrapper for extra arguments
    :param extra_info: extra information about the method deprecation
    :return: real deprecator method
    """

    def real_deprecated(func):
        """
        Generic Perfecto deprecator uses to warning about depreceted
        function call. Wrap a function using this deprecator to extra information
        about replacemnet for function {func}.
        :param func: function passed to the decorator
        :return: wrapper function
        """
        @functools.wraps(func)
        def func_deprecated(*args, **kwargs):
            deprecated_msg = "Call to deprecated function \"{}\"".format(func.__name__)
            warnings.simplefilter('always', DeprecationWarning)  # Shows only deprecation warnings for a while

            # if provided extra info add it to the deprecation message
            if extra_info is not None:
                deprecated_msg += '\n' + extra_info

            warnings.warn(deprecated_msg, category=DeprecationWarning, stacklevel=2) # warn
            warnings.simplefilter('default', DeprecationWarning)  # reset filter back
            return func(*args, **kwargs)

        return func_deprecated

    return real_deprecated
