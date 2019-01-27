import copy
from typing import Optional, Dict, Any, List, ClassVar


def args_kwargs_decorator(names: Optional[Dict[str, Any]] = None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            for item in names.items():
                kwargs.setdefault(item[0], copy.deepcopy(item[1]))
            return f(*args, **kwargs)
        return wrapper
    return decorator


def order_by_list(order: List[str]):
    def _order(plugin: ClassVar):
        try:
            return order.index(plugin.__class__.__name__)
        except ValueError:
            return -1
    return _order


def filter_by_list(order: List[str]):
    def _filter(plugin: ClassVar):
        return plugin.__class__.__name__ in order
    return _filter
