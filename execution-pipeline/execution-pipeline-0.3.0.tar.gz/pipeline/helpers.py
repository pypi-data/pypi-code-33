import inspect


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def named_method_params(method, args, kwargs):
    """
    Takes a method and its arguments and returns a dictionary of all values that will be passed to it. This allows for
    easy inspection.
    """
    args_names = method.__code__.co_varnames[:method.__code__.co_argcount]
    params = get_default_args(method)
    args_dict = {**dict(zip(args_names, args)), **kwargs}
    params.update(args_dict)
    return params
