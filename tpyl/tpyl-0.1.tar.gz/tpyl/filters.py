import six

from tpyl import utils


def load_filters(filters):
    filter_dict = {
        'is_truthy': is_truthy,
        'is_falsy': is_falsy,
    }

    for filter_file in filters or []:
        module = utils.import_module(filter_file)
        for attr in [m for m in dir(module) if not m.startswith('__') and not m.endswith('__')]:
            fn = getattr(module, attr, None)
            if not six.callable(fn):
                continue
            filter_dict[fn.__name__] = fn

    return filter_dict


def is_truthy(value, default=None):
    value = default if value is None else value
    return value is True or str(value or False).lower() in ('true', 'yes', '1')


def is_falsy(value, default=None):
    value = default if value is None else value
    return value is False or str(value or True).lower() in ('false', 'no', '0')
