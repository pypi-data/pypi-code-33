# system modules
import inspect

# internal modules

# external modules


def get_properties(obj):
    """
    Get a mapping of property names to properties from a given object's class
    or a class itself.

    Args:
        obj (object): either an object or a class

    Returns:
        dict : mapping of property names to the properties
    """
    return dict(
        inspect.getmembers(
            obj if isinstance(obj, type) else type(obj),
            lambda x: isinstance(x, property),
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
