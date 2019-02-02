from pydnameth.infrastucture.common import is_float
from pydnameth.infrastucture.path import get_data_base_path
from pydnameth.config.common import CommonTypes
import os.path
import pickle


def load_attributes_dict(config):
    fn = get_data_base_path(config) + '/' + \
         config.attributes.observables.name
    fn_txt = fn + '.txt'
    fn_pkl = fn + '.pkl'

    if os.path.isfile(fn_pkl):

        f = open(fn_pkl, 'rb')
        attributes_dict = pickle.load(f)
        f.close()

    else:

        f = open(fn_txt)
        key_line = f.readline()
        keys = key_line.split('\t')
        keys = [x.rstrip() for x in keys]
        possible_keys = list(config.attributes.observables.types.keys())
        possible_keys = [config.attributes.target] + possible_keys

        attributes_dict = {}
        for key in keys:
            if key in possible_keys:
                attributes_dict[key] = []

        for line in f:
            values = line.split('\t')
            for key_id in range(0, len(keys)):
                key = keys[key_id]
                if key in possible_keys:
                    value = values[key_id].rstrip()
                    if is_float(value):
                        value = float(value)
                        if value.is_integer():
                            attributes_dict[key].append(int(value))
                        else:
                            attributes_dict[key].append(float(value))
                    else:
                        attributes_dict[key].append(value)
        f.close()

        f = open(fn_pkl, 'wb')
        pickle.dump(attributes_dict, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    return attributes_dict


def load_cells_dict(config):
    fn = get_data_base_path(config) + '/' + config.attributes.cells.name
    fn_txt = fn + '.txt'
    fn_pkl = fn + '.pkl'

    if os.path.isfile(fn_pkl):

        f = open(fn_pkl, 'rb')
        cells_dict = pickle.load(f)
        f.close()

    else:

        f = open(fn_txt)
        key_line = f.readline()
        keys = key_line.split('\t')
        # First column is always sample name
        keys = [x.rstrip() for x in keys][1::]

        if isinstance(config.attributes.cells.types, list):
            possible_keys = config.attributes.cells.types
        elif config.attributes.cells.types == CommonTypes.any.value:
            possible_keys = keys
        else:
            possible_keys = []

        cells_dict = {}
        for key in keys:
            if key in possible_keys:
                cells_dict[key] = []

        for line in f:
            values = line.split('\t')[1::]
            for key_id in range(0, len(keys)):
                key = keys[key_id]
                if key in possible_keys:
                    value = values[key_id].rstrip()
                    if is_float(value):
                        cells_dict[key].append(float(value))
                    else:
                        cells_dict[key].append(value)
        f.close()

        f = open(fn_pkl, 'wb')
        pickle.dump(cells_dict, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    return cells_dict
