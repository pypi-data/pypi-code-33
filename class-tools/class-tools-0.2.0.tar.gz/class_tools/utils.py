# system modules
import inspect

# internal modules

# external modules


def get_properties(obj, getter=None, setter=None, deleter=None):
    """
    Get a mapping of property names to properties from a given object's class
    or a class itself.

    Args:
        obj (object): either an object or a class
        getter, setter, deleter (bool, optional): also check whether a
            getter/setter/deleter is defined. The default is no check.

    Returns:
        dict : mapping of property names to the properties
    """
    return dict(
        inspect.getmembers(
            obj if isinstance(obj, type) else type(obj),
            lambda x: (
                isinstance(x, property)
                and all(
                    bool(v) == bool(getattr(x, p))
                    for p, v in {
                        "fget": getter,
                        "fset": setter,
                        "fdel": deleter,
                    }.items()
                    if v is not None
                )
            ),
        )
    )


def full_object_path(var):
    """
    Get the full path string for a given object

    Args:
        obj (object): The variable to get the full string from

    Returns:
        str : The full object path
    """
    name = var.__name__
    module = var.__module__
    return (
        name
        if module == "builtins"
        else "{module}.{name}".format(name=name, module=module)
    )
