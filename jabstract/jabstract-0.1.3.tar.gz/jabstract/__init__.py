import copy


def apply_kwargs(kwargs, default_kwargs):
    for field, override in kwargs.items():
        default = default_kwargs.get(field, {})
        if isinstance(override, dict) and isinstance(default, dict):
            default_kwargs[field] = apply_kwargs(override, default)
        else:
            default_kwargs[field] = override
    return default_kwargs


def jabstract(payload):
    def p(**kwargs):
        return apply_kwargs(kwargs, copy.deepcopy(payload))
    return p
