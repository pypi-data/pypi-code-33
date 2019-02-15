import inspect
from .. import ADAPTERS


__cache = {}  # {model_cls: adapter_cls, ...}

def get_adapter_cls(model_or_cls):
    """ Returns database adapter class for given ORM model instance or class.
    
    :param model_or_cls: an ORM model instance or class.
    :returns: An adapter class (subclass of
        :py:class:`~.adapter_base.AdapterBase`) for the model.
    """
    global __cache
    
    cls = model_or_cls
    if not inspect.isclass(cls):
        cls = model_or_cls.__class__

    if cls in __cache:
        return __cache[cls]

    for adapter_cls in ADAPTERS:
        if adapter_cls.is_usable(cls):
            __cache[cls] = adapter_cls
            return adapter_cls


def get_adapter_cls_by_name(name):
    """ Returns a database adapter class with a given name.
    
    :param name: Name of a database adapter.
    :return: Database adapter (subclass of
        :py:class:`~.adapter_base.AdapterBase`).
    """
    for adapter_cls in ADAPTERS:
        if adapter_cls.__name__ == name:
            return adapter_cls
