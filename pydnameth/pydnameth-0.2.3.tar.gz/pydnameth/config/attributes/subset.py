from pydnameth.config.common import CommonTypes
import numpy as np
from pydnameth.routines.common import is_float


def pass_indexes(config, target, variable, any):
    passed_indexes = []
    attributes = config.attributes_dict[target]
    if variable == any:
        passed_indexes = list(range(0, len(attributes)))
    else:

        if variable not in attributes:
            raise ValueError(f'No {str(variable)} in {target} column.')

        for index in range(0, len(attributes)):
            if variable == attributes[index]:
                passed_indexes.append(index)
    return passed_indexes


def get_indexes(config):
    indexes = list(range(0, len(list(config.attributes_dict.values())[0])))

    for obs, value in config.attributes.observables.types.items():
        any = CommonTypes.any.value
        if obs in config.attributes_dict:

            if isinstance(value, list):

                passed_indexes = []

                for v in value:

                    if is_float(v):
                        v = float(v)
                        if v.is_integer():
                            v = int(v)

                    passed_indexes += pass_indexes(config, obs, v, any)
            else:

                if is_float(value):
                    value = float(value)
                    if value.is_integer():
                        value = int(value)

                passed_indexes = pass_indexes(config, obs, value, any)

            indexes = list(set(indexes).intersection(passed_indexes))
        else:
            raise ValueError('Wrong observables.types key.')

    indexes.sort()

    return indexes


def subset_attributes(config):
    for key in config.attributes_dict:
        values = config.attributes_dict[key]
        values = list(np.array(values)[config.attributes_indexes])
        config.attributes_dict[key] = values


def subset_cells(config):
    for key in config.cells_dict:
        values = config.cells_dict[key]
        values = list(np.array(values)[config.attributes_indexes])
        config.cells_dict[key] = values
