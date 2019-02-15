import copy


class Parameter:

    type_mapping = {
        "float": (int, float),
        "integer": int,
        "bool": bool,
        "list": list,
        "dict": dict,
        "string": str,
        "enum": object,
    }

    def __init__(self, param: dict, name):
        self.name = name
        self.description = param["description"]
        self.type = self.type_mapping[param["type"]]
        self.enum = param.get("enum")
        self.optional = param.get("optional", False)
        self.value = param["default"]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if self.optional and val is None:
            self._value = val
            return
        if not isinstance(val, self.type):
            raise ValueError(
                f"Setting parameter {self.name} of type {self.type} with value {val}."
            )
        elif self.enum and val not in self.enum:
            raise ValueError(
                f"Setting parameter {self.name} with a value {val} that is not in {self.enum}."
            )
        self._value = val


class FGParameters(object):
    def __init__(self, parameters: dict):
        self.parameter = {}
        for name, spec in parameters.items():
            self.parameter[name] = Parameter(spec, name)

    def __getitem__(self, key):
        return self.parameter[key].value

    def keys(self):
        return self.parameter.keys()

    def update(self, values):
        for name, value in values.items():
            if name not in self.parameter:
                raise KeyError(f"Parameter {name} not found in manifest.json.")
            self.parameter[name].value = value

    def copy(self):
        return copy.deepcopy(self)

    def check(self, name, checker, error_message):
        if not checker(self[name]):
            raise ValueError(f'Parameter "{name}" failed validation: {error_message}')
